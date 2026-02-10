"""
Main layout for AltarExtractor application.
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from ..config import DEFAULT_DB_NAME


def build_layout():
    """Build and return the main application layout."""
    return dbc.Container(
        [
            # Stores
            dcc.Store(id="creds-store", storage_type="local"),
            dcc.Store(id="ui-store", storage_type="local"),
            dcc.Store(id="db-history", storage_type="local"),
            dcc.Store(id="runs-cache", storage_type="memory"),
            dcc.Store(id="config-keys-store", storage_type="local"),
            dcc.Store(id="filters-store", storage_type="local"),
            dcc.Store(id="metrics-store", storage_type="memory"),
            dcc.Store(id="metrics-values-store", storage_type="memory"),
            dcc.Store(id="metrics-selected-store", storage_type="local"),
            dcc.Store(id="experiments-random-store", storage_type="local"),
            dcc.Store(id="experiments-page-size-store", storage_type="local"),
            dcc.Store(id="metrics-page-size-store", storage_type="local"),
            dcc.Store(id="metrics-show-keys-store", storage_type="local"),
            dcc.Store(id="metrics-layout-mode-store", storage_type="local"),
            dcc.Store(id="results-store", storage_type="memory"),
            dcc.Interval(id="init-tick", interval=0, n_intervals=0, max_intervals=1),

            # Navbar
            dbc.Navbar(
                dbc.Container(
                    [
                        dbc.NavbarBrand("AltarExtractor", class_name="mb-0 h4 text-dark"),
                        dbc.Button("Database credentials", id="toggle-connection", color="link", class_name="mb-0 h5 p-0"),
                    ]
                ),
                color="light",
                sticky="top",
                class_name="mb-3",
            ),

            # Connection credentials panel
            dbc.Collapse(
                id="connection-collapse",
                is_open=True,
                children=dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.P("Enter your MongoDB credentials or a MongoDB URI."),
                                        # Connection mode switch
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.RadioItems(
                                                        options=[
                                                            {"label": "Use URI", "value": "uri"},
                                                            {"label": "Use Credentials", "value": "credentials"},
                                                        ],
                                                        value="credentials",
                                                        id="connection-mode-switch",
                                                        inline=True,
                                                    ),
                                                    md=12,
                                                ),
                                            ],
                                            class_name="mb-3",
                                        ),
                                        # URI mode fields
                                        html.Div(
                                            id="uri-mode-fields",
                                            children=[
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            dcc.Input(
                                                                id="uri-input",
                                                                placeholder="MongoDB URI (e.g. mongodb+srv://user:pass@cluster/db?authSource=admin)",
                                                                type="text",
                                                                value="",
                                                                style={"width": "100%"},
                                                            ),
                                                            width=12,
                                                        ),
                                                    ],
                                                    class_name="mb-2",
                                                ),
                                            ],
                                            style={"display": "none"},
                                        ),
                                        # Credentials mode fields
                                        html.Div(
                                            id="credentials-mode-fields",
                                            children=[
                                                dbc.Row(
                                                    [
                                                        dbc.Col(dcc.Input(id="host-input", placeholder="Host (default: localhost)", type="text", value="", style={"width": "100%"}), md=6),
                                                        dbc.Col(dcc.Input(id="port-input", placeholder="Port (default: 27017)", type="text", value="", style={"width": "100%"}), md=6),
                                                    ],
                                                    class_name="mb-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(dcc.Input(id="username-input", placeholder="Username (optional)", type="text", value="", style={"width": "100%"}), md=6),
                                                        dbc.Col(dcc.Input(id="password-input", placeholder="Password (optional)", type="password", value="", style={"width": "100%"}), md=6),
                                                    ],
                                                    class_name="mb-2",
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col(dcc.Input(id="authsource-input", placeholder="Auth source (default: database name)", type="text", value="", style={"width": "100%"}), md=12),
                                                    ],
                                                    class_name="mb-2",
                                                ),
                                            ],
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Checklist(
                                                        options=[
                                                            {"label": "Save credentials", "value": "save"},
                                                        ],
                                                        value=[],
                                                        id="save-options",
                                                        switch=True,
                                                    ),
                                                    md=12,
                                                ),
                                            ],
                                            class_name="mb-2",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(dbc.Button("Clear saved", id="clear-saved-button", color="link", n_clicks=0), width="auto"),
                                            ],
                                            class_name="g-2 align-items-center",
                                        ),
                                    ]
                                ),
                                class_name="mb-3",
                            ),
                            md=6,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([]),
                                class_name="mb-3",
                            ),
                            md=6,
                        ),
                    ],
                    class_name="g-2",
                ),
            ),

            # Database name + Connect button row
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Database"),
                            dbc.Input(id="db-name-input", placeholder=f"Database name (default: {DEFAULT_DB_NAME})", type="text", list="db-name-list"),
                            html.Datalist(id="db-name-list"),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Label(" "),
                            dbc.Button("Connect", id="connect-button", color="primary", n_clicks=0, class_name="d-block"),
                        ],
                        md=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Label(" "),
                            dbc.Alert(id="status-alert", is_open=False, color="light", class_name="mb-0"),
                        ],
                        md=6,
                    ),
                ],
                class_name="g-2 align-items-end mb-3",
            ),

            # Select Keys card
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.Span("Select Keys"),
                                html.I(className="ms-auto bi bi-chevron-down"),
                            ],
                            id="toggle-select-keys",
                            n_clicks=0,
                            className="d-flex align-items-center",
                            style={"cursor": "pointer", "fontSize": "1.25rem", "fontWeight": "600"},
                        )
                    ),
                    dbc.Collapse(
                        dbc.CardBody(
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Available config keys ([type] [distinct value counts])"),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Dropdown(
                                                            id="config-keys-select",
                                                            options=[],
                                                            value=[],
                                                            multi=True,
                                                            placeholder="Select config keys...",
                                                        ),
                                                        html.Div(id="config-keys-none-note", style={"color": "#666", "marginTop": "0.25rem", "marginBottom": "0.75rem"}),
                                                        dbc.Button("Check/Uncheck all", id="config-keys-toggle-all", size="sm", color="secondary", class_name="mb-2"),
                                                        dbc.ListGroup(id="available-keys", style={"display": "none"}),
                                                    ]
                                                ),
                                            ]
                                        ),
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            [
                                                dbc.CardHeader("Selected keys"),
                                                dbc.CardBody(dbc.ListGroup(id="selected-keys")),
                                            ]
                                        ),
                                        md=8,
                                    ),
                                ]
                            )
                        ),
                        id="select-keys-collapse",
                        is_open=True,
                    ),
                ],
                class_name="mb-3",
            ),

            # Experiments card
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.Span("Experiments"),
                                html.I(className="ms-auto bi bi-chevron-down"),
                            ],
                            id="toggle-experiments",
                            n_clicks=0,
                            className="d-flex align-items-center",
                            style={"cursor": "pointer", "fontSize": "1.25rem", "fontWeight": "600"},
                        )
                    ),
                    dbc.Collapse(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(dbc.Button("Check/Uncheck all results", id="results-toggle-all", size="sm", color="secondary"), width="auto"),
                                                dbc.Col(dcc.Dropdown(id="results-select", options=[], value=[], multi=True, placeholder="Select result keys...")),
                                            ],
                                            id="results-controls-row",
                                            class_name="g-2 mb-1 align-items-center",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Number of rows"),
                                                        dcc.Input(id="experiments-page-size-input", type="number", value=10, min=1, step=1, style={"width": "80px", "marginLeft": "8px"}),
                                                    ],
                                                    width="auto",
                                                ),
                                                dbc.Col(
                                                    dbc.Checklist(
                                                        options=[{"label": "Random order", "value": "random"}],
                                                        value=[],
                                                        id="experiments-random-check",
                                                        switch=True,
                                                    ),
                                                    width="auto",
                                                    class_name="ms-2",
                                                ),
                                            ],
                                            class_name="g-2 mb-1 align-items-center",
                                        ),
                                        html.Div(id="results-none-note", style={"color": "#666", "marginTop": "0.25rem", "marginBottom": "0.25rem"}),
                                    ]
                                ),
                                dash_table.DataTable(
                                    id="experiments-table",
                                    columns=[{"name": "Experiment", "id": "experiment"}],
                                    data=[],
                                    page_size=20,
                                    style_table={"overflowX": "auto", "width": "100%"},
                                    style_cell={"textAlign": "left", "padding": "8px"},
                                    style_header={"fontWeight": "bold"},
                                ),
                                html.Div(
                                    [
                                        dbc.Button("Open in Pygwalker", id="open-pygwalker-exp-btn", color="primary", class_name="mt-2 me-2"),
                                        dbc.Button("Download dataset", id="download-exp-open", color="secondary", class_name="mt-2"),
                                    ]
                                ),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader("Open in Pygwalker"),
                                        dbc.ModalBody(
                                            html.Div(
                                                [
                                                    html.P("Choose which columns to include:"),
                                                    dbc.Button("All keys", id="open-exp-all-keys", color="primary", class_name="me-2"),
                                                    dbc.Button("Only selected keys", id="open-exp-selected-keys", color="secondary"),
                                                ]
                                            )
                                        ),
                                    ],
                                    id="open-exp-modal",
                                    is_open=False,
                                ),
                                dbc.Modal(
                                    [
                                        dbc.ModalHeader("Download CSV"),
                                        dbc.ModalBody(
                                            dbc.Input(id="download-exp-filename", type="text", placeholder="experiments.csv", value="experiments.csv")
                                        ),
                                        dbc.ModalFooter(
                                            [
                                                dbc.Button("Cancel", id="download-exp-cancel", class_name="me-2"),
                                                dbc.Button("Download", id="download-exp-confirm", color="primary"),
                                            ]
                                        ),
                                    ],
                                    id="download-exp-modal",
                                    is_open=False,
                                ),
                                dcc.Download(id="download-exp-csv"),
                            ]
                        ),
                        id="experiments-collapse",
                        is_open=True,
                    ),
                ],
                class_name="mb-3",
            ),

            # Metrics card
            dbc.Card(
                [
                    dbc.CardHeader(
                        html.Div(
                            [
                                html.Span("Metrics"),
                                html.I(className="ms-auto bi bi-chevron-down"),
                            ],
                            id="toggle-metrics",
                            n_clicks=0,
                            className="d-flex align-items-center",
                            style={"cursor": "pointer", "fontSize": "1.25rem", "fontWeight": "600"},
                        )
                    ),
                    dbc.Collapse(
                        dbc.CardBody(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(dbc.Button("Check/Uncheck all metrics", id="metrics-toggle-all", size="sm", color="secondary"), width="auto"),
                                                dbc.Col(dcc.Dropdown(id="metrics-select", options=[], value=[], multi=True, placeholder="Select metrics...")),
                                            ],
                                            id="metrics-controls-row",
                                            class_name="g-2 align-items-center",
                                        ),
                                        html.Div(id="metrics-none-note", style={"color": "#666", "marginTop": "0.5rem"}),
                                    ]
                                ),
                                html.Div(
                                    [
                                        html.Hr(),
                                        html.Div("Per-step metrics table", style={"fontWeight": "600", "marginBottom": "0.5rem"}),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label("Number of rows"),
                                                        dcc.Input(id="metrics-page-size-input", type="number", value=10, min=1, step=1, style={"width": "80px", "marginLeft": "8px"}),
                                                    ],
                                                    width="auto",
                                                ),
                                                dbc.Col(
                                                    dbc.Checklist(
                                                        options=[{"label": "Show selected keys", "value": "show"}],
                                                        value=["show"],
                                                        id="metrics-show-keys-switch",
                                                        switch=True,
                                                    ),
                                                    width="auto",
                                                    class_name="ms-3",
                                                ),
                                                dbc.Col(
                                                    dbc.RadioItems(
                                                        options=[
                                                            {"label": "Steps as rows", "value": "rows"},
                                                            {"label": "Steps as columns", "value": "cols"},
                                                        ],
                                                        value="rows",
                                                        id="metrics-layout-mode",
                                                        inline=True,
                                                    ),
                                                    width="auto",
                                                    class_name="ms-3",
                                                ),
                                            ],
                                            class_name="g-2 align-items-center mb-2",
                                        ),
                                        dash_table.DataTable(
                                            id="metrics-steps-table",
                                            columns=[{"name": "Experiment", "id": "experiment"}],
                                            data=[],
                                            page_size=20,
                                            style_table={"overflowX": "auto", "width": "100%"},
                                            style_cell={"textAlign": "left", "padding": "8px"},
                                            style_header={"fontWeight": "bold"},
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button("Open in Pygwalker", id="open-pygwalker-btn", color="primary", class_name="mt-2 me-2"),
                                                dbc.Button("Download dataset", id="download-steps-open", color="secondary", class_name="mt-2"),
                                            ]
                                        ),
                                        dbc.Modal(
                                            [
                                                dbc.ModalHeader("Open in Pygwalker"),
                                                dbc.ModalBody(
                                                    html.Div(
                                                        [
                                                            html.P("Choose which columns to include:"),
                                                            dbc.Button("All keys", id="open-steps-all-keys", color="primary", class_name="me-2"),
                                                            dbc.Button("Only selected keys", id="open-steps-selected-keys", color="secondary"),
                                                        ]
                                                    )
                                                ),
                                            ],
                                            id="open-steps-modal",
                                            is_open=False,
                                        ),
                                        dbc.Modal(
                                            [
                                                dbc.ModalHeader("Download CSV"),
                                                dbc.ModalBody(
                                                    dbc.Input(id="download-steps-filename", type="text", placeholder="metrics_steps.csv", value="metrics_steps.csv")
                                                ),
                                                dbc.ModalFooter(
                                                    [
                                                        dbc.Button("Cancel", id="download-steps-cancel", class_name="me-2"),
                                                        dbc.Button("Download", id="download-steps-confirm", color="primary"),
                                                    ]
                                                ),
                                            ],
                                            id="download-steps-modal",
                                            is_open=False,
                                        ),
                                        dcc.Download(id="download-steps-csv"),
                                        dcc.Store(id="pygwalker-url"),
                                        html.Div(id="pygwalker-open-dummy", style={"display": "none"}),
                                    ],
                                    id="metrics-per-step-section",
                                ),
                            ]
                        ),
                        id="metrics-collapse",
                        is_open=True,
                    ),
                ],
                class_name="mb-3",
            ),
        ],
        fluid=True,
    )

