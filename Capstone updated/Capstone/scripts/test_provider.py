import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extraction.llm_provider import ProviderPool

pool = ProviderPool()
print("Providers configured:", pool.providers)
for prov in ["cerebras_llama70b", "groq_llama70b", "gemini_flash", "sambanova_llama70b"]:
    try:
        res, used = pool.generate('Return JSON only: {"status": "ok"}', provider=prov)
        print(f"SUCCESS with {prov}! Result: {res.strip()[:60]}")
        break
    except Exception as e:
        print(f"Provider {prov} failed: {e}")
