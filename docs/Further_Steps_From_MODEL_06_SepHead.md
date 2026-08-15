# Further Steps From MODEL-06-SepHead

## Current checkpoint

Current best model:

```text
Dual-Branch 1D-ResNet
        ↓
BiGRU
        ↓
Multi-Head Self-Attention
        ↓
separate SBP / DBP heads
```

Current original results:

| Model | SBP MAE | SBP RMSE | SBP r | DBP MAE | DBP RMSE | DBP r | Subject SBP | Subject DBP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MODEL-06-SepHead | 11.58 | 14.58 | 0.388 | 6.70 | 8.54 | 0.355 | **10.12** | **5.91** |

**Freeze this checkpoint. Do not overwrite it.**

Suggested name:

```text
MODEL-06-SepHead_original.pth
```

---

# 1. Immediate objective

Do **not** make the architecture more complicated yet.

The next question is whether the BP distribution is limiting learning.

Run:

```text
Original training distribution
        ↓
MODEL-06-SepHead
```

versus:

```text
Balanced training distribution
        ↓
same MODEL-06-SepHead
```

Keep validation and test distributions completely unchanged.

---

# 2. Analyze the BP distribution first

For TRAIN / VALIDATION / TEST, calculate:

```text
SBP:
count, mean, median, std, min, max, percentiles

DBP:
count, mean, median, std, min, max, percentiles
```

Generate:

```text
SBP histogram
DBP histogram
SBP vs DBP scatter
```

Use only the training set when deciding balancing weights/bins.

---

# 3. Check regression-to-the-mean

For the current model, plot:

```text
true SBP vs predicted SBP
true DBP vs predicted DBP
```

Calculate:

```text
true mean/std
prediction mean/std
bias by BP range
MAE by BP range
```

Look specifically for:

```text
low BP → overprediction
high BP → underprediction
```

or the reverse.

If this exists, balancing becomes particularly important.

---

# 4. Never balance validation or test

Correct:

```text
MCD-Iriun
    ↓
subject-level split
    ↓
┌──────────┬──────────┬──────────┐
TRAIN      VALID      TEST
  ↓          │          │
balance    unchanged  unchanged
```

Do not balance the complete dataset before splitting.

Do not change the test distribution.

---

# 5. Use subject-aware balancing

Avoid repeatedly duplicating individual windows:

```text
rare window → duplicate 10×
```

Highly overlapping windows from one subject are correlated.

Prefer:

```text
BP range
   ↓
subject-aware sampling / weighting
   ↓
training
```

Rare BP ranges should receive more exposure without allowing a small number of subjects to dominate.

---

# 6. Run three training variants

### EXP-A — Original

```text
Natural MCD training distribution
```

This is your existing MODEL-06-SepHead.

### EXP-B — Moderate balancing

Reduce dominance of common BP ranges while retaining some natural distribution.

### EXP-C — Strong balancing

More aggressively equalize BP ranges.

Do not change architecture, preprocessing, windowing, input representation, optimizer, or evaluation protocol between A/B/C.

The only intended change is training sampling.

---

# 7. Balancing strategy

Create SBP/DBP bins using the **training set only**.

Start with weighted sampling.

Conceptually:

```text
weight ∝ 1 / bin_frequency
```

but cap the maximum weight.

For example:

```text
weight = min(max_weight,
             target_frequency / bin_frequency)
```

Do not massively oversample extremely rare samples.

Initially prioritize SBP balancing because SBP is the weaker target, while monitoring DBP carefully.

If needed later, investigate joint SBP/DBP balancing.

---

# 8. Evaluate more than global MAE

For every experiment report:

```text
Window:
SBP MAE
SBP RMSE
SBP r
DBP MAE
DBP RMSE
DBP r

Subject:
SBP MAE
DBP MAE
```

Also report:

```text
MAE by BP bin
bias by BP bin
prediction range
```

A balanced model is valuable if it improves underrepresented ranges without seriously damaging the overall result.

---

# 9. Keep the original checkpoint

Regardless of results, keep:

```text
MODEL-06-SepHead_original.pth
MODEL-06-SepHead_balanced_moderate.pth
MODEL-06-SepHead_balanced_strong.pth
```

Never replace the original model.

---

# 10. Current input decision

Your derivative ablation was:

```text
PPG only
PPG + vPPG
PPG + vPPG + aPPG
```

It did not justify making all derivatives part of the main model.

For the balancing experiment use:

```text
PPG
```

as the primary input.

Do not add more architecture or features simultaneously.

This is also preferable for eventual rPPG deployment because numerical derivatives can amplify camera noise.

---

# 11. Next: compare the old MCD-Iriun LSTM

After balancing, run the previous MCD-Iriun LSTM on **exactly the same test protocol**.

Compare:

```text
old MCD-Iriun LSTM
MODEL-06-SepHead original
best balanced MODEL-06-SepHead
```

Use:

```text
same subjects
same preprocessing
same target definitions
same evaluation code
```

This establishes whether the new architecture genuinely replaces the old LSTM.

---

# 12. Do not ensemble yet

Do not combine the LSTM and MODEL-06 immediately.

First calculate on identical held-out subjects:

```text
LSTM error
MODEL-06 error
correlation(LSTM error, MODEL-06 error)
```

If errors are highly correlated, an ensemble probably adds little.

If errors are complementary, test a fusion/ensemble using validation data.

---

# 13. MIMIC-III transfer experiment

Your existing:

```text
lstm_ppg_nonmixed
```

should first be used as a **pretraining candidate**, not simply as another BP predictor.

Test:

```text
MIMIC-III PPG
      ↓
PPG representation pretraining
      ↓
transfer compatible encoder
      ↓
MCD-Iriun
      ↓
MODEL-06-SepHead fine-tuning
```

