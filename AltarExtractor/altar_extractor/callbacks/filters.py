"""
Filter-related callbacks for AltarExtractor.
"""

from typing import Dict
from dash import html, dcc, Input, Output, State, no_update, ALL
import dash
import dash_bootstrap_components as dbc
import json


def register_filters_callbacks(app):
    """Register filter-related callbacks."""

    @app.callback(
        Output("config-keys-select", "options"),
        Output("config-keys-select", "value"),
        Output("config-keys-select", "style"),
        Output("config-keys-none-note", "children"),
        Input("config-keys-store", "data"),
        Input("runs-cache", "data"),
        prevent_initial_call=False,
    )
    def populate_config_keys_dropdown(store, runs_cache):
        data = store or {"available": [], "selected": []}
        available = data.get("available", []) or []
        selected = data.get("selected", []) or []
        all_keys = sorted(set(list(available) + list(selected)))

        runs = runs_cache or []

        def type_name_for_value(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return "boolean"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return "number"
            if isinstance(value, str):
                return "string"
            if isinstance(value, list):
                return "list"
            if isinstance(value, dict):
                return "dict"
            return "unknown"

        key_to_type: Dict[str, str] = {}
        for key in all_keys:
            seen_types = set()
            for run in runs:
                cfg = run.get("config", {}) or {}
                if isinstance(cfg, dict) and key in cfg:
                    t = type_name_for_value(cfg.get(key))
                    if t is not None:
                        seen_types.add(t)
                if len(seen_types) > 1:
                    break
            if len(seen_types) == 0:
                key_to_type[key] = "unknown"
            elif len(seen_types) == 1:
                key_to_type[key] = next(iter(seen_types))
            else:
                key_to_type[key] = "mixed"

        def encode_for_set(value):
            try:
                return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
            except Exception:
                return str(value)

        key_to_value_count: Dict[str, int] = {}
        for key in all_keys:
            distinct = set()
            for run in runs:
                cfg = run.get("config", {}) or {}
                if not isinstance(cfg, dict):
                    continue
                v = cfg.get(key, None)
                if v is None:
                    continue
                distinct.add(encode_for_set(v))
            key_to_value_count[key] = len(distinct)

        options = [{"label": f"{k} ({key_to_type.get(k, 'unknown')} {key_to_value_count.get(k, 0)})", "value": k} for k in all_keys]
        if len(options) == 0:
            return [], [], {"display": "none"}, "No config keys found"
        selected_clean = [k for k in selected if k in set(all_keys)]
        note = "All keys selected" if (len(selected_clean) == len(all_keys) and len(all_keys) > 0) else ""
        return options, selected_clean, {}, note

    @app.callback(
        Output("config-keys-store", "data", allow_duplicate=True),
        Input("config-keys-select", "value"),
        State("config-keys-store", "data"),
        prevent_initial_call=True,
    )
    def on_config_keys_select_change(selected_values, store):
        store = store or {"available": [], "selected": []}
        available_old = list(store.get("available", []) or [])
        selected_old = list(store.get("selected", []) or [])
        all_keys = list(dict.fromkeys(list(available_old) + list(selected_old)))
        selected_set = set(k for k in (selected_values or []) if k in set(all_keys))
        available = [k for k in all_keys if k not in selected_set]
        selected = [k for k in all_keys if k in selected_set]
        return {"available": available, "selected": selected}

    @app.callback(
        Output("available-keys", "children"),
        Output("selected-keys", "children"),
        Input("config-keys-store", "data"),
        Input("runs-cache", "data"),
        Input("filters-store", "data"),
    )
    def render_key_lists(config_store, runs_cache, filters_store):
        store = config_store or {"available": [], "selected": []}
        available = store.get("available", []) or []
        selected = store.get("selected", []) or []
        runs = runs_cache or []
        keys_to_check = set(list(available) + list(selected))

        def type_name_for_value(value):
            if value is None:
                return None
            if isinstance(value, bool):
                return "boolean"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return "number"
            if isinstance(value, str):
                return "string"
            if isinstance(value, list):
                return "list"
            if isinstance(value, dict):
                return "dict"
            return "unknown"

        key_to_type: Dict[str, str] = {}
        for key in keys_to_check:
            seen_types = set()
            for run in runs:
                cfg = run.get("config", {}) or {}
                if isinstance(cfg, dict) and key in cfg:
                    t = type_name_for_value(cfg.get(key))
                    if t is not None:
                        seen_types.add(t)
                if len(seen_types) > 1:
                    break
            if len(seen_types) == 0:
                key_to_type[key] = "unknown"
            elif len(seen_types) == 1:
                key_to_type[key] = next(iter(seen_types))
            else:
                key_to_type[key] = "mixed"

        def encode_for_set(value):
            try:
                return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)
            except Exception:
                return str(value)

        key_to_str_values: Dict[str, list] = {}
        key_to_value_count: Dict[str, int] = {}

        for key in selected:
            values = set()
            for run in runs:
                cfg = run.get("config", {}) or {}
                if isinstance(cfg, dict):
                    v = cfg.get(key)
                    if isinstance(v, str):
                        values.add(v)
            if values:
                key_to_str_values[key] = sorted(values)

        for key in keys_to_check:
            distinct = set()
            for run in runs:
                cfg = run.get("config", {}) or {}
                if not isinstance(cfg, dict):
                    continue
                v = cfg.get(key, None)
                if v is None:
                    continue
                distinct.add(encode_for_set(v))
            key_to_value_count[key] = len(distinct)

        available_children = [
            dbc.ListGroupItem(
                f"{key} ({key_to_type.get(key, 'unknown')} {key_to_value_count.get(key, 0)})",
                id={"type": "available-key", "key": key},
                action=True,
                n_clicks=0,
            )
            for key in available
        ]

        existing_filters = filters_store or {}
        selected_children = []

        for key in selected:
            ktype = key_to_type.get(key, "unknown")
            current = existing_filters.get(key, {}) if isinstance(existing_filters, dict) else {}
            cnt = key_to_value_count.get(key, 0)
            label = html.Div(f"{key} ({cnt})")

            if ktype == "boolean":
                control = dbc.RadioItems(
                    options=[
                        {"label": "All", "value": "all"},
                        {"label": "True", "value": "true"},
                        {"label": "False", "value": "false"},
                    ],
                    value=current.get("mode", "all"),
                    id={"type": "filter-bool", "key": key},
                    inline=True,
                )
            elif ktype == "number":
                control = dbc.Row(
                    [
                        dbc.Col(dcc.Input(id={"type": "filter-number-min", "key": key}, type="number", placeholder="min", value=current.get("min", None), style={"width": "100%"}), md=6),
                        dbc.Col(dcc.Input(id={"type": "filter-number-max", "key": key}, type="number", placeholder="max", value=current.get("max", None), style={"width": "100%"}), md=6),
                    ],
                    class_name="g-2",
                )
            elif ktype == "string":
                control = dcc.Dropdown(
                    id={"type": "filter-string", "key": key},
                    options=[{"label": v, "value": v} for v in key_to_str_values.get(key, [])],
                    value=current.get("values", []),
                    multi=True,
                    placeholder="Select values...",
                    style={"width": "100%"},
                )
            else:
                control = html.Div("No filters", style={"color": "#666"})

            buttons = html.Div(
                [
                    dbc.Button(
                        html.I(className="bi bi-chevron-up", style={"fontSize": "1.15rem", "lineHeight": "1"}),
                        id={"type": "move-up", "key": key},
                        size="sm",
                        color="link",
                        class_name="px-1 py-0 lh-1",
                        style={"height": "1.25rem"},
                    ),
                    dbc.Button(
                        html.I(className="bi bi-chevron-down", style={"fontSize": "1.15rem", "lineHeight": "1"}),
                        id={"type": "move-down", "key": key},
                        size="sm",
                        color="link",
                        class_name="px-1 py-0 lh-1",
                        style={"height": "1.25rem"},
                    ),
                    dbc.Button(
                        html.I(className="bi bi-x-lg", style={"fontSize": "1.15rem", "lineHeight": "1"}),
                        id={"type": "remove-selected-key", "key": key},
                        size="sm",
                        color="link",
                        class_name="px-1 py-0 lh-1 text-danger",
                        style={"height": "1.25rem"},
                    ),
                ],
                style={"whiteSpace": "nowrap"},
            )

            selected_children.append(
                dbc.ListGroupItem(
                    dbc.Row(
                        [
                            dbc.Col(label, md=6),
                            dbc.Col(control, md=5),
                            dbc.Col(buttons, md=1, class_name="text-end"),
                        ],
                        class_name="g-2 align-items-center",
                    ),
                    id={"type": "selected-key", "key": key},
                    action=False,
                    color="primary",
                )
            )

        return available_children, selected_children

    @app.callback(
        Output("filters-store", "data", allow_duplicate=True),
        Input({"type": "filter-bool", "key": ALL}, "value"),
        Input({"type": "filter-number-min", "key": ALL}, "value"),
        Input({"type": "filter-number-max", "key": ALL}, "value"),
        Input({"type": "filter-string", "key": ALL}, "value"),
        State({"type": "filter-bool", "key": ALL}, "id"),
        State({"type": "filter-number-min", "key": ALL}, "id"),
        State({"type": "filter-number-max", "key": ALL}, "id"),
        State({"type": "filter-string", "key": ALL}, "id"),
        State("config-keys-store", "data"),
        prevent_initial_call=True,
    )
    def update_filters_store(bool_values, min_values, max_values, string_values, bool_ids, min_ids, max_ids, string_ids, config_store):
        filters: Dict[str, Dict] = {}
        selected = (config_store or {}).get("selected", []) or []

        for idx, id_obj in enumerate(bool_ids or []):
            key = id_obj.get("key")
            if key not in selected:
                continue
            val = (bool_values or [None])[idx] if idx < len(bool_values or []) else None
            if val in ("true", "false", "all"):
                filters.setdefault(key, {})["mode"] = val

        for idx, id_obj in enumerate(min_ids or []):
            key = id_obj.get("key")
            if key not in selected:
                continue
            val = (min_values or [None])[idx] if idx < len(min_values or []) else None
            if val is not None and val != "":
                try:
                    filters.setdefault(key, {})["min"] = float(val)
                except Exception:
                    pass
            else:
                filters.setdefault(key, {})["min"] = None

        for idx, id_obj in enumerate(max_ids or []):
            key = id_obj.get("key")
            if key not in selected:
                continue
            val = (max_values or [None])[idx] if idx < len(max_values or []) else None
            if val is not None and val != "":
                try:
                    filters.setdefault(key, {})["max"] = float(val)
                except Exception:
                    pass
            else:
                filters.setdefault(key, {})["max"] = None

        for idx, id_obj in enumerate(string_ids or []):
            key = id_obj.get("key")
            if key not in selected:
                continue
            vals = (string_values or [None])[idx] if idx < len(string_values or []) else None
            if isinstance(vals, list):
                filters.setdefault(key, {})["values"] = vals

        return {k: v for k, v in filters.items() if k in selected}

    @app.callback(
        Output("config-keys-store", "data", allow_duplicate=True),
        Input({"type": "available-key", "key": ALL}, "n_clicks"),
        Input({"type": "remove-selected-key", "key": ALL}, "n_clicks"),
        Input({"type": "move-up", "key": ALL}, "n_clicks"),
        Input({"type": "move-down", "key": ALL}, "n_clicks"),
        State({"type": "available-key", "key": ALL}, "id"),
        State({"type": "remove-selected-key", "key": ALL}, "id"),
        State({"type": "move-up", "key": ALL}, "id"),
        State({"type": "move-down", "key": ALL}, "id"),
        State("config-keys-store", "data"),
        prevent_initial_call=True,
    )
    def move_keys(available_clicks, remove_clicks, up_clicks, down_clicks, available_ids, remove_ids, up_ids, down_ids, store):
        ctx = dash.callback_context
        if not ctx.triggered or store is None:
            return no_update

        store = store or {"available": [], "selected": []}
        available = list(store.get("available", []) or [])
        selected = list(store.get("selected", []) or [])

        triggered = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            trigger_id = json.loads(triggered)
        except Exception:
            return no_update

        try:
            triggered_value = ctx.triggered[0].get("value", None)
        except Exception:
            triggered_value = None
        if trigger_id.get("type") in {"available-key", "remove-selected-key", "move-up", "move-down"}:
            if not isinstance(triggered_value, int) or triggered_value <= 0:
                return no_update

        if trigger_id.get("type") == "available-key":
            key = trigger_id.get("key")
            if key in available:
                available.remove(key)
            if key not in selected:
                selected.append(key)
        elif trigger_id.get("type") == "remove-selected-key":
            key = trigger_id.get("key")
            if key in selected:
                selected.remove(key)
            if key not in available:
                available.append(key)
                available.sort()
        elif trigger_id.get("type") == "move-up":
            key = trigger_id.get("key")
            if key in selected:
                idx = selected.index(key)
                if idx > 0:
                    selected[idx - 1], selected[idx] = selected[idx], selected[idx - 1]
        elif trigger_id.get("type") == "move-down":
            key = trigger_id.get("key")
            if key in selected:
                idx = selected.index(key)
                if idx < len(selected) - 1:
                    selected[idx + 1], selected[idx] = selected[idx], selected[idx + 1]

        return {"available": available, "selected": selected}

    @app.callback(
        Output("config-keys-store", "data", allow_duplicate=True),
        Input("config-keys-toggle-all", "n_clicks"),
        State("config-keys-store", "data"),
        prevent_initial_call=True,
    )
    def toggle_all_config_keys(n_clicks, store):
        if not n_clicks:
            return no_update
        store = store or {"available": [], "selected": []}
        available = list(store.get("available", []) or [])
        selected = list(store.get("selected", []) or [])
        union_keys = list(available) + list(selected)
        if len(union_keys) == 0:
            return no_update
        if len(available) == 0 and len(selected) == len(union_keys):
            return {"available": sorted(union_keys), "selected": []}
        return {"available": [], "selected": union_keys}

