"""
Placeholder Asset Generator - Creates basic GLB assets for testing.
Run this script in Blender to generate placeholder furniture models.

Usage: blender --background --python generate_placeholder_assets.py
"""

import bpy
import os
import sys
import math
from pathlib import Path


# Base path for assets
ASSETS_PATH = Path(__file__).parent.parent / "assets" / "models"


def clear_scene():
    """Clear all objects from scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_material(name: str, color: tuple, roughness: float = 0.5) -> bpy.types.Material:
    """Create a basic PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def create_box(name, w, h, d, location=(0,0,0), material=None):
    """Create a box mesh."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    if material:
        obj.data.materials.append(material)
    return obj


def export_glb(filepath):
    """Export current selection as GLB."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        use_selection=True,
        export_apply=True
    )
    print(f"Exported: {filepath}")


# ============================================================================
# ASSET CREATORS
# ============================================================================

def create_door(name, width=0.9, height=2.1, depth=0.05):
    """Create a simple door model."""
    clear_scene()

    # Door frame
    frame_mat = create_material("frame_mat", (0.3, 0.2, 0.1))

    # Door panel
    door_mat = create_material("door_mat", (0.5, 0.35, 0.2))

    # Frame top
    create_box("frame_top", width + 0.1, 0.05, depth + 0.02, (0, 0, height), frame_mat)

    # Frame left
    create_box("frame_left", 0.05, height, depth + 0.02, (-width/2 - 0.025, 0, height/2), frame_mat)

    # Frame right
    create_box("frame_right", 0.05, height, depth + 0.02, (width/2 + 0.025, 0, height/2), frame_mat)

    # Door panel
    create_box("door_panel", width - 0.02, height - 0.02, depth, (0, 0, height/2), door_mat)

    # Handle
    handle_mat = create_material("handle_mat", (0.8, 0.7, 0.2), 0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.1, location=(width/2 - 0.1, -depth, height/2))
    handle = bpy.context.active_object
    handle.name = "handle"
    handle.rotation_euler = (math.pi/2, 0, 0)
    handle.data.materials.append(handle_mat)

    # Select all for export
    bpy.ops.object.select_all(action='SELECT')


