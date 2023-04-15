import os
from typing import List
from utils.crawler import Crawler
from utils.orm import ORM
import utils.models as models


def reply_function(messages: List[models.Message]) -> str:
    return messages[-1].message + " to you too :) " + messages[-1].sender

def main():
    connection_str = f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
    orm = ORM(connection_str)
    
    crawler = Crawler(headless=True)
    # result = crawler.send_message("deliapro99", "Hello from instagram bot 2")
    recent_messages_from_usernames = crawler.get_any_recent_messages(reply_fn=reply_function)
    for recent_messages_from_username in recent_messages_from_usernames:
        orm.insert_messages(recent_messages_from_username)
    
        

if __name__ == "__main__":
    main()