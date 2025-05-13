from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from recommender import search_movies_by_keywords

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend-by-preferences', methods=['POST'])
def handle_recommend():
    try:
        user_input = request.json.get('preferences', '').strip()
        if not user_input:
            return jsonify({'error': 'Vui lòng nhập sở thích'}), 400

        results = search_movies_by_keywords(user_input)
        return jsonify({'movies': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def show_results():
    query = request.args.get('query', '')
    movies_json = request.args.get('movies', '')
    movies = []

    if movies_json:
        try:
            movies_data = json.loads(movies_json).get('movies', [])
            movies = pd.DataFrame(movies_data) if movies_data else []
        except json.JSONDecodeError:
            movies = [{"error": "Dữ liệu không hợp lệ"}]

    return render_template('index.html', query=query, movies=movies.to_dict(orient='records') if isinstance(movies, pd.DataFrame) else movies)

if __name__ == '__main__':
    app.run(debug=True)