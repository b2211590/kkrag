import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from kendra import Kendra
from gpt_chain import build_chain

# 各シークレットを環境変数から読み込む
load_dotenv()
datasource_path = os.getenv("DATASOURCE_PATH")
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
discord_channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))

# Discordのボットの設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Kendraクラスのインスタンスを作成
kendra = Kendra(datasource_path)


def compare_similarity_with_threshold(results: list, threshold=0.85) -> bool:
    """閾値と類似度を比べて大きい時に True を返す関数

    Args:
        first_answer (list): 類似度が一番高い回答セット
        threshold (float, optional): デフォルトは0.85

    Returns:
        bool: 類似度の方が大きい時に True
    """

    is_greater: bool = False

    first_answer: list = results[0]

    # 最も高い類似度を比較する
    first_sim = first_answer[2]

    if first_sim > threshold:
        is_greater = True

    return is_greater


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    # アクティビティを設定
    new_activity = f"チャットボット"
    await client.change_presence(activity=discord.Game(new_activity))

    # スラッシュコマンドを同期
    await tree.sync()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f'We got message: {message.content}')

    if message.content.startswith('こんにちは'):
        await message.channel.send('こんにちは! ぼくは kkrag! \nH206に関する質問を回答するよ。なんでも質問してね!')


@tree.command(name='ask', description='質問内容を入力してくれると答えるよ')
async def ask(interaction: discord.Interaction, question: str):
    print(f'the \'ask\' is called.')
    reply_msg = "this is read only in debugging."

    # Kendraを使って最も類似した質問の回答と参考URLを取得
    results = kendra.find_best_matches(question)
    print(f'\n事前回答: {results}')

    similarity_is_greater: bool = compare_similarity_with_threshold(results)

    if similarity_is_greater is False:
        reply_msg = "すみません。質問の意図が汲み取れませんでした。また質問してください。"

    else:
        # 改善された回答を取得
        # GPTs_answer = throw_QandA_to_GPT(question, results)
        GPTs_answer = build_chain(question, results)
        print(GPTs_answer)
        # GPTs_contents = GPTs_answer.choices[0].message.content
        # reply_msg = f"質問: {question}\n\n回答: {GPTs_contents}\n\n参考URL: {url}"

    # ユーザーに回答を送信
    await interaction.response.send_message(reply_msg)


client.run(discord_bot_token)


# def throw_QandA_to_GPT(question: str, results: list):
#
#     # OpenAIを使って回答を改善
#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "system",
#                 "content": "あなたは質問に対する回答を提供するAIです。つぎに伝える事前回答が存在すれば、その内容忠実に回答してください。もしわからなければ、その旨を伝えてください。",
#             },
#             {
#                 "role": "user",
#                 "content": f"質問: {question}\n\n事前回答: {answer}\n\n参考URL: {url}\n\n事前回答の正確性: {similarity}\n\n改善された回答:",
#             }
#         ],
#         model="gpt-3.5-turbo",
#         max_tokens=150
#     )
#
#     print(f'ChatGPTレスポンス: {chat_completion}')
#
#     # 改善された回答を取得
#     return chat_completion
