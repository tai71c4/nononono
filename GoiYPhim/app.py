from flask import Flask, render_template, request, jsonify
from search_ai import recommend_by_preferences  # Gợi ý theo sở thích

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Route gợi ý theo sở thích người dùng
@app.route('/recommend-by-preferences', methods=['POST'])
def handle_ai_recommendation():
    try:
        user_input = request.json.get('preferences', '').strip()
        if not user_input:
            return jsonify({'error': 'Vui lòng nhập sở thích'}), 400
        
        # Gọi hàm từ search_ai.py
        recommendations = recommend_by_preferences(user_input)
        return jsonify({'movies': recommendations})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route hiển thị kết quả gợi ý
@app.route('/results')
def show_results():
    query = request.args.get('query', '')
    movies = request.args.get('movies', '[]')
    return render_template(
        'index.html',
        results=eval(movies),
        query=query
    )

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)