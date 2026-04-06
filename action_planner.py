import numpy as np
import random


def generate_action_plan(risks, factory_inputs, market_inputs,
                         dataset_stats=None, ml_recommendation=None):
    actions     = []
    machines    = factory_inputs.get("machines", 10)
    workers     = factory_inputs.get("workers", 30)
    hours       = factory_inputs.get("hours", 8)
    e_cost      = factory_inputs.get("energy_cost", 0.13)
    p_price     = factory_inputs.get("product_price", 220)
    w_cost      = factory_inputs.get("worker_daily_cost", 110)
    prod_rate   = factory_inputs.get("production_rate",       10.0)
    energy_kw   = factory_inputs.get("energy_kw_per_machine", 15.0)

    energy_mult  = market_inputs.get("energy_cost_multiplier", 1.0)
    demand       = market_inputs.get("demand_multiplier", 1.0)
    mat_mult     = market_inputs.get("material_cost_multiplier", 1.0)
    tool_wear    = dataset_stats.get("avg_tool_wear", 108)  if dataset_stats else 108
    failure_rate = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034
    temp_diff    = dataset_stats.get("temp_diff", 10.0)     if dataset_stats else 10.0

    if ml_recommendation:
        optimal_speed  = ml_recommendation["machine_speed"]
        rec_workers    = ml_recommendation["workers_active"]
        model_label    = f"GBM + RL Agent ({ml_recommendation.get('rl_episodes',0):,} episodes trained)"
        predicted_fail = ml_recommendation.get("predicted_failure", failure_rate)
        predicted_qual = ml_recommendation.get("predicted_quality", 0.9)
    else:
        optimal_speed, rec_workers = _fallback_optimize(factory_inputs, market_inputs, failure_rate)
        model_label    = "Random Search Optimizer"
        predicted_fail = failure_rate
        predicted_qual = 0.9

    speed_diff = optimal_speed - 1.0
    if abs(speed_diff) >= 0.05:
        direction = "Increase" if speed_diff > 0 else "Reduce"
        if speed_diff > 0:
            impact = abs(speed_diff) * machines * prod_rate * hours * p_price * demand * 0.7
        else:
            impact = abs(speed_diff) * machines * energy_kw * hours * e_cost * energy_mult * 0.8
        actions.append({
            "priority": 1,
            "icon": "🚀" if speed_diff > 0 else "⚡",
            "title": f"{direction} Machine Speed to {optimal_speed}x",
            "detail": (
                f"{model_label} recommends {optimal_speed}x speed "
                f"(energy: {energy_mult:.1f}x, demand: {demand:.1f}x). "
                f"Change from 1.0x to {optimal_speed}x."
            ),
            "saving": round(abs(impact), 2),
            "type":   "revenue" if speed_diff > 0 else "energy",
            "ml_powered": True
        })
    else:
        actions.append({
            "priority": 3,
            "icon": "✅",
            "title": "Keep Machines at Current Speed (1.0x)",
            "detail": f"{model_label} confirms 1.0x is already optimal today.",
            "saving": 0,
            "type": "info",
            "ml_powered": True
        })

    if rec_workers < workers:
        saving = (workers - rec_workers) * w_cost
        actions.append({
            "priority": 1 if demand <= 0.75 else 2,
            "icon": "👷",
            "title": f"Activate {rec_workers} Workers Today (not all {workers})",
            "detail": (
                f"RL Agent found {rec_workers} workers maximizes profit "
                f"under current demand ({demand:.1f}x) and material costs ({mat_mult:.1f}x)."
            ),
            "saving": round(saving, 2),
            "type": "cost",
            "ml_powered": True
        })

    if predicted_fail >= 0.05:
        expected_broken = predicted_fail * machines
        breakdown_cost  = expected_broken * prod_rate * p_price * hours
        actions.append({
            "priority": 1 if predicted_fail >= 0.15 else 2,
            "icon": "⚠️",
            "title": f"GBM Predicts {predicted_fail*100:.1f}% Failure Risk Today",
            "detail": (
                f"The Gradient Boosting model predicts a {predicted_fail*100:.1f}% "
                f"machine failure probability based on current conditions. "
                f"{'Schedule immediate maintenance.' if predicted_fail >= 0.15 else 'Monitor closely and prepare spare parts.'}"
            ),
            "saving": round(breakdown_cost, 2),
            "type": "maintenance",
            "ml_powered": True
        })

    if predicted_qual < 0.85:
        quality_loss = (1 - predicted_qual) * machines * prod_rate * hours * p_price * 0.5
        actions.append({
            "priority": 2,
            "icon": "🎯",
            "title": f"Output Quality Predicted at {predicted_qual*100:.0f}%",
            "detail": (
                f"GBM model predicts {predicted_qual*100:.0f}% quality — "
                f"below optimal. Consider reducing speed slightly and checking tool condition."
            ),
            "saving": round(quality_loss, 2),
            "type": "quality",
            "ml_powered": True
        })

    if tool_wear >= 160:
        avoided_breakdowns = 0.40 * failure_rate * machines * prod_rate * p_price * hours
        actions.append({
            "priority": 1, "icon": "🔧",
            "title": "Schedule Maintenance BEFORE Next Shift",
            "detail": f"Tool wear at {tool_wear:.0f} min — critical. Delay raises breakdown risk ~15%/shift.",
            "saving": round(avoided_breakdowns, 2),
            "type": "maintenance", "ml_powered": False
        })
    elif tool_wear >= 80:
        actions.append({
            "priority": 2, "icon": "🔧",
            "title": "Plan Maintenance Within 3 Days",
            "detail": f"Tool wear at {tool_wear:.0f} min — book maintenance this week.",
            "saving": round(machines * p_price * prod_rate * 0.05, 2),
            "type": "maintenance", "ml_powered": False
        })

    if temp_diff >= 11:
        thermal_saving = 0.15 * failure_rate * machines * prod_rate * p_price * hours
        actions.append({
            "priority": 2, "icon": "🌡️",
            "title": "Activate Extra Cooling Systems",
            "detail": f"Machine temp {temp_diff:.1f}K above ambient — overheating accelerates wear.",
            "saving": round(thermal_saving, 2),
            "type": "maintenance", "ml_powered": False
        })

    if demand <= 0.65:
        waste_saving = machines * prod_rate * hours * p_price * 0.10
        actions.append({
            "priority": 1, "icon": "📦",
            "title": "Switch to Build-to-Order Only",
            "detail": "Demand critically low — only produce confirmed orders, stop speculative production.",
            "saving": round(waste_saving, 2),
            "type": "strategy", "ml_powered": False
        })

    if energy_mult >= 1.3:
        saving = machines * energy_kw * hours * e_cost * (energy_mult - 1.0) * 0.35 * 0.30
        actions.append({
            "priority": 2, "icon": "🕐",
            "title": "Move Heavy Operations to Off-Peak Hours",
            "detail": f"Electricity at {energy_mult:.1f}x — shift energy-intensive tasks to cheaper hours.",
            "saving": round(saving, 2),
            "type": "energy", "ml_powered": False
        })

    actions.sort(key=lambda x: x["priority"])
    return actions


