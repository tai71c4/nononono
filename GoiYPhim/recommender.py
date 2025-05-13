import pandas as pd

# Tải dữ liệu
movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# Gộp trung bình đánh giá vào dataset phim
movie_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
movie_ratings.columns = ['movieId', 'avg_rating']
movies = movies.merge(movie_ratings, on='movieId', how='left').fillna(0)

def search_movies_by_keywords(keywords, top_n=20):
    """
    Tìm kiếm phim theo từ khóa từ nhiều trường, sắp xếp theo đánh giá cao nhất
    """
    keywords = keywords.lower().split(',')
    conditions = pd.Series(False, index=movies.index)

    for keyword in keywords:
        keyword = keyword.strip()
        conditions |= movies['title'].str.lower().str.contains(keyword, na=False)
        conditions |= movies['cast_and_crew'].str.lower().str.contains(keyword, na=False)
        conditions |= movies['genre'].str.lower().str.contains(keyword, na=False)
        conditions |= movies['year'].astype(str).str.contains(keyword, na=False)
        conditions |= movies['movieId'].astype(str).str.contains(keyword, na=False)

    results = movies[conditions].sort_values(by='avg_rating', ascending=False).head(top_n)

    # Trả về cả danh sách phim lẫn dữ liệu để vẽ biểu đồ
    return results[['title', 'genre', 'avg_rating', 'poster_path']].to_dict(orient='records')
