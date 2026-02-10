"""
Connection-related callbacks for AltarExtractor.
"""

from typing import Dict
from dash import Input, Output, State, no_update
import dash
import pymongo

from ..config import DEFAULT_DB_NAME
from ..services.mongo import (
    build_mongodb_uri,
    fetch_config_keys,
    fetch_runs_docs,
    fetch_metrics_values_map,
)
from ..services.data import collect_metric_ids_from_runs


def register_connection_callbacks(app):
    """Register all connection-related callbacks."""

    @app.callback(
        Output("status-alert", "children"),
        Output("status-alert", "color"),
        Output("status-alert", "is_open"),
        Output("runs-cache", "data"),
        Output("config-keys-store", "data"),
        Output("metrics-store", "data"),
        Output("metrics-values-store", "data"),
        Output("results-store", "data"),
        Input("connect-button", "n_clicks"),
        Input("init-tick", "n_intervals"),
        State("uri-input", "value"),
        State("host-input", "value"),
        State("port-input", "value"),
        State("username-input", "value"),
        State("password-input", "value"),
        State("authsource-input", "value"),
        State("db-name-input", "value"),
        State("creds-store", "data"),
        State("db-history", "data"),
        State("config-keys-store", "data"),
        State("connection-mode-switch", "value"),
        prevent_initial_call=False,
    )
    def on_connect_click(
        n_clicks: int,
        n_intervals: int,
        uri_value: str,
        host_value: str,
        port_value: str,
        username_value: str,
        password_value: str,
        auth_source_value: str,
        db_name_value: str,
        saved_creds,
        db_history,
        existing_config_store,
        connection_mode: str,
    ):
        ctx = dash.callback_context
        triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

        if triggered is None:
            return "Connecting...", "light", True, no_update, no_update, no_update, no_update, no_update

        auto_triggered = (triggered == "init-tick")

        # Resolve DB name
        resolved_db_name = (db_name_value or "").strip()
        if not resolved_db_name:
            saved_db_name = ""
            try:
                saved_db_name = ((saved_creds or {}).get("db_name") or "").strip() if isinstance(saved_creds, dict) else ""
            except Exception:
                saved_db_name = ""
            if saved_db_name:
                resolved_db_name = saved_db_name
            elif db_history and isinstance(db_history, list) and len(db_history) > 0:
                resolved_db_name = db_history[0]
            else:
                resolved_db_name = DEFAULT_DB_NAME

        # Determine connection mode
        resolved_mode = connection_mode or "credentials"
        if auto_triggered and saved_creds and isinstance(saved_creds, dict):
            resolved_mode = saved_creds.get("connection_mode", resolved_mode)

        # Resolve credentials
        if auto_triggered and saved_creds:
            uri_from_user = (saved_creds or {}).get("uri") or uri_value
            host = (saved_creds or {}).get("host") or host_value
            port = (saved_creds or {}).get("port") or port_value
            username = (saved_creds or {}).get("username") or username_value
            password = (saved_creds or {}).get("password") or password_value
            auth_source = (saved_creds or {}).get("authSource") or auth_source_value
        else:
            uri_from_user = uri_value
            host = host_value
            port = port_value
            username = username_value
            password = password_value
            auth_source = auth_source_value

        # Apply connection mode
        if resolved_mode == "uri":
            host = None
            port = None
            username = None
            password = None
            auth_source = None
        else:
            uri_from_user = None

        # Build URI and connect
        uri = build_mongodb_uri(
            uri_from_user=uri_from_user,
            host=host,
            port=port,
            username=username,
            password=password,
            database_name=resolved_db_name,
            auth_source=auth_source,
        )
        try:
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
        except Exception as exc:
            return f"Connection failed: {exc}", "danger", True, no_update, no_update, no_update, no_update, no_update

        # Fetch data
        try:
            keys = fetch_config_keys(client, resolved_db_name)
            runs = fetch_runs_docs(client, resolved_db_name)

            # Compute metric names
            metric_names = set()
            for r in runs:
                m = r.get("metrics", None)
                if isinstance(m, dict):
                    for k in m.keys():
                        if isinstance(k, str) and k.strip():
                            metric_names.add(k)
                elif isinstance(m, list):
                    for item in m:
                        if isinstance(item, dict):
                            nm = item.get("name")
                            if isinstance(nm, str) and nm.strip():
                                metric_names.add(nm)

            metrics = sorted(metric_names)
            metric_ids = collect_metric_ids_from_runs(runs)
            metrics_values_map = fetch_metrics_values_map(client, resolved_db_name, metric_ids)

            # Result keys
            result_keys = set()
            for r in runs:
                res = r.get("result", None)
                if isinstance(res, dict):
                    for k in res.keys():
                        if isinstance(k, str) and k.strip():
                            result_keys.add(k)
            results_keys_sorted = sorted(result_keys)

            count = len(runs)
            status_text = f"Connected. Database '{resolved_db_name}' has {count} run(s)."

            # Preserve selected keys
            existing_selected = []
            if existing_config_store and isinstance(existing_config_store, dict):
                existing_selected = list(existing_config_store.get("selected", []) or [])
            merged_selected = [k for k in existing_selected if k in set(keys)]
            config_store = {"available": keys, "selected": merged_selected}

            return status_text, "success", True, runs, config_store, metrics, metrics_values_map, results_keys_sorted
        except Exception as exc:
            return f"Connected, but failed to query runs/config keys: {exc}", "danger", True, no_update, no_update, no_update, no_update, no_update

    @app.callback(
        Output("creds-store", "data"),
        Input("connect-button", "n_clicks"),
        Input("clear-saved-button", "n_clicks"),
        State("uri-input", "value"),
        State("host-input", "value"),
        State("port-input", "value"),
        State("username-input", "value"),
        State("password-input", "value"),
        State("authsource-input", "value"),
        State("db-name-input", "value"),
        State("save-options", "value"),
        State("connection-mode-switch", "value"),
        prevent_initial_call=True,
    )
    def update_saved_credentials(
        connect_clicks,
        clear_clicks,
        uri_value,
        host_value,
        port_value,
        username_value,
        password_value,
        auth_source_value,
        db_name_value,
        save_options,
        connection_mode,
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return no_update
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "clear-saved-button":
            return {}

        save_enabled = "save" in (save_options or [])
        if not save_enabled:
            return no_update

        return {
            "uri": (uri_value or ""),
            "host": (host_value or ""),
            "port": (port_value or ""),
            "username": (username_value or ""),
            "password": (password_value or ""),
            "authSource": (auth_source_value or ""),
            "db_name": (db_name_value or ""),
            "connection_mode": (connection_mode or "credentials"),
        }

    @app.callback(
        Output("uri-input", "value"),
        Output("host-input", "value"),
        Output("port-input", "value"),
        Output("username-input", "value"),
        Output("password-input", "value"),
        Output("authsource-input", "value"),
        Output("save-options", "value"),
        Input("creds-store", "data"),
    )
    def populate_inputs_from_saved(data):
        if not data:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update

        save_values = ["save"] if any([
            data.get("uri"), data.get("host"), data.get("port"),
            data.get("username"), data.get("db_name"), data.get("password")
        ]) else []

        return (
            data.get("uri", ""),
            data.get("host", ""),
            data.get("port", ""),
            data.get("username", ""),
            data.get("password", ""),
            data.get("authSource", ""),
            save_values,
        )

    @app.callback(
        Output("uri-mode-fields", "style"),
        Output("credentials-mode-fields", "style"),
        Input("connection-mode-switch", "value"),
    )
    def toggle_connection_mode_fields(mode):
        if mode == "uri":
            return {}, {"display": "none"}
        else:
            return {"display": "none"}, {}

    @app.callback(
        Output("connection-mode-switch", "value"),
        Input("creds-store", "data"),
        prevent_initial_call=False,
    )
    def restore_connection_mode(creds_data):
        if not creds_data or not isinstance(creds_data, dict):
            return "credentials"
        saved_mode = creds_data.get("connection_mode", "credentials")
        return saved_mode if saved_mode in ("uri", "credentials") else "credentials"

    @app.callback(
        Output("db-history", "data"),
        Input("connect-button", "n_clicks"),
        State("db-name-input", "value"),
        State("db-history", "data"),
        prevent_initial_call=True,
    )
    def update_db_history(n_clicks, db_name, db_history):
        if not db_name:
            return no_update
        history = db_history or []
        if db_name in history:
            return history
        return ([db_name] + history)[:20]

    @app.callback(
        Output("db-name-list", "children"),
        Input("db-history", "data"),
    )
    def render_db_datalist(db_history):
        from dash import html
        options = db_history or []
        return [html.Option(value=opt) for opt in options]

    @app.callback(
        Output("db-name-input", "value"),
        Input("db-history", "data"),
        Input("creds-store", "data"),
        State("db-name-input", "value"),
        prevent_initial_call=False,
    )
    def set_db_name_from_history(db_history, creds_data, current_value):
        if current_value:
            return no_update
        saved_db = (creds_data or {}).get("db_name") if isinstance(creds_data, dict) else None
        if isinstance(saved_db, str) and saved_db.strip():
            return saved_db
        if db_history and isinstance(db_history, list) and len(db_history) > 0:
            return db_history[0]
        return no_update

