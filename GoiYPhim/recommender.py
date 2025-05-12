import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_movies():
    df = pd.read_csv('data/movies.csv', low_memory=False)
    df = df[['title', 'overview', 'genres']].dropna()
    df = df[df['overview'].notnull()]
    df['combined'] = df['overview']
    return df

def recommend_movies(query, df):
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined'])

    query_vec = tfidf.transform([query])
    cosine_sim = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = cosine_sim.argsort()[-5:][::-1]

    return df.iloc[top_indices][['title', 'genres']]
