import bpy
import os
from mathutils import Vector
from . import merge_collection
from . import make_list


class Utils(bpy.types.Operator):
    bl_label = "Create"
    bl_idname = "gameexport.utils"
    bl_description = "A demo operator"
    bl_options = {"UNDO"}

    def get_all_children_collections(self, col, col_children):
        if col.children:
            for child in col.children:
                col_children.append(child)
                if child.children:
                    Utils.get_all_children_collections(self, child, col_children)
        return col_children

    def cleanup_after_export(self):
        for col in bpy.data.collections:
            if "EXPORT" in col.name:
                bpy.data.collections.remove(col)

    def find_parent(self, col):
        for c in bpy.data.collections:
            if c.children:
                for child in c.children:
                    if child == col:
                        return c
        return bpy.context.scene.collection

    def find_parent_recursive(self, col):
        if col.name in bpy.context.view_layer.layer_collection.children:
            return col
        for c in bpy.data.collections:
            if col.name in bpy.data.collections.children:
                return(Utils.find_parent_recursive(self, c))

    def find_view_layer_collection(self, col, col_layer, col_list):
        if col_layer.collection == col:
            col_list.append(col_layer)
        if col_layer.children:
            for child in col_layer.children:
                Utils.find_view_layer_collection(self, col, child, col_list)
        else:
            return col_list

    def find_collection(self, obj):
        for c in bpy.data.collections:            
            if obj in list(c.objects):
                return c

    def find_origin(self, col):
        origin_object = False
        print(f"-- finding origin for col {col}")
        # see if origin_object exists in current collection
        for o in col.objects:
            if "origin" in o.name.lower():
                origin_object = o.location.copy()
        # see if origin_object exists in parent collections
        if not origin_object:
            origin_object = Utils.find_origin_recursive(self, col)
        print(origin_object)
        print("finishing")
        return origin_object

    def find_origin_recursive(self, col):
        parent = Utils.find_parent(self, col)
        origin_object = False
        for o in parent.objects:
            if "origin" in o.name.lower():
                origin_object = o.location.copy()
                return origin_object
        if not origin_object:
            if parent == bpy.context.scene.collection:
                return origin_object
            return Utils.find_origin_recursive(self, parent)
        return origin_object

    def is_valid(self, col, bake):
        low = ["low_", "lo_", "_low", "_lo"]
        high = ["high_", "hi_", "_high", "_hi"]
        if bake == "low":
            if not any(col.name.lower().find(el) != -1 for el in low):
                return False
        if bake == "high":
            if not any(col.name.lower().find(el) != -1 for el in high):
                return False
        if bake == "":
            if "^" in col.name:
                return False
        exclusion_list = ["*", "cutter"]  # TODO place in user prefs
        for i in exclusion_list:
            if i.lower() in col.name.lower():
                return False
        if col.hide_viewport:  # or col.hide_render ??
            return False
        # TODO also check for parent
        vlc = bpy.context.view_layer.layer_collection
        vlc_list = []
        Utils.find_view_layer_collection(self, col, vlc, vlc_list)
        if len(vlc_list) > 0:
            if vlc_list[0].exclude:
                return False
        if "__MERGED_" in col.name:
            return False
        if "EXPORT" in col.name:
            return False
        return True

    def should_merge(self, col):
        if not col.objects:
            return False
        if "&" in col.name:
            return True
        return False

    def list_all_layercollections_and_collections(self, col_list, vl):
        col_list.append([vl, vl.collection])
        for child in vl.children:
            Utils.list_all_layercollections_and_collections(
                self, col_list, child)
        return col_list

    def duplicate_collection(self, col):
        new_name = col.name + "_DUPLICATE"
        new_col = bpy.data.collections.new(new_name)
        Utils.duplicate_objects(self, col, new_col)
        return new_col

    def set_origin(self, pos):
        saved_location = bpy.context.scene.cursor.location
        bpy.context.scene.cursor.location = pos
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = saved_location

    def duplicate_objects(self, old_col, new_col):
        merge_prefix = "_M_"  # TODO make global
        for obj in old_col.objects:
            if obj.type == "MESH":
                obj_data = obj.data.copy()
                new_obj = bpy.data.objects.new(merge_prefix + obj.name, obj_data)
                new_col.objects.link(new_obj)
                new_obj.matrix_world = obj.matrix_world
                new_obj.rotation_euler = obj.rotation_euler
                new_obj.data.use_auto_smooth = obj.data.use_auto_smooth
                new_obj.data.auto_smooth_angle = obj.data.auto_smooth_angle
                for vertexGroup in obj.vertex_groups:
                    new_obj.vertex_groups.new(name=vertexGroup.name)
                Utils.copy_modifier(self, obj, new_obj)
            elif obj.type == "EMPTY" and bpy.context.scene.FBXFreezeInstances and obj.instance_type == "COLLECTION":
                new_empty = bpy.data.objects.new("empty", None)
                new_empty.name = obj.name + "_DUPLICATE"
                new_col.objects.link(new_empty)
                new_empty.matrix_world = obj.matrix_world
                new_empty.rotation_euler = obj.rotation_euler
                new_empty.instance_type = obj.instance_type
                new_empty.instance_collection = obj.instance_collection
            elif obj.type == "EMPTY":  # and "origin" in obj.name.lower():
                new_col.objects.link(obj)

    def copy_modifier(self, source, target):
        active_object = source
        target_object = target
        for m_src in active_object.modifiers:
            m_dst = target_object.modifiers.get(m_src.name, None)
            if not m_dst:
                m_dst = target_object.modifiers.new(m_src.name, m_src.type)
            # collect names of writable properties
            properties = [p.identifier for p in m_src.bl_rna.properties
                          if not p.is_readonly]
            # copy those properties
            for prop in properties:
                setattr(m_dst, prop, getattr(m_src, prop))

    def setpath(self, col_name):
        path = bpy.context.scene.FbxExportPath
        path = path.replace("$path$", bpy.context.preferences.addons['GameExport'].preferences.user_path)
        prefix = bpy.context.scene.FbxExportPrefix
        if path == "":
            path = os.path.dirname(bpy.data.filepath) + "\\"
        elif path[1] != ":":
            path = os.path.dirname(bpy.data.filepath) + "\\" + path
        col_name = col_name.replace("&", "")  # TODO replace with global
        if bpy.context.scene.FBXExportColletionIsFolder:
            col_name = col_name + "\\" + col_name
        path += prefix + col_name + ".fbx"
        try:
            dir_name = os.path.dirname(path)
            os.makedirs(dir_name)
        except:
            pass

        return path

    def setpathspecialcases(self, path, bake):
        path = os.path.dirname(bpy.data.filepath) + "\\" + bpy.path.basename(bpy.context.blend_data.filepath)
        if not bake:
            if "Source~" in path:
                path = path.replace("Source~", "")
            if "Art_Source" in path:
                # TODO put these in user prefs
                path = path.replace("Art_Source", "UP_Client")
        if ".blend" in path:
            path = path.replace(".blend", ".fbx")
        if ".Blend" in path:
            path = path.replace(".Blend", ".fbx")
        return path

    def actionstoNLA(self, filter):
        for nlatrack in bpy.context.object.animation_data.nla_tracks:
            bpy.context.object.animation_data.nla_tracks.remove(nlatrack)

        for action in bpy.data.actions:
            if filter in action.name:
                bpy.context.object.animation_data.nla_tracks.new()
                bpy.context.object.animation_data.nla_tracks[(len(bpy.context.object.animation_data.nla_tracks)-1)].name = action.name
                bpy.context.object.animation_data.nla_tracks[(len(bpy.context.object.animation_data.nla_tracks)-1)].strips.new(action.name,0,action)

    def flipUVIndex(self):
        uvl = bpy.context.view_layer.objects.active.data.uv_layers
        if (len(uvl) == 2):
            # set active uv to 0
            uvl.active_index = 0
            # get 0 name
            name = uvl[0].name
            # duplicate, will end up at 2
            bpy.ops.mesh.uv_texture_add()
            # delete 0
            uvl.active_index = 0
            bpy.ops.mesh.uv_texture_remove()
            # set index 1 to be name
            uvl[1].name = name

    def addCustomNormalsToSelected(self):
        a = bpy.context.active_object
        for i in bpy.context.selected_objects:
            try:
                bpy.context.view_layer.objects.active = i
                bpy.ops.mesh.customdata_custom_splitnormals_add()
            except:
                pass
        bpy.context.view_layer.objects.active = a

    def duplicate(self, name, object, col):
        data = object.data
        new_obj = bpy.data.objects.new(name, data)
        # col = Utils.find_collection(self, object)
        col.objects.link(new_obj)
        new_obj.matrix_world = object.matrix_world
        for vertexGroup in object.vertex_groups:
            new_obj.vertex_groups.new(name=vertexGroup.name)
        return new_obj

    def lod(self, objects_to_lod, lod_collection, export_collection):
        # objects_to_lod = bpy.context.selected_objects
        remove = False
        for lod_obj in objects_to_lod:            
            for element in lod_obj.vertex_groups:
                objects = [i for i in lod_collection.objects if element.name in i.name]
                for o in objects:
                    remove = True
                    new_obj = Utils.duplicate(self, o.name, lod_obj, export_collection)
                    Utils.copy_modifier(self, bpy.data.objects[o.name], new_obj)
        if remove:
            export_collection.objects.unlink(lod_obj)
            
