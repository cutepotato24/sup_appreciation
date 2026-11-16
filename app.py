"""Surprise appreciation site for our supervisor, built with Streamlit."""

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from book_html import build_book_html
from pdf_builder import build_pdf

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
MESSAGES_PATH = BASE_DIR / "messages.json"
AUDIO_PATH = BASE_DIR / "salamat.mp3"

PAGE_CSS = """
<style>
.stApp { background: #E7D1D4; color: #50383D; }
[data-testid="stAudio"], .stAudio {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
.block-container {
    max-width: 100vw;
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 2rem;
}
.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    margin: 0.5rem 0 0.2rem 0;
    color: #75434D;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #98616A;
    margin-bottom: 1.5rem;
}
div.stButton > button, div.stDownloadButton > button {
    border-radius: 4px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
    border: 1px solid #B4777E;
    color: #75434D;
    background: #F1DBDC;
    box-shadow: 0 3px 8px rgba(104, 65, 72, 0.16);
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    color: #50383D;
    border-color: #89515B;
    transform: translateY(-2px);
}
</style>
"""

st.set_page_config(page_title="A Little Surprise", page_icon="🎉", layout="wide")


def load_json(path: Path) -> Any:
    """Load a JSON file."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    """Run the app."""
    config = load_json(CONFIG_PATH)
    config["title"] = config["title"].replace("[Supervisor's Name]", "Stal")
    messages = load_json(MESSAGES_PATH)

    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    if "opened" not in st.session_state:
        st.session_state.opened = False

    if not st.session_state.opened:
        st.markdown(f"<div class='hero-title'>🎉 {html.escape(config['title'])} 🎉</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hero-subtitle'>{html.escape(config['subtitle'])}</div>", unsafe_allow_html=True)
        _, middle, _ = st.columns([1, 2, 1])
        if middle.button("🎁 Open your surprise", use_container_width=True):
            st.session_state.opened = True
            st.balloons()
            st.rerun()
        return

    st.audio(str(AUDIO_PATH), format="audio/mp3", autoplay=True, loop=True)

    # The whole book (cover, pages, flipping, full screen) lives in one HTML component.
    components.html(build_book_html(config, messages, BASE_DIR), height=800, scrolling=False)
    st.caption("Click the right page (or → key) to turn forward, the left page (or ← key) to go back.")

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
