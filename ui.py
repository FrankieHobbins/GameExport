import bpy


class PANEL_PT_gameexport(bpy.types.Panel):
    # bl_idname = "gameexport.ui_panel"
    bl_label = "Export FBX"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("gameexport.export", text="Export")
        row = layout.row()
        row.prop(context.scene, "FbxExportPath", text="")
        # row.operator('gameexport.openfolder', text='Path')


class PANEL_PT_gameexport_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    add_bevel: bpy.props.EnumProperty(
        items=[
            ('bevel', 'Add bevel', '', '', 0),
            ('no_bevel', 'No bevel', '', '', 1)
        ],
        default='no_bevel'
    )

    special_source_workflow: bpy.props.BoolProperty(
        name="Unity Source Workflow",
        default=False
    )

    default_unity_fbx: bpy.props.BoolProperty(
        name="Match unity builtin FBX",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        # layout.label(text='Add bevel modifier:')
        # row = layout.row()
        # row.prop(self, 'add_bevel', expand=True)
        # layout.label(text='Testing:')
        row = layout.row()
        row.prop(self, 'special_source_workflow', expand=True)
        row.prop(self, 'default_unity_fbx', expand=True)


class OpenFolder(bpy.types.Operator):
    # not currently used
    bl_label = "Open Export Folder"
    bl_idname = "gameexport.openfolder"
    bl_description = "Open the export folder"

    def execute(self, context):
        # open folder in windows explorer
        bpy.ops.wm.path_open(filepath=bpy.context.scene.FbxExportPath)
        return {'FINISHED'}
