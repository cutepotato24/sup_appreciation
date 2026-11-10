"""Surprise appreciation site for our supervisor, built with Streamlit."""

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

from pdf_builder import build_pdf

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
MESSAGES_PATH = BASE_DIR / "messages.json"

# (background gradient start, end, accent colour) for each message card.
CARD_STYLES = [
    ("#FF9A9E", "#FAD0C4", "#C2185B"),
    ("#A18CD1", "#FBC2EB", "#5E35B1"),
    ("#84FAB0", "#8FD3F4", "#00695C"),
    ("#FDCB6E", "#FF7675", "#BF360C"),
    ("#74EBD5", "#9FACE6", "#1A237E"),
    ("#F6D365", "#FDA085", "#E65100"),
]
CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]

PAGE_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #FFF1EB 0%, #E8F4FF 35%, #F6E8FF 70%, #FFF9DB 100%);
}
.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    margin: 0.5rem 0 0.2rem 0;
    background: linear-gradient(90deg, #FF4D8D, #FF9A3C, #F9D423, #37D67A, #2CB5E8, #8E54E9);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 6s linear infinite;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #5C4B8A;
    margin-bottom: 1.5rem;
}
.intro-box {
    background: rgba(255, 255, 255, 0.75);
    border-left: 8px solid #FF4D8D;
    border-radius: 16px;
    padding: 1rem 1.4rem;
    font-size: 1.1rem;
    color: #2B2B2B;
    margin: 1rem 0 1.5rem 0;
}
.section-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #8E24AA;
    margin: 1.5rem 0 1rem 0;
}
.msg-card {
    padding: 1.3rem 1.5rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
    animation: pop 0.6s ease both;
}
.msg-text { font-size: 1.1rem; line-height: 1.65; color: #2B2B2B; }
.msg-author { margin-top: 0.9rem; font-weight: 700; text-align: right; font-size: 1.05rem; }
.closing {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #E91E63;
    margin: 1.5rem 0;
}
div.stButton > button {
    border-radius: 999px;
    font-weight: 700;
    font-size: 1.1rem;
    padding: 0.6rem 1.2rem;
    border: none;
    color: white;
    background: linear-gradient(90deg, #FF4D8D, #FF9A3C);
    box-shadow: 0 4px 14px rgba(255, 77, 141, 0.45);
}
div.stButton > button:hover { color: white; transform: scale(1.04); }
@keyframes shine { to { background-position: 200% center; } }
@keyframes pop { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: none; } }
</style>
"""

st.set_page_config(page_title="A Little Surprise", page_icon="🎉", layout="centered")


def load_json(path: Path) -> Any:
    """Load a JSON file.

    Parameters
    ----------
    path : Path
        Location of the JSON file.

    Returns
    -------
    Any
        Parsed JSON content.
    """
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def render_card(author: str, message: str, index: int) -> None:
    """Render a single team message as a colourful card.

    Parameters
    ----------
    author : str
        Name of the teammate.
    message : str
        Message text (HTML is escaped; line breaks are preserved).
    index : int
        Position of the message, used to pick the card colours and emoji.
    """
    start, end, accent = CARD_STYLES[index % len(CARD_STYLES)]
    emoji = CARD_EMOJIS[index % len(CARD_EMOJIS)]
    safe_message = html.escape(message).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="msg-card" style="background:linear-gradient(135deg,{start},{end});animation-delay:{index * 0.1}s;">
            <div class="msg-text">{safe_message}</div>
            <div class="msg-author" style="color:{accent};">{emoji} {html.escape(author)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the app."""
    config = load_json(CONFIG_PATH)
    messages = load_json(MESSAGES_PATH)

    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='hero-title'>🎉 {html.escape(config['title'])} 🎉</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-subtitle'>{html.escape(config['subtitle'])}</div>", unsafe_allow_html=True)

    if "opened" not in st.session_state:
        st.session_state.opened = False

    if not st.session_state.opened:
        _, middle, _ = st.columns([1, 2, 1])
        if middle.button("🎁 Open your surprise", use_container_width=True):
            st.session_state.opened = True
            st.balloons()
            st.rerun()
        return

    st.markdown(f"<div class='intro-box'>{html.escape(config['intro'])}</div>", unsafe_allow_html=True)

    photo = config.get("photo")
    if photo and (BASE_DIR / photo).exists():
        st.image(str(BASE_DIR / photo), use_container_width=True)

    st.markdown(f"<div class='section-title'>💌 Messages from the team ({len(messages)})</div>", unsafe_allow_html=True)
    for index, item in enumerate(messages):
        render_card(item["name"], item["message"], index)

    st.markdown(f"<div class='closing'>{html.escape(config['closing'])}</div>", unsafe_allow_html=True)
    _, middle, _ = st.columns([1, 2, 1])
    middle.download_button(
        "📄 Download your messages (PDF)",
        data=build_pdf(config, messages),
        file_name="messages-from-the-team.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    if middle.button("🎈 More balloons!", use_container_width=True):
        st.balloons()


main()
