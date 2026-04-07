import numpy as np
import random


def calculate_profit(factory_inputs, market_inputs, machine_speed, workers_active, runs=100):
    machines    = factory_inputs.get("machines", 10)
    hours       = factory_inputs.get("hours", 8)
    e_cost      = factory_inputs.get("energy_cost", 0.13)
    mat_cost    = factory_inputs.get("material_cost", 80)
    p_price     = factory_inputs.get("product_price", 220)
    w_cost      = factory_inputs.get("worker_daily_cost", 110)
    workers_max = factory_inputs.get("workers", 30)
    prod_rate   = factory_inputs.get("production_rate",       10.0)
    energy_kw   = factory_inputs.get("energy_kw_per_machine", 15.0)

    energy_mult  = market_inputs.get("energy_cost_multiplier", 1.0)
    demand       = market_inputs.get("demand_multiplier", 1.0)
    mat_mult     = market_inputs.get("material_cost_multiplier", 1.0)
    failure_prob = market_inputs.get("failure_prob", 0.034)

    profits = []
    for _ in range(runs):
        active = sum(1 for _ in range(machines) if random.random() > failure_prob)
        eff    = min(workers_active / max(1, workers_max), 1.0)
        prod   = active * machine_speed * hours * prod_rate * eff
        e_exp  = active * energy_kw * machine_speed * hours * e_cost * energy_mult
        m_exp  = prod * mat_cost * mat_mult
        rev    = prod * p_price * min(1.0, demand)
        w_exp  = workers_active * w_cost
        profits.append(rev - e_exp - m_exp - w_exp)

    return round(np.mean(profits), 2)


def compare_with_without_plan(factory_inputs, market_inputs, actions,
                               dataset_stats=None, ml_recommendation=None):
    failure_prob = dataset_stats.get("failure_rate", 0.034) if dataset_stats else 0.034
    market_base  = {**market_inputs, "failure_prob": failure_prob}

    profit_without = calculate_profit(
        factory_inputs, market_base,
        machine_speed=1.0,
        workers_active=factory_inputs.get("workers", 30)
    )

    recommended_speed   = 1.0
    recommended_workers = factory_inputs.get("workers", 30)

    if ml_recommendation:
        recommended_speed   = ml_recommendation.get("machine_speed",  recommended_speed)
        recommended_workers = ml_recommendation.get("workers_active", recommended_workers)

    has_maintenance  = any(a["type"] == "maintenance" for a in actions)
    adjusted_failure = failure_prob * (0.45 if has_maintenance else 1.0)
    market_optimized = {**market_inputs, "failure_prob": adjusted_failure}

    profit_with_ops = calculate_profit(
        factory_inputs, market_optimized,
        machine_speed=recommended_speed,
        workers_active=recommended_workers
    )

    non_maintenance_savings = sum(
        a["saving"] for a in actions
        if a["type"] in ("energy", "cost", "quality", "strategy") and a["saving"] > 0
    )

    REALISATION_RATE = 0.15
    total_with = profit_with_ops + non_maintenance_savings * REALISATION_RATE

    return {
        "profit_without":       profit_without,
        "profit_with":          round(total_with, 2),
        "difference":           round(total_with - profit_without, 2),
        "improvement_pct":      round((total_with - profit_without) / abs(profit_without) * 100, 1) if profit_without != 0 else 0,
        "recommended_speed":    recommended_speed,
        "recommended_workers":  recommended_workers,
        "total_action_savings": round(sum(a["saving"] for a in actions if a["saving"] > 0), 2)
    }
