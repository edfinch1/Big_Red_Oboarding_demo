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

SEO_SYSTEM_PROMPT = """You are a Brand Auditor for Big Red Group. 
Your goal is to provide a granular quality score for experience listings.

SCORING RUBRIC (0-100):
- Tone & Vibe (0-50 pts): 
  * 50: High-Octane, Adventure-focused, Memorable.
  * 25: Professional and clear, but lacks 'Excitement'.
  * 10: Dry, clinical, or robotic.
- Structure & Flow (0-50 pts):
  * 50: Includes clear 'What to expect' and 'What's included' sections.
  * 30: Good info, but missing one of the standard headers.
  * 10: Missing both headers and lacks clear structure.

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
