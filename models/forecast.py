import pandas as pd


class Forecast:
    def __init__(self, length=3):
        self.budget = pd.read_csv()
        self.statements = []
        self.length = length
        self.forecast = pd.DataFrame()