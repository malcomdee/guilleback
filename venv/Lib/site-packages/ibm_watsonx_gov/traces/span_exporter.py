# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


import gzip
import json
import os
import random
import re
import requests
import threading
import zlib

from concurrent.futures import ThreadPoolExecutor
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger
from io import BytesIO
try:
    from google.protobuf.json_format import MessageToDict
    from opentelemetry.exporter.otlp.proto.common.trace_encoder import \
        encode_spans
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
        OTLPSpanExporter as HTTPSpanExporter
    from opentelemetry.exporter.otlp.proto.http import \
        Compression
    from opentelemetry.proto.trace.v1.trace_pb2 import TracesData
    from opentelemetry.sdk.trace.export import SpanExportResult
except:
    pass
from pathlib import Path
from time import time, sleep
from typing import Optional

_MAX_RETRY = 6
logger = GovSDKLogger.get_logger(__name__)


class WxGovSpanExporter(HTTPSpanExporter):
    def __init__(
        self,
        enable_local_traces: Optional[bool] = False,
        enable_server_traces: Optional[bool] = False,
        file_name: Optional[str] = None,
        storage_path: Optional[str] = None,
        max_workers: int = 2,
        *args, **kwargs
    ):
        """
        Initialize a HTTPSpan exporter which additionally store traces to a local log file

        Args:
            enable_local_traces: For storing traces locally
            enable_server_traces: For forwarding traces to tracing service
            file_name: Base name for the trace file (without extension)
            storage_path: Directory to store trace files
            *args, **kwargs: default inputs of HTTPSpanExporter
        """
        super().__init__(*args, **kwargs)
        self.enable_local_traces = enable_local_traces
        self.enable_server_traces = enable_server_traces
        self.storage_path = Path(storage_path)
        self.file_path = self.storage_path / f"{file_name}.log"
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        excluded_urls = os.getenv("WATSONX_TRACING_EXCLUDED_URLS")
        if excluded_urls:
            patterns = [pattern.strip()
                        for pattern in excluded_urls.split(",") if pattern.strip()]
            self.excluded_url_patterns = re.compile(
                "|".join(patterns)) if patterns else None
        else:
            self.excluded_url_patterns = None

        # Ensure storage directory exists
        if enable_local_traces:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._initialize_trace_file()

    def _initialize_trace_file(self) -> None:
        """Initialize the trace file with file"""
        with self._lock, self.file_path.open("w") as f:
            pass

    def _store_locally(self, spans: bytes) -> None:
        """Append spans to the trace file in a thread-safe manner."""
        try:
            traces = TracesData.FromString(spans)
            traces_dict = MessageToDict(traces)
            with self._lock, self.file_path.open("a") as f:
                json.dump(traces_dict, f)
                f.write("\n")
        except Exception as e:
            return SpanExportResult.FAILURE

    def export(self, spans) -> SpanExportResult:
        if not spans or self._should_exclude_span(spans[0]):
            return SpanExportResult.SUCCESS

        if self._shutdown:
            return SpanExportResult.FAILURE

        serialized_data = encode_spans(spans).SerializePartialToString()

        if self.enable_server_traces and os.getenv(
                "WATSONX_TRACING_ENABLED", "true").lower() == "true":
            self._export_serialized_spans(serialized_data)
        if self.enable_local_traces:
            self._store_locally(serialized_data)

    def _should_exclude_span(self, span):
        """
        Exclude spans associated with specified URLs.
        """
        if not self.excluded_url_patterns or not hasattr(span, "attributes"):
            return False

        http_url = span.attributes.get("http.url")
        if http_url and self.excluded_url_patterns.search(http_url):
            return True

        return False

    def _export_serialized_spans(self, serialized_data):
        # Code replicated from HTTPSpanExporter.export
        deadline_sec = time() + self._timeout
        for retry_num in range(_MAX_RETRY):
            resp = self._export(serialized_data, deadline_sec - time())
            if resp.ok:
                return SpanExportResult.SUCCESS
            # multiplying by a random number between .8 and 1.2 introduces a +/20% jitter to each backoff.
            backoff_seconds = 2**retry_num * random.uniform(0.8, 1.2)
            if (
                not WxGovSpanExporter._is_retryable(resp)
                or retry_num + 1 == _MAX_RETRY
                or backoff_seconds > (deadline_sec - time())
            ):
                logger.error(
                    "Failed to export span batch code: %s, reason: %s",
                    resp.status_code,
                    resp.text,
                )
                return SpanExportResult.FAILURE
            logger.warning(
                "Transient error %s encountered while exporting span batch, retrying in %.2fs.",
                resp.reason,
                backoff_seconds,
            )
            sleep(backoff_seconds)
        # Not possible to reach here but the linter is complaining.
        return SpanExportResult.FAILURE

    @staticmethod
    def _is_retryable(resp: requests.Response) -> bool:
        if resp.status_code == 408:
            return True
        if resp.status_code >= 500 and resp.status_code <= 599:
            return True
        return False

    def _export(self, serialized_data: bytes, timeout_sec: float):
        data = serialized_data
        if self._compression == Compression.Gzip:
            gzip_data = BytesIO()
            with gzip.GzipFile(fileobj=gzip_data, mode="w") as gzip_stream:
                gzip_stream.write(serialized_data)
            data = gzip_data.getvalue()
        elif self._compression == Compression.Deflate:
            data = zlib.compress(serialized_data)

        # By default, keep-alive is enabled in Session's request
        # headers. Backends may choose to close the connection
        # while a post happens which causes an unhandled
        # exception. This try/except will retry the post on such exceptions
        try:
            resp = self._session.post(
                url=self._endpoint,
                data=data,
                verify=self._certificate_file,
                timeout=timeout_sec,
                cert=self._client_cert,
            )
        except ConnectionError:
            resp = self._session.post(
                url=self._endpoint,
                data=data,
                verify=self._certificate_file,
                timeout=timeout_sec,
                cert=self._client_cert,
            )
        return resp
