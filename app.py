import discord
from discord.ext import commands
from openai import OpenAI
from kendra import Kendra

# Discordのボットの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Kendraクラスのインスタンスを作成
kendra = Kendra('rag-faq-db-6.csv')

# OpenAI APIキーを設定
# openai.api_key = 'openai-api-key'
client = OpenAI(
    api_key='openai-api-key',)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    # for guild in bot.guilds:
    #    print(f'Guild: {guild.name} (ID: {guild.id})')
    #    for channel in guild.channels:
    #        print(f' - {channel.name} (ID: {channel.id})')
    channel = bot.get_channel(1256130302171025481)
    await channel.send("わたしがきた")


@bot.event
async def on_massage(message: discord.Message):
    if message.author.bot:
        return
    if message.content == 'hello':
        await message.reply("こんにちは。ぼくは kkrag です！なんでも聞いてね！")


@bot.command()
async def hoge(ctx, arg):
    await ctx.send(arg)


@bot.command()
async def ask(ctx, *, question):
    # Kendraを使って最も類似した質問の回答と参考URLを取得
    answer, url = kendra.find_best_match(question)

    # OpenAIを使って回答を改善（必要に応じて）
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {"role": "system", "content": "あなたは質問に対する回答を提供するAIです。もし回答がドキュメントやソースに存在しない場合は、その旨を伝えてください。"},
    #         {"role": "user", "content": f"質問: {question}\n\n事前回答: {answer}\n\n参考URL: {url}\n\n改善された回答:"}
    #     ],
    #     max_tokens=150
    # )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "あなたは質問に対する回答を提供するAIです。もし回答がドキュメントやソースに存在しない場合は、その旨を伝えてください。",
            },
            {
                "role": "user",
                "content": f"質問: {question}\n\n事前回答: {answer}\n\n参考URL: {url}\n\n改善された回答:",
            }
        ],
        model="gpt-3.5-turbo",
        max_tokens=150
    )

    # 改善された回答を取得
    improved_answer = chat_completion['choices'][0]['text'].strip()

    # ユーザーに回答を送信
    await ctx.send(f"質問: {question}\n\n回答: {improved_answer}\n\n参考URL: {url}")

# Discordボットのトークンを設定
bot.run('discord-bot-token')
