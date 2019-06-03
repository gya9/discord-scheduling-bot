import pandas as pd
import datetime as dt
from pytz import timezone

now_HM = dt.datetime.now(timezone('Asia/Tokyo')).strftime('%H:%M')

print(now_HM)
print(len(now_HM))