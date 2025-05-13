import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

# Load dữ liệu
print("Đang tải dữ liệu...")
movies = pd.read_csv('D:/GitGub/nononono/GoiYPhim/movie_recommender/data/movies.csv')
ratings = pd.read_csv('D:/GitGub/nononono/GoiYPhim/movie_recommender/data/ratings.csv')

# Lọc dữ liệu để giảm kích thước
print("Đang lọc dữ liệu...")
min_user_ratings = 100  # Người dùng có ít nhất 100 đánh giá
min_movie_ratings = 200  # Phim có ít nhất 200 đánh giá
user_counts = ratings['userId'].value_counts()
movie_counts = ratings['movieId'].value_counts()
filtered_ratings = ratings[
    (ratings['userId'].isin(user_counts[user_counts >= min_user_ratings].index)) &
    (ratings['movieId'].isin(movie_counts[movie_counts >= min_movie_ratings].index))
]

# Gộp dữ liệu
df = filtered_ratings.merge(movies, on='movieId')[['userId', 'title', 'rating']]

# Tạo ma trận thưa user-item
print(f"Số người dùng sau khi lọc: {len(df['userId'].unique())}")
print(f"Số phim sau khi lọc: {len(df['title'].unique())}")
user_ids = df['userId'].astype('category')
movie_titles = df['title'].astype('category')
pivot = csr_matrix(
    (df['rating'].astype(float), (user_ids.cat.codes, movie_titles.cat.codes)),
    shape=(len(user_ids.cat.categories), len(movie_titles.cat.categories))
)
print("Đã tạo ma trận thưa.")

# Tính similarity giữa các phim (item-based)
print("Đang tính similarity giữa các phim...")
similarity = cosine_similarity(pivot.T, dense_output=False)  # .T để tính trên phim
print("Hoàn tất tính similarity!")

# Hàm gợi ý
def get_recommendations(user_id, top_n=5):
    print(f"Tìm gợi ý cho user_id: {user_id}")
    if user_id not in user_ids.cat.categories:
        return ["❌ Không tìm thấy người dùng."]
    
    user_idx = user_ids.cat.categories.get_loc(user_id)
    user_ratings = pivot[user_idx].toarray().flatten()  # Đánh giá của người dùng
    rated_indices = np.where(user_ratings > 0)[0]  # Các phim người dùng đã đánh giá
    
    # Tính điểm gợi ý dựa trên độ tương đồng phim
    scores = np.zeros(len(movie_titles.cat.categories))
    for idx in rated_indices:
        sim_scores = similarity[idx].toarray().flatten()
        scores += sim_scores * user_ratings[idx]
    
    # Sắp xếp và loại bỏ phim đã xem
    scores[rated_indices] = -1  # Đánh dấu phim đã xem
    top_indices = np.argsort(scores)[::-1][:top_n]
    recommended = [movie_titles.cat.categories[i] for i in top_indices]
    
    return recommended

print("Đã sẵn sàng để gợi ý!")