import pandas as pd
import numpy as np
from typing import Optional

COLUMN_KEYWORDS = {
    "speed": [
        "speed", "rpm", "rotation", "rotational", "velocity",
        "vitesse", "frequence", "frequency", "spindle"
    ],
    "torque": [
        "torque", "force", "couple", "moment", "load", "charge", "torsion"
    ],
    "tool_wear": [
        "wear", "usure", "tool", "outil", "abrasion", "age",
        "runtime", "hours", "heures", "cycle", "mileage"
    ],
    "temperature": [
        "temp", "temperature", "heat", "chaleur", "thermal",
        "process_temp", "air_temp", "celsius", "kelvin"
    ],
    "failure": [
        "failure", "fail", "defect", "fault", "panne", "defaillance",
        "breakdown", "error", "alarm", "anomaly", "anomalie",
        "incident", "malfunction", "label", "target", "machine failure"
    ],
    "energy": [
        "energy", "power", "watt", "kwh", "consommation",
        "consumption", "electricity", "electricite"
    ],
    "pressure": [
        "pressure", "pression", "bar", "psi", "pascal"
    ],
    "vibration": [
        "vibration", "vibr", "acceleration", "shock", "choc"
    ],
    "quality": [
        "quality", "qualite", "grade", "score", "yield",
        "rendement", "pass", "ok", "good"
    ]
}


def _score_column(col_name: str, keywords: list) -> float:
    col_lower = col_name.lower().replace("_", " ").replace("-", " ")
    score = 0.0
    for kw in keywords:
        if kw in col_lower:
            score += 2.0 if f" {kw} " in f" {col_lower} " else 1.0
    return score


