from __future__ import annotations

import argparse
from pathlib import Path
import joblib

from .config import PipelineConfig
from .estimation import fit_model
from .run_pipeline import build_features


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a cuff-calibrated timing-feature BP model.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--model-out", required=True)
    args = parser.parse_args()
    frame = build_features(args.manifest, PipelineConfig.from_json(args.config))
    model, features = fit_model(frame)
    destination = Path(args.model_out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": features}, destination)
    print(f"Trained on {len(frame)} records; wrote {destination}")


if __name__ == "__main__":
    main()
