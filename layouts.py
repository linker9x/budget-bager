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
print(df)

home = html.Div([header.Header(),
    html.H1('home')
])

page2 = html.Div([header.Header(),
    html.H1('page2')
])

page1 = html.Div([
    html.Div([
        # HEADER
        header.Header(),
        # PAGE NAME
        html.Div([
            html.H6(['Page1'], className="bb-header", style={'marginTop': 10})
        ]),
        html.Div(id='descrip-date'),
        # DATE PICKER
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
        ], className=" twelve columns"),
        #GRAPH?
        html.Div([
            html.Div([
                dcc.Graph(id='paid-search')
              ], className=" twelve columns")
        ], className="row ")
    ])
])
