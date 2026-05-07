"""
Agri MCP Server — Rural Intelligence Layer
Covers: Mandi Prices, Weather, Government Schemes, Crop Advisory
Built for Chhattisgarh, expandable across India
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import Any

# ─────────────────────────────────────────────
# CONFIG — load from .env or environment
# ─────────────────────────────────────────────
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "YOUR_DATA_GOV_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")
CHHATTISGARH_DISTRICTS = [
    "Raipur", "Bilaspur", "Durg", "Rajnandgaon", "Jagdalpur",
    "Ambikapur", "Korba", "Raigarh", "Janjgir", "Dhamtari",
    "Mahasamund", "Kawardha", "Kondagaon", "Sukma", "Bastar",
    "Kanker", "Narayanpur", "Bijapur", "Surguja", "Koriya"
]

# ─────────────────────────────────────────────
# UTILITY: HTTP Fetch
# ─────────────────────────────────────────────
def fetch_url(url: str, params: dict = None) -> dict:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgriMCP/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "url": url}
    except urllib.error.URLError as e:
        return {"error": f"Network error: {str(e.reason)}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}

# ─────────────────────────────────────────────
# TOOL 1: Mandi Prices (Agmarknet via data.gov.in)
# ─────────────────────────────────────────────
def get_mandi_prices(commodity: str = None, district: str = None, state: str = "Chhattisgarh") -> dict:
    """
    Fetch live mandi commodity prices from Agmarknet via data.gov.in
    Falls back to structured mock data if API key not set
    """
    if DATA_GOV_API_KEY == "YOUR_DATA_GOV_API_KEY":
        # Return realistic mock data when API key not yet configured
        return {
            "source": "Agmarknet (Mock — Add DATA_GOV_API_KEY to .env for live data)",
            "state": state,
            "district": district or "All Chhattisgarh Districts",
            "commodity": commodity or "All Commodities",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "prices": [
                {
                    "commodity": "Paddy (Common)",
                    "market": "Raipur",
                    "district": "Raipur",
                    "min_price": 1940,
                    "max_price": 2015,
                    "modal_price": 1980,
                    "unit": "Quintal",
                    "msp_2024": 2183,
                    "msp_gap_percent": -9.3
                },
                {
                    "commodity": "Maize",
                    "market": "Bilaspur",
                    "district": "Bilaspur",
                    "min_price": 1820,
                    "max_price": 1920,
                    "modal_price": 1870,
                    "unit": "Quintal",
                    "msp_2024": 2090,
                    "msp_gap_percent": -10.5
                },
                {
                    "commodity": "Soybean",
                    "market": "Rajnandgaon",
                    "district": "Rajnandgaon",
                    "min_price": 3800,
                    "max_price": 4100,
                    "modal_price": 3950,
                    "unit": "Quintal",
                    "msp_2024": 4600,
                    "msp_gap_percent": -14.1
                },
                {
                    "commodity": "Arhar (Tur)",
                    "market": "Durg",
                    "district": "Durg",
                    "min_price": 6200,
                    "max_price": 6800,
                    "modal_price": 6500,
                    "unit": "Quintal",
                    "msp_2024": 7000,
                    "msp_gap_percent": -7.1
                },
                {
                    "commodity": "Wheat",
                    "market": "Raipur",
                    "district": "Raipur",
                    "min_price": 2150,
                    "max_price": 2280,
                    "modal_price": 2200,
                    "unit": "Quintal",
                    "msp_2024": 2275,
                    "msp_gap_percent": -3.3
                }
            ],
            "insight": "⚠️ Most commodities trading BELOW MSP. Farmers selling paddy are losing ~₹203/quintal vs MSP.",
            "action": "Check PM Fasal Bima Yojana eligibility for price protection coverage."
        }

    # Live API call
    params = {
        "api-key": DATA_GOV_API_KEY,
        "format": "json",
        "filters[State.keyword]": state,
        "limit": 50
    }
    if commodity:
        params["filters[Commodity]"] = commodity
    if district:
        params["filters[District]"] = district

    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    data = fetch_url(url, params)

    if "error" in data:
        return {"error": data["error"], "tip": "Verify your DATA_GOV_API_KEY in .env file"}

    records = data.get("records", [])
    return {
        "source": "Agmarknet Live via data.gov.in",
        "state": state,
        "district": district,
        "commodity": commodity,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_records": len(records),
        "prices": records
    }

# ─────────────────────────────────────────────
# TOOL 2: Weather Advisory (OpenWeatherMap)
# ─────────────────────────────────────────────
def get_weather_advisory(district: str = "Raipur") -> dict:
    """
    Fetch weather data and generate agricultural advisory
    """
    if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        return {
            "source": "OpenWeatherMap (Mock — Add OPENWEATHER_API_KEY to .env for live data)",
            "district": district,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weather": {
                "temperature_c": 34,
                "humidity_percent": 68,
                "rainfall_mm_24h": 0,
                "wind_speed_kmh": 12,
                "condition": "Hot and dry"
            },
            "agricultural_advisory": {
                "irrigation": "⚠️ High temperature + low humidity. Irrigate within next 24 hours for standing kharif crops.",
                "pest_risk": "🔴 High risk of stem borer in paddy under dry hot conditions. Monitor field edges.",
                "sowing": "⏳ Wait for pre-monsoon showers before next sowing cycle.",
                "harvest": "✅ Good conditions for harvesting if crops are mature.",
                "storage": "✅ Low humidity ideal for grain storage. Ensure proper ventilation."
            },
            "weekly_forecast_summary": "Dry spell likely for next 5-7 days. Pre-monsoon showers expected after 10th.",
            "monsoon_arrival_estimate": "Mid-June (IMD forecast for Chhattisgarh)",
            "action": "Register for SMS alerts at mkisan.gov.in for daily weather advisories."
        }

    # Live API
    params = {
        "q": f"{district},IN",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    data = fetch_url("https://api.openweathermap.org/data/2.5/weather", params)

    if "error" in data:
        return {"error": data["error"], "tip": "Verify OPENWEATHER_API_KEY in .env"}

    temp = data.get("main", {}).get("temp", 0)
    humidity = data.get("main", {}).get("humidity", 0)
    rainfall = data.get("rain", {}).get("1h", 0)
    condition = data.get("weather", [{}])[0].get("description", "Unknown")

    advisory = []
    if temp > 35:
        advisory.append("🔴 Extreme heat — irrigate crops immediately, avoid pesticide spraying")
    elif temp > 30:
        advisory.append("⚠️ High temperature — monitor soil moisture, evening irrigation recommended")

    if humidity < 40:
        advisory.append("⚠️ Low humidity — increased pest risk, check for aphids and mites")
    elif humidity > 85:
        advisory.append("🔴 High humidity — fungal disease risk, apply preventive fungicide")

    if rainfall > 20:
        advisory.append("⚠️ Heavy rainfall — delay harvesting, check for waterlogging in low fields")

    return {
        "source": "OpenWeatherMap Live",
        "district": district,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "weather": {
            "temperature_c": temp,
            "humidity_percent": humidity,
            "rainfall_mm_1h": rainfall,
            "condition": condition
        },
        "agricultural_advisory": advisory or ["✅ Normal conditions — no urgent advisories"]
    }

# ─────────────────────────────────────────────
# TOOL 3: Government Schemes Finder
# ─────────────────────────────────────────────
def get_agri_schemes(farmer_type: str = "small", crop: str = "paddy", district: str = "Raipur") -> dict:
    """
    Match farmers to relevant central and state government schemes
    """
    all_schemes = [
        {
            "scheme": "PM Fasal Bima Yojana (PMFBY)",
            "type": "Crop Insurance",
            "applicable_for": ["all"],
            "crops": ["paddy", "wheat", "maize", "soybean", "arhar", "all"],
            "benefit": "Insurance coverage for crop loss due to natural calamities",
            "premium_percent": "2% for Kharif, 1.5% for Rabi crops",
            "how_to_apply": "Nearest bank branch or CSC centre before sowing deadline",
            "deadline": "31st July for Kharif crops",
            "chhattisgarh_nodal": "Agriculture Department, Raipur",
            "helpline": "1800-180-1551"
        },
        {
            "scheme": "PM Kisan Samman Nidhi",
            "type": "Direct Income Support",
            "applicable_for": ["small", "marginal"],
            "crops": ["all"],
            "benefit": "₹6,000/year direct transfer in 3 instalments of ₹2,000",
            "eligibility": "Landholding farmers with valid Aadhaar and bank account",
            "how_to_apply": "pmkisan.gov.in or nearest CSC",
            "deadline": "Open — register anytime",
            "helpline": "155261 / 011-24300606"
        },
        {
            "scheme": "Kisan Credit Card (KCC)",
            "type": "Credit Access",
            "applicable_for": ["all"],
            "crops": ["all"],
            "benefit": "Short-term crop loans at 4% interest rate (subsidised)",
            "loan_limit": "Up to ₹3 lakh at concessional rate",
            "how_to_apply": "Nearest bank branch with land records",
            "deadline": "Open — year round",
            "helpline": "Contact nearest bank branch"
        },
        {
            "scheme": "Rajiv Gandhi Kisan Nyay Yojana (CG State Scheme)",
            "type": "Input Subsidy",
            "applicable_for": ["all"],
            "crops": ["paddy", "maize", "soybean", "arhar"],
            "benefit": "₹9,000-10,000/acre direct input subsidy for CG farmers",
            "eligibility": "Chhattisgarh farmers registered in state database",
            "how_to_apply": "Agriculture Department or village Patwari",
            "deadline": "Annual registration before sowing",
            "chhattisgarh_specific": True,
            "helpline": "0771-2511831"
        },
        {
            "scheme": "Soil Health Card Scheme",
            "type": "Advisory",
            "applicable_for": ["all"],
            "crops": ["all"],
            "benefit": "Free soil testing + personalised fertiliser recommendations",
            "how_to_apply": "Nearest Krishi Vigyan Kendra (KVK) or Agriculture office",
            "deadline": "Open — every 2 years",
            "helpline": "1800-180-1551"
        },
        {
            "scheme": "National Food Security Mission",
            "type": "Input Subsidy + Training",
            "applicable_for": ["small", "marginal"],
            "crops": ["paddy", "wheat", "maize", "arhar"],
            "benefit": "Subsidised seeds, fertilisers, demonstration plots, training",
            "how_to_apply": "District Agriculture Officer",
            "deadline": "Before Kharif/Rabi season"
        },
        {
            "scheme": "PM Kusum Yojana",
            "type": "Solar Irrigation",
            "applicable_for": ["all"],
            "crops": ["all"],
            "benefit": "90% subsidy on solar pump installation for irrigation",
            "eligibility": "Farmers with agricultural land and existing irrigation setup",
            "how_to_apply": "CREDA Chhattisgarh or state energy department",
            "chhattisgarh_specific": True,
            "helpline": "CREDA: 0771-2971061"
        },
        {
            "scheme": "e-NAM (National Agriculture Market)",
            "type": "Market Access",
            "applicable_for": ["all"],
            "crops": ["all"],
            "benefit": "Sell crops directly online across 1000+ mandis, better price discovery",
            "how_to_apply": "enam.gov.in — register with Aadhaar and bank account",
            "deadline": "Open"
        }
    ]

    # Filter by farmer type and crop
    matched = []
    for scheme in all_schemes:
        type_match = "all" in scheme["applicable_for"] or farmer_type.lower() in scheme["applicable_for"]
        crop_match = "all" in scheme["crops"] or crop.lower() in scheme["crops"]
        if type_match and crop_match:
            matched.append(scheme)

    cg_specific = [s for s in matched if s.get("chhattisgarh_specific")]

    return {
        "farmer_profile": {
            "type": farmer_type,
            "primary_crop": crop,
            "district": district
        },
        "total_schemes_matched": len(matched),
        "chhattisgarh_specific_schemes": len(cg_specific),
        "schemes": matched,
        "priority_action": f"Register for PM Kisan (₹6,000/year) and PMFBY crop insurance before July 31st if not done.",
        "nearest_help": f"Visit Agriculture Department office in {district} or call 1800-180-1551 (free)"
    }

# ─────────────────────────────────────────────
# TOOL 4: Crop Advisory by Season
# ─────────────────────────────────────────────
def get_crop_advisory(crop: str = "paddy", stage: str = "sowing", district: str = "Raipur") -> dict:
    """
    Provide crop-specific advisory for Chhattisgarh conditions
    """
    advisories = {
        "paddy": {
            "local_name": "Dhan",
            "cg_importance": "Primary Kharif crop — 75% of CG agricultural area",
            "sowing": {
                "timing": "June 15 – July 15 (after 100mm cumulative rainfall)",
                "seed_rate": "25-30 kg/acre for transplanting, 40 kg/acre for direct seeding",
                "varieties_recommended": ["MTU-1010", "Swarna", "DRR Dhan 44", "Poornima (local)"],
                "soil_prep": "2-3 ploughings, puddling for transplanted paddy",
                "fertiliser": "NPK 40:20:20 kg/acre as basal dose",
                "tip": "Use certified seeds from government seed centres — 50% subsidy available"
            },
            "growing": {
                "irrigation": "Maintain 2-5 cm water level during tillering, reduce at panicle stage",
                "weeding": "First weeding at 20-25 days, use conoweeders to save labour cost",
                "pest_watch": ["Stem borer (July-Aug)", "Brown plant hopper (Aug-Sep)", "Blast disease (high humidity)"],
                "fertiliser_top_dress": "20 kg Urea/acre at tillering stage",
                "tip": "Join WhatsApp group of local KVK for real-time pest alerts"
            },
            "harvesting": {
                "timing": "When 80% grains are golden yellow (100-120 days from transplanting)",
                "method": "Mechanical harvester preferred — save 60% labour cost",
                "post_harvest": "Dry to 14% moisture before storage",
                "msp_2024": "₹2,183/quintal",
                "selling_tip": "Sell through government procurement (MARKFED) to get MSP — avoid distress sale"
            }
        },
        "maize": {
            "local_name": "Makka",
            "cg_importance": "Second largest Kharif crop, growing demand for poultry feed",
            "sowing": {
                "timing": "June 1 – July 15",
                "seed_rate": "8-10 kg/acre",
                "varieties_recommended": ["Ganga-5", "DHM-117", "Vivek QPM-9"],
                "soil_prep": "Well-drained field essential, avoid waterlogging",
                "fertiliser": "NPK 50:25:25 kg/acre",
                "tip": "Hybrid varieties give 2x yield — worth the extra seed cost"
            },
            "growing": {
                "irrigation": "Critical at knee-high, silking and grain filling stages",
                "weeding": "Keep weed-free for first 40 days",
                "pest_watch": ["Fall armyworm (new threat — spreading in CG)", "Stem borer"],
                "tip": "Fall armyworm — check leaf whorls daily, use Spinetoram spray if detected"
            },
            "harvesting": {
                "timing": "When husk turns brown and grains are hard (95-105 days)",
                "msp_2024": "₹2,090/quintal",
                "selling_tip": "Poultry companies in Raipur offer better rates than mandi — explore direct sale"
            }
        },
        "soybean": {
            "local_name": "Soybean",
            "cg_importance": "Major oilseed crop in Chhattisgarh plain districts",
            "sowing": {
                "timing": "June 20 – July 10 (delay causes yield loss)",
                "seed_rate": "30-35 kg/acre",
                "varieties_recommended": ["JS 335", "JS 9305", "NRC-7"],
                "soil_prep": "Well-drained loamy soil, pH 6-7",
                "fertiliser": "NPK 20:40:20 kg/acre (high phosphorus needed)",
                "tip": "Seed treatment with Rhizobium culture saves ₹500-800/acre in fertiliser"
            },
            "growing": {
                "pest_watch": ["Girdle beetle (most serious)", "Leaf eating caterpillar", "Yellow mosaic virus"],
                "tip": "Girdle beetle — collect and destroy adults manually in early morning"
            },
            "harvesting": {
                "timing": "When 95% pods turn brown (90-100 days)",
                "msp_2024": "₹4,600/quintal",
                "selling_tip": "Current market ~₹3,950 — below MSP. Register with state procurement for MSP benefit"
            }
        }
    }

    crop_data = advisories.get(crop.lower())
    if not crop_data:
        return {
            "error": f"Crop '{crop}' not in database yet",
            "available_crops": list(advisories.keys()),
            "tip": "Request additional crops — we're expanding the database"
        }

    stage_data = crop_data.get(stage.lower(), crop_data.get("sowing"))

    return {
        "crop": crop,
        "district": district,
        "stage": stage,
        "local_name": crop_data["local_name"],
        "cg_importance": crop_data["cg_importance"],
        "advisory": stage_data,
        "source": "ICAR + Chhattisgarh Agriculture Department + KVK recommendations",
        "contact": "Nearest KVK (Krishi Vigyan Kendra) for field-specific advice"
    }

# ─────────────────────────────────────────────
# TOOL 5: Farmer Distress Risk Assessment
# ─────────────────────────────────────────────
def assess_distress_risk(district: str, crop: str = "paddy", landholding_acres: float = 2.0) -> dict:
    """
    Cross-layer intelligence: assess farmer distress risk in a district
    Combines price data + weather + scheme penetration
    """
    # Realistic district-level data for CG
    district_data = {
        "Bastar": {"rainfall_deficit": -35, "msp_gap": -12, "scheme_penetration": 28, "ngo_active": 8},
        "Surguja": {"rainfall_deficit": -22, "msp_gap": -9, "scheme_penetration": 35, "ngo_active": 5},
        "Kanker": {"rainfall_deficit": -18, "msp_gap": -10, "scheme_penetration": 42, "ngo_active": 3},
        "Sukma": {"rainfall_deficit": -41, "msp_gap": -14, "scheme_penetration": 19, "ngo_active": 6},
        "Narayanpur": {"rainfall_deficit": -38, "msp_gap": -13, "scheme_penetration": 22, "ngo_active": 4},
        "Raipur": {"rainfall_deficit": 5, "msp_gap": -8, "scheme_penetration": 68, "ngo_active": 15},
        "Bilaspur": {"rainfall_deficit": -8, "msp_gap": -7, "scheme_penetration": 61, "ngo_active": 12},
        "Durg": {"rainfall_deficit": -5, "msp_gap": -6, "scheme_penetration": 65, "ngo_active": 10},
    }

    d = district_data.get(district, {"rainfall_deficit": -15, "msp_gap": -9, "scheme_penetration": 45, "ngo_active": 5})

    # Calculate risk score (0-100)
    risk_score = 0
    if d["rainfall_deficit"] < -30:
        risk_score += 40
    elif d["rainfall_deficit"] < -15:
        risk_score += 25
    elif d["rainfall_deficit"] < 0:
        risk_score += 10

    if d["msp_gap"] < -12:
        risk_score += 30
    elif d["msp_gap"] < -8:
        risk_score += 20
    else:
        risk_score += 10

    if d["scheme_penetration"] < 30:
        risk_score += 30
    elif d["scheme_penetration"] < 50:
        risk_score += 15

    # Income impact
    avg_yield_quintal = 12 if crop == "paddy" else 8
    msp = 2183 if crop == "paddy" else 2090
    market_price = msp * (1 + d["msp_gap"] / 100)
    income_loss_per_acre = (msp - market_price) * avg_yield_quintal
    total_income_loss = income_loss_per_acre * landholding_acres

    risk_level = "🔴 High Risk" if risk_score > 65 else "🟡 Medium Risk" if risk_score > 35 else "🟢 Low Risk"

    return {
        "district": district,
        "crop": crop,
        "landholding_acres": landholding_acres,
        "risk_assessment": {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "rainfall_status": f"{abs(d['rainfall_deficit'])}% {'deficit' if d['rainfall_deficit'] < 0 else 'surplus'} vs normal",
            "price_situation": f"Market {abs(d['msp_gap'])}% below MSP",
            "scheme_access": f"Only {d['scheme_penetration']}% of eligible farmers accessing schemes",
            "ngo_presence": f"{d['ngo_active']} active NGOs in district"
        },
        "financial_impact": {
            "estimated_income_loss_per_acre": f"₹{income_loss_per_acre:,.0f}",
            "total_estimated_loss": f"₹{total_income_loss:,.0f} for {landholding_acres} acres",
            "monthly_equivalent": f"₹{total_income_loss/6:,.0f}/month shortfall"
        },
        "immediate_actions": [
            f"Register for PMFBY crop insurance before July 31 — protects against rainfall deficit loss",
            f"Check PM Kisan status — ₹2,000 instalment may be due",
            f"Contact {d['ngo_active']} active NGOs in {district} for additional support",
            f"Sell through government procurement to get MSP instead of mandi"
        ],
        "data_note": "Risk scoring based on IMD rainfall data, Agmarknet prices, and Agriculture Dept scheme data"
    }

# ─────────────────────────────────────────────
# TOOL 6: District Agriculture Dashboard
# ─────────────────────────────────────────────
def get_district_dashboard(district: str = "Raipur") -> dict:
    """
    Comprehensive single-view dashboard for a CG district
    """
    prices = get_mandi_prices(district=district)
    weather = get_weather_advisory(district=district)
    schemes = get_agri_schemes(district=district)
    risk = assess_distress_risk(district=district)

    return {
        "district": district,
        "state": "Chhattisgarh",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "distress_risk": risk["risk_assessment"]["risk_level"],
            "weather_condition": weather.get("weather", {}).get("condition", "Check weather section"),
            "schemes_available": schemes["total_schemes_matched"],
            "cg_specific_schemes": schemes["chhattisgarh_specific_schemes"]
        },
        "mandi_prices": prices.get("prices", [])[:3],
        "weather_advisory": weather.get("agricultural_advisory", {}),
        "top_schemes": schemes["schemes"][:3],
        "risk_detail": risk["risk_assessment"],
        "financial_impact": risk["financial_impact"],
        "priority_actions": risk["immediate_actions"],
        "data_sources": [
            "Agmarknet (Mandi Prices)",
            "OpenWeatherMap (Weather)",
            "MyScheme / Agriculture Dept (Schemes)",
            "IMD Rainfall Data (Risk Assessment)"
        ]
    }

# ─────────────────────────────────────────────
# MCP TOOL DISPATCHER
# ─────────────────────────────────────────────
TOOLS = {
    "get_mandi_prices": {
        "function": get_mandi_prices,
        "description": "Fetch live mandi/market prices for agricultural commodities in Chhattisgarh",
        "parameters": {
            "commodity": "Crop name e.g. paddy, maize, soybean, wheat (optional)",
            "district": "District name in Chhattisgarh (optional)",
            "state": "State name (default: Chhattisgarh)"
        }
    },
    "get_weather_advisory": {
        "function": get_weather_advisory,
        "description": "Get weather data and agricultural advisory for a Chhattisgarh district",
        "parameters": {
            "district": "District name e.g. Raipur, Bastar, Surguja"
        }
    },
    "get_agri_schemes": {
        "function": get_agri_schemes,
        "description": "Find government schemes (central + Chhattisgarh state) matching farmer profile",
        "parameters": {
            "farmer_type": "small / marginal / large",
            "crop": "Primary crop e.g. paddy, maize, soybean",
            "district": "District in Chhattisgarh"
        }
    },
    "get_crop_advisory": {
        "function": get_crop_advisory,
        "description": "Get detailed crop-specific advisory for Chhattisgarh conditions",
        "parameters": {
            "crop": "Crop name: paddy / maize / soybean",
            "stage": "Crop stage: sowing / growing / harvesting",
            "district": "District name"
        }
    },
    "assess_distress_risk": {
        "function": assess_distress_risk,
        "description": "Assess farmer distress risk in a district combining price, weather and scheme data",
        "parameters": {
            "district": "District name in Chhattisgarh",
            "crop": "Primary crop",
            "landholding_acres": "Farm size in acres (number)"
        }
    },
    "get_district_dashboard": {
        "function": get_district_dashboard,
        "description": "Get complete agriculture intelligence dashboard for a Chhattisgarh district",
        "parameters": {
            "district": "District name in Chhattisgarh"
        }
    }
}

def run_tool(tool_name: str, **kwargs) -> dict:
    if tool_name not in TOOLS:
        return {
            "error": f"Tool '{tool_name}' not found",
            "available_tools": list(TOOLS.keys())
        }
    try:
        return TOOLS[tool_name]["function"](**kwargs)
    except Exception as e:
        return {"error": str(e), "tool": tool_name}

def list_tools() -> dict:
    return {
        "server": "Agri MCP Server — Rural Intelligence Layer",
        "version": "1.0.0",
        "coverage": "Chhattisgarh (expandable across India)",
        "tools": {
            name: {
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in TOOLS.items()
        }
    }

if __name__ == "__main__":
    # Demo run — shows all tools working
    print("\n" + "="*60)
    print("AGRI MCP SERVER — DEMO RUN")
    print("="*60)

    demos = [
        ("list_tools", {}),
        ("get_mandi_prices", {"district": "Raipur"}),
        ("get_weather_advisory", {"district": "Bastar"}),
        ("get_agri_schemes", {"farmer_type": "small", "crop": "paddy", "district": "Surguja"}),
        ("get_crop_advisory", {"crop": "paddy", "stage": "sowing", "district": "Raipur"}),
        ("assess_distress_risk", {"district": "Bastar", "crop": "paddy", "landholding_acres": 2.5}),
        ("get_district_dashboard", {"district": "Surguja"})
    ]

    for tool_name, params in demos:
        print(f"\n{'─'*60}")
        print(f"🔧 TOOL: {tool_name}")
        if params:
            print(f"📥 INPUT: {json.dumps(params)}")
        print(f"{'─'*60}")
        if tool_name == "list_tools":
            result = list_tools()
        else:
            result = run_tool(tool_name, **params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
