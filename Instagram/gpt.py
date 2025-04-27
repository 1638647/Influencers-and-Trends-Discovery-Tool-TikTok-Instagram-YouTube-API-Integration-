import time
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar la clave API desde .env
os.environ.pop("OPENAI_API_KEY", None)

load_dotenv()
API = os.getenv("OPENAI_API_KEY")

def GPT(promt):
    assistant_id = "asst_786gGKLoOv2AqRAt78JkUAsR"
    assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": promt
            }
        ],
    )
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
    time.sleep(20)  
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

client = OpenAI(api_key=API)
