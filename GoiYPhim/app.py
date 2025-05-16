from flask import Flask, request, jsonify, render_template, session
import pyodbc
import logging

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'your_secure_random_secret_key_123'

def get_db():
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=ASUS-TUF-GAMING;'
            'DATABASE=HeThongGoiYPhim;'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes;'
        )
        logging.info("Database connection established successfully")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise

@app.route('/')
def home():
    logging.debug(f"Rendering home page, username in session: {session.get('username')}")
    return render_template('index.html', username=session.get('username'))

@app.route('/register', methods=['POST'])
def register():
    logging.debug("Processing register request")
    if not request.is_json:
        logging.error("Request is not JSON")
        return jsonify({'error': 'Yêu cầu phải là JSON'}), 400
    data = request.json
    username = data.get('username')
    if not username:
        logging.error("Username is missing")
        return jsonify({'error': 'Tên đăng nhập là bắt buộc'}), 400
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            logging.warning(f"Username {username} already exists")
            return jsonify({'error': 'Tên đăng nhập đã tồn tại'}), 400
        
        cursor.execute("INSERT INTO Users (Username) VALUES (?)", (username,))
        conn.commit()
        conn.close()
        logging.info(f"User {username} registered successfully")
        return jsonify({'success': True, 'message': 'Đăng ký thành công'})
    except Exception as e:
        logging.error(f"Register error: {str(e)}")
        return jsonify({'error': f'Lỗi đăng ký: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    logging.debug("Processing login request")
    if not request.is_json:
        logging.error("Request is not JSON")
        return jsonify({'error': 'Yêu cầu phải là JSON'}), 400
    data = request.json
    username = data.get('username')

    logging.debug(f"Login attempt with username: {username}")
    if not username:
        logging.error("Username is missing")
        return jsonify({'error': 'Tên đăng nhập là bắt buộc'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            logging.warning(f"Username {username} not found")
            return jsonify({'error': 'Tên đăng nhập không tồn tại'}), 401

        user_id = user[0]
        session['username'] = username
        session.permanent = True
        conn.close()
        logging.info(f"User {username} logged in successfully, user_id: {user_id}")
        return jsonify({'success': True, 'user_id': user_id, 'message': 'Đăng nhập thành công'})
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        return jsonify({'error': f'Lỗi đăng nhập: {str(e)}'}), 500

@app.route('/logout', methods=['POST'])
def logout():
    logging.debug("Processing logout request")
    session.pop('username', None)
    logging.info("User logged out successfully")
    return jsonify({'success': True, 'message': 'Đăng xuất thành công'})

@app.route('/search', methods=['POST'])
def search():
    logging.debug("Processing search request")
    if 'username' not in session:
        logging.error("User not logged in")
        return jsonify({'error': 'Vui lòng đăng nhập'}), 401

    if not request.is_json:
        logging.error("Request is not JSON")
        return jsonify({'error': 'Yêu cầu phải là JSON'}), 400
    keywords = request.json.get('keywords')
    if not keywords or not isinstance(keywords, str):
        logging.error("Invalid or missing keywords")
        return jsonify({'error': 'Vui lòng nhập từ khóa hợp lệ'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()

        conditions = []
        params = []
        for term in keywords.split():
            term = term.strip()
            if not term:
                continue
            # Kiểm tra nếu term là số (có thể là năm)
            if term.isdigit():
                conditions.append("m.ReleaseYear = ?")
                params.append(int(term))
            else:
                term = term.replace('%', '[%]').replace('_', '[_]')
                conditions.append("""
                    (LOWER(m.Title) LIKE ? OR 
                     LOWER(m.Director) LIKE ? OR 
                     LOWER(m.LeadActors) LIKE ? OR
                     EXISTS (
                         SELECT 1 FROM MovieGenres mg 
                         JOIN Genres g ON mg.GenreID = g.GenreID 
                         WHERE mg.MovieID = m.MovieID 
                         AND LOWER(g.GenreName) LIKE ?
                     ))
                """)
                search_term = f'%{term.lower()}%'
                params.extend([search_term] * 4)

        query = """
            SELECT DISTINCT 
                m.MovieID, m.Title, m.ReleaseYear, m.Duration, 
                m.Director, m.LeadActors, m.Rating
            FROM Movies m
            LEFT JOIN MovieGenres mg ON m.MovieID = mg.MovieID
            LEFT JOIN Genres g ON mg.GenreID = g.GenreID
            {}
            ORDER BY m.Rating DESC
        """.format('WHERE ' + ' OR '.join(conditions) if conditions else '')

        logging.debug(f"Search query: {query}")
        logging.debug(f"Search params: {params}")
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        movies = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Lấy thể loại cho từng phim
        for movie in movies:
            cursor.execute("""
                SELECT g.GenreName 
                FROM MovieGenres mg 
                JOIN Genres g ON mg.GenreID = g.GenreID 
                WHERE mg.MovieID = ?
            """, (movie['MovieID'],))
            genres = [row[0] for row in cursor.fetchall()]
            movie['Genres'] = ', '.join(genres) if genres else 'N/A'

        logging.info(f"Search results: {len(movies)} movies found")

        user_id = get_user_id(session['username'])
        if movies:
            for movie in movies:
                cursor.execute("""
                    INSERT INTO WatchHistory (UserID, MovieID, WatchDate)
                    SELECT ?, ?, GETDATE()
                    WHERE NOT EXISTS (
                        SELECT 1 FROM WatchHistory 
                        WHERE UserID = ? AND MovieID = ?
                    )
                """, (user_id, movie['MovieID'], user_id, movie['MovieID']))
            conn.commit()

        conn.close()
        return jsonify({'movies': movies})
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': f'Lỗi tìm kiếm: {str(e)}'}), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    logging.debug("Processing recommendations request")
    if 'username' not in session:
        logging.error("User not logged in")
        return jsonify({'error': 'Vui lòng đăng nhập'}), 401

    try:
        user_id = get_user_id(session['username'])
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT MovieID FROM WatchHistory WHERE UserID = ?", (user_id,))
        watched = [row[0] for row in cursor.fetchall()]

        query = """
            SELECT TOP 10
                m.MovieID, m.Title, m.ReleaseYear, m.Duration,
                m.Director, m.LeadActors, m.Rating,
                r.RecommendationScore
            FROM Recommendations r
            JOIN Movies m ON r.MovieID = m.MovieID
            WHERE r.UserID = ?
            ORDER BY r.RecommendationScore DESC
        """
        logging.debug(f"Recommendations query: {query}")
        cursor.execute(query, (user_id,))

        columns = [column[0] for column in cursor.description]
        recommendations = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for movie in recommendations:
            cursor.execute("""
                SELECT g.GenreName 
                FROM MovieGenres mg 
                JOIN Genres g ON mg.GenreID = g.GenreID 
                WHERE mg.MovieID = ?
            """, (movie['MovieID'],))
            genres = [row[0] for row in cursor.fetchall()]
            movie['Genres'] = ', '.join(genres) if genres else 'N/A'

        if len(recommendations) < 10:
            cursor.execute("""
                SELECT TOP ?
                    m.MovieID, m.Title, m.ReleaseYear, m.Duration,
                    m.Director, m.LeadActors, m.Rating,
                    0.5 AS RecommendationScore
                FROM Movies m
                WHERE m.MovieID NOT IN (
                    SELECT MovieID FROM WatchHistory WHERE UserID = ?
                )
                ORDER BY NEWID()
            """, (10 - len(recommendations), user_id))

            extra = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for movie in extra:
                cursor.execute("""
                    SELECT g.GenreName 
                    FROM MovieGenres mg 
                    JOIN Genres g ON mg.GenreID = g.GenreID 
                    WHERE mg.MovieID = ?
                """, (movie['MovieID'],))
                genres = [row[0] for row in cursor.fetchall()]
                movie['Genres'] = ', '.join(genres) if genres else 'N/A'
            recommendations.extend(extra)

        conn.close()

        for movie in recommendations:
            movie['RecommendationScore'] = min(100, movie['RecommendationScore'] * 100)

        logging.info(f"Returning {len(recommendations)} recommendations for user_id: {user_id}")
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        logging.error(f"Recommendations error: {str(e)}")
        return jsonify({'error': f'Lỗi gợi ý: {str(e)}'}), 500

@app.route('/recommendations-page')
def recommendations_page():
    logging.debug("Rendering recommendations page")
    if 'username' not in session:
        logging.error("User not logged in for recommendations page")
        return render_template('recommendations.html', error='Vui lòng đăng nhập')

    try:
        user_id = get_user_id(session['username'])
        conn = get_db()
        cursor = conn.cursor()

        query = """
            SELECT
                m.MovieID, m.Title, m.ReleaseYear, m.Duration,
                m.Director, m.LeadActors, m.Rating,
                r.RecommendationScore
            FROM Recommendations r
            JOIN Movies m ON r.MovieID = m.MovieID
            WHERE r.UserID = ?
            ORDER BY r.RecommendationScore DESC
        """
        logging.debug(f"Recommendations page query: {query}")
        cursor.execute(query, (user_id,))

        columns = [column[0] for column in cursor.description]
        movies = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for movie in movies:
            cursor.execute("""
                SELECT g.GenreName 
                FROM MovieGenres mg 
                JOIN Genres g ON mg.GenreID = g.GenreID 
                WHERE mg.MovieID = ?
            """, (movie['MovieID'],))
            genres = [row[0] for row in cursor.fetchall()]
            movie['Genres'] = ', '.join(genres) if genres else 'N/A'
            movie['RecommendationScore'] = min(100, movie['RecommendationScore'] * 100)

        conn.close()
        logging.info(f"Rendering recommendations page for user: {session['username']}")
        return render_template('recommendations.html', movies=movies, username=session['username'])
    except Exception as e:
        logging.error(f"Recommendations page error: {str(e)}")
        return render_template('recommendations.html', error=f'Lỗi: {str(e)}')

def get_user_id(username):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Users WHERE Username = ?", (username,))
        user_id = cursor.fetchone()
        conn.close()
        if user_id:
            logging.debug(f"Found user_id {user_id[0]} for username {username}")
            return user_id[0]
        logging.warning(f"No user_id found for username {username}")
        return None
    except Exception as e:
        logging.error(f"Get user_id error: {str(e)}")
        return None

if __name__ == '__main__':
    logging.info("Starting Flask application")
    app.run(debug=True)