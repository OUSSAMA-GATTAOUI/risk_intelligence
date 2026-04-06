import numpy as np
from config import RISK_THRESHOLDS, RISK_COLORS, RISK_EMOJIS, FACTORY_PRESETS


def classify(value, key):
    thresholds = RISK_THRESHOLDS[key]
    for level in ["critical", "high", "medium", "low"]:
        lo, hi = thresholds[level]
        if lo <= value < hi:
            return level
    return "low"


def _get_rates(factory_inputs):
    prod_rate = factory_inputs.get("production_rate",       10.0)
    energy_kw = factory_inputs.get("energy_kw_per_machine", 15.0)
    return prod_rate, energy_kw


def calculate_oee(factory_inputs, market_inputs, dataset_stats=None, machine_speed=1.0):
    failure_rate = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034
    tool_wear    = dataset_stats.get("avg_tool_wear", 108)   if dataset_stats else 108
    temp_diff    = dataset_stats.get("temp_diff", 10.0)      if dataset_stats else 10.0

    energy_mult   = market_inputs.get("energy_cost_multiplier", 1.0)
    # machine_speed is passed in directly from the ML recommendation;
    # fall back to market_inputs only if the default 1.0 was not overridden.
    if machine_speed == 1.0:
        machine_speed = market_inputs.get("machine_speed_setting", 1.0)

    if failure_rate > 0:
        mtbf_hours   = 1.0 / failure_rate
        mttr_hours   = 2.0
        availability = mtbf_hours / (mtbf_hours + mttr_hours)
    else:
        availability = 0.98
    availability = max(0.40, min(0.98, availability))

    energy_penalty = max(0.0, (energy_mult - 1.5) * 0.05)
    performance    = min(1.0, max(0.50, machine_speed - energy_penalty))

    wear_penalty    = min(0.20, tool_wear / 1250)
    thermal_penalty = max(0.0, (temp_diff - 9.0) * 0.012)
    quality         = max(0.60, 1.0 - wear_penalty - thermal_penalty)

    oee = availability * performance * quality

    return {
        "oee":          round(oee * 100, 1),
        "availability": round(availability * 100, 1),
        "performance":  round(performance * 100, 1),
        "quality":      round(quality * 100, 1),
        "world_class":  oee >= 0.85,
        "status": (
            "World Class 🏆" if oee >= 0.85 else
            "Good"           if oee >= 0.70 else
            "Average"        if oee >= 0.50 else
            "Poor — Act Now"
        ),
        "status_color": (
            "#00ff87" if oee >= 0.85 else
            "#00d4ff" if oee >= 0.70 else
            "#f59e0b" if oee >= 0.50 else
            "#ff4757"
        )
    }


def calculate_production_targets(factory_inputs, market_inputs, dataset_stats=None):
    machines = factory_inputs.get("machines", 10)
    hours    = factory_inputs.get("hours", 8)
    p_price  = factory_inputs.get("product_price", 220)
    mat_cost = factory_inputs.get("material_cost", 80)
    e_cost   = factory_inputs.get("energy_cost", 0.13)
    w_cost   = factory_inputs.get("worker_daily_cost", 110)
    workers  = factory_inputs.get("workers", 30)

    prod_rate, energy_kw = _get_rates(factory_inputs)

    demand      = market_inputs.get("demand_multiplier", 1.0)
    energy_mult = market_inputs.get("energy_cost_multiplier", 1.0)
    mat_mult    = market_inputs.get("material_cost_multiplier", 1.0)

    failure_rate = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034

    max_units             = machines * prod_rate * hours
    active_machine_factor = max(0.5, 1.0 - failure_rate * 2)
    actual_units          = machines * prod_rate * hours * active_machine_factor

    energy_daily = machines * energy_kw * hours * e_cost * energy_mult
    wages_daily  = workers * w_cost
    fixed_costs  = energy_daily + wages_daily

    variable_cost_per_unit = mat_cost * mat_mult
    margin_per_unit        = p_price - variable_cost_per_unit

    breakeven_units = (fixed_costs / margin_per_unit) if margin_per_unit > 0 else float("inf")
    target_units    = breakeven_units * 1.20

    sellable_units = actual_units * min(1.0, demand)
    daily_revenue  = sellable_units * p_price

    return {
        "max_units_possible": round(max_units),
        "projected_units":    round(actual_units),
        "breakeven_units":    round(breakeven_units),
        "target_units":       round(target_units),
        "margin_per_unit":    round(margin_per_unit, 2),
        "fixed_costs_today":  round(fixed_costs, 2),
        "on_track":           actual_units >= target_units,
        "breakeven_pct":      round((actual_units / max(1, breakeven_units)) * 100, 1),
        "efficiency_pct":     round((actual_units / max(1, max_units)) * 100, 1),
        "daily_revenue_proj": round(daily_revenue, 2),
        "daily_cost_proj":    round(fixed_costs + actual_units * variable_cost_per_unit, 2),
    }


