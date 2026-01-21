"""
Interior Design System - FastAPI Backend
Handles user requests, Gemini integration, and Blender orchestration.
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.services.gemini_service import GeminiService, MockGeminiService
from app.services.blender_service import BlenderService, MockBlenderService
from app.services.scene_manager import SceneManager
from app.models.schemas import (
    DesignRequest,
    DesignResponse,
    SceneState,
    GeminiAction
)
from app.utils.config import settings


# Initialize services
gemini_service = None
blender_service = None
scene_manager: Optional[SceneManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    global gemini_service, blender_service, scene_manager

    # Ensure directories exist FIRST (before mounting static files)
    Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.SCENES_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize services on startup
    # Use mock services if configured or if API key not set
    if settings.USE_MOCK_GEMINI or not settings.GEMINI_API_KEY:
        print("Using Mock Gemini Service")
        gemini_service = MockGeminiService()
    else:
        gemini_service = GeminiService(api_key=settings.GEMINI_API_KEY)

    if settings.USE_MOCK_BLENDER:
        print("Using Mock Blender Service")
        blender_service = MockBlenderService(output_dir=settings.OUTPUT_DIR)
    else:
        blender_service = BlenderService(
            blender_path=settings.BLENDER_PATH,
            scripts_dir=settings.BLENDER_SCRIPTS_DIR,
            output_dir=settings.OUTPUT_DIR
        )

    scene_manager = SceneManager(
        scenes_dir=settings.SCENES_DIR,
        output_dir=settings.OUTPUT_DIR
    )

    print("Interior Design System initialized")
    print(f"  Output dir: {settings.OUTPUT_DIR}")
    print(f"  Gemini: {'Mock' if settings.USE_MOCK_GEMINI or not settings.GEMINI_API_KEY else 'Live'}")
    print(f"  Blender: {'Mock' if settings.USE_MOCK_BLENDER else 'Live'}")

    yield

    # Cleanup on shutdown
    print("Shutting down Interior Design System")


app = FastAPI(
    title="Interior Design System",
    description="AI-powered interior design with Blender rendering",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists before mounting
Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Serve generated GLB files
app.mount("/models", StaticFiles(directory=settings.OUTPUT_DIR), name="models")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "running", "service": "Interior Design System"}


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "gemini": gemini_service is not None,
        "blender": blender_service is not None,
        "scene_manager": scene_manager is not None
    }


@app.post("/api/upload-layout")
async def upload_layout(
    file: UploadFile = File(...),
    apartment_type: str = Form(default="2bhk")
):
    """
    Upload a 2D apartment layout (PNG/SVG).
    Returns a session ID for subsequent operations.
    """
    if apartment_type not in ["2bhk", "3bhk"]:
        raise HTTPException(
            status_code=400,
            detail="Only 2BHK or 3BHK apartments are supported"
        )

    # Validate file type
    if not file.filename.lower().endswith(('.png', '.svg', '.jpg', '.jpeg')):
        raise HTTPException(
            status_code=400,
            detail="Only PNG, SVG, JPG files are supported"
        )

    # Generate session ID
    session_id = str(uuid.uuid4())

    # Save uploaded file
    upload_path = Path(settings.UPLOADS_DIR) / f"{session_id}_layout{Path(file.filename).suffix}"
    content = await file.read()
    with open(upload_path, "wb") as f:
        f.write(content)

    # Initialize scene for this session
    initial_scene = scene_manager.create_scene(
        session_id=session_id,
        apartment_type=apartment_type,
        layout_path=str(upload_path)
    )

    # Generate initial 3D model
    try:
        glb_path = await blender_service.generate_initial_scene(
            session_id=session_id,
            apartment_type=apartment_type,
            scene_state=initial_scene
        )

        return {
            "session_id": session_id,
            "apartment_type": apartment_type,
            "model_url": f"/models/{session_id}.glb",
            "scene_state": initial_scene.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scene: {str(e)}")


@app.post("/api/design", response_model=DesignResponse)
async def process_design_request(request: DesignRequest):
    """
    Process a natural language design request.
    Uses Gemini to translate intent to structured actions,
    then applies changes via Blender.
    """
    session_id = request.session_id

    # Get current scene state
    current_scene = scene_manager.get_scene(session_id)
    if not current_scene:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get structured actions from Gemini
    try:
        gemini_response = await gemini_service.translate_intent(
            user_prompt=request.prompt,
            current_scene=current_scene
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {str(e)}")

    # Check for constraint violations
    if gemini_response.error:
        return DesignResponse(
            success=False,
            error=gemini_response.error,
            model_url=f"/models/{session_id}.glb",
            actions_taken=[]
        )

    # Validate actions against constraints
    validated_actions = []
    for action in gemini_response.actions:
        validation = _validate_action(action, current_scene)
        if validation["valid"]:
            validated_actions.append(action)
        else:
            return DesignResponse(
                success=False,
                error=validation["error"],
                model_url=f"/models/{session_id}.glb",
                actions_taken=[]
            )

    # Apply actions to scene state
    updated_scene = scene_manager.apply_actions(session_id, validated_actions)

    # Generate updated 3D model via Blender
    try:
        glb_path = await blender_service.apply_changes(
            session_id=session_id,
            actions=validated_actions,
            scene_state=updated_scene
        )

        return DesignResponse(
            success=True,
            model_url=f"/models/{session_id}.glb?t={uuid.uuid4().hex[:8]}",
            actions_taken=[a.model_dump() for a in validated_actions],
            scene_state=updated_scene.model_dump()
        )
    except Exception as e:
        # Rollback scene state on failure
        scene_manager.rollback(session_id)
        raise HTTPException(status_code=500, detail=f"Blender error: {str(e)}")


@app.get("/api/scene/{session_id}")
async def get_scene_state(session_id: str):
    """Get current scene state for a session."""
    scene = scene_manager.get_scene(session_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Session not found")
    return scene.model_dump()


@app.get("/api/assets")
async def get_available_assets():
    """Get list of available assets from the library."""
    from app.utils.asset_library import ASSET_LIBRARY
    return ASSET_LIBRARY


@app.get("/api/model/{session_id}")
async def get_model(session_id: str):
    """Get the GLB model file for a session."""
    model_path = Path(settings.OUTPUT_DIR) / f"{session_id}.glb"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
    return FileResponse(
        model_path,
        media_type="model/gltf-binary",
        filename=f"{session_id}.glb"
    )


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Clean up a session and its files."""
    scene_manager.delete_scene(session_id)

    # Clean up files
    for pattern in [f"{session_id}*"]:
        for f in Path(settings.OUTPUT_DIR).glob(pattern):
            f.unlink(missing_ok=True)
        for f in Path(settings.UPLOADS_DIR).glob(pattern):
            f.unlink(missing_ok=True)

    return {"status": "deleted", "session_id": session_id}


