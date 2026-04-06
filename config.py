FACTORY_PRESETS = {
    "⚙️ CNC Machining / Auto Parts": {
        "machines": 10, "workers": 30, "hours": 8,
        "product_price": 220.0, "material_cost": 80.0,
        "energy_cost": 0.13, "worker_daily_cost": 110.0,
        "industry": "machining", "unit": "part",
        "production_rate": 8.0,
        "energy_kw_per_machine": 12.0,
        "description": "CNC mills, lathes, drilling. Based on UCI AI4I 2020 dataset."
    },
    "🔩 Steel / Metal Fabrication": {
        "machines": 18, "workers": 50, "hours": 12,
        "product_price": 310.0, "material_cost": 140.0,
        "energy_cost": 0.15, "worker_daily_cost": 95.0,
        "industry": "steel", "unit": "ton",
        "production_rate": 2.0,
        "energy_kw_per_machine": 85.0,
        "description": "Rolling mills, welding lines, press brakes."
    },
    "✈️ Aerospace & Precision Parts": {
        "machines": 8, "workers": 25, "hours": 8,
        "product_price": 1800.0, "material_cost": 600.0,
        "energy_cost": 0.18, "worker_daily_cost": 160.0,
        "industry": "aerospace", "unit": "component",
        "production_rate": 1.5,
        "energy_kw_per_machine": 18.0,
        "description": "High-precision machining, strict quality tolerances."
    },
    "🚗 Automotive Assembly": {
        "machines": 45, "workers": 120, "hours": 16,
        "product_price": 4200.0, "material_cost": 2100.0,
        "energy_cost": 0.14, "worker_daily_cost": 105.0,
        "industry": "automotive", "unit": "vehicle",
        "production_rate": 0.5,
        "energy_kw_per_machine": 40.0,
        "description": "Assembly lines, stamping, body-in-white operations."
    },
    "💻 Electronics / PCB Manufacturing": {
        "machines": 15, "workers": 35, "hours": 8,
        "product_price": 250.0, "material_cost": 90.0,
        "energy_cost": 0.18, "worker_daily_cost": 100.0,
        "industry": "electronics", "unit": "board",
        "production_rate": 25.0,
        "energy_kw_per_machine": 8.0,
        "description": "SMT lines, wave soldering, PCB assembly."
    },
    "🔬 Semiconductor / Microchip": {
        "machines": 20, "workers": 60, "hours": 24,
        "product_price": 850.0, "material_cost": 280.0,
        "energy_cost": 0.22, "worker_daily_cost": 140.0,
        "industry": "semiconductor", "unit": "wafer",
        "production_rate": 0.8,
        "energy_kw_per_machine": 120.0,
        "description": "Cleanroom fab, lithography, etching. 24/7 operation."
    },
    "👕 Textile / Clothing": {
        "machines": 30, "workers": 80, "hours": 10,
        "product_price": 35.0, "material_cost": 15.0,
        "energy_cost": 0.09, "worker_daily_cost": 60.0,
        "industry": "textile", "unit": "garment",
        "production_rate": 15.0,
        "energy_kw_per_machine": 3.5,
        "description": "Weaving, cutting, sewing lines."
    },
    "🍕 Food & Beverage Processing": {
        "machines": 12, "workers": 40, "hours": 16,
        "product_price": 55.0, "material_cost": 25.0,
        "energy_cost": 0.12, "worker_daily_cost": 75.0,
        "industry": "food", "unit": "batch",
        "production_rate": 4.0,
        "energy_kw_per_machine": 22.0,
        "description": "Continuous processing lines, cold chain, HACCP regulated."
    },
    "💊 Pharmaceutical / Medical": {
        "machines": 10, "workers": 45, "hours": 16,
        "product_price": 1200.0, "material_cost": 350.0,
        "energy_cost": 0.20, "worker_daily_cost": 130.0,
        "industry": "pharma", "unit": "batch",
        "production_rate": 0.5,
        "energy_kw_per_machine": 35.0,
        "description": "GMP-regulated, FDA/EMA compliance, strict contamination control."
    },
    "🧪 Chemical / Petrochemical": {
        "machines": 25, "workers": 55, "hours": 24,
        "product_price": 480.0, "material_cost": 180.0,
        "energy_cost": 0.16, "worker_daily_cost": 120.0,
        "industry": "chemical", "unit": "ton",
        "production_rate": 3.0,
        "energy_kw_per_machine": 75.0,
        "description": "Reactors, distillation columns, pumps. 24/7 continuous process."
    },
    "🛢️ Oil & Gas Refinery": {
        "machines": 60, "workers": 150, "hours": 24,
        "product_price": 890.0, "material_cost": 420.0,
        "energy_cost": 0.11, "worker_daily_cost": 180.0,
        "industry": "oil_gas", "unit": "barrel",
        "production_rate": 8.0,
        "energy_kw_per_machine": 150.0,
        "description": "Refining, cracking, separation units. High safety criticality."
    },
    "🏗️ Cement / Building Materials": {
        "machines": 20, "workers": 45, "hours": 24,
        "product_price": 85.0, "material_cost": 28.0,
        "energy_cost": 0.11, "worker_daily_cost": 80.0,
        "industry": "cement", "unit": "ton",
        "production_rate": 5.0,
        "energy_kw_per_machine": 200.0,
        "description": "Kilns, mills, crushers. Very energy-intensive operation."
    },
    "🌲 Wood / Furniture / Pulp": {
        "machines": 22, "workers": 55, "hours": 10,
        "product_price": 420.0, "material_cost": 160.0,
        "energy_cost": 0.10, "worker_daily_cost": 70.0,
        "industry": "wood", "unit": "piece",
        "production_rate": 6.0,
        "energy_kw_per_machine": 15.0,
        "description": "Sawmills, CNC routers, finishing lines."
    },
    "📦 Packaging / Plastics": {
        "machines": 18, "workers": 40, "hours": 16,
        "product_price": 12.0, "material_cost": 4.5,
        "energy_cost": 0.13, "worker_daily_cost": 72.0,
        "industry": "packaging", "unit": "1000 units",
        "production_rate": 3.0,
        "energy_kw_per_machine": 30.0,
        "description": "Injection moulding, blow moulding, thermoforming."
    },
    "⛏️ Mining / Quarrying": {
        "machines": 35, "workers": 90, "hours": 20,
        "product_price": 190.0, "material_cost": 50.0,
        "energy_cost": 0.13, "worker_daily_cost": 130.0,
        "industry": "mining", "unit": "ton",
        "production_rate": 4.0,
        "energy_kw_per_machine": 55.0,
        "description": "Crushers, conveyors, drill rigs. High safety risk environment."
    },
    "🔧 Custom (Enter Your Own)": {
        "machines": 5, "workers": 20, "hours": 8,
        "product_price": 100.0, "material_cost": 40.0,
        "energy_cost": 0.10, "worker_daily_cost": 80.0,
        "industry": "custom", "unit": "unit",
        "production_rate": 10.0,
        "energy_kw_per_machine": 15.0,
        "description": "Configure every parameter for your specific factory."
    },
}

