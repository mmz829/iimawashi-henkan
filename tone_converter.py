import argparse
import os

import google.generativeai as genai

TONE_PROMPTS = {
    "kansai": "関西弁で、親しみやすく自然な話し言葉に変換してください。",
    "business": "丁寧なビジネス敬語に変換してください。",
    "gyaru": "ギャル語で、明るくカジュアルな若者言葉に変換してください。",
}

SYSTEM_INSTRUCTION_TEMPLATE = """あなたは日本語の文章トーン変換アシスタントです。
ユーザーの入力文を、次の指定トーンに変換してください。
{tone_instruction}

出力は変換後の文章のみとし、説明や前置きは書かないでください。
元の意味は維持してください。
"""


def convert(text: str, tone: str) -> str:
    """入力文を指定トーンに変換して返す。"""
    if tone not in TONE_PROMPTS:
        raise ValueError(f"未対応のトーンです: {tone}")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("環境変数 GEMINI_API_KEY が設定されていません。")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        system_instruction=SYSTEM_INSTRUCTION_TEMPLATE.format(
            tone_instruction=TONE_PROMPTS[tone]
        ),
    )
    response = model.generate_content(text)
    return (response.text or "").strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="文章を指定トーンに変換します。")
    parser.add_argument("text", help="変換したい文章")
    parser.add_argument(
        "--tone",
        choices=sorted(TONE_PROMPTS.keys()),
        default="kansai",
        help="変換先トーン (kansai / business / gyaru)",
    )
    args = parser.parse_args()
    print(convert(args.text, args.tone))


if __name__ == "__main__":
    main()