Compare against:

```text
MODEL-06-SepHead trained from scratch on MCD
```

If MIMIC pretraining does not improve unseen-subject MCD performance, stop using it.

Do not blindly concatenate MIMIC + MCD.

---

# 14. External validation

After selecting the best MCD model:

```text
best MCD model
      ↓
freeze
      ↓
external compatible dataset
```

CLBP-300 is a relevant candidate when its data/labels are compatible with your evaluation.

Initially use the external dataset for testing, not training.

---

# 15. Critical PPG → rPPG experiment

The current model uses:

```text
MCD-Iriun synchronized PPG
```

not:

```text
camera RGB → rPPG
```

Therefore it is currently a **physiological BP model**, not yet a complete camera BP model.

Test:

```text
PPG → BP
```

against:

```text
camera RGB
   ↓
rPPG
   ↓
same BP model
```

This measures the camera-domain gap.

---

# 16. Build paired PPG/rPPG evaluation

Where synchronized recordings exist, preserve:

```text
contact PPG
camera RGB/rPPG
timestamps
SBP
DBP
subject ID
ROI
signal quality
```

Compare:

```text
waveform similarity
HR error
spectral similarity
beat timing
morphology
BP prediction error
```

This separates poor rPPG extraction from poor BP modeling.

---

# 17. rPPG adaptation

After zero-shot testing, evaluate:

### A — Zero-shot

```text
PPG-trained MODEL-06
        ↓
rPPG
        ↓
BP
```

### B — Frozen encoder

```text
PPG encoder
    ↓
freeze
    ↓
rPPG adaptation
```

### C — Partial fine-tuning

```text
PPG model
    ↓
fine-tune final layers
    ↓
rPPG
```

### D — Full fine-tuning

```text
PPG model
    ↓
low-learning-rate fine-tuning
    ↓
rPPG
```

Select using subject-independent validation.

---

# 18. Do not add more architecture yet

Postpone:

```text
larger ResNet
more attention
Transformer
larger BiGRU
additional derivatives
more fusion blocks
```

The current architecture already provides meaningful improvement over your simpler baselines.

The next bottleneck should be determined experimentally.

---

# 19. Personal calibration comes later

Once the best generic model is selected:

```text
generic BP model
      +
one cuff measurement
      ↓
personal calibration
      ↓
future BP estimates
```

Compare:

```text
uncalibrated
vs
one-point calibrated
```

Also evaluate within-subject BP changes where the dataset supports them.

Calibration is not a replacement for generalization.

---

# 20. Gold progression

```text
CURRENT
MODEL-06-SepHead original
        │
        ↓
1. BP distribution analysis
        │
        ↓
2. Moderate balancing
        │
        ↓
3. Strong balancing
        │
        ↓
4. BP-bin / bias evaluation
        │
        ↓
5. Select best balanced candidate
        │
        ├──────────────┐
        ↓              ↓
6. Old LSTM test    7. MIMIC transfer
        │              │
        └──────┬───────┘
               ↓
       8. Best PPG model
               ↓
       9. External validation
               ↓
      10. rPPG zero-shot
               ↓
      11. rPPG adaptation
               ↓
      12. Quality/uncertainty gate
               ↓
      13. Personal calibration
               ↓
      14. TFLite/mobile optimization
```

---

# 21. Exact next actions

## Action 1
Freeze:

```text
MODEL-06-SepHead_original.pth
```

## Action 2
Analyze:

```text
SBP/DBP distributions
prediction distributions
BP-bin MAE
BP-bin bias
```

## Action 3
Train:

```text
MODEL-06-SepHead + moderate balancing
```

## Action 4
Train:

```text
MODEL-06-SepHead + strong balancing
```

## Action 5
Compare all three on the same untouched test set.

## Action 6
Select using:

```text
subject MAE
+
correlation
+
BP-bin performance
+
bias
```

## Action 7
Evaluate the old MCD-Iriun LSTM on the same protocol.

## Action 8
Run:

```text
MIMIC pretrained → MCD fine-tuned
```

## Action 9
Test the best PPG model externally.

## Action 10
Begin:

```text
PPG → rPPG → BP
```

domain-transfer experiments.

---

# 22. Decision tree

```text
Does moderate balancing improve BP-bin bias
without seriously hurting overall performance?
             │
       ┌─────┴─────┐
      YES           NO
       │             │
       ↓             ↓
Keep candidate     Keep original
       │             │
       └──────┬──────┘
              ↓
       Compare old LSTM
              ↓
       MIMIC pretraining
              ↓
       External validation
              ↓
       rPPG zero-shot
              ↓
       rPPG adaptation
              ↓
       Calibration
              ↓
       Mobile deployment
```

---

# 23. Definition of the next milestone

The next milestone is **not** simply obtaining the lowest MCD MAE.

It is determining whether:

1. balancing improves individualized BP estimation;
2. MODEL-06-SepHead generalizes better than the old LSTM;
3. MIMIC pretraining provides transferable information;
4. the best PPG model survives the transition to camera rPPG.

Only after those questions are answered should you add architecture complexity or an ensemble.

---

# 24. Current project state

```text
✓ MCD-Iriun PPG
✓ Population baseline
✓ Demographic baseline
✓ ResNet baseline
✓ Dual-Branch ResNet + BiGRU
✓ MHSA
✓ Demographic fusion
✓ Separate SBP/DBP heads
✓ MODEL-06-SepHead original = current best
✓ PPG/vPPG/aPPG ablation

NEXT:
→ BP distribution analysis
→ moderate balancing
→ strong balancing
→ same-test comparison
→ old LSTM comparison
→ MIMIC transfer
→ external validation
→ rPPG transfer
→ calibration
→ mobile deployment
```
