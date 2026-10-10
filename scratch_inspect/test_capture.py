import subprocess
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1] / "Capstone updated/Capstone"
print("Starting backend...")
proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.app.api:app", "--host", "127.0.0.1", "--port", "8000"], cwd=str(ROOT))

try:
    time.sleep(12)  # wait for startup
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        print("Navigating to app...")
        page.goto("http://127.0.0.1:8000", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        
        print("Clicking Analyzer tab...")
        page.click("button:has-text('Analyzer')")
        page.wait_for_timeout(2500)
        
        out_path = Path(__file__).resolve().parent / "current_app_analyzer.png"
        page.screenshot(path=str(out_path), full_page=False)
        print(f"Captured {out_path}")
        browser.close()
finally:
    proc.terminate()
