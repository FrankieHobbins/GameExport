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
        return col_copy.objects

    def merge(self, col):
        # merge all objects in collcetion
        origin_object = False
        obj_list = [o for o in col.objects if o.type == 'MESH']
        empty_list = [o for o in col.objects if o.type == 'EMPTY' and o.instance_type == "COLLECTION"]
        for o in bpy.data.objects:
            o.select_set(False)
        # deal with empty objects that could have be instances of meshes
        if bpy.context.scene.FBXFreezeInstances:
            if len(empty_list) > 0:
                bpy.context.view_layer.objects.active = empty_list[0]
                for o in empty_list:
                    o.select_set(True)
                bpy.ops.object.duplicates_make_real()
                for ob in bpy.context.selected_objects:
                    if ob.type == "MESH":
                        ob.data = ob.data.copy()  # make objects single user
                obj_list += bpy.context.selected_editable_objects
            # remove surplus empties
            for o in empty_list:
                bpy.data.objects.remove(o)
        # find origin
        for o in col.objects:
            if "origin" in o.name.lower():
                origin_object = o.location.copy()
        # remove objects from list we dont want to merge
        new_list = obj_list.copy()
        for o in new_list:
            if o.type == "EMPTY":
                obj_list.remove(o)
            if "COL_BOX" in o.name:  # TODO: add to prefs
                obj_list.remove(o)

        # select objects and join
        if len(obj_list) > 0:
            for ob in bpy.context.selected_objects:
                ob.select_set = False
            for o in obj_list:
                o.select_set(True)
            bpy.context.view_layer.objects.active = obj_list[0]
            MergeCollection.apply_modifiers(self, col)
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            # fix to stop conflicts with new merged objects against old objects
            new_name = col.name.replace("__MERGED_", "")
            for o in bpy.data.objects:
                if o.name == new_name:
                    o.name += "_CONFLICT__"
            bpy.context.active_object.name = new_name
            # set origin
            if origin_object:
                org_loc = bpy.context.scene.cursor.location
                bpy.context.scene.cursor.location = origin_object
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
                bpy.context.scene.cursor.location = org_loc
        # deal with objects we didnt want to merge but want to keep their name
        for o in col.objects:
            if "_M_" in o.name:
                new_name = o.name.replace("_M_", "")
                bpy.data.objects[new_name].name = new_name + "_CONFLICT__"
                o.name = new_name
        for o in bpy.data.objects:
            o.select_set(False)

    def apply_modifiers(self, col):
        sel_obj_cache = bpy.context.selected_objects
        for ob in bpy.context.selected_objects:
            ob.select = False
        for obj in col.objects:
            obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        for ob in bpy.context.selected_objects:
            ob.select = False
        for obj in sel_obj_cache:
            obj.select_set(True)

    def rename_merge_collection(self, name):
        if "&" in name:
            name = name.replace("&", "")  # TODO replace with global
            name += "__MERGED_"
        return name
