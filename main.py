from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from config.logger import logger

from config.sop_table import SOPTable
from config.database import run_database_migrations

from app.sop.route import router as sop_router
from app.assistant.route import router as assistant_router

run_database_migrations()

app = FastAPI(
    title="Clinical Assistant",
    description="Using OpenRouter as AI Provider and using free model",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sop_router, prefix="/api")
app.include_router(assistant_router, prefix="/api")

# =====================================================================
# 2. MIDDLEWARE UNTUK MEMANTAU HTTP REQUEST
# =====================================================================
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     logger.info(f"Request Masuk: {request.method} {request.url.path}")
    
#     start_time = datetime.now()
#     response = await call_next(request)
#     process_time = (datetime.now() - start_time).total_seconds() * 1000
    
#     logger.info(f"Request Selesai: {request.method} {request.url.path} - Status: {response.status_code} - Waktu Proses: {process_time:.2f}ms")
    
#     return response

# =====================================================================
# 3. ENDPOINT ROUTE
# =====================================================================

@app.get("/", tags=["Root"])
def read_root():
    logger.info("Akses ke endpoint root (/) berhasil dilakukan.")
    return {
        "status": "Aplikasi Berjalan",
        "service": "Clinical Document Review Assistant",
        "timestamp": datetime.now().isoformat()
    }

# @app.get("/health-check", tags=["Monitoring"])
# def health_check():
#     db_status = "Connected (Simulated)"
#     openrouter_status = "Ready (Simulated)"
    
#     logger.info(f"Menjalankan Health Check Sistem. DB: {db_status}, OpenRouter: {openrouter_status}")
#     return {
#         "status": "Healthy",
#         "database": db_status,
#         "ai_provider": openrouter_status
#     }

# @app.get("/test-error", tags=["Monitoring"])
# def test_error():
#     logger.warning("User memicu simulasi error pada endpoint /test-error")
#     try:
#         pembagian_nol = 10 / 0
#     except Exception as e:
#         logger.error(f"Terjadi kesalahan fatal pada logika matematika: {str(e)}", exc_info=True)
#         return {
#             "status": "Error Tercatat",
#             "detail": str(e),
#             "pesan": "Error ini telah sukses dicatat ke dalam berkas log harian."
#         }
