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


def build_chain(question: str, results: list) -> dict:

    first_reference, second_reference, third_reference = results

    inputs = {
        'question': question,
        'ref1': first_reference[0],
        'sim1': first_reference[2],
        'ref2': second_reference[0],
        'sim2': second_reference[2],
        'ref3': third_reference[0],
        'sim3': third_reference[2]
    }

    system_message_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            template="###命令書###\nあなたはH206という研究室の質問に対する回答を提供するAIです。制約条件に従って回答を作成してください。\n\n###制約条件###\n事前に用意したFAQのなかから質問に近いものの情報を参考情報として渡すので、その参考情報の正確度を考慮すること\n正確度が低い参考情報は回答に含めないこと\n必ず参考情報をもとに回答すること\n改善された回答: の続きを作成すること\n\n###対象###\nH206の研究室に所属する学生"
        )
    )

    human_message_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=["question", 'ref1', 'sim1',
                             'ref2', 'sim2', 'ref3', 'sim3'],
            template="質問: {question}\n\n参考情報1: {ref1}\n\n参考情報1の正確度: {sim1}\n\n参考情報2: {ref2}\n\n参考情報2の正確度: {sim2}\n\n参考情報3: {ref3}\n\n参考情報3の正確度: {sim3}\n\n改善された回答:"
        )
    )

    chat_prompt_template = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt])

    chain = LLMChain(
        llm=ChatOpenAI(api_key=openai_api_key, model_name="gpt-3.5-turbo"),
        prompt=chat_prompt_template
    )

    response = chain(inputs)

    return response
