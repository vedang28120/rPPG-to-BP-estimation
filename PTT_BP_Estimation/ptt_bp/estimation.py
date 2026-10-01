from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline


NON_FEATURE_COLUMNS = {"record_id", "subject_id", "mode", "sbp", "dbp"}


def model_features(frame: pd.DataFrame) -> list[str]:
    columns = [c for c in frame.columns if c not in NON_FEATURE_COLUMNS]
    if not columns:
        raise ValueError("No numeric timing features available")
    return columns


def make_model() -> Pipeline:
    return Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("regressor", MultiOutputRegressor(RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3, random_state=42, n_jobs=-1)))
    ])


def fit_model(frame: pd.DataFrame) -> tuple[Pipeline, list[str]]:
    features = model_features(frame)
    if frame[["sbp", "dbp"]].isna().any().any():
        raise ValueError("Training records require cuff-aligned sbp and dbp labels")
    model = make_model()
    model.fit(frame[features], frame[["sbp", "dbp"]])
    return model, features


def predict(model: Pipeline, frame: pd.DataFrame, features: list[str]) -> np.ndarray:
    return model.predict(frame.reindex(columns=features))