def detect_columns(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    mapping = {}

    for feature, keywords in COLUMN_KEYWORDS.items():
        best_col, best_score = None, 0.0
        for col in numeric_cols:
            score = _score_column(col, keywords)
            if score > best_score:
                best_score = score
                best_col   = col
        mapping[feature] = best_col if best_score > 0 else None

    if mapping["failure"] is None:
        for col in numeric_cols:
            unique_vals = df[col].dropna().unique()
            if set(unique_vals).issubset({0, 1, 0.0, 1.0}):
                mapping["failure"] = col
                break

    return mapping


def normalize_column(series: pd.Series, feature: str) -> pd.Series:
    s = series.dropna()
    if len(s) == 0:
        return series

    if feature == "speed":
        mn, mx = s.min(), s.max()
        if mx > mn:
            return 0.4 + (series - mn) / (mx - mn) * 1.2
        return pd.Series(np.ones(len(series)) * 1.0, index=series.index)

    elif feature == "torque":
        return series.clip(0, 200)

    elif feature == "tool_wear":
        mn, mx = s.min(), s.max()
        if mx > 300:
            return series * (300 / mx)
        return series.clip(0, 300)

    elif feature == "temperature":
        mn = s.min()
        if mn > 200:
            return series - 273.15 + 25
        elif mn > 50:
            return (series - 32) * 5 / 9
        return series

    elif feature == "failure":
        if s.max() > 1:
            return (series > series.median()).astype(int)
        return series.fillna(0).astype(int)

    elif feature == "energy":
        mn, mx = s.min(), s.max()
        if mx > mn:
            return 1.0 + (series - mn) / (mx - mn) * 10
        return series

    else:
        mn, mx = s.min(), s.max()
        if mx > mn:
            return (series - mn) / (mx - mn)
        return series


def adapt_dataset(df: pd.DataFrame, user_mapping: Optional[dict] = None) -> dict:
    df           = df.copy()
    auto_mapping = detect_columns(df)
    mapping      = {**auto_mapping, **(user_mapping or {})}
    stats            = {}
    confidence_hits  = 0
    total_features   = 5

    if mapping.get("failure") and mapping["failure"] in df.columns:
        fail_col            = normalize_column(df[mapping["failure"]], "failure")
        stats["failure_rate"] = round(float(fail_col.mean()), 4)
        confidence_hits     += 1
    else:
        stats["failure_rate"] = 0.034

    if mapping.get("tool_wear") and mapping["tool_wear"] in df.columns:
        wear_col              = normalize_column(df[mapping["tool_wear"]], "tool_wear")
        stats["avg_tool_wear"] = round(float(wear_col.mean()), 1)
        confidence_hits       += 1
    else:
        stats["avg_tool_wear"] = 108.0

    if mapping.get("temperature") and mapping["temperature"] in df.columns:
        temp_col          = normalize_column(df[mapping["temperature"]], "temperature")
        stats["temp_diff"] = round(float(temp_col.std() * 2 + 8), 2)
        confidence_hits   += 1
    else:
        stats["temp_diff"] = 10.0

    if mapping.get("torque") and mapping["torque"] in df.columns:
        torque_col          = normalize_column(df[mapping["torque"]], "torque")
        stats["avg_torque"] = round(float(torque_col.mean()), 2)
        confidence_hits     += 1
    else:
        stats["avg_torque"] = 40.0

    if mapping.get("speed") and mapping["speed"] in df.columns:
        speed_col         = normalize_column(df[mapping["speed"]], "speed")
        stats["avg_rpm"]  = round(float(speed_col.mean() * 2860), 0)
        confidence_hits   += 1
    else:
        stats["avg_rpm"] = 1538.0

    if mapping.get("energy") and mapping["energy"] in df.columns:
        energy_col                         = normalize_column(df[mapping["energy"]], "energy")
        stats["avg_energy_consumption"]    = round(float(energy_col.mean()), 2)

    if mapping.get("vibration") and mapping["vibration"] in df.columns:
        vib_col                = df[mapping["vibration"]].dropna()
        stats["avg_vibration"] = round(float(vib_col.mean()), 3)

    stats["total_records"] = len(df)
    stats["confidence"]    = round(confidence_hits / total_features, 2)

    return {
        "adapted_stats":  stats,
        "column_mapping": mapping,
        "confidence":     stats["confidence"],
        "detected_cols":  {k: v for k, v in mapping.items() if v is not None},
        "missing_cols":   [k for k, v in mapping.items() if v is None]
    }


def prepare_ml_training_data(df: pd.DataFrame, mapping: dict) -> tuple:
    required = ["speed", "failure"]
    for r in required:
        if not mapping.get(r) or mapping[r] not in df.columns:
            return None

    n = len(df)
    speed_col  = normalize_column(df[mapping["speed"]], "speed")         if mapping.get("speed")  and mapping["speed"]  in df.columns else pd.Series(np.ones(n))
    torque_col = normalize_column(df[mapping["torque"]], "torque")       if mapping.get("torque") and mapping["torque"] in df.columns else pd.Series(np.random.uniform(20, 60, n))
    wear_col   = normalize_column(df[mapping["tool_wear"]], "tool_wear") if mapping.get("tool_wear") and mapping["tool_wear"] in df.columns else pd.Series(np.random.uniform(50, 200, n))
    temp_col   = normalize_column(df[mapping["temperature"]], "temperature") if mapping.get("temperature") and mapping["temperature"] in df.columns else pd.Series(np.random.uniform(298, 312, n))

    temp_diff      = temp_col.std() * 2 + 8 if mapping.get("temperature") else 10.0
    temp_diff_col  = pd.Series(np.full(n, temp_diff))
    speed_setting  = speed_col.copy()
    energy_mult    = pd.Series(np.ones(n))
    demand_mult    = pd.Series(np.ones(n))

    X = np.column_stack([
        speed_col.values, torque_col.values, wear_col.values,
        temp_diff_col.values, speed_setting.values,
        energy_mult.values, demand_mult.values
    ])

    y_failure = normalize_column(df[mapping["failure"]], "failure").values.astype(int)

    if mapping.get("energy") and mapping["energy"] in df.columns:
        y_energy = normalize_column(df[mapping["energy"]], "energy").values
    else:
        y_energy = (speed_col * torque_col * 0.05 + np.random.normal(0, 0.3, n)).values

    if mapping.get("quality") and mapping["quality"] in df.columns:
        y_quality = normalize_column(df[mapping["quality"]], "quality").values
    else:
        y_quality = np.clip(
            1.0 - 0.003 * wear_col.values - 0.005 * temp_diff + np.random.normal(0, 0.05, n),
            0, 1
        )

    return X, y_failure, y_energy, y_quality


def get_dataset_summary(df: pd.DataFrame, mapping: dict) -> dict:
    detected = {k: v for k, v in mapping.items() if v is not None}
    missing  = [k for k, v in mapping.items() if v is None]
    return {
        "total_rows":        len(df),
        "total_columns":     len(df.columns),
        "detected_features": len(detected),
        "missing_features":  len(missing),
        "detected":          detected,
        "missing":           missing,
        "column_names":      df.columns.tolist()
    }
