import bpy
from . import main


class Tools(bpy.types.Operator):
    bl_label = "Game Export Tools"
    bl_idname = "gameexport.tools"
    bl_description = "game export tools"
    bl_options = {"REGISTER", "UNDO"}

    def vertex_group_assign(self, vg_name):
        for o in bpy.context.selected_objects:
            if vg_name in o.vertex_groups:
                pass
            else:
                o.vertex_groups.new(name=vg_name)
            o.vertex_groups[vg_name].add(range(0, len(o.data.vertices)), 1, 'REPLACE')


class VetexGroupAssign(bpy.types.Operator):
    bl_label = "Game Export Tools"
    bl_idname = "gameexport.vertex_group_assign"
    bl_description = "game export tools vertex group assign"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.vertex_group_assign()
        return {"FINISHED"}

    def vertex_group_assign(self):
        vg_name = bpy.context.scene.NewVertexGroupName
        for o in bpy.context.selected_objects:
            if o.type == "MESH":
                print("tf")
                if vg_name in o.vertex_groups:
                    pass
                else:
                    o.vertex_groups.new(name=vg_name)
                o.vertex_groups[vg_name].add(range(0, len(o.data.vertices)), 1, 'REPLACE')


class VetexGroupRemove(bpy.types.Operator):
    bl_label = "Game Export Tools"
    bl_idname = "gameexport.vertex_group_remove"
    bl_description = "game export tools vertex group assign"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        vg_name = bpy.context.scene.NewVertexGroupRemoveName
        for o in bpy.context.selected_objects:
            for vg in o.vertex_groups:
                if vg_name in vg.name:
                    o.vertex_groups.remove(vg)
        return {"FINISHED"}


class ProcessWithoutExport(bpy.types.Operator):
    bl_label = "Game Export Tools"
    bl_idname = "gameexport.process_without_export"
    bl_description = "game export tools process model without exporting"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.context.scene.FBXProcessWithoutExport = True
        bpy.ops.gameexport.export(selected=True)
        bpy.context.scene.FBXProcessWithoutExport = False
        return {"FINISHED"}
