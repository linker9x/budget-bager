import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from models.forecast import Forecast
from models.accountviews import AccountViews

# from app import server
from app import app
from callbacks import register_callbacks

# This is just here to change the icon and the title
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>HEAD</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div>FOOTER</div>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# # # # # # # # #
# Models
# # # # # # # # #
av = AccountViews('2020-01-01', '2020-06-30')
fc = Forecast(av, length=3)

# # # # # # # # #
# Callbacks
# # # # # # # # #
register_callbacks(app, av, fc)

# # # # # # # # #
# external_css = ["https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
#                 "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
#                 "//fonts.googleapis.com/css?family=Raleway:400,300,600",
#                 "https://codepen.io/bcd/pen/KQrXdb.css",
#                 "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
#                 "https://codepen.io/dmcomfort/pen/JzdzEZ.css"]
#
# for css in external_css:
#     app.css.append_css({"external_url": css})

# external_js = ["https://code.jquery.com/jquery-3.2.1.min.js",
#                "https://codepen.io/bcd/pen/YaXojL.js"]
#
# for js in external_js:
#     app.scripts.append_script({"external_url": js})

if __name__ == '__main__':
    app.run_server(debug=True)