def calculate_shift_plan(factory_inputs, market_inputs, dataset_stats=None):
    workers = factory_inputs.get("workers", 30)
    demand  = market_inputs.get("demand_multiplier", 1.0)
    e_mult  = market_inputs.get("energy_cost_multiplier", 1.0)

    night_energy_mult = e_mult * 0.75

    if demand >= 1.3:
        morning, afternoon, night = round(workers*0.40), round(workers*0.38), round(workers*0.22)
    elif demand >= 0.8:
        morning, afternoon, night = round(workers*0.45), round(workers*0.35), round(workers*0.20)
    else:
        morning, afternoon, night = round(workers*0.50), round(workers*0.30), round(workers*0.20)

    return [
        {"name": "Morning",   "time": "06:00 – 14:00", "workers": morning,
         "energy_mult": e_mult*1.1,       "recommended_speed": min(1.3, demand*1.1), "icon": "🌅"},
        {"name": "Afternoon", "time": "14:00 – 22:00", "workers": afternoon,
         "energy_mult": e_mult*1.0,       "recommended_speed": min(1.2, demand),     "icon": "☀️"},
        {"name": "Night",     "time": "22:00 – 06:00", "workers": night,
         "energy_mult": night_energy_mult, "recommended_speed": min(1.1, demand*0.9), "icon": "🌙"},
    ]


