"""
UI toggle and display callbacks for AltarExtractor.
"""

from dash import Input, Output, State, no_update


def register_ui_callbacks(app):
    """Register UI-related callbacks for panel toggles and display."""

    @app.callback(
        Output("connection-collapse", "is_open"),
        Output("ui-store", "data"),
        Input("toggle-connection", "n_clicks"),
        State("connection-collapse", "is_open"),
        State("ui-store", "data"),
    )
    def toggle_connection_panel(n_clicks, is_open, ui_data):
        stored_open = True if not ui_data else bool(ui_data.get("connection_open", True))
        if n_clicks is None:
            return stored_open, {"connection_open": stored_open}
        new_state = not is_open
        return new_state, {"connection_open": new_state}

    @app.callback(
        Output("connection-collapse", "is_open", allow_duplicate=True),
        Input("ui-store", "data"),
        prevent_initial_call=True,
    )
    def apply_saved_ui_state(ui_data):
        if not ui_data:
            return no_update
        return bool(ui_data.get("connection_open", True))

    @app.callback(
        Output("select-keys-collapse", "is_open"),
        Input("toggle-select-keys", "n_clicks"),
        State("select-keys-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_select_keys(n_clicks, is_open):
        if not n_clicks:
            return no_update
        return not is_open

    @app.callback(
        Output("experiments-collapse", "is_open"),
        Input("toggle-experiments", "n_clicks"),
        State("experiments-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_experiments(n_clicks, is_open):
        if not n_clicks:
            return no_update
        return not is_open

    @app.callback(
        Output("metrics-collapse", "is_open"),
        Input("toggle-metrics", "n_clicks"),
        State("metrics-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_metrics(n_clicks, is_open):
        if not n_clicks:
            return no_update
        return not is_open

    @app.callback(
        Output("metrics-per-step-section", "style"),
        Input("metrics-select", "options"),
    )
    def toggle_metrics_section(options):
        has_metrics = isinstance(options, list) and len(options) > 0
        return {} if has_metrics else {"display": "none"}

