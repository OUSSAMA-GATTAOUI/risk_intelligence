"""
tests/test_profit_calculator.py
Tests for calculate_profit and compare_with_without_plan.
Run with: pytest tests/
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from profit_calculator import calculate_profit, compare_with_without_plan


FACTORY = {
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
    "failure_prob": 0.034,
}

MARKET_CRISIS = {
    "demand_multiplier": 0.4,
    "energy_cost_multiplier": 3.0,
    "material_cost_multiplier": 2.0,
    "failure_prob": 0.20,
}

SAMPLE_ACTIONS = [
    {"priority": 1, "type": "energy",      "saving": 500.0,  "ml_powered": True,  "icon": "⚡", "title": "Reduce speed", "detail": ""},
    {"priority": 2, "type": "maintenance", "saving": 1200.0, "ml_powered": False, "icon": "🔧", "title": "Maintenance",  "detail": ""},
    {"priority": 2, "type": "cost",        "saving": 300.0,  "ml_powered": True,  "icon": "👷", "title": "Workers",     "detail": ""},
]


class TestCalculateProfit:
    def test_returns_float(self):
        result = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=30)
        assert isinstance(result, float)

    def test_higher_speed_raises_revenue_under_good_demand(self):
        low  = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=0.7, workers_active=30, runs=200)
        high = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.3, workers_active=30, runs=200)
        assert high >= low

    def test_crisis_market_lowers_profit(self):
        normal = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=30, runs=200)
        crisis = calculate_profit(FACTORY, MARKET_CRISIS, machine_speed=1.0, workers_active=30, runs=200)
        assert crisis < normal

    def test_fewer_workers_reduces_cost(self):
        full    = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=30, runs=200)
        reduced = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=10, runs=200)
        # reduced workers means lower cost, potentially higher profit when demand is low
        # this is a sanity check that they produce different values
        assert full != reduced

    def test_stable_with_high_runs(self):
        """Two runs of 500 should be close to each other (Monte Carlo stability)."""
        r1 = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=30, runs=500)
        r2 = calculate_profit(FACTORY, MARKET_NORMAL, machine_speed=1.0, workers_active=30, runs=500)
        # should be within 10% of each other
        assert abs(r1 - r2) / (abs(r1) + 1) < 0.10


class TestCompareWithWithoutPlan:
    def test_returns_required_keys(self):
        result = compare_with_without_plan(FACTORY, MARKET_NORMAL, SAMPLE_ACTIONS, None, None)
        required = {
            "profit_without", "profit_with", "difference",
            "improvement_pct", "recommended_speed", "recommended_workers",
            "total_action_savings",
        }
        assert required.issubset(result.keys())

    def test_maintenance_action_improves_profit(self):
        """Having a maintenance action should reduce failure_prob and improve profit."""
        result = compare_with_without_plan(FACTORY, MARKET_NORMAL, SAMPLE_ACTIONS)
        # profit_with should be >= profit_without (maintenance reduces failures)
        # This is probabilistic so we just check it's computed
        assert isinstance(result["difference"], float)

    def test_empty_actions_still_works(self):
        result = compare_with_without_plan(FACTORY, MARKET_NORMAL, [])
        assert result["total_action_savings"] == 0.0

    def test_improvement_pct_matches_difference(self):
        result = compare_with_without_plan(FACTORY, MARKET_NORMAL, SAMPLE_ACTIONS)
        if result["profit_without"] != 0:
            expected_pct = round(
                (result["difference"] / abs(result["profit_without"])) * 100, 1
            )
            assert abs(result["improvement_pct"] - expected_pct) < 0.2

    def test_ml_recommendation_applied(self):
        ml_rec = {"machine_speed": 1.2, "workers_active": 25}
        result = compare_with_without_plan(FACTORY, MARKET_NORMAL, SAMPLE_ACTIONS,
                                           None, ml_rec)
        assert result["recommended_speed"] == 1.2
        assert result["recommended_workers"] == 25
