import urllib.request
import urllib.parse
import json
import datetime
import time

BASELINES = {
    "electricity_eur_kwh":   0.12,
    "aluminum_usd_kg":       2.30,
    "copper_usd_kg":         8.50,
    "steel_usd_kg":          0.65,
    "oil_usd_barrel":        75.0,
    "temp_celsius_baseline": 20.0,
}

_cache     = {}
_cache_ttl = 3600


def _fetch_json(url: str, timeout: int = 8) -> dict:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FactoryAI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _cached(key: str, fetch_fn):
    now = time.time()
    if key in _cache:
        value, ts = _cache[key]
        if now - ts < _cache_ttl:
            return value
    value = fetch_fn()
    if value is not None:
        _cache[key] = (value, now)
    return value


def fetch_temperature(lat: float = 48.85, lon: float = 2.35) -> dict:
    def _fetch():
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code"
            f"&timezone=auto"
        )
        data = _fetch_json(url)
        if data and "current" in data:
            current = data["current"]
            return {
                "temp_celsius": current.get("temperature_2m", 20.0),
                "humidity":     current.get("relative_humidity_2m", 50),
                "weather_code": current.get("weather_code", 0),
                "location":     f"{lat:.2f}°N, {lon:.2f}°E",
                "source":       "Open-Meteo",
                "timestamp":    current.get("time", "")
            }
        return None

    result = _cached(f"weather_{lat}_{lon}", _fetch)
    if result is None:
        return {
            "temp_celsius": 20.0, "humidity": 50, "weather_code": 0,
            "location": "Fallback", "source": "fallback",
            "timestamp": datetime.datetime.now().isoformat()
        }
    return result


def temp_to_risk_factor(temp_celsius: float) -> float:
    if temp_celsius < 15:   return 0.9
    elif temp_celsius < 25: return 1.0
    elif temp_celsius < 32: return 1.15
    elif temp_celsius < 38: return 1.35
    else:                   return 1.6


def fetch_metal_prices() -> dict:
    def _fetch():
        url  = "https://api.metals.dev/v1/latest?api_key=demo&currency=USD&unit=kg"
        data = _fetch_json(url)
        if data and "metals" in data:
            metals = data["metals"]
            return {
                "aluminum_usd_kg": metals.get("aluminum", BASELINES["aluminum_usd_kg"]),
                "copper_usd_kg":   metals.get("copper",   BASELINES["copper_usd_kg"]),
                "source":          "metals.dev",
                "timestamp":       datetime.datetime.now().isoformat()
            }
        return None

    result = _cached("metals", _fetch)
    if result is None:
        import random
        return {
            "aluminum_usd_kg": BASELINES["aluminum_usd_kg"] * random.uniform(0.9, 1.3),
            "copper_usd_kg":   BASELINES["copper_usd_kg"]   * random.uniform(0.9, 1.2),
            "source":          "estimated (API unavailable)",
            "timestamp":       datetime.datetime.now().isoformat()
        }
    return result


def metals_to_material_multiplier(metal_prices: dict, factory_material: str = "mixed") -> float:
    al     = metal_prices.get("aluminum_usd_kg", BASELINES["aluminum_usd_kg"])
    cu     = metal_prices.get("copper_usd_kg",   BASELINES["copper_usd_kg"])
    al_mult = al / BASELINES["aluminum_usd_kg"]
    cu_mult = cu / BASELINES["copper_usd_kg"]

    if factory_material == "aluminum": return round(al_mult, 3)
    elif factory_material == "copper": return round(cu_mult, 3)
    else:                              return round((al_mult + cu_mult) / 2, 3)


def fetch_energy_proxy(country_code: str = "FRA") -> dict:
    def _fetch_oil():
        url  = "https://api.worldbank.org/v2/en/indicator/PNRGSPOT?format=json&mrv=1&per_page=1"
        data = _fetch_json(url)
        if data and len(data) > 1 and data[1]:
            entries = data[1]
            if entries:
                val = entries[0].get("value")
                if val:
                    return float(val)
        return None

    oil_price = _cached("oil_wb", _fetch_oil)
    if oil_price:
        oil_mult    = oil_price / BASELINES["oil_usd_barrel"]
        energy_mult = 0.4 + 0.6 * oil_mult
    else:
        now = datetime.datetime.now()
        hour = now.hour
        if 8 <= hour <= 18:   base_mult = 1.1
        elif 19 <= hour <= 22: base_mult = 1.2
        else:                  base_mult = 0.85
        if now.weekday() >= 5:
            base_mult *= 0.8
        energy_mult = base_mult

    return {
        "energy_cost_multiplier": round(max(0.5, min(3.0, energy_mult)), 3),
        "oil_price_usd":          round(oil_price, 2) if oil_price else None,
        "source":                 "World Bank + time-of-day proxy",
        "timestamp":              datetime.datetime.now().isoformat(),
        "peak_hours":             8 <= datetime.datetime.now().hour <= 18
    }


