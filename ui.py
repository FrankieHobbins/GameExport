import bpy
from . import utils
from . import tools
from bpy.props import (BoolProperty, StringProperty, CollectionProperty)

utils = utils.Utils
tools == tools.Tools


class PathSwitcher(bpy.types.PropertyGroup):
    Show_joints: BoolProperty(
        name="Expand",
        description="Show the joints of this part",
        default=False
    )

    Part: StringProperty(
        name="Part",
        description="Part of body",
        default="",
        maxlen=1024,
    )

    First: StringProperty(
        name="Index",
        description="First part suffix",
        default="",
        maxlen=1024,
    )

    Second: StringProperty(
        name="Side",
        description="Second part suffix",
        default="",
        maxlen=1024,
    )


class PANEL_PT_gameexport_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    # TODO check this works properly on new installs
    special_source_workflow: bpy.props.BoolProperty(
        name="Unity Source Workflow",
        default=False
    )

    default_unity_fbx: bpy.props.BoolProperty(
        name="Match unity built in FBX",
        default=False
    )

    default_engine_export: bpy.props.EnumProperty(
        name="Default Engine",
        items=[
            ('unity', 'Unity', '', '', 0),
            ('unreal', 'Unreal', '', '', 1)
        ],
        default='unity'
    )

    user_path: bpy.props.StringProperty(
        name="$path$",
    )

    path_switch: bpy.props.CollectionProperty(
        type=PathSwitcher
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'special_source_workflow', expand=True)
        row.prop(self, 'default_engine_export', expand=False)
        row = layout.row()
        row.prop(self, 'user_path')
        row.prop(self, 'path_switch')


class PANEL_PT_gameexport(bpy.types.Panel):
    # bl_idname = "gameexport.ui_panel"
    bl_label = "Export FBX"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        split = row.split(factor=0.8)
        c = split.column()
        row.scale_y = 1.5
        props = c.operator("gameexport.export", text="Export")
        props.bake = False
        props.selected = False
        c = split.column()
        c.operator('gameexport.openfolder', text='', icon="FILE_FOLDER")
        row = layout.row()
        props = row.operator("gameexport.export", text="Selected")
        props.bake = False
        props.selected = True
        # row.scale_x = 2
        props = row.operator("gameexport.export", text="Bake")
        props.bake = True
        props.selected = False


class PANEL_PT_gameexporttools(bpy.types.Panel):
    # bl_idname = "gameexport.ui_panel"
    bl_label = "Tools"
    bl_parent_id = "PANEL_PT_gameexport"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        # row.label(text="Add Vertex Group to Selected Objects")
        row = layout.row()
        props = row.operator("gameexport.vertex_group_assign", text="Add Vertex Group")
        row.prop(context.scene, "NewVertexGroupName", text="")


class PANEL_PT_gameexportsettings(bpy.types.Panel):
    # bl_idname = "gameexport.ui_panel"
    bl_label = "Settings"
    bl_parent_id = "PANEL_PT_gameexport"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "FbxExportPath", text="path")
        path = bpy.context.scene.FbxExportPath
        path = path.replace("$path$", bpy.context.preferences.addons[__package__].preferences.user_path)
        layout.label(text=path)
        row = layout.row()
        row.prop(context.scene, "FbxExportPrefix", text="prefix")
        row = layout.row()
        row.prop(context.scene, "FbxExportScale", text="scale")
        row = layout.row()
        row.prop(context.scene, "FbxExportEngine", text="engine")
        row = layout.row()
        row.prop(context.scene, "FBXFixUnityRotation", text="Fix Unity Rotation")
        row = layout.row()
        row.prop(context.scene, "FBXExportSM", text="Individual Objects")
        row = layout.row()
        row.prop(context.scene, "FBXExportCentreMeshes", text="Centred")
        row = layout.row()
        row.prop(context.scene, "FBXKeepEmpties", text="Keep Empties")
        row = layout.row()
        row.prop(context.scene, "FBXFreezeInstances", text="Freeze Instances")
        row = layout.row()
        row.prop(context.scene, "FBXExportColletionIsFolder", text="Collection is Folder")
        row = layout.row()
        row.prop(context.scene, "FBXFlipUVIndex", text="Reverse UV channels")
        row = layout.row()
        row.prop(context.scene, "FBXLeaveExport", text="DEBUG: Leave Objects")
        """
        if len(bpy.data.actions) > 0:
            layout.template_list("ACTIONS_UL_List", "", bpy.data, "actions", context.object, "action_list_index", rows=2)
            try:
                if bpy.types.Scene.LastAnimSelected != bpy.data.actions[bpy.context.object.action_list_index]:
                    bpy.context.object.animation_data.action = bpy.data.actions[bpy.context.object.action_list_index]
                    currentaction = bpy.context.object.animation_data.action
                    keys = currentaction.frame_range
                    lastkey = (keys[-1])
                    bpy.context.scene.frame_end = lastkey
                bpy.types.Scene.LastAnimSelected = bpy.data.actions[bpy.context.object.action_list_index]  # lets you selected with the action dropdown from action editor
            except:
                pass
        """


class OpenFolder(bpy.types.Operator):
    # not currently used
    bl_label = "Open Export Folder"
    bl_idname = "gameexport.openfolder"
    bl_description = "Open the export folder"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # open folder in windows explorer
        path = bpy.context.scene.FbxExportPath
        path = path.replace("$path$", bpy.context.preferences.addons['GameExport'].preferences.user_path)
        bpy.ops.wm.path_open(filepath=path)
        return {'FINISHED'}


class ACTIONS_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text="", translate=False, icon_value=icon)
        if bpy.context.active_object is not None:
            row = layout.row(align=False)
            row.prop(item, "name", text="", emboss=False)
            row.prop(item, "Export", text="")
