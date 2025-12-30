from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import nltk
nltk.download('stopwords')
stopword_es = nltk.corpus.stopwords.words('spanish')
stopword_es.extend(['don'])

class TfIDFSearcher:
    def __init__(self, documents):
        self.documents = documents
        self.vectorizer = CountVectorizer(stop_words=stopword_es)
        self.transformer = TfidfTransformer()
        self.tfidf_matrix = self._fit_transform()

    def _fit_transform(self):
        count_matrix = self.vectorizer.fit_transform(self.documents)
        tfidf_matrix = self.transformer.fit_transform(count_matrix)
        return tfidf_matrix

    def search(self, query, top_n=5):
        query_vec = self.vectorizer.transform([query])
        query_tfidf = self.transformer.transform(query_vec)
        scores = (self.tfidf_matrix * query_tfidf.T).toarray()
        ranked_indices = scores.flatten().argsort()[::-1][:top_n]
        return [(i, self.documents[i], scores[i][0]) for i in ranked_indices if scores[i][0] > 0]