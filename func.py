import re, requests, json
import numpy as np
import pandas as pd
from keys import token_str, steamapi_key_str, gya9_id

def add_id(self,message):
    try:
        df = pd.read_csv('users.csv', index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['discord_id', ''])

    searchid = np.int64(message.author.id)

    if searchid in df.loc[:,'discord_id'].values:
        msg = 'すでに登録されています'

    else:
        tmp_se = pd.Series([searchid], index=df.columns)
        df = df.append(tmp_se, ignore_index=True)

        msg = '登録しました'

    df.to_csv('users.csv')

    return msg

def notification(self):
    try:
        df = pd.read_csv('users.csv', index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['discord_id'])

    return df.loc[:, 'discord_id'].values