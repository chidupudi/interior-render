"""
Pydantic models for the Interior Design System.
Defines request/response schemas and internal data structures.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RoomState(BaseModel):
    """State of a single room."""
    room_id: str
    room_type: str  # bedroom, living_room, kitchen, bathroom
    wall_color: str = "#FFFFFF"
    dimensions: Dict[str, float] = Field(default_factory=dict)  # width, height, depth
    position: Dict[str, float] = Field(default_factory=dict)  # x, y


class AssetState(BaseModel):
    """State of a placed asset."""
    asset_id: str
    asset_type: str  # door, window, tv_unit, table, etc.
    library_id: str  # Reference to asset library
    room_id: str
    position: Dict[str, float] = Field(default_factory=dict)  # x, y, z
    rotation: float = 0.0  # degrees
    scale: float = 1.0


class SceneState(BaseModel):
    """Complete scene state for a session."""
    session_id: str
    apartment_type: str  # 2bhk, 3bhk
    layout_path: Optional[str] = None
    rooms: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    assets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    version: int = 1


class GeminiAction(BaseModel):
    """A single action returned by Gemini."""
    tool: str  # set_wall_color, add_asset, replace_asset, move_asset, remove_asset
    parameters: Dict[str, Any]


class GeminiResponse(BaseModel):
    """Parsed response from Gemini."""
    actions: List[GeminiAction] = Field(default_factory=list)
    error: Optional[str] = None
    raw_response: Optional[str] = None


class DesignRequest(BaseModel):
    """User design request."""
    session_id: str
    prompt: str


class DesignResponse(BaseModel):
    """Response to a design request."""
    success: bool
    model_url: str
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    scene_state: Optional[Dict[str, Any]] = None


class BlenderCommand(BaseModel):
    """Command to send to Blender."""
    command_type: str
    session_id: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    scene_state: Dict[str, Any] = Field(default_factory=dict)
    output_path: str
