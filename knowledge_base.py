import logging
import torch
from sentence_transformers import SentenceTransformer, util
from typing import List


class KnowledgeBase():
    def __init__(self, answers: List[str]):
        self.answers = answers

        logging.debug("Loading the sentence embedding model")
        self.embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

        logging.debug("Embedding knowledge base answers")
        self.answer_embeddings = self.embedding_model.encode(
            self.answers, show_progress_bar=False)

    def look_up(self, question: str) -> str:
        question_embedding = self.embedding_model.encode(
            question, show_progress_bar=False)

        cos_scores = util.dot_score(question_embedding, self.answer_embeddings)
        top_results = torch.topk(cos_scores, k=1)
        top_score, top_idx = top_results[0][0], top_results[1][0]

        return self.answers[top_idx], top_score.item()
