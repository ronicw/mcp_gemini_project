import os
import json
import requests
from google import genai
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

# Helper function to get city coordinates
def get_city_coordinates(city_name):
    """Get latitude and longitude for a city using Nominatim API."""
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'WeatherApp/1.0',  # Required by Nominatim's terms of service
        'Accept-Charset': 'utf-8'  # Explicitly request UTF-8 encoding
    }
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 5,  # Get up to 5 matching locations
        'accept-language': 'en'  # Request English results when available
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        locations = response.json()
        
        if not locations:
            return None, "No locations found for this city."
        
        if len(locations) == 1:
            # If only one location found, return it directly
            location = locations[0]
            return {
                'latitude': float(location['lat']),
                'longitude': float(location['lon']),
                'display_name': location['display_name']
            }, None
        
        # If multiple locations found, let user choose
        print("\nMultiple locations found:")
        for idx, loc in enumerate(locations, 1):
            print(f"{idx}. {loc['display_name']}")
        
        while True:
            try:
                choice = int(input("\nSelect a location (enter number): "))
                if 1 <= choice <= len(locations):
                    location = locations[choice - 1]
                    return {
                        'latitude': float(location['lat']),
                        'longitude': float(location['lon']),
                        'display_name': location['display_name']
                    }, None
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
            
    except requests.RequestException as e:
        return None, f"Error fetching city coordinates: {str(e)}"

# def celsius_to_fahrenheit(celsius):
#     """Convert Celsius to Fahrenheit."""
#     return (celsius * 9/5) + 32


# Define tools as functions
@mcp.tool()
def process_weather_query(city):
    """Process a weather query for a given city."""
    location, error = get_city_coordinates(city)
    if error:
        return f"Error: {error}"
    
    display_name = location['display_name']
    print(f"\nUsing location: {display_name}")
    latitude = location['latitude']
    longitude = location['longitude']

    """Invoke the publicly available API to return the weather for a given location."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    # current = response.json().get("current", {})

    # return ToolResponse(content=[Text(
    #     f"Weather in {display_name}:\n"
    #     f"Temperature: {current.get('temperature_2m', 'N/A')}°C\n"
    #     f"Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h"
    # )])
    return response.json()["current"]

@mcp.tool()
def get_weather(latitude, longitude):
    """Invoke the publicly available API to return the weather for a given location."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    # current = response.json().get("current", {})

    # return ToolResponse(content=[Text(
    #     f"Weather at ({latitude}, {longitude}):\n"
    #     f"Temperature: {current.get('temperature_2m', 'N/A')}°C\n"
    #     f"Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h"
    # )])
    return response.json()["current"]

@mcp.tool()
def get_knowledge_base() -> str:
    """Retrieve the entire knowledge base as a formatted string.

    Returns:
        A formatted string containing all Q&A pairs from the knowledge base.
    """
    try:
        kb_path = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")
        with open(kb_path, "r") as f:
            kb_data = json.load(f)

        # Format the knowledge base as a string
        kb_text = "Here is the retrieved knowledge base:\n\n"

        if isinstance(kb_data, list):
            for i, item in enumerate(kb_data, 1):
                if isinstance(item, dict):
                    question = item.get("question", "Unknown question")
                    answer = item.get("answer", "Unknown answer")
                else:
                    question = f"Item {i}"
                    answer = str(item)

                kb_text += f"Q{i}: {question}\n"
                kb_text += f"A{i}: {answer}\n\n"
        else:
            kb_text += f"Knowledge base content: {json.dumps(kb_data, indent=2)}\n\n"

        return kb_text
    except FileNotFoundError:
        return "Error: Knowledge base file not found"
    except json.JSONDecodeError:
        return "Error: Invalid JSON in knowledge base file"
    except Exception as e:
        return f"Error: {str(e)}"



if __name__ == "__main__":
    # print(get_weather("17.385", "78.4867"))
    # print(process_weather_query("Osage,Iowa"))

    mcp.run(transport="stdio")
