from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session

from config.logger import logger
from config.database import get_db  # Mengambil fungsi konektor session database Anda
from app.assistant.services import review_patient_documents

# Inisialisasi APIRouter khusus untuk modul Assistant (Grup Route)
router = APIRouter(
    prefix="/assistant",
    tags=["Clinical Assistant Analysis"]
)

@router.post("/review")
async def trigger_clinical_document_review(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Endpoint Real-Time Utama: Menerima bundel dokumen pasien (.docx),
    mengekstrak teks langsung di memori RAM, melakukan validasi silang identitas,
    mencocokkan aturan SOP via pgvector, dan mengembalikan hasil analisis JSON terstruktur.
    """
    logger.info(f"[Assistant Route] New request. Total file: {len(files)}")
    
    # 1. Validasi Awal: Pastikan minimal ada file yang diunggah
    if not files or len(files) == 0:
        logger.warning("[Assistant Route] New request has no uploaded files.")
        raise HTTPException(
            status_code=400,
            detail="Failed: Files cannot be empty."
        )
        
    # 2. Validasi Ekstensi: Memastikan semua file yang masuk berformat .docx
    for file in files:
        if not file.filename.endswith('.docx'):
            logger.warning(f"[Assistant Route] Invalid file format: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File format '{file.filename}' is invalid. All patient case must be .docx format."
            )
            
    try:
        logger.info("[Assistant Route] Starting review patient document.")
        analysis_result = await review_patient_documents(files, db)
        logger.info("[Assistant Route] Finish review patient document.")
        return analysis_result
        
    except Exception as e:
        # Catat detail error ke log harian Anda jika AI atau database tersendat
        logger.error(f"[Assistant Route] Failed with error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed with error: {str(e)}"
        )
