from flask import Flask, render_template, request, jsonify
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
    return render_template('index.html', query=query)

if __name__ == '__main__':
    app.run(debug=True)
