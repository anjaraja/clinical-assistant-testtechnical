import io
import os
import json
import asyncio

from docx import Document
from sqlalchemy.orm import Session

from config.sop_table import SOPTable
from openai import OpenAI

from config.logger import logger

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY") 
)

async def review_patient_documents(files: list, db: Session) -> dict:
    
    combined_patient_text = []
    summary_details = []

    try:
        for file in files:
            try:
                file_bytes = await file.read()
                clear_text = extract_text_from_ram_docx(file_bytes)
                
                combined_patient_text.append(f"--- FILE DATA: {file.filename} ---\n{clear_text}\n--- END OF FILE DATA: {file.filename} ---")
                summary_details.append({"filename": file.filename, "words": len(clear_text.split())})
            except Exception as e:
                logger.error(f"[Assistant Services] Failed while extracting {file.filename}")
                raise e

        final_patient_context = "\n\n".join(combined_patient_text)
        
        logger.info(f"[Assistant Services] Processing first chunk as summary")
        patient_text_chunk = get_first_chunk_for_embedding(final_patient_context, max_words=300)
        logger.info(f"[Assistant Services] First chunk process success: {patient_text_chunk}")
        
        try:
            total_sop_rows = db.query(SOPTable).count() 
            if total_sop_rows == 0:
                logger.warning("[Assistant Services] SOPTable is empty. Stopping process.")
                raise ValueError("No SOP data available in the database. Please generate SOP vector using SOP service at http://localhost:9999/api/sop/generate-sop")

            patient_vector = await get_patient_embedding(patient_text_chunk)
            
            logger.info(f"[Assistant Services] Start query finding relevant sop by vector. Get top 7 row that most relevant")
            relevant_sop_records = db.query(SOPTable) \
                .order_by(SOPTable.embedding.cosine_distance(patient_vector)) \
                .limit(7) \
                .all()
            logger.info(f"[Assistant Services] Finish query process")
                
            sop_contexts = []
            for record in relevant_sop_records:
                sop_contexts.append(f"--- RULS DOCUMENT: {record.source_document} ---\n{record.text_content}")
                
            final_sop_context = "\n\n".join(sop_contexts)
        except Exception as db_err:
            logger.error(f"[Assistant Services] Failed while doing query, with error: {str(db_err)}")
            raise RuntimeError(f"Failed while doing query, with error: {str(db_err)}")

        logger.info(f"[Assistant Services] Succesfull get {len(relevant_sop_records)} SOP rules from database.")
        
        ai_structured_analysis = await analyze_case_with_llm(final_patient_context, final_sop_context)
        
        return {
            "status": True,
            "meta_uploaded_files": summary_details,
            "clinical_review_report": ai_structured_analysis
        }

    except Exception as main_error:

        logger.error(f"[Assistant Services] Failed when processing embedding or text generation. prepare fallback json format. Error: {str(main_error)}")
        
        return {
            "status": False,
            "meta_uploaded_files": [{"filename": f.filename, "words": 0} for f in files],
            "clinical_review_report": {
                "case_id": "N/A",
                "patient_id": "N/A",
                "patient_name": "N/A",
                "is_compliant": False,
                "require_human_review": True,
                "inconsistencies_found": [f"System Error Exception: {str(main_error)}"],
                "missing_documents": ["Failed to process document."],
                "validation_details": {},
                "review_summary":""
            }
        }

def extract_text_from_ram_docx(file_contents: bytes) -> str:
    try:
        docx_file = io.BytesIO(file_contents)
        doc = Document(docx_file)
        full_text = []

        # extract text from paragraph
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())

        # Extract text from tables and add "|" as delimiter column.
        for table in doc.tables:
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    row_data.append(cell_text)
                if row_data:
                    full_text.append(" | ".join(row_data))

        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"[Assistant Services] Failed extracting text with error: {str(e)}")
        raise ValueError(f"Failed extracting text with error: {str(e)}")

