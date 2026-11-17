"""
Automated genuine screenshot capture tool for CineAI using Google Chrome Headless.
Ensures full DOM and canvas rendering before capturing.
"""
import subprocess
import time
import urllib.request
import sys
import os
import shutil

APP_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR_1 = os.path.join(APP_DIR, "CineAI_College_Submission", "screenshots")
OUTPUT_DIR_2 = os.path.join(os.path.dirname(APP_DIR), "CineAI_College_Submission", "screenshots")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PAGES = [
    ("01_home_page.png", "http://127.0.0.1:8501/?nav=home"),
    ("02_trending_movies.png", "http://127.0.0.1:8501/?nav=home"),
    ("03_movie_search.png", "http://127.0.0.1:8501/?nav=search"),
    ("04_movie_rating.png", "http://127.0.0.1:8501/?nav=search"),
    ("05_user_preferences.png", "http://127.0.0.1:8501/?nav=preferences"),
    ("06_personalized_recommendations.png", "http://127.0.0.1:8501/?nav=recommendations"),
    ("07_user_dashboard.png", "http://127.0.0.1:8501/?nav=dashboard"),
    ("08_ai_model_explanation.png", "http://127.0.0.1:8501/?nav=explanation"),
    ("09_interactive_model_playground.png", "http://127.0.0.1:8501/?nav=playground")
]

def capture_all():
    os.makedirs(OUTPUT_DIR_1, exist_ok=True)
    os.makedirs(OUTPUT_DIR_2, exist_ok=True)

    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "127.0.0.1",
        "--server.headless", "true"
    ]
    proc = subprocess.Popen(cmd, cwd=APP_DIR)

    try:
        # Wait until server is fully loaded
        ready = False
        for _ in range(40):
            time.sleep(1.0)
            try:
                with urllib.request.urlopen("http://127.0.0.1:8501", timeout=3) as resp:
                    if resp.getcode() == 200:
                        ready = True
                        break
            except Exception:
                pass

        if not ready:
            print("Server not ready.")
            return False

        print("Server ready on 127.0.0.1:8501. Warming up Streamlit models and UI cache...")
        # Warmup call using Chrome
        warmup_cmd = [
            CHROME_PATH,
            "--headless=new",
            "--disable-gpu",
            "--window-size=1440,920",
            "--virtual-time-budget=10000",
            "http://127.0.0.1:8501/?nav=home"
        ]
        subprocess.run(warmup_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(4)
        print("Warmup complete. Capturing high-resolution screenshots...")

        for filename, url in PAGES:
            out_file = os.path.join(OUTPUT_DIR_1, filename)
            chrome_cmd = [
                CHROME_PATH,
                "--headless=new",
                "--disable-gpu",
                "--window-size=1440,920",
                "--hide-scrollbars",
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=8000",
                f"--screenshot={out_file}",
                url
            ]
            subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if os.path.exists(out_file):
                size = os.path.getsize(out_file)
                print(f"Captured {filename}: {size} bytes")
                shutil.copy2(out_file, os.path.join(OUTPUT_DIR_2, filename))
            time.sleep(1)

        return True
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    capture_all()
