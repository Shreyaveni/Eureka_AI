import os
import openai
from groq import Groq
from config import groq_api_key

client = Groq(api_key=groq_api_key)
completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": "generate a sick leave mail to manager"
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")

print(completion)
