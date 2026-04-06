INDUSTRY_PROFILES = {

    "machining": {
        "name": "CNC Machining / Auto Parts",
        "icon": "⚙️",
        "oee_world_class":    85,
        "oee_industry_avg":   60,
        "oee_poor":           40,
        "mtbf_hours":         720,
        "mttr_hours":         4,
        "target_scrap_rate":  0.02,
        "target_rework_rate": 0.05,
        "compliance": [
            {"name": "ISO 9001:2015", "area": "Quality Management",  "critical": True},
            {"name": "IATF 16949",    "area": "Automotive Quality",  "critical": True},
            {"name": "ISO 45001",     "area": "Occupational Safety", "critical": False},
            {"name": "ISO 14001",     "area": "Environmental Mgmt",  "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.5,
            "Tool Wear & Maintenance":   1.4,
            "Thermal Stress":            1.2,
            "Energy Cost":               1.0,
            "Market Demand":             1.0,
            "Supply Chain / Materials":  1.1,
            "Machine Overload (Torque)": 1.3,
        },
        "typical_failures": [
            "Tool breakage (38%)", "Bearing failure (22%)",
            "Spindle overheating (18%)", "Coolant system (12%)", "Other (10%)"
        ],
        "key_kpis": ["OEE", "MTBF", "MTTR", "First Pass Yield", "Tool Life", "Scrap Rate"],
        "industry_tip": "In machining, tool wear is the #1 hidden cost. Tracking tool life per operation saves 15-25% on tooling costs.",
    },

    "steel": {
        "name": "Steel / Metal Fabrication",
        "icon": "🔩",
        "oee_world_class":    80,
        "oee_industry_avg":   55,
        "oee_poor":           35,
        "mtbf_hours":         500,
        "mttr_hours":         8,
        "target_scrap_rate":  0.04,
        "target_rework_rate": 0.08,
        "compliance": [
            {"name": "ISO 9001:2015", "area": "Quality Management",   "critical": True},
            {"name": "EN 10204",      "area": "Material Certificates", "critical": True},
            {"name": "ISO 45001",     "area": "Occupational Safety",   "critical": True},
            {"name": "ISO 14001",     "area": "Environmental Mgmt",    "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.3,
            "Tool Wear & Maintenance":   1.2,
            "Thermal Stress":            1.5,
            "Energy Cost":               1.8,
            "Market Demand":             1.1,
            "Supply Chain / Materials":  1.4,
            "Machine Overload (Torque)": 1.4,
        },
        "typical_failures": [
            "Roll/die wear (31%)", "Motor overload (25%)",
            "Hydraulic failure (20%)", "Furnace issues (14%)", "Other (10%)"
        ],
        "key_kpis": ["OEE", "Energy Intensity (kWh/ton)", "Yield Loss", "MTBF", "CO₂/ton"],
        "industry_tip": "Steel is extremely energy-intensive. A 10% reduction in energy cost often requires shifting operations to off-peak hours (night/weekend).",
    },

    "aerospace": {
        "name": "Aerospace & Precision Parts",
        "icon": "✈️",
        "oee_world_class":    75,
        "oee_industry_avg":   50,
        "oee_poor":           30,
        "mtbf_hours":         1200,
        "mttr_hours":         12,
        "target_scrap_rate":  0.005,
        "target_rework_rate": 0.01,
        "compliance": [
            {"name": "AS9100 Rev D",  "area": "Aerospace Quality",   "critical": True},
            {"name": "NADCAP",        "area": "Special Processes",   "critical": True},
            {"name": "FAR Part 21",   "area": "FAA Certification",   "critical": True},
            {"name": "ISO 9001:2015", "area": "Quality Management",  "critical": True},
            {"name": "ITAR",          "area": "Export Control",      "critical": True},
            {"name": "ISO 45001",     "area": "Occupational Safety", "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.2,
            "Tool Wear & Maintenance":   1.8,
            "Thermal Stress":            1.5,
            "Energy Cost":               0.8,
            "Market Demand":             0.9,
            "Supply Chain / Materials":  1.6,
            "Machine Overload (Torque)": 1.6,
        },
        "typical_failures": [
            "Dimensional non-conformance (42%)", "Surface finish failure (28%)",
            "Material cert issues (15%)", "Machine calibration drift (10%)", "Other (5%)"
        ],
        "key_kpis": ["First Pass Yield", "MTBF", "CPK/PPK", "On-Time Delivery", "Cost of Quality"],
        "industry_tip": "Aerospace has near-zero tolerance for defects. A single non-conforming part can ground a fleet. Invest in real-time SPC (Statistical Process Control).",
    },

    "automotive": {
        "name": "Automotive Assembly",
        "icon": "🚗",
        "oee_world_class":    90,
        "oee_industry_avg":   70,
        "oee_poor":           50,
        "mtbf_hours":         400,
        "mttr_hours":         2,
        "target_scrap_rate":  0.01,
        "target_rework_rate": 0.03,
        "compliance": [
            {"name": "IATF 16949",    "area": "Automotive Quality", "critical": True},
            {"name": "ISO 9001:2015", "area": "Quality Management", "critical": True},
            {"name": "OSHA 1910",     "area": "Workplace Safety",   "critical": True},
            {"name": "ISO 14001",     "area": "Environmental Mgmt", "critical": True},
            {"name": "VDA 6.3",       "area": "Process Audit",      "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.8,
            "Tool Wear & Maintenance":   1.2,
            "Thermal Stress":            1.0,
            "Energy Cost":               1.1,
            "Market Demand":             1.5,
            "Supply Chain / Materials":  1.8,
            "Machine Overload (Torque)": 1.1,
        },
        "typical_failures": [
            "Robot arm failure (29%)", "Conveyor breakdown (24%)",
            "Weld quality issue (22%)", "Paint defect (15%)", "Other (10%)"
        ],
        "key_kpis": ["Takt Time", "Line Efficiency", "JPH (Jobs Per Hour)", "FTT", "MTTR"],
        "industry_tip": "Automotive runs on Takt Time — every second of downtime ripples down the line. Aim for MTTR under 10 minutes through standardized repair kits at each station.",
    },

    "electronics": {
        "name": "Electronics / PCB Manufacturing",
        "icon": "💻",
        "oee_world_class":    85,
        "oee_industry_avg":   62,
        "oee_poor":           40,
        "mtbf_hours":         900,
        "mttr_hours":         3,
        "target_scrap_rate":  0.01,
        "target_rework_rate": 0.04,
        "compliance": [
            {"name": "IPC-A-610",      "area": "PCB Acceptability",    "critical": True},
            {"name": "ISO 9001:2015",  "area": "Quality Management",   "critical": True},
            {"name": "RoHS Directive", "area": "Hazardous Substances", "critical": True},
            {"name": "IEC 61340",      "area": "ESD Control",          "critical": True},
            {"name": "ISO 14001",      "area": "Environmental Mgmt",   "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.3,
            "Tool Wear & Maintenance":   1.1,
            "Thermal Stress":            1.6,
            "Energy Cost":               1.2,
            "Market Demand":             1.4,
            "Supply Chain / Materials":  1.7,
            "Machine Overload (Torque)": 0.8,
        },
        "typical_failures": [
            "Solder defect (35%)", "Component placement error (25%)",
            "AOI false reject (18%)", "Stencil clogging (12%)", "Other (10%)"
        ],
        "key_kpis": ["DPMO", "First Pass Yield", "Solder Defect Rate", "OEE", "Component Shortage Days"],
        "industry_tip": "Component shortages can halt lines with no warning. Maintain a 6-week buffer for critical ICs and monitor lead times weekly.",
    },

    "semiconductor": {
        "name": "Semiconductor / Microchip",
        "icon": "🔬",
        "oee_world_class":    80,
        "oee_industry_avg":   55,
        "oee_poor":           30,
        "mtbf_hours":         2000,
        "mttr_hours":         24,
        "target_scrap_rate":  0.003,
        "target_rework_rate": 0.005,
        "compliance": [
            {"name": "SEMI Standards", "area": "Equipment Interfaces", "critical": True},
            {"name": "ISO 9001:2015",  "area": "Quality Management",   "critical": True},
            {"name": "ITAR",           "area": "Export Control",        "critical": True},
            {"name": "ISO 14644",      "area": "Cleanroom Standards",   "critical": True},
            {"name": "OSHA Hazmat",    "area": "Chemical Safety",       "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.5,
            "Tool Wear & Maintenance":   2.0,
            "Thermal Stress":            1.8,
            "Energy Cost":               1.6,
            "Market Demand":             1.0,
            "Supply Chain / Materials":  1.5,
            "Machine Overload (Torque)": 1.0,
        },
        "typical_failures": [
            "Particle contamination (38%)", "Lithography misalignment (27%)",
            "Etch uniformity (18%)", "Equipment drift (12%)", "Other (5%)"
        ],
        "key_kpis": ["Wafer Start Rate", "Die Yield", "DPMO", "Cycle Time", "Cleanroom Class"],
        "industry_tip": "A single particle in a cleanroom can destroy an entire wafer lot worth hundreds of thousands. Particle monitoring frequency directly correlates with yield.",
    },

    "textile": {
        "name": "Textile / Clothing",
        "icon": "👕",
        "oee_world_class":    75,
        "oee_industry_avg":   52,
        "oee_poor":           35,
        "mtbf_hours":         300,
        "mttr_hours":         1,
        "target_scrap_rate":  0.05,
        "target_rework_rate": 0.10,
        "compliance": [
            {"name": "OEKO-TEX Std 100", "area": "Chemical Safety",      "critical": True},
            {"name": "ISO 9001:2015",    "area": "Quality Management",   "critical": False},
            {"name": "SA8000",           "area": "Social Accountability", "critical": True},
            {"name": "GOTS",             "area": "Organic Textile",      "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.1,
            "Tool Wear & Maintenance":   1.0,
            "Thermal Stress":            1.0,
            "Energy Cost":               1.3,
            "Market Demand":             1.8,
            "Supply Chain / Materials":  1.6,
            "Machine Overload (Torque)": 0.8,
        },
        "typical_failures": [
            "Yarn breakage (33%)", "Needle/loom jam (28%)",
            "Tension inconsistency (20%)", "Motor failure (12%)", "Other (7%)"
        ],
        "key_kpis": ["Efficiency %", "Defect Rate (DHU)", "On-Time Delivery", "Energy/garment", "Labour Productivity"],
        "industry_tip": "In garment manufacturing, labour productivity (pieces per worker per hour) is the most controllable KPI. A 10% improvement there outweighs all machinery investments.",
    },

    "food": {
        "name": "Food & Beverage Processing",
        "icon": "🍕",
        "oee_world_class":    85,
        "oee_industry_avg":   65,
        "oee_poor":           45,
        "mtbf_hours":         400,
        "mttr_hours":         2,
        "target_scrap_rate":  0.03,
        "target_rework_rate": 0.02,
        "compliance": [
            {"name": "HACCP",          "area": "Food Safety",        "critical": True},
            {"name": "ISO 22000",      "area": "Food Safety Mgmt",   "critical": True},
            {"name": "BRC/FSSC 22000", "area": "Retailer Standard",  "critical": True},
            {"name": "FDA 21 CFR",     "area": "US Food Regulation", "critical": False},
            {"name": "EU 178/2002",    "area": "EU Food Law",        "critical": False},
            {"name": "ISO 14001",      "area": "Environmental Mgmt", "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.3,
            "Tool Wear & Maintenance":   1.1,
            "Thermal Stress":            1.8,
            "Energy Cost":               1.4,
            "Market Demand":             1.2,
            "Supply Chain / Materials":  1.5,
            "Machine Overload (Torque)": 0.9,
        },
        "typical_failures": [
            "Filling/packaging jam (30%)", "Temperature excursion (25%)",
            "CIP (cleaning) overrun (20%)", "Conveyor breakdown (15%)", "Other (10%)"
        ],
        "key_kpis": ["OEE", "Line Efficiency", "Waste %", "CCP Compliance", "Energy/batch", "Allergen Control"],
        "industry_tip": "Temperature is a Critical Control Point (CCP) in food. An undetected excursion doesn't just cost product — it can trigger a full recall. Invest in real-time temp monitoring.",
    },

    "pharma": {
        "name": "Pharmaceutical / Medical",
        "icon": "💊",
        "oee_world_class":    80,
        "oee_industry_avg":   50,
        "oee_poor":           30,
        "mtbf_hours":         1000,
        "mttr_hours":         8,
        "target_scrap_rate":  0.005,
        "target_rework_rate": 0.005,
        "compliance": [
            {"name": "GMP (EU Annex 1)",    "area": "Good Manufacturing",     "critical": True},
            {"name": "FDA 21 CFR Part 211", "area": "US Drug Manufacturing",  "critical": True},
            {"name": "ISO 13485",           "area": "Medical Devices",        "critical": True},
            {"name": "ICH Q10",             "area": "Pharma Quality System",  "critical": True},
            {"name": "GAMP 5",              "area": "Computerized Systems",   "critical": True},
            {"name": "EMA Guidelines",      "area": "EU Drug Regulation",     "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.2,
            "Tool Wear & Maintenance":   1.5,
            "Thermal Stress":            2.0,
            "Energy Cost":               1.0,
            "Market Demand":             1.0,
            "Supply Chain / Materials":  2.0,
            "Machine Overload (Torque)": 1.0,
        },
        "typical_failures": [
            "Cross-contamination risk (35%)", "Batch documentation error (28%)",
            "Environmental monitoring excursion (20%)", "Equipment calibration (12%)", "Other (5%)"
        ],
        "key_kpis": ["Batch Success Rate", "Right First Time", "OOS Rate", "CAPA Closure", "Regulatory Compliance %"],
        "industry_tip": "In pharma, every deviation must be documented and investigated. Unplanned deviations that delay batch release cost more than the batch itself. Build digital deviation tracking.",
    },

    "chemical": {
        "name": "Chemical / Petrochemical",
        "icon": "🧪",
        "oee_world_class":    88,
        "oee_industry_avg":   70,
        "oee_poor":           50,
        "mtbf_hours":         1500,
        "mttr_hours":         12,
        "target_scrap_rate":  0.02,
        "target_rework_rate": 0.01,
        "compliance": [
            {"name": "ATEX Directive",  "area": "Explosive Atmospheres", "critical": True},
            {"name": "REACH",           "area": "Chemical Registration",  "critical": True},
            {"name": "ISO 45001",       "area": "Occupational Safety",    "critical": True},
            {"name": "PSM (OSHA 3132)", "area": "Process Safety Mgmt",   "critical": True},
            {"name": "ISO 14001",       "area": "Environmental Mgmt",    "critical": True},
            {"name": "ISO 9001:2015",   "area": "Quality Management",    "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.6,
            "Tool Wear & Maintenance":   1.4,
            "Thermal Stress":            1.8,
            "Energy Cost":               1.7,
            "Market Demand":             1.0,
            "Supply Chain / Materials":  1.3,
            "Machine Overload (Torque)": 1.3,
        },
        "typical_failures": [
            "Pump/seal failure (32%)", "Heat exchanger fouling (26%)",
            "Valve malfunction (20%)", "Instrumentation drift (14%)", "Other (8%)"
        ],
        "key_kpis": ["Process Safety Events", "LOPC (Loss of Primary Containment)", "Energy Intensity", "OEE", "Environmental Incidents"],
        "industry_tip": "Process safety incidents in chemical plants can have catastrophic consequences. Implement a real-time pressure/temperature monitoring system with automatic shutdowns.",
    },

    "oil_gas": {
        "name": "Oil & Gas Refinery",
        "icon": "🛢️",
        "oee_world_class":    92,
        "oee_industry_avg":   75,
        "oee_poor":           55,
        "mtbf_hours":         8760,
        "mttr_hours":         48,
        "target_scrap_rate":  0.01,
        "target_rework_rate": 0.005,
        "compliance": [
            {"name": "API Standards",   "area": "Petroleum Equipment",   "critical": True},
            {"name": "ISO 45001",       "area": "Occupational Safety",   "critical": True},
            {"name": "ATEX/IECEx",      "area": "Explosive Atmospheres", "critical": True},
            {"name": "PSM (OSHA 3132)", "area": "Process Safety",        "critical": True},
            {"name": "ISO 14001",       "area": "Environmental Mgmt",    "critical": True},
            {"name": "REACH",           "area": "Chemical Registration",  "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.5,
            "Tool Wear & Maintenance":   1.3,
            "Thermal Stress":            1.7,
            "Energy Cost":               1.0,
            "Market Demand":             1.8,
            "Supply Chain / Materials":  1.2,
            "Machine Overload (Torque)": 1.4,
        },
        "typical_failures": [
            "Rotating equipment failure (30%)", "Corrosion/fouling (27%)",
            "Instrumentation failure (22%)", "Valve/piping (14%)", "Other (7%)"
        ],
        "key_kpis": ["On-Stream Factor", "Solomon EII", "Energy Intensity", "Safety Incidents", "Throughput"],
        "industry_tip": "Refineries plan major shutdowns (turnarounds) every 3-5 years. The cost of an unplanned shutdown is 10-50x higher than a planned one. Condition monitoring is the key investment.",
    },

    "cement": {
        "name": "Cement / Building Materials",
        "icon": "🏗️",
        "oee_world_class":    85,
        "oee_industry_avg":   68,
        "oee_poor":           48,
        "mtbf_hours":         2000,
        "mttr_hours":         24,
        "target_scrap_rate":  0.03,
        "target_rework_rate": 0.01,
        "compliance": [
            {"name": "EN 197",        "area": "Cement Standards",    "critical": True},
            {"name": "ISO 9001:2015", "area": "Quality Management",  "critical": True},
            {"name": "ISO 14001",     "area": "Environmental Mgmt",  "critical": True},
            {"name": "EU ETS",        "area": "Carbon Trading",      "critical": True},
            {"name": "ISO 45001",     "area": "Occupational Safety", "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.4,
            "Tool Wear & Maintenance":   1.5,
            "Thermal Stress":            1.7,
            "Energy Cost":               2.0,
            "Market Demand":             1.3,
            "Supply Chain / Materials":  1.2,
            "Machine Overload (Torque)": 1.3,
        },
        "typical_failures": [
            "Kiln refractory wear (35%)", "Mill liner wear (28%)",
            "Fan/blower failure (18%)", "Crusher jam (12%)", "Other (7%)"
        ],
        "key_kpis": ["Clinker Factor", "Heat Consumption (kcal/kg)", "CO₂/ton", "OEE", "Energy Intensity"],
        "industry_tip": "Energy is 30-40% of cement production cost. Optimizing kiln fuel mix and pre-heater efficiency delivers the biggest savings — often €2-5/ton of cement.",
    },

    "wood": {
        "name": "Wood / Furniture / Pulp",
        "icon": "🌲",
        "oee_world_class":    78,
        "oee_industry_avg":   58,
        "oee_poor":           38,
        "mtbf_hours":         400,
        "mttr_hours":         3,
        "target_scrap_rate":  0.06,
        "target_rework_rate": 0.08,
        "compliance": [
            {"name": "FSC / PEFC",    "area": "Sustainable Forestry",  "critical": True},
            {"name": "CARB Phase 2",  "area": "Formaldehyde Emission", "critical": True},
            {"name": "EN 14342",      "area": "Wood Floor Products",   "critical": False},
            {"name": "ISO 9001:2015", "area": "Quality Management",    "critical": False},
            {"name": "ISO 45001",     "area": "Occupational Safety",   "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.2,
            "Tool Wear & Maintenance":   1.6,
            "Thermal Stress":            1.1,
            "Energy Cost":               1.3,
            "Market Demand":             1.4,
            "Supply Chain / Materials":  1.5,
            "Machine Overload (Torque)": 1.3,
        },
        "typical_failures": [
            "Blade/bit wear (36%)", "Dust extraction blockage (24%)",
            "Feed system jam (20%)", "Motor overload (13%)", "Other (7%)"
        ],
        "key_kpis": ["Wood Recovery Rate", "Blade Life", "Defect Rate", "OEE", "Energy/m³"],
        "industry_tip": "Wood recovery rate (usable output vs raw input) directly drives profitability. Optimizing cut patterns with nesting software typically improves recovery by 5-12%.",
    },

    "packaging": {
        "name": "Packaging / Plastics",
        "icon": "📦",
        "oee_world_class":    85,
        "oee_industry_avg":   65,
        "oee_poor":           45,
        "mtbf_hours":         600,
        "mttr_hours":         2,
        "target_scrap_rate":  0.03,
        "target_rework_rate": 0.05,
        "compliance": [
            {"name": "ISO 9001:2015",    "area": "Quality Management",   "critical": True},
            {"name": "EU Packaging Dir", "area": "Packaging & Waste",    "critical": True},
            {"name": "FDA 21 CFR 177",   "area": "Food Contact Plastics", "critical": False},
            {"name": "ISO 14001",        "area": "Environmental Mgmt",   "critical": True},
            {"name": "REACH",            "area": "Chemical Registration", "critical": True},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.3,
            "Tool Wear & Maintenance":   1.4,
            "Thermal Stress":            1.5,
            "Energy Cost":               1.4,
            "Market Demand":             1.3,
            "Supply Chain / Materials":  1.5,
            "Machine Overload (Torque)": 1.1,
        },
        "typical_failures": [
            "Mould fouling/damage (30%)", "Resin contamination (25%)",
            "Temperature inconsistency (22%)", "Ejector failure (14%)", "Other (9%)"
        ],
        "key_kpis": ["Cycle Time", "Cavity Efficiency", "Scrap Rate", "OEE", "Energy/kg"],
        "industry_tip": "In injection moulding, cycle time is everything. A 1-second reduction per cycle on a 10-second cycle = 10% more output with zero extra cost.",
    },

    "mining": {
        "name": "Mining / Quarrying",
        "icon": "⛏️",
        "oee_world_class":    70,
        "oee_industry_avg":   48,
        "oee_poor":           28,
        "mtbf_hours":         350,
        "mttr_hours":         6,
        "target_scrap_rate":  0.10,
        "target_rework_rate": 0.05,
        "compliance": [
            {"name": "MSHA (30 CFR)",       "area": "Mine Safety",           "critical": True},
            {"name": "ISO 45001",           "area": "Occupational Safety",   "critical": True},
            {"name": "ISO 14001",           "area": "Environmental Mgmt",    "critical": True},
            {"name": "IFC Performance Stds","area": "Environmental/Social",  "critical": True},
            {"name": "ISO 9001:2015",       "area": "Quality Management",    "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.7,
            "Tool Wear & Maintenance":   1.8,
            "Thermal Stress":            1.2,
            "Energy Cost":               1.6,
            "Market Demand":             1.3,
            "Supply Chain / Materials":  1.4,
            "Machine Overload (Torque)": 1.6,
        },
        "typical_failures": [
            "Wear part failure (38%)", "Conveyor breakdown (25%)",
            "Crusher/screen jam (18%)", "Haul truck breakdown (12%)", "Other (7%)"
        ],
        "key_kpis": ["Availability", "Utilization", "Recovery Rate", "Energy/ton", "Safety LTI Rate"],
        "industry_tip": "In mining, wear parts (crusher liners, conveyor belts, drill bits) account for 40-60% of maintenance costs. Condition monitoring and CBM (Condition-Based Maintenance) pay for themselves in months.",
    },

    "custom": {
        "name": "Custom Factory",
        "icon": "🔧",
        "oee_world_class":    85,
        "oee_industry_avg":   60,
        "oee_poor":           40,
        "mtbf_hours":         500,
        "mttr_hours":         4,
        "target_scrap_rate":  0.03,
        "target_rework_rate": 0.05,
        "compliance": [
            {"name": "ISO 9001:2015", "area": "Quality Management", "critical": True},
            {"name": "ISO 45001",     "area": "Occupational Safety","critical": True},
            {"name": "ISO 14001",     "area": "Environmental Mgmt", "critical": False},
        ],
        "risk_weights": {
            "Machine Failure Risk":      1.0,
            "Tool Wear & Maintenance":   1.0,
            "Thermal Stress":            1.0,
            "Energy Cost":               1.0,
            "Market Demand":             1.0,
            "Supply Chain / Materials":  1.0,
            "Machine Overload (Torque)": 1.0,
        },
        "typical_failures": [
            "Mechanical failure (35%)", "Electrical failure (25%)",
            "Operator error (20%)", "Process variation (12%)", "Other (8%)"
        ],
        "key_kpis": ["OEE", "MTBF", "MTTR", "Scrap Rate", "On-Time Delivery"],
        "industry_tip": "Start by measuring OEE. Most factories discover their real OEE is 30-50% lower than they thought — and the gap is pure recoverable profit.",
    },
}


def get_profile(industry_key: str) -> dict:
    return INDUSTRY_PROFILES.get(industry_key, INDUSTRY_PROFILES["custom"])


def get_compliance_status(profile: dict, risk_result: dict) -> list:
    critical_count = risk_result.get("critical_count", 0)
    overall        = risk_result.get("overall_level", "low")

    statuses = []
    for std in profile["compliance"]:
        if std["critical"] and overall in ("critical",):
            status = "❌ FAIL"
            color  = "#ff4757"
            note   = "Critical risks detected — non-compliance likely"
        elif std["critical"] and overall in ("high",) and critical_count > 0:
            status = "⚠️ AT RISK"
            color  = "#f59e0b"
            note   = "High risks present — review required"
        elif std["critical"] and overall == "high":
            status = "⚠️ REVIEW"
            color  = "#f59e0b"
            note   = "Elevated risk level — schedule audit"
        else:
            status = "✅ OK"
            color  = "#00ff87"
            note   = "No immediate compliance issues detected"

        statuses.append({
            "standard": std["name"],
            "area":     std["area"],
            "critical": std["critical"],
            "status":   status,
            "color":    color,
            "note":     note,
        })

    return statuses


def get_weighted_risks(risks: list, profile: dict) -> list:
    weights    = profile.get("risk_weights", {})
    weighted   = []
    scores_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    level_map  = {1: "low", 2: "medium", 3: "high", 4: "critical"}

    for r in risks:
        weight    = weights.get(r["name"], 1.0)
        raw_score = scores_map.get(r["level"], 1)
        w_score   = min(4, raw_score * weight)
        w_level   = level_map[min(4, round(w_score))]
        weighted.append({**r, "weighted_level": w_level, "weight": weight, "weighted_score": w_score})

    return weighted


def get_industry_kpi_targets(factory_inputs: dict, profile: dict) -> dict:
    machines = factory_inputs.get("machines", 10)
    hours    = factory_inputs.get("hours", 8)
    workers  = factory_inputs.get("workers", 30)

    mtbf = profile["mtbf_hours"]
    mttr = profile["mttr_hours"]

    availability_target = mtbf / (mtbf + mttr)
    teep                = profile["oee_world_class"] / 100 * (hours / 24)

    return {
        "mtbf_target_h":      mtbf,
        "mttr_target_h":      mttr,
        "availability_target": round(availability_target * 100, 1),
        "oee_world_class":    profile["oee_world_class"],
        "oee_industry_avg":   profile["oee_industry_avg"],
        "oee_poor":           profile["oee_poor"],
        "teep":               round(teep * 100, 1),
        "target_scrap_pct":   round(profile["target_scrap_rate"] * 100, 2),
        "target_rework_pct":  round(profile["target_rework_rate"] * 100, 2),
    }