def fetch_demand_index(country_code: str = "WLD") -> dict:
    def _fetch():
        url  = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NV.IND.MANF.ZS?format=json&mrv=2&per_page=2"
        data = _fetch_json(url)
        if data and len(data) > 1 and data[1]:
            entries = [e for e in data[1] if e.get("value") is not None]
            if len(entries) >= 2:
                latest   = entries[0]["value"]
                previous = entries[1]["value"]
                growth   = (latest - previous) / abs(previous) if previous else 0
                demand_mult = 1.0 + (growth / 10)
                return {
                    "demand_multiplier":             round(max(0.6, min(1.6, demand_mult)), 3),
                    "manufacturing_share_latest":    round(latest, 2),
                    "growth_rate_pct":               round(growth * 100, 2),
                    "source":                        "World Bank Manufacturing Data"
                }
        return None

    result = _cached(f"demand_{country_code}", _fetch)
    if result is None:
        month    = datetime.datetime.now().month
        seasonal = {
            1: 0.85, 2: 0.88, 3: 0.95, 4: 1.02,
            5: 1.08, 6: 1.05, 7: 0.92, 8: 0.88,
            9: 1.05, 10: 1.10, 11: 1.08, 12: 0.95
        }
        return {
            "demand_multiplier":          seasonal.get(month, 1.0),
            "manufacturing_share_latest": None,
            "growth_rate_pct":            None,
            "source":                     "seasonal estimate (API unavailable)"
        }
    return result


def fetch_all(lat: float = 48.85, lon: float = 2.35,
              country_code: str = "WLD", factory_material: str = "mixed") -> dict:
    results = {
        "status": {}, "raw": {}, "multipliers": {},
        "timestamp": datetime.datetime.now().isoformat()
    }
    try:
        weather = fetch_temperature(lat, lon)
        results["raw"]["weather"] = weather
        results["multipliers"]["temp_celsius"]         = weather["temp_celsius"]
        results["multipliers"]["thermal_risk_factor"]  = temp_to_risk_factor(weather["temp_celsius"])
        results["status"]["weather"]                   = f" {weather['source']}"
    except Exception:
        results["multipliers"]["temp_celsius"]         = 20.0
        results["multipliers"]["thermal_risk_factor"]  = 1.0
        results["status"]["weather"]                   = " Fallback (20°C)"

    try:
        metals  = fetch_metal_prices()
        results["raw"]["metals"] = metals
        mat_mult = metals_to_material_multiplier(metals, factory_material)
        results["multipliers"]["material_cost_multiplier"] = mat_mult
        results["status"]["materials"]                     = f" {metals['source']}"
    except Exception:
        results["multipliers"]["material_cost_multiplier"] = 1.0
        results["status"]["materials"]                     = " Fallback (1.0x)"

    try:
        energy  = fetch_energy_proxy(country_code)
        results["raw"]["energy"] = energy
        results["multipliers"]["energy_cost_multiplier"] = energy["energy_cost_multiplier"]
        results["status"]["energy"]                      = f" {energy['source']}"
    except Exception:
        results["multipliers"]["energy_cost_multiplier"] = 1.0
        results["status"]["energy"]                      = " Fallback (1.0x)"

    try:
        demand  = fetch_demand_index(country_code)
        results["raw"]["demand"] = demand
        results["multipliers"]["demand_multiplier"] = demand["demand_multiplier"]
        results["status"]["demand"]                 = f" {demand['source']}"
    except Exception:
        results["multipliers"]["demand_multiplier"] = 1.0
        results["status"]["demand"]                 = " Fallback (1.0x)"

    return results


CITY_COORDINATES = {
    "Paris, France":           (48.85,  2.35),
    "Berlin, Germany":         (52.52,  13.40),
    "London, UK":              (51.51,  -0.12),
    "Madrid, Spain":           (40.42,  -3.70),
    "Milan, Italy":            (45.46,   9.19),
    "Casablanca, Morocco":     (33.59,  -7.62),
    "Tunis, Tunisia":          (36.81,  10.18),
    "Algiers, Algeria":        (36.74,   3.06),
    "Cairo, Egypt":            (30.06,  31.24),
    "Istanbul, Turkey":        (41.01,  28.95),
    "Dubai, UAE":              (25.20,  55.27),
    "Mumbai, India":           (19.07,  72.88),
    "Shanghai, China":         (31.23, 121.47),
    "Tokyo, Japan":            (35.68, 139.69),
    "New York, USA":           (40.71,  -74.01),
    "Detroit, USA":            (42.33,  -83.05),
    "São Paulo, Brazil":       (-23.55, -46.63),
    "Johannesburg, S. Africa": (-26.20,  28.04),
    "Custom (enter manually)": None
}
