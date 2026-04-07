from __future__ import annotations
from typing import List, Dict, Optional

import numpy as np
import random
import hashlib
import json
import os

from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

try:
    import joblib
    _JOBLIB_AVAILABLE = True
except ImportError:
    _JOBLIB_AVAILABLE = False

try:
    import shap as _shap
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".model_cache")


def _ensure_cache_dir():
    os.makedirs(_CACHE_DIR, exist_ok=True)


def _cache_key(factory_inputs: dict, data_source: str) -> str:
    """Stable hash of factory config + data source for cache lookup."""
    payload = json.dumps(factory_inputs, sort_keys=True) + data_source
    return hashlib.md5(payload.encode()).hexdigest()[:12]


class GradientBoostingModel:
    def __init__(self):
        self.failure_model = GradientBoostingClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
        )
        self.energy_model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
        )
        self.quality_model = GradientBoostingRegressor(
            n_estimators=80, max_depth=3, learning_rate=0.1, random_state=42
        )
        self.scaler  = StandardScaler()
        self.trained = False
        self._X_train = None   # kept for SHAP background sample
        self.feature_names = [
            "rotational_speed_norm",
            "torque",
            "tool_wear",
            "temp_diff",
            "machine_speed_setting",
            "energy_cost_mult",
            "demand_mult",
        ]


    def _generate_synthetic_data(self, n: int = 3000):
        np.random.seed(42)
        rpm_norm    = np.random.uniform(0.4, 1.6, n)
        torque      = np.random.uniform(3, 77, n)
        tool_wear   = np.random.uniform(0, 250, n)
        temp_diff   = np.random.uniform(8.5, 14.0, n)
        speed_set   = np.random.uniform(0.5, 1.5, n)
        energy_mult = np.random.uniform(0.8, 2.5, n)
        demand_mult = np.random.uniform(0.5, 1.8, n)

        X = np.column_stack([rpm_norm, torque, tool_wear, temp_diff,
                             speed_set, energy_mult, demand_mult])

        failure_logit = (
            -4.0
            + 0.015 * tool_wear
            + 0.04  * torque
            + 0.15  * temp_diff
            + 0.8   * speed_set
            + np.random.normal(0, 0.3, n)
        )
        failure_prob = 1 / (1 + np.exp(-failure_logit))
        y_failure    = (np.random.uniform(0, 1, n) < failure_prob).astype(int)

        y_energy = np.clip(
            speed_set * rpm_norm * 5
            + torque  * 0.03
            + energy_mult * 2
            + np.random.normal(0, 0.5, n),
            0.5, 15,
        )
        y_quality = np.clip(
            1.0
            - 0.003 * tool_wear
            - 0.005 * (temp_diff - 9)
            - 0.02  * np.maximum(0, speed_set - 1.2)
            + np.random.normal(0, 0.05, n),
            0, 1,
        )
        return X, y_failure, y_energy, y_quality

    def train(self, df=None, column_mapping=None):
        if df is not None:
            try:
                from data_adapter import detect_columns, prepare_ml_training_data
                mapping = column_mapping or detect_columns(df)
                result  = prepare_ml_training_data(df, mapping)
                if result is not None:
                    X, y_failure, y_energy, y_quality = result
                    source = (
                        f"real data ({len(df):,} records, "
                        f"{len([v for v in mapping.values() if v])} features detected)"
                    )
                else:
                    raise ValueError("Not enough features in dataset")
            except Exception as exc:
                print(f"[GBM] Dataset adapter issue ({exc}), using synthetic data.")
                X, y_failure, y_energy, y_quality = self._generate_synthetic_data()
                source = "synthetic data (3,000 records)"
        else:
            X, y_failure, y_energy, y_quality = self._generate_synthetic_data()
            source = "synthetic data (3,000 records)"

        X_scaled        = self.scaler.fit_transform(X)
        self._X_train   = X_scaled          
        self.failure_model.fit(X_scaled, y_failure)
        self.energy_model.fit(X_scaled, y_energy)
        self.quality_model.fit(X_scaled, y_quality)
        self.trained    = True

        preds = self.failure_model.predict(X_scaled)
        acc   = np.mean(preds == y_failure) * 100

        return {
            "source":           source,
            "samples":          len(X),
            "failure_accuracy": round(acc, 1),
            "features":         self.feature_names,
        }


    def predict(self, speed, torque, tool_wear, temp_diff,
                energy_mult: float = 1.0, demand_mult: float = 1.0) -> dict:
        if not self.trained:
            raise RuntimeError("Model not trained yet. Call .train() first.")

        x        = np.array([[speed, torque, tool_wear, temp_diff,
                               speed, energy_mult, demand_mult]])
        x_scaled = self.scaler.transform(x)

        failure_prob  = self.failure_model.predict_proba(x_scaled)[0][1]
        energy_per_m  = float(self.energy_model.predict(x_scaled)[0])
        quality_score = float(np.clip(self.quality_model.predict(x_scaled)[0], 0, 1))

        return {
            "failure_prob":       round(failure_prob, 4),
            "energy_per_machine": round(energy_per_m, 3),
            "quality_score":      round(quality_score, 3),
        }
    def feature_importance(self) -> List[Dict]:

        if not self.trained:
            return []

        raw   = self.failure_model.feature_importances_
        total = raw.sum() or 1.0
        pairs = [
            {"feature": name, "importance_pct": round(float(val / total * 100), 1)}
            for name, val in zip(self.feature_names, raw)
        ]
        return sorted(pairs, key=lambda x: x["importance_pct"], reverse=True)

    def get_top_failure_drivers(self, n: int = 3) -> List[str]:

        if not self.trained:
            return ["Model not trained — run analysis first."]

        importance = self.feature_importance()[:n]

        if _SHAP_AVAILABLE and self._X_train is not None:
            try:
                explainer   = _shap.TreeExplainer(self.failure_model)
                background  = self._X_train[::max(1, len(self._X_train) // 100)]
                shap_values = explainer.shap_values(background)
                if isinstance(shap_values, list):
                    shap_values = shap_values[1]     
                mean_abs    = np.abs(shap_values).mean(axis=0)
                total_abs   = mean_abs.sum() or 1.0
                shap_pairs  = sorted(
                    zip(self.feature_names, mean_abs / total_abs * 100),
                    key=lambda x: x[1], reverse=True,
                )[:n]
                ordinals = ["#1", "#2", "#3", "#4", "#5"]
                drivers  = []
                for i, (feat, pct) in enumerate(shap_pairs):
                    label = feat.replace("_", " ").replace("norm", "").strip()
                    drivers.append(
                        f"{label.title()} is the {ordinals[i]} driver "
                        f"of your failure risk ({pct:.0f}% SHAP contribution)"
                    )
                return drivers
            except Exception:
                pass 
        ordinals = ["#1", "#2", "#3", "#4", "#5"]
        drivers  = []
        for i, row in enumerate(importance):
            label = row["feature"].replace("_", " ").replace("norm", "").strip()
            drivers.append(
                f"{label.title()} is the {ordinals[i]} failure driver "
                f"({row['importance_pct']}% importance)"
            )
        return drivers

    def save(self, path: str):
        if not _JOBLIB_AVAILABLE:
            return
        _ensure_cache_dir()
        joblib.dump({
            "failure_model": self.failure_model,
            "energy_model":  self.energy_model,
            "quality_model": self.quality_model,
            "scaler":        self.scaler,
            "feature_names": self.feature_names,
            "X_train":       self._X_train,
        }, path)

    def load(self, path: str) -> bool:
        if not _JOBLIB_AVAILABLE or not os.path.exists(path):
            return False
        try:
            data = joblib.load(path)
            self.failure_model = data["failure_model"]
            self.energy_model  = data["energy_model"]
            self.quality_model = data["quality_model"]
            self.scaler        = data["scaler"]
            self.feature_names = data.get("feature_names", self.feature_names)
            self._X_train      = data.get("X_train")
            self.trained       = True
            return True
        except Exception:
            return False


class QLearningAgent:
    SPEEDS  = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4]
    WORKERS = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    ACTIONS = None

    def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.3):
        self.alpha   = alpha
        self.gamma   = gamma
        self.epsilon = epsilon
        self.ACTIONS = [(s, w) for s in self.SPEEDS for w in self.WORKERS]
        self.q_table = {}
        self.trained = False

    def _discretize_state(self, energy_mult, demand_mult, failure_prob):
        e = 0 if energy_mult < 1.2 else (1 if energy_mult < 1.8 else 2)
        d = 0 if demand_mult  < 0.8 else (1 if demand_mult  < 1.3 else 2)
        f = 0 if failure_prob < 0.03 else (1 if failure_prob < 0.1 else 2)
        return (e, d, f)

    def _get_q(self, state, action_idx):
        return self.q_table.get((state, action_idx), 0.0)

    def _choose_action(self, state, explore: bool = True):
        if explore and random.random() < self.epsilon:
            return random.randint(0, len(self.ACTIONS) - 1)
        q_vals = [self._get_q(state, i) for i in range(len(self.ACTIONS))]
        return int(np.argmax(q_vals))

    def _simulate_reward(self, speed, worker_frac, factory_inputs, market_inputs, gbm_model):
        machines    = factory_inputs["machines"]
        workers_max = factory_inputs["workers"]
        hours       = factory_inputs["hours"]
        p_price     = factory_inputs["product_price"]
        mat_cost    = factory_inputs["material_cost"]
        e_cost      = factory_inputs["energy_cost"]
        w_cost      = factory_inputs["worker_daily_cost"]
        energy_mult = market_inputs["energy_cost_multiplier"]
        demand_mult = market_inputs["demand_multiplier"]
        mat_mult    = market_inputs["material_cost_multiplier"]

        workers_active = max(1, int(workers_max * worker_frac))
        gbm_pred = gbm_model.predict(
            speed=speed, torque=40.0, tool_wear=100.0, temp_diff=10.0,
            energy_mult=energy_mult, demand_mult=demand_mult,
        )
        failure_prob  = gbm_pred["failure_prob"]
        energy_per_m  = gbm_pred["energy_per_machine"]
        quality_score = gbm_pred["quality_score"]

        active_machines = sum(1 for _ in range(machines) if random.random() > failure_prob)
        worker_eff  = min(workers_active / workers_max, 1.0)
        production  = active_machines * speed * hours * 10 * worker_eff * quality_score
        energy_exp  = active_machines * energy_per_m * hours * e_cost * energy_mult
        mat_exp     = production * mat_cost * mat_mult
        revenue     = production * p_price * demand_mult
        worker_exp  = workers_active * w_cost
        return revenue - energy_exp - mat_exp - worker_exp

    def train(self, factory_inputs, market_scenarios, gbm_model,
              episodes: int = 2000, verbose: bool = False) -> dict:
        rewards_history = []
        for ep in range(episodes):
            market       = random.choice(market_scenarios)
            energy_mult  = market["energy_cost_multiplier"]
            demand_mult  = market["demand_multiplier"]
            gbm_pred     = gbm_model.predict(
                speed=1.0, torque=40, tool_wear=100, temp_diff=10,
                energy_mult=energy_mult, demand_mult=demand_mult,
            )
            failure_prob = gbm_pred["failure_prob"]
            state        = self._discretize_state(energy_mult, demand_mult, failure_prob)
            action_idx   = self._choose_action(state, explore=True)
            speed, worker_frac = self.ACTIONS[action_idx]
            reward       = self._simulate_reward(speed, worker_frac, factory_inputs, market, gbm_model)
            rewards_history.append(reward)
            old_q = self._get_q(state, action_idx)
            self.q_table[(state, action_idx)] = old_q + self.alpha * (reward - old_q)
            if ep % 200 == 0 and self.epsilon > 0.05:
                self.epsilon *= 0.95

        self.trained = True
        last_500 = rewards_history[-500:]
        return {
            "episodes":            episodes,
            "avg_reward_last_500": round(np.mean(last_500), 2),
            "q_table_size":        len(self.q_table),
            "final_epsilon":       round(self.epsilon, 4),
        }

    def recommend(self, energy_mult, demand_mult, failure_prob) -> dict:
        if not self.trained:
            return {"machine_speed": 1.0, "worker_fraction": 1.0, "source": "default"}
        state      = self._discretize_state(energy_mult, demand_mult, failure_prob)
        action_idx = self._choose_action(state, explore=False)
        speed, worker_frac = self.ACTIONS[action_idx]
        return {
            "machine_speed":   speed,
            "worker_fraction": worker_frac,
            "source":          "rl_agent",
        }


    def save(self, path: str):
        if not _JOBLIB_AVAILABLE:
            return
        _ensure_cache_dir()
        joblib.dump({
            "q_table": self.q_table,
            "epsilon": self.epsilon,
            "alpha":   self.alpha,
            "gamma":   self.gamma,
        }, path)

    def load(self, path: str) -> bool:
        if not _JOBLIB_AVAILABLE or not os.path.exists(path):
            return False
        try:
            data = joblib.load(path)
            self.q_table = data["q_table"]
            self.epsilon = data.get("epsilon", 0.05)
            self.alpha   = data.get("alpha",   0.1)
            self.gamma   = data.get("gamma",   0.9)
            self.trained = True
            return True
        except Exception:
            return False

