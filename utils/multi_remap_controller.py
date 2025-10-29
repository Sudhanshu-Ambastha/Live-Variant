"""
multi_remap_controller.py

Controller utility for applying multiple color remaps to a duplicated
variant mesh object, preserving base textures and materials.

Usage Example:

    from texture_setup import create_textured_duplicate_with_spacing
    from multi_remap_controller import apply_multi_remap

    base, variant = create_textured_duplicate_with_spacing()

    remaps = [
        ((1.0, 0.8, 0.0, 1.0), (0.0, 0.5, 1.0, 1.0)),  # yellow → blue
        ((0.8, 0.2, 0.2, 1.0), (0.0, 1.0, 0.0, 1.0)),  # red → green
    ]

    apply_multi_remap(base, variant, remaps)
"""

import bpy
from color_remap import apply_color_remaps


def apply_multi_remap(base_obj, variant_obj, remap_list, tolerance=0.08):
    """
    Apply one or more color remaps from `remap_list` to the variant object.

    Args:
        base_obj (Object): The base mesh object (with base material).
        variant_obj (Object): The variant mesh object to modify.
        remap_list (list): List of ((R,G,B,A), (R,G,B,A)) remap pairs.
        tolerance (float): Color match threshold (default 0.08).

    Behavior:
        - If no remap list is defined → variant gets same color as base.
        - If defined → applies all remaps in a single optimized material.
    """
    if not base_obj or not variant_obj:
        print("❌ Both base and variant objects must be provided.")
        return

    if not remap_list:
        print("⚠️ No remaps defined — assigning base material to variant.")
        if base_obj.active_material:
            mat_copy = base_obj.active_material.copy()
            variant_obj.data.materials.clear()
            variant_obj.data.materials.append(mat_copy)
        return

    print(f"🎨 Applying {len(remap_list)} remaps to '{variant_obj.name}' (tol={tolerance})")
    apply_color_remaps(base_obj, variant_obj, remap_list, tolerance)

    print("✅ Multi-remap applied successfully.")


# Optional test
if __name__ == "__main__":
    objs = bpy.context.selected_objects
    if len(objs) == 2:
        remaps = [
            ((1.0, 0.8, 0.0, 1.0), (0.0, 0.2, 1.0, 1.0)),
            ((0.8, 0.2, 0.2, 1.0), (0.0, 1.0, 0.0, 1.0)),
        ]
        apply_multi_remap(objs[0], objs[1], remaps)
    else:
        print("⚠️ Select base and variant objects before running.")
