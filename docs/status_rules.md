# Status rules

This module documents the public-safe sensor status rules used in the synthetic
examples.

The rules are intentionally transparent:

- stale data is classified from last-contact time
- battery status is classified from simple voltage thresholds
- flat-line status is detected from a recent numeric window
- level and flow status are classified from user-provided low/high thresholds

These are demonstration rules. Real operational thresholds should be defined
with project engineers and kept outside public repositories when they reveal
private site behaviour.
