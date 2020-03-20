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
        row = layout.row()
        row.prop(context.scene, "FbxExportScale", text="scale")
        row = layout.row()
        row.prop(context.scene, "FbxExportEngine", text="engine")
        row = layout.row()
        row.prop(context.scene, "FBXExportSelected", text="Export Selected")
        row = layout.row()
        row.prop(context.scene, "FBXExportColletionIsFolder", text="Collection is Folder")
        # row.operator('gameexport.openfolder', text='Path')


class PANEL_PT_gameexport_addon_prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

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

    def draw(self, context):
        layout = self.layout
        # layout.label(text='Add bevel modifier:')
        # row = layout.row()
        # row.prop(self, 'add_bevel', expand=True)
        # layout.label(text='Testing:')
        row = layout.row()
        row.prop(self, 'special_source_workflow', expand=True)
        row.prop(self, 'default_engine_export', expand=False)


class OpenFolder(bpy.types.Operator):
    # not currently used
    bl_label = "Open Export Folder"
    bl_idname = "gameexport.openfolder"
    bl_description = "Open the export folder"

    def execute(self, context):
        # open folder in windows explorer
        bpy.ops.wm.path_open(filepath=bpy.context.scene.FbxExportPath)
        return {'FINISHED'}
