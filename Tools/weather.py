import httpx
import asyncio
import os
import ipinfo
from dotenv import load_dotenv
from datetime import date, timedelta, datetime

load_dotenv()

def filter_weather(data: dict) -> dict:
    days = data.get("days", [{}])
    day = days[0] if days else {}

    return {
        "city": data.get("resolvedAddress", ""),
        "timezone": data.get("timezone", ""),
        "date": day.get("datetime", ""),
        "date_epoch": day.get("datetimeEpoch", ""),

        "weather": day.get("conditions", ""),
        "description": day.get("description", ""),

        "temp_avg": day.get("temp", ""),
        "temp_max": day.get("tempmax", ""),
        "temp_min": day.get("tempmin", ""),
        "feels_like": day.get("feelslike", ""),

        "humidity_percent": day.get("humidity", ""),
        "pressure_hpa": day.get("pressure", ""),
        "visibility_km": day.get("visibility", ""),
        "cloudcover_percent": day.get("cloudcover", ""),

        "wind_speed": day.get("windspeed", ""),
        "wind_gust": day.get("windgust", ""),
        "wind_direction_deg": day.get("winddir", ""),

        "sunrise": day.get("sunrise", ""),
        "sunset": day.get("sunset", ""),

        "uv_index": day.get("uvindex", ""),
        "precip_mm": day.get("precip", ""),
        "snow_mm": day.get("snow", ""),

        "source": day.get("source", "")
    }

def is_valid_date(day: str) -> str | None:
    day = day.lower().strip()

    if day == "today":
        return date.today().strftime("%Y-%m-%d")

    if day == "tomorrow":
        return (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    if day == "yesterday":
        return (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        parsed = datetime.strptime(day, "%Y/%m/%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None            

def get_Location(city:str):
    if not city.lower == "current" or "currant":
        try:
            handler = ipinfo.getHandler()
            details = handler.getDetails()
            return details.city
        except Exception as e:
            return "Please check your internet connection."
    else:
        return city
    
async def _get_weather_async(city, day):

    place = get_Location(city=city)
    date = is_valid_date(day=day)
    api_key = os.getenv("WEATHER_API_KEY")
    api_url = os.getenv("WEATHER_BASE_URL")

    if not api_key or not api_url or not place or not date:
        return("Weather API is not Working")
    
    url = f"{api_url}/{place}/{date}?key={api_key}" 
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

def get_weather(city, d):
    """Fetches Weather of a Given City and Date."""
    response =  asyncio.run(_get_weather_async(city, d))
    weather = filter_weather(response)
    return {
        "System" : "Fetched Weather API Data for {city} on {d}",
        "Data" : weather
    }


if __name__ == "__main__":
    print(get_weather("Ludhiana", "2026/01/29"))
