import os
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime, timedelta
from dateutil.relativedelta import *


def Header():
    return html.Div([
        # get_logo(),
        get_header(),
        html.Br([]),
        get_menu(),
        get_period_picker()
    ])


def get_logo():
    logo = html.Div([

        html.Div([
            html.Img(src='https://i.pinimg.com/564x/4a/bc/38/4abc38758eba60d6712bd86dd1542697.jpg', height='10', width='20')
        ], className="ten columns padded"),

        # html.Div([
        #     dcc.Link('Full View   ', href='/cc-travel-report/full-view')
        # ], className="two columns page-view no-print")

    ], className="row gs-header")
    return logo


def get_header():
    header = html.Div([

        html.Div([
            html.H5(
                'Budget Badger')
        ], className="twelve columns padded")

    ], className="row gs-header gs-text-header")
    return header


def get_menu():
    menu = html.Div([
        dcc.Link('|Home   |', href='/home/', className="tab first"),
        dcc.Link('P1 - Table   |', href='/page1/', className="tab"),
        dcc.Link('P2 - Period   |', href='/page2/', className="tab"),
        dcc.Link('P3 - Category   |', href='/page3/', className="tab"),
        dcc.Link('P4 - Forecast   |', href='/page4/', className="tab")

    ], className="row ")
    return menu


def get_period_picker():
    dates = os.listdir('./exp_data/PNC/statements/')
    dates = [date.replace('.csv', '') for date in dates]
    start_dates = [datetime.strptime(date, '%m_%Y').date() for date in dates]
    end_dates = [date + relativedelta(months=+1, day=1) - timedelta(days=1) for date in start_dates]
    start_dates.sort(reverse=True)
    end_dates.sort(reverse=True)

    print(end_dates)
    period_picker = html.Div([
        html.Div([
            html.Div([
                html.H6('Start',
                        style={'margin-right': '1em'})
            ], style=dict(
                    width='14%',
                    display='inline-block',
                    verticalAlign='middle')),
            dcc.Dropdown(
                options=[{'label': '{}'.format(date), 'value': date} for date in start_dates],
                value=start_dates[-1],
                multi=False,
                id='per-picker-dd1',
                style=dict(
                    width='84%',
                    display='inline-block',
                    verticalAlign='middle')
            )
        ], style=dict(
                    width='49%',
                    display='inline-block',
                    verticalAlign='middle')),
        html.Div([
            html.Div([
                html.H6('End',
                        style={'margin-right': '1em'})
            ], style=dict(
                    width='14%',
                    display='inline-block',
                    verticalAlign='middle')),
            dcc.Dropdown(
                options=[{'label': '{}'.format(date), 'value': date} for date in end_dates],
                value=end_dates[0],
                multi=False,
                id='per-picker-dd2',
                style=dict(
                    width='84%',
                    display='inline-block',
                    verticalAlign='middle')
            )
        ], style=dict(
                    width='49%',
                    display='inline-block',
                    verticalAlign='middle'))
    ], style=dict(display='flex'))
    return period_picker