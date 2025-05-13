# app.py
from flask import Flask, render_template, request
from recommender import recommend_movies

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = int(request.form['user_id'])
    recommendations = recommend_movies(user_id)
    return render_template('index.html', results=recommendations, user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