def score_risks(factory_inputs, market_inputs, dataset_stats=None):
    machines  = factory_inputs.get("machines", 10)
    hours     = factory_inputs.get("hours", 8)
    e_cost    = factory_inputs.get("energy_cost", 0.13)
    p_price   = factory_inputs.get("product_price", 220)
    mat_cost  = factory_inputs.get("material_cost", 80)
    prod_rate, energy_kw = _get_rates(factory_inputs)

    failure_rate = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034
    tool_wear    = dataset_stats.get("avg_tool_wear", 108)   if dataset_stats else 108
    temp_diff    = dataset_stats.get("temp_diff", 10.0)      if dataset_stats else 10.0
    torque       = dataset_stats.get("avg_torque", 40.0)     if dataset_stats else 40.0

    energy_mult = market_inputs.get("energy_cost_multiplier", 1.0)
    demand      = market_inputs.get("demand_multiplier", 1.0)
    mat_mult    = market_inputs.get("material_cost_multiplier", 1.0)

    risks = []

    breakdown_cost_per_machine = prod_rate * p_price * hours * failure_rate
    risks.append({
        "name": "Machine Failure Risk", "icon": "⚙️",
        "level": classify(failure_rate, "failure_prob"),
        "value": f"{failure_rate*100:.2f}%",
        "raw_value": failure_rate, "max_value": 0.30,
        "description": f"Machines break down {failure_rate*100:.2f}% of the time per shift.",
        "impact": f"Expected loss from breakdowns: ~€{breakdown_cost_per_machine*machines:,.0f}/day.",
        "fix": "Schedule preventive maintenance. Check hydraulics, bearings, coolant levels."
    })

    risks.append({
        "name": "Tool Wear & Maintenance", "icon": "🔧",
        "level": classify(tool_wear, "tool_wear"),
        "value": f"{tool_wear:.0f} min",
        "raw_value": tool_wear, "max_value": 260,
        "description": f"Tools have run {tool_wear:.0f} min avg. Critical zone: >220 min.",
        "impact": "Worn tools increase defects and energy draw by up to 20%.",
        "fix": "Replace tools above 200 min. Clean holders. Run diagnostic cycle."
    })

    risks.append({
        "name": "Thermal Stress", "icon": "🌡️",
        "level": classify(temp_diff, "temp_diff"),
        "value": f"{temp_diff:.1f}K diff",
        "raw_value": temp_diff, "max_value": 20,
        "description": f"Process runs {temp_diff:.1f}K hotter than ambient air.",
        "impact": "High heat triples wear rate and raises breakdown probability.",
        "fix": "Check coolant flow, clean heat exchangers, verify ventilation is clear."
    })

    extra_energy_cost = (energy_mult - 1) * machines * energy_kw * hours * e_cost
    risks.append({
        "name": "Energy Cost", "icon": "⚡",
        "level": classify(energy_mult, "energy_mult"),
        "value": f"{energy_mult:.1f}x normal",
        "raw_value": energy_mult, "max_value": 3.0,
        "description": f"Electricity is {energy_mult:.1f}x the normal price today.",
        "impact": f"Extra energy cost vs normal day: €{extra_energy_cost:,.0f}.",
        "fix": "Shift heavy ops to off-peak. Switch off idle machines. Reduce speed slightly."
    })

    risks.append({
        "name": "Market Demand", "icon": "📉",
        "level": classify(demand, "demand"),
        "value": f"{demand*100:.0f}% of normal",
        "raw_value": demand, "max_value": 2.0,
        "description": f"Orders at {demand*100:.0f}% of typical level.",
        "impact": "Low demand = unsold inventory. High demand = possible overload.",
        "fix": "Low: switch to build-to-order. High: prioritize fastest lines."
    })

    extra_mat = (mat_mult - 1) * mat_cost
    risks.append({
        "name": "Supply Chain / Materials", "icon": "🚚",
        "level": classify(mat_mult, "material_mult"),
        "value": f"{mat_mult:.1f}x normal",
        "raw_value": mat_mult, "max_value": 3.0,
        "description": f"Raw materials cost {mat_mult:.1f}x the normal price.",
        "impact": f"Each unit costs €{extra_mat:.1f} more in materials than usual.",
        "fix": "Negotiate spot contracts. Explore alternative suppliers."
    })

    risks.append({
        "name": "Machine Overload (Torque)", "icon": "👷",
        "level": classify(torque, "torque"),
        "value": f"{torque:.1f} Nm",
        "raw_value": torque, "max_value": 80,
        "description": f"Average machine torque: {torque:.1f} Nm. Safe max: 60 Nm.",
        "impact": "Overload accelerates bearing and spindle wear — silent damage.",
        "fix": "Reduce feed rate. Check tool geometry. Verify workpiece clamping."
    })

    scores          = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    weighted_scores = [scores[r["level"]] for r in risks]
    avg             = np.mean(weighted_scores)
    overall         = "critical" if avg >= 3.5 else "high" if avg >= 2.5 else "medium" if avg >= 1.5 else "low"

    crit_n       = sum(1 for r in risks if r["level"] == "critical")
    high_n       = sum(1 for r in risks if r["level"] == "high")
    med_n        = sum(1 for r in risks if r["level"] == "medium")
    low_n        = sum(1 for r in risks if r["level"] == "low")
    health_score = max(0, 100 - (crit_n * 25 + high_n * 12 + med_n * 5 + low_n * 1))

    return {
        "risks":          risks,
        "overall_level":  overall,
        "overall_score":  round(avg, 2),
        "health_score":   health_score,
        "critical_count": crit_n,
        "high_count":     high_n,
        "medium_count":   med_n,
        "low_count":      low_n,
    }
