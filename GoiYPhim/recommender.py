import pandas as pd

# Đọc dữ liệu
movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# Kiểm tra và chuẩn hóa thang điểm của cột rating
print("Thống kê cột rating trước khi chuẩn hóa:")
print(ratings['rating'].describe())

# Nếu thang điểm là 0-5, chuyển thành 0-10
if ratings['rating'].max() <= 5:
    ratings['rating'] = ratings['rating'] * 2  # Nhân đôi để chuyển thành thang 0-10
    print("Đã chuẩn hóa thang điểm từ 0-5 thành 0-10.")
else:
    print("Thang điểm đã ở mức 0-10 hoặc cao hơn, không cần chuẩn hóa.")

# Tính avg_rating
movie_ratings = ratings.groupby('movieId')['rating'].mean().reset_index()
movie_ratings.columns = ['movieId', 'avg_rating']
movies = movies.merge(movie_ratings, on='movieId', how='left').fillna(0)

# Kiểm tra avg_rating sau khi chuẩn hóa
print("Thống kê avg_rating sau khi chuẩn hóa:")
print(movies['avg_rating'].describe())

def search_movies_by_keywords(keywords, top_n=20):
    """
    Tìm kiếm phim theo từ khóa từ nhiều trường, áp dụng logic AND, sắp xếp theo đánh giá cao nhất
    """
    keywords = [keyword.strip().lower() for keyword in keywords.lower().split(',') if keyword.strip()]
    if not keywords:
        return []

    # Phân loại từ khóa: năm và các từ khóa khác
    year_keyword = None
    other_keywords = []
    for keyword in keywords:
        if keyword.isdigit() and len(keyword) == 4:  
            year_keyword = int(keyword)
        else:
            other_keywords.append(keyword)

    # Khởi tạo mask ban đầu là True
    mask = pd.Series(True, index=movies.index)

    # Lọc theo năm (nếu có)
    if year_keyword is not None:
        mask = mask & (movies['year'].astype(str) == str(year_keyword))

    # Lọc theo các trường khác (title, cast_and_crew, genre)
    if other_keywords:
        for keyword in other_keywords:
            field_mask = (
                movies['title'].str.lower().str.contains(keyword, na=False) |
                movies['cast_and_crew'].str.lower().str.contains(keyword, na=False) |
                movies['genre'].str.lower().str.contains(keyword, na=False)
            )
            mask = mask & field_mask

    # Lọc phim theo mask, sắp xếp theo avg_rating và lấy top_n
    results = movies[mask].sort_values(by='avg_rating', ascending=False).head(top_n)

    return results[['title', 'genre', 'avg_rating', 'poster_path']].to_dict(orient='records')