import os
import openai

class OpenAIApi:
    def __init__(self, user_name:str="AI's user", openai_api_key:str=None):
        if openai_api_key is None:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        self.user_name = user_name
        
    def chat_response(self, system_message:str, user_message:str) -> str:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_message},
                        {"role": "user", "content": user_message},
                    ]
            )
        
        return response['choices'][0]['message']['content']
        