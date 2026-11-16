"""Build the self-contained HTML flip-book shown in the Streamlit app."""
 
import base64

import html

import mimetypes

from pathlib import Path

from urllib.parse import quote
 
CARD_ACCENTS = ["#9B5664", "#A75D68", "#7D4852", "#B06E75", "#80505A", "#986872"]

CARD_EMOJIS = ["🌟", "💖", "🌈", "🎈", "✨", "🌸", "🎊", "🍀"]
 
 
def _crumple_uri(seed: int, color: str, surface_scale: float, azimuth: int) -> str:

    """Return a data-URI SVG of crumpled paper (turbulence ridges lit from one side).
 
    Parameters

    ----------

    seed : int

        Noise seed, so every page has different creases.

    color : str

        Paper colour used as the lighting colour.

    surface_scale : float

        Crease depth. Higher means a more crumpled sheet.

    azimuth : int

        Direction of the light in degrees.
 
    Returns

    -------

    str

        A ``data:image/svg+xml`` URI usable in CSS ``url()``.

    """

    svg = (

        "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='800' viewBox='0 0 600 800' "

        "preserveAspectRatio='none'>"

        "<filter id='f' x='0' y='0' width='100%' height='100%'>"

        f"<feTurbulence type='turbulence' baseFrequency='0.007 0.010' numOctaves='5' seed='{seed}' result='n'/>"

        f"<feDiffuseLighting in='n' lighting-color='{color}' surfaceScale='{surface_scale}' diffuseConstant='1.2'>"

        f"<feDistantLight azimuth='{azimuth}' elevation='58'/></feDiffuseLighting></filter>"

        "<rect width='600' height='800' filter='url(#f)'/></svg>"

    )

    return "data:image/svg+xml," + quote(svg, safe="/:=,;'()")
 
 
def _photo_uri(path: Path) -> str:

    """Embed an image file as a base64 data URI."""

    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"

    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")
 
 
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

        photo_html = f"<div class='photo'><img src='{_photo_uri(base_dir / photo)}' alt=''></div>"

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

        f"<div class='fit ctitle'>{html.escape(config['title'])}</div>"

        f"<div class='csub'>{html.escape(config['subtitle'])}</div></div>"

    )
 
 
def _back_cover() -> str:

    return "<div class='in coverin'><div class='csub'>💖 with love, from the team 💖</div></div>"
 
 
