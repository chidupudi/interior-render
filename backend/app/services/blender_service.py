"""
Blender Service - Orchestrates Blender for 3D scene generation.
Handles process spawning, command serialization, and output collection.
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Optional

from app.models.schemas import GeminiAction, SceneState, BlenderCommand


class BlenderService:
    """Service for invoking Blender automation scripts."""

    def __init__(
        self,
        blender_path: str,
        scripts_dir: str,
        output_dir: str
    ):
        """
        Initialize Blender service.

        Args:
            blender_path: Path to Blender executable
            scripts_dir: Path to Blender Python scripts
            output_dir: Directory for GLB output files
        """
        self.blender_path = blender_path
        self.scripts_dir = Path(scripts_dir)
        self.output_dir = Path(output_dir)
        self.main_script = self.scripts_dir / "scene_processor.py"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_initial_scene(
        self,
        session_id: str,
        apartment_type: str,
        scene_state: SceneState
    ) -> str:
        """
        Generate initial 3D scene from apartment type.

        Args:
            session_id: Unique session identifier
            apartment_type: Type of apartment (2bhk, 3bhk)
            scene_state: Initial scene state

        Returns:
            Path to generated GLB file
        """
        output_path = self.output_dir / f"{session_id}.glb"
        command_file = self.output_dir / f"{session_id}_command.json"

        # Create command for Blender
        command = BlenderCommand(
            command_type="generate_initial",
            session_id=session_id,
            actions=[],
            scene_state=scene_state.model_dump(),
            output_path=str(output_path)
        )

        # Write command to file (Blender will read this)
        with open(command_file, 'w') as f:
            json.dump(command.model_dump(), f, indent=2)

        # Execute Blender
        await self._execute_blender(command_file)

        # Clean up command file
        command_file.unlink(missing_ok=True)

        return str(output_path)

    async def apply_changes(
        self,
        session_id: str,
        actions: List[GeminiAction],
        scene_state: SceneState
    ) -> str:
        """
        Apply design changes to scene and export updated GLB.

        Args:
            session_id: Session identifier
            actions: List of actions to apply
            scene_state: Updated scene state

        Returns:
            Path to generated GLB file
        """
        output_path = self.output_dir / f"{session_id}.glb"
        command_file = self.output_dir / f"{session_id}_command.json"

        # Create command for Blender
        command = BlenderCommand(
            command_type="apply_changes",
            session_id=session_id,
            actions=[a.model_dump() for a in actions],
            scene_state=scene_state.model_dump(),
            output_path=str(output_path)
        )

        # Write command to file
        with open(command_file, 'w') as f:
            json.dump(command.model_dump(), f, indent=2)

        # Execute Blender
        await self._execute_blender(command_file)

        # Clean up command file
        command_file.unlink(missing_ok=True)

        return str(output_path)

    async def _execute_blender(self, command_file: Path) -> None:
        """
        Execute Blender with the automation script.

        Args:
            command_file: Path to JSON command file
        """
        # Build Blender command
        cmd = [
            self.blender_path,
            "--background",
            "--python", str(self.main_script),
            "--",
            str(command_file)
        ]

        # Run Blender as subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.scripts_dir.parent)
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown Blender error"
            raise RuntimeError(f"Blender execution failed: {error_msg}")

        # Log output for debugging
        if stdout:
            print(f"Blender output: {stdout.decode()}")


class MockBlenderService:
    """Mock Blender service for testing without Blender installed."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_initial_scene(
        self,
        session_id: str,
        apartment_type: str,
        scene_state: SceneState
    ) -> str:
        """Generate a mock GLB file."""
        output_path = self.output_dir / f"{session_id}.glb"

        # Create a minimal valid GLB file (empty scene)
        # GLB header + minimal JSON chunk
        glb_data = self._create_minimal_glb()
        with open(output_path, 'wb') as f:
            f.write(glb_data)

        return str(output_path)

    async def apply_changes(
        self,
        session_id: str,
        actions: List[GeminiAction],
        scene_state: SceneState
    ) -> str:
        """Apply changes and regenerate mock GLB."""
        return await self.generate_initial_scene(session_id, "", scene_state)

    def _create_minimal_glb(self) -> bytes:
        """Create a minimal valid GLB file."""
        import struct

        # Minimal glTF JSON
        gltf_json = json.dumps({
            "asset": {"version": "2.0"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{
                "primitives": [{
                    "attributes": {"POSITION": 0},
                    "indices": 1
                }]
            }],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": 3,
                    "type": "VEC3",
                    "max": [1, 1, 0],
                    "min": [-1, -1, 0]
                },
                {
                    "bufferView": 1,
                    "componentType": 5123,
                    "count": 3,
                    "type": "SCALAR"
                }
            ],
            "bufferViews": [
                {"buffer": 0, "byteOffset": 0, "byteLength": 36},
                {"buffer": 0, "byteOffset": 36, "byteLength": 6}
            ],
            "buffers": [{"byteLength": 44}]
        })

        # Pad JSON to 4-byte boundary
        json_bytes = gltf_json.encode('utf-8')
        json_padding = (4 - len(json_bytes) % 4) % 4
        json_bytes += b' ' * json_padding

        # Binary buffer: triangle vertices + indices
        vertices = struct.pack('<9f', -1, -1, 0, 1, -1, 0, 0, 1, 0)  # 3 vertices
        indices = struct.pack('<3H', 0, 1, 2)  # 3 indices
        padding = b'\x00' * 2  # Pad to 4 bytes
        bin_data = vertices + indices + padding

        # GLB header
        magic = b'glTF'
        version = struct.pack('<I', 2)
        total_length = 12 + 8 + len(json_bytes) + 8 + len(bin_data)
        length = struct.pack('<I', total_length)

        # JSON chunk
        json_chunk_length = struct.pack('<I', len(json_bytes))
        json_chunk_type = struct.pack('<I', 0x4E4F534A)  # JSON

        # BIN chunk
        bin_chunk_length = struct.pack('<I', len(bin_data))
        bin_chunk_type = struct.pack('<I', 0x004E4942)  # BIN

        return (
            magic + version + length +
            json_chunk_length + json_chunk_type + json_bytes +
            bin_chunk_length + bin_chunk_type + bin_data
        )
