import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

IPINFO_API_BASE = "https://ipinfo.io"
WEATHER_API_BASE = "https://api.weather.gov"

@mcp.tool()
async def get_user_location() -> dict[str, str] | None:
    """Get the coordinates, city, region, and country of the user.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{IPINFO_API_BASE}/json")
            data = response.json()
        except httpx.HTTPError:
            return None
        
        return {
            "city": data["city"],
            "region": data["region"],
            "country": data["country"],
            "loc": data["loc"],
        }

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{WEATHER_API_BASE}/points/{latitude},{longitude}")
            data = response.json()
            print(data)
        except httpx.HTTPError:
            return "Unable to fetch forecast data for this location."
        
        if not data:
            return "Unable to fetch location data for this location."
        
        forecast_url = data["properties"]["forecast"]
        if not forecast_url:
            return "No forecast URL found for this location."
        
        try:
            response = await client.get(forecast_url)
            forecast_data = response.json()
        except httpx.HTTPError:
            return "Unable to fetch forecast data for this location."

    forecasts = forecast_data["properties"]["periods"][:10]
    return "\n---\n".join(str(forecast) for forecast in forecasts)


if __name__ == "__main__":
    mcp.run(transport="stdio")