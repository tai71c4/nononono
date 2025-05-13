import pandas as pd

def recommend_by_preferences(user_input):
    """
    Gợi ý tất cả phim dựa trên sở thích người dùng (từ khóa thể loại).
    user_input: Chuỗi chứa các thể loại, ví dụ: "action, sci-fi"
    """
    try:
        # Load dữ liệu phim
        movies = pd.read_csv('data/movies.csv')
        
        # Chuyển input thành danh sách từ khóa
        keywords = [keyword.strip().lower() for keyword in user_input.split(',')]
        
        # Tìm phim có thể loại khớp với ít nhất một từ khóa
        mask = movies['genres'].str.lower().str.contains('|'.join(keywords), na=False)
        recommendations = movies[mask][['title', 'genres']]
        
        # Trả về danh sách tiêu đề phim
        return recommendations['title'].tolist() if not recommendations.empty else ["Không tìm thấy phim phù hợp."]
    
    except Exception as e:
        return [f"Lỗi: {str(e)}"]