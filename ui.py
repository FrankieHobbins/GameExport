import bpy


class GameExportUI(bpy.types.Panel):
    bl_idname = "Wha"
    bl_label = "Export FBX"
    bl_category = "GameExport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("gameexport.main", text="Export")
        row = layout.row()
        row.prop(context.scene, "FbxExportPath")