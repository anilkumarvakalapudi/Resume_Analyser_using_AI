import os
import re
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": str(system_prompt)},
            {"role": "user", "content": str(user_prompt)}
        ]
    )

    content = response.choices[0].message.content

    match = re.search(r"\{.*\}", content, re.DOTALL)
    return match.group(0) if match else content
