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

CARD_ACCENTS = ["#805A36", "#745334", "#657044", "#8A5738", "#62573A", "#7A4F3A"]
CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]

PAGE_CSS = """
<style>
.stApp {
    background-color: #FFF4D8;
    background-image:
        repeating-linear-gradient(135deg, rgba(255, 111, 97, 0.09) 0, rgba(255, 111, 97, 0.09) 2px, transparent 2px, transparent 34px),
        linear-gradient(125deg, #FFF1CB 0%, #F9DDE0 34%, #DDF0F2 68%, #E0EFD8 100%);
    color: #463722;
}
.hero-title {
    text-align: center;
    font-size: 3.2rem;
    font-weight: 800;
    margin: 0.5rem 0 0.2rem 0;
    color: #4F3923;
    font-family: Georgia, "Times New Roman", serif;
}
.hero-subtitle {
    text-align: center;
    font-size: 1.3rem;
    color: #70573A;
    margin-bottom: 1.5rem;
}
.intro-box {
    background: linear-gradient(135deg, #F8EED8, #E9D7B5);
    border-left: 6px solid #A0784D;
    border-radius: 6px;
    padding: 1rem 1.4rem;
    font-size: 1.1rem;
    color: #463722;
    margin: 1rem 0 1.5rem 0;
    box-shadow: inset 0 0 22px rgba(114, 81, 43, 0.08);
}
.section-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #62472B;
    margin: 1.5rem 0 1rem 0;
    font-family: Georgia, "Times New Roman", serif;
}
.envelope-panel {
    text-align: center;
    background: rgba(248, 238, 216, 0.82);
    border: 1px solid #B49368;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin: 1rem 0;
    box-shadow: inset 0 0 20px rgba(114, 81, 43, 0.08);
}
.envelope-icon { font-size: 2.8rem; line-height: 1.2; }
.envelope-label { color: #684F32; font-size: 1.05rem; font-weight: 700; }
.msg-card {
    padding: 1.3rem 1.5rem;
    border: 1px solid #B49368;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    background-color: #F3E7CE;
    background-image:
        repeating-linear-gradient(0deg, rgba(94, 65, 34, 0.035) 0, rgba(94, 65, 34, 0.035) 1px, transparent 1px, transparent 5px),
        linear-gradient(135deg, #FBF3DF, #E9D6B2);
    box-shadow: 0 5px 14px rgba(74, 54, 29, 0.16), inset 0 0 24px rgba(114, 81, 43, 0.08);
    animation: pop 0.6s ease both;
}
.msg-text { font-size: 1.1rem; line-height: 1.65; color: #463722; }
.msg-author { margin-top: 0.9rem; font-weight: 700; text-align: right; font-size: 1.05rem; }
.closing {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #705136;
    margin: 1.5rem 0;
    font-family: Georgia, "Times New Roman", serif;
}
div.stButton > button {
    border-radius: 4px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
    border: 1px solid #9B774E;
    color: #4E3923;
    background: linear-gradient(180deg, #F8EED8, #E6D1AA);
    box-shadow: 0 3px 8px rgba(74, 54, 29, 0.16);
}
div[class*="st-key-open_message_"] button {
    min-height: 104px;
    border-color: #9B7448;
    background:
        linear-gradient(147deg, transparent 49%, rgba(126, 83, 42, 0.32) 50%, transparent 51%) left bottom / 50% 62% no-repeat,
        linear-gradient(213deg, transparent 49%, rgba(126, 83, 42, 0.32) 50%, transparent 51%) right bottom / 50% 62% no-repeat,
        linear-gradient(180deg, #FBF2DF, #E6D0A8);
    box-shadow: 0 4px 10px rgba(74, 54, 29, 0.2), inset 0 0 14px rgba(114, 81, 43, 0.08);
    font-family: Georgia, "Times New Roman", serif;
}
div.stButton > button:hover { color: #352516; border-color: #765432; transform: translateY(-2px); }
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


@st.dialog("A message for Stal")
def show_message_dialog(author: str, message: str, index: int) -> None:
    render_card(author, message, index)
    if st.button("Close message", key=f"close_message_{index}", use_container_width=True):
        st.session_state.selected_message = None
        st.rerun()


def main() -> None:
    """Run the app."""
    config = load_json(CONFIG_PATH)
    config["title"] = config["title"].replace("[Supervisor's Name]", "Stal")
    messages = load_json(MESSAGES_PATH)
    messages.append(CATH_MESSAGE)

    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='hero-title'>🎉 {html.escape(config['title'])} 🎉</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='hero-subtitle'>{html.escape(config['subtitle'])}</div>", unsafe_allow_html=True)

    if "opened" not in st.session_state:
        st.session_state.opened = False
    if "selected_message" not in st.session_state:
        st.session_state.selected_message = None

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
    st.markdown(
        "<div class='envelope-panel'><div class='envelope-icon'>✉️</div>"
        "<div class='envelope-label'>Choose an envelope to open</div></div>",
        unsafe_allow_html=True,
    )
    for row_start in range(0, len(messages), 2):
        columns = st.columns(2)
        for column, index in zip(columns, range(row_start, min(row_start + 2, len(messages)))):
            item = messages[index]
            with column:
                if st.button(
                    f"✉️ Open {item['name']}'s message",
                    key=f"open_message_{index}",
                    use_container_width=True,
                ):
                    st.session_state.selected_message = index
                    st.rerun()

    selected_message = st.session_state.selected_message
    if selected_message is not None and 0 <= selected_message < len(messages):
        item = messages[selected_message]
        show_message_dialog(item["name"], item["message"], selected_message)

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
