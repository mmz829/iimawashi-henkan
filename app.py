import html
import json

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from tone_converter import convert

load_dotenv()

TONE_OPTIONS = {
    "関西弁": "kansai",
    "丁寧語": "business",
    "ギャル語": "gyaru",
}

st.set_page_config(
    page_title="言い回し変換",
    page_icon="🗣️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_tone" not in st.session_state:
    st.session_state.last_tone = None

# ウィジェット生成前にクリアする（生成後の書き換えはエラーになる）
if st.session_state.pop("pending_clear", False):
    st.session_state.input_text = ""


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hachi+Maru+Pop&family=Kaisei+Decol:wght@500;700&family=Shippori+Mincho:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap');

    :root {
        --ink: #1b2430;
        --ink-soft: #667484;
        --panel: #ffffff;
        --line: rgba(27, 36, 48, 0.1);
        --accent: #3f5e8a;
        --accent-deep: #314a6d;
        --accent-soft: rgba(63, 94, 138, 0.14);
        --choice: #b85c57;
        --choice-deep: #9a4a46;
        --choice-soft: rgba(184, 92, 87, 0.16);
        --shadow: 0 16px 40px rgba(27, 36, 48, 0.06);
    }

    .stApp {
        background:
            radial-gradient(ellipse 70% 45% at 50% -8%, rgba(63, 94, 138, 0.1), transparent 60%),
            linear-gradient(180deg, #f7f8fa 0%, #eef1f5 100%);
        color: var(--ink);
        font-family: "Zen Kaku Gothic New", "Hiragino Sans", sans-serif;
    }

    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="InputInstructions"] {
        display: none !important;
    }

    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 4rem !important;
        max-width: 720px;
    }

    .hero {
        text-align: center;
        margin-bottom: 2rem;
        animation: rise 0.7s ease-out both;
    }

    .brand {
        position: relative;
        display: inline-block;
        font-family: "Kaisei Decol", "Hiragino Mincho ProN", serif;
        font-size: clamp(2.55rem, 6.5vw, 3.45rem);
        font-weight: 700;
        letter-spacing: 0.18em;
        color: var(--ink);
        margin: 0;
        line-height: 1.2;
        padding: 0 0.08em 0.4em 0.18em;
    }

    .brand span {
        color: var(--accent);
    }

    .brand::after {
        content: "";
        position: absolute;
        left: 50%;
        bottom: 0.08rem;
        width: 2.4rem;
        height: 2px;
        border-radius: 999px;
        background: var(--accent);
        opacity: 0.55;
        transform: translateX(-50%);
    }

    div[data-testid="stForm"] {
        background: var(--panel);
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        padding: 1.55rem 1.45rem 1.3rem !important;
        box-shadow: var(--shadow);
        animation: rise 0.85s ease-out 0.08s both;
    }

    div[data-testid="stWidgetLabel"] {
        display: none !important;
    }

    .field-label {
        margin: 0 0 0.55rem;
        font-family: "Zen Kaku Gothic New", "Hiragino Sans", sans-serif;
        font-size: 0.98rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--ink);
        line-height: 1.3;
    }

    .field-label-tone {
        margin-top: -0.55rem !important;
        margin-bottom: 0.55rem;
    }

    div[data-testid="stTextArea"] {
        position: relative !important;
        margin-bottom: 0.35rem !important;
    }

    div[data-testid="stTextArea"] textarea {
        background: #fafbfc !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        color: var(--ink) !important;
        font-family: "Zen Kaku Gothic New", sans-serif !important;
        font-size: 1.02rem !important;
        line-height: 1.7 !important;
        padding: 1rem 2.8rem 1rem 1.1rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(63, 94, 138, 0.45) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }

    div[data-testid="stRadio"] {
        margin-bottom: 1.15rem !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.65rem;
    }

    div[data-testid="stRadio"] [role="radiogroup"] > label {
        background: #fafbfc;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.85rem 0.55rem !important;
        margin: 0 !important;
        justify-content: center;
        transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }

    div[data-testid="stRadio"] [role="radiogroup"] > label:hover {
        transform: translateY(-1px);
        border-color: rgba(63, 94, 138, 0.4);
    }

    div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) {
        border-color: var(--accent);
        background: #f3f6fb;
        box-shadow: 0 8px 18px var(--accent-soft);
    }

    div[data-testid="stRadio"] input[type="radio"] {
        accent-color: var(--choice) !important;
    }

    div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
        border-color: rgba(184, 92, 87, 0.4) !important;
    }

    div[data-testid="stRadio"] [data-baseweb="radio"] input:checked + div,
    div[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child[data-checked="true"] {
        background-color: var(--choice) !important;
        border-color: var(--choice) !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] p {
        font-weight: 700 !important;
        letter-spacing: 0.06em;
        color: var(--ink) !important;
        text-align: center;
    }

    div[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) p {
        color: var(--accent-deep) !important;
    }

    /* クリア用ボタンの見た目（位置はJSでテキストエリア内へ） */
    button[data-testid="stBaseButton-secondaryFormSubmit"] {
        width: 1.85rem !important;
        height: 1.85rem !important;
        min-height: 1.85rem !important;
        padding: 0 !important;
        border-radius: 999px !important;
        border: 1px solid var(--line) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        background-image: none !important;
        color: var(--ink-soft) !important;
        box-shadow: 0 2px 8px rgba(27, 36, 48, 0.06) !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        letter-spacing: 0 !important;
    }

    button[data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        transform: none !important;
        background: #f3f6fb !important;
        color: var(--accent-deep) !important;
        border-color: rgba(63, 94, 138, 0.35) !important;
        filter: none !important;
        box-shadow: 0 2px 8px rgba(27, 36, 48, 0.06) !important;
    }

    button[data-testid="stBaseButton-secondaryFormSubmit"] p {
        color: inherit !important;
    }

    div[data-testid="stForm"] button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] {
        width: 100% !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.95rem 1.4rem !important;
        background: var(--accent) !important;
        background-image: none !important;
        color: #ffffff !important;
        font-family: "Zen Kaku Gothic New", sans-serif !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        box-shadow: 0 10px 24px var(--accent-soft) !important;
    }

    div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover,
    div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: var(--accent-deep) !important;
        color: #ffffff !important;
    }

    div[data-testid="stForm"] button[kind="primaryFormSubmit"] p,
    div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"] p {
        color: #ffffff !important;
    }

    .result-card {
        margin-top: 1.35rem;
        padding: 1.35rem 1.4rem 1.25rem;
        border-radius: 16px;
        background: #ffffff;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        animation: rise 0.55s ease-out both;
    }

    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        margin-bottom: 0.8rem;
    }

    .result-label {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--accent-deep);
    }

    .result-label::before {
        content: "";
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 50%;
        background: var(--accent);
        box-shadow: 0 0 0 4px var(--accent-soft);
    }

    .result-text {
        font-size: 1.16rem;
        line-height: 1.95;
        letter-spacing: 0.03em;
        color: var(--ink);
        white-space: pre-wrap;
        word-break: break-word;
    }

    .result-text-kansai {
        font-family: "Kaisei Decol", "Hiragino Mincho ProN", serif;
    }

    .result-text-business {
        font-family: "Shippori Mincho", "Hiragino Mincho ProN", "Yu Mincho", serif;
        font-size: 1.14rem;
        line-height: 2;
        letter-spacing: 0.06em;
    }

    .result-text-gyaru {
        font-family: "Hachi Maru Pop", "Hiragino Maru Gothic ProN", sans-serif;
        font-size: 1.2rem;
        line-height: 1.9;
        letter-spacing: 0.08em;
    }

    div.copy-row .stButton > button {
        width: auto !important;
        min-height: 2rem !important;
        padding: 0.3rem 0.9rem !important;
        border-radius: 999px !important;
        border: 1px solid var(--line) !important;
        background: #fafbfc !important;
        background-image: none !important;
        color: var(--accent-deep) !important;
        box-shadow: none !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
    }

    div.copy-row .stButton > button:hover {
        transform: none !important;
        background: #f3f6fb !important;
        border-color: rgba(63, 94, 138, 0.35) !important;
        color: var(--accent-deep) !important;
        filter: none !important;
        box-shadow: none !important;
    }

    div.copy-row .stButton > button p {
        color: inherit !important;
    }

    .stAlert {
        border-radius: 12px !important;
    }

    @keyframes rise {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 640px) {
        div[data-testid="stRadio"] [role="radiogroup"] {
            grid-template-columns: 1fr;
        }

        div[data-testid="stForm"] {
            padding: 1.15rem 1rem 1.05rem !important;
            border-radius: 16px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1 class="brand">言い回し<span>変換</span></h1>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("convert_form", border=False, enter_to_submit=False):
    st.markdown(
        '<div class="field-label field-label-input">変換したい文章</div>',
        unsafe_allow_html=True,
    )
    text = st.text_area(
        "変換したい文章",
        height=170,
        placeholder="例）我輩は猫である。名前はまだ無い。",
        label_visibility="collapsed",
        key="input_text",
    )
    cleared = st.form_submit_button("✕")

    st.markdown(
        '<div class="field-label field-label-tone">話し方</div>',
        unsafe_allow_html=True,
    )
    tone_label = st.radio(
        "話し方",
        list(TONE_OPTIONS.keys()),
        horizontal=True,
        label_visibility="collapsed",
    )

    submitted = st.form_submit_button(
        "変換する",
        use_container_width=True,
        type="primary",
    )

# ✕ をテキストエリア右上へ移動（レイアウトは崩さない）
components.html(
    """
    <script>
    (() => {
      const doc = window.parent.document;
      const placeClearButton = () => {
        const area = doc.querySelector('[data-testid="stForm"] [data-testid="stTextArea"]');
        if (!area) return;
        const buttons = Array.from(doc.querySelectorAll('[data-testid="stForm"] button'));
        const clearBtn = buttons.find((b) => (b.textContent || "").trim() === "✕");
        if (!clearBtn) return;
        const host = clearBtn.closest('[data-testid="element-container"]') || clearBtn.parentElement;
        if (!host || host.dataset.inTextarea === "1") return;
        area.style.position = "relative";
        host.dataset.inTextarea = "1";
        host.style.position = "absolute";
        host.style.top = "10px";
        host.style.right = "10px";
        host.style.width = "auto";
        host.style.margin = "0";
        host.style.zIndex = "40";
        area.appendChild(host);
      };
      placeClearButton();
      setTimeout(placeClearButton, 50);
      setTimeout(placeClearButton, 200);
    })();
    </script>
    """,
    height=0,
    width=0,
)

if cleared:
    st.session_state.pending_clear = True
    st.rerun()

if submitted:
    if not text.strip():
        st.warning("文章を入力してください。")
        st.session_state.last_result = None
        st.session_state.last_tone = None
    else:
        with st.spinner("言葉のトーンを整えています…"):
            try:
                result = convert(text, TONE_OPTIONS[tone_label])
            except Exception as e:
                st.error(f"変換に失敗しました: {e}")
                st.session_state.last_result = None
                st.session_state.last_tone = None
            else:
                st.session_state.last_result = result
                st.session_state.last_tone = tone_label

if st.session_state.last_result and st.session_state.last_tone:
    tone_name = st.session_state.last_tone
    tone_key = TONE_OPTIONS[tone_name]
    result = st.session_state.last_result
    safe_result = html.escape(result).replace("\n", "<br>")
    copy_payload = json.dumps(result, ensure_ascii=False)
    line_count = max(1, result.count("\n") + 1)
    card_height = min(480, max(170, 100 + line_count * 38 + len(result) // 24))

    components.html(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Hachi+Maru+Pop&family=Kaisei+Decol:wght@500;700&family=Shippori+Mincho:wght@500;700&family=Zen+Kaku+Gothic+New:wght@400;500;700&display=swap');
          html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: "Zen Kaku Gothic New", "Hiragino Sans", sans-serif;
            color: #1b2430;
          }}
          .result-card {{
            box-sizing: border-box;
            margin-top: 0.4rem;
            padding: 1.2rem 1.25rem 1.15rem;
            border-radius: 16px;
            background: #ffffff;
            border: 1px solid rgba(27, 36, 48, 0.1);
            box-shadow: 0 16px 40px rgba(27, 36, 48, 0.06);
          }}
          .result-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
          }}
          .result-label {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-size: 0.9rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: #314a6d;
          }}
          .result-label::before {{
            content: "";
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 50%;
            background: #3f5e8a;
            box-shadow: 0 0 0 4px rgba(63, 94, 138, 0.14);
          }}
          .copy-btn {{
            border: 1px solid rgba(27, 36, 48, 0.1);
            border-radius: 999px;
            background: #fafbfc;
            color: #314a6d;
            font-family: "Zen Kaku Gothic New", sans-serif;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            padding: 0.35rem 0.85rem;
            cursor: pointer;
          }}
          .copy-btn:hover {{ background: #f3f6fb; }}
          .copy-btn.copied {{
            background: #3f5e8a;
            border-color: #3f5e8a;
            color: #fff;
          }}
          .result-text {{
            font-size: 1.16rem;
            line-height: 1.95;
            letter-spacing: 0.03em;
            word-break: break-word;
          }}
          .result-text-kansai {{
            font-family: "Kaisei Decol", "Hiragino Mincho ProN", serif;
          }}
          .result-text-business {{
            font-family: "Shippori Mincho", "Hiragino Mincho ProN", "Yu Mincho", serif;
            font-size: 1.14rem;
            line-height: 2;
            letter-spacing: 0.06em;
          }}
          .result-text-gyaru {{
            font-family: "Hachi Maru Pop", "Hiragino Maru Gothic ProN", sans-serif;
            font-size: 1.2rem;
            line-height: 1.9;
            letter-spacing: 0.08em;
          }}
        </style>
        <div class="result-card">
          <div class="result-header">
            <div class="result-label">変換結果 · {html.escape(tone_name)}</div>
            <button type="button" class="copy-btn" id="copy-btn">コピー</button>
          </div>
          <div class="result-text result-text-{tone_key}">{safe_result}</div>
        </div>
        <script>
          const btn = document.getElementById("copy-btn");
          const text = {copy_payload};
          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText(text);
              btn.textContent = "コピー済み";
              btn.classList.add("copied");
              setTimeout(() => {{
                btn.textContent = "コピー";
                btn.classList.remove("copied");
              }}, 1600);
            }} catch (e) {{
              btn.textContent = "失敗";
              setTimeout(() => {{ btn.textContent = "コピー"; }}, 1600);
            }}
          }});
        </script>
        """,
        height=card_height,
        scrolling=True,
    )
