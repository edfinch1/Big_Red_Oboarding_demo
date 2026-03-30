"""
agents.py — Targeted AI Agents for Big Red Onboarding.
Strictly separates Insurance Compliance from SEO/Content Audits.
"""

import os
from typing import Optional, List

from openai import OpenAI
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared Schema
# ---------------------------------------------------------------------------

class ValidationResult(BaseModel):
    """Structured output for all audits."""

    seo_score: int = Field(0, ge=0, le=100)
    seo_feedback: str = ""
    insurance_expiry: str = "N/A"
    is_compliant: bool = False
    compliance_reasoning: str = ""
    missing_elements: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Specialized System Prompts
# ---------------------------------------------------------------------------

INSURANCE_SYSTEM_PROMPT = """You are the Lead Compliance Auditor for Big Red Group. 
Your goal is strictly to verify Insurance Compliance.

CRITICAL COMPLIANCE RULES:
- Liability Amount: MUST be at least $10,000,000 AUD. 
- Expiry Date: Today's date is 2026-03-30. If the expiry is on or before today, is_compliant is FALSE.
- Entity Match: Must mentions 'Public Liability' or 'General Liability'.

OUTPUT:
Only fill insurance-related fields. Leave seo_score as 0 and seo_feedback as empty string.
JSON Schema:
{
"insurance_expiry": "YYYY-MM-DD",
"is_compliant": boolean,
"compliance_reasoning": string,
"missing_elements": [string only if insurance elements are missing]
}"""

SEO_SYSTEM_PROMPT = """You are a Strict Brand Auditor for Big Red Group. 
Your goal is to ensure only the highest quality, high-conversion listings go live.

SCORING CRITIQUE (BE HARSH):
- Vibe (0-50 pts): Tone MUST be 'High-Octane', 'Adventurous', or 'Memorable'. If it is dry, clinical, or boring, score 0 for this section.
- Structure (0-50 pts): You MUST find the headers 'What to expect' and 'What's included'. 
  * If BOTH are missing: Maximum Total Score = 30.
  * If ONE is missing: Maximum Total Score = 55.

OUTPUT:
Only fill SEO-related fields. JSON Schema:
{
"seo_score": int,
"seo_feedback": string,
"missing_elements": [string list of missing sections]
}"""


# ---------------------------------------------------------------------------
# Targeted AI Logic
# ---------------------------------------------------------------------------

def run_insurance_audit(
    insurance_text: Optional[str] = None,
    insurance_images: Optional[List[str]] = None,
) -> ValidationResult:
    """Audit ONLY the insurance documentation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)
    user_content = []

    if insurance_text:
        user_content.append({"type": "text", "text": f"INSURANCE TEXT:\n{insurance_text}"})
    elif insurance_images:
        for b64 in insurance_images:
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"}
            })

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": INSURANCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format=ValidationResult,
    )
    return completion.choices[0].message.parsed


def run_seo_audit(description: str) -> ValidationResult:
    """Audit ONLY the listing description."""
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SEO_SYSTEM_PROMPT},
            {"role": "user", "content": f"LISTING DESCRIPTION:\n{description}"},
        ],
        response_format=ValidationResult,
    )
    return completion.choices[0].message.parsed
