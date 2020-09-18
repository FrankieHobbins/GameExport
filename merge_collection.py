import bpy
from . import utils


class MergeCollection(bpy.types.Operator):
    bl_label = "Merge Collection"
    bl_idname = "gameexport.mergecollection"
    bl_description = "Used to merge all objects inside a collection into 1"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.merge_active()
        return {"FINISHED"}

    def merge_active(self):
        col = bpy.context.view_layer.active_layer_collection.collection
        name = MergeCollection.rename_merge_collection(self, col.name)
        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = name
        vlc = bpy.context.view_layer.layer_collection
        vlc.collection.children.link(col_copy)
        # merge all objects into one
        self.merge(col_copy)

    def merge_specified(self, col):
        # duplicate collection and rename
        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = MergeCollection.rename_merge_collection(self, col.name)
        bpy.context.view_layer.layer_collection.collection.children.link(col_copy)
        # merge all objects into one
        MergeCollection.merge(self, col_copy)
        return col_copy.objects[0]

    def merge(self, col):
        c = {}
        origin_object = False
        c["active_object"] = bpy.context.active_object
        obj_list = [o for o in col.objects if o.type == 'MESH']
        empty_list = [o for o in col.objects if o.type == 'EMPTY']

        """
        # deal with empty objects that could have be instances of meshes
        if len(empty_list) > 0:
            print(f" **WARNING** Attempting to merge objects that are instanced, may not have correct result {bpy.context.selected_editable_objects}")
            bpy.context.view_layer.objects.active = empty_list[0]
            c["selected_editable_objects"] = empty_list
            bpy.ops.object.duplicates_make_real()
            obj_list += bpy.context.selected_editable_objects
        """

        for o in col.objects:
            if "origin" in o.name.lower():
                origin_object = o.location.copy()
            print(col.name + "||" + o.name)

        # select objects and join
        if len(obj_list) > 0:            
            bpy.context.view_layer.objects.active = obj_list[0]
            c["active_object"] = obj_list[0]
            c["selected_editable_objects"] = obj_list
            MergeCollection.apply_modifiers(self, col)
            bpy.ops.object.join(c)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            # fix to stop conflicts with new merged objects against old objects
            new_name = col.name.replace("__MERGED_", "")
            for o in bpy.data.objects:
                if o.name == new_name:
                    o.name += "_CONFLICT__"
            bpy.context.active_object.name = new_name
            if origin_object:
                print(origin_object)
                org_loc = bpy.context.scene.cursor.location
                bpy.context.scene.cursor.location = origin_object
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                bpy.context.scene.cursor.location = org_loc

    def apply_modifiers(self, col):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in col.objects:
            obj.select_set(True)
        bpy.ops.object.convert(target='MESH')

    def rename_merge_collection(self, name):
        if "&" in name:
            name = name.replace("&", "")  # TODO replace with global
            name += "__MERGED_"
        return name