def get_first_chunk_for_embedding(text: str, max_words: int = 300) -> str:
    words = text.split()
    preview_words = words[:max_words]
    chunk_text = " ".join(preview_words)
    return chunk_text

async def get_patient_embedding(text_chunk: str) -> list:
    try:
        response = client.embeddings.create(
            model="gemini-embedding-001",
            input=text_chunk
        )
        logger.info(f"[Assistant Services] Embedding Raw Text : {text_chunk}")
        log_response = response.model_dump()
        log_response['data'][0]['embedding'] = "Hide for log"
        logger.info(f"[Assistant Service] Embedding Response : {log_response}")
        
        # PERBAIKAN: Akses objek data indeks pertama [0] baru ambil properti .embedding
        vector_result = response.data[0].embedding
        vector_result = vector_result[:2048]
        return vector_result
    except Exception as e:
        logger.error(f"[Assistant Service] Failed while execute the embedding process, with error: {str(e)}")
        raise ConnectionError(f"Failed while execute the embedding process, with error: {str(e)}")


async def analyze_case_with_llm(patient_context: str, sop_context: str) -> dict:
    
    logger.info("[Assistant Service] Start Text Generation process")
    system_instruction = (
        "You are Clinical Document Review Assistant, Proffessional AI Medical Assistant.\n"
        "Your main task is to balidate a given set of patient case documents based on the rules in the attached official SOP document.\n\n"
        "CRITICAL DATA INTEGRITY RULES:\n"
        "1. Check and validate 'Patient ID' and 'Case ID' column for each patient document.\n"
        "2. If an document have DIFFERENT Patient ID/CASE ID or NOT attach the ID, You must change 'is_compliant' to be false, 'require_human_review' to be true, and describe the detail about that in 'inconsistencies_found'\n"
        "3. If there any mandatory documents missing from the SOP list, please describe that in 'missing_documents'.\n"
        "4. To make the result consistence, your JSON must include this defailed information: case_id, patient_id, patient_name, is_compliant, require_human_review, inconsistencies_found, missing_documents, validation_detail and review_summary.\n"
        "5. Your output must comply 100% with the requested JSON format structure and always give 'review_summary' as information from your analysis. Do not give small talk text!"
    )
    
    user_prompt = (
        f"=== OFFICIAL REFERENCE MEDICAL SOP DOCUMENT ===\n{sop_context}\n\n"
        f"=== MEDICAL RECORD DOCUMENT OF THE PATIENT BEING EXAMINING ===\n{patient_context}\n\n"
        f"Do the Analysis NOW and give evaluated structure results with valid JSON format."
    )
    
    try:
        response = client.chat.completions.create(
            model="gemini-3.8-flash",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        logger.info(f"[Assistant Service] Completions Response : {response}")
        
        raw_json_text = response.choices[0].message.content

        completion_token = response.usage.completion_tokens
        prompt_token = response.usage.prompt_tokens
        total_token = response.usage.total_tokens
        thinking_token = total_token - prompt_token - completion_token

        input_price = prompt_token * 0.00000075
        output_price = completion_token * 0.00000375
        thinking_price = thinking_token * 0.00000375
        total_cost_text_generation = input_price + output_price + thinking_price

        logger.info(f"[Assistant Service] Token Usage and Price : Input [{prompt_token},${input_price}] | Output [{completion_token},${output_price}] | Thinking [{thinking_token},${thinking_price}] | Total Cost [{total_cost_text_generation}]")
        
        parsed_result = json.loads(raw_json_text)
        return parsed_result
        
    except json.JSONDecodeError as je:
        logger.error(f"[Assistant Service] Failed when read JSON files from the response, with error: {str(je)}")
        raise ValueError("Failed when read JSON files from the response")
    except Exception as e:
        logger.error(f"[Assistant Service] Failed while processing Text Generation LLM, with error: {str(e)}")
        raise RuntimeError(f"Failed while processing Text Generation LLM, with error: {str(e)}")




