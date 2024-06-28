import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Kendra:
    def __init__(self, faq_path):
        self.faq_data = pd.read_csv(faq_path)
        self.vectorizer = TfidfVectorizer()
        self.vectorizer.fit(self.faq_data['質問'])

    def find_best_match(self, question):
        question_vec = self.vectorizer.transform([question])
        faq_vecs = self.vectorizer.transform(self.faq_data['質問'])
        similarities = cosine_similarity(question_vec, faq_vecs).flatten()
        best_match_idx = np.argmax(similarities)
        best_match = self.faq_data.iloc[best_match_idx]
        return best_match['回答'], best_match['参考URL']

# 使用例:
# kendra = Kendra('/mnt/data/rag-faq-db-6.csv')
# answer, url = kendra.find_best_match("入力された質問")
