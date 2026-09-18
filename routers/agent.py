from fastapi import APIRouter, HTTPException, status
from schemas import ScanIngestRequest, SecurityReportResponse
from services.ai_agent import analyze_scan_output

router = APIRouter(prefix="/api/v1/agent", tags=["AI Security Agent"])

@router.post("/analyze", response_model=SecurityReportResponse)
async def analyze_scan(payload: ScanIngestRequest):
    try:
        report = await analyze_scan_output(payload)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent processing failed: {str(e)}"
        )
