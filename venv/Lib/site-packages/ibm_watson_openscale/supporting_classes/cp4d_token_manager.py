# coding: utf-8

# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Optional
from ibm_cloud_sdk_core.jwt_token_manager import JWTTokenManager

from ibm_watson_openscale.utils.client_utils import get_access_token

import datetime


class CP4D40TokenManager(JWTTokenManager):
    """Token Manager of CloudPak for data.

    The Token Manager performs basic auth with a username and password
    to acquire JWT tokens.

    Args:
        username: The username for authentication.
        password: The password for authentication.
        url: The endpoint for JWT token requests.

    Keyword Arguments:
        disable_ssl_verification: Disable ssl verification. Defaults to False.
        headers: Headers to be sent with every service token request. Defaults to None.
        proxies: Proxies to use for making request. Defaults to None.
        proxies.http (optional): The proxy endpoint to use for HTTP requests.
        proxies.https (optional): The proxy endpoint to use for HTTPS requests.

    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication.
        url (str): The endpoint for JWT token requests.
        headers (dict): Headers to be sent with every service token request.
        proxies (dict): Proxies to use for making token requests.
        proxies.http (str): The proxy endpoint to use for HTTP requests.
        proxies.https (str): The proxy endpoint to use for HTTPS requests.
    """
    TOKEN_NAME = 'accessToken'
    #VALIDATE_AUTH_PATH = '/v1/preauth/validateAuth'

    def __init__(self,
                 username: str,
                 password: str,
                 url: str,
                 *,
                 apikey: str = None,
                 disable_ssl_verification: bool = False,
                 headers: Optional[Dict[str, str]] = None,
                 proxies: Optional[Dict[str, str]] = None,
                 bedrock_url: str = None) -> None:
        self.username = username
        self.password = password
        #if url and not self.VALIDATE_AUTH_PATH in url:
        #    url = url + '/v1/preauth/validateAuth'
        self.url = url
        self.apikey = apikey
        self.headers = headers
        self.proxies = proxies
        self.bedrock_url = bedrock_url
        self.token_generation_time = datetime.datetime.now().timestamp()
        self.bearer_token = None
        super().__init__(url, disable_ssl_verification=disable_ssl_verification,
                         token_name=self.TOKEN_NAME)

    def get_token(self) -> dict:
        """Makes a request for a token.
        """
        expired_token = self.is_token_expired(self.bearer_token)
        if expired_token == True:
            self.bearer_token =  get_access_token(self.url,self.username,self.password, apikey = self.apikey, bedrock_url = self.bedrock_url)
            self.token_generation_time = datetime.datetime.now().timestamp()   
            
        return self.bearer_token
    
    def request_token(self) -> dict:
        """Makes a request for a token.
        """
        return self.get_token()
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """Headers to be sent with every CP4D token request.

        Args:
            headers: The headers to be sent with every CP4D token request.
        """
        if isinstance(headers, dict):
            self.headers = headers
        else:
            raise TypeError('headers must be a dictionary')

    def set_proxies(self, proxies: Dict[str, str]) -> None:
        """Sets the proxies the token manager will use to communicate with CP4D on behalf of the host.

        Args:
            proxies: Proxies to use for making request. Defaults to None.
            proxies.http (optional): The proxy endpoint to use for HTTP requests.
            proxies.https (optional): The proxy endpoint to use for HTTPS requests.
        """
        if isinstance(proxies, dict):
            self.proxies = proxies
        else:
            raise TypeError('proxies must be a dictionary')
        
    def is_token_expired(self,token):
        if token is None:
            return True
        current_time = datetime.datetime.now().timestamp()
        difference_in_time = current_time - self.token_generation_time
        # If token was generated 30 min ago then considered it as expired
        # 30 * 60 = 1800 
        if difference_in_time>=1800:
            return True
        return False    
