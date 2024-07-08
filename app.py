import discord
from discord.ext import commands
from openai import OpenAI
from kendra import Kendra
import os
from dotenv import load_dotenv

# 各シークレットを環境変数から読み込む
load_dotenv()
datasource_path = os.getenv("DATASOURCE_PATH")
openai_api_key = os.getenv("OPENAI_API_KEY")
discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
discord_channel_id = os.getenv("DISCORD_CHANNEL_ID")

# Discordのボットの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Kendraクラスのインスタンスを作成
kendra = Kendra(datasource_path)

# OpenAI APIキーを設定
client = OpenAI(api_key=openai_api_key)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    channel = bot.get_channel(discord_channel_id)
    await channel.send("こんにちは。ぼくは kkrag です！なんでも聞いてね！")


@bot.command()
async def ask(ctx, *, question):
    reply_msg = ""

    # Kendraを使って最も類似した質問の回答と参考URLを取得
    results = kendra.find_best_match(question)
    print(f'\n事前回答: {results}')

    first_answer, second_answer, third_answer = results[:3]

    similarity_is_greater = compare_similarity_with_threshold(first_answer)

    if similarity_is_greater is False:
        reply_msg = "すみません。質問の意図が汲み取れませんでした。また質問してください。"

    else:
        # 改善された回答を取得
        GPTs_answer = throw_QandA_to_GPT(question, results)
        GPTs_contents = GPTs_answer.choices[0].message.content
        reply_msg = f"質問: {question}\n\n回答: {GPTs_contents}\n\n参考URL: {url}"

    # ユーザーに回答を送信
    await ctx.send(reply_msg)


# Discordボットのトークンを設定
bot.run(discord_bot_token)


def compare_similarity_with_threshold(first_answer: list, threshold=0.85):
    """閾値と類似度を比べて大きい時に True を返す関数

    Args:
        first_answer (list): 類似度が一番高い回答セット
        threshold (float, optional): デフォルトは0.85

    Returns:
        bool: 類似度の方が大きい時に True
    """

    # 最も高い類似度を比較する
    first_sim = first_answer[2]

    if first_sim > threshold:
        return True

    return False


def throw_QandA_to_GPT(question: str, results: list):

    # OpenAIを使って回答を改善
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "あなたは質問に対する回答を提供するAIです。つぎに伝える事前回答が存在すれば、その内容忠実に回答してください。もしわからなければ、その旨を伝えてください。",
            },
            {
                "role": "user",
                "content": f"質問: {question}\n\n事前回答: {answer}\n\n参考URL: {url}\n\n事前回答の正確性: {similarity}\n\n改善された回答:",
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=150
    )

    print(f'ChatGPTレスポンス: {chat_completion}')

    # 改善された回答を取得
    return chat_completion
