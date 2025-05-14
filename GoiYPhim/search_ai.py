# search_ai.py
import pandas as pd
from recommender import movies  # Nhập DataFrame movies đã được xử lý từ recommender.py

def search_movies_by_preferences(user_input, top_n=20):
    """
    Tìm kiếm phim dựa trên sở thích người dùng (từ khóa), sắp xếp theo avg_rating giảm dần.
    """
    try:
        # Tách và chuẩn hóa từ khóa từ user_input
        keywords = [keyword.strip().lower() for keyword in user_input.split(',') if keyword.strip()]
        
        if not keywords:
            return [{"error": "Vui lòng nhập ít nhất một từ khóa."}]

        # Phân loại từ khóa: năm và các từ khóa khác
        year_keyword = None
        other_keywords = []
        for keyword in keywords:
            if keyword.isdigit() and len(keyword) == 4:  # Giả sử từ khóa là năm nếu nó là số 4 chữ số
                year_keyword = int(keyword)
            else:
                other_keywords.append(keyword)

        # Khởi tạo mask ban đầu là True
        mask = pd.Series(True, index=movies.index)

        # Lọc theo năm (nếu có)
        if year_keyword is not None:
            if 'year' not in movies.columns:
                return [{"error": "Dữ liệu không có cột 'year'. Vui lòng kiểm tra file movies.csv."}]
            mask = mask & (movies['year'] == year_keyword)

        # Lọc theo các trường khác (title, cast_and_crew, genre)
        if other_keywords:
            for keyword in other_keywords:
                field_mask = (
                    movies['title'].str.lower().str.contains(keyword, na=False) |
                    movies['cast_and_crew'].str.lower().str.contains(keyword, na=False) |
                    movies['genre'].str.lower().str.contains(keyword, na=False)
                )
                mask = mask & field_mask

        # Lọc phim theo mask, sắp xếp theo avg_rating giảm dần
        results = movies[mask][['title', 'genre', 'year', 'avg_rating']]
        if results.empty:
            return [{"error": "Không tìm thấy phim phù hợp."}]

        # Sắp xếp theo avg_rating giảm dần và giới hạn số lượng kết quả
        results = results.sort_values(by='avg_rating', ascending=False)
        if top_n:
            results = results.head(top_n)
        
        return results.to_dict(orient='records')  # Trả về danh sách dictionary chứa thông tin phim

    except Exception as e:
        return [{"error": f"Lỗi: {str(e)}"}]