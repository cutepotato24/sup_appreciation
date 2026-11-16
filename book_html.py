"""Build the interactive appreciation photobook displayed inside a Streamlit iframe."""

import base64
import json
import mimetypes
from pathlib import Path
from typing import Any


BOOK_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {
    color-scheme: light;
    font-family: Georgia, "Times New Roman", serif;
    color: #50383D;
}
* { box-sizing: border-box; }
html, body {
    width: 100%;
    height: 100%;
    min-width: 0;
    margin: 0;
    overflow: hidden;
    background: #E7D1D4;
}
button { font: inherit; }
#reader {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 760px;
    padding: 18px 22px;
    overflow: hidden;
}
.scene {
    position: absolute;
    inset: 18px 22px;
}
.scene[hidden] { display: none !important; }
#cover-scene {
    z-index: 3;
    display: flex;
    align-items: center;
    justify-content: center;
}
.cover {
    position: relative;
    display: flex;
    width: 50%;
    height: calc(100% - 34px);
    min-height: 560px;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 54px 52px 44px 68px;
    border: 12px double #B4777E;
    border-radius: 12px;
    background:
        radial-gradient(ellipse at 12% 14%, rgba(255,255,255,.25), transparent 30%),
        radial-gradient(ellipse at 90% 82%, rgba(97,48,57,.16), transparent 32%),
        linear-gradient(145deg, #E6C2C7, #D8AEB5 58%, #E6C2C7);
    box-shadow: inset 0 0 0 4px #F1DBDC, inset 0 0 30px rgba(89,45,54,.22), 0 18px 34px rgba(87,48,55,.24);
    text-align: center;
    transform-origin: left center;
    backface-visibility: hidden;
}
.cover::before {
    position: absolute;
    inset: 0 auto 0 18px;
    width: 12px;
    border-right: 2px solid rgba(117,67,77,.38);
    border-left: 2px solid rgba(117,67,77,.38);
    background: rgba(120,71,79,.1);
    content: "";
}
.cover-content { width: 100%; }
.cover h1 {
    margin: 0;
    color: #75434D;
    font-size: clamp(2.2rem, 4vw, 3.8rem);
    line-height: 1.15;
}
.cover-subtitle {
    margin: 20px 0 0;
    color: #89515B;
    font-size: clamp(1.05rem, 1.6vw, 1.4rem);
}
.cover-intro {
    max-width: 42rem;
    margin: 24px auto 0;
    color: #69464B;
    font-family: Arial, sans-serif;
    font-size: clamp(.9rem, 1.1vw, 1.05rem);
    line-height: 1.65;
}
.cover-photo {
    display: block;
    max-width: min(100%, 300px);
    max-height: 190px;
    margin: 22px auto 0;
    border: 8px solid #FBF3EE;
    box-shadow: 0 5px 16px rgba(76,45,49,.24);
    object-fit: cover;
}
.cover-open, .nav-button {
    min-height: 42px;
    padding: 9px 22px;
    border: 1px solid #A76A73;
    border-radius: 5px;
    background: #F7E8E6;
    box-shadow: 0 3px 8px rgba(104,65,72,.17);
    color: #75434D;
    cursor: pointer;
    font-weight: 700;
    transition: background .2s ease, transform .2s ease;
}
.cover-open { margin-top: 30px; }
.cover-open:hover, .nav-button:hover:not(:disabled) {
    background: #F1DBDC;
    transform: translateY(-2px);
}
.cover.opening { animation: coverTurn .85s cubic-bezier(.4,0,.2,1) forwards; }
.cover.returning { animation: coverReturn .85s cubic-bezier(.4,0,.2,1) forwards; }
@keyframes coverTurn {
    from { transform: perspective(1500px) rotateY(0); }
    to { transform: perspective(1500px) rotateY(-165deg); }
}
@keyframes coverReturn {
    from { transform: perspective(1500px) rotateY(-165deg); }
    to { transform: perspective(1500px) rotateY(0); }
}
#spread-scene {
    z-index: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.spread-heading {
    display: flex;
    min-height: 34px;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    color: #89515B;
    font-size: .95rem;
}
.spread-heading strong { color: #75434D; font-size: 1.05rem; }
.book {
    position: relative;
    display: grid;
    min-height: 0;
    flex: 1 1 auto;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    perspective: 1800px;
    isolation: isolate;
}
.page, .sheet-face {
    position: relative;
    min-width: 0;
    height: 100%;
    overflow: hidden;
    border: 1px solid #CB9FA3;
    background-color: #F7E8E6;
    background-image:
        radial-gradient(ellipse at 12% 14%, rgba(255,255,255,.72), transparent 25%),
        radial-gradient(ellipse at 91% 21%, rgba(147,79,88,.23), transparent 29%),
        radial-gradient(ellipse at 22% 84%, rgba(146,89,95,.2), transparent 30%),
        radial-gradient(ellipse at 79% 71%, rgba(255,255,255,.48), transparent 25%),
        linear-gradient(147deg, transparent 39%, rgba(128,70,78,.17) 46%, rgba(255,255,255,.56) 50%, transparent 57%),
        linear-gradient(32deg, transparent 27%, rgba(128,70,78,.16) 34%, rgba(255,255,255,.5) 38%, transparent 45%),
        linear-gradient(92deg, transparent 31%, rgba(128,70,78,.09) 37%, rgba(255,255,255,.36) 40%, transparent 46%),
        repeating-linear-gradient(2deg, rgba(110,62,70,.035) 0, transparent 2px, transparent 6px);
    box-shadow: 0 8px 22px rgba(104,65,72,.2);
}
.page::before, .sheet-face::before {
    position: absolute;
    top: 8px;
    left: calc(50% - 42px);
    z-index: 2;
    width: 84px;
    height: 23px;
    border: 1px solid rgba(156,100,105,.34);
    background: rgba(218,175,177,.84);
    box-shadow: 0 2px 4px rgba(104,65,72,.18);
    content: "";
    transform: rotate(var(--tape-angle, -2deg));
}
.page-left { border-right: 0; border-radius: 8px 0 0 8px; cursor: pointer; }
.page-right { border-left: 0; border-radius: 0 8px 8px 0; cursor: pointer; }
.book::after {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 50%;
    z-index: 4;
    width: 24px;
    background: linear-gradient(90deg, rgba(91,52,59,.08), rgba(91,52,59,.22), rgba(255,255,255,.25), rgba(91,52,59,.08));
    content: "";
    pointer-events: none;
    transform: translateX(-50%);
}
.paper-content {
    position: relative;
    display: flex;
    width: 100%;
    height: 100%;
    flex-direction: column;
    padding: clamp(26px, 3vw, 46px);
}
.message-copy {
    min-height: 0;
    flex: 1 1 auto;
    margin: 14px 0 18px;
    overflow: auto;
    color: #50383D;
    font-family: Arial, sans-serif;
    font-size: 18px;
    font-style: italic;
    line-height: 1.42;
    overflow-wrap: anywhere;
    white-space: pre-wrap;
}
.message-author {
    flex: 0 0 auto;
    margin-top: auto;
    color: #89515B;
    font-family: Arial, sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-align: right;
}
.page-number {
    flex: 0 0 auto;
    margin-top: 12px;
    color: #A0757A;
    font-size: .78rem;
    letter-spacing: .08em;
    text-align: center;
}
.blank-page::before { display: none; }
.turn-sheet {
    position: absolute;
    top: 0;
    left: 50%;
    z-index: 5;
    display: none;
    width: 50%;
    height: 100%;
    transform-origin: left center;
    transform-style: preserve-3d;
}
.turn-sheet.turn-backward { right: 50%; left: auto; transform-origin: right center; }
.turn-sheet.turn-forward, .turn-sheet.turn-backward { display: block; }
.sheet-face {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
}
.sheet-front { border-radius: 0 8px 8px 0; }
.sheet-back { border-radius: 8px 0 0 8px; transform: rotateY(180deg); }
.turn-sheet.turn-forward { animation: flipForward .9s cubic-bezier(.45,.02,.28,1) forwards; }
.turn-sheet.turn-backward { animation: flipBackward .9s cubic-bezier(.45,.02,.28,1) forwards; }
@keyframes flipForward {
    0% { transform: rotateY(0); box-shadow: 0 6px 12px rgba(70,40,45,.12); }
    45% { box-shadow: 14px 9px 28px rgba(70,40,45,.3); }
    100% { transform: rotateY(-180deg); box-shadow: 0 2px 8px rgba(70,40,45,.16); }
}
@keyframes flipBackward {
    0% { transform: rotateY(0); box-shadow: 0 6px 12px rgba(70,40,45,.12); }
    45% { box-shadow: -14px 9px 28px rgba(70,40,45,.3); }
    100% { transform: rotateY(180deg); box-shadow: 0 2px 8px rgba(70,40,45,.16); }
}
.book-controls {
    display: flex;
    min-height: 42px;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    color: #89515B;
}
.nav-button { min-width: 120px; }
.nav-button:disabled { opacity: .45; cursor: default; }
.book-counter { flex: 1; text-align: center; }
.closing {
    margin: 0;
    color: #75434D;
    font-size: 1rem;
    font-weight: 700;
    text-align: center;
}
#closing[hidden] { display: block !important; visibility: hidden; }
@media (max-width: 700px) {
    #reader { min-height: 760px; padding: 10px; }
    .scene { inset: 10px; }
    .cover { width: 86%; min-height: 0; padding: 38px 24px 30px 38px; }
    #spread-scene { gap: 6px; }
    .spread-heading { font-size: .78rem; }
    .book { min-height: 0; }
    .paper-content { padding: 24px 17px; }
    .message-copy { font-size: 13px; line-height: 1.35; }
    .nav-button { min-width: 0; padding: 8px 12px; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
</style>
</head>
<body>
<main id="reader">
    <section id="cover-scene" class="scene">
        <div id="cover" class="cover">
            <div class="cover-content">
                <h1 id="cover-title"></h1>
                <p id="cover-subtitle" class="cover-subtitle"></p>
                <p id="cover-intro" class="cover-intro"></p>
                <img id="cover-photo" class="cover-photo" alt="A team photo" hidden>
            </div>
            <button id="open-book" class="cover-open" type="button">Open the book →</button>
        </div>
    </section>
    <section id="spread-scene" class="scene" hidden>
        <header class="spread-heading">
            <strong>💌 Messages from the team</strong>
            <span id="spread-label"></span>
        </header>
        <div id="book" class="book">
            <div id="left-page" class="page page-left"></div>
            <div id="right-page" class="page page-right"></div>
            <div id="turn-sheet" class="turn-sheet">
                <div id="turn-front" class="sheet-face sheet-front"></div>
                <div id="turn-back" class="sheet-face sheet-back"></div>
            </div>
        </div>
        <footer class="book-controls">
            <button id="previous-page" class="nav-button" type="button">← Previous</button>
            <span id="book-counter" class="book-counter"></span>
            <button id="next-page" class="nav-button" type="button">Next →</button>
        </footer>
        <p id="closing" class="closing" hidden></p>
    </section>
</main>
<script id="book-data" type="application/json">__BOOK_DATA__</script>
<script>
(() => {
    const data = JSON.parse(document.getElementById("book-data").textContent);
    const messages = data.messages;
    const totalSpreads = Math.max(1, Math.ceil(messages.length / 2));
    const coverScene = document.getElementById("cover-scene");
    const spreadScene = document.getElementById("spread-scene");
    const cover = document.getElementById("cover");
    const leftPage = document.getElementById("left-page");
    const rightPage = document.getElementById("right-page");
    const turnSheet = document.getElementById("turn-sheet");
    const turnFront = document.getElementById("turn-front");
    const turnBack = document.getElementById("turn-back");
    const previousButton = document.getElementById("previous-page");
    const nextButton = document.getElementById("next-page");
    const counter = document.getElementById("book-counter");
    const closing = document.getElementById("closing");
    const tapeAngles = [-3, 2, -1, 3];
    let spreadIndex = 0;
    let turning = false;

    document.getElementById("cover-title").textContent = data.title;
    document.getElementById("cover-subtitle").textContent = data.subtitle;
    document.getElementById("cover-intro").textContent = data.intro;
    if (data.photo) {
        const photo = document.getElementById("cover-photo");
        photo.src = data.photo;
        photo.hidden = false;
    }

    function fitText(element) {
        let size = window.innerWidth <= 700 ? 13 : 18;
        const minimum = window.innerWidth <= 700 ? 10 : 11;
        element.style.fontSize = `${size}px`;
        while (element.scrollHeight > element.clientHeight + 1 && size > minimum) {
            size -= 0.5;
            element.style.fontSize = `${size}px`;
        }
    }

    function fillPage(element, item, pageIndex) {
        element.replaceChildren();
        element.classList.toggle("blank-page", !item);
        if (!item) return;

        element.style.setProperty("--tape-angle", `${tapeAngles[pageIndex % tapeAngles.length]}deg`);
        const content = document.createElement("div");
        content.className = "paper-content";

        const copy = document.createElement("div");
        copy.className = "message-copy";
        copy.textContent = item.message;

        const author = document.createElement("div");
        author.className = "message-author";
        author.textContent = `${item.emoji} ${item.name}`;

        const number = document.createElement("div");
        number.className = "page-number";
        number.textContent = `Page ${pageIndex + 1}`;

        content.append(copy, author, number);
        element.append(content);
        requestAnimationFrame(() => fitText(copy));
    }

    function renderSpread() {
        const firstIndex = spreadIndex * 2;
        const leftMessage = messages[firstIndex];
        const rightMessage = messages[firstIndex + 1];
        fillPage(leftPage, leftMessage, firstIndex);
        fillPage(rightPage, rightMessage, firstIndex + 1);
        turnSheet.className = "turn-sheet";
        counter.textContent = `Spread ${spreadIndex + 1} of ${totalSpreads}`;
        previousButton.disabled = false;
        nextButton.disabled = spreadIndex >= totalSpreads - 1;
        closing.textContent = data.closing;
        closing.hidden = spreadIndex < totalSpreads - 1;
        document.getElementById("spread-label").textContent =
            `Pages ${firstIndex + 1}–${Math.min(firstIndex + 2, messages.length)} of ${messages.length}`;
    }

    function openBook() {
        if (turning) return;
        turning = true;
        spreadScene.hidden = false;
        renderSpread();
        cover.classList.add("opening");
        cover.addEventListener("animationend", () => {
            coverScene.hidden = true;
            cover.classList.remove("opening");
            turning = false;
        }, { once: true });
    }

    function returnToCover() {
        if (turning) return;
        turning = true;
        coverScene.hidden = false;
        cover.classList.remove("returning");
        void cover.offsetWidth;
        cover.classList.add("returning");
        cover.addEventListener("animationend", () => {
            spreadScene.hidden = true;
            cover.classList.remove("returning");
            turning = false;
        }, { once: true });
    }

    function turnForward() {
        if (turning || spreadIndex >= totalSpreads - 1) return;
        turning = true;
        const nextSpread = spreadIndex + 1;
        const currentRightIndex = spreadIndex * 2 + 1;
        const nextLeftIndex = nextSpread * 2;
        fillPage(leftPage, messages[spreadIndex * 2], spreadIndex * 2);
        fillPage(rightPage, messages[nextLeftIndex + 1], nextLeftIndex + 1);
        fillPage(turnFront, messages[currentRightIndex], currentRightIndex);
        fillPage(turnBack, messages[nextLeftIndex], nextLeftIndex);
        turnSheet.className = "turn-sheet turn-forward";
        turnSheet.addEventListener("animationend", () => {
            spreadIndex = nextSpread;
            renderSpread();
            turning = false;
        }, { once: true });
    }

    function turnBackward() {
        if (turning) return;
        if (spreadIndex === 0) {
            returnToCover();
            return;
        }
        turning = true;
        const previousSpread = spreadIndex - 1;
        const currentLeftIndex = spreadIndex * 2;
        const previousLeftIndex = previousSpread * 2;
        fillPage(leftPage, messages[previousLeftIndex], previousLeftIndex);
        fillPage(rightPage, messages[spreadIndex * 2 + 1], spreadIndex * 2 + 1);
        fillPage(turnFront, messages[currentLeftIndex], currentLeftIndex);
        fillPage(turnBack, messages[previousLeftIndex + 1], previousLeftIndex + 1);
        turnSheet.className = "turn-sheet turn-backward";
        turnSheet.addEventListener("animationend", () => {
            spreadIndex = previousSpread;
            renderSpread();
            turning = false;
        }, { once: true });
    }

    document.getElementById("open-book").addEventListener("click", openBook);
    previousButton.addEventListener("click", turnBackward);
    nextButton.addEventListener("click", turnForward);
    leftPage.addEventListener("click", turnBackward);
    rightPage.addEventListener("click", turnForward);
    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowRight") {
            event.preventDefault();
            if (coverScene.hidden) turnForward();
            else openBook();
        } else if (event.key === "ArrowLeft" && coverScene.hidden) {
            event.preventDefault();
            turnBackward();
        }
    });
})();
</script>
</body>
</html>
"""


def _photo_data_uri(config: dict[str, Any], base_dir: Path) -> str:
    photo = config.get("photo")
    if not photo:
        return ""

    root = base_dir.resolve()
    photo_path = (root / str(photo)).resolve()
    if not photo_path.is_relative_to(root) or not photo_path.is_file():
        return ""

    mime_type = mimetypes.guess_type(photo_path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(photo_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_book_html(config: dict[str, Any], messages: list[dict[str, str]], base_dir: Path) -> str:
    """Build the self-contained HTML and controls for the appreciation photobook."""
    data = {
        "title": str(config.get("title", "")),
        "subtitle": str(config.get("subtitle", "")),
        "intro": str(config.get("intro", "")),
        "closing": str(config.get("closing", "")),
        "photo": _photo_data_uri(config, base_dir),
        "messages": [
            {
                "name": str(message.get("name", "")),
                "message": str(message.get("message", "")),
                "emoji": ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"][index % 8],
            }
            for index, message in enumerate(messages)
        ],
    }
    serialized = json.dumps(data, ensure_ascii=False)
    serialized = (
        serialized.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )
    return BOOK_HTML.replace("__BOOK_DATA__", serialized)
