import sys, discord, requests, json, traceback, time, asyncio
import numpy as np
import pandas as pd
import datetime as dt
from pytz import timezone
from keys import token_str, steamapi_key_str, gya9_id, id_98i4, id_bot_channel

class MyClient(discord.Client):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def sendbotchannel(self, msg):
        '''bot用チャンネルに書き込む'''
        bot_channel = self.get_channel(id_bot_channel)
        await bot_channel.send(msg)

    async def send2developer(self, msg):
        '''開発者にDMを送る'''
        developer = self.get_user(gya9_id)
        dm = await developer.create_dm()
        await dm.send(msg)

    async def send2user(self, user_id, msg):
        try:
            tmp_user = self.get_user(user_id)
            dm = await tmp_user.create_dm()
            await dm.send(msg)
        except Exception:
            await self.send2developer(traceback.format_exc())

    async def on_ready(self):
        msg = f'Logged on as {self.user}!'
        await self.send2developer(msg)


    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():

            dt_now = dt.datetime.now(timezone('Asia/Tokyo')).strftime('%H:%M')

            if dt_now == '00:00':
                df = pd.read_csv('users.csv', index_col=0)
                df.loc[:,'message'] = ''
                df.to_csv('users.csv')

                m = '@everyone 今日の予定の記入をお願いします！\r\nこのBOTにリプライすると予定を登録できます'
                await self.sendbotchannel(m)

            elif dt_now == '22:00':

                m = '@everyone るーそるの余命(23:30)が近いので、そろそろやりましょう！'
                await self.sendbotchannel(m)

            elif dt_now[3:] == '00' and int(dt_now[:2]) >= 12:

                nomessage_list = []

                df = pd.read_csv('users.csv', index_col=0)
                df_ok = pd.read_csv('users.csv', index_col=0).dropna()
                df_notyet = df[df.isnull().any(axis=1)]

                m = ""
                for i in range(len(df_ok)):
                    user_id = df_ok.iloc[i,0]
                    user_message = df_ok.iloc[i,1]
                    m += '【' + self.get_user(user_id).name + '】\r\n'
                    m += user_message + '\r\n\r\n'
                await self.sendbotchannel(m)


                for i in range(len(df_notyet)):
                    user_id = df_notyet.iloc[i,0]
                    nomessage_list.append(user_id)

                if nomessage_list != []:
                    msg = ""
                    for user_id in nomessage_list:
                        msg += '<@{}> '.format(user_id)
                    msg += '\r\n今日の予定が未記入です！\r\nこのBOTにリプライすると予定を登録できます'

                    await self.sendbotchannel(msg)

            await asyncio.sleep(60) # task runs every 60 seconds

    async def on_message(self, message):
        """ メッセージ受信時のイベントハンドラ """
        try:
            if message.author.id == self.user.id:
                return

            if message.content.startswith("おはよう"):
                m = "おはようございます、" + message.author.name + "さん！"
                await message.channel.send(m)

            if message.content.startswith("おやすみ"):
                m = "おやすみなさい、" + message.author.name + "さん！"
                await message.channel.send(m)

            if message.content.startswith('!check'):
                df = pd.read_csv('users.csv', index_col=0).dropna()

                m = ""
                for i in range(len(df)):
                    user_id = df.iloc[i,0]
                    user_message = df.iloc[i,1]
                    m += '【' + self.get_user(user_id).name + '】\r\n'
                    m += user_message + '\r\n\r\n'

                if m == "":
                    m = 'まだ誰も入力していません'

                await self.sendbotchannel(m)

            if message.content.startswith('!bye'):
                m = ':wave:'
                await message.channel.send(m)
                await self.close()

            if str(self.user.id) in message.content: 
                df = pd.read_csv('users.csv', index_col=0)
                df.loc[df['discord_id'] == message.author.id, 'message'] = message.content[22:]
                df.to_csv('users.csv')

                m = "<@{}> さんの情報を更新しました。".format(message.author.id)
                await self.sendbotchannel(m)

        except Exception: # エラー発生時にはトレースバックがDMで送られてくる
            await self.send2developer(traceback.format_exc())

client = MyClient()
client.run(token_str)