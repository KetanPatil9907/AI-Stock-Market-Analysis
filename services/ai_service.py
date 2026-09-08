"""
AIService
---------
Single reusable wrapper around whichever AI provider you configure.
Configure via environment variable AI_API_KEY. If not set, is_configured
is False and callers (the agents) fall back to their own logic rather
than pretending an AI call happened.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    pass


class AIService:
    def __init__(self):
        self.api_key = os.environ.get("AI_API_KEY", "").strip()
        self.model = os.environ.get("AI_MODEL", "claude-sonnet-4-6")
        self.is_configured = bool(self.api_key)
        self._client = None

        if self.is_configured:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                logger.warning(
                    "AI_API_KEY is set but the 'anthropic' package isn't "
                    "installed. Run: pip install anthropic"
                )
                self.is_configured = False

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.is_configured:
            raise AIServiceError("AI_API_KEY is not configured.")

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(
                block.text for block in response.content if block.type == "text"
            )
            text = text.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("AI response was not valid JSON: %s", e)
            raise AIServiceError("AI returned an unparseable response.")
        except Exception as e:
            logger.error("AI call failed: %s", e)
            raise AIServiceError(str(e))

    def analyze_stock(self, stock_data: dict) -> dict:
        system_prompt = (
            "You are a financial education assistant analyzing a stock for "
            "an educational platform. You must use ONLY the data provided — "
            "never invent numbers. If data is insufficient, say so explicitly. "
            "Never give guaranteed advice or say 'definitely buy'. "
            "Respond with ONLY a JSON object, no other text, matching this "
            "schema: {\"company_overview\": str, \"fundamental_score\": int, "
            "\"technical_score\": int, \"growth_score\": int, \"risk_score\": int, "
            "\"overall_score\": int, \"strengths\": [str], \"weaknesses\": [str], "
            "\"opportunities\": [str], \"risks\": [str], \"important_factors\": [str], "
            "\"conclusion\": str, \"classification\": "
            "\"STRONG|POSITIVE|NEUTRAL|CAUTION|HIGH RISK\"}"
        )
        user_prompt = f"Stock data:\n{json.dumps(stock_data, indent=2)}"
        return self.generate_json(system_prompt, user_prompt)