class MLEngine:

    def __init__(self):
        self.gbm        = GradientBoostingModel()
        self.agent      = QLearningAgent()
        self.trained    = False
        self.train_info = {}
        self._cache_key = None
    def train(
        self,
        factory_inputs:  dict,
        df               = None,
        column_mapping:  dict = None,
        episodes:        int  = 2000,
        force_retrain:   bool = False,
    ) -> dict:

        data_source = "csv" if df is not None else "synthetic"
        ck          = _cache_key(factory_inputs, data_source)
        gbm_path    = os.path.join(_CACHE_DIR, f"gbm_{ck}.joblib")
        rl_path     = os.path.join(_CACHE_DIR, f"rl_{ck}.joblib")

        if not force_retrain and _JOBLIB_AVAILABLE:
            gbm_loaded = self.gbm.load(gbm_path)
            rl_loaded  = self.agent.load(rl_path)
            if gbm_loaded and rl_loaded:
                self.trained = True
                self.train_info = {
                    "gbm": {
                        "source":           "cached model (no retraining needed)",
                        "samples":          0,
                        "failure_accuracy": "—",
                        "features":         self.gbm.feature_names,
                    },
                    "rl": {
                        "episodes":            episodes,
                        "avg_reward_last_500": "—",
                        "q_table_size":        len(self.agent.q_table),
                        "final_epsilon":       round(self.agent.epsilon, 4),
                    },
                    "from_cache": True,
                }
                self._cache_key = ck
                return self.train_info

        gbm_info = self.gbm.train(df, column_mapping=column_mapping)

        scenarios = [
            {"energy_cost_multiplier": e, "demand_multiplier": d, "material_cost_multiplier": m}
            for e in [0.8, 1.0, 1.2, 1.5, 1.8, 2.5]
            for d in [0.5, 0.7, 1.0, 1.2, 1.5]
            for m in [1.0, 1.3, 1.7]
        ]
        rl_info = self.agent.train(factory_inputs, scenarios, self.gbm, episodes=episodes)

        if _JOBLIB_AVAILABLE:
            self.gbm.save(gbm_path)
            self.agent.save(rl_path)

        self.trained    = True
        self._cache_key = ck
        self.train_info = {
            "gbm": gbm_info,
            "rl":  rl_info,
            "from_cache": False,
        }
        return self.train_info



    def recommend(self, factory_inputs: dict, market_inputs: dict) -> dict:
        if not self.trained:
            raise RuntimeError("Call .train() first.")

        energy_mult  = market_inputs.get("energy_cost_multiplier", 1.0)
        demand_mult  = market_inputs.get("demand_multiplier", 1.0)
        workers_max  = factory_inputs.get("workers", 30)
        gbm_pred     = self.gbm.predict(
            speed=1.0, torque=40, tool_wear=100, temp_diff=10,
            energy_mult=energy_mult, demand_mult=demand_mult,
        )
        failure_prob = gbm_pred["failure_prob"]
        rl_rec       = self.agent.recommend(energy_mult, demand_mult, failure_prob)

        recommended_workers = max(
            int(workers_max * 0.5),
            int(workers_max * rl_rec["worker_fraction"]),
        )
        return {
            "machine_speed":     rl_rec["machine_speed"],
            "workers_active":    recommended_workers,
            "worker_fraction":   rl_rec["worker_fraction"],
            "predicted_failure": gbm_pred["failure_prob"],
            "predicted_energy":  gbm_pred["energy_per_machine"],
            "predicted_quality": gbm_pred["quality_score"],
            "model_source":      "GBM + RL Agent",
            "gbm_source":        self.train_info["gbm"]["source"],
            "rl_episodes":       self.train_info["rl"]["episodes"],
            "rl_avg_reward":     self.train_info["rl"].get("avg_reward_last_500", "—"),
            "from_cache":        self.train_info.get("from_cache", False),
        }

    def predict_conditions(self, speed, torque, tool_wear,
                           temp_diff, energy_mult: float = 1.0,
                           demand_mult: float = 1.0) -> dict:
        return self.gbm.predict(speed, torque, tool_wear, temp_diff, energy_mult, demand_mult)



    def get_feature_importance(self) -> list[dict]:
        return self.gbm.feature_importance()

    def get_failure_drivers(self, n: int = 3) -> list[str]:

        return self.gbm.get_top_failure_drivers(n=n)

    def cache_status(self) -> dict:
        """Return info about the current model cache state."""
        return {
            "joblib_available": _JOBLIB_AVAILABLE,
            "shap_available":   _SHAP_AVAILABLE,
            "cache_dir":        _CACHE_DIR,
            "from_cache":       self.train_info.get("from_cache", False),
            "cache_key":        self._cache_key,
        }
