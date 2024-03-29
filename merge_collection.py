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
        # called by this class and can be run alone
        col = bpy.context.view_layer.active_layer_collection.collection
        name = MergeCollection.rename_merge_collection(self, col.name, col)
        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = name
        vlc = bpy.context.view_layer.layer_collection
        vlc.collection.children.link(col_copy)
        # merge all objects into one
        self.merge(col_copy)

    def merge_specified(self, col):
        # called by game export script
        # duplicate collection and rename
        col_copy = utils.Utils.duplicate_collection(self, col)
        col_copy.name = MergeCollection.rename_merge_collection(self, col.name, col)
        bpy.context.view_layer.layer_collection.collection.children.link(col_copy)
        # merge all objects into one
        MergeCollection.merge(self, col_copy, utils.Utils.find_origin(self, col))
        return col_copy.objects

    def merge(self, col, origin_object):
        print (f"merging {col.name}")
        obj_list = [o for o in col.objects if o.type == 'MESH']
        empty_list = [o for o in col.objects if o.type == 'EMPTY' and o.instance_type == "COLLECTION"]
        instance_list = [o for o in col.objects if o.instance_type != "NONE"]
        instance_object_children_list = []
        remove_list = []
        if origin_object:
            col.FBXExportOffset = origin_object
            #print (f"seting {col} to {origin_object}")
        for o in bpy.data.objects:
            o.select_set(False)
        # deal with instanced objects, collections, faces and verts
        if bpy.context.scene.FBXFreezeInstances:
            if len(instance_list) > 0:
                bpy.context.view_layer.objects.active = instance_list[0]
                for o in instance_list:
                    o.select_set(True)
                    instance_object_children_list = [i for i in o.children]
                bpy.ops.object.duplicates_make_real(use_base_parent=False, use_hierarchy=True)
                for ob in bpy.context.selected_objects:
                    #print(ob)
                    if ob.type == "MESH":
                        ob.data = ob.data.copy()  # make objects single user
                obj_list += bpy.context.selected_editable_objects
            # remove surplus empties
            for o in empty_list:
                bpy.data.objects.remove(o)
        new_list = obj_list.copy()
        # deal with objects not to merge or export
        for o in new_list:
            if o.type == "EMPTY":
                obj_list.remove(o)
            if "COL_BOX" in o.name or "COL_MESH" in o.name or "OUTLINE" in o.name or "!" in o.name:  # TODO: add to prefs
                obj_list.remove(o)
            if not o.show_instancer_for_viewport:
                remove_list.append(o.name)
                obj_list.remove(o)
            if o in instance_object_children_list:
                print(f"adding {o} to remove list")
                remove_list.append(o.name)
                obj_list.remove(o)
        # delete now
        for o in remove_list:
            print(f" removing {o}")
            bpy.data.objects.remove(bpy.data.objects[o])

        # select objects and join
        if len(obj_list) > 0:
            for ob in bpy.context.selected_objects:
                ob.select_set(False)
            for o in obj_list:
                o.select_set(True)
            bpy.context.view_layer.objects.active = obj_list[0]
            MergeCollection.apply_modifiers(self, col)
            MergeCollection.convert_uv(self, col)
            utils.Utils.addCustomNormalsToSelected(self)
            bpy.ops.object.join()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            # fix to stop conflicts with new merged objects against old objects
            # new_name = col.name.replace("__MERGED_", "")
            new_name = col.name.split("__MERGED_")[0]
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
            #bpy.context.active_object.location = (0,0,0)
        for o in bpy.data.objects:
            o.select_set(False)

    def apply_modifiers(self, col):
        sel_obj_cache = bpy.context.selected_objects
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
        for obj in col.objects:
            obj.select_set(True)
        bpy.ops.object.convert(target='MESH')
        for ob in bpy.context.selected_objects:
            ob.select_set(False)
        for obj in sel_obj_cache:
            obj.select_set(True)
    
    def convert_uv(self, col):
        active_obj_cache = bpy.context.active_object
        # convert attributes to uvs for geometry nodes
        for o in col.objects:
            try:                
                o.data.attributes.active = o.data.attributes["UVMap"]
                bpy.context.view_layer.objects.active = o
                bpy.ops.geometry.attribute_convert(mode="UV_MAP")
                print(o.name + " has attributes UVMap ")
            except:
                print(o.name + " has NO attributes UVMap ")
                pass
        bpy.context.view_layer.objects.active = active_obj_cache

    def rename_merge_collection(self, name, old_col):
        if "&" in name:
            col_path = utils.Utils.find_parent_path_recursive(self, old_col, "")
            col_path = col_path.replace(name+"\\", "")
            name = name.replace("&", "")  # TODO replace with global
            name += "__MERGED_" + col_path
            
        return name
