import bpy


class OpenFolder(bpy.types.Operator):
    # not currently used
    bl_label = "Open Export Folder"
    bl_idname = "gameexport.openfolder"
    bl_description = "Open the export folder"

    def execute(self, context):
        # open folder in windows explorer
        bpy.ops.wm.path_open(filepath=bpy.context.scene.FbxExportPath)
        return {'FINISHED'}


from bpy.props import (BoolProperty, StringProperty, CollectionProperty)


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


class ACTIONS_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.label(text="", translate=False, icon_value=icon)        
        if bpy.context.active_object is not None:
            row = layout.row(align=False)
            row.prop(item,"name", text="", emboss=False)
            row.prop(item,"Export", text="")

class PANEL_PT_gameexport(bpy.types.Panel):
    # bl_idname = "gameexport.ui_panel"
    bl_label = "Export FBX"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        props = layout.operator("gameexport.export", text="Export")
        props.bake = False
        props.selected = False
        row = layout.row()
        props = layout.operator("gameexport.export", text="Selected")
        props.bake = False
        props.selected = True
        row = layout.row()
        props = layout.operator("gameexport.export", text="Bake")
        props.bake = True
        props.selected = False
        row = layout.row()
        row.prop(context.scene, "FbxExportPath", text="path")
        row = layout.row()
        row.prop(context.scene, "FbxExportPrefix", text="prefix")
        row = layout.row()
        row.prop(context.scene, "FbxExportScale", text="scale")
        row = layout.row()
        row.prop(context.scene, "FbxExportEngine", text="engine")
        row = layout.row()
        row.prop(context.scene, "FBXFixUnityRotation", text="Fix Unity Rotation")
        row = layout.row()
        row.prop(context.scene, "FBXLeaveExport", text="Leave Objects")
        row = layout.row()
        row.prop(context.scene, "FBXExportSM", text="Individual Objets")
        row = layout.row()
        row.prop(context.scene, "FBXExportCentreMeshes", text="Centred")
        row = layout.row()
        row.prop(context.scene, "FBXExportColletionIsFolder", text="Collection is Folder")
        row = layout.row()
        row.prop(context.scene, "FBXFlipUVIndex", text="Reverse UV channels")       
        if len(bpy.data.actions) > 0:
            layout.template_list("ACTIONS_UL_List", "", bpy.data, "actions", context.object, "action_list_index", rows=2)            
            if bpy.types.Scene.LastAnimSelected != bpy.data.actions[bpy.context.object.action_list_index]:
                bpy.context.object.animation_data.action = bpy.data.actions[bpy.context.object.action_list_index]
                currentaction = bpy.context.object.animation_data.action
                keys = currentaction.frame_range
                lastkey = (keys[-1])
                bpy.context.scene.frame_end = lastkey
            bpy.types.Scene.LastAnimSelected = bpy.data.actions[bpy.context.object.action_list_index]  # lets you selected with the action dropdown from action editor      

        # row.operator('gameexport.openfolder', text='Path')


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

    path_switch: bpy.props.CollectionProperty(
        type=PathSwitcher
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'special_source_workflow', expand=True)
        row.prop(self, 'default_engine_export', expand=False)
        row = layout.row()
        row.prop(self, 'path_switch')