CURRENCIES = {
    "€ Euro":                 {"symbol": "€",   "code": "EUR", "rate": 1.00},
    "$ US Dollar":            {"symbol": "$",   "code": "USD", "rate": 1.09},
    "£ British Pound":        {"symbol": "£",   "code": "GBP", "rate": 0.86},
    "MAD Moroccan Dirham":    {"symbol": "MAD", "code": "MAD", "rate": 10.92},
    "TND Tunisian Dinar":     {"symbol": "TND", "code": "TND", "rate": 3.38},
    "DZD Algerian Dinar":     {"symbol": "DZD", "code": "DZD", "rate": 147.2},
    "EGP Egyptian Pound":     {"symbol": "EGP", "code": "EGP", "rate": 33.5},
    "AED UAE Dirham":         {"symbol": "AED", "code": "AED", "rate": 4.00},
    "SAR Saudi Riyal":        {"symbol": "SAR", "code": "SAR", "rate": 4.09},
    "INR Indian Rupee":       {"symbol": "₹",   "code": "INR", "rate": 90.8},
    "CNY Chinese Yuan":       {"symbol": "¥",   "code": "CNY", "rate": 7.89},
    "BRL Brazilian Real":     {"symbol": "R$",  "code": "BRL", "rate": 5.42},
    "ZAR South African Rand": {"symbol": "R",   "code": "ZAR", "rate": 20.2},
    "TRY Turkish Lira":       {"symbol": "₺",   "code": "TRY", "rate": 35.1},
}

RISK_THRESHOLDS = {
    "failure_prob": {
        "low":      (0,     0.01),
        "medium":   (0.01,  0.05),
        "high":     (0.05,  0.15),
        "critical": (0.15,  1.01)
    },
    "tool_wear": {
        "low":      (0,     80),
        "medium":   (80,    160),
        "high":     (160,   220),
        "critical": (220,   99999)
    },
    "temp_diff": {
        "low":      (0,     8),
        "medium":   (8,     11),
        "high":     (11,    13),
        "critical": (13,    99999)
    },
    "energy_mult": {
        "low":      (0,     1.2),
        "medium":   (1.2,   1.5),
        "high":     (1.5,   2.0),
        "critical": (2.0,   99999)
    },
    "demand": {
        "low":      (1.2,   99999),
        "medium":   (0.8,   1.2),
        "high":     (0.6,   0.8),
        "critical": (0,     0.6)
    },
    "material_mult": {
        "low":      (0,     1.2),
        "medium":   (1.2,   1.5),
        "high":     (1.5,   2.0),
        "critical": (2.0,   99999)
    },
    "torque": {
        "low":      (0,     30),
        "medium":   (30,    45),
        "high":     (45,    60),
        "critical": (60,    99999)
    }
}

RISK_COLORS = {
    "low":      "#00ff87",
    "medium":   "#f59e0b",
    "high":     "#ff6b35",
    "critical": "#ff4757"
}

RISK_EMOJIS = {
    "low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"
}
