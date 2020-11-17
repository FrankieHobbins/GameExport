import bpy


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
