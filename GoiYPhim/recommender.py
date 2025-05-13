import pandas as pd
from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split

# Load dữ liệu
print("Đang tải dữ liệu...")
movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# Chuẩn bị dữ liệu cho Surprise
print("Đang chuẩn bị dữ liệu...")
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)

# Chia dữ liệu
trainset, testset = train_test_split(data, test_size=0.2)

# Huấn luyện mô hình SVD
print("Đang huấn luyện mô hình SVD...")
algo = SVD()
algo.fit(trainset)

print("Đã huấn luyện xong mô hình!")

# Hàm gợi ý phim
def recommend_movies(user_id, top_n=5):
    print(f"Tìm gợi ý cho user_id: {user_id}")
    if user_id not in ratings['userId'].unique():
        return ["❌ Không tìm thấy người dùng."]

    rated_movies = ratings[ratings['userId'] == user_id]['movieId'].values
    all_movie_ids = movies['movieId'].unique()
    movies_to_predict = [mid for mid in all_movie_ids if mid not in rated_movies]

    predictions = [algo.predict(user_id, mid) for mid in movies_to_predict]
    predictions.sort(key=lambda x: x.est, reverse=True)
    top_predictions = predictions[:top_n]

    recommended_movie_ids = [pred.iid for pred in top_predictions]
    recommended_movies = movies[movies['movieId'].isin(recommended_movie_ids)]['title'].tolist()

    return recommended_movies

def load_movies():
    return movies
