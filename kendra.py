from transformers import BertJapaneseTokenizer, BertModel
import torch
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine

class SentenceBertJapanese:
    def __init__(self, model_name_or_path, device=None):
        self.tokenizer = BertJapaneseTokenizer.from_pretrained(model_name_or_path)
        self.model = BertModel.from_pretrained(model_name_or_path)
        self.model.eval()

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        self.model.to(device)

    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] # model_outputの最初の要素が全てのトークンの埋め込みを含む
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    @torch.no_grad()
    def encode(self, sentences, batch_size=8):
        all_embeddings = []
        iterator = range(0, len(sentences), batch_size)
        for batch_idx in iterator:
            batch = sentences[batch_idx:batch_idx + batch_size]
            encoded_input = self.tokenizer.batch_encode_plus(batch, padding="max_length", max_length=512,truncation=True, return_tensors="pt").to(self.device)
            model_output = self.model(**encoded_input)
            sentence_embeddings = self._mean_pooling(model_output, encoded_input["attention_mask"]).to('cpu')

            all_embeddings.extend(sentence_embeddings)

        return torch.stack(all_embeddings)

class Kendra:
    def __init__(self, faq_path, model_name_or_path="cl-tohoku/bert-base-japanese"):
        self.faq_data = pd.read_csv(faq_path)
        self.model = SentenceBertJapanese(model_name_or_path)

    def find_best_matches(self, question, top_n=3):
        # 質問のエンコーディング
        question_emb = self.model.encode([question])

        # FAQ の質問のエンコーディング
        faq_embs = self.model.encode(self.faq_data['質問'].tolist())

        # 質問と FAQ の質問の cosine 類似度を計算
        similarities = [1 - cosine(question_emb[0], faq_emb) for faq_emb in faq_embs]

        # TOP N の類似度の高い FAQ を取得
        top_n_idxs = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_n]
        top_n_matches = self.faq_data.iloc[top_n_idxs]
        top_n_similarities = [similarities[idx] for idx in top_n_idxs]

        # 結果を準備
        results = []
        for i, (_, row) in enumerate(top_n_matches.iterrows()):
            results.append([row['回答'], row['参考URL'], top_n_similarities[i]])
        return results
