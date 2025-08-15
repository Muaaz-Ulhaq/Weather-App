import re
def detect_location_params(user_input: str, country_code: str = "us") -> dict:

    # Remove extra spaces
    user_input = user_input.strip()

    # Check if input is coordinates (latitude,longitude)
    coord_pattern = re.compile(r"^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$")
    if coord_pattern.match(user_input):
        lat, lon = [x.strip() for x in user_input.split(",")]
        return {"lat": lat, "lon": lon}

    # Check if input is numeric (likely ZIP/Postal code)
    if user_input.isdigit():
        return {"zip": f"{user_input},{country_code}"}

    # Otherwise treat as city name
    return {"q": user_input}