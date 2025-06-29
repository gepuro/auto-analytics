import json
import os

from google import genai
from google.genai import types


def gemini(contents, model, max_output_tokens):
    """
    Google Gemini APIを使用して、コンテンツを生成する関数
    """
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    for i in range(5):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=i * 0.1,  # 失敗したら、temperatureを0.1大きくする
                    candidate_count=1,
                    max_output_tokens=max_output_tokens,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {"response": {"type": "STRING"}},
                    },
                ),
            )
            return json.loads(response.candidates[0].content.parts[0].text)["response"]
        except:
            continue
    raise Exception(f"Geminiで{i+1}回リトライしても結果を得られません")
