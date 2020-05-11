import importlib
import bpy
bl_info = {
    "name": "Game Export",
    "description": "A Game Exporter",
    "author": "Frankie Hobbins",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "wiki_url": "my github url here",
    "tracker_url": "my github url here/issues",
    "category": "Animation"
}


# When main is already in local, we know this is not the initial import...
if "main" in locals():
    importlib.reload(main)
    importlib.reload(utils)
    importlib.reload(merge_collection)
    importlib.reload(make_list)
    importlib.reload(ui)

from . import make_list
from . import merge_collection
from . import utils
from . import main
from . import ui

# main.FirstOperator.doprint()

classes = (
    main.Main,
    utils.Utils,
    make_list.MakeList,
    merge_collection.MergeCollection,
    ui.PANEL_PT_gameexport,
    ui.OpenFolder,
    ui.PANEL_PT_gameexport_addon_prefs
)

bpy.types.Scene.FbxExportPath = bpy.props.StringProperty(name="Path", subtype="DIR_PATH")
bpy.types.Scene.FbxExportScale = bpy.props.FloatProperty(name="FbxExportScale", default=1.0)
bpy.types.Scene.FbxExportEngine = bpy.props.EnumProperty(
        items=[
            ('default', 'Default', '', '', 0),
            ('unity', 'Unity', '', '', 1),
            ('unreal', 'Unreal', '', '', 2)
        ],
        default='unity'
        )
bpy.types.Scene.FBXExportSelected = bpy.props.BoolProperty(name="FBXExportSelected", default=False)
bpy.types.Scene.FBXExportSM = bpy.props.BoolProperty(name="FBXExportSM", default=False)
bpy.types.Scene.FBXExportColletionIsFolder = bpy.props.BoolProperty(name="FBXExportColletionIsFolder", default=False)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()
