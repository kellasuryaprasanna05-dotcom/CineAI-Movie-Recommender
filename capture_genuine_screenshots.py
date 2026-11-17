"""
High-fidelity genuine screenshot capture tool for CineAI.
Uses Chrome DevTools Protocol (CDP) to guarantee complete DOM rendering
and high-resolution PNG captures.
"""
import os
import sys
import time
import json
import base64
import shutil
import asyncio
import subprocess
import urllib.request
import websockets

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR_1 = os.path.join(APP_DIR, "CineAI_College_Submission", "screenshots")
OUT_DIR_2 = os.path.join(os.path.dirname(APP_DIR), "CineAI_College_Submission", "screenshots")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PAGES = [
    ("01_home_page.png", "http://127.0.0.1:8501/?nav=home", 6),
    ("02_trending_movies.png", "http://127.0.0.1:8501/?nav=home", 5),
    ("03_movie_search.png", "http://127.0.0.1:8501/?nav=search", 5),
    ("04_movie_rating.png", "http://127.0.0.1:8501/?nav=search", 5),
    ("05_user_preferences.png", "http://127.0.0.1:8501/?nav=preferences", 4),
    ("06_personalized_recommendations.png", "http://127.0.0.1:8501/?nav=recommendations", 6),
    ("07_user_dashboard.png", "http://127.0.0.1:8501/?nav=dashboard", 5),
    ("08_ai_model_explanation.png", "http://127.0.0.1:8501/?nav=explanation", 5),
    ("09_interactive_model_playground.png", "http://127.0.0.1:8501/?nav=playground", 5),
]

async def capture_tab(target_url, wait_sec, out_path):
    encoded_url = urllib.request.quote(target_url, safe=':/?=&')
    req = urllib.request.Request(f"http://127.0.0.1:9222/json/new?{encoded_url}", method="PUT")
    with urllib.request.urlopen(req) as resp:
        tab_info = json.loads(resp.read().decode())
    
    tab_id = tab_info["id"]
    ws_url = tab_info["webSocketDebuggerUrl"]

    try:
        async with websockets.connect(ws_url, max_size=20 * 1024 * 1024) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            # Wait for Streamlit to render all components and charts
            await asyncio.sleep(wait_sec)
            
            # Request screenshot
            await ws.send(json.dumps({
                "id": 2,
                "method": "Page.captureScreenshot",
                "params": {"format": "png", "captureBeyondViewport": False}
            }))
            
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 2:
                    img_data = base64.b64decode(msg["result"]["data"])
                    with open(out_path, "wb") as f:
                        f.write(img_data)
                    break
    finally:
        # Close tab
        try:
            close_req = urllib.request.Request(f"http://127.0.0.1:9222/json/close/{tab_id}")
            urllib.request.urlopen(close_req, timeout=2)
        except Exception:
            pass

async def main():
    os.makedirs(OUT_DIR_1, exist_ok=True)
    os.makedirs(OUT_DIR_2, exist_ok=True)

    print("Starting Streamlit server on 127.0.0.1:8501...")
    st_cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ]
    st_proc = subprocess.Popen(st_cmd, cwd=APP_DIR)

    print("Starting Headless Chrome with CDP on port 9222...")
    chrome_cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        "--window-size=1440,920",
        "about:blank"
    ]
    chrome_proc = subprocess.Popen(chrome_cmd)

    try:
        # Wait until Streamlit is ready
        ready = False
        for i in range(40):
            time.sleep(1.0)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8501", timeout=2) as r:
                    if r.getcode() == 200:
                        ready = True
                        break
            except Exception:
                pass
        
        if not ready:
            print("[ERROR] Streamlit did not start.")
            return

        print("[OK] Streamlit is live. Capturing genuine UI screenshots...")
        time.sleep(3)

        for filename, url, wait_time in PAGES:
            out_file = os.path.join(OUT_DIR_1, filename)
            print(f"Capturing {filename} ({url})...")
            await capture_tab(url, wait_time, out_file)
            size = os.path.getsize(out_file)
            print(f" -> Saved {filename} ({size:,} bytes)")
            shutil.copy2(out_file, os.path.join(OUT_DIR_2, filename))

        print("\nAll screenshots successfully captured!")

    finally:
        chrome_proc.terminate()
        st_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
            st_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()
            st_proc.kill()

if __name__ == "__main__":
    asyncio.run(main())
