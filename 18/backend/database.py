import sqlite3

DB_PATH = "movies.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_all_movies():
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute("Select id, title, director, category, rating, image_url FROM movie")
    rows = cursor.fetchall()
    connect.close()
    movies = [
        {
            "id": row[0],
            "title": row[1],
            "director": row[2],
            "category": row[3],
            "rating": row[4],
            "image_url": row[5]
        }
        for row in rows
    ]
    return movies

def insert_movie(movie: dict):
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute(
        "INSERT INTO movie (title, director, category, rating, image_url) VALUES (?, ?, ?, ?, ?)",
        (movie["title"], movie["director"], movie["category"], movie.get("rating"), movie.get("image_url"))
    )
    connect.commit()
    connect.close()

def delete_movie(movie: dict):
    return