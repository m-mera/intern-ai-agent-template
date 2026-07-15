import os
import json
import requests

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL")

if not API_KEY:
    raise ValueError(
        "AZURE_OPENAI_API_KEY が設定されていません。Codespaces Secretを確認してください。"
    )

if not ENDPOINT:
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT が設定されていません。Codespaces Secretを確認してください。"
    )

if not MODEL_NAME:
    raise ValueError(
        "AZURE_OPENAI_MODEL が設定されていません。Codespaces Secretを確認してください。"
    )

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

INSTRUCTIONS = """
あなたはHealthy Life Agentです。

# 目的
毎日の生活を少しでも健康的にしたい人を支援する。

# 対象
健康を意識したい学生

# できること
- 睡眠改善
- 食生活改善
- 運動習慣改善
- 健康管理のアドバイス

# 回答ルール
- 分かりやすい日本語で回答する
- 学生でも実践しやすい内容を提案する
- できるだけ手軽に始められる内容にする
- 医療的な診断はしない
- 強い症状や体調不良がある場合は、医療機関への相談を促す
"""


def extract_assistant_message(response_json):
    assistant_message = ""

    for item in response_json.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    assistant_message += content.get("text", "")

    return assistant_message


def get_response(message):
    payload = {"model": MODEL_NAME, "instructions": INSTRUCTIONS, "input": message}

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)

        response.raise_for_status()

    except requests.RequestException as e:
        error_body = ""

        if "response" in locals():
            error_body = response.text

        return f"エラーが発生しました: {e}\n{error_body}"

    response_json = response.json()

    assistant_message = extract_assistant_message(response_json)

    if assistant_message == "":
        return "回答文を取得できませんでした。レスポンス内容:\n" + json.dumps(
            response_json, indent=2, ensure_ascii=False
        )

    return assistant_message


if __name__ == "__main__":
    print("Healthy Life Agent を開始します。終了する場合は exit と入力してください。")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        print("AI Assistant:", get_response(user_input))
