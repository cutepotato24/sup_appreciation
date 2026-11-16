"""Build the self-contained HTML flip-book shown in the Streamlit app."""
 
import base64

import html

import io

import mimetypes

import re

from functools import lru_cache

from pathlib import Path

from urllib.parse import quote
 
CARD_ACCENTS = ["#8A4B3A", "#7A4A2E", "#7D4852", "#8F5A3C", "#5E4630", "#8A5560"]

CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]
 
 
def _leather_uri(seed: int, color: str) -> str:

    """Return a data-URI SVG of padded leatherette (fine pebble grain plus soft dents)."""

    svg = (

        "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='800' viewBox='0 0 600 800' "

        "preserveAspectRatio='none'>"

        "<filter id='f' x='0' y='0' width='100%' height='100%'>"

        f"<feTurbulence type='fractalNoise' baseFrequency='0.55' numOctaves='3' seed='{seed}' result='g'/>"

        f"<feTurbulence type='fractalNoise' baseFrequency='0.006 0.008' numOctaves='3' seed='{seed + 3}' result='d'/>"

        "<feComposite in='g' in2='d' operator='arithmetic' k1='0' k2='0.55' k3='0.45' k4='0' result='n'/>"

        f"<feDiffuseLighting in='n' lighting-color='{color}' surfaceScale='2.4' diffuseConstant='1.25'>"

        "<feDistantLight azimuth='50' elevation='62'/></feDiffuseLighting></filter>"

        "<rect width='600' height='800' filter='url(#f)'/></svg>"

    )

    return "data:image/svg+xml," + quote(svg, safe="/:=,;'()")
 
 
def _aged_paper_uri(seed: int, color: str) -> str:

    """Return a data-URI SVG of old album paper: fine grain, brown blotches and foxing spots.
 
    Parameters

    ----------

    seed : int

        Noise seed, so every page ages differently.

    color : str

        Base paper colour.
 
    Returns

    -------

    str

        A ``data:image/svg+xml`` URI usable in CSS ``url()``.

    """

    svg = (

        "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='800' viewBox='0 0 600 800' "

        "preserveAspectRatio='none'>"

        "<filter id='f' x='0' y='0' width='100%' height='100%'>"

        f"<feTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' seed='{seed}' result='fine'/>"

        f"<feDiffuseLighting in='fine' lighting-color='{color}' surfaceScale='0.9' diffuseConstant='1.2' result='paper'>"

        "<feDistantLight azimuth='45' elevation='60'/></feDiffuseLighting>"

        f"<feTurbulence type='fractalNoise' baseFrequency='0.007 0.010' numOctaves='4' seed='{seed + 1}' result='blot'/>"

        "<feColorMatrix in='blot' type='matrix' result='stain' "

        "values='0 0 0 0 0.60  0 0 0 0 0.42  0 0 0 0 0.20  0 0 0 1.3 -0.52'/>"

        "<feComposite in='stain' in2='paper' operator='over' result='aged'/>"

        f"<feTurbulence type='fractalNoise' baseFrequency='0.11' numOctaves='2' seed='{seed + 2}' result='sp'/>"

        "<feColorMatrix in='sp' type='matrix' result='fox' "

        "values='0 0 0 0 0.55  0 0 0 0 0.38  0 0 0 0 0.20  0 0 0 14 -10.4'/>"

        "<feComposite in='fox' in2='aged' operator='over'/></filter>"

        "<rect width='600' height='800' filter='url(#f)'/></svg>"

    )

    return "data:image/svg+xml," + quote(svg, safe="/:=,;'()")
 
 
def _photo_uri(path: Path) -> str:

    """Embed an image file as a base64 data URI."""

    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"

    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
 
 
PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}

MAX_PHOTOS_PER_PAGE = 3
 
 
@lru_cache(maxsize=256)

def _small_photo_uri(path: str, mtime: float) -> str | None:

    """Shrink a photo (max 1000 px, JPEG) and return it as a data URI; None if it can't be read.
 
    ``mtime`` is only part of the cache key, so edited files are re-read.

    """

    try:

        from PIL import Image, ImageOps
 
        with Image.open(path) as img:

            img = ImageOps.exif_transpose(img).convert("RGB")

            img.thumbnail((1000, 1000))

            buffer = io.BytesIO()

            img.save(buffer, "JPEG", quality=82, optimize=True)

        return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")

    except Exception:  # unreadable or unsupported file: skip it instead of breaking the book

        return None
 
 
