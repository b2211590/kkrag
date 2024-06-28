import discord
from discord.ext import commands
import openai
from kendra import Kendra

# Discordのボットの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Kendraクラスのインスタンスを作成
kendra = Kendra('/mnt/data/rag-faq-db-6.csv')

# OpenAI APIキーを設定
openai.api_key = 'your-openai-api-key'


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def ask(ctx, *, question):
    # Kendraを使って最も類似した質問の回答と参考URLを取得
    answer, url = kendra.find_best_match(question)

    # OpenAIを使って回答を改善（必要に応じて）
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"""
        以下の質問に対して適切な回答を提供してください。もし回答がドキュメントやソースに存在しない場合は、その旨を伝えてください。

        質問: {question}

        事前回答: {answer}

        参考URL: {url}

        改善された回答:
        """,
        max_tokens=150
    )

    # 改善された回答を取得
    improved_answer = response['choices'][0]['text'].strip()

    # ユーザーに回答を送信
    await ctx.send(f"質問: {question}\n\n回答: {improved_answer}\n\n参考URL: {url}")

# Discordボットのトークンを設定
bot.run('your-discord-bot-token')
