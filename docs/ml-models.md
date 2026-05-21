# ML Model Strategy

GhostProof ships with deterministic heuristic fallbacks. Production deployments should register calibrated models per modality.

## Image

Recommended:

- EfficientNet-B4 or ConvNeXt forensic classifier trained on real and synthetic images.
- Frequency-domain classifier for GAN/diffusion artifact patterns.
- Face artifact detector with landmarks and local inconsistency maps.
- Metadata classifier for C2PA, EXIF absence, software lineage, and compression anomalies.

## Video

Recommended:

- X3D, R(2+1)D, or TimeSformer temporal classifier.
- Face crop sequence model for warping and identity drift.
- Lip-sync model such as SyncNet-style embedding comparison.
- Blink and gaze consistency analysis.

## Audio

Recommended:

- RawNet2 or wav2vec2 classifier fine-tuned for spoofing.
- LFCC/mel-spectrogram CNN for synthetic harmonics.
- Speaker verification mismatch against claimed speaker when consented reference exists.

## Text

Recommended:

- RoBERTa or DeBERTa classifier calibrated per domain.
- Perplexity and burstiness features from a small local language model.
- Stylometry and repetition features.

## Registry Requirements

- Signed model artifact manifest.
- Dataset card and intended-use notes.
- Calibration curves and threshold report.
- Robustness report for compression, resize, paraphrase, noise, and adversarial perturbation.
