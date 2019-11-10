import sys, discord, requests, json, traceback, time, asyncio, os
import numpy as np
import pandas as pd
import datetime as dt
from pytz import timezone
from keys import token_str, steamapi_key_str, dev_id, id_bot_channel, modes, dotw

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        # self.bg_task = self.loop.create_task(self.my_background_task())

    async def sendbotchannel(self, msg):
        '''bot用チャンネルに書き込む'''
        bot_channel = self.get_channel(id_bot_channel)
        await bot_channel.send(msg)

    async def send2developer(self, msg):
        '''開発者にDMを送る'''
        developer = self.get_user(dev_id)
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

    # async def my_background_task(self):
    #     await self.wait_until_ready()
    #     while not self.is_closed():

    #         dt_now = dt.datetime.now(timezone('Asia/Tokyo')).strftime('%H:%M')
    #         wd = dt.datetime.now(timezone('Asia/Tokyo')).weekday()

            # if dt_now == '00:00':
            #     df = pd.read_csv('users_test.csv', index_col=0)

            #     delete_wd = wd - 1
            #     if delete_wd == -1:
            #         delete_wd = 6

            #     df.loc[:,'message_{}'.format(delete_wd)] = ''
            #     df.to_csv('users_test.csv')

            #     m = '@everyone 今日の予定の記入をお願いします！\r\nこのBOTにリプライすると予定を登録できます'
            #     await self.sendbotchannel(m)

            # elif dt_now == '22:00':

            #     m = '@everyone るーそるの余命(23:30)が近いので、そろそろやりましょう！'
            #     await self.sendbotchannel(m)

            # elif dt_now[3:] == '00' and int(dt_now[:2]) >= 12:
            #     '''毎時0分に書き込まれた予定を表示し、まだ書いていない人に通知'''

            #     nomessage_list = []

            #     df = pd.read_csv('users_test.csv', index_col=0)
            #     df = df.iloc[:,[0,wd+1]]
            #     df_ok = df.dropna()
            #     df_notyet = df[df.isnull().any(axis=1)]

            #     m = ""
            #     for i in range(len(df_ok)):
            #         user_id = df_ok.iloc[i,0]
            #         user_message = df_ok.iloc[i,1]
            #         if user_message.startswith('\n'):
            #             user_message = user_message[1:]
            #         m += '【' + self.get_user(user_id).name + '】\r\n'
            #         m += user_message + '\r\n\r\n'
            #     if m != "":
            #         await self.sendbotchannel(m)


            #     for i in range(len(df_notyet)):
            #         user_id = df_notyet.iloc[i,0]
            #         nomessage_list.append(user_id)

            #     if nomessage_list != []:
            #         msg = ""
            #         for user_id in nomessage_list:
            #             msg += '<@{}> '.format(user_id)
            #         msg += '\r\n今日の予定が未記入です！\r\nこのBOTにリプライすると予定を登録できます'

            #         await self.sendbotchannel(msg)

            # await asyncio.sleep(60) # task runs every 60 seconds

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

            if message.content.startswith('!today'):
                wd = dt.datetime.now(timezone('Asia/Tokyo')).weekday()
                df = pd.read_csv('users_test.csv', index_col=0).iloc[:,[0,wd+1]].dropna()

                m = ""
                for i in range(len(df)):
                    user_id = df.iloc[i,0]
                    user_message = df.iloc[i,1]
                    if user_message.startswith('\n'):
                        user_message = user_message[1:]
                    m += '【' + self.get_user(user_id).name + '】\r\n'
                    m += user_message + '\r\n\r\n'

                if m == "":
                    m = 'まだ誰も入力していません'

                await self.sendbotchannel(m)

            if message.content.startswith('!asita') or message.content.startswith('!ashita') or message.content.startswith('!tommorow'):
                wd = dt.datetime.now(timezone('Asia/Tokyo')).weekday()
                wd = (wd+1)%7
                df = pd.read_csv('users_test.csv', index_col=0).iloc[:,[0,wd+1]].dropna()

                m = ""
                for i in range(len(df)):
                    user_id = df.iloc[i,0]
                    user_message = df.iloc[i,1]
                    if user_message.startswith('\n'):
                        user_message = user_message[1:]
                    m += '【' + self.get_user(user_id).name + '】\r\n'
                    m += user_message + '\r\n\r\n'

                if m == "":
                    m = 'まだ誰も入力していません'

                await self.sendbotchannel(m)

            if message.content.startswith('!week'):
                '''一週間分の記入されたスケジュールを表示'''
                today = dt.datetime.now(timezone('Asia/Tokyo'))
                wd_today = today.weekday()
                df = pd.read_csv('users_test.csv', index_col=0)

                m = ""

                for i in range(7):
                    wd = (wd_today+i)%7
                    target_day = today + dt.timedelta(days=i)
                    strdt = target_day.strftime("%m/%d")
                    m_wd = '**---' + strdt + '(' + dotw[wd] + ')' + '---**\r\n'
                    df_wd = df.iloc[:,[0,wd+1]].dropna()

                    for i in range(len(df_wd)):
                        user_id = df_wd.iloc[i,0]
                        user_message = df_wd.iloc[i,1]
                        if user_message.startswith('\n'):
                            user_message = user_message[1:]
                        m_wd += '【' + self.get_user(user_id).name + '】\r\n'
                        m_wd += user_message + '\r\n\r\n'

                    m += m_wd
                
                await self.sendbotchannel(m)

            if message.content.startswith('<@{}>'.format(self.user.id)):
                '''botにリプライされたメッセージを予定としてDBに保存'''

                df = pd.read_csv('users_test.csv', index_col=0)
                con = message.content[22:].lstrip()

                if con[0:2] == '明日':
                    '''メッセージ冒頭に「明日」とあるときの処理'''
                    wd = dt.datetime.now(timezone('Asia/Tokyo')).weekday()
                    wd = (wd+1)%7

                    df.loc[df['discord_id'] == message.author.id, 'message_{}'.format(wd)] = con[2:].lstrip()
                    df.to_csv('users_test.csv')

                    m = "<@{}> さんの情報を更新しました。".format(message.author.id)
                    await self.sendbotchannel(m)

                elif con[0] not in dotw:
                    '''メッセージ冒頭に曜日が含まれていない時の処理
                       当日のスケジュールを記入したものとして扱う'''

                    wd = dt.datetime.now(timezone('Asia/Tokyo')).weekday()
                    df.loc[df['discord_id'] == message.author.id, 'message_{}'.format(wd)] = con.lstrip()
                    df.to_csv('users_test.csv')

                    m = "<@{}> さんの情報を更新しました。".format(message.author.id)
                    await self.sendbotchannel(m)

                elif con[0] in dotw:
                    '''メッセージ冒頭に曜日が含まれている時の処理'''

                    target_wd = dotw.index(con[0])
                    con = con[1:].lstrip()

                    if con[0] == "曜":
                        con = con[1:].lstrip()
                    if con[0] == "日":
                        con = con[1:].lstrip()

                    df.loc[df['discord_id'] == message.author.id, 'message_{}'.format(target_wd)] = con
                    df.to_csv('users_test.csv')

                    m = "<@{}> さんの情報を更新しました。".format(message.author.id)
                    await self.sendbotchannel(m)

            if message.content == '!help':
                m = '【スケジュール登録方法】\r\n' + \
                    'このbotに対してリプライを送ることで登録できます\r\n' + \
                    '例①　今日の予定を登録したいとき\r\n' + \
                    '「<@477152129023344640> 21:00~24:00」\r\n' + \
                    '例②　明日の予定を登録したいとき\r\n' + \
                    '「<@477152129023344640> 明日　夜遅く帰宅、人いたらやりたい」\r\n' + \
                    '例③　水曜日の予定を登録したいとき\r\n' + \
                    '「<@477152129023344640> 水　不在です！」'

                await message.channel.send(m)

            if message.content == '!nade':
                target_mode = 'nade'
                for mode in modes:
                    if mode == target_mode:
                        os.system('sudo bash ./{}_mode/enable_{}_mode.sh'.format(mode,mode))
                    else:
                        os.system('sudo bash ./{}_mode/disable_{}_mode.sh'.format(mode,mode))

                m = "Changed to {} mode. Restarting...".format(target_mode)
                await message.channel.send(m)

                os.system('sudo -u steam /etc/init.d/csgo-server-launcher restart')
                m = 'Done!\r\nconnect 52.199.68.250; password 98i4\r\nsteam://connect/52.199.68.250:27015/98i4'
                await message.channel.send(m)

            if message.content == '!retake':
                target_mode = 'retake'
                for mode in modes:
                    if mode == target_mode:
                        os.system('sudo bash ./{}_mode/enable_{}_mode.sh'.format(mode,mode))
                    else:
                        os.system('sudo bash ./{}_mode/disable_{}_mode.sh'.format(mode,mode))

                m = "Changed to {} mode. Restarting...".format(target_mode)
                await message.channel.send(m)

                os.system('sudo -u steam /etc/init.d/csgo-server-launcher restart')
                m = 'Done!\r\nconnect 52.199.68.250; password 98i4\r\nsteam://connect/52.199.68.250:27015/98i4'
                await message.channel.send(m)

            if message.content == '!execute':
                target_mode = 'execute'
                for mode in modes:
                    if mode == target_mode:
                        os.system('sudo bash ./{}_mode/enable_{}_mode.sh'.format(mode,mode))
                    else:
                        os.system('sudo bash ./{}_mode/disable_{}_mode.sh'.format(mode,mode))

                m = "Changed to {} mode. Restarting...".format(target_mode)
                await message.channel.send(m)

                os.system('sudo -u steam /etc/init.d/csgo-server-launcher restart')
                m = 'Done!\r\nconnect 52.199.68.250; password 98i4\r\nsteam://connect/52.199.68.250:27015/98i4'
                await message.channel.send(m)

            if message.content.startswith('!bye'):
                '''終了用コマンド'''
                m = ':wave:'
                await message.channel.send(m)
                await self.close()

        except Exception: # エラー発生時にはトレースバックがDMで送られてくる
            await self.send2developer(traceback.format_exc())

client = MyClient()
client.run(token_str)