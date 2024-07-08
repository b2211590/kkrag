from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain.chains.llm import LLMChain
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key: str = os.getenv("OPENAI_API_KEY")


def build_chain(question: str, results: list):

    # 変数をアンパック
    first_answer, second_answer, third_answer = results
    fa_ans, fa_url, fa_sim = first_answer
    sa_ans, sa_url, sa_sim = second_answer
    ta_ans, ta_url, ta_sim = third_answer

    system_message_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            template="あなたは質問に対する回答を提供するAIです。つぎに伝える参考情報が存在すればその内容を正確性をもとに総合的に判断して、改善された回答として忠実に回答してください。"
        )
    )

    human_message_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["question", 'answer1', 'similarity1',
                             'answer2', 'similarity2', 'answer3', 'similarity3'],
            template="質問: {question}\n\n参考情報1: {answer1}\n\n参考情報1の正確性: {similarity1}\n\n参考情報2: {answer2}\n\n参考情報2の正確性: {similarity2}\n\n参考情報3: {answer3}\n\n参考情報3の正確性: {similarity3}\n\n改善された回答:"
        )
    )

    chat_prompt_template = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt])

    chain = LLMChain(
        llm=ChatOpenAI(api_key=openai_api_key, model_name="gpt-3.5-turbo"),
        prompt=chat_prompt_template
    )

    response = chain(question, fa_ans, fa_sim, sa_ans, sa_sim, ta_ans, ta_sim)

    return response

# print(chain("データサイエンティスト"))
