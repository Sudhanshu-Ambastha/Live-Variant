bl_info = {
    "name": "Live Variant Color Remapper",
    "author": "Sudhanshu Ambastha",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Live Variant",
    "description": "Create textured duplicates with automatic color remapping",
    "category": "Material",
}

from utils import ui

def register():
    ui.register()

def unregister():
    ui.unregister()

if __name__ == "__main__":
    register()
