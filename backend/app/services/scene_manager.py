"""
Scene Manager - Handles scene state persistence and manipulation.
Stores scenes in memory with file-based backup on VM disk.
"""

import json
import copy
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.models.schemas import SceneState, GeminiAction
from app.utils.asset_library import ASSET_LIBRARY


# Default room layouts for apartment types
DEFAULT_LAYOUTS = {
    "2bhk": {
        "rooms": {
            "living_room": {
                "room_type": "living_room",
                "wall_color": "#F5F5F5",
                "dimensions": {"width": 5.0, "height": 3.0, "depth": 4.0},
                "position": {"x": 0, "y": 0}
            },
            "bedroom_1": {
                "room_type": "bedroom",
                "wall_color": "#E8E8E8",
                "dimensions": {"width": 4.0, "height": 3.0, "depth": 4.0},
                "position": {"x": 5.5, "y": 0}
            },
            "bedroom_2": {
                "room_type": "bedroom",
                "wall_color": "#E8E8E8",
                "dimensions": {"width": 3.5, "height": 3.0, "depth": 3.5},
                "position": {"x": 5.5, "y": 4.5}
            },
            "kitchen": {
                "room_type": "kitchen",
                "wall_color": "#FFFAF0",
                "dimensions": {"width": 3.0, "height": 3.0, "depth": 3.0},
                "position": {"x": 0, "y": 4.5}
            },
            "bathroom_1": {
                "room_type": "bathroom",
                "wall_color": "#F0FFFF",
                "dimensions": {"width": 2.0, "height": 3.0, "depth": 2.0},
                "position": {"x": 3.5, "y": 4.5}
            }
        },
        "default_assets": {
            "door_main": {
                "asset_type": "doors",
                "library_id": "door_wooden_01",
                "room_id": "living_room",
                "position": {"x": 0, "y": 2, "z": 0},
                "rotation": 0
            },
            "window_living": {
                "asset_type": "windows",
                "library_id": "window_standard_01",
                "room_id": "living_room",
                "position": {"x": 2.5, "y": 0, "z": 1.5},
                "rotation": 0
            }
        }
    },
    "3bhk": {
        "rooms": {
            "living_room": {
                "room_type": "living_room",
                "wall_color": "#F5F5F5",
                "dimensions": {"width": 6.0, "height": 3.0, "depth": 5.0},
                "position": {"x": 0, "y": 0}
            },
            "bedroom_1": {
                "room_type": "bedroom",
                "wall_color": "#E8E8E8",
                "dimensions": {"width": 4.5, "height": 3.0, "depth": 4.0},
                "position": {"x": 6.5, "y": 0}
            },
            "bedroom_2": {
                "room_type": "bedroom",
                "wall_color": "#E8E8E8",
                "dimensions": {"width": 4.0, "height": 3.0, "depth": 3.5},
                "position": {"x": 6.5, "y": 4.5}
            },
            "bedroom_3": {
                "room_type": "bedroom",
                "wall_color": "#E8E8E8",
                "dimensions": {"width": 3.5, "height": 3.0, "depth": 3.5},
                "position": {"x": 11.5, "y": 0}
            },
            "kitchen": {
                "room_type": "kitchen",
                "wall_color": "#FFFAF0",
                "dimensions": {"width": 3.5, "height": 3.0, "depth": 3.5},
                "position": {"x": 0, "y": 5.5}
            },
            "bathroom_1": {
                "room_type": "bathroom",
                "wall_color": "#F0FFFF",
                "dimensions": {"width": 2.5, "height": 3.0, "depth": 2.0},
                "position": {"x": 4, "y": 5.5}
            },
            "bathroom_2": {
                "room_type": "bathroom",
                "wall_color": "#F0FFFF",
                "dimensions": {"width": 2.0, "height": 3.0, "depth": 2.0},
                "position": {"x": 11.5, "y": 4}
            }
        },
        "default_assets": {
            "door_main": {
                "asset_type": "doors",
                "library_id": "door_wooden_01",
                "room_id": "living_room",
                "position": {"x": 0, "y": 2.5, "z": 0},
                "rotation": 0
            },
            "window_living_1": {
                "asset_type": "windows",
                "library_id": "window_large_01",
                "room_id": "living_room",
                "position": {"x": 3, "y": 0, "z": 1.5},
                "rotation": 0
            }
        }
    }
}


