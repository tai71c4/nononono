# app.py
from flask import Flask, render_template, request, jsonify, session
import json
from search_ai import search_movies_by_preferences

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Thay bằng một chuỗi bí mật bất kỳ

@app.route('/')
def index():
    username = session.get('username', '')
    return render_template('index.html', username=username)

@app.route('/search', methods=['POST'])
def handle_search():
    try:
        keywords = request.json.get('keywords', '')
        username = request.json.get('username', '')
        if not username:
            return jsonify({'error': 'Vui lòng đăng nhập trước khi tìm kiếm'}), 400
        if not keywords:
            return jsonify({'error': 'Vui lòng nhập từ khóa'}), 400

        # Lưu username vào session
        session['username'] = username

        # Gọi hàm tìm kiếm từ search_ai.py
        results = search_movies_by_preferences(keywords)

        # Lưu lịch sử tìm kiếm vào session
        if 'search_history' not in session:
            session['search_history'] = []
        session['search_history'].append({
            'keywords': keywords,
            'results': results
        })
        session.modified = True  # Đánh dấu session đã thay đổi

        return jsonify({'movies': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommend-by-preferences', methods=['POST'])
def handle_recommend():
    try:
        username = request.json.get('username', '')
        if not username:
            return jsonify({'error': 'Vui lòng đăng nhập trước khi nhận gợi ý'}), 400

        # Lấy lịch sử tìm kiếm từ session
        search_history = session.get('search_history', [])
        if not search_history:
            return jsonify({'movies': []})

        # Kết hợp tất cả từ khóa từ lịch sử tìm kiếm
        combined_keywords = []
        for search in search_history:
            keywords = search['keywords'].split(',')
            combined_keywords.extend([kw.strip() for kw in keywords if kw.strip()])

        # Gọi hàm tìm kiếm với từ khóa kết hợp để gợi ý
        if not combined_keywords:
            return jsonify({'movies': []})

        combined_keywords_str = ','.join(combined_keywords)
        recommendations = search_movies_by_preferences(combined_keywords_str, top_n=5)

        return jsonify({'movies': recommendations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommendations')
def show_recommendations():
    username = session.get('username', '')

    if not username:
        movies = [{"error": "Vui lòng đăng nhập trước khi xem gợi ý"}]
        return render_template('recommendations.html', movies=movies)

    search_history = session.get('search_history', [])
    if not search_history:
        movies = [{"error": "Không có lịch sử tìm kiếm để gợi ý"}]
        return render_template('recommendations.html', movies=movies)

    combined_keywords = []
    for search in search_history:
        keywords = search['keywords'].split(',')
        combined_keywords.extend([kw.strip() for kw in keywords if kw.strip()])

    if not combined_keywords:
        movies = [{"error": "Không có từ khóa để gợi ý"}]
        return render_template('recommendations.html', movies=movies)

    combined_keywords_str = ','.join(combined_keywords)
    recommendations = search_movies_by_preferences(combined_keywords_str, top_n=12)

    print("Dữ liệu recommendations:", recommendations)
    if not recommendations or not isinstance(recommendations, list):
        movies = [{"error": "Không thể tải danh sách gợi ý"}]
    else:
        movies = recommendations

    return render_template('recommendations.html', movies=movies)

@app.route('/results')
def show_results():
    query = request.args.get('query', '')
    movies_json = request.args.get('movies', '')
    movies = []
    if movies_json:
        try:
            movies = json.loads(movies_json).get('movies', [])
        except json.JSONDecodeError:
            movies = [{"error": "Dữ liệu không hợp lệ"}]
    return render_template('results.html', query=query, movies=movies)

@app.route('/logout', methods=['POST'])
def logout():
    # Chỉ xóa username, giữ lại search_history
    session.pop('username', None)
    return jsonify({'message': 'Đăng xuất thành công'})

if __name__ == '__main__':
    app.run(debug=True)