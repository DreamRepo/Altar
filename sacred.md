# Sacred — quick concepts


#### Illustration: from original script to Sacred script:

![Sacred script overview](https://raw.githubusercontent.com/Alienor134/Altar/refs/heads/dev/assets/quick_description/sacred_script.png)

- Official docs: https://sacred.readthedocs.io/
- Original paper (PDF): https://ml.informatik.uni-freiburg.de/wp-content/uploads/papers/17-SciPy-Sacred.pdf

A tiny cheat‑sheet for the core pieces you’ll see reflected in Altar:

| Concept | Sacred term | What it means |
|---|---|---|
| Config | `config` | Parameters for a run (hyperparameters, settings). Dict‑like, serializable. |
| Run | `run` | One execution: status, start/stop, resources, seed. |
| Artifacts | `artifacts` | Files saved with the run (images, small CSVs, etc.). |
| Logs | `captured_out` / logging | Stdout/stderr captured; helpful for debugging and provenance. |
| Info | `info` | Free‑form metadata you attach (notes, computed stats, tags). |
| Commands | `@ex.command` | Named entry points (e.g., `train`, `evaluate`). |
| Observer | `Observer` | Backend that stores runs (e.g., MongoObserver for MongoDB). |
| Capture | `@capture` | Inject config values into functions without threading args everywhere. |

## Handy snippets (from this repo's examples)

Below are live excerpts pulled from the `example_sacred` folder in this repository, so you can copy/paste or run them directly.

### Minimal experiment (`example_sacred/experiment.py`)

```python
{% include_relative example_sacred/experiment.py %}
```

### Multiple runs launcher (`example_sacred/run_multi_exp.py`)

```python
{% include_relative example_sacred/run_multi_exp.py %}
```

Tip: these scripts illustrate config definitions, commands, observers, logging metrics with `_run.log_scalar`, adding artifacts, and structuring experiments for repeatable runs.
