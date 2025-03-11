import base64
import os
from google import genai
from google.genai import types

def generate(input_text: str, api_key: str = None):
    # Use provided API key or fallback to environment variable
    client = genai.Client(
        api_key=api_key,
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=input_text
                ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        #response_mime_type="application/json",
    )
    answer = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        answer += chunk.text
        print(chunk.text, end="")
    return answer