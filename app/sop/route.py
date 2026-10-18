from fastapi import APIRouter, HTTPException
from config.logger import logger
from app.sop.services import process_sop
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/sop",
    tags=["SOP Services"]
)

@router.post("/generate-sop")
async def generate_sop():
    
    try:
        logger.info("[SOP Route] - Initiate process SOP document")
        
        result = await process_sop()
        
        logger.info("[SOP Route] - document successfully generated")

        return {
            "status": True,
            "message": "OK",
            "detail": result
        }
        
    except Exception as e:
        logger.error(f"[SOP Route] - Failed to initiate process SOP document with error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status":False,
                "message":None,
                "detail":f"Failed with error: {str(e)}"
            },
        )