def _fallback_optimize(factory_inputs, market_inputs, failure_rate, n=300):
    machines    = factory_inputs.get("machines", 10)
    workers_max = factory_inputs.get("workers", 30)
    hours       = factory_inputs.get("hours", 8)
    e_cost      = factory_inputs.get("energy_cost", 0.13)
    mat_cost    = factory_inputs.get("material_cost", 80)
    p_price     = factory_inputs.get("product_price", 220)
    w_cost      = factory_inputs.get("worker_daily_cost", 110)
    prod_rate   = factory_inputs.get("production_rate", 10.0)
    energy_kw   = factory_inputs.get("energy_kw_per_machine", 15.0)
    energy_mult = market_inputs.get("energy_cost_multiplier", 1.0)
    demand      = market_inputs.get("demand_multiplier", 1.0)
    mat_mult    = market_inputs.get("material_cost_multiplier", 1.0)

    best_profit, best_speed, best_workers = float("-inf"), 1.0, workers_max

    for _ in range(n):
        speed   = round(random.choice(np.arange(0.5, 1.55, 0.1)), 1)
        workers = random.randint(int(workers_max * 0.5), workers_max)
        profits = []
        for _ in range(5):
            active = sum(1 for _ in range(machines) if random.random() > failure_rate)
            eff    = min(workers / max(1, workers_max), 1.0)
            prod   = active * speed * hours * prod_rate * eff
            profit = (prod * p_price * min(1.0, demand)
                      - active * energy_kw * speed * hours * e_cost * energy_mult
                      - prod * mat_cost * mat_mult
                      - workers * w_cost)
            profits.append(profit)
        avg = np.mean(profits)
        if avg > best_profit:
            best_profit, best_speed, best_workers = avg, speed, workers

    return best_speed, best_workers
