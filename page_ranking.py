from nltk.stem.snowball import SnowballStemmer
import re, string
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_pages(search_term, results):
    results.insert(0, search_term)
    results = [preprocess(text) for text in results]

    # Convert the texts into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(results)

    # Calculate the cosine similarity between the vectors
    similarity = cosine_similarity(vectors)

    return [x+1e-7 for x in similarity[0][1:]]



def preprocess(text):
    stemmer = SnowballStemmer("english")
    text = text.lower()
    text = re.sub("[.,]", " ", text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '' , text)
    text = re.sub(' +', ' ', text)
    return " ".join([stemmer.stem(word) for word in text.split()])