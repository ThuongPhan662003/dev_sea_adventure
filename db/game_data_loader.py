import pymysql
from config import DB_CONFIG


class GameDataLoader:
    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            db=DB_CONFIG["database"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def get_players_in_game(self, game_id):
        """
        Lấy danh sách người chơi đang tham gia 1 game cụ thể, bao gồm:
        - player_name
        - color
        - vị trí khởi tạo (dựa theo lượt và dữ liệu cũ)
        """
        with self.conn.cursor() as cursor:
            query = """
                SELECT gp.game_player_id, p.player_name, gp.color, gp.`order`
                FROM gameplayer gp
                JOIN roomplayer rp ON gp.room_player_id = rp.room_player_id
                JOIN player p ON rp.player_id = p.player_id
                WHERE gp.game_id = %s
                ORDER BY gp.`order`
            """
            cursor.execute(query, (game_id,))
            return cursor.fetchall()

    def get_map_for_game(self, game_id):
        """
        Lấy danh sách map (position, source_id nếu có).
        """
        with self.conn.cursor() as cursor:
            query = """
                SELECT position, source_id
                FROM map
                WHERE game_id = %s
                ORDER BY position
            """
            cursor.execute(query, (game_id,))
            return cursor.fetchall()

    def get_sourcecode_info(self):
        """
        Lấy thông tin chi tiết về tất cả source code (score, level).
        """
        with self.conn.cursor() as cursor:
            query = """
                SELECT source_id, level, score
                FROM sourcecode
            """
            cursor.execute(query)
            return cursor.fetchall()

    def close(self):
        self.conn.close()
