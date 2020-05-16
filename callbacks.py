from dash.dependencies import Input, Output
from layouts import home, page1, page2
from components.functions import update_datatable
from datetime import datetime
from datetime import date, timedelta

def register_callbacks(app):

    #### callback to switch page content
    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/home/':
            return home
        elif pathname == '/page1/':
            return page1
        elif pathname == '/page2/':
            return page2
        else:
            return None


    #### Date Picker Callback
    @app.callback(Output('descrip-date', 'children'),
                  [Input('stat-date-picker', 'start_date'),
                   Input('stat-date-picker', 'end_date')])
    def update_output(start_date, end_date):
        if start_date is not None:
            start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
            start_date_string = start_date.strftime('%B %d, %Y')
            string_prefix = 'Start Date: ' + start_date_string + '| '
        if end_date is not None:
            end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
            end_date_string = end_date.strftime('%B %d, %Y')
            days_selected = (end_date - start_date).days
            prior_start_date = start_date - timedelta(days_selected + 1)
            prior_start_date_string = datetime.strftime(prior_start_date, '%B %d, %Y')
            prior_end_date = end_date - timedelta(days_selected + 1)
            prior_end_date_string = datetime.strftime(prior_end_date, '%B %d, %Y')
            string_prefix = string_prefix + 'End Date: ' + end_date_string + '| Period Length: ' + str(
                days_selected + 1) + ' Days'
        if len(string_prefix) == len('You have selected: '):
            return 'Select a date to see it displayed here'
        else:
            return string_prefix

    #### Table Callback
    @app.callback(Output('stat-datatable', 'data'),
                  [Input('stat-date-picker', 'start_date'),
                   Input('stat-date-picker', 'end_date'),
                   Input('cat-dropdown', 'value'),
                   Input('acc-checklist', 'value')])
    def update_data_1(start_date, end_date, categories, accounts):
        data_1 = update_datatable(start_date, end_date, categories, accounts)
        return data_1