class SceneManager:
    """Manages scene state in memory with file-based persistence."""

    def __init__(self, scenes_dir: str, output_dir: str):
        """
        Initialize scene manager.

        Args:
            scenes_dir: Directory for scene state JSON files
            output_dir: Directory for generated outputs
        """
        self.scenes_dir = Path(scenes_dir)
        self.output_dir = Path(output_dir)
        self.scenes_dir.mkdir(parents=True, exist_ok=True)

        # In-memory scene cache
        self._scenes: Dict[str, SceneState] = {}
        # History for rollback support
        self._history: Dict[str, List[SceneState]] = {}

    def create_scene(
        self,
        session_id: str,
        apartment_type: str,
        layout_path: Optional[str] = None
    ) -> SceneState:
        """
        Create a new scene from apartment type.

        Args:
            session_id: Unique session identifier
            apartment_type: Type of apartment (2bhk, 3bhk)
            layout_path: Optional path to uploaded layout image

        Returns:
            Initial SceneState
        """
        # Get default layout
        layout = DEFAULT_LAYOUTS.get(apartment_type, DEFAULT_LAYOUTS["2bhk"])

        # Create scene state
        scene = SceneState(
            session_id=session_id,
            apartment_type=apartment_type,
            layout_path=layout_path,
            rooms=copy.deepcopy(layout["rooms"]),
            assets=copy.deepcopy(layout.get("default_assets", {})),
            version=1
        )

        # Store in memory
        self._scenes[session_id] = scene
        self._history[session_id] = [copy.deepcopy(scene)]

        # Persist to disk
        self._save_to_disk(scene)

        return scene

    def get_scene(self, session_id: str) -> Optional[SceneState]:
        """
        Get scene state for a session.

        Args:
            session_id: Session identifier

        Returns:
            SceneState or None if not found
        """
        # Check memory first
        if session_id in self._scenes:
            return self._scenes[session_id]

        # Try loading from disk
        return self._load_from_disk(session_id)

    def apply_actions(
        self,
        session_id: str,
        actions: List[GeminiAction]
    ) -> SceneState:
        """
        Apply a list of actions to the scene state.

        Args:
            session_id: Session identifier
            actions: List of actions to apply

        Returns:
            Updated SceneState
        """
        scene = self.get_scene(session_id)
        if not scene:
            raise ValueError(f"Scene not found: {session_id}")

        # Save current state for potential rollback
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(copy.deepcopy(scene))

        # Apply each action
        for action in actions:
            scene = self._apply_action(scene, action)

        # Update version
        scene.version += 1

        # Update memory and disk
        self._scenes[session_id] = scene
        self._save_to_disk(scene)

        return scene

    def rollback(self, session_id: str) -> Optional[SceneState]:
        """
        Rollback to previous scene state.

        Args:
            session_id: Session identifier

        Returns:
            Previous SceneState or None
        """
        if session_id not in self._history or not self._history[session_id]:
            return None

        # Pop the last saved state
        previous_state = self._history[session_id].pop()
        self._scenes[session_id] = previous_state
        self._save_to_disk(previous_state)

        return previous_state

    def delete_scene(self, session_id: str) -> None:
        """
        Delete a scene from memory and disk.

        Args:
            session_id: Session identifier
        """
        # Remove from memory
        self._scenes.pop(session_id, None)
        self._history.pop(session_id, None)

        # Remove from disk
        scene_file = self.scenes_dir / f"{session_id}.json"
        scene_file.unlink(missing_ok=True)

    def _apply_action(
        self,
        scene: SceneState,
        action: GeminiAction
    ) -> SceneState:
        """Apply a single action to the scene state."""
        tool = action.tool
        params = action.parameters

        if tool == "set_wall_color":
            room_id = params["room_id"]
            hex_color = params["hex_color"]
            if room_id in scene.rooms:
                scene.rooms[room_id]["wall_color"] = hex_color

        elif tool == "add_asset":
            asset_type = params["asset_type"]
            asset_id = params["asset_id"]
            room_id = params["room_id"]

            # Get asset info from library
            asset_info = ASSET_LIBRARY.get(asset_type, {}).get(asset_id, {})

            # Generate unique instance ID
            instance_id = f"{asset_id}_{len(scene.assets) + 1}"

            # Get room position for default placement
            room = scene.rooms.get(room_id, {})
            room_pos = room.get("position", {"x": 0, "y": 0})
            room_dims = room.get("dimensions", {"width": 4, "depth": 4})

            # Place in center of room by default
            scene.assets[instance_id] = {
                "asset_type": asset_type,
                "library_id": asset_id,
                "room_id": room_id,
                "position": {
                    "x": room_pos["x"] + room_dims["width"] / 2,
                    "y": room_pos["y"] + room_dims.get("depth", 4) / 2,
                    "z": 0
                },
                "rotation": 0,
                "scale": asset_info.get("default_scale", 1.0)
            }

        elif tool == "replace_asset":
            asset_id = params["asset_id"]
            new_asset_id = params["new_asset_id"]
            if asset_id in scene.assets:
                old_asset = scene.assets[asset_id]
                asset_type = old_asset["asset_type"]
                new_asset_info = ASSET_LIBRARY.get(asset_type, {}).get(new_asset_id, {})

                # Keep position and rotation, update library reference
                scene.assets[asset_id]["library_id"] = new_asset_id
                scene.assets[asset_id]["scale"] = new_asset_info.get("default_scale", 1.0)

        elif tool == "move_asset":
            asset_id = params["asset_id"]
            if asset_id in scene.assets:
                if "x" in params:
                    scene.assets[asset_id]["position"]["x"] = params["x"]
                if "y" in params:
                    scene.assets[asset_id]["position"]["y"] = params["y"]
                if "rotation" in params:
                    scene.assets[asset_id]["rotation"] = params["rotation"]

        elif tool == "remove_asset":
            asset_id = params["asset_id"]
            scene.assets.pop(asset_id, None)

        return scene

    def _save_to_disk(self, scene: SceneState) -> None:
        """Save scene state to disk as JSON."""
        scene_file = self.scenes_dir / f"{scene.session_id}.json"
        with open(scene_file, 'w') as f:
            json.dump(scene.model_dump(), f, indent=2)

    def _load_from_disk(self, session_id: str) -> Optional[SceneState]:
        """Load scene state from disk."""
        scene_file = self.scenes_dir / f"{session_id}.json"
        if not scene_file.exists():
            return None

        with open(scene_file, 'r') as f:
            data = json.load(f)
            scene = SceneState(**data)
            self._scenes[session_id] = scene
            return scene
