def weather_factor(weather):
    if "storm" in weather.lower():
        return 1.5
    elif "rain" in weather.lower():
        return 1.2
    return 1.0

def traffic_factor(origin, destination, hour=None):
    import datetime
    if hour is None:
        hour = datetime.datetime.now().hour

    rush_hours = [7, 8, 9, 16, 17, 18]  # Typical rush hour times
    base_factor = 1.0

    if hour in rush_hours:
        base_factor = 1.4
    elif 10 <= hour <= 15:
        base_factor = 1.1
    else:
        base_factor = 1.2  # night or early morning

    # Optional: add randomness based on city pair
    pair_key = f"{origin}-{destination}"
    pair_mod = sum(ord(c) for c in pair_key) % 10
    randomness = 0.05 * (pair_mod / 10)

    return round(base_factor + randomness, 2)

def cargo_factor(cargo):
    return {"fragile": 1.3, "hazmat": 1.5, "general": 1.0}.get(cargo.lower(), 1.0)
