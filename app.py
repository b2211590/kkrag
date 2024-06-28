from flask import Flask, request, jsonify
import openai
from kendra import Kendra

app = Flask(__name__)
kendra = Kendra('/mnt/data/rag-faq-db-6.csv')

openai.api_key = 'your-openai-api-key'

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']
    answer, url = kendra.find_best_match(question)
    
    # 必要に応じて、OpenAIを使用して回答を改善
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"質問: {question}\n\n回答: {answer}\n\n参考URL: {url}",
        max_tokens=150
    )
    
    return jsonify({
        'question': question,
        'answer': response['choices'][0]['text'].strip(),
        'reference': url
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
