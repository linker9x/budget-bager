import dash_core_components as dcc
import dash_html_components as html
import dash_table
from components import header
from datetime import datetime as dt
from datetime import date, timedelta
import pandas as pd

df_pnc = pd.read_csv('./data/PNC_12M.csv')
df_chase = pd.read_csv('./data/Chase_12M.csv')
df = pd.concat([df_pnc, df_chase]).reset_index(drop=True).sort_values(by=['Date'])
df['Date'] = pd.to_datetime(df['Date'])

__fixed_cat = ['CAR', 'HEALTHCARE', 'FITNESS', 'PHONE']
__var_cat = ['AMAZON', 'TRAVEL', 'PERSONAL', 'SHOPPING', 'ENTERTAINMENT', 'CATS',
             'GROCERIES', 'RESTAURANT', 'GAS']

home = html.Div([header.Header(),
    html.H1('home')
])

page4 = html.Div([
    html.Div([
            # HEADER
            header.Header(),
            # PAGE NAME
            html.Div([
                html.H6(['Page4'], className="bb-header", style={'marginTop': 10})
            ])
    ]),
    # SELECTION/INPUTS
    html.Div([
        dcc.DatePickerRange(
          id='p4-date-picker',
          min_date_allowed=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
          max_date_allowed=df['Date'].max().to_pydatetime(),
          initial_visible_month=dt(df['Date'].max().to_pydatetime().year, df['Date'].max().to_pydatetime().month, 1),
          start_date=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
          end_date=df['Date'].max().to_pydatetime(),
        ),
        dcc.Dropdown(
            options=[
                {'label': '3 Month', 'value': '3'},
                {'label': '6 Month', 'value': '6'}
            ],
            value='3',
            clearable=False,
            id='p4-month-dropdown'
        )
    ]),
    # GRAPH(S)
    html.Div([
        html.Div([dcc.Graph(id='p4-time-forecast-plot',
                            clear_on_unhover=True)
                  ])
    ])
])


##########
# Category Overview Page
##########
page3 = html.Div([
    html.Div([
        # HEADER
        header.Header(),
        # PAGE NAME
        html.Div([
            html.H6(['Page3'], className="bb-header", style={'marginTop': 10})
        ]),
        html.Div([
            dcc.DatePickerRange(
              id='p3-date-picker',
              min_date_allowed=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
              max_date_allowed=df['Date'].max().to_pydatetime(),
              initial_visible_month=dt(df['Date'].max().to_pydatetime().year, df['Date'].max().to_pydatetime().month, 1),
              start_date=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
              end_date=df['Date'].max().to_pydatetime(),
            ),
            dcc.Dropdown(
                options=[
                    {'label': 'Mono', 'value': 'MONO'},
                    {'label': 'Multi', 'value': 'MULTI'}
                ],
                value='MULTI',
                clearable=False,
                id='p3-mode-dropdown'
            ),
            dcc.Dropdown(
                options=[{'label': '{}'.format(cat), 'value': cat} for cat in __fixed_cat + __var_cat],
                value=['AMAZON', 'GROCERIES'],
                multi=True,
                id='p3-cat-dropdown'
            )
        ]),
        # TOP DIV
        html.Div([dcc.Graph(id='p3-time-plot',
                            clear_on_unhover=True)]),
        html.Div([
            html.Div([dcc.Graph(id='p3-box-plot',
                                clear_on_unhover=True)]),
            html.Div([dcc.Graph(id='p3-bar-plot',
                                clear_on_unhover=True)])
        ])
    ]),
    html.Div([
        dash_table.DataTable(
                        id='p3-cat-datatable',
                        columns=[{"name": i, "id": i} for i in df.columns],
                        style_table={'maxWidth': '1500px'},
                        # editable=True,
                        # row_selectable="multi",
                        # selected_rows=[0],
                        )
    ])
])

##########
# Period Overview Page
##########
page2 = html.Div([
    html.Div([
        # HEADER
        header.Header(),
        # PAGE NAME
        html.Div([
            html.H6(['Page2'], className="bb-header", style={'marginTop': 10})
        ]),
        html.Div([
            dcc.DatePickerRange(
              id='p2-date-picker',
              min_date_allowed=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
              max_date_allowed=df['Date'].max().to_pydatetime(),
              initial_visible_month=dt(df['Date'].max().to_pydatetime().year, df['Date'].max().to_pydatetime().month, 1),
              start_date=dt(df['Date'].min().to_pydatetime().year, df['Date'].min().to_pydatetime().month, 1),
              end_date=df['Date'].max().to_pydatetime(),
            )
        ]),
        # TOP DIV
        html.Div([dcc.Graph(id='in-out-area-graph')]),
        # BOTTOM DIV
        html.Div([
            # Fixed + Var Graph
            html.Div([dcc.Graph(id='fixed-var-stacked')]),
            # Pie charts
            html.Div([dcc.Graph(id='fixed-pie'), dcc.Graph(id='var-pie')])
        ])
    ])
])


##########
# Statement Page
##########
page1 = html.Div([
    html.Div([
        # HEADER
        header.Header(),
        # PAGE NAME
        html.Div([
            html.H6(['Page1'], className="bb-header", style={'marginTop': 10})
        ]),
        html.Div(id='descrip-date'),
        # DATE/CAT PICKER
        html.Div([
            html.Div([
                dcc.DatePickerRange(
                  id='stat-date-picker',
                  min_date_allowed=df['Date'].min().to_pydatetime(),
                  max_date_allowed=df['Date'].max().to_pydatetime(),
                  initial_visible_month=dt(df['Date'].max().to_pydatetime().year, df['Date'].max().to_pydatetime().month, 1),
                  start_date=dt(df['Date'].max().to_pydatetime().year, df['Date'].max().to_pydatetime().month, 1),
                  end_date=df['Date'].max().to_pydatetime(),
                ),
                dcc.Dropdown(
                    options=[{'label': '{}'.format(cat), 'value': cat} for cat in df['Category'].unique()],
                    value=df['Category'].unique(),
                    multi=True,
                    id='cat-dropdown'
                )
            ]),
            html.Div(id='page1')
        ], className="row ", style={'marginTop': 10, 'marginBottom': 10}),
        # RADIO BUTTONS
        html.Div([
            dcc.Checklist(
                options=[{'label': '{}'.format(acc), 'value': acc} for acc in df['Source'].unique()],
                value=['PNC', 'Chase'],
                labelStyle={'display': 'inline-block', 'width': '30%', 'margin': 'auto', 'marginTop': 10, 'paddingLeft': 10},
                id='acc-checklist'
            )
        ]),
        # TABLE
        html.Div([
            dash_table.DataTable(
                id='stat-datatable',
                columns=[{"name": i, "id": i} for i in df.columns],
                # + [{"name": j, "id": j} for j in df.columns],
                style_table={'maxWidth': '1500px'},
                # editable=True,
                # row_selectable="multi",
                # selected_rows=[0],
                ),
        ], className=" twelve columns")
    ])
])