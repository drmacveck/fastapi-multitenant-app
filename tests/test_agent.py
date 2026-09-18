import pytest
from unittest.mock import MagicMock, patch
from schemas import ScanIngestRequest, SecurityReportResponse
from services.ai_agent import analyze_scan_output

@pytest.mark.asyncio
async def test_analyze_scan_output_success():
    mock_payload = ScanIngestRequest(
        target="192.168.1.1",
        raw_nmap_output="PORT 80/tcp OPEN http"
    )
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"target": "192.168.1.1", "summary": "Port 80 open", "risk_score": 5, "vulnerabilities": [{"port": 80, "service": "http", "severity": "MEDIUM", "description": "Unencrypted HTTP", "remediation": "Enable HTTPS"}]}'
    }
    mock_response.raise_for_status = lambda: None

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        report = await analyze_scan_output(mock_payload)
        
        assert isinstance(report, SecurityReportResponse)
        assert report.target == "192.168.1.1"
        assert report.risk_score == 5
        assert len(report.vulnerabilities) == 1
        assert report.vulnerabilities[0].port == 80
