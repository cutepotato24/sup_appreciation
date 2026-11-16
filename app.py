"""Surprise appreciation site for our supervisor, built with Streamlit."""
 
import html

import json

from pathlib import Path

from typing import Any
 
import streamlit as st

import streamlit.components.v1 as components
 
from book_html import build_book_html

from book_pdf import build_book_pdf
 
BASE_DIR = Path(__file__).parent

CONFIG_PATH = BASE_DIR / "config.json"

MESSAGES_PATH = BASE_DIR / "messages.json"

AUDIO_PATH = BASE_DIR / "salamat.mp3"
 
PAGE_CSS = """
<style>

.stApp { background: #E7D1D4; color: #50383D; }

[data-testid="stAudio"], .stAudio {

    position: absolute !important; width: 1px !important; height: 1px !important;

    overflow: hidden !important; opacity: 0 !important; pointer-events: none !important;

}

.block-container { max-width: 100vw; padding-left: 1rem; padding-right: 1rem; padding-top: 2rem; }

.hero-title { text-align: center; font-size: 3.2rem; font-weight: 800; margin: 0.5rem 0 0.2rem 0; color: #75434D; }

.hero-subtitle { text-align: center; font-size: 1.3rem; color: #98616A; margin-bottom: 1.5rem; }

div.stButton > button, div.stDownloadButton > button {

    border-radius: 4px; font-weight: 700; font-size: 1rem; padding: 0.6rem 1.2rem;

    border: 1px solid #B4777E; color: #75434D; background: #F1DBDC;

    box-shadow: 0 3px 8px rgba(104, 65, 72, 0.16);

}

div.stButton > button:hover, div.stDownloadButton > button:hover {

    color: #50383D; border-color: #89515B; transform: translateY(-2px);

}
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
 
 
@st.cache_data(show_spinner="Preparing the print-ready PDF…")

def make_print_pdf(book_doc: str) -> bytes | None:

    """Render the book to a PDF once and reuse it on later reruns."""

    return build_book_pdf(book_doc)
 
 
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

    book_doc = build_book_html(config, messages, BASE_DIR)

    components.html(book_doc, height=800, scrolling=False)

    st.caption("Click the right page (or → key) to turn forward, the left page (or ← key) to go back. For a PDF, use the 📄 Save as PDF button under the book and tick \"Background graphics\".")
 
    # Standalone copy of the book: a single .html file that opens in any browser, offline.

    standalone = book_doc.replace(

        "</head>", "<style>html,body{background:#B58C94}#wrap{border-radius:0}</style></head>", 1

    )

    _, middle, _ = st.columns([1, 2, 1])

    middle.download_button(

        "📖 Download the book (open in any browser)",

        data=standalone,

        file_name="book-for-stal.html",

        mime="text/html",

        use_container_width=True,

    )

    print_pdf = make_print_pdf(book_doc)

    if print_pdf:

        middle.download_button(

            "🖨️ Download print-ready PDF",

            data=print_pdf,

            file_name="book-for-stal.pdf",

            mime="application/pdf",

            use_container_width=True,

        )

    else:

        st.caption(

            "Print-ready PDF unavailable: run `pip install playwright` and `playwright install chromium`, "

            "or use the 📄 Save as PDF button under the book."

        )

    if middle.button("🎈 More balloons!", use_container_width=True):

        st.balloons()
 
 
main()
 