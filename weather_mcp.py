import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server instance
mcp = FastMCP()

# API endpoints
IPINFO_API_BASE = "https://ipinfo.io"
WEATHER_API_BASE = "https://api.weather.gov"


@mcp.tool()
async def get_user_location() -> dict[str, str] | None:
    """
    Retrieve the user's geolocation using IP-based lookup.

    Returns:
        A dictionary with city, region, country, and location coordinates.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{IPINFO_API_BASE}/json")
            data = response.json()
        except httpx.HTTPError:
            return None

        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc"),
        }


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    Fetch weather forecast for the provided latitude and longitude.

    Args:
        latitude (float): Geographic latitude
        longitude (float): Geographic longitude

    Returns:
        A string summarizing the next 10 weather periods.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{WEATHER_API_BASE}/points/{latitude},{longitude}"
            )
            data = response.json()
        except httpx.HTTPError:
            return "Unable to fetch location data for this location."

        forecast_url = data.get("properties", {}).get("forecast")
        if not forecast_url:
            return "No forecast URL found for this location."

        try:
            response = await client.get(forecast_url)
            forecast_data = response.json()
        except httpx.HTTPError:
            return "Unable to fetch forecast data for this location."

    forecasts = forecast_data.get("properties", {}).get("periods", [])[:10]
    return "\n---\n".join(str(forecast) for forecast in forecasts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
