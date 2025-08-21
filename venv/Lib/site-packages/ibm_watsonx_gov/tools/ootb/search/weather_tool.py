# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import Annotated, Any, Optional, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    location: Annotated[str, Field(description="Name of the location")]
    country: Annotated[Optional[str], Field(
        description="Name of the country", default=None)]


class WeatherTool(BaseTool):
    """
    Tool for retrieving the weather of a location.

    Examples:
        Basic usage
            .. code-block:: python

                weather_tool = WeatherTool()
                weather_tool.invoke({"location":"London"})
    """

    name: str = "weather_tool"
    description: str = "Find the weather for a location or a city and country."
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str, country: str = None, **kwargs: Any) -> Any:
        """Performs weather search based on location and country"""

        coordinates = self.__get_coordinates(location, country)
        coord = f"latitude={coordinates['latitude']}&longitude={coordinates['longitude']}"
        current = "current=temperature_2m,rain,relative_humidity_2m,wind_speed_10m"
        url = f"https://api.open-meteo.com/v1/forecast?{coord}&{current}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            raise Exception(
                f"Unexpected response from Weather tool {response.text}")

        response_json = response.json()

        fullLocation = location
        if country:
            fullLocation = f"{fullLocation}, {country}"

        current = response_json['current']
        current_units = response_json['current_units']
        result = f"""Current weather in {fullLocation}
    Temperature: {current['temperature_2m']}{current_units['temperature_2m']}
    Rain: {current['rain']}{current_units['rain']}
    Relative humidity: {current['relative_humidity_2m']}{current_units['relative_humidity_2m']}
    Wind: {current['wind_speed_10m']}{current_units['wind_speed_10m']}
    """

        return result

    def __get_coordinates(self, location, country):
        params = f"name={location}"
        if country:
            params = f"{params}&country={country}"

        url = f"https://geocoding-api.open-meteo.com/v1/search?{params}&count=1&language=en&format=json"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code >= 400:
            raise Exception(
                f"Unable to get coordinates for location from Weather tool {response.text}")

        results = response.json()
        if "results" not in results:
            raise Exception(
                "Unable to find weather for location {}.".format(location))
        return {
            "latitude": results["results"][0]["latitude"],
            "longitude": results["results"][0]["longitude"]
        }
