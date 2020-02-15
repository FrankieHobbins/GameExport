import bpy


class GameExportUI(bpy.types.Panel):
    bl_idname = "gameexport.ui_panel"
    bl_label = "Export FBX"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("gameexport.main", text="Export")
        row = layout.row()
        row.prop(context.scene, "FbxExportPath", text="")        
        #row.operator('gameexport.openfolder', text='Path')


class OpenFolder(bpy.types.Operator):
    bl_label = "Open Export Folder"
    bl_idname = "gameexport.openfolder"
    bl_description = "Open the export folder"

    def execute(self, context):
        bpy.ops.wm.path_open(filepath=bpy.context.scene.FbxExportPath)
        return {'FINISHED'}
