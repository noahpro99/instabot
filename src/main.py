import os
from typing import List
from utils.crawler import Crawler
from utils.orm import ORM
import utils.models as models
from utils.openai_api import OpenAIApi


def reply_function(messages: List[models.Message]) -> str:
    global ai
    
    system_message:str = f"""
    Your job is to respond to messages noah's contacts as the assistant of {ai.user_name} 
    and to make sure that {ai.user_name} is happy with your responses to his contacts since they will not be able to see them.
    Do not repeat yourself at all.
    """
    thread_laid_out:List[str] = [f"{message.sender}: {message.message}\n" for message in messages]
    user_message:str = f"""
    Please respond as if you are my assistant to my contact {messages[-1].sender}.
    Here is a thread that you will be responding to:
    
    {"".join(thread_laid_out)}
    
    Please make sure to respond to {messages[-1].sender} in a way that will make me happy.
    """
    print(f"System message: {system_message}")
    print(f"User message: {user_message}")
    response:str = ai.chat_response(system_message, user_message)
    return response

def main():
    connection_str = f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
    orm = ORM(connection_str)
    global ai
    ai = OpenAIApi(user_name="Noah Provenzano")
    
    crawler = Crawler(headless=False)
    # result = crawler.send_message("deliapro99", "Hello from instagram bot 2")
    while True:
        crawler.wait_for_message(check_delay_s=20)
        recent_messages_from_usernames = crawler.get_any_recent_messages(reply_fn=reply_function)
        for recent_messages_from_username in recent_messages_from_usernames:
            orm.insert_messages(recent_messages_from_username)
    

if __name__ == "__main__":
    main()