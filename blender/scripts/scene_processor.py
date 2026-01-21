"""
Blender Scene Processor - Main automation script for Interior Design System.
This script is invoked by the backend to process scene commands and export GLB files.

Usage: blender --background --python scene_processor.py -- command_file.json
"""

import bpy
import sys
import json
import math
import os
from pathlib import Path
from typing import Dict, List, Any, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

ASSETS_BASE_PATH = Path(__file__).parent.parent / "assets" / "models"
MATERIALS_PATH = Path(__file__).parent.parent / "assets" / "materials"

# Wall material colors (fallback if no texture)
DEFAULT_WALL_HEIGHT = 3.0
DEFAULT_FLOOR_LEVEL = 0.0
WALL_THICKNESS = 0.15


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_scene():
    """Remove all objects from the current scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple (0-1 range)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def create_material(name: str, color: tuple, roughness: float = 0.8) -> bpy.types.Material:
    """Create a PBR material with given color."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness

    # Create Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat


def create_box(
    name: str,
    width: float,
    height: float,
    depth: float,
    location: tuple = (0, 0, 0),
    material: Optional[bpy.types.Material] = None
) -> bpy.types.Object:
    """Create a box mesh with given dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, depth, height)

    # Apply scale
    bpy.ops.object.transform_apply(scale=True)

    if material:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)

    return obj


def import_glb(filepath: str, location: tuple = (0, 0, 0)) -> Optional[bpy.types.Object]:
    """Import a GLB file and return the root object."""
    if not os.path.exists(filepath):
        print(f"Asset file not found: {filepath}")
        return None

    # Store current objects
    before = set(bpy.data.objects)

    # Import GLB
    bpy.ops.import_scene.gltf(filepath=filepath)

    # Find new objects
    after = set(bpy.data.objects)
    new_objects = after - before

    if not new_objects:
        return None

    # Create parent empty for grouping
    root = bpy.data.objects.new(f"asset_{Path(filepath).stem}", None)
    bpy.context.collection.objects.link(root)

    # Parent all new objects
    for obj in new_objects:
        if obj.parent is None:
            obj.parent = root

    root.location = location
    return root


# ============================================================================
# SCENE BUILDERS
# ============================================================================

class RoomBuilder:
    """Builds room geometry (walls, floor, ceiling)."""

    def __init__(self):
        self.rooms: Dict[str, Dict] = {}

    def create_room(
        self,
        room_id: str,
        room_data: Dict[str, Any]
    ) -> List[bpy.types.Object]:
        """Create a room with walls, floor, and ceiling."""
        objects = []

        dims = room_data.get("dimensions", {})
        pos = room_data.get("position", {})
        wall_color = room_data.get("wall_color", "#FFFFFF")

        width = dims.get("width", 4.0)
        height = dims.get("height", DEFAULT_WALL_HEIGHT)
        depth = dims.get("depth", 4.0)
        x = pos.get("x", 0)
        y = pos.get("y", 0)

        # Create wall material
        rgb = hex_to_rgb(wall_color)
        wall_mat = create_material(f"{room_id}_wall_mat", rgb)

        # Create floor material
        floor_mat = create_material(f"{room_id}_floor_mat", (0.7, 0.65, 0.55), roughness=0.9)

        # Floor
        floor = create_box(
            f"{room_id}_floor",
            width, 0.1, depth,
            (x + width/2, y + depth/2, -0.05),
            floor_mat
        )
        objects.append(floor)

        # Walls (4 walls with openings for doors/windows handled separately)
        # Back wall (along X axis, at Y=0)
        back_wall = create_box(
            f"{room_id}_wall_back",
            width, height, WALL_THICKNESS,
            (x + width/2, y, height/2),
            wall_mat
        )
        objects.append(back_wall)

        # Front wall (along X axis, at Y=depth)
        front_wall = create_box(
            f"{room_id}_wall_front",
            width, height, WALL_THICKNESS,
            (x + width/2, y + depth, height/2),
            wall_mat
        )
        objects.append(front_wall)

        # Left wall (along Y axis, at X=0)
        left_wall = create_box(
            f"{room_id}_wall_left",
            WALL_THICKNESS, height, depth,
            (x, y + depth/2, height/2),
            wall_mat
        )
        objects.append(left_wall)

        # Right wall (along Y axis, at X=width)
        right_wall = create_box(
            f"{room_id}_wall_right",
            WALL_THICKNESS, height, depth,
            (x + width, y + depth/2, height/2),
            wall_mat
        )
        objects.append(right_wall)

        # Store room reference
        self.rooms[room_id] = {
            "objects": objects,
            "data": room_data,
            "wall_material": wall_mat
        }

        return objects

    def update_wall_color(self, room_id: str, hex_color: str):
        """Update wall color for a room."""
        if room_id not in self.rooms:
            print(f"Room not found: {room_id}")
            return

        rgb = hex_to_rgb(hex_color)
        mat = self.rooms[room_id]["wall_material"]

        # Update material color
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'BSDF_PRINCIPLED':
                    node.inputs['Base Color'].default_value = (*rgb, 1.0)


class AssetManager:
    """Manages furniture and fixtures in the scene."""

    def __init__(self):
        self.assets: Dict[str, bpy.types.Object] = {}

    def add_asset(
        self,
        instance_id: str,
        asset_type: str,
        library_id: str,
        position: Dict[str, float],
        rotation: float = 0,
        scale: float = 1.0
    ) -> Optional[bpy.types.Object]:
        """Add an asset from the library to the scene."""
        # Build asset path
        asset_path = ASSETS_BASE_PATH / asset_type / f"{library_id}.glb"

        # Try to import the asset
        obj = import_glb(str(asset_path))

        if obj is None:
            # Create placeholder if asset not found
            print(f"Creating placeholder for: {library_id}")
            obj = self._create_placeholder(instance_id, asset_type)

        if obj:
            obj.name = instance_id
            obj.location = (
                position.get("x", 0),
                position.get("y", 0),
                position.get("z", 0)
            )
            obj.rotation_euler = (0, 0, math.radians(rotation))
            obj.scale = (scale, scale, scale)

            self.assets[instance_id] = obj

        return obj

    def remove_asset(self, instance_id: str):
        """Remove an asset from the scene."""
        if instance_id in self.assets:
            obj = self.assets[instance_id]

            # Remove children first
            for child in obj.children:
                bpy.data.objects.remove(child, do_unlink=True)

            bpy.data.objects.remove(obj, do_unlink=True)
            del self.assets[instance_id]

    def move_asset(
        self,
        instance_id: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        rotation: Optional[float] = None
    ):
        """Move or rotate an existing asset."""
        if instance_id not in self.assets:
            print(f"Asset not found: {instance_id}")
            return

        obj = self.assets[instance_id]

        if x is not None:
            obj.location.x = x
        if y is not None:
            obj.location.y = y
        if rotation is not None:
            obj.rotation_euler.z = math.radians(rotation)

    def replace_asset(self, instance_id: str, new_library_id: str, asset_type: str):
        """Replace an asset with a different one from the library."""
        if instance_id not in self.assets:
            print(f"Asset not found: {instance_id}")
            return

        old_obj = self.assets[instance_id]
        old_location = old_obj.location.copy()
        old_rotation = old_obj.rotation_euler.z
        old_scale = old_obj.scale.x

        # Remove old
        self.remove_asset(instance_id)

        # Add new
        self.add_asset(
            instance_id,
            asset_type,
            new_library_id,
            {"x": old_location.x, "y": old_location.y, "z": old_location.z},
            math.degrees(old_rotation),
            old_scale
        )

    def _create_placeholder(
        self,
        name: str,
        asset_type: str
    ) -> bpy.types.Object:
        """Create a placeholder box for missing assets."""
        # Default sizes based on asset type
        sizes = {
            "doors": (0.9, 0.1, 2.1),
            "windows": (1.2, 0.1, 1.2),
            "tv_units": (1.8, 0.4, 0.5),
            "tables": (1.2, 0.8, 0.75),
            "kitchen_cabinets": (0.6, 0.6, 0.85),
            "bedroom_wardrobes": (2.0, 0.6, 2.4),
            "computer_tables": (1.2, 0.6, 0.75)
        }

        size = sizes.get(asset_type, (1, 1, 1))
        mat = create_material(f"{name}_placeholder_mat", (0.5, 0.5, 0.5))

        return create_box(name, size[0], size[2], size[1], material=mat)


# ============================================================================
# SCENE PROCESSOR
# ============================================================================

class SceneProcessor:
    """Main processor for handling scene commands."""

    def __init__(self):
        self.room_builder = RoomBuilder()
        self.asset_manager = AssetManager()

    def process_command(self, command: Dict[str, Any]):
        """Process a command from the backend."""
        command_type = command.get("command_type")
        session_id = command.get("session_id")
        scene_state = command.get("scene_state", {})
        actions = command.get("actions", [])
        output_path = command.get("output_path")

        print(f"Processing command: {command_type} for session: {session_id}")

        if command_type == "generate_initial":
            self._generate_initial_scene(scene_state)
        elif command_type == "apply_changes":
            self._apply_changes(scene_state, actions)
        else:
            print(f"Unknown command type: {command_type}")
            return

        # Export to GLB
        if output_path:
            self._export_glb(output_path)

    def _generate_initial_scene(self, scene_state: Dict[str, Any]):
        """Generate the initial scene from state."""
        clear_scene()

        # Setup scene
        self._setup_scene()

        # Create rooms
        rooms = scene_state.get("rooms", {})
        for room_id, room_data in rooms.items():
            self.room_builder.create_room(room_id, room_data)

        # Add default assets
        assets = scene_state.get("assets", {})
        for instance_id, asset_data in assets.items():
            self.asset_manager.add_asset(
                instance_id,
                asset_data.get("asset_type", ""),
                asset_data.get("library_id", ""),
                asset_data.get("position", {}),
                asset_data.get("rotation", 0),
                asset_data.get("scale", 1.0)
            )

        # Add lighting
        self._setup_lighting()

    def _apply_changes(self, scene_state: Dict[str, Any], actions: List[Dict]):
        """Apply incremental changes to the scene."""
        # First regenerate base if needed
        self._generate_initial_scene(scene_state)

        # Apply additional actions (already reflected in scene_state)
        # Actions are primarily for logging/debugging here

    def _setup_scene(self):
        """Configure scene settings for GLB export."""
        # Set units to meters
        bpy.context.scene.unit_settings.system = 'METRIC'
        bpy.context.scene.unit_settings.scale_length = 1.0

    def _setup_lighting(self):
        """Add basic lighting to the scene."""
        # Sun light
        bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.name = "Sun"
        sun.data.energy = 3.0

        # Ambient light (area light)
        bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
        area = bpy.context.active_object
        area.name = "AmbientLight"
        area.data.energy = 100.0
        area.data.size = 10.0

    def _export_glb(self, output_path: str):
        """Export scene to GLB format."""
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Select all mesh objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.context.scene.objects:
            if obj.type in {'MESH', 'EMPTY', 'LIGHT'}:
                obj.select_set(True)

        # Export settings for optimized GLB
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=False,
            export_apply=True,
            export_texcoords=True,
            export_normals=True,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_materials='EXPORT',
            export_colors=True,
            export_lights=True
        )

        print(f"Exported GLB to: {output_path}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point when run from command line."""
    # Get command file path from arguments
    argv = sys.argv
    if "--" not in argv:
        print("Error: No command file specified")
        print("Usage: blender --background --python scene_processor.py -- command.json")
        sys.exit(1)

    # Arguments after "--" are script arguments
    script_args = argv[argv.index("--") + 1:]
    if not script_args:
        print("Error: Command file path required")
        sys.exit(1)

    command_file = script_args[0]

    # Load command
    try:
        with open(command_file, 'r') as f:
            command = json.load(f)
    except Exception as e:
        print(f"Error loading command file: {e}")
        sys.exit(1)

    # Process command
    processor = SceneProcessor()
    processor.process_command(command)

    print("Scene processing complete")


if __name__ == "__main__":
    main()
