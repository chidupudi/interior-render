"""
Asset Library - Predefined furniture and fixtures for the Interior Design System.
All assets have fixed scales, pivots, and materials.
"""

# Allowed asset types per system constraints
ALLOWED_ASSET_TYPES = [
    "doors",
    "windows",
    "tv_units",
    "tables",
    "kitchen_cabinets",
    "bedroom_wardrobes",
    "computer_tables"
]

# Complete asset library with metadata
ASSET_LIBRARY = {
    "doors": {
        "door_wooden_01": {
            "name": "Classic Wooden Door",
            "description": "Standard wooden door with brass handle",
            "model_file": "doors/door_wooden_01.glb",
            "thumbnail": "doors/door_wooden_01_thumb.png",
            "dimensions": {"width": 0.9, "height": 2.1, "depth": 0.05},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "wood_oak"
        },
        "door_wooden_02": {
            "name": "Modern Wooden Door",
            "description": "Sleek wooden door with chrome handle",
            "model_file": "doors/door_wooden_02.glb",
            "thumbnail": "doors/door_wooden_02_thumb.png",
            "dimensions": {"width": 0.9, "height": 2.1, "depth": 0.05},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "wood_walnut"
        },
        "door_glass_01": {
            "name": "Glass Panel Door",
            "description": "Door with frosted glass panels",
            "model_file": "doors/door_glass_01.glb",
            "thumbnail": "doors/door_glass_01_thumb.png",
            "dimensions": {"width": 0.9, "height": 2.1, "depth": 0.05},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "wood_white_glass"
        },
        "door_double_01": {
            "name": "Double Door",
            "description": "Wide double door for main entrance",
            "model_file": "doors/door_double_01.glb",
            "thumbnail": "doors/door_double_01_thumb.png",
            "dimensions": {"width": 1.8, "height": 2.1, "depth": 0.05},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_mahogany"
        }
    },
    "windows": {
        "window_standard_01": {
            "name": "Standard Window",
            "description": "Single pane window with aluminum frame",
            "model_file": "windows/window_standard_01.glb",
            "thumbnail": "windows/window_standard_01_thumb.png",
            "dimensions": {"width": 1.2, "height": 1.2, "depth": 0.1},
            "default_scale": 1.0,
            "pivot": "center",
            "material": "aluminum_glass"
        },
        "window_large_01": {
            "name": "Large Window",
            "description": "Floor-to-ceiling window",
            "model_file": "windows/window_large_01.glb",
            "thumbnail": "windows/window_large_01_thumb.png",
            "dimensions": {"width": 2.0, "height": 2.5, "depth": 0.1},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "aluminum_glass"
        },
        "window_sliding_01": {
            "name": "Sliding Window",
            "description": "Horizontal sliding window",
            "model_file": "windows/window_sliding_01.glb",
            "thumbnail": "windows/window_sliding_01_thumb.png",
            "dimensions": {"width": 1.5, "height": 1.0, "depth": 0.1},
            "default_scale": 1.0,
            "pivot": "center",
            "material": "upvc_glass"
        }
    },
    "tv_units": {
        "tv_unit_modern_01": {
            "name": "Modern TV Unit",
            "description": "Sleek floating TV console with storage",
            "model_file": "tv_units/tv_unit_modern_01.glb",
            "thumbnail": "tv_units/tv_unit_modern_01_thumb.png",
            "dimensions": {"width": 1.8, "height": 0.5, "depth": 0.4},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_white"
        },
        "tv_unit_modern_02": {
            "name": "Wall-mounted TV Unit",
            "description": "Minimalist wall-mounted entertainment unit",
            "model_file": "tv_units/tv_unit_modern_02.glb",
            "thumbnail": "tv_units/tv_unit_modern_02_thumb.png",
            "dimensions": {"width": 2.0, "height": 0.4, "depth": 0.35},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_grey"
        },
        "tv_unit_classic_01": {
            "name": "Classic TV Cabinet",
            "description": "Traditional wooden TV cabinet with doors",
            "model_file": "tv_units/tv_unit_classic_01.glb",
            "thumbnail": "tv_units/tv_unit_classic_01_thumb.png",
            "dimensions": {"width": 1.5, "height": 0.6, "depth": 0.45},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_oak"
        },
        "tv_unit_entertainment_01": {
            "name": "Entertainment Center",
            "description": "Large entertainment center with shelving",
            "model_file": "tv_units/tv_unit_entertainment_01.glb",
            "thumbnail": "tv_units/tv_unit_entertainment_01_thumb.png",
            "dimensions": {"width": 2.5, "height": 2.0, "depth": 0.45},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_walnut"
        }
    },
    "tables": {
        "table_dining_01": {
            "name": "4-Seater Dining Table",
            "description": "Rectangular dining table for 4 people",
            "model_file": "tables/table_dining_01.glb",
            "thumbnail": "tables/table_dining_01_thumb.png",
            "dimensions": {"width": 1.2, "height": 0.75, "depth": 0.8},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_oak"
        },
        "table_dining_02": {
            "name": "6-Seater Dining Table",
            "description": "Large dining table for 6 people",
            "model_file": "tables/table_dining_02.glb",
            "thumbnail": "tables/table_dining_02_thumb.png",
            "dimensions": {"width": 1.8, "height": 0.75, "depth": 0.9},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_walnut"
        },
        "table_coffee_01": {
            "name": "Modern Coffee Table",
            "description": "Low rectangular coffee table with glass top",
            "model_file": "tables/table_coffee_01.glb",
            "thumbnail": "tables/table_coffee_01_thumb.png",
            "dimensions": {"width": 1.0, "height": 0.45, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "metal_glass"
        },
        "table_side_01": {
            "name": "Side Table",
            "description": "Small round side table",
            "model_file": "tables/table_side_01.glb",
            "thumbnail": "tables/table_side_01_thumb.png",
            "dimensions": {"width": 0.5, "height": 0.55, "depth": 0.5},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_white"
        },
        "table_console_01": {
            "name": "Console Table",
            "description": "Narrow console table for hallways",
            "model_file": "tables/table_console_01.glb",
            "thumbnail": "tables/table_console_01_thumb.png",
            "dimensions": {"width": 1.2, "height": 0.8, "depth": 0.35},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "wood_grey"
        }
    },
    "kitchen_cabinets": {
        "cabinet_base_01": {
            "name": "Base Cabinet",
            "description": "Standard kitchen base cabinet with drawer",
            "model_file": "kitchen_cabinets/cabinet_base_01.glb",
            "thumbnail": "kitchen_cabinets/cabinet_base_01_thumb.png",
            "dimensions": {"width": 0.6, "height": 0.85, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_white"
        },
        "cabinet_base_sink_01": {
            "name": "Sink Cabinet",
            "description": "Base cabinet designed for sink installation",
            "model_file": "kitchen_cabinets/cabinet_base_sink_01.glb",
            "thumbnail": "kitchen_cabinets/cabinet_base_sink_01_thumb.png",
            "dimensions": {"width": 0.8, "height": 0.85, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_white"
        },
        "cabinet_wall_01": {
            "name": "Wall Cabinet",
            "description": "Upper wall-mounted kitchen cabinet",
            "model_file": "kitchen_cabinets/cabinet_wall_01.glb",
            "thumbnail": "kitchen_cabinets/cabinet_wall_01_thumb.png",
            "dimensions": {"width": 0.6, "height": 0.7, "depth": 0.35},
            "default_scale": 1.0,
            "pivot": "top_left",
            "material": "laminate_white"
        },
        "cabinet_corner_01": {
            "name": "Corner Cabinet",
            "description": "L-shaped corner cabinet",
            "model_file": "kitchen_cabinets/cabinet_corner_01.glb",
            "thumbnail": "kitchen_cabinets/cabinet_corner_01_thumb.png",
            "dimensions": {"width": 0.9, "height": 0.85, "depth": 0.9},
            "default_scale": 1.0,
            "pivot": "bottom_back_left",
            "material": "laminate_white"
        },
        "cabinet_tall_01": {
            "name": "Tall Pantry Cabinet",
            "description": "Full-height pantry storage cabinet",
            "model_file": "kitchen_cabinets/cabinet_tall_01.glb",
            "thumbnail": "kitchen_cabinets/cabinet_tall_01_thumb.png",
            "dimensions": {"width": 0.6, "height": 2.1, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_grey"
        }
    },
    "bedroom_wardrobes": {
        "wardrobe_sliding_01": {
            "name": "Sliding Door Wardrobe",
            "description": "Modern wardrobe with sliding doors",
            "model_file": "bedroom_wardrobes/wardrobe_sliding_01.glb",
            "thumbnail": "bedroom_wardrobes/wardrobe_sliding_01_thumb.png",
            "dimensions": {"width": 2.0, "height": 2.4, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_white"
        },
        "wardrobe_sliding_02": {
            "name": "Large Sliding Wardrobe",
            "description": "Extra-wide wardrobe with mirror panel",
            "model_file": "bedroom_wardrobes/wardrobe_sliding_02.glb",
            "thumbnail": "bedroom_wardrobes/wardrobe_sliding_02_thumb.png",
            "dimensions": {"width": 2.5, "height": 2.4, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_walnut_mirror"
        },
        "wardrobe_hinged_01": {
            "name": "Hinged Door Wardrobe",
            "description": "Traditional wardrobe with swing doors",
            "model_file": "bedroom_wardrobes/wardrobe_hinged_01.glb",
            "thumbnail": "bedroom_wardrobes/wardrobe_hinged_01_thumb.png",
            "dimensions": {"width": 1.5, "height": 2.2, "depth": 0.55},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "wood_oak"
        },
        "wardrobe_walkin_01": {
            "name": "Walk-in Closet System",
            "description": "Open wardrobe system for walk-in closets",
            "model_file": "bedroom_wardrobes/wardrobe_walkin_01.glb",
            "thumbnail": "bedroom_wardrobes/wardrobe_walkin_01_thumb.png",
            "dimensions": {"width": 3.0, "height": 2.4, "depth": 0.5},
            "default_scale": 1.0,
            "pivot": "bottom_left",
            "material": "laminate_grey"
        }
    },
    "computer_tables": {
        "desk_simple_01": {
            "name": "Simple Computer Desk",
            "description": "Basic rectangular desk for home office",
            "model_file": "computer_tables/desk_simple_01.glb",
            "thumbnail": "computer_tables/desk_simple_01_thumb.png",
            "dimensions": {"width": 1.2, "height": 0.75, "depth": 0.6},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_white"
        },
        "desk_lshape_01": {
            "name": "L-Shaped Desk",
            "description": "Corner desk with L-shaped design",
            "model_file": "computer_tables/desk_lshape_01.glb",
            "thumbnail": "computer_tables/desk_lshape_01_thumb.png",
            "dimensions": {"width": 1.6, "height": 0.75, "depth": 1.4},
            "default_scale": 1.0,
            "pivot": "bottom_back_left",
            "material": "laminate_walnut"
        },
        "desk_gaming_01": {
            "name": "Gaming Desk",
            "description": "Ergonomic gaming desk with cable management",
            "model_file": "computer_tables/desk_gaming_01.glb",
            "thumbnail": "computer_tables/desk_gaming_01_thumb.png",
            "dimensions": {"width": 1.4, "height": 0.75, "depth": 0.7},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_black"
        },
        "desk_standing_01": {
            "name": "Standing Desk",
            "description": "Height-adjustable standing desk",
            "model_file": "computer_tables/desk_standing_01.glb",
            "thumbnail": "computer_tables/desk_standing_01_thumb.png",
            "dimensions": {"width": 1.5, "height": 1.1, "depth": 0.7},
            "default_scale": 1.0,
            "pivot": "bottom_center",
            "material": "laminate_white_metal"
        }
    }
}


def get_asset(asset_type: str, asset_id: str) -> dict:
    """Get asset details by type and ID."""
    return ASSET_LIBRARY.get(asset_type, {}).get(asset_id, None)


def get_all_assets_of_type(asset_type: str) -> dict:
    """Get all assets of a given type."""
    return ASSET_LIBRARY.get(asset_type, {})


def search_assets(query: str) -> list:
    """Search assets by name or description."""
    results = []
    query_lower = query.lower()

    for asset_type, assets in ASSET_LIBRARY.items():
        for asset_id, asset in assets.items():
            if (query_lower in asset["name"].lower() or
                query_lower in asset.get("description", "").lower()):
                results.append({
                    "asset_type": asset_type,
                    "asset_id": asset_id,
                    **asset
                })

    return results
