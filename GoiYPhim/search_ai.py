import pandas as pd

def recommend_by_preferences(user_input, top_n=25):
    """
    Gợi ý phim dựa trên sở thích người dùng (thể loại hoặc tên phim).
    user_input: Chuỗi nhập vào từ người dùng, ví dụ: "action, avatar"
    top_n: Số lượng phim tối đa trả về (None để trả về tất cả)
    """
    try:
        # Load dữ liệu phim
        movies = pd.read_csv('data/movies.csv')
        
        # Xử lý input thành từ khóa
        keywords = [keyword.strip().lower() for keyword in user_input.split(',') if keyword.strip()]
        
        if not keywords:
            return ["Vui lòng nhập ít nhất một từ khóa."]

        # Lọc phim có từ khóa trùng trong tên hoặc thể loại
        mask = movies['title'].str.lower().str.contains('|'.join(keywords), na=False) | \
               movies['genres'].str.lower().str.contains('|'.join(keywords), na=False)

        # Lọc kết quả
        results = movies[mask][['title', 'genres']]
        if results.empty:
            return ["Không tìm thấy phim phù hợp."]

        # Trả kết quả theo số lượng yêu cầu
        if top_n:
            results = results.head(top_n)
        
        return results['title'].tolist()
    
    except Exception as e:
        return [f"Lỗi: {str(e)}"]