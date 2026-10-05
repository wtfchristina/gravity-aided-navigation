# Integrity Monitoring Research Layer

Version 0.4 adds an integrity-analysis layer intended for research and trade studies.

The implementation computes:

- position error against simulation truth
- a causal rolling protection-level **proxy**
- alert-limit exceedance
- empirical availability
- an HMI-like proxy event rate when truth error exceeds the alert limit without an alert

This deliberately uses the word **proxy**. The implementation is not an aviation-certified protection-level algorithm, RAIM implementation, or safety case. It exists to make integrity concepts visible in the same workflow as navigation accuracy and sensor trade studies.

Example:

```bash
qpnt integrity configs/fixed_wing_fused.yaml --runs 25 --alert-limit-m 300
```
