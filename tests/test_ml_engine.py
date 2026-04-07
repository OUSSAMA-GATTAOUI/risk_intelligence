import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from ml_engine import GradientBoostingModel, QLearningAgent, MLEngine


FACTORY = {
    "machines": 5,
    "workers": 15,
    "hours": 8,
    "product_price": 220.0,
    "material_cost": 80.0,
    "energy_cost": 0.13,
    "worker_daily_cost": 110.0,
    "production_rate": 10.0,
    "energy_kw_per_machine": 15.0,
}

MARKET = {
    "demand_multiplier": 1.0,
    "energy_cost_multiplier": 1.0,
    "material_cost_multiplier": 1.0,
}


class TestGradientBoostingModel:
    def setup_method(self):
        self.model = GradientBoostingModel()
        self.model.train() 

    def test_train_returns_info(self):
        info = GradientBoostingModel().train()
        assert "failure_accuracy" in info
        assert "samples" in info

    def test_predict_returns_dict(self):
        result = self.model.predict(
            speed=1.0, torque=40.0, tool_wear=100.0, temp_diff=10.0
        )
        assert "failure_prob" in result
        assert "energy_per_machine" in result
        assert "quality_score" in result

    def test_failure_prob_in_range(self):
        result = self.model.predict(1.0, 40.0, 100.0, 10.0)
        assert 0.0 <= result["failure_prob"] <= 1.0

    def test_quality_score_in_range(self):
        result = self.model.predict(1.0, 40.0, 100.0, 10.0)
        assert 0.0 <= result["quality_score"] <= 1.0

    def test_high_wear_raises_failure_prob(self):
        low  = self.model.predict(1.0, 40.0, tool_wear=10.0,  temp_diff=9.0)
        high = self.model.predict(1.0, 60.0, tool_wear=240.0, temp_diff=14.0)
        assert high["failure_prob"] >= low["failure_prob"]

    def test_feature_importance_returns_list(self):
        importance = self.model.feature_importance()
        assert isinstance(importance, list)
        assert len(importance) == len(self.model.feature_names)

    def test_feature_importance_sums_to_100(self):
        importance = self.model.feature_importance()
        total = sum(item["importance_pct"] for item in importance)
        assert abs(total - 100.0) < 1.0 

    def test_failure_drivers_returns_strings(self):
        drivers = self.model.get_top_failure_drivers(n=3)
        assert len(drivers) == 3
        assert all(isinstance(d, str) for d in drivers)

    def test_predict_before_train_raises(self):
        fresh = GradientBoostingModel()
        with pytest.raises(RuntimeError):
            fresh.predict(1.0, 40.0, 100.0, 10.0)


class TestQLearningAgent:
    def setup_method(self):
        self.gbm = GradientBoostingModel()
        self.gbm.train()
        self.agent = QLearningAgent()
        scenarios = [
            {"energy_cost_multiplier": 1.0, "demand_multiplier": 1.0, "material_cost_multiplier": 1.0},
            {"energy_cost_multiplier": 1.5, "demand_multiplier": 0.8, "material_cost_multiplier": 1.3},
        ]
        self.agent.train(FACTORY, scenarios, self.gbm, episodes=200)

    def test_recommend_returns_dict(self):
        rec = self.agent.recommend(1.0, 1.0, 0.03)
        assert "machine_speed" in rec
        assert "worker_fraction" in rec

    def test_speed_in_valid_range(self):
        rec = self.agent.recommend(1.0, 1.0, 0.03)
        assert rec["machine_speed"] in QLearningAgent.SPEEDS

    def test_worker_fraction_in_valid_range(self):
        rec = self.agent.recommend(1.0, 1.0, 0.03)
        assert rec["worker_fraction"] in QLearningAgent.WORKERS

    def test_trained_flag_set(self):
        assert self.agent.trained is True


class TestMLEngine:
    def setup_method(self):
        self.engine = MLEngine()
        self.info   = self.engine.train(FACTORY, episodes=200)

    def test_train_returns_info(self):
        assert "gbm" in self.info
        assert "rl"  in self.info

    def test_recommend_returns_dict(self):
        rec = self.engine.recommend(FACTORY, MARKET)
        assert "machine_speed" in rec
        assert "workers_active" in rec
        assert "predicted_failure" in rec

    def test_workers_active_within_bounds(self):
        rec = self.engine.recommend(FACTORY, MARKET)
        assert 1 <= rec["workers_active"] <= FACTORY["workers"]

    def test_get_failure_drivers(self):
        drivers = self.engine.get_failure_drivers(n=3)
        assert len(drivers) == 3

    def test_recommend_before_train_raises(self):
        fresh = MLEngine()
        with pytest.raises(RuntimeError):
            fresh.recommend(FACTORY, MARKET)

    def test_cache_status_keys(self):
        status = self.engine.cache_status()
        assert "joblib_available" in status
        assert "cache_key" in status