def create_window(name, width=1.2, height=1.2, depth=0.1):
    """Create a simple window model."""
    clear_scene()

    frame_mat = create_material("frame_mat", (0.9, 0.9, 0.9))
    glass_mat = create_material("glass_mat", (0.8, 0.9, 1.0), 0.1)
    glass_mat.node_tree.nodes["Principled BSDF"].inputs['Transmission'].default_value = 0.9

    # Frame
    create_box("frame_outer", width, height, depth, (0, 0, 0), frame_mat)

    # Glass
    create_box("glass", width - 0.1, height - 0.1, 0.02, (0, 0, 0), glass_mat)

    # Cross bars
    create_box("bar_h", width - 0.1, 0.03, 0.04, (0, 0, 0), frame_mat)
    create_box("bar_v", 0.03, height - 0.1, 0.04, (0, 0, 0), frame_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_tv_unit(name, width=1.8, height=0.5, depth=0.4):
    """Create a TV unit model."""
    clear_scene()

    body_mat = create_material("body_mat", (0.2, 0.2, 0.25))
    accent_mat = create_material("accent_mat", (0.15, 0.15, 0.15))

    # Main body
    create_box("body", width, height - 0.05, depth, (0, 0, height/2), body_mat)

    # Top surface
    create_box("top", width + 0.02, 0.02, depth + 0.02, (0, 0, height), accent_mat)

    # Legs
    leg_mat = create_material("leg_mat", (0.6, 0.5, 0.3))
    for x in [-width/2 + 0.1, width/2 - 0.1]:
        for y in [-depth/2 + 0.05, depth/2 - 0.05]:
            create_box(f"leg_{x}_{y}", 0.04, 0.1, 0.04, (x, y, 0.05), leg_mat)

    # Drawers (decorative)
    drawer_mat = create_material("drawer_mat", (0.25, 0.25, 0.3))
    for i in range(3):
        x = -width/2 + 0.3 + i * (width/3)
        create_box(f"drawer_{i}", width/3 - 0.05, height - 0.15, 0.02, (x, -depth/2 + 0.01, height/2), drawer_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_dining_table(name, width=1.2, height=0.75, depth=0.8):
    """Create a dining table model."""
    clear_scene()

    top_mat = create_material("top_mat", (0.6, 0.45, 0.3))
    leg_mat = create_material("leg_mat", (0.5, 0.35, 0.2))

    # Table top
    create_box("top", width, 0.04, depth, (0, 0, height), top_mat)

    # Legs
    leg_w = 0.06
    for x in [-width/2 + 0.1, width/2 - 0.1]:
        for y in [-depth/2 + 0.1, depth/2 - 0.1]:
            create_box(f"leg_{x}_{y}", leg_w, height - 0.04, leg_w, (x, y, height/2 - 0.02), leg_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_coffee_table(name, width=1.0, height=0.45, depth=0.6):
    """Create a coffee table model."""
    clear_scene()

    top_mat = create_material("top_mat", (0.85, 0.9, 0.95), 0.1)  # Glass-like
    frame_mat = create_material("frame_mat", (0.2, 0.2, 0.2), 0.3)

    # Glass top
    top_mat.node_tree.nodes["Principled BSDF"].inputs['Transmission'].default_value = 0.5
    create_box("top", width, 0.02, depth, (0, 0, height), top_mat)

    # Metal frame
    create_box("frame_h1", width, 0.03, 0.03, (0, -depth/2 + 0.05, height - 0.05), frame_mat)
    create_box("frame_h2", width, 0.03, 0.03, (0, depth/2 - 0.05, height - 0.05), frame_mat)

    # Legs
    for x in [-width/2 + 0.05, width/2 - 0.05]:
        for y in [-depth/2 + 0.05, depth/2 - 0.05]:
            create_box(f"leg_{x}_{y}", 0.03, height, 0.03, (x, y, height/2), frame_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_wardrobe(name, width=2.0, height=2.4, depth=0.6):
    """Create a wardrobe model."""
    clear_scene()

    body_mat = create_material("body_mat", (0.9, 0.9, 0.92))
    door_mat = create_material("door_mat", (0.85, 0.85, 0.88))
    handle_mat = create_material("handle_mat", (0.7, 0.7, 0.7), 0.2)

    # Main body
    create_box("body", width, height, depth, (0, 0, height/2), body_mat)

    # Sliding door tracks (grooves)
    create_box("track_top", width - 0.02, 0.02, 0.02, (0, -depth/2 + 0.02, height - 0.03), body_mat)
    create_box("track_bottom", width - 0.02, 0.02, 0.02, (0, -depth/2 + 0.02, 0.03), body_mat)

    # Doors (sliding)
    door_w = width / 2 - 0.02
    create_box("door_left", door_w, height - 0.1, 0.02, (-width/4 + 0.01, -depth/2 - 0.01, height/2), door_mat)
    create_box("door_right", door_w, height - 0.1, 0.02, (width/4 - 0.01, -depth/2 - 0.02, height/2), door_mat)

    # Handles
    for x in [0.02, -0.02]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.8, location=(x, -depth/2 - 0.03, height/2))
        h = bpy.context.active_object
        h.name = f"handle_{x}"
        h.data.materials.append(handle_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_kitchen_cabinet(name, width=0.6, height=0.85, depth=0.6):
    """Create a kitchen cabinet model."""
    clear_scene()

    body_mat = create_material("body_mat", (0.95, 0.95, 0.97))
    counter_mat = create_material("counter_mat", (0.3, 0.3, 0.32), 0.3)
    handle_mat = create_material("handle_mat", (0.7, 0.7, 0.7), 0.2)

    # Body
    create_box("body", width, height - 0.04, depth, (0, 0, height/2 - 0.02), body_mat)

    # Counter top
    create_box("counter", width + 0.02, 0.04, depth + 0.02, (0, 0, height), counter_mat)

    # Door
    create_box("door", width - 0.04, height - 0.15, 0.02, (0, -depth/2 - 0.01, height/2 - 0.04), body_mat)

    # Handle
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -depth/2 - 0.02, height - 0.2))
    handle = bpy.context.active_object
    handle.name = "handle"
    handle.scale = (0.08, 0.02, 0.015)
    bpy.ops.object.transform_apply(scale=True)
    handle.data.materials.append(handle_mat)

    bpy.ops.object.select_all(action='SELECT')


def create_computer_desk(name, width=1.2, height=0.75, depth=0.6):
    """Create a computer desk model."""
    clear_scene()

    top_mat = create_material("top_mat", (0.92, 0.92, 0.94))
    leg_mat = create_material("leg_mat", (0.85, 0.85, 0.87))
    accent_mat = create_material("accent_mat", (0.2, 0.2, 0.22))

    # Desktop
    create_box("top", width, 0.025, depth, (0, 0, height), top_mat)

    # Side panels (instead of legs)
    create_box("side_left", 0.02, height - 0.025, depth - 0.05, (-width/2 + 0.01, 0, height/2 - 0.01), leg_mat)
    create_box("side_right", 0.02, height - 0.025, depth - 0.05, (width/2 - 0.01, 0, height/2 - 0.01), leg_mat)

    # Back panel (for cable management)
    create_box("back", width - 0.04, height * 0.3, 0.02, (0, depth/2 - 0.02, height * 0.65), leg_mat)

    # Keyboard tray area (indent)
    create_box("tray_support", width * 0.6, 0.02, depth * 0.4, (0, -depth * 0.1, height - 0.1), accent_mat)

    bpy.ops.object.select_all(action='SELECT')


# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_all_assets():
    """Generate all placeholder assets."""

    assets = {
        "doors": [
            ("door_wooden_01", create_door, {"width": 0.9, "height": 2.1}),
            ("door_wooden_02", create_door, {"width": 0.9, "height": 2.1}),
            ("door_glass_01", create_door, {"width": 0.9, "height": 2.1}),
            ("door_double_01", create_door, {"width": 1.8, "height": 2.1}),
        ],
        "windows": [
            ("window_standard_01", create_window, {"width": 1.2, "height": 1.2}),
            ("window_large_01", create_window, {"width": 2.0, "height": 2.5}),
            ("window_sliding_01", create_window, {"width": 1.5, "height": 1.0}),
        ],
        "tv_units": [
            ("tv_unit_modern_01", create_tv_unit, {"width": 1.8, "height": 0.5}),
            ("tv_unit_modern_02", create_tv_unit, {"width": 2.0, "height": 0.4}),
            ("tv_unit_classic_01", create_tv_unit, {"width": 1.5, "height": 0.6}),
            ("tv_unit_entertainment_01", create_tv_unit, {"width": 2.5, "height": 2.0}),
        ],
        "tables": [
            ("table_dining_01", create_dining_table, {"width": 1.2, "height": 0.75, "depth": 0.8}),
            ("table_dining_02", create_dining_table, {"width": 1.8, "height": 0.75, "depth": 0.9}),
            ("table_coffee_01", create_coffee_table, {"width": 1.0, "height": 0.45, "depth": 0.6}),
            ("table_side_01", create_coffee_table, {"width": 0.5, "height": 0.55, "depth": 0.5}),
            ("table_console_01", create_dining_table, {"width": 1.2, "height": 0.8, "depth": 0.35}),
        ],
        "kitchen_cabinets": [
            ("cabinet_base_01", create_kitchen_cabinet, {"width": 0.6, "height": 0.85}),
            ("cabinet_base_sink_01", create_kitchen_cabinet, {"width": 0.8, "height": 0.85}),
            ("cabinet_wall_01", create_kitchen_cabinet, {"width": 0.6, "height": 0.7, "depth": 0.35}),
            ("cabinet_corner_01", create_kitchen_cabinet, {"width": 0.9, "height": 0.85, "depth": 0.9}),
            ("cabinet_tall_01", create_kitchen_cabinet, {"width": 0.6, "height": 2.1}),
        ],
        "bedroom_wardrobes": [
            ("wardrobe_sliding_01", create_wardrobe, {"width": 2.0, "height": 2.4}),
            ("wardrobe_sliding_02", create_wardrobe, {"width": 2.5, "height": 2.4}),
            ("wardrobe_hinged_01", create_wardrobe, {"width": 1.5, "height": 2.2}),
            ("wardrobe_walkin_01", create_wardrobe, {"width": 3.0, "height": 2.4}),
        ],
        "computer_tables": [
            ("desk_simple_01", create_computer_desk, {"width": 1.2, "height": 0.75}),
            ("desk_lshape_01", create_computer_desk, {"width": 1.6, "height": 0.75, "depth": 1.4}),
            ("desk_gaming_01", create_computer_desk, {"width": 1.4, "height": 0.75}),
            ("desk_standing_01", create_computer_desk, {"width": 1.5, "height": 1.1}),
        ],
    }

    for category, items in assets.items():
        category_path = ASSETS_PATH / category
        category_path.mkdir(parents=True, exist_ok=True)

        for asset_name, creator_func, params in items:
            print(f"Generating: {category}/{asset_name}")
            creator_func(asset_name, **params)
            export_glb(str(category_path / f"{asset_name}.glb"))


if __name__ == "__main__":
    generate_all_assets()
    print("\nAll placeholder assets generated!")
