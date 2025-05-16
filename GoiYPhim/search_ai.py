import pyodbc
import pandas as pd
from datetime import datetime

def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
            'SERVER=ASUS-TUF-GAMING;'
            'DATABASE=HeThongGoiYPhim;'
            'Trusted_Connection=yes;'
            'TrustServerCertificate=yes;' 
    )
    return conn

def search_movies(keywords, user_id=None, limit=20):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        for term in keywords.split():
            term = term.strip()
            if not term:
                continue
            term = term.replace('%', '[%]').replace('_', '[_]')  # Escape ký tự đặc biệt
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
        
        query = f"""
            WITH MovieGenres AS (
                SELECT mg.MovieID, STRING_AGG(g.GenreName, ', ') AS Genres
                FROM MovieGenres mg
                JOIN Genres g ON mg.GenreID = g.GenreID
                GROUP BY mg.MovieID
            )
            SELECT TOP {limit}
                m.MovieID, m.Title, mg.Genres, m.ReleaseYear,
                m.Duration, m.Director, m.LeadActors, m.Rating
            FROM Movies m
            JOIN MovieGenres mg ON m.MovieID = mg.MovieID
            {'WHERE ' + ' OR '.join(conditions) if conditions else ''}
            ORDER BY m.Rating DESC
        """
        
        print(f"Search keywords: {keywords}")
        print(f"Search params: {params}")
        cursor.execute(query, params)
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print(f"Search results: {results}")
        
        if user_id and results:
            for movie in results:
                cursor.execute("""
                    INSERT INTO WatchHistory (UserID, MovieID, WatchDate)
                    SELECT ?, ?, GETDATE()
                    WHERE NOT EXISTS (
                        SELECT 1 FROM WatchHistory 
                        WHERE UserID = ? AND MovieID = ?
                    )
                """, (user_id, movie['MovieID'], user_id, movie['MovieID']))
            conn.commit()
        
        return results
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []
    finally:
        conn.close()