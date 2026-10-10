HAZRA BARI VIRTUAL DUAL TEMPLE — UPDATED PACKAGE

Main Streamlit entry file: bittu.py

Deploy with: streamlit run bittu.py

Daily dynamic timing behavior:
- The Panchang page requests the current date in Durgapur IST on each app run.
- Sun/moon timing lookup uses that date dynamically; results are cached for up to one hour per date, not hard-coded.
- Astronomy API timestamps are parsed as ISO-8601 and converted to Asia/Kolkata (IST).
- If the API is unreachable, Astral can calculate sunrise/sunset; unavailable moonrise/moonset are shown as unavailable rather than guessed.
- Astronomical times remain visible if Navamsha Panchang credentials are missing. Tithi/Nakshatra/Yoga/Paksha still require a valid Navamsha API key.
- A visible, always-lit virtual Akhand Diya status appears on Maa Durga and Mahadev Shiva Darshan cards and in Aarti.
- The Shiva deity image is bundled as mahadev_shiva.png.

Streamlit Secrets for live Panchang details:
PANCHANG_API_URL = "https://api.navamsha.in/api/v1/panchang/full"
PANCHANG_API_KEY = "your-valid-Navamsha-key"

Astronomical data attribution: https://sunrise-sunset.org/api

ModuleNotFoundError fix: bittu.py treats Astral as optional so the app can start even if dependencies have not yet been installed. Keep requirements.txt in the repository root to enable Astral fallback calculations.