def load_photos(folder: Path) -> list[str]:

    """Return all photos of a folder as small data URIs, in natural filename order."""

    if not folder.is_dir():

        return []

    files = [f for f in folder.iterdir() if f.suffix.lower() in PHOTO_EXTS]

    files.sort(key=lambda f: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", f.name)])

    uris = [_small_photo_uri(str(f), f.stat().st_mtime) for f in files]

    return [u for u in uris if u]
 
 
def split_evenly(total: int, parts: int) -> list[int]:

    """Split ``total`` into ``parts`` counts that differ by at most one, spread evenly."""

    return [round((i + 1) * total / parts) - round(i * total / parts) for i in range(parts)]
 
 
def _photo_page(uris: list[str], page_no: int, seed: int) -> str:

    rotations = [-2.2, 1.8, -1.2, 2.4, -1.8, 1.4]

    items = "".join(

        f"<div class='pol' style='transform:rotate({rotations[(seed + j) % len(rotations)]}deg)'>"

        f"<div class='ph'><img src='{uri}' alt=''></div><i class='corners'></i></div>"

        for j, uri in enumerate(uris)

    )

    return f"<div class='in'><div class='pgrid n{len(uris)}'>{items}</div><div class='pno'>Page {page_no}</div></div>"
 
 
def _message_page(index: int, name: str, message: str, page_no: int) -> str:

    accent = CARD_ACCENTS[index % len(CARD_ACCENTS)]

    emoji = CARD_EMOJIS[index % len(CARD_EMOJIS)]

    tape = [-3, 2, -1, 3][index % 4]

    return (

        f"<div class='tape' style='transform:rotate({tape}deg)'></div>"

        f"<div class='in'><div class='fit msg'>{html.escape(message)}</div>"

        f"<div class='author' style='color:{accent}'>{emoji} {html.escape(name)}</div>"

        f"<div class='pno'>Page {page_no}</div></div>"

    )
 
 
def _intro_page(config: dict, base_dir: Path, page_no: int) -> str:

    photo = config.get("photo")

    photo_html = ""

    if photo and (base_dir / photo).exists():

        photo_html = f"<div class='photo'><img src='{_photo_uri(base_dir / photo)}' alt=''><i class='corners'></i></div>"

    return (

        "<div class='tape' style='transform:rotate(-2deg)'></div>"

        f"<div class='in'><div class='fit msg center'>{html.escape(config.get('intro', ''))}</div>"

        f"{photo_html}<div class='pno'>Page {page_no}</div></div>"

    )
 
 
def _closing_page(config: dict, page_no: int) -> str:

    return (

        f"<div class='in'><div class='fit closing center'>{html.escape(config.get('closing', ''))}</div>"

        f"<div class='pno'>Page {page_no}</div></div>"

    )
 
 
def _cover(config: dict) -> str:

    return (

        "<div class='in coverin'>"

        "<div class='ckicker'>📷 PHOTO ALBUM</div>"

        f"<div class='fit ctitle'>{html.escape(config['title'])}</div>"

        f"<div class='csub'>{html.escape(config['subtitle'])}</div></div>"

    )
 
 
def _back_cover() -> str:

    return "<div class='in coverin'><div class='csub'>📷 Mahal Ka Namin, Stal 💖</div></div>"
 
 
def build_book_html(config: dict, messages: list, base_dir: Path, photos_dir: Path | None = None) -> str:

    """Build the complete HTML document for the flip book.
 
    Parameters

    ----------

    config : dict

        Site config (title, subtitle, intro, closing, photo).

    messages : list

        Items with ``name`` and ``message`` keys.

    base_dir : Path

        Folder used to resolve the photo path.

    photos_dir : Path | None

        Folder of photos to spread evenly after the messages (message, 2-3 photos, message, ...).
 
    Returns

    -------

    str

        A full HTML document to pass to ``st.components.v1.html``.

    """

    # Face list: cover, intro, messages..., closing, [blank], back cover.

    # A face at an even position sits on the right (front of a sheet); odd on the left (back of a sheet).

    faces: list[tuple[str, str]] = [("cover", _cover(config))]

    faces.append(("page", _intro_page(config, base_dir, 1)))

    photos = load_photos(photos_dir) if photos_dir else []

    per_message = split_evenly(len(photos), len(messages)) if messages else []

    cursor = 0

    for i, item in enumerate(messages):

        faces.append(("page", _message_page(i, item["name"], item["message"], len(faces))))

        count = per_message[i] if per_message else 0

        group, cursor = photos[cursor : cursor + count], cursor + count

        if group:

            pages = -(-len(group) // MAX_PHOTOS_PER_PAGE)  # ceil: at most 3 photos per page

            start = 0

            for size in split_evenly(len(group), pages):

                faces.append(("page", _photo_page(group[start : start + size], len(faces), i + start)))

                start += size

    faces.append(("page", _closing_page(config, len(faces))))

    if (len(faces) + 1) % 2:

        faces.append(("page", "<div class='in'></div>"))

    faces.append(("cover", _back_cover()))
 
    sheets = []

    for s in range(len(faces) // 2):

        sheet_faces = []

        for side, pos in (("front", 2 * s), ("back", 2 * s + 1)):

            kind, content = faces[pos]

            side_cls = "rightpage" if side == "front" else "leftpage"

            sheet_faces.append(f"<div class='face {side} {side_cls} {kind} p{pos % 4}'>{content}</div>")

        sheets.append(f"<div class='sheet'>{''.join(sheet_faces)}</div>")
 
    paper = "#F1E2C3"

    cover = "#B9606E"

    crumple_css = "".join(

        f".p{k}{{background-image:url(\"{_aged_paper_uri(11 + 7 * k, paper)}\")}}"

        f".p{k}.cover{{background-image:url(\"{_leather_uri(31 + 5 * k, cover)}\")}}"

        for k in range(4)

    )
 
    return (

        TEMPLATE.replace("__CRUMPLE__", crumple_css)

        .replace("__SHEETS__", "".join(sheets))

    )
 
 
TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>

*{box-sizing:border-box}

html,body{margin:0;height:100%;overflow:hidden;background:transparent;

  font-family:Georgia,"Times New Roman",serif;color:#44301F}

#wrap{height:100%;display:flex;flex-direction:column;border-radius:12px;

  background:radial-gradient(ellipse at 50% 45%,#DDBDC2 0%,#BF959C 70%,#A9808A 100%)}

html:fullscreen #wrap,html:-webkit-full-screen #wrap{border-radius:0}

.stage{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;

  perspective:2800px;overflow:hidden}

.book{position:relative;width:calc(var(--pw)*2);height:var(--ph);

  transform-style:preserve-3d;transition:transform .9s ease;cursor:pointer}

.sheet{position:absolute;top:0;left:50%;width:50%;height:100%;transform-origin:left center;

  transform-style:preserve-3d;transition:transform 1.15s cubic-bezier(.45,.05,.25,1)}

.sheet.flipped{transform:rotateY(-180deg)}

.face{position:absolute;inset:0;overflow:hidden;background-color:#EBDBB9;background-size:100% 100%;

  backface-visibility:hidden;-webkit-backface-visibility:hidden}

.face *{backface-visibility:hidden;-webkit-backface-visibility:hidden}

.face.front{transform:translateZ(.6px)}

.face.back{transform:rotateY(180deg) translateZ(.6px)}

.rightpage{border-radius:2px 7px 7px 2px;box-shadow:3px 4px 10px rgba(70,35,45,.30)}

.leftpage{border-radius:7px 2px 2px 7px;box-shadow:-3px 4px 10px rgba(70,35,45,.30)}

/* spine shading + soft vignette + extra crease lines */

.face::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:0}

.face.page::before{box-shadow:inset 0 0 calc(var(--pw)*.11) rgba(150,100,45,.36),

  inset 0 0 calc(var(--pw)*.02) rgba(110,70,30,.30)}

.rightpage.page::before{background:

  linear-gradient(to right,rgba(60,35,20,.42),rgba(60,35,20,.10) 5%,transparent 14%),

  linear-gradient(to left,rgba(60,35,20,.12),transparent 5%)}

.leftpage.page::before{background:

  linear-gradient(to left,rgba(60,35,20,.42),rgba(60,35,20,.10) 5%,transparent 14%),

  linear-gradient(to right,rgba(60,35,20,.12),transparent 5%)}

.face.cover{border-radius:4px 12px 12px 4px}

.face.cover.leftpage{border-radius:12px 4px 4px 12px}

.face.cover.rightpage::before{background:

  linear-gradient(to right,transparent 6.4%,rgba(0,0,0,.38) 7%,rgba(255,255,255,.18) 7.7%,transparent 8.4%),

  linear-gradient(to right,rgba(0,0,0,.40),rgba(0,0,0,.05) 7%,transparent 9%),

  radial-gradient(ellipse at 30% 20%,rgba(255,255,255,.20),transparent 55%),

  linear-gradient(to left,rgba(0,0,0,.25),transparent 8%)}

.face.cover.leftpage::before{background:

  linear-gradient(to left,transparent 6.4%,rgba(0,0,0,.38) 7%,rgba(255,255,255,.18) 7.7%,transparent 8.4%),

  linear-gradient(to left,rgba(0,0,0,.40),rgba(0,0,0,.05) 7%,transparent 9%),

  radial-gradient(ellipse at 70% 20%,rgba(255,255,255,.20),transparent 55%),

  linear-gradient(to right,rgba(0,0,0,.25),transparent 8%)}

.face.cover::after{content:"";position:absolute;z-index:0;top:4.5%;bottom:4.5%;left:12%;right:6%;

  border:2px dashed rgba(246,223,166,.75);border-radius:8px;pointer-events:none}

.face.cover.leftpage::after{left:6%;right:12%}

/* punched binder holes along the spine of every paper page */

.face.page::after{content:"";position:absolute;z-index:0;top:7%;bottom:7%;width:calc(var(--pw)*.04);

  background:radial-gradient(circle calc(var(--pw)*.017) at 50% 50%,rgba(50,25,30,.78) 0 58%,

    rgba(255,255,255,.45) 66%,transparent 72%) 0 0/100% 12.5% repeat-y;pointer-events:none}

.face.page.rightpage::after{left:calc(var(--pw)*.035)}

.face.page.leftpage::after{right:calc(var(--pw)*.035)}

__CRUMPLE__

.in{position:absolute;inset:0;z-index:1;display:flex;flex-direction:column;

  padding:calc(var(--pw)*.10) calc(var(--pw)*.09) calc(var(--pw)*.06)}

.rightpage .in{padding-left:calc(var(--pw)*.13)}

.leftpage .in{padding-right:calc(var(--pw)*.13)}

.fit{flex:1 1 0;min-height:0;overflow:hidden;white-space:pre-wrap;word-break:break-word;

  line-height:1.38;font-style:italic;font-size:14px}

.fit.center{text-align:center}

.author{flex:none;margin-top:calc(var(--pw)*.025);font-weight:700;text-align:right;

  font-size:calc(var(--pw)*.045)}

.pno{flex:none;margin-top:calc(var(--pw)*.02);text-align:center;color:#8B6F4E;

  font-size:calc(var(--pw)*.028);letter-spacing:.08em}

.tape{position:absolute;top:-1.2%;left:calc(50% - var(--pw)*.09);width:calc(var(--pw)*.18);

  height:calc(var(--pw)*.05);background:rgba(222,200,150,.82);border:1px solid rgba(150,120,70,.35);

  box-shadow:0 2px 3px rgba(104,65,72,.15);z-index:3}

.photo{position:relative;flex:0 0 46%;margin-top:calc(var(--pw)*.04);transform:rotate(-1.2deg);min-height:0}

.photo img{width:100%;height:100%;object-fit:cover;display:block;border:calc(var(--pw)*.007) solid #fff;

  box-shadow:0 3px 9px rgba(50,25,32,.38)}

.pgrid{flex:1 1 0;min-height:0;display:grid;gap:calc(var(--pw)*.045)}

.pgrid.n1{grid-template-columns:1fr;grid-template-rows:1fr}

.pgrid.n2{grid-template-columns:1fr;grid-template-rows:1fr 1fr}

.pgrid.n3{grid-template-columns:1fr 1fr;grid-template-rows:1.15fr 1fr}

.pgrid.n3 .pol:first-child{grid-column:1/3}

.pol{position:relative;min-width:0;min-height:0}

.pol .ph{position:absolute;inset:4%;overflow:hidden;background:#eee;border:calc(var(--pw)*.007) solid #fff;

  box-shadow:0 3px 9px rgba(50,25,32,.38)}

.pol .corners{inset:4%}

.corners{position:absolute;inset:0;pointer-events:none;z-index:2;--c:#2E221D;--s:calc(var(--pw)*.07);

  background:

   linear-gradient(135deg,var(--c) 50%,transparent 50%) left top/var(--s) var(--s) no-repeat,

   linear-gradient(225deg,var(--c) 50%,transparent 50%) right top/var(--s) var(--s) no-repeat,

   linear-gradient(45deg,var(--c) 50%,transparent 50%) left bottom/var(--s) var(--s) no-repeat,

   linear-gradient(315deg,var(--c) 50%,transparent 50%) right bottom/var(--s) var(--s) no-repeat;

  filter:drop-shadow(0 1px 1px rgba(0,0,0,.4))}

.pol img{width:100%;height:100%;object-fit:cover;display:block}

.tape.sm{top:-3%;left:calc(50% - var(--pw)*.07);width:calc(var(--pw)*.14);height:calc(var(--pw)*.04)}

.closing{font-style:normal;font-weight:700;color:#7A4A3A;display:flex;align-items:center;

  justify-content:center;text-align:center}

.coverin{align-items:center;justify-content:center;text-align:center}

.coverin{padding-left:calc(var(--pw)*.17);padding-right:calc(var(--pw)*.12)}

.face.leftpage .coverin{padding-left:calc(var(--pw)*.12);padding-right:calc(var(--pw)*.17)}

.ckicker{letter-spacing:.28em;color:#F6DFA6;font-size:calc(var(--pw)*.034);font-weight:700;

  margin-bottom:calc(var(--pw)*.05);text-shadow:0 1px 0 rgba(0,0,0,.35)}

.ctitle{flex:none!important;height:auto;color:#F6DFA6;font-style:normal;font-weight:700;

  font-size:calc(var(--pw)*.082);line-height:1.2;overflow:visible!important;

  text-shadow:0 1px 0 rgba(255,255,255,.25),0 -1px 1px rgba(0,0,0,.45)}

.csub{margin-top:calc(var(--pw)*.05);color:#F7DDE0;font-size:calc(var(--pw)*.048);text-align:center;

  text-shadow:0 1px 1px rgba(0,0,0,.35)}

.bar{flex:none;display:flex;align-items:center;justify-content:center;gap:12px;padding:10px;

  font-family:system-ui,sans-serif}

.bar button{border:1px solid #B4777E;border-radius:6px;background:#F1DBDC;color:#75434D;

  font-weight:700;font-size:15px;padding:8px 16px;cursor:pointer;box-shadow:0 3px 8px rgba(104,65,72,.2)}

.bar button:hover:not(:disabled){background:#fff;transform:translateY(-1px)}

.bar button:disabled{opacity:.4;cursor:default}

#label{min-width:130px;text-align:center;color:#50383D;font-weight:600;font-size:14px}
 
#hearts{position:fixed;inset:0;pointer-events:none;overflow:hidden;z-index:50}

.heart{position:absolute;top:-70px;line-height:1;opacity:.28;will-change:transform;

  animation:heartfall linear forwards;}

.heart>i{display:inline-block;font-style:normal;animation:heartsway ease-in-out infinite alternate}

@keyframes heartfall{

  0%{transform:translateY(0);opacity:0}

  8%{opacity:.28}

  85%{opacity:.28}

  100%{transform:translateY(calc(100vh + 140px));opacity:0}}

@keyframes heartsway{from{transform:translateX(calc(var(--sway)*-1)) rotate(-14deg)}

  to{transform:translateX(var(--sway)) rotate(14deg)}}

#hb{display:none}

body.fs #hb{display:inline-block}

@media (prefers-reduced-motion:reduce){#hearts{display:none}}

@media print{

  #hearts{display:none!important}

  @page{size:6in 8.3in;margin:0}

  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}

  html,body{height:auto!important;min-height:0!important;overflow:visible!important;background:none!important;margin:0!important;padding:0!important}

  #wrap{display:block!important;height:auto!important;background:none!important;border-radius:0!important}

  .bar{display:none!important}

  .stage{display:block!important;perspective:none!important;overflow:visible!important;height:auto!important;margin:0!important;padding:0!important}

  .book{display:block!important;width:auto!important;height:auto!important;transform:none!important;

    transform-style:flat!important;transition:none!important;cursor:auto}

  .sheet{position:static!important;display:block!important;width:auto!important;height:auto!important;

    transform:none!important;transform-style:flat!important;transition:none!important;margin:0!important;padding:0!important}

  .face,.face.front,.face.back{position:relative!important;display:block!important;

    width:6in!important;height:8.25in!important;margin:0!important;transform:none!important;

    visibility:visible!important;box-shadow:none!important;border-radius:0!important;overflow:hidden!important;

    break-after:page;page-break-after:always;break-inside:avoid;page-break-inside:avoid}

  .face:last-child:last-of-type{break-after:auto;page-break-after:auto}

  .sheet:last-child .face.back{break-after:auto;page-break-after:auto}

}
</style></head>
<body>
<div id="hearts"></div>
<div id="wrap">
<div class="stage" id="stage"><div class="book" id="book">__SHEETS__</div></div>
<div class="bar">
<button id="prev">← Previous</button>
<span id="label"></span>
<button id="next">Next →</button>
<button id="fs">⛶ Full screen</button>
<button id="hb">💗 Hearts: on</button>
<button id="pdf">📄 Save as PDF</button>
</div>
</div>
<script>

(function(){

  var RATIO=0.72;

  var book=document.getElementById('book'), stage=document.getElementById('stage');

  var sheets=[].slice.call(document.querySelectorAll('.sheet'));

  var n=sheets.length, cur=0, zc=100, pw=400;

  var prevB=document.getElementById('prev'), nextB=document.getElementById('next');

  var label=document.getElementById('label'), fsB=document.getElementById('fs');
 
  function setZ(){

    sheets.forEach(function(s,i){ if(!s._anim) s.style.zIndex = i<cur ? i+1 : n-i; });

  }

  function vis(s,front,back){

    s.firstChild.style.visibility = front ? 'visible' : 'hidden';

    s.lastChild.style.visibility  = back  ? 'visible' : 'hidden';

  }

  function flip(s,toLeft){

    s._anim=true; s.style.zIndex=++zc;

    vis(s,true,true);                       // both faces needed while the page is turning

    s.classList.toggle('flipped',toLeft);

    clearTimeout(s._t1); clearTimeout(s._t2);

    s._t1=setTimeout(function(){ vis(s,!toLeft,toLeft); },575);   // halfway: hide the face turned away

    s._t2=setTimeout(function(){ s._anim=false; setZ(); },1200);

  }

  function go(dir){

    if(dir>0 && cur<n){ flip(sheets[cur],true); cur++; }       // right page turns over to the left

    else if(dir<0 && cur>0){ cur--; flip(sheets[cur],false); } // left page turns back to the right

    else return;

    enterFullscreen();

    update();

  }

  function update(){

    var shift = cur===0 ? -pw/2 : (cur===n ? pw/2 : 0);

    book.style.transform='translateX('+shift+'px)';

    label.textContent = cur===0 ? 'Cover' : (cur===n ? 'The end' : 'Pages '+(2*cur-1)+'–'+(2*cur));

    prevB.disabled = cur===0; nextB.disabled = cur===n;

  }

  function fit(){

    var els=document.querySelectorAll('.fit');

    var maxPx=pw*0.056;

    for(var i=0;i<els.length;i++){

      var el=els[i];

      if(el.classList.contains('ctitle')) continue;

      var lo=5, hi=maxPx;

      el.style.fontSize=hi+'px';

      if(el.scrollHeight<=el.clientHeight+1) continue;

      for(var k=0;k<14;k++){

        var mid=(lo+hi)/2; el.style.fontSize=mid+'px';

        if(el.scrollHeight>el.clientHeight+1) hi=mid; else lo=mid;

      }

      el.style.fontSize=lo+'px';

    }

  }

  function layout(){

    var w=stage.clientWidth, h=stage.clientHeight;

    pw=Math.max(120, Math.min(w*0.465, h*0.95*RATIO));

    var root=document.documentElement.style;

    root.setProperty('--pw',pw+'px'); root.setProperty('--ph',(pw/RATIO)+'px');

    update(); fit(); updateHearts();

  }
 
  prevB.onclick=function(e){e.stopPropagation();go(-1)};

  nextB.onclick=function(e){e.stopPropagation();go(1)};

  book.addEventListener('click',function(e){

    var r=book.getBoundingClientRect();

    go(e.clientX < r.left + r.width/2 ? -1 : 1);

  });

  document.addEventListener('keydown',function(e){

    if(e.key==='ArrowRight'||e.key==='PageDown') go(1);

    if(e.key==='ArrowLeft'||e.key==='PageUp') go(-1);

  });

  var tx=null;

  document.addEventListener('touchstart',function(e){tx=e.touches[0].clientX},{passive:true});

  document.addEventListener('touchend',function(e){

    if(tx===null) return;

    var dx=e.changedTouches[0].clientX-tx; tx=null;

    if(Math.abs(dx)>40) go(dx<0?1:-1);

  });
 
  fsB.onclick=function(e){

    e.stopPropagation();

    var d=document, el=d.documentElement;

    if(d.fullscreenElement||d.webkitFullscreenElement){

      (d.exitFullscreen||d.webkitExitFullscreen).call(d); return;

    }

    enterFullscreen();

  };

  function enterFullscreen(){

    if(document.fullscreenElement||document.webkitFullscreenElement) return;

    var el=document.documentElement;

    var req=el.requestFullscreen||el.webkitRequestFullscreen, p;

    try{

      if(!req) throw new Error('Fullscreen is not supported');

      p=req.call(el);

    }catch(err){ p=Promise.reject(err); }

    if(p&&p.catch) p.catch(function(){

      var frame=window.frameElement;

      var frameReq=frame&&(frame.requestFullscreen||frame.webkitRequestFullscreen);

      if(!frameReq){ fsB.textContent='Press F11 for full screen'; return; }

      try{

        var framePromise=frameReq.call(frame);

        if(framePromise&&framePromise.catch) framePromise.catch(function(){

          fsB.textContent='Press F11 for full screen';

        });

      }catch(err2){ fsB.textContent='Press F11 for full screen'; }

    });

  }

  var pdfB=document.getElementById('pdf');

  pdfB.onclick=function(e){ e.stopPropagation(); window.print(); };

  window.addEventListener('beforeprint',function(){      // size every page for the paper, then fit text

    pw=576; var r=document.documentElement.style;

    r.setProperty('--pw','576px'); r.setProperty('--ph','800px'); fit();

  });

  window.addEventListener('afterprint',function(){ layout(); });

  // ---- floating hearts, only while in full screen

  var heartsEl=document.getElementById('hearts'), hb=document.getElementById('hb');

  var EMOJI=['💖','💗','💕','💘','💝','❤️','🩷'], heartTimer=null, heartsOn=true;

  function isFS(){

    return !!(document.fullscreenElement||document.webkitFullscreenElement)

      || (window.innerWidth>=screen.width-2 && window.innerHeight>=screen.height-2);

  }

  function spawnHeart(){

    if(heartsEl.children.length>45) return;

    var h=document.createElement('span'), inner=document.createElement('i');

    var dur=7+Math.random()*7;

    h.className='heart';

    h.style.left=(Math.random()*96)+'%';

    h.style.fontSize=(16+Math.random()*30)+'px';

    h.style.animationDuration=dur+'s';

    inner.textContent=EMOJI[Math.floor(Math.random()*EMOJI.length)];

    inner.style.setProperty('--sway',(14+Math.random()*46)+'px');

    inner.style.animationDuration=(2+Math.random()*2.5)+'s';

    h.appendChild(inner); heartsEl.appendChild(h);

    setTimeout(function(){ if(h.parentNode) h.parentNode.removeChild(h); },dur*1000+300);

  }

  function updateHearts(){

    var fs=isFS();

    document.body.classList.toggle('fs',fs);

    if(fs && heartsOn && !heartTimer){

      for(var i=0;i<8;i++) setTimeout(spawnHeart,i*350);   // quick start so the screen isn't empty

      heartTimer=setInterval(spawnHeart,480);

    } else if((!fs || !heartsOn) && heartTimer){

      clearInterval(heartTimer); heartTimer=null;

      if(!fs) heartsEl.innerHTML='';

    }

  }

  hb.onclick=function(e){

    e.stopPropagation(); heartsOn=!heartsOn;

    hb.textContent = heartsOn ? '💗 Hearts: on' : '🤍 Hearts: off';

    if(!heartsOn) heartsEl.innerHTML='';

    updateHearts();

  };

  function fsChange(){

    updateHearts();

    var on=document.fullscreenElement||document.webkitFullscreenElement;

    fsB.textContent = on ? '✕ Exit full screen' : '⛶ Full screen';

    setTimeout(layout,150); setTimeout(layout,500);

  }

  document.addEventListener('fullscreenchange',fsChange);

  document.addEventListener('webkitfullscreenchange',fsChange);

  window.addEventListener('resize',layout);
 
  sheets.forEach(function(s){ vis(s,true,false); });

  setZ(); layout();

  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(layout);

  setTimeout(layout,200);

})();
</script>
</body></html>

"""
 