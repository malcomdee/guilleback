# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

import requests
from langchain.agents import AgentExecutor
from langgraph.graph import StateGraph
from langgraph.pregel import Pregel


class AgentInterface(ABC):
    """
    Base interface for all agent types.

    All agents must implement the invoke method.
    """
    @abstractmethod
    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes the agent with the given input and returns the output.

        Args:
            input_data (dict): The input payload for the agent.

        Returns:
            dict: The output from the agent.
        """
        pass

class LangChainAgent(AgentInterface):
    """
    Wrapper for LangChain agents constructed using a build function defined in code.
    """
    def __init__(self, build_fn: Callable[[], AgentExecutor], **kwargs):
        self.agent = build_fn

   
    def invoke(self, input_data: dict) -> dict:
        """
        Invokes the LangChain agent.

        Args:
            input_data (dict): The input data for the agent.

        Returns:
            dict: The result from the agent execution.
        """
        result = self.agent.invoke(input_data)

        return {"result": result}

class LangGraphAgent(AgentInterface):
    """
    Wrapper for LangGraph agents constructed using a build function defined in code.
    This class initializes and runs a LangGraph agent from a provided build function,
    which is expected to return a compiled LangGraph Pregel instance.
    """    
    def __init__(self, build_fn: Callable[[], Pregel], **kwargs):
        
        """
            Initializes the LangGraphAgent with a build function.
            Args:
                build_fn(Callable[[], Pregel]:  A function with no arguments and it returns a Pregel object (LangGraph’s compiled graph type)
        """
        self.graph = build_fn
    
    def invoke(self, input_data: dict) -> dict:
        """
        Invokes the LangGraph agent.

        Args:
            input_data (dict): The input data for the graph.

        Returns:
            dict: The result from the graph execution.
        """
        result = self.graph.invoke(input_data)

        return {"result": result}


class RestAgent(AgentInterface):
    """
    Wrapper for agents accessible via REST API.
    """
    def __init__(self, endpoint: str, headers: dict, method = "POST"):
        """
        Initializes the REST agent wrapper.
        Args:
            endpoint(str): URL endpoint of the  agent
            headers(dict): Headers in key value pair
            method(str): Http method name
        """
        self.endpoint = endpoint
        self.headers = headers
        self.method = method
    
    def invoke(self, input_schema_data: dict) -> dict:
        """
        Calls the remote agent via  request.

        Args:
            input_data (dict): The payload to send to the remote agent.

        Returns:
            dict: The JSON response from the agent.
        """
        if self.method.upper() == "GET":
            response = requests.get(self.endpoint, headers=self.headers)
            response.raise_for_status()
            
        elif self.method.upper() == "POST":
            response = requests.post(
                self.endpoint, json=input_schema_data, headers=self.headers)
            try:
                response = response.json()
            except ValueError:
                response = response.text
                print(response)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        else:
            raise ValueError(f"Unsupported method {self.method}")

        return  {"result": response}
