import os
import asyncio

from docx import Document
from openai import OpenAI

from config.database import SessionLocal
from config.sop_table import SOPTable

from config.logger import logger

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY")
)

SOP_FOLDER_PATH = os.path.join("storage", "sop")

async def process_sop():
    logger.info(f"[SOP Services] Start sop document process")

    db = SessionLocal()

    try:

        local_files = get_local_docx_files()

        db_records = db.query(SOPTable.source_document).distinct().all()
        database_files = {record.source_document for record in db_records}
        
        # get difference document
        deleted_files = list(database_files - local_files)
        
        if deleted_files:
            logger.info(f"[SOP Services] Start deleting by not exist files by source_document in {deleted_files}")

            db.query(SOPTable).filter(SOPTable.source_document.in_(deleted_files)).delete(synchronize_session=False)
            db.commit()

            logger.info(f"[SOP Services] Row with not exists file by source_document deleted")
        else:
            logger.info(f"[SOP Services] Skip deleting row")
            
        files_to_process = list(local_files)
        
        summary_details = []
        total_all_chunks = 0
        for file_name in files_to_process:

            logger.info(f"[SOP Services] Process deleting row by exists file. source_document: {file_name}")
            db.query(SOPTable).filter(SOPTable.source_document == file_name).delete(synchronize_session=False)
            db.commit()
            
            file_path = os.path.join(SOP_FOLDER_PATH, file_name)
            try:

                logger.info(f"[SOP Services] Start extracting {file_name} text")
                clear_text = extract_text_from_docx(file_path)
                logger.info(f"[SOP Services] Finish extracting '{file_name}'. Text length: {len(clear_text)}. First 150 text: \"{clear_text[:150]}...\". Word Length: {len(clear_text.split())}")

                logger.info(f"[SOP Services] Start chunk process {file_name}")
                chunks = split_text_into_chunks(clear_text, chunk_size=400, overlap=50)
                logger.info(f"[SOP Services] Chunk '{file_name}' process success. Chunk length: {len(chunks)}")
                
                for index, chunk_content in enumerate(chunks):

                    logger.info(f"[SOP Services] Start request embedding to openrouter to get vector")
                    vector = await get_embedding_from_openrouter(chunk_content)
                    logger.info(f"[SOP Services] -> Chunk #{index+1} vectored. Dimensi: {len(vector)} | Sampel Angka: {vector[:3]}...")

                    new_chunk = SOPTable(
                        source_document=file_name,
                        text_content=chunk_content,
                        embedding=vector
                    )


                    logger.info(f"[SOP Services] add new chunk")
                    db.add(new_chunk)

                    
                    if len(chunks) > 1:
                        await asyncio.sleep(1.5)

                db.commit()
                logger.info(f"[SOP Services] Successfully commit and inserting new chunks")
                
                total_all_chunks += len(chunks)
                summary_details.append({
                    "file_name": file_name,
                    "status": "Extract, Chunking and insert to database successfull",
                    "total_characters": len(clear_text)
                })
            except Exception as e:
                logger.error(f"[SOP Services] Failed to extract. With error: {str(e)}")
                db.rollback() 
                summary_details.append({
                    "file_name": file_name,
                    "status": f"with error: {str(e)}",
                    "total_characters": 0
                })
            
        return {
            "status": "Sync_Complete",
            "total_deleted_from_db": len(deleted_files),
            "total_processed_or_updated": len(files_to_process),
            "details": summary_details
        }

    finally:
        db.close()

def get_local_docx_files():
    # Check exists folder
    if not os.path.exists(SOP_FOLDER_PATH):
        os.makedirs(SOP_FOLDER_PATH)
        
    all_files = os.listdir(SOP_FOLDER_PATH)

    # olny take file format .docx
    docx_files = {f for f in all_files if f.endswith('.docx')}
    
    logger.info(f"[SOP Services] Files on directory found {len(docx_files)} file .docx")

    return docx_files


def extract_text_from_docx(file_path: str) -> str:
    
    doc = Document(file_path)
    full_text = []

    # extract text from paragraph
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())

    # extract text from table and add "|" as delimiter
    for table in doc.tables:
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                row_data.append(cell_text)
            if row_data:
                # merge text
                full_text.append(" | ".join(row_data))

    return "\n".join(full_text)

def split_text_into_chunks(text: str, chunk_size: int = 400, overlap: int = 50) -> list:
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        # extract word from i until i+chunk_size
        chunk_words = words[i:i + chunk_size]
        # merge extracted word
        chunk_text = " ".join(chunk_words)
        
        if chunk_text.strip():
            chunks.append(chunk_text)
            
    return chunks

async def get_embedding_from_openrouter(text_chunk: str):
    try:
        
        response = client.embeddings.create(
            model="gemini-embedding-001",
            input=text_chunk
        )
        logger.info(f"[SOP Services] Embedding Raw Text : {text_chunk}")
        log_response = response.model_dump()
        log_response['data'][0]['embedding'] = "Hide for log"
        logger.info(f"[SOP Services] Embedding Response : {log_response}")
        
        # Ekstraksi array angka hasil kalkulasi AI
        vector_result = response.data[0].embedding
        vector_result = vector_result[:2048]
        return vector_result
        
    except Exception as e:
        logger.error(f"[AI Embedding] Failed while processing embedding, with error: {str(e)}")
        raise e