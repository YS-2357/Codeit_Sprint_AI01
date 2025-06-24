import sqlite3
from datetime import datetime
from schema import Review
from utils import get_logger

DB_PATH = "db/reviews.db"
logger = get_logger(__name__)

def get_connection():
    return sqlite3.connect(DB_PATH)

def insert_review(review: Review):
    logger.debug(f"🛠️ 리뷰 삽입 요청: {review}")
    connect = get_connection()
    cursor = connect.cursor()

    cursor.execute(
        """
        INSERT INTO review(movie_id, reviewer, content, sentiment_label, sentiment_score)
        VALUES (?, ?, ?, ?, ?)
        """,
        (review.movie_id, review.reviewer, review.content, review.sentiment_label, review.sentiment_score)
    )

    connect.commit()
    connect.close()
    logger.info(f"✅ 리뷰 삽입 완료 (movie_id={review.movie_id})")

def fetch_reviews_by_movie(movie_id: int):
    logger.debug(f"🛠️ 리뷰 조회 요청 (movie_id={movie_id})")
    connect = get_connection()
    cursor = connect.cursor()

    cursor.execute(
        """
        SELECT id, movie_id, reviewer, content, sentiment_label, sentiment_score, created_at
        FROM review
        WHERE movie_id = ?
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (movie_id,)
    )

    rows = cursor.fetchall()
    connect.close()

    reviews = [
        {
            "id": row[0],
            "movie_id": row[1],
            "reviewer": row[2],
            "content": row[3],
            "sentiment_label": row[4],
            "sentiment_score": row[5],
            "created_at": row[6]
        }
        for row in rows
    ]

    logger.info(f"✅ {len(reviews)}개의 리뷰 조회 완료")
    return reviews