import pyodbc
import pandas as pd
from surprise import SVD, Dataset, Reader
from datetime import datetime

def generate_recommendations(user_id):
    if not user_id:
        print("Error: Invalid user_id")
        return False

    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=ASUS-TUF-GAMING;'
            'DATABASE=HeThongGoiYPhim;'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes;' 
    )
    
    try:
        ratings = pd.read_sql("""
            SELECT UserID, MovieID, RatingGiven 
            FROM WatchHistory 
            WHERE RatingGiven IS NOT NULL
        """, conn)
        
        algo = None
        if len(ratings) >= 10:  # Kiểm tra số lượng đánh giá
            reader = Reader(rating_scale=(1, 10))
            data = Dataset.load_from_df(ratings[['UserID', 'MovieID', 'RatingGiven']], reader)
            trainset = data.build_full_trainset()
            algo = SVD()
            algo.fit(trainset)
            print(f"Trained SVD model with {len(ratings)} ratings")
        else:
            print("Not enough ratings, falling back to content-based")

        watched = pd.read_sql("""
            SELECT DISTINCT MovieID FROM WatchHistory 
            WHERE UserID = ?
        """, conn, params=(user_id,))['MovieID'].tolist()
        
        all_movies = pd.read_sql("SELECT MovieID FROM Movies", conn)['MovieID'].tolist()
        unseen = [mid for mid in all_movies if mid not in watched]
        
        movies_data = pd.read_sql("""
            SELECT m.MovieID, m.Rating, 
                   STRING_AGG(g.GenreName, ', ') AS Genres
            FROM Movies m
            JOIN MovieGenres mg ON m.MovieID = mg.MovieID
            JOIN Genres g ON mg.GenreID = g.GenreID
            GROUP BY m.MovieID, m.Rating
        """, conn)
        
        recommendations = []
        for movie_id in unseen[:100]:
            cf_score = algo.predict(user_id, movie_id).est if algo else 0
            movie_rating = movies_data[movies_data['MovieID'] == movie_id]['Rating'].values[0] if not movies_data.empty else 5
            cb_score = movie_rating
            hybrid_score = 0.7 * (cf_score / 10) + 0.3 * (cb_score / 10)
            hybrid_score = max(0, min(1, hybrid_score))
            recommendations.append((movie_id, hybrid_score))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        cursor = conn.cursor()
        for movie_id, score in recommendations[:50]:
            cursor.execute("""
                MERGE INTO Recommendations AS target
                USING (VALUES (?, ?, ?, GETDATE())) AS source(UserID, MovieID, Score, Date)
                ON target.UserID = source.UserID AND target.MovieID = source.MovieID
                WHEN MATCHED THEN UPDATE SET 
                    RecommendationScore = source.Score,
                    RecommendedAt = source.Date
                WHEN NOT MATCHED THEN INSERT 
                    (UserID, MovieID, RecommendationScore, RecommendedAt)
                    VALUES (source.UserID, source.MovieID, source.Score, source.Date);
            """, (user_id, movie_id, score))
        conn.commit()
        print(f"Saved {len(recommendations[:50])} recommendations for user {user_id}")
        
        return True
        
    except Exception as e:
        print(f"Recommendation generation failed: {str(e)}")
        return False
    finally:
        conn.close()