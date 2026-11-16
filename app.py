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

CARD_ACCENTS = ["#9B5664", "#A75D68", "#7D4852", "#B06E75", "#80505A", "#986872"]
CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]

PAGE_CSS = """
<style>
.stApp {
    background: #E7D1D4;
    color: #50383D;
}
[data-testid="stAudio"],
.stAudio {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
.block-container {
    width: 100%;
    max-width: 100vw;
    padding-left: 1rem;
    padding-right: 1rem;
}
@media (max-width: 640px) {
    .block-container {
        max-width: 100%;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .book-cover {
        width: 100%;
        padding: 3rem 2rem 3rem 3rem;
    }
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
.intro-box {
    background: #F1DBDC;
    border-left: 6px solid #B4777E;
    border-radius: 6px;
    padding: 1rem 1.4rem;
    font-size: 1.1rem;
    color: #50383D;
    margin: 1rem 0 1.5rem 0;
    box-shadow: inset 0 0 22px rgba(120, 71, 79, 0.08);
}
.section-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #89515B;
    margin: 1.5rem 0 1rem 0;
}
.book-cover {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    width: calc(50vw - 2rem);
    height: clamp(520px, 74vh, 760px);
    margin: 2rem auto;
    padding: 4rem 4rem 4rem 5rem;
    border: 12px double #B4777E;
    border-radius: 12px;
    background: #DDB7BC;
    box-shadow:
        inset 0 0 0 4px #F1DBDC,
        inset 0 0 28px rgba(120, 71, 79, 0.16),
        0 16px 30px rgba(104, 65, 72, 0.22);
    text-align: center;
    animation: coverOpen 0.75s ease both;
}
.book-cover::before {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    left: 18px;
    width: 10px;
    border-left: 2px solid rgba(117, 67, 77, 0.32);
    border-right: 2px solid rgba(117, 67, 77, 0.32);
    background: rgba(120, 71, 79, 0.08);
}
.cover-title {
    color: #75434D;
    font-family: Georgia, "Times New Roman", serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 700;
    line-height: 1.2;
}
.cover-subtitle {
    margin-top: 1.5rem;
    color: #89515B;
    font-size: 1.35rem;
}
.msg-card {
    position: relative;
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    width: 100%;
    height: clamp(520px, 74vh, 760px);
    padding: 1.3rem 1.5rem;
    border: 1px solid #D1A8AC;
    border-radius: 6px;
    margin: 1.4rem 0 1.2rem;
    background-color: #F7E8E6;
    background-image:
        radial-gradient(ellipse at 12% 14%, rgba(255, 255, 255, 0.62), transparent 25%),
        radial-gradient(ellipse at 91% 21%, rgba(147, 79, 88, 0.19), transparent 29%),
        radial-gradient(ellipse at 22% 84%, rgba(146, 89, 95, 0.18), transparent 30%),
        radial-gradient(ellipse at 79% 71%, rgba(255, 255, 255, 0.42), transparent 25%),
        linear-gradient(147deg, transparent 39%, rgba(128, 70, 78, 0.15) 46%, rgba(255, 255, 255, 0.48) 50%, transparent 57%),
        linear-gradient(32deg, transparent 27%, rgba(128, 70, 78, 0.14) 34%, rgba(255, 255, 255, 0.44) 38%, transparent 45%),
        linear-gradient(92deg, transparent 31%, rgba(128, 70, 78, 0.08) 37%, rgba(255, 255, 255, 0.32) 40%, transparent 46%),
        repeating-linear-gradient(2deg, rgba(110, 62, 70, 0.025) 0, transparent 2px, transparent 6px);
    outline: 1px solid rgba(181, 129, 130, 0.2);
    outline-offset: -6px;
    box-shadow: 0 5px 14px rgba(104, 65, 72, 0.16);
    transform-style: preserve-3d;
    backface-visibility: hidden;
    animation-duration: 0.85s;
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    animation-fill-mode: both;
}
.msg-card.page-left { transform-origin: right center; }
.msg-card.page-right { transform-origin: left center; }
.msg-card.turn-forward.page-left { animation-name: flipForwardLeft; }
.msg-card.turn-forward.page-right { animation-name: flipForwardRight; }
.msg-card.turn-backward.page-left { animation-name: flipBackwardLeft; }
.msg-card.turn-backward.page-right { animation-name: flipBackwardRight; }
.msg-card.turn-forward.page-right,
.msg-card.turn-backward.page-right {
    animation-delay: 0.12s;
}
.photo-tape {
    position: absolute;
    top: -12px;
    left: calc(50% - 44px);
    width: 88px;
    height: 24px;
    background: rgba(218, 175, 177, 0.82);
    border: 1px solid rgba(156, 100, 105, 0.3);
    box-shadow: 0 2px 3px rgba(104, 65, 72, 0.15);
    pointer-events: none;
    z-index: 1;
}
.msg-text {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    font-size: var(--message-font-size, 1rem);
    line-height: 1.38;
    color: #50383D;
    font-style: italic;
}
.msg-author {
    flex-shrink: 0;
    margin-top: 0.9rem;
    font-weight: 700;
    text-align: right;
    font-size: 1.05rem;
}
.page-number {
    flex-shrink: 0;
    margin-top: 0.8rem;
    color: #A0757A;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-align: center;
}
.book-counter {
    text-align: center;
    color: #89515B;
    margin: -0.5rem 0 1rem;
}
.closing {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #89515B;
    margin: 1.5rem 0;
}
div.stButton > button {
    border-radius: 4px;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 1.2rem;
    border: 1px solid #B4777E;
    color: #75434D;
    background: #F1DBDC;
    box-shadow: 0 3px 8px rgba(104, 65, 72, 0.16);
}
div.stButton > button:hover { color: #50383D; border-color: #89515B; transform: translateY(-2px); }
@keyframes flipForwardLeft {
    0% { opacity: 0.15; transform: perspective(1200px) rotateY(100deg); filter: brightness(0.7); }
    55% { opacity: 0.9; transform: perspective(1200px) rotateY(22deg); filter: brightness(0.88); }
    100% { opacity: 1; transform: perspective(1200px) rotateY(0); filter: brightness(1); }
}
@keyframes flipForwardRight {
    0% { opacity: 0.15; transform: perspective(1200px) rotateY(-100deg); filter: brightness(0.7); }
    55% { opacity: 0.9; transform: perspective(1200px) rotateY(-22deg); filter: brightness(0.88); }
    100% { opacity: 1; transform: perspective(1200px) rotateY(0); filter: brightness(1); }
}
@keyframes flipBackwardLeft {
    0% { opacity: 0.15; transform: perspective(1200px) rotateY(-100deg); filter: brightness(0.7); }
    55% { opacity: 0.9; transform: perspective(1200px) rotateY(-22deg); filter: brightness(0.88); }
    100% { opacity: 1; transform: perspective(1200px) rotateY(0); filter: brightness(1); }
}
@keyframes flipBackwardRight {
    0% { opacity: 0.15; transform: perspective(1200px) rotateY(100deg); filter: brightness(0.7); }
    55% { opacity: 0.9; transform: perspective(1200px) rotateY(22deg); filter: brightness(0.88); }
    100% { opacity: 1; transform: perspective(1200px) rotateY(0); filter: brightness(1); }
}
@keyframes coverOpen {
    from { opacity: 0; transform: perspective(1200px) rotateY(-12deg) translateX(-12px); }
    to { opacity: 1; transform: perspective(1200px) rotateY(0) translateX(0); }
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


def render_card(author: str, message: str, index: int, turn_direction: str, page_position: int) -> None:
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
    tape_rotation = [-3, 2, -1, 3][index % 4]
    page_side = "left" if page_position == 0 else "right"
    estimated_length = len(message) + 25 * message.count("\n")
    font_size = min(1.1, max(0.75, 32 / max(1, estimated_length) ** 0.5))
    safe_message = html.escape(message).replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="msg-card turn-{turn_direction} page-{page_side}" style="--message-font-size:{font_size:.2f}rem;">
            <div class="photo-tape" style="transform: rotate({tape_rotation}deg);"></div>
            <div class="msg-text">{safe_message}</div>
            <div class="msg-author" style="color:{accent};">{emoji} {html.escape(author)}</div>
            <div class="page-number">Page {index + 1}</div>
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

    if "opened" not in st.session_state:
        st.session_state.opened = False
    if "current_spread" not in st.session_state:
        st.session_state.current_spread = -1
    if "turn_direction" not in st.session_state:
        st.session_state.turn_direction = "forward"
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
    if st.session_state.current_spread == -1:
        st.markdown(
            f"<div class='book-cover'>"
            f"<div class='cover-title'>{html.escape(config['title'])}</div>"
            f"<div class='cover-subtitle'>{html.escape(config['subtitle'])}</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        _, middle, _ = st.columns([1, 2, 1])
        if middle.button("Open the book →", use_container_width=True):
            st.session_state.current_spread = 0
            st.session_state.turn_direction = "forward"
            st.rerun()
        return

    if st.session_state.current_spread == 0:
        st.markdown(f"<div class='intro-box'>{html.escape(config['intro'])}</div>", unsafe_allow_html=True)
        photo = config.get("photo")
        if photo and (BASE_DIR / photo).exists():
            st.image(str(BASE_DIR / photo), use_container_width=True)

    pages_per_spread = 2
    total_spreads = (len(messages) + pages_per_spread - 1) // pages_per_spread
    current_spread = st.session_state.current_spread
    first_page = current_spread * pages_per_spread
    last_page = min(first_page + pages_per_spread, len(messages))
    st.markdown("<div class='section-title'>📖 Messages from the team</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='book-counter'>Spread {current_spread + 1} of {total_spreads}"
        f" · Pages {first_page + 1}–{last_page} of {len(messages)}</div>",
        unsafe_allow_html=True,
    )
    page_columns = st.columns(pages_per_spread, gap="large")
    for page_position, (column, index) in enumerate(zip(page_columns, range(first_page, last_page))):
        with column:
            item = messages[index]
            render_card(item["name"], item["message"], index, st.session_state.turn_direction, page_position)

    previous_column, next_column = st.columns(2, gap="large")
    with previous_column:
        previous_label = "← Cover" if current_spread == 0 else "← Previous 2 pages"
        if st.button(previous_label, use_container_width=True):
            st.session_state.turn_direction = "backward"
            st.session_state.current_spread = current_spread - 1
            st.rerun()
    with next_column:
        if st.button(
            "Next 2 pages →",
            disabled=current_spread >= total_spreads - 1,
            use_container_width=True,
        ):
            st.session_state.turn_direction = "forward"
            st.session_state.current_spread += 1
            st.rerun()

    if current_spread == total_spreads - 1:
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
