from flask import Flask, render_template, request
from recommender import load_movies, recommend_movies
from search_ai import smart_search

app = Flask(__name__)
movies_df = load_movies()

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    recommendations = []
    genres = sorted(set(movies_df['genres'].dropna()))
    selected_genre = request.form.get("genre") if request.method == "POST" else "All"

    if request.method == "POST":
        query = request.form.get("query")
        filtered_df = movies_df

        if selected_genre and selected_genre != "All":
            filtered_df = filtered_df[filtered_df['genres'].str.contains(selected_genre)]

        recommendations = recommend_movies(query, filtered_df)
        results = smart_search(query)

    return render_template("index.html", results=results, recommendations=recommendations, genres=genres)

if __name__ == "__main__":
    app.run(debug=True)
