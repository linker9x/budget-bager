import pandas as pd


class Forecast:
    def __init__(self):
        self.budget = pd.read_csv()
        self.statements = []
        self.length = 6
        self.forecast = pd.DataFrame()