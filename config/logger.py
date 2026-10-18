import os
import logging
from datetime import datetime

# 1. SIAPKAN DIREKTORI LOGS
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 2. ATUR NAMA FILE LOG HARIAN (Contoh: logs/log-2026-10-15.log)
current_date = datetime.now().strftime("%Y-%m-%d")
LOG_FILE_PATH = os.path.join(LOG_DIR, f"log-{current_date}.log")

# 3. FORMAT PENULISAN LOG
log_formatter = logging.Formatter(
    fmt="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Handler 1: Menulis ke file fisik di laptop (via Bind Mount Docker)
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setFormatter(log_formatter)

# Handler 2: Menampilkan live di terminal Docker screen
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

# 4. INISIALISASI LOGGER UTAMA APLIKASI
logger = logging.getLogger("clinical_assistant")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info("=== Sistem Logging Berhasil Dimuat dari app/logger.py ===")
