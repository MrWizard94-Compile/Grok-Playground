# EXP-028 Adversarial High Frontier Report

Date: 20260701_085128
Classification: [ADVERSARIAL / SUPPORTED INFERENCE + MODEL TEST]

**Key Observation [OBSERVATION]:** Adversarial high-F construction (wide fan-in from large source pool) achieved F up to ~108 at N~900. Mean obs_L = 0.1123 (vs controlled ref 0.1091).

Delta modest. Architecture appears to keep L low even under deliberately maximized frontier width.
This is evidence that raw graph F is not the sole (or dominant in this impl) determinant of executive locality.

Full data + plots in this dir and plots/.
See RESEARCH_LOG and CLAIMS for integration.
