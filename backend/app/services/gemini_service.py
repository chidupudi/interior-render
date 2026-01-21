"""
Gemini Service - Translates natural language to structured actions.
Uses Google's Gemini API for intent recognition and action generation.
"""

import json
import re
from typing import Optional
import google.generativeai as genai

from app.models.schemas import GeminiResponse, GeminiAction, SceneState
from app.utils.asset_library import ASSET_LIBRARY, ALLOWED_ASSET_TYPES


SYSTEM_PROMPT = """You are an interior design assistant that translates natural language requests into structured JSON actions.

## STRICT RULES:
1. You MUST output ONLY valid JSON - no explanations, no markdown, no extra text
2. You can ONLY use these tools:
   - set_wall_color(room_id, hex_color)
   - add_asset(asset_type, asset_id, room_id)
   - replace_asset(asset_id, new_asset_id)
   - move_asset(asset_id, x, y, rotation)
   - remove_asset(asset_id)

3. You can ONLY work with these asset types:
   - doors
   - windows
   - tv_units
   - tables
   - kitchen_cabinets
   - bedroom_wardrobes
   - computer_tables

4. You CANNOT:
   - Move or modify structural walls
   - Add stairs or create multi-floor designs
   - Create custom assets
   - Generate geometry
   - Modify room dimensions

5. If a request violates constraints, return: {"error": "Request not allowed by system constraints"}

## OUTPUT FORMAT:
{
  "actions": [
    {
      "tool": "tool_name",
      "parameters": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}

## AVAILABLE ASSETS:
{assets}

## CURRENT SCENE STATE:
{scene_state}

## USER REQUEST:
{user_prompt}

Output ONLY the JSON response:"""


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self, api_key: str):
        """Initialize Gemini with API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def translate_intent(
        self,
        user_prompt: str,
        current_scene: SceneState
    ) -> GeminiResponse:
        """
        Translate user's natural language prompt to structured actions.

        Args:
            user_prompt: Natural language design request
            current_scene: Current state of the scene

        Returns:
            GeminiResponse with actions or error
        """
        # Build the prompt
        prompt = SYSTEM_PROMPT.format(
            assets=json.dumps(self._get_asset_summary(), indent=2),
            scene_state=json.dumps(current_scene.model_dump(), indent=2),
            user_prompt=user_prompt
        )

        try:
            # Call Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,  # Low temperature for deterministic output
                    max_output_tokens=2048,
                )
            )

            raw_text = response.text.strip()

            # Parse JSON response
            return self._parse_response(raw_text)

        except Exception as e:
            return GeminiResponse(
                error=f"Gemini API error: {str(e)}",
                raw_response=None
            )

    def _parse_response(self, raw_text: str) -> GeminiResponse:
        """Parse Gemini's raw text response into structured format."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', raw_text)
            if not json_match:
                return GeminiResponse(
                    error="Failed to parse Gemini response as JSON",
                    raw_response=raw_text
                )

            json_str = json_match.group()
            data = json.loads(json_str)

            # Check for error response
            if "error" in data:
                return GeminiResponse(
                    error=data["error"],
                    raw_response=raw_text
                )

            # Parse actions
            actions = []
            for action_data in data.get("actions", []):
                action = GeminiAction(
                    tool=action_data.get("tool", ""),
                    parameters=action_data.get("parameters", {})
                )
                actions.append(action)

            return GeminiResponse(
                actions=actions,
                raw_response=raw_text
            )

        except json.JSONDecodeError as e:
            return GeminiResponse(
                error=f"Invalid JSON in response: {str(e)}",
                raw_response=raw_text
            )

    def _get_asset_summary(self) -> dict:
        """Get a summary of available assets for the prompt."""
        summary = {}
        for asset_type, assets in ASSET_LIBRARY.items():
            summary[asset_type] = list(assets.keys())
        return summary


class MockGeminiService:
    """Mock Gemini service for testing without API."""

    async def translate_intent(
        self,
        user_prompt: str,
        current_scene: SceneState
    ) -> GeminiResponse:
        """Return mock responses based on keywords in prompt."""
        prompt_lower = user_prompt.lower()

        # Simple keyword-based mock responses
        if "wall" in prompt_lower and ("color" in prompt_lower or "paint" in prompt_lower):
            # Extract color if mentioned
            color = "#E8D4B8" if "beige" in prompt_lower else "#87CEEB" if "blue" in prompt_lower else "#90EE90" if "green" in prompt_lower else "#FFFFFF"
            room_id = list(current_scene.rooms.keys())[0] if current_scene.rooms else "living_room"

            return GeminiResponse(
                actions=[
                    GeminiAction(
                        tool="set_wall_color",
                        parameters={"room_id": room_id, "hex_color": color}
                    )
                ]
            )

        elif "add" in prompt_lower and "tv" in prompt_lower:
            room_id = "living_room" if "living_room" in current_scene.rooms else list(current_scene.rooms.keys())[0]
            return GeminiResponse(
                actions=[
                    GeminiAction(
                        tool="add_asset",
                        parameters={
                            "asset_type": "tv_units",
                            "asset_id": "tv_unit_modern_01",
                            "room_id": room_id
                        }
                    )
                ]
            )

        elif "remove" in prompt_lower:
            if current_scene.assets:
                asset_id = list(current_scene.assets.keys())[0]
                return GeminiResponse(
                    actions=[
                        GeminiAction(
                            tool="remove_asset",
                            parameters={"asset_id": asset_id}
                        )
                    ]
                )

        elif "stairs" in prompt_lower or "floor" in prompt_lower or "duplex" in prompt_lower:
            return GeminiResponse(
                error="Request not allowed by system constraints"
            )

        # Default: no actions
        return GeminiResponse(
            actions=[],
            error="Could not understand the request. Please be more specific about what you want to change."
        )
