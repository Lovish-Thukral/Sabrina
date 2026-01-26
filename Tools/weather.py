import httpx
import asyncio
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

async def _get_weather_async(city, date):
    d = ""
    match date.lower():
        case "today":
            d = date.today()
        case "tommorow":
            d = date.today() + timedelta(days=1)
        case "yesterday":
            d = date.today() - timedelta(days=1)
        case _:
            d = date

    api_key = os.getenv("Weather_API")
    if not api_key:
        raise RuntimeError("Weather_API key not found")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "date" : "",
        "units": "metric"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def get_weather(city):
    """Synchronous wrapper. No asyncio leaks outside."""
    return asyncio.run(_get_weather_async(city))


if __name__ == "__main__":
    print(get_weather("Ludhiana"))
