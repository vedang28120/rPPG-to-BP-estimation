from __future__ import annotations

import argparse
import joblib
import numpy as np
import pandas as pd

from .config import PipelineConfig
from .estimation import predict
from .run_pipeline import build_features


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved PTT/PAT BP model on cuff-labelled records.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    frame = build_features(args.manifest, PipelineConfig.from_json(args.config))
    if frame[["sbp", "dbp"]].isna().any().any():
        raise ValueError("Evaluation requires cuff-aligned sbp and dbp labels")
    artifact = joblib.load(args.model)
    predicted = predict(artifact["model"], frame, artifact["features"])
    result = frame[["record_id", "subject_id", "sbp", "dbp"]].copy()
    result[["pred_sbp", "pred_dbp"]] = predicted
    result["sbp_error"] = result.pred_sbp - result.sbp
    result["dbp_error"] = result.pred_dbp - result.dbp
    result.to_csv(args.output, index=False)
    print("SBP MAE:", round(float(np.mean(np.abs(result.sbp_error))), 3), "mmHg")
    print("DBP MAE:", round(float(np.mean(np.abs(result.dbp_error))), 3), "mmHg")


if __name__ == "__main__":
    main()
