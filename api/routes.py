from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import List, Optional
from data.db import Session, Result, get_result_by_id, get_results_by_url, result_to_dict, insert_result
from classify.classify import classify_event
from ingestion.ingest import download_8k
from ingestion.parse import extract_text_from_html
import os
import uuid
import json
from config.config import EventConfig
import re

router = APIRouter()

class ClassificationRequest(BaseModel):
    url: str
    template: str = 'zero_shot.tpl'
    config: Optional[str] = None

class BatchRequest(BaseModel):
    urls: List[str]
    template: str = 'zero_shot.tpl'
    config: Optional[str] = None

def clean_filing_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_company_name(text):
    # Try to find the line before (Exact name of Registrant as specified in its charter)
    match = re.search(r'([A-Za-z0-9 .,&\-]+)\s*\(Exact name of Registrant as specified in its charter\)', text)
    if match:
        return match.group(1).strip()
    # Common company suffixes
    suffixes = r'(Inc\.|Corporation|Corp\.|LLC|Ltd\.|Co\.|Limited|Incorporated)'
    # Fallback: first line ending with a company suffix
    match = re.search(rf'^([A-Za-z0-9 .,&\-]+{suffixes})$', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: first occurrence in text
    match = re.search(rf'([A-Za-z0-9 .,&\-]+{suffixes})', text)
    if match:
        return match.group(1).strip()
    return 'Unknown'

@router.post("/classify/")
async def classify(req: ClassificationRequest):
    """Classify a single SEC filing."""
    print("TEMPLATE RECEIVED FROM FRONTEND:", req.template)
    print("USE_COT FLAG:", req.template == 'cot.tpl')
    DATA_DIR = "data/filings"
    os.makedirs(DATA_DIR, exist_ok=True)
    filename = req.url.split('/')[-1]
    html_path = os.path.join(DATA_DIR, filename)
    download_8k(req.url, html_path)
    raw_text = extract_text_from_html(html_path)
    filing_text = clean_filing_text(raw_text)
    config = EventConfig(req.config)
    allowed_events = config.get_event_types()
    result = classify_event(filing_text, allowed_events, req.template == 'cot.tpl')
    if req.template == 'zero_shot.tpl':
        from classify.validator import validate_zero_shot
        validation = validate_zero_shot(result, allowed_events)
    else:
        from classify.validator import validate_cot
        validation = validate_cot(result, allowed_events)
    try:
        parsed_output = json.loads(result)
    except Exception:
        parsed_output = result
    req_id = str(uuid.uuid4())
    company_name = extract_company_name(filing_text)
    single_result = {
        req_id: {
            'id': req_id,
            'url': req.url,
            'model_output': parsed_output,
            'validation': str(validation).lower(),
            'company': company_name
        }
    }
    # Map template to human-readable name
    template_name = 'Chain-of-Thought' if req.template == 'cot.tpl' else 'Zero-Shot'
    insert_result(id=req_id, url=req.url, model_output=parsed_output, validation=str(validation).lower(), company=company_name, template=template_name)
    return single_result

@router.post("/batch/")
async def batch(req: BatchRequest):
    """Process multiple SEC filings in batch."""
    DATA_DIR = "data/filings"
    os.makedirs(DATA_DIR, exist_ok=True)
    config = EventConfig(req.config)
    allowed_events = config.get_event_types()
    results = []
    for url in req.urls:
        filename = url.split('/')[-1]
        html_path = os.path.join(DATA_DIR, filename)
        download_8k(url, html_path)
        raw_text = extract_text_from_html(html_path)
        filing_text = clean_filing_text(raw_text)
        result = classify_event(filing_text, allowed_events, req.template == 'cot.tpl')
        if req.template == 'zero_shot.tpl':
            from classify.validator import validate_zero_shot
            validation = validate_zero_shot(result, allowed_events)
        else:
            from classify.validator import validate_cot
            validation = validate_cot(result, allowed_events)
        try:
            parsed_output = json.loads(result)
        except Exception:
            parsed_output = result
        req_id = str(uuid.uuid4())
        company_name = extract_company_name(filing_text)
        results.append({
            'id': req_id,
            'url': url,
            'model_output': parsed_output,
            'validation': str(validation).lower(),
            'company': company_name
        })
        # Map template to human-readable name
        template_name = 'Chain-of-Thought' if req.template == 'cot.tpl' else 'Zero-Shot'
        insert_result(id=req_id, url=url, model_output=parsed_output, validation=str(validation).lower(), company=company_name, template=template_name)
    return results

@router.get('/results/{result_id}')
def get_result(result_id: str):
    result = get_result_by_id(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result_to_dict(result)

@router.get('/results/all/')
def get_all_results():
    # print('get_all_results called')
    session = Session()
    results = session.query(Result).all()
    session.close()
    return [result_to_dict(r) for r in results]

@router.get('/results/by_url/')
def get_results_by_url_endpoint(url: str = Query(..., description="Filing URL to search for")):
    results = get_results_by_url(url)
    # Always return a list, even if empty (never 404)
    return [result_to_dict(r) for r in results]

@router.delete('/results/all/', status_code=status.HTTP_204_NO_CONTENT)
def delete_all_results():
    session = Session()
    session.query(Result).delete()
    session.commit()
    session.close()
    return

@router.delete('/results/{result_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_result(result_id: str):
    session = Session()
    result = get_result_by_id(result_id)
    if not result:
        session.close()
        raise HTTPException(status_code=404, detail="Result not found")
    session.delete(result)
    session.commit()
    session.close()
    return
