import importlib
import bpy
bl_info = {
    "name": "Game Export",
    "description": "A Game Exporter",
    "author": "Frankie Hobbins",
    "version": (1, 1, 7),
    "blender": (2, 90, 0),
    "wiki_url": "my github url here",
    "category": "Import-Export"
}


# When main is already in local, we know this is not the initial import...
if "main" in locals():
    importlib.reload(main)
    importlib.reload(utils)
    importlib.reload(merge_collection)
    importlib.reload(make_list)
    importlib.reload(ui)
    importlib.reload(export)
    importlib.reload(tools)

from . import make_list
from . import merge_collection
from . import utils
from . import main
from . import ui
from . import export
from . import tools

classes = (
    ui.ACTIONS_UL_List,
    ui.PathSwitcher,
    main.Main,
    utils.Utils,
    make_list.MakeList,
    merge_collection.MergeCollection,
    ui.PANEL_PT_gameexport,
    ui.PANEL_PT_gameexportsettings,
    ui.PANEL_PT_gameexporttools,
    ui.OpenFolder,
    ui.PANEL_PT_gameexport_addon_prefs,
    export.FBXExport,
    tools.Tools,
    tools.VetexGroupAssign,
    tools.VetexGroupRemove,
    tools.CopyVertexGroups,
)


def update_path(self, context):
    self.FbxExportPath = self.FbxExportPath.replace(bpy.context.preferences.addons[__package__].preferences.user_path, "$path$")


bpy.types.Scene.FbxExportPath = bpy.props.StringProperty(name="Path", default="", subtype="DIR_PATH", description="Path to export to", update=update_path)
bpy.types.Scene.FbxExportPrefix = bpy.props.StringProperty(name="FbxExportPrefix", description="Prefix to put before each fbx")
bpy.types.Scene.FbxExportScale = bpy.props.FloatProperty(name="FbxExportScale", default=1.0, description="Fbx Export Scale")
bpy.types.Scene.FbxExportEngine = bpy.props.EnumProperty(
    items=[
        ('default', 'Default', '', '', 0),
        ('unity', 'Unity', '', '', 1),
        ('unreal', 'Unreal', '', '', 2)
    ],
    default='unity'
)
bpy.types.Scene.FBXExportSelected = bpy.props.BoolProperty(name="FBXExportSelected", default=False, description="Only export collection of currently selected object")
bpy.types.Scene.FBXExportSM = bpy.props.BoolProperty(name="FBXExportSM", default=False, description="Each object gets a unique FBX")
bpy.types.Scene.FBXExportCentreMeshes = bpy.props.BoolProperty(name="FBXExportCentreMeshes", default=False, description="Center meshes before exporting. For merged meshes, any object in collection called \"origin\" will be used to set the origin before centering")
bpy.types.Scene.FBXExportColletionIsFolder = bpy.props.BoolProperty(name="FBXExportColletionIsFolder", default=False, description="Export Collections as windows folders")
bpy.types.Scene.FBXLeaveExport = bpy.props.BoolProperty(name="FBXLeaveExport", default=False, description="Debug option to see whats been exported")
# bpy.types.Scene.FBXProcessWithoutExport = bpy.props.BoolProperty(name="FBXProcessWithoutExport", default=True, description="Debug option to process without exporting")
bpy.types.Scene.FBXFixUnityRotation = bpy.props.BoolProperty(name="FBXFixUnityRotation", default=False, description="Rotate on export to fix the issue where models appaer in unity with rotation offset")
bpy.types.Scene.FBXFlipUVIndex = bpy.props.BoolProperty(name="FBXFlipUVIndex", default=False, description="Set UV0 to be UV1 and UV1 to be UV0")
bpy.types.Scene.FBXKeepEmpties = bpy.props.BoolProperty(name="FBXKeepEmpties", default=False, description="Keep empties, apart from origins")
bpy.types.Scene.FBXFreezeInstances = bpy.props.BoolProperty(name="FBXFreezeInstances", default=False, description="Turn instance geo into real geo")
bpy.types.Object.action_list_index = bpy.props.IntProperty()
bpy.types.Object.FBXExportOffset = bpy.props.FloatVectorProperty(size=3)
bpy.types.Action.Export = bpy.props.BoolProperty(name="Export")
bpy.types.Scene.LastAnimSelected = bpy.props.StringProperty(name="Last Anim Selected")
bpy.types.Scene.ExportStringReplace = bpy.props.StringProperty(name="what")
bpy.types.Collection.FBXExportOffset = bpy.props.FloatVectorProperty(size=3)
# tools
bpy.types.Scene.NewVertexGroupName = bpy.props.StringProperty(name="Vertex Group Name", default="new vertex group", description="Path to export to")
bpy.types.Scene.NewVertexGroupRemoveName = bpy.props.StringProperty(name="Vertex Group Remove Name", default="", description="Vertex Group to remove, leave blank for all")


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
