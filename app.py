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
    print(f'\nThe first similarity is <{first_sim}> .')

    if first_sim > threshold:
        is_greater = True

    return is_greater


@client.event
async def on_ready():
    print(f'\nWe have logged in as {client.user}')

    # アクティビティを設定
    new_activity = f"/ask で質問してね"
    await client.change_presence(activity=discord.Game(new_activity))

    # スラッシュコマンドを同期
    await tree.sync()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(f'\nWe got message: {message.content}')

    if message.content.startswith('こんにちは'):
        await message.channel.send('こんにちは! ぼくは kkrag! \nH206に関する質問を回答するよ。なんでも質問してね!')


@tree.command(name='ask', description='質問内容を入力してくれると答えるよ')
async def ask(interaction: discord.Interaction, question: str):
    print(f'\nthe ask: {question} is called.')
    try:
        reply_msg = f'{question}について考え中...'

        # ユーザーに回答を送信
        await interaction.response.defer()

        # Kendraを使って最も類似した質問の回答と参考URLを取得
        results = kendra.find_best_matches(question)
        print(f'\n事前回答: {results}')

        similarity_is_greater: bool = compare_similarity_with_threshold(
            results)

        if similarity_is_greater is False:
            reply_msg = "すみません。質問の意図が汲み取れませんでした。また質問してください。"

        else:
            # 改善された回答を取得
            GPTs_answer = build_chain(question, results)
            print('\n')
            print(GPTs_answer)

            if GPTs_answer:
                reply_msg = f"質問: {question}\n\n回答: {GPTs_answer['text']}\n\n参考URL: {results[0][1]}"
            else:
                reply_msg = "ChatGPTSunechattaError: うまくchainできなかったようです"

        # 最終応答を送信
        await interaction.followup.send(content=reply_msg)

    except Exception as e:
        await interaction.followup.send(content=f"An error occurred: {str(e)}")


@client.event
async def on_disconnect():
    print("We disconnected, trying to reconnect...")


@client.event
async def on_resumed():
    print("We successfully reconnected.")

try:
    client.run(discord_bot_token)
except discord.errors.ConnectionClosed:
    print("Connection closed, restarting bot...")
    client.run(discord_bot_token)
