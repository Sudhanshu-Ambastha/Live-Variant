"""
texture_setup.py

Utility functions for:
- Creating texture-paint-ready materials.
- Generating and saving texture images.
- Duplicating objects (with rig + modifiers) and spacing along the X-axis.

Usage example (inside Blender Python console or another script):

    import texture_setup as tsu
    tsu.create_textured_duplicate_with_spacing()
"""

import bpy
import os


# -----------------------------------------------------
# IMAGE HANDLER
# -----------------------------------------------------

def save_image_to_temp(image, filename="BaseColor_Texture.png"):
    """Save image to Blender's temp folder as a real file."""
    temp_dir = bpy.app.tempdir or os.path.expanduser("~")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, filename)
    image.filepath_raw = filepath
    image.file_format = 'PNG'
    image.save()
    image.use_fake_user = True
    return filepath


# -----------------------------------------------------
# MATERIAL CREATOR
# -----------------------------------------------------

def create_base_material_with_texture(obj, color=(0.8, 0.8, 0.8, 1.0)):
    """
    Create and assign a texture-paint-ready material to the given object.

    Args:
        obj (Object): Blender object (must be of type 'MESH')
        color (tuple): RGBA tuple for the initial texture color

    Returns:
        tuple: (Material, Image)
    """
    if not obj or obj.type != 'MESH':
        print("❌ Select a mesh object first.")
        return None, None

    # Create new material with nodes
    mat = bpy.data.materials.new(name=f"{obj.name}_BaseMaterial")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Clear all existing nodes
    for node in nodes:
        nodes.remove(node)

    # Create texture-paintable node setup
    tex_node = nodes.new("ShaderNodeTexImage")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    out = nodes.new("ShaderNodeOutputMaterial")

    tex_node.location = (-400, 0)
    bsdf.location = (0, 0)
    out.location = (300, 0)

    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Create and save image
    img_name = f"{obj.name}_BaseTex"
    img = bpy.data.images.new(img_name, width=1024, height=1024, alpha=True)
    img.generated_color = color
    save_image_to_temp(img, f"{img_name}.png")

    # Attach image to texture node
    tex_node.image = img

    # Assign material to object
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat

    # Prepare for texture paint
    bpy.ops.object.mode_set(mode='TEXTURE_PAINT')
    bpy.context.tool_settings.image_paint.canvas = img
    bpy.ops.object.mode_set(mode='OBJECT')

    print(f"✅ Created material '{mat.name}' and assigned to '{obj.name}'")
    return mat, img


# -----------------------------------------------------
# DUPLICATION HANDLER
# -----------------------------------------------------

def duplicate_with_rig_and_texture(base_obj):
    """
    Duplicate mesh object with rig (if any), modifiers, and textures intact.
    Returns the new duplicate object.
    """
    if not base_obj or base_obj.type != 'MESH':
        print("❌ Please select a valid mesh object.")
        return None

    # Duplicate mesh object
    variant_obj = base_obj.copy()
    variant_obj.data = base_obj.data.copy()
    bpy.context.collection.objects.link(variant_obj)
    variant_obj.name = f"{base_obj.name}_Variant"

    # Preserve rig/armature
    if base_obj.parent and base_obj.parent.type == 'ARMATURE':
        variant_obj.parent = base_obj.parent
        # Copy modifiers
        variant_obj.modifiers.clear()
        for mod in base_obj.modifiers:
            try:
                new_mod = variant_obj.modifiers.new(mod.name, mod.type)
                for attr in dir(mod):
                    if not attr.startswith("_") and hasattr(new_mod, attr):
                        try:
                            setattr(new_mod, attr, getattr(mod, attr))
                        except:
                            pass
            except Exception as e:
                print(f"⚠️ Could not copy modifier '{mod.name}': {e}")

    # Copy materials (linked)
    variant_obj.data.materials.clear()
    for mat in base_obj.data.materials:
        variant_obj.data.materials.append(mat)

    # Offset positions for visibility
    base_obj.location.x -= 2.0
    variant_obj.location.x = base_obj.location.x + 4.0

    print(f"✅ Duplicated '{base_obj.name}' → '{variant_obj.name}' (rig + materials preserved)")
    return variant_obj


# -----------------------------------------------------
# MAIN ENTRY
# -----------------------------------------------------

def create_textured_duplicate_with_spacing():
    """
    Creates base texture material, assigns it to the active object,
    duplicates it with rig + materials intact, and positions:
        - original at X = -2
        - duplicate at X = +2
    """
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        print("❌ Please select a mesh object first.")
        return None, None

    # Ensure base material exists
    mat, img = create_base_material_with_texture(obj)
    if not mat:
        return None, None

    # Duplicate object with rig + texture
    dup = duplicate_with_rig_and_texture(obj)

    print(f"✅ Ready: '{obj.name}' and '{dup.name}' are spaced and share materials.")
    return obj, dup


# -----------------------------------------------------
# TEST
# -----------------------------------------------------

if __name__ == "__main__":
    create_textured_duplicate_with_spacing()
