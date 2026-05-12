# Appendix D: Architectural Ablation Study

This study tests three configurations across the 22 core tasks from the exhaustive benchmark to evaluate the impact of the Feedback and Memory layers.

## Table II: Ablation Performance Summary

| Architecture Configuration | Success Rate | Avg Iterations (CT) | Total Recoveries (RR) | Avg Strategy Diversity (SD) | Avg Failures Tolerated (FT) |
|---|---|---|---|---|---|
| single-agent | 68.8% (11/16) | 1.12 | 0 | 1.00 | 0.31 |
| no-memory | 81.2% (13/16) | 1.75 | 0 | 1.12 | 0.06 |
| no-security | 87.5% (14/16) | 1.56 | 1 | 1.31 | 0.19 |
| full-ASC | 81.2% (13/16) | 2.00 | 2 | 1.44 | 0.12 |
