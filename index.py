import os
import discord
from translate import Translator
from os.path import join, dirname
from dotenv import load_dotenv
import uuid
import json
import promptOptimize
import requests,base64
from io import BytesIO
# Discord.pyからクライアントインスタンスを作成するよおおおおおおおおおおお
client = discord.Client(intents = discord.Intents.all())
intents = discord.Intents.default()
intents.message_content = True

# 環境変数の設定だよおおおおおうへへへへへへｗｗｗｗｗ
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Hugging_FaceとDiscordBotのトークン、ApplicationIDを環境変数から読み込むうううううううううういひひひひひひｗｗｗｗ

DISCORD_TOKEN = os.environ.get("BOT_TOKEN")
APPLICATION_ID = os.environ.get("APPLICATION_ID") # 起動自体には必要ないが、メンションで反応させる際に必要

@client.event
async def on_ready():
    print('{0.user}'.format(client) ,"がログインしました")

@client.event
async def on_message(message:discord.Message):
    # メッセージの送信者がbotだった場合は無視するよぉぉぉぉぉぉん
    if message.author.bot:
        return

    # URLは無視する
    if '://' in message.content:
        return

    if message.author != client and message.content == '!help':
        if message.guild:
            await message.channel.send('このBotは、「@USB無くした かわいい猫」のように、メンション＋作りたい画像の単語を送信することで画像が作れるよ！(DMで使用する場合はメンションは要りません。)\n\n## 【生成時のヒント】\n- 画像を表す単語はコンマ「,」で区切って複数書くと、より理想の画像に近づくよ！\n- 実写に近い画像を作りたい場合は、単語のどこかに「写実的」と付けてね！\n- イラストを生成したい場合は、単語のどこかに「イラスト」と書いてね！\n- うまく理想の画像が作れない場合は、英語で送信してみてね！')
        else:
            await message.channel.send('このBotは、「かわいい猫,黒毛,オッドアイ」のように、作りたい画像の単語を送信することで画像が作れるよ！\n\n## 【生成時のヒント】\n- 画像を表す単語はコンマ「,」で区切って複数書くと、より理想の画像に近づくよ！\n- 実写に近い画像を作りたい場合は、単語のどこかに「写実的」と付けてね！\n- イラストを生成したい場合は、単語のどこかに「イラスト」と書いてね！\n- うまく理想の画像が作れない場合は、英語で送信してみてね！')
        return

    if message.author != client and (f"<@{APPLICATION_ID}>" in message.content) or not message.guild:
        mode = 0
        json_load = json.load(open('permission.json','r'))
        # permission.jsonを参照し、一般ユーザーの使用を許可するかどうか確認し、許可しない場合はreturn(メンテナンス中など、生成してほしくない時に使用する)
        if not json_load['normal_user'] and not message.author.name == 'yomi4486' :
            await message.channel.send('現在メンテナンス中です。')
            return
        #プロンプトからメンションのテキスト(<@12345678>みたいなやつ)と、メンションの後に自動で入るスペースを取り除く（画像を生成中ですって送るときに変なスペースができて気持ち悪いから）
        JPprompt = message.content.replace(f'<@{APPLICATION_ID}> ', f'<@{APPLICATION_ID}>').replace(f'<@{APPLICATION_ID}>', '')
        native_prompt = JPprompt
        msg = await message.channel.send(f'「{native_prompt}」の画像を生成中です…')
        # 送信されたメッセージがメンションのみだった場合は処理を行わず、Botの説明を軽く行う
        if not JPprompt.replace(' ', '').replace('　', '') == '':
            if len(JPprompt) > 499:
                await message.channel.send('プロンプトが長すぎるよ！500文字未満にしてね！')
                return
            
            if 'イラスト' in JPprompt or 'illust' in JPprompt.lower() or 'アニメ' in JPprompt or 'anime' in JPprompt.lower():
                JPprompt = JPprompt.lower().replace('illust','').replace('anime','').replace('アニメ','').replace('イラスト','')
                JPprompt = JPprompt + ',anime,waifu:1.2'
                mode = 1
            
            JPprompt = promptOptimize.optimize(JPprompt)
            # 正確性が増すので英語に翻訳してからプロンプトに突っ込む
            translator = Translator(from_lang = "ja", to_lang = "en")
            prompt = translator.translate(JPprompt)
            if ("/" in prompt):
                prompt = JPprompt
            # プロンプトはコンマで区切ったほうがいいので、コンマが使われていないプロンプトの場合はスペースをコンマに置き換える

            if not "," in prompt:
                replaceprompt = ''
                while not prompt == replaceprompt:
                    replaceprompt = prompt
                    prompt = prompt.replace(' ',',').replace('　',',').replace(',,',',')
            if mode == 0:
                filename = uuid.uuid4()

                payload = {
                    "prompt": f"{prompt} ,high quality, 8k",
                    "steps": 20,
                    "width":512,
                    "height":512,
                    "batch_size": 1,
                    "cfg_scale": 7,
                    "restore_faces": True,
                    "negative_prompt": "low quality,blurry,lowres,duplicate,morbid,deformed,monochrome,greyscale,comic,4koma,2koma,sepia,simple background,rough,unfinished,horror,duplicate legs,duplicate arms,error,worst quality,normal quality",
                }
                response = requests.post(url=f'http://127.0.0.1:7861/sdapi/v1/txt2img', json=payload,headers={"Content-Type": "application/json"})
                r = response.json()
                with open(f".\\result\\{filename}.png", 'wb') as f:
                    f.write(base64.b64decode(r['images'][0]))

                await msg.delete()
                await message.reply('完成したよ！',file=discord.File(f'.\\result\\{filename}.png'))
                os.remove(f".\\result\\{filename}.png")
            else:
                try:
                    response = requests.get(url=f'http://192.168.255.186:9876/image?token={message.author.id}&prompt={prompt}&step=50')
                    await message.reply(file=discord.File(BytesIO(response.content),"result.png"))
                except Exception as e:
                    print(e)
                    await message.reply(f"生成に失敗しました！\n```\n{e}\n```")
        else:
            await message.channel.send('作りたい画像の単語を指定してね！\n（例：@USB無くした かわいい猫）')
        
client.run(DISCORD_TOKEN)