import json
import os
import httpx
from schemas import ScanIngestRequest, SecurityReportResponse

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

SYSTEM_PROMPT = """
You are an expert security analyst. Analyze the provided network scan data for the given target.
Identify open ports, services, potential vulnerabilities, and suggested remediations.
Respond ONLY with a valid JSON object following this schema:
{
  "target": "<target_ip>",
  "summary": "<executive_summary>",
  "risk_score": <number_1_to_10>,
  "vulnerabilities": [
    {
      "port": <port_number>,
      "service": "<service_name>",
      "severity": "<LOW|MEDIUM|HIGH|CRITICAL>",
      "description": "<vulnerability_details>",
      "remediation": "<recommended_fix>"
    }
  ]
}
"""

async def analyze_scan_output(payload: ScanIngestRequest) -> SecurityReportResponse:
    prompt = f"Target: {payload.target}\nScan Data:\n{payload.raw_nmap_output}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
                "stream": False,
                "format": "json"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        parsed_json = json.loads(result.get("response", "{}"))
        return SecurityReportResponse(**parsed_json)
