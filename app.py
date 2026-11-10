"""Surprise appreciation site for our supervisor, built with Streamlit."""

import html
import json
from pathlib import Path
from typing import Any

import streamlit as st

CONFIG_PATH = Path(__file__).parent / "config.json"
MESSAGES_PATH = Path(__file__).parent / "messages.json"
CARD_COLORS = ["#FFF4E6", "#E7F5FF", "#EBFBEE", "#F3F0FF", "#FFF0F6", "#FFF9DB"]

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


def render_card(author: str, message: str, color: str) -> None:
    """Render a single team message as a coloured card.

    Parameters
    ----------
    author : str
        Name of the teammate.
    message : str
        Message text (HTML is escaped; line breaks are preserved).
    color : str
        Background colour of the card.
    """
    safe_message = html.escape(message).replace("\n", "<br>")
    st.markdown(
        f"""
        <div style="background:{color};padding:1.2rem 1.4rem;border-radius:16px;margin-bottom:1rem;
                    color:#2b2b2b;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size:1.05rem;line-height:1.6;">{safe_message}</div>
            <div style="margin-top:0.8rem;font-weight:600;text-align:right;">— {html.escape(author)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the app."""
    config = load_json(CONFIG_PATH)
    messages = load_json(MESSAGES_PATH)

    st.markdown(
        f"<h1 style='text-align:center;'>🎉 {html.escape(config['title'])} 🎉</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center;font-size:1.2rem;'>{html.escape(config['subtitle'])}</p>",
        unsafe_allow_html=True,
    )

    if "opened" not in st.session_state:
        st.session_state.opened = False

    if not st.session_state.opened:
        _, middle, _ = st.columns([1, 2, 1])
        if middle.button("🎁 Open your surprise", use_container_width=True, type="primary"):
            st.session_state.opened = True
            st.balloons()
            st.rerun()
        return

    st.divider()
    st.write(config["intro"])

    photo = config.get("photo")
    if photo and (Path(__file__).parent / photo).exists():
        st.image(str(Path(__file__).parent / photo), use_container_width=True)

    st.subheader(f"💌 Messages from the team ({len(messages)})")
    for index, item in enumerate(messages):
        render_card(item["name"], item["message"], CARD_COLORS[index % len(CARD_COLORS)])

    st.divider()
    st.markdown(
        f"<h3 style='text-align:center;'>{html.escape(config['closing'])}</h3>",
        unsafe_allow_html=True,
    )
    if st.button("🎈 More balloons!"):
        st.balloons()


main()
