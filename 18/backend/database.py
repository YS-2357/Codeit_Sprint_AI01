import sqlite3
from schema import Movie
from logger import get_logger

DB_PATH = "movies.db"

logger = get_logger(__name__)

def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_all_movies():
    logger.debug("🛠️ 전체 영화 목록 조회 시작")
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
    logger.info(f"✅ {len(movies)}개의 영화 조회 완료")
    return movies

def insert_movie(movie: Movie):
    logger.debug(f"🛠️ 영화 삽입 요청: {movie.title} by {movie.director}")
    connect = get_connection()
    cursor = connect.cursor()

    # 중복 확인
    cursor.execute(
        "SELECT COUNT(*) FROM movie WHERE title = ? AND director = ?",
        (movie.title, movie.director)
    )
    if cursor.fetchone()[0] > 0:
        connect.close()
        logger.warning(f"⚠️ 중복된 영화 삽입 시도: {movie.title} by {movie.director}")
        raise ValueError("이미 등록된 영화입니다.")

    # 삽입
    cursor.execute(
        "INSERT INTO movie (title, director, category, rating, image_url) VALUES (?, ?, ?, ?, ?)",
        (movie.title, movie.director, movie.category, movie.rating, movie.image_url)
    )
    connect.commit()
    connect.close()
    logger.info(f"✅ 영화 삽입 완료: {movie.title} by {movie.director}")

def update_movie(movie: Movie) -> int:
    logger.debug(f"🛠️ 요청된 수정: {movie.title} by {movie.director}")
    connect = get_connection()
    cursor = connect.cursor()

    # 기존 영화 존재 여부 확인
    cursor.execute(
        "SELECT COUNT(*) FROM movie WHERE title = ? AND director = ?",
        (movie.title, movie.director)
    )
    if cursor.fetchone()[0] == 0:
        connect.close()
        logger.warning(f"⚠️ 수정 대상 영화 없음: {movie.title} by {movie.director}")
        return 0
    
    cursor.execute(
        """
        UPDATE movie
        SET category = ?, rating = ?, image_url = ?
        WHERE title = ? AND director = ?
        """,
        (movie.category, movie.rating, movie.image_url, movie.title, movie.director)
    )
    
    connect.commit()
    updated = cursor.rowcount
    connect.close()
    logger.info(f"✅ 수정 완료: {movie.title} by {movie.director} (수정된 행 수: {updated})")
    return updated

def delete_movie(movie: Movie) -> int:
    logger.debug(f"🛠️ 삭제 요청: {movie.title} by {movie.director}")
    connect = get_connection()
    cursor = connect.cursor()

    cursor.execute(
        "DELETE FROM movie WHERE title = ? AND director = ?",
        (movie.title, movie.director)
    )
    deleted = cursor.rowcount
    connect.commit()
    connect.close()
    if deleted == 0:
        logger.warning(f"⚠️ 삭제할 영화 없음: {movie.title} by {movie.director}")
    else:
        logger.info(f"✅ 삭제 완료: {movie.title} by {movie.director}")
    return deleted