def build_book_html(config: dict, messages: list, base_dir: Path) -> str:

    """Build the complete HTML document for the flip book.
 
    Parameters

    ----------

    config : dict

        Site config (title, subtitle, intro, closing, photo).

    messages : list

        Items with ``name`` and ``message`` keys.

    base_dir : Path

        Folder used to resolve the photo path.
 
    Returns

    -------

    str

        A full HTML document to pass to ``st.components.v1.html``.

    """

    # Face list: cover, intro, messages..., closing, [blank], back cover.

    # A face at an even position sits on the right (front of a sheet); odd on the left (back of a sheet).

    faces: list[tuple[str, str]] = [("cover", _cover(config))]

    faces.append(("page", _intro_page(config, base_dir, 1)))

    for i, item in enumerate(messages):

        faces.append(("page", _message_page(i, item["name"], item["message"], len(faces))))

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
 
    paper = "#FFF1EE"

    cover = "#E6BDC3"

    crumple_css = "".join(

        f".p{k}{{background-image:url(\"{_crumple_uri(11 + 7 * k, paper, 6.5 + k % 2, 40 + 55 * k)}\")}}"

        f".p{k}.cover{{background-image:url(\"{_crumple_uri(31 + 5 * k, cover, 8, 45 + 40 * k)}\")}}"

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

  font-family:Georgia,"Times New Roman",serif;color:#50383D}

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

.face{position:absolute;inset:0;overflow:hidden;background-color:#F3DFDC;background-size:100% 100%;

  backface-visibility:hidden;-webkit-backface-visibility:hidden}

.face.back{transform:rotateY(180deg)}

.rightpage{border-radius:2px 7px 7px 2px;box-shadow:3px 4px 10px rgba(70,35,45,.30)}

.leftpage{border-radius:7px 2px 2px 7px;box-shadow:-3px 4px 10px rgba(70,35,45,.30)}

/* spine shading + soft vignette + extra crease lines */

.face::before{content:"";position:absolute;inset:0;pointer-events:none;z-index:0}

.rightpage::before{background:

  linear-gradient(to right,rgba(70,30,40,.42),rgba(70,30,40,.10) 5%,transparent 14%),

  linear-gradient(to left,rgba(70,30,40,.14),transparent 6%),

  linear-gradient(118deg,transparent 44%,rgba(90,45,55,.16) 45%,rgba(255,255,255,.35) 46%,transparent 48%),

  linear-gradient(28deg,transparent 60%,rgba(90,45,55,.14) 61%,rgba(255,255,255,.30) 62%,transparent 64%)}

.leftpage::before{background:

  linear-gradient(to left,rgba(70,30,40,.42),rgba(70,30,40,.10) 5%,transparent 14%),

  linear-gradient(to right,rgba(70,30,40,.14),transparent 6%),

  linear-gradient(62deg,transparent 38%,rgba(90,45,55,.16) 39%,rgba(255,255,255,.35) 40%,transparent 42%),

  linear-gradient(152deg,transparent 66%,rgba(90,45,55,.14) 67%,rgba(255,255,255,.30) 68%,transparent 70%)}

.face.cover{border:calc(var(--pw)*.025) double #B4777E}

.face.cover::before{background:linear-gradient(to right,rgba(70,30,40,.30),transparent 10%)}

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

.pno{flex:none;margin-top:calc(var(--pw)*.02);text-align:center;color:#A0757A;

  font-size:calc(var(--pw)*.028);letter-spacing:.08em}

.tape{position:absolute;top:-1.2%;left:calc(50% - var(--pw)*.09);width:calc(var(--pw)*.18);

  height:calc(var(--pw)*.05);background:rgba(218,175,177,.85);border:1px solid rgba(156,100,105,.3);

  box-shadow:0 2px 3px rgba(104,65,72,.15);z-index:3}

.photo{flex:0 0 46%;margin-top:calc(var(--pw)*.04);padding:calc(var(--pw)*.02);background:#fff;

  box-shadow:0 3px 8px rgba(70,35,45,.3);transform:rotate(-1.2deg);min-height:0}

.photo img{width:100%;height:100%;object-fit:cover;display:block}

.closing{font-style:normal;font-weight:700;color:#89515B;display:flex;align-items:center;

  justify-content:center;text-align:center}

.coverin{align-items:center;justify-content:center;text-align:center}

.ctitle{flex:none!important;height:auto;color:#75434D;font-style:normal;font-weight:700;

  font-size:calc(var(--pw)*.095);line-height:1.2;overflow:visible!important}

.csub{margin-top:calc(var(--pw)*.05);color:#89515B;font-size:calc(var(--pw)*.05);text-align:center}

.bar{flex:none;display:flex;align-items:center;justify-content:center;gap:12px;padding:10px;

  font-family:system-ui,sans-serif}

.bar button{border:1px solid #B4777E;border-radius:6px;background:#F1DBDC;color:#75434D;

  font-weight:700;font-size:15px;padding:8px 16px;cursor:pointer;box-shadow:0 3px 8px rgba(104,65,72,.2)}

.bar button:hover:not(:disabled){background:#fff;transform:translateY(-1px)}

.bar button:disabled{opacity:.4;cursor:default}

#label{min-width:130px;text-align:center;color:#50383D;font-weight:600;font-size:14px}
</style></head>
<body>
<div id="wrap">
<div class="stage" id="stage"><div class="book" id="book">__SHEETS__</div></div>
<div class="bar">
<button id="prev">← Previous</button>
<span id="label"></span>
<button id="next">Next →</button>
<button id="fs">⛶ Full screen</button>
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

  function flip(s,toLeft){

    s._anim=true; s.style.zIndex=++zc; s.classList.toggle('flipped',toLeft);

    setTimeout(function(){ s._anim=false; setZ(); },1200);

  }

  function go(dir){

    if(dir>0 && cur<n){ flip(sheets[cur],true); cur++; }       // right page turns over to the left

    else if(dir<0 && cur>0){ cur--; flip(sheets[cur],false); } // left page turns back to the right

    else return;

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

    update(); fit();

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

    var req=el.requestFullscreen||el.webkitRequestFullscreen, p;

    try{ p=req.call(el); }catch(err){ p=Promise.reject(err); }

    if(p&&p.catch) p.catch(function(){

      try{ window.frameElement.requestFullscreen(); }

      catch(err2){ fsB.textContent='Press F11 for full screen'; }

    });

  };

  function fsChange(){

    var on=document.fullscreenElement||document.webkitFullscreenElement;

    fsB.textContent = on ? '✕ Exit full screen' : '⛶ Full screen';

    setTimeout(layout,150); setTimeout(layout,500);

  }

  document.addEventListener('fullscreenchange',fsChange);

  document.addEventListener('webkitfullscreenchange',fsChange);

  window.addEventListener('resize',layout);
 
  setZ(); layout();

  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(layout);

  setTimeout(layout,200);

})();
</script>
</body></html>

"""
 