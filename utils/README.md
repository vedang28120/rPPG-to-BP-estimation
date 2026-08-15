# Utilities Module (`utils/`)

## Purpose
Provides cross-cutting tools for structured CSV telemetry logging, publication-grade visualization, clinical ANSI/AAMI Bland-Altman validation, PDF reporting, and repository hygiene.

## Dependencies
- External Libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `fpdf2`, `opencv-python`, `scikit-learn`
- Internal Modules: Consumes metadata and outputs from `core_extraction/`, `filtering/`, and `models/inference/`

## Key Files
- `bland_altman_validator.py`: Executes strict Subject-Independent 5-Fold Cross-Validation, evaluating ANSI/AAMI compliance (mean error $\le 5$ mmHg, SD $\le 8$ mmHg) and BHS protocol grading.
- `research_visualizer.py`: Generates IEEE/Nature-styled figures: 3D Takens phase portraits, Bayesian predictive uncertainty error bars ($\pm 2\sigma$), LDS smoothed label distributions, MediaPipe wireframes, and Bland-Altman agreement plots.
- `data_logger.py`: High-performance append-mode CSV logger for frame-by-frame 13-column optical data (`pos_extraction_log.csv`) and windowed vitals telemetry (`vitals_log.csv`).
- `pdf_report_generator.py`: PDF engine built on `fpdf2` that compiles executive summaries, graphical figures, sample CSV tables, and clinical vital sign cards into `Project_Documentation.pdf`.
- `cleanup_manager.py`: DevOps cleanup script utilizing safe whitelisting and automated archiving to maintain repository hygiene.
- `plot_mae.py`: Specialized MAE error distribution boxplot visualizer.
