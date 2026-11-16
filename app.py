"""Surprise appreciation site for our supervisor, built with Streamlit."""

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

from cath_message import CATH_MESSAGE
from pdf_builder import build_pdf

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
MESSAGES_PATH = BASE_DIR / "messages.json"
AUDIO_PATH = BASE_DIR / "salamat.mp3"

CARD_ACCENTS = ["#9F1239", "#BE123C", "#881337", "#B4233C", "#A61B3B", "#7F1D35"]
CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]

PAGE_CSS = """
<style>
.stApp, .stApp * {
    font-style: italic !important;
}
.stApp {
    background: #FFF1F2;
    color: #4C1D25;
}
.block-container {
    max-width: 100%;
    padding-left: 2rem;
    padding-right: 2rem;
}
.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    margin: 0.5rem 0 0.2rem 0;
    color: #7F1D35;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #9F3048;
    margin-bottom: 1.5rem;
}
.intro-box {
    background: #FCE4E7;
    border-left: 6px solid #BE123C;
    border-radius: 6px;
    padding: 1rem 1.4rem;
    font-size: 1.1rem;
    color: #5B1F2A;
    margin: 1rem 0 1.5rem 0;
    box-shadow: inset 0 0 22px rgba(159, 18, 57, 0.06);
}
.section-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #9F1239;
    margin: 1.5rem 0 1rem 0;
}
.msg-card {
    padding: 1.3rem 1.5rem;
    border: 1px solid #F3B9C4;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    background: #FFF7F7;
    box-shadow: 0 5px 14px rgba(127, 29, 53, 0.12);
    animation: pop 0.6s ease both;
}
.msg-text { font-size: 1.1rem; line-height: 1.65; color: #4C1D25; }
.msg-author { margin-top: 0.9rem; font-weight: 700; text-align: right; font-size: 1.05rem; }
.closing {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #9F3048;
    margin: 1.5rem 0;
}
div.stButton > button {
    border-radius: 4px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
    border: 1px solid #BE123C;
    color: #7F1D35;
    background: #FCE4E7;
    box-shadow: 0 3px 8px rgba(127, 29, 53, 0.12);
}
div.stButton > button:hover { color: #5B1F2A; border-color: #881337; transform: translateY(-2px); }
@keyframes pop { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: none; } }
</style>
"""

st.set_page_config(page_title="A Little Surprise", page_icon="🎉", layout="wide")


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
    accent = CARD_ACCENTS[index % len(CARD_ACCENTS)]
    emoji = CARD_EMOJIS[index % len(CARD_EMOJIS)]
    safe_message = html.escape(message).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="msg-card" style="animation-delay:{index * 0.1}s;">
            <div class="msg-text">{safe_message}</div>
            <div class="msg-author" style="color:{accent};">{emoji} {html.escape(author)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the app."""
    config = load_json(CONFIG_PATH)
    config["title"] = config["title"].replace("[Supervisor's Name]", "Stal")
    messages = load_json(MESSAGES_PATH)
    messages.append(CATH_MESSAGE)

    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.audio(str(AUDIO_PATH), format="audio/mp3", autoplay=True, loop=True)
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
