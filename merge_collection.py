import bpy
from . import utils


class MergeCollection(bpy.types.Operator):
    bl_label = "Merge Collection"
    bl_idname = "gameexport.mergecollection"
    bl_description = "Used to merge all objects inside a collection into 1"

    def execute(self, context):
        self.merge_active()
        return {"FINISHED"}

    def merge(self, col):
        c = {}
        obj_list = [o for o in col.objects if o.type == 'MESH']
        bpy.context.view_layer.objects.active = obj_list[0]
        c["active_object"] = bpy.context.active_object
        c["selected_editable_objects"] = obj_list
        MergeCollection.apply_modifiers(self, col)
        bpy.ops.object.join(c)
        bpy.ops.object.transform_apply(
            location=True, rotation=True, scale=True)
        bpy.context.active_object.name = col.name

    def apply_modifiers(self, col):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in col.objects:
            obj.select_set(True)
        bpy.ops.object.convert(target='MESH')

    def merge_alone(self, col, name, target_col):
        # copy and rename
        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = name

        # link to target collection
        target_col.children.link(col_copy)

        # merge all objects into one
        MergeCollection.merge(self, col_copy)

    def merge_active(self):

        col = bpy.context.view_layer.active_layer_collection.collection

        if "&" in col.name:
            name = col.name.replace("&", "") # TODO replace with global
        else:
            name = col.name + "&"

        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = name
        vlc = bpy.context.view_layer.layer_collection
        vlc.collection.children.link(col_copy)

        # merge all objects into one
        self.merge(col_copy)