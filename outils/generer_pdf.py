#!/usr/bin/env python3
"""Génère le CV PDF (assets/cv/maxence-baconnet-cv.pdf) à partir de la version imprimable du site.

Prérequis : pip install playwright && playwright install chromium
Usage     : python3 outils/generer_pdf.py   (depuis la racine du dépôt, après python3 build.py)
"""
import asyncio
import functools
import http.server
import threading
from pathlib import Path

from playwright.async_api import async_playwright

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "assets" / "cv" / "maxence-baconnet-cv.pdf"


def serveur():
    gestionnaire = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(RACINE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


async def main(port, executable=None):
    async with async_playwright() as p:
        options = {"executable_path": executable} if executable else {}
        navigateur = await p.chromium.launch(**options)
        page = await navigateur.new_page()
        await page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        await page.emulate_media(media="print")
        SORTIE.parent.mkdir(parents=True, exist_ok=True)
        await page.pdf(path=str(SORTIE), format="A4", print_background=True, prefer_css_page_size=True)
        await navigateur.close()
    print("CV généré :", SORTIE.relative_to(RACINE))


if __name__ == "__main__":
    import os
    httpd = serveur()
    asyncio.run(main(httpd.server_address[1], os.environ.get("CHROME")))
    httpd.shutdown()
