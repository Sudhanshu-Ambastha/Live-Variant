"""
ui.py

Blender UI Panel for Live Variant System.
Lets users:
 - Duplicate an object with proper texture setup.
 - Define multiple source→target color remaps.
 - Generate a recolored variant automatically.

Integrates with:
 - texture_setup.py
 - multi_remap_controller.py
"""

import bpy
from bpy.props import FloatVectorProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, Operator, Panel


# --------------------------------------------------------
# 1️⃣ Property Group for each color remap pair
# --------------------------------------------------------
class LiveVariantColorMap(PropertyGroup):
    source_color: FloatVectorProperty(
        name="Source",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0)
    )

    target_color: FloatVectorProperty(
        name="Target",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 0.0, 0.0, 1.0)
    )


# --------------------------------------------------------
# 2️⃣ Scene-level property to hold multiple remaps
# --------------------------------------------------------
class LiveVariantSettings(PropertyGroup):
    remap_list: CollectionProperty(type=LiveVariantColorMap)


# --------------------------------------------------------
# 3️⃣ Operators
# --------------------------------------------------------
class LV_OT_AddRemap(Operator):
    """Add a new color remap"""
    bl_idname = "livevariant.add_remap"
    bl_label = "Add Remap"

    def execute(self, context):
        context.scene.live_variant_settings.remap_list.add()
        return {'FINISHED'}


class LV_OT_RemoveRemap(Operator):
    """Remove the last color remap"""
    bl_idname = "livevariant.remove_remap"
    bl_label = "Remove Remap"

    def execute(self, context):
        remaps = context.scene.live_variant_settings.remap_list
        if remaps:
            remaps.remove(len(remaps) - 1)
        return {'FINISHED'}


class LV_OT_CreateBaseAndVariant(Operator):
    """Create base + variant with textures, rig, and spacing"""
    bl_idname = "livevariant.create_pair"
    bl_label = "Create Textured Pair"

    def execute(self, context):
        from texture_setup import create_textured_duplicate_with_spacing
        base_obj, variant_obj = create_textured_duplicate_with_spacing()
        if not base_obj or not variant_obj:
            self.report({'ERROR'}, "Failed to create pair — check selection.")
            return {'CANCELLED'}
        self.report({'INFO'}, f"Pair created: {base_obj.name}, {variant_obj.name}")
        return {'FINISHED'}


class LV_OT_GenerateVariant(Operator):
    """Generate variant and apply color remaps"""
    bl_idname = "livevariant.generate_variant"
    bl_label = "Apply Color Remaps"

    def execute(self, context):
        from multi_remap_controller import apply_multi_remap

        # Validation
        base_obj = context.active_object
        if not base_obj:
            self.report({'ERROR'}, "Select the base mesh first.")
            return {'CANCELLED'}

        # Try to find its duplicate
        variant_obj = None
        for obj in bpy.context.scene.objects:
            if obj.name.startswith(f"{base_obj.name}_Variant"):
                variant_obj = obj
                break

        if not variant_obj:
            self.report({'ERROR'}, "Variant not found. Click 'Create Textured Pair' first.")
            return {'CANCELLED'}

        # Collect user-defined remaps
        remaps = []
        for entry in context.scene.live_variant_settings.remap_list:
            remaps.append((tuple(entry.source_color), tuple(entry.target_color)))

        # Apply multi-remap
        apply_multi_remap(base_obj, variant_obj, remaps)
        self.report({'INFO'}, f"Remaps applied to {variant_obj.name}")
        return {'FINISHED'}


# --------------------------------------------------------
# 4️⃣ UI Panel
# --------------------------------------------------------
class LV_PT_LiveVariantPanel(Panel):
    bl_label = "Live Variant System"
    bl_idname = "LV_PT_live_variant_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Live Variant'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.live_variant_settings

        col = layout.column(align=True)
        col.operator("livevariant.create_pair", icon="MESH_DATA")
        layout.separator()

        layout.label(text="Color Remap Pairs:")
        for i, item in enumerate(settings.remap_list):
            box = layout.box()
            row = box.row()
            row.prop(item, "source_color", text="From")
            row.prop(item, "target_color", text="To")

        row = layout.row(align=True)
        row.operator("livevariant.add_remap", text="+ Add")
        row.operator("livevariant.remove_remap", text="– Remove")

        layout.separator()
        layout.operator("livevariant.generate_variant", icon='NODETREE')


# --------------------------------------------------------
# 5️⃣ Registration
# --------------------------------------------------------
classes = (
    LiveVariantColorMap,
    LiveVariantSettings,
    LV_OT_AddRemap,
    LV_OT_RemoveRemap,
    LV_OT_CreateBaseAndVariant,
    LV_OT_GenerateVariant,
    LV_PT_LiveVariantPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.live_variant_settings = PointerProperty(type=LiveVariantSettings)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.live_variant_settings


if __name__ == "__main__":
    register()
