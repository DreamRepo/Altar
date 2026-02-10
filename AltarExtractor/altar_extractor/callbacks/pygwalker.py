"""
Pygwalker integration callbacks for AltarExtractor.
"""

from typing import Dict, List
from dash import Input, Output, State, no_update
from dash.dependencies import ClientsideFunction
import dash
import uuid
import pandas as pd
from flask import request, make_response
from bson import ObjectId

from ..state.cache import PYGWALKER_CACHE


def register_pygwalker(app, server):
    """Register pygwalker route and callbacks."""

    # Clientside callback to open pygwalker URL in new tab
    app.clientside_callback(
        ClientsideFunction(namespace="pyg", function_name="open"),
        Output("pygwalker-open-dummy", "children"),
        Input("pygwalker-url", "data"),
    )

    # Flask route for pygwalker page
    @server.route("/pygwalker")
    def pygwalker_route():
        try:
            key = request.args.get("id", "").strip()
            data = PYGWALKER_CACHE.get(key, [])
            df = pd.DataFrame(data or [])
            try:
                from pygwalker.api.html import to_html
                html_str = to_html(df, title="AltarExtractor — Pygwalker")
            except Exception:
                html_str = f"""
<!DOCTYPE html>
<html>
  <head><meta charset="utf-8"><title>Pygwalker unavailable</title></head>
  <body>
    <h2>Pygwalker is not available</h2>
    <p>Install it with: <code>pip install pygwalker</code></p>
    <h3>Preview DataFrame (first 100 rows)</h3>
    <pre>{df.head(100).to_string(index=False)}</pre>
  </body>
</html>
""".strip()
            resp = make_response(html_str)
            resp.headers["Content-Type"] = "text/html; charset=utf-8"
            return resp
        except Exception as exc:
            resp = make_response(f"Failed to render pygwalker page: {exc}")
            resp.headers["Content-Type"] = "text/plain; charset=utf-8"
            return resp, 500

    # Modal open callbacks
    @app.callback(
        Output("open-steps-modal", "is_open", allow_duplicate=True),
        Input("open-pygwalker-btn", "n_clicks"),
        State("open-steps-modal", "is_open"),
        prevent_initial_call=True,
    )
    def open_steps_modal(n_clicks, is_open):
        return True

    @app.callback(
        Output("open-exp-modal", "is_open", allow_duplicate=True),
        Input("open-pygwalker-exp-btn", "n_clicks"),
        State("open-exp-modal", "is_open"),
        prevent_initial_call=True,
    )
    def open_exp_modal(n_clicks, is_open):
        return True

    # Experiments pygwalker callback
    @app.callback(
        Output("pygwalker-url", "data", allow_duplicate=True),
        Output("open-exp-modal", "is_open", allow_duplicate=True),
        Input("open-exp-all-keys", "n_clicks"),
        Input("open-exp-selected-keys", "n_clicks"),
        State("runs-cache", "data"),
        State("config-keys-store", "data"),
        State("filters-store", "data"),
        State("results-select", "value"),
        State("experiments-table", "data"),
        prevent_initial_call=True,
    )
    def open_pygwalker_exp_choice(click_all, click_sel, runs_cache, config_store, filters_store, selected_result_keys, table_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update
        which = ctx.triggered[0]["prop_id"].split(".")[0]

        runs = runs_cache or []
        selected = (config_store or {}).get("selected", [])
        available = (config_store or {}).get("available", [])
        all_keys = list(dict.fromkeys(list(available) + list(selected)))
        active_filters = filters_store or {}

        def row_passes_filters(run_cfg: Dict) -> bool:
            for key in selected:
                f = active_filters.get(key) if isinstance(active_filters, dict) else None
                if not f:
                    continue
                value = run_cfg.get(key, None) if isinstance(run_cfg, dict) else None
                mode = f.get("mode") if isinstance(f, dict) else None
                if mode in ("true", "false"):
                    if not isinstance(value, bool):
                        return False
                    desired = (mode == "true")
                    if value != desired:
                        return False
                has_min = "min" in f and f.get("min") is not None
                has_max = "max" in f and f.get("max") is not None
                if has_min or has_max:
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        return False
                    if has_min and value < f.get("min"):
                        return False
                    if has_max and value > f.get("max"):
                        return False
                values = f.get("values") if isinstance(f, dict) else None
                if isinstance(values, list) and len(values) > 0:
                    if not isinstance(value, str):
                        return False
                    if value not in values:
                        return False
            return True

        filtered_runs = [run for run in runs if row_passes_filters(run.get("config", {}) or {})]

        result_keys = [k for k in (selected_result_keys or []) if isinstance(k, str) and k.strip()]
        data = []
        if which == "open-exp-selected-keys":
            data = table_data or []
        else:
            for run in filtered_runs:
                row = {"run_id": run.get("run_id", ""), "experiment": run.get("experiment", "")}
                cfg = run.get("config", {}) or {}
                if not isinstance(cfg, dict):
                    cfg = {}
                for key in all_keys:
                    row[key] = cfg.get(key)
                r = run.get("result", None)
                if isinstance(r, dict):
                    for key in result_keys:
                        row[f"result:{key}"] = r.get(key, "")
                data.append(row)

        key = str(uuid.uuid4())
        try:
            PYGWALKER_CACHE[key] = data
        except Exception:
            return no_update, False
        return f"/pygwalker?id={key}", False

    # Metrics steps pygwalker callback
    @app.callback(
        Output("pygwalker-url", "data", allow_duplicate=True),
        Output("open-steps-modal", "is_open", allow_duplicate=True),
        Input("open-steps-all-keys", "n_clicks"),
        Input("open-steps-selected-keys", "n_clicks"),
        State("runs-cache", "data"),
        State("config-keys-store", "data"),
        State("filters-store", "data"),
        State("metrics-select", "value"),
        State("metrics-values-store", "data"),
        State("metrics-steps-table", "data"),
        prevent_initial_call=True,
    )
    def open_pygwalker_steps_choice(click_all, click_sel, runs_cache, config_store, filters_store, selected_metrics_names, metrics_values_map, table_data):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update, no_update
        which = ctx.triggered[0]["prop_id"].split(".")[0]

        if which == "open-steps-selected-keys":
            data = table_data or []
            key = str(uuid.uuid4())
            try:
                PYGWALKER_CACHE[key] = data
            except Exception:
                return no_update, False
            return f"/pygwalker?id={key}", False

        runs = runs_cache or []
        selected = (config_store or {}).get("selected", [])
        available = (config_store or {}).get("available", [])
        all_keys = list(dict.fromkeys(list(available) + list(selected)))
        active_filters = filters_store or {}
        metrics_values_map = metrics_values_map or {}
        selected_metrics = [m for m in (selected_metrics_names or []) if isinstance(m, str) and m.strip()]

        def row_passes_filters(run_cfg: Dict) -> bool:
            for key in selected:
                f = active_filters.get(key) if isinstance(active_filters, dict) else None
                if not f:
                    continue
                value = run_cfg.get(key, None) if isinstance(run_cfg, dict) else None
                mode = f.get("mode") if isinstance(f, dict) else None
                if mode in ("true", "false"):
                    if not isinstance(value, bool):
                        return False
                    desired = (mode == "true")
                    if value != desired:
                        return False
                has_min = "min" in f and f.get("min") is not None
                has_max = "max" in f and f.get("max") is not None
                if has_min or has_max:
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        return False
                    if has_min and value < f.get("min"):
                        return False
                    if has_max and value > f.get("max"):
                        return False
                values = f.get("values") if isinstance(f, dict) else None
                if isinstance(values, list) and len(values) > 0:
                    if not isinstance(value, str):
                        return False
                    if value not in values:
                        return False
            return True

        filtered_runs = [run for run in runs if row_passes_filters(run.get("config", {}) or {})]

        def extract_metric_id_for_run(run_metrics, metric_name):
            if isinstance(run_metrics, dict):
                v = run_metrics.get(metric_name, None)
                if isinstance(v, dict) and v.get("id") is not None:
                    return str(v.get("id"))
                if isinstance(v, (str, ObjectId)):
                    return str(v)
                return None
            if isinstance(run_metrics, list):
                for item in run_metrics:
                    if isinstance(item, dict) and item.get("name") == metric_name:
                        mid = item.get("id") or item.get("_id")
                        if mid is not None:
                            return str(mid)
                        return None
            return None

        rows: List[Dict] = []
        for run in filtered_runs:
            base = {"run_id": run.get("run_id", ""), "experiment": run.get("experiment", "")}
            cfg = run.get("config", {}) or {}
            for key in all_keys:
                base[key] = cfg.get(key)

            run_metrics = run.get("metrics", None)
            step_grid = None
            metric_series: Dict[str, List] = {}
            for mname in selected_metrics:
                mid = extract_metric_id_for_run(run_metrics, mname)
                payload = (metrics_values_map or {}).get(str(mid), {}) if mid else {}
                values = payload.get("values") or []
                steps = payload.get("steps") or list(range(len(values)))
                metric_series[mname] = values
                if steps and (step_grid is None or len(steps) > len(step_grid)):
                    step_grid = steps
            if step_grid is None:
                continue

            for idx, step in enumerate(step_grid):
                row = dict(base)
                row["step"] = step
                for mname in selected_metrics:
                    series = metric_series.get(mname, [])
                    row[f"metric:{mname}"] = series[idx] if idx < len(series) else ""
                rows.append(row)

        key = str(uuid.uuid4())
        try:
            PYGWALKER_CACHE[key] = rows
        except Exception:
            return no_update, False
        return f"/pygwalker?id={key}", False

