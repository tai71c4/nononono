import pandas as pd

def recommend_by_preferences(user_input, top_n=20):
    try:
        # Đọc dữ liệu từ file movies.csv
        movies = pd.read_csv('data/movies.csv')

        # Tách và chuẩn hóa từ khóa từ user_input
        keywords = [keyword.strip().lower() for keyword in user_input.split(',') if keyword.strip()]
        
        if not keywords:
            return ["Vui lòng nhập ít nhất một từ khóa."]

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
                return ["Dữ liệu không có cột 'year'. Vui lòng kiểm tra file movies.csv."]
            mask = mask & (movies['year'] == year_keyword)

        # Lọc theo các trường khác (title, cast_and_crew, genre, poster_path)
        if other_keywords:
            # Tạo điều kiện cho mỗi từ khóa trong các trường
            for keyword in other_keywords:
                # Kiểm tra từ khóa trong các cột text (title, cast_and_crew, genre, poster_path)
                field_mask = (
                    movies['title'].str.lower().str.contains(keyword, na=False) |
                    movies['cast_and_crew'].str.lower().str.contains(keyword, na=False) |
                    movies['genre'].str.lower().str.contains(keyword, na=False) |
                    movies['poster_path'].str.lower().str.contains(keyword, na=False)
                )
                mask = mask & field_mask

        # Lọc phim theo mask
        results = movies[mask][['title', 'genre', 'year', 'cast_and_crew']]  # Trả về các cột cần thiết
        if results.empty:
            return ["Không tìm thấy phim phù hợp."]

        # Giới hạn số lượng kết quả nếu top_n được chỉ định
        if top_n:
            results = results.head(top_n)
        
        return results.to_dict(orient='records')  # Trả về danh sách dictionary chứa thông tin phim

    except Exception as e:
        return [f"Lỗi: {str(e)}"]

# Ví dụ sử dụng
if __name__ == "__main__":
    user_input = "action,2015,leonardo"
    recommendations = recommend_by_preferences(user_input)
    for movie in recommendations:
        print(movie)