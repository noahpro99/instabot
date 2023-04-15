import psycopg2
from typing import List
import utils.models as models
class ORM:
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
        
    def get_all_users(self) -> List[models.User]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users")
        users: List[models.User] = []
        for user in self.cur.fetchall():
            users.append(models.User(*user))
        return users
    
    def insert_messages(self, messages: List[models.Message]):
        cur = self.conn.cursor()
        usernames = set([message.sender for message in messages] + [message.receiver for message in messages])
        cur.executemany("INSERT INTO users (username) VALUES (%s) ON CONFLICT DO NOTHING", [(username,) for username in usernames])
        cur.executemany("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", [(message.sender, message.receiver, message.message) for message in messages])
        self.conn.commit()
        cur.close()
        
    def get_all_messages(self) -> List[models.Message]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM messages")
        messages: List[models.Message] = []
        for message in cur.fetchall():
            messages.append(models.Message(*message))
        return messages
            

    def get_user_by_username(self, username: str) -> models.User:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if user is None:
            return None
        return models.User(*user)
    
    
    # on takedown
    def __del__(self):
        self.conn.close()