def _validate_action(action: GeminiAction, scene: SceneState) -> dict:
    """Validate an action against system constraints."""
    from app.utils.asset_library import ASSET_LIBRARY, ALLOWED_ASSET_TYPES

    tool = action.tool
    params = action.parameters

    # Validate tool name
    allowed_tools = ["set_wall_color", "add_asset", "replace_asset", "move_asset", "remove_asset"]
    if tool not in allowed_tools:
        return {"valid": False, "error": f"Unknown tool: {tool}"}

    # Tool-specific validation
    if tool == "set_wall_color":
        room_id = params.get("room_id")
        hex_color = params.get("hex_color")
        if room_id not in scene.rooms:
            return {"valid": False, "error": f"Room not found: {room_id}"}
        if not hex_color or not hex_color.startswith("#"):
            return {"valid": False, "error": "Invalid hex color format"}

    elif tool == "add_asset":
        asset_type = params.get("asset_type")
        asset_id = params.get("asset_id")
        room_id = params.get("room_id")

        if asset_type not in ALLOWED_ASSET_TYPES:
            return {"valid": False, "error": f"Asset type not allowed: {asset_type}"}
        if asset_id not in ASSET_LIBRARY.get(asset_type, {}):
            return {"valid": False, "error": f"Asset not in library: {asset_id}"}
        if room_id not in scene.rooms:
            return {"valid": False, "error": f"Room not found: {room_id}"}

    elif tool == "replace_asset":
        old_id = params.get("asset_id")
        new_id = params.get("new_asset_id")
        if old_id not in scene.assets:
            return {"valid": False, "error": f"Asset not found: {old_id}"}
        # Find asset type from old asset
        old_asset = scene.assets[old_id]
        asset_type = old_asset.get("type")
        if new_id not in ASSET_LIBRARY.get(asset_type, {}):
            return {"valid": False, "error": f"Replacement asset not in library: {new_id}"}

    elif tool == "move_asset":
        asset_id = params.get("asset_id")
        if asset_id not in scene.assets:
            return {"valid": False, "error": f"Asset not found: {asset_id}"}

    elif tool == "remove_asset":
        asset_id = params.get("asset_id")
        if asset_id not in scene.assets:
            return {"valid": False, "error": f"Asset not found: {asset_id}"}

    return {"valid": True, "error": None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
