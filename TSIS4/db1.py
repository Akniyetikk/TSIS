import psycopg2
from config1 import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS game_sessions (
                id SERIAL PRIMARY KEY,
                player_id INTEGER REFERENCES players(id),
                score INTEGER NOT NULL,
                level_reached INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT NOW()
            );
        """)
    conn.commit()
    conn.close()

def get_player_id(username):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO UPDATE SET username = EXCLUDED.username RETURNING id;", (username,))
        p_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return p_id

def save_game_result(player_id, score, level):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)", (player_id, score, level))
    conn.commit()
    conn.close()

def get_leaderboard():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.username, s.score, s.level_reached, s.played_at 
            FROM game_sessions s JOIN players p ON s.player_id = p.id 
            ORDER BY s.score DESC LIMIT 10;
        """)
        return cur.fetchall()

def get_personal_best(player_id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s", (player_id,))
        res = cur.fetchone()[0]
    return res if res else 0
