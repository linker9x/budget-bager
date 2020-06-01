import os
import sys
from datetime import date, datetime, timedelta, time
sys.path.append(os.path.abspath(os.path.join('..')))
sys.path.append(os.path.abspath(os.path.join('.')))

import pandas as pd
import numpy as np

from models.accounts.checking_account import PNCAccount

if __name__ == "__main__":
    acc = PNCAccount('./exp_data/PNC', '2020-01-01', '2020-04-30')
    print(acc)
    print(acc.balance_log)
    print(acc.card_payments)

