# 言い回し変換

入力した日本語の文章を、**関西弁・丁寧語・ギャル語**へ変換する Streamlit アプリです。

## できること

- 文章の意味を保ったまま話し方だけ変換
- 話し方ごとの結果フォント切り替え
- 変換結果のワンクリックコピー
- 入力欄のクリア（✕）

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

プロジェクト直下に `.env` を作成し、Gemini API キーを設定します。

```env
GEMINI_API_KEY=your_api_key_here
```

## 起動

```bash
source .venv/bin/activate
streamlit run app.py
```

ブラウザで http://localhost:8501 を開いてください。

## 構成

| ファイル | 内容 |
|---|---|
| `app.py` | Streamlit UI |
| `tone_converter.py` | Gemini による言い回し変換 |
| `requirements.txt` | 依存パッケージ |
| `.streamlit/config.toml` | テーマ設定 |

## 注意

- `.env` は Git 管理対象外です。API キーをリポジトリに含めないでください。
