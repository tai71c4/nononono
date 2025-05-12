from recommender import load_movies

def smart_search(query):
    df = load_movies()
    results = df[df['title'].str.contains(query, case=False, na=False)]
    return results[['title', 'genres']].head(10)
