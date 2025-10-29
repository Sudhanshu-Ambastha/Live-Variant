"""
color_remap.py

Utility to remap a specific color (or multiple colors) in a material’s texture
to a new target color using Blender shader nodes.

Usage example:

    import color_remap as cr
    cr.apply_color_remaps(
        base_obj=bpy.data.objects["Cube"],
        variant_obj=bpy.data.objects["Cube_Variant"],
        remap_pairs=[
            ((1.0, 0.8, 0.0, 1.0), (0.0, 0.2, 1.0, 1.0)),  # Yellow → Blue
            ((0.8, 0.2, 0.2, 1.0), (0.1, 0.9, 0.3, 1.0)),  # Red → Green
        ],
        tolerance=0.1
    )
"""

import bpy


def apply_color_remaps(base_obj, variant_obj, remap_pairs, tolerance=0.1):
    """
    Create or update the variant's material to replace multiple source colors
    with target colors using node-based remapping.

    Args:
        base_obj (Object): The base mesh object containing the source material.
        variant_obj (Object): The variant mesh object to apply the remapped material.
        remap_pairs (list[tuple]): List of ((R,G,B,A), (R,G,B,A)) pairs to replace.
        tolerance (float): Color distance threshold for blending (0.01–0.5).

    Returns:
        Material: The remapped material assigned to the variant.
    """
    if not (base_obj and variant_obj):
        print("❌ Both base and variant objects are required.")
        return None

    if not base_obj.active_material:
        print("❌ Base object has no material to copy from.")
        return None

    base_mat = base_obj.active_material
    src_img = None
    if base_mat.use_nodes:
        for n in base_mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                src_img = n.image
                break
    if not src_img:
        print("❌ No texture image found in base material.")
        return None

    # --- Create new remap material ---
    remap_mat = bpy.data.materials.new(name=f"{variant_obj.name}_RemapMaterial")
    remap_mat.use_nodes = True
    nt = remap_mat.node_tree
    nt.nodes.clear()

    # --- Base Nodes ---
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = src_img

    tex.location = (-800, 0)
    bsdf.location = (600, 0)
    out.location = (900, 0)

    # Start with texture color as base
    last_color_output = tex.outputs["Color"]

    # --- Build Remap Chain for Each Color Pair ---
    for i, (source_color, target_color) in enumerate(remap_pairs):
        src_col = nt.nodes.new("ShaderNodeRGB")
        tgt_col = nt.nodes.new("ShaderNodeRGB")
        dist = nt.nodes.new("ShaderNodeVectorMath")
        div = nt.nodes.new("ShaderNodeMath")
        sub = nt.nodes.new("ShaderNodeMath")
        clamp = nt.nodes.new("ShaderNodeClamp")
        mix = nt.nodes.new("ShaderNodeMixRGB")

        # Position nodes for readability
        offset_y = -i * 250
        src_col.location = (-600, 200 + offset_y)
        tgt_col.location = (-600, -100 + offset_y)
        dist.location = (-350, 50 + offset_y)
        div.location = (-100, 50 + offset_y)
        sub.location = (150, 50 + offset_y)
        clamp.location = (400, 50 + offset_y)
        mix.location = (250, -200 + offset_y)

        # Assign node values
        src_col.outputs[0].default_value = source_color
        tgt_col.outputs[0].default_value = target_color
        dist.operation = 'DISTANCE'
        div.operation = 'DIVIDE'
        sub.operation = 'SUBTRACT'

        # --- Build subnetwork for one color remap ---
        nt.links.new(last_color_output, dist.inputs[0])
        nt.links.new(src_col.outputs["Color"], dist.inputs[1])
        div.inputs[1].default_value = max(tolerance, 1e-5)
        nt.links.new(dist.outputs["Value"], div.inputs[0])
        sub.inputs[0].default_value = 1.0
        nt.links.new(div.outputs["Value"], sub.inputs[1])
        nt.links.new(sub.outputs["Value"], clamp.inputs["Value"])
        nt.links.new(last_color_output, mix.inputs[1])
        nt.links.new(tgt_col.outputs["Color"], mix.inputs[2])
        nt.links.new(clamp.outputs["Result"], mix.inputs["Fac"])

        # This mix becomes the new color output for next iteration
        last_color_output = mix.outputs["Color"]

    # --- Connect Final Output to BSDF ---
    nt.links.new(last_color_output, bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # --- Assign Material to Variant ---
    variant_obj.data.materials.clear()
    variant_obj.data.materials.append(remap_mat)

    print(f"🎨 Applied {len(remap_pairs)} color remaps to '{variant_obj.name}' (tol={tolerance})")
    return remap_mat


# Optional test
if __name__ == "__main__":
    objs = bpy.context.selected_objects
    if len(objs) == 2:
        apply_color_remaps(
            objs[0],
            objs[1],
            [
                ((1.0, 0.8, 0.0, 1.0), (0.0, 0.2, 1.0, 1.0)),
                ((0.8, 0.2, 0.2, 1.0), (0.1, 0.9, 0.3, 1.0))
            ]
        )
    else:
        print("⚠️ Select base and variant objects before running.")
