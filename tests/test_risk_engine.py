import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from risk_engine import score_risks, calculate_oee, calculate_production_targets, calculate_shift_plan

FACTORY_BASE = {
    "machines": 10,
    "workers": 30,
    "hours": 8,
    "product_price": 220.0,
    "material_cost": 80.0,
    "energy_cost": 0.13,
    "worker_daily_cost": 110.0,
    "production_rate": 10.0,
    "energy_kw_per_machine": 15.0,
}

MARKET_NORMAL = {
    "demand_multiplier": 1.0,
    "energy_cost_multiplier": 1.0,
    "material_cost_multiplier": 1.0,
}

MARKET_CRISIS = {
    "demand_multiplier": 0.4,
    "energy_cost_multiplier": 2.5,
    "material_cost_multiplier": 2.0,
}

STATS_NORMAL = {
    "failure_rate": 0.034,
    "avg_tool_wear": 108.0,
    "temp_diff": 10.0,
    "avg_torque": 40.0,
}

STATS_CRITICAL = {
    "failure_rate": 0.25,
    "avg_tool_wear": 230.0,
    "temp_diff": 15.0,
    "avg_torque": 70.0,
}


class TestScoreRisks:
    def test_returns_seven_risks(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert len(result["risks"]) == 7

    def test_all_risk_levels_valid(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        valid = {"low", "medium", "high", "critical"}
        for r in result["risks"]:
            assert r["level"] in valid, f"Invalid level: {r['level']}"

    def test_health_score_in_range(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert 0 <= result["health_score"] <= 100

    def test_critical_stats_lower_health(self):
        normal  = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        bad     = score_risks(FACTORY_BASE, MARKET_CRISIS, STATS_CRITICAL)
        assert bad["health_score"] <= normal["health_score"]

    def test_overall_level_valid(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert result["overall_level"] in {"low", "medium", "high", "critical"}

    def test_counts_sum_to_seven(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        total = (result["critical_count"] + result["high_count"] +
                 result["medium_count"] + result["low_count"])
        assert total == 7

    def test_no_dataset_stats_uses_defaults(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, None)
        assert len(result["risks"]) == 7

    def test_high_failure_rate_triggers_critical_or_high(self):
        result = score_risks(FACTORY_BASE, MARKET_NORMAL, STATS_CRITICAL)
        levels = [r["level"] for r in result["risks"] if r["name"] == "Machine Failure Risk"]
        assert levels[0] in {"high", "critical"}
class TestCalculateOEE:
    def test_oee_in_range(self):
        result = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert 0 <= result["oee"] <= 100

    def test_components_in_range(self):
        result = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        for key in ("availability", "performance", "quality"):
            assert 0 <= result[key] <= 100, f"{key} out of range"

    def test_oee_approx_product_of_components(self):
        r = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        expected = (r["availability"] / 100) * (r["performance"] / 100) * (r["quality"] / 100) * 100
        assert abs(r["oee"] - round(expected, 1)) < 1.0

    def test_world_class_flag(self):
        result = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert isinstance(result["world_class"], bool)

    def test_high_failure_reduces_availability(self):
        normal   = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        critical = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_CRITICAL)
        assert critical["availability"] <= normal["availability"]

    def test_no_stats_still_works(self):
        result = calculate_oee(FACTORY_BASE, MARKET_NORMAL, None)
        assert "oee" in result

    def test_machine_speed_affects_performance(self):
        slow = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL, machine_speed=0.6)
        fast = calculate_oee(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL, machine_speed=1.3)
        assert fast["performance"] >= slow["performance"]

class TestProductionTargets:
    def test_max_units_gte_projected(self):
        result = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert result["max_units_possible"] >= result["projected_units"]

    def test_breakeven_positive(self):
        result = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert result["breakeven_units"] > 0

    def test_target_gt_breakeven(self):
        result = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert result["target_units"] > result["breakeven_units"]

    def test_on_track_is_bool(self):
        result = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert isinstance(result["on_track"], bool)

    def test_low_demand_reduces_revenue(self):
        normal = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        low    = calculate_production_targets(FACTORY_BASE, MARKET_CRISIS, STATS_NORMAL)
        assert low["daily_revenue_proj"] <= normal["daily_revenue_proj"]

    def test_margin_per_unit_correct(self):
        result = calculate_production_targets(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        expected = FACTORY_BASE["product_price"] - FACTORY_BASE["material_cost"]
        assert abs(result["margin_per_unit"] - expected) < 0.01
class TestShiftPlan:
    def test_returns_three_shifts(self):
        plan = calculate_shift_plan(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        assert len(plan) == 3

    def test_worker_counts_sum_close_to_total(self):
        plan  = calculate_shift_plan(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        total = sum(s["workers"] for s in plan)
        assert abs(total - FACTORY_BASE["workers"]) <= 3

    def test_each_shift_has_required_keys(self):
        plan     = calculate_shift_plan(FACTORY_BASE, MARKET_NORMAL)
        required = {"name", "time", "workers", "energy_mult", "recommended_speed", "icon"}
        for shift in plan:
            assert required.issubset(shift.keys()), f"Missing keys in {shift}"

    def test_night_energy_cheaper(self):
        plan = calculate_shift_plan(FACTORY_BASE, MARKET_NORMAL, STATS_NORMAL)
        mults = {s["name"]: s["energy_mult"] for s in plan}
        assert mults["Night"] < mults["Morning"]
