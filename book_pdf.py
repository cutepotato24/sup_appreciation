"""Turn the flip-book HTML into a print-ready PDF (one book page per PDF page)."""
 
import subprocess

import sys
 
_RENDER = r"""

import base64, sys

from playwright.sync_api import sync_playwright

html = sys.stdin.buffer.read().decode("utf-8")

with sync_playwright() as p:

    browser = p.chromium.launch()

    page = browser.new_page(viewport={"width": 1300, "height": 800})

    page.set_content(html, wait_until="load")

    page.wait_for_timeout(600)
 
    # The crumpled-paper textures are SVG filters. Turn each one into a small JPEG so the PDF stays light.

    css = ""

    for k in range(4):

        for sel, rule in ((".face.p%d:not(.cover)" % k, ".p%d" % k), (".face.cover.p%d" % k, ".p%d.cover" % k)):

            bg = page.evaluate(

                "s => { const e = document.querySelector(s); return e ? getComputedStyle(e).backgroundImage : '' }", sel

            )

            if not bg.startswith('url("data:image/svg+xml'):

                continue

            tex = browser.new_page(viewport={"width": 750, "height": 1000})

            tex.set_content("<body style='margin:0'><div id='t'></div></body>")

            tex.add_style_tag(

                content="#t{width:750px;height:1000px;background-image:%s;background-size:100%% 100%%}" % bg

            )

            tex.wait_for_timeout(200)

            jpg = tex.screenshot(type="jpeg", quality=82)

            tex.close()

            css += "%s{background-image:url(data:image/jpeg;base64,%s)!important}" % (

                rule, base64.b64encode(jpg).decode("ascii"))

    page.add_style_tag(content=css)
 
    page.emulate_media(media="print")

    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")

    page.wait_for_timeout(300)

    pdf = page.pdf(prefer_css_page_size=True, print_background=True)

    browser.close()

sys.stdout.buffer.write(pdf)

"""
 
 
def build_book_pdf(book_html: str) -> bytes | None:

    """Render the book HTML to PDF with headless Chromium.
 
    Parameters

    ----------

    book_html : str

        Full HTML document from ``build_book_html``.
 
    Returns

    -------

    bytes | None

        PDF bytes, or ``None`` if Playwright/Chromium is not installed or rendering failed.

    """

    try:

        result = subprocess.run(

            [sys.executable, "-c", _RENDER],

            input=book_html.encode("utf-8"),

            capture_output=True,

            timeout=90,

            check=True,

        )

    except (subprocess.SubprocessError, OSError):

        return None

    return result.stdout if result.stdout.startswith(b"%PDF") else None
 