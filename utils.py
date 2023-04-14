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
            if col.name in c.children:
                return(Utils.find_parent_recursive(self, c))

    def find_parent_path_recursive(self, col, path_str):
        if col is None:
            return path_str
        path_str = col.name + "\\" + path_str
        parent_col = None
        for c in bpy.data.collections:
            if col.name in c.children:
                parent_col = c
                break
        return Utils.find_parent_path_recursive(self, parent_col, path_str)

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
        # see if origin_object exists in current collection
        for o in col.objects:
            if "origin" in o.name.lower():
                origin_object = o.location.copy()
        # see if origin_object exists in parent collections
        if not origin_object:
            origin_object = Utils.find_origin_recursive(self, col)
        else:
            col.FBXExportOffset = origin_object
            # print(f"--setting origin for col {col} at {origin_object}")
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
        if bpy.context.scene.FBXExportHigh == False:

            exclusion_list = exclusion_list + high
        if bpy.context.scene.FBXExportLow == False:
            exclusion_list = exclusion_list + low

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
        child_parent_list = []
        for obj in old_col.objects:
            if obj.parent and obj.parent.name in old_col.objects:
                obj_name = obj.name
                if obj.type == "MESH":
                    obj_name = merge_prefix + obj_name
                obj_parent_name = obj.parent.name
                if obj.parent.type == "MESH":
                    obj_parent_name = merge_prefix + obj_parent_name
                child_parent_list.append([obj_name, obj_parent_name])
            if obj.type == "MESH":
                new_obj = obj.copy()
                new_obj.name = merge_prefix + obj.name
                new_obj.data = obj.data.copy()
                new_obj.parent = obj.parent
                new_col.objects.link(new_obj)
            elif obj.instance_type == "COLLECTION" and not bpy.context.scene.FBXCullInstanceCollections:
                new_empty = bpy.data.objects.new("empty", None)
                new_empty.name = obj.name + "_DUPLICATE"
                new_col.objects.link(new_empty)
                new_empty.matrix_world = obj.matrix_world
                new_empty.rotation_euler = obj.rotation_euler
                new_empty.instance_type = obj.instance_type
                new_empty.instance_collection = obj.instance_collection
            elif obj.type == "EMPTY":  # and "origin" in obj.name.lower():
                new_col.objects.link(obj)
        # reparent
        for item in child_parent_list:
            bpy.data.objects[item[0]].parent = bpy.data.objects[item[1]]
            bpy.data.objects[item[0]].matrix_world[0][3] += bpy.data.objects[item[0]].matrix_parent_inverse[0][3]
            bpy.data.objects[item[0]].matrix_world[1][3] += bpy.data.objects[item[0]].matrix_parent_inverse[1][3]
            bpy.data.objects[item[0]].matrix_world[2][3] += bpy.data.objects[item[0]].matrix_parent_inverse[2][3]

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

    def setpath(self, col_name, obj_name):
        path = bpy.context.scene.FbxExportPath
        print("path is: ", path)
        if bpy.context.preferences.addons['GameExport'].preferences.user_path != "":
            path = path.replace("$path$", bpy.context.preferences.addons['GameExport'].preferences.user_path)
        prefix = bpy.context.scene.FbxExportPrefix
        if path == "":
            path = os.path.dirname(bpy.data.filepath) + "\\"
        elif path[1] != ":":
            path = os.path.dirname(bpy.data.filepath) + "\\" + path
        col_name = col_name.replace("&", "")  # TODO replace with global
        if bpy.context.scene.FBXExportColletionIsFolder:
            print(col_name, obj_name[0])
            path += col_name + "\\" + prefix + obj_name[0] + ".fbx"
        else:
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
                path = path.replace("Art_Source", "Game\\UP_Client")
        if ".blend" in path:
            path = path.replace(".blend", ".fbx")
        if ".Blend" in path:
            path = path.replace(".Blend", ".fbx")
        return path

    def actionstoNLA(self, filter):
        try:
            for nlatrack in bpy.context.object.animation_data.nla_tracks:
                bpy.context.object.animation_data.nla_tracks.remove(nlatrack)

            for action in bpy.data.actions:
                if filter in action.name:
                    bpy.context.object.animation_data.nla_tracks.new()
                    bpy.context.object.animation_data.nla_tracks[(len(bpy.context.object.animation_data.nla_tracks)-1)].name = action.name
                    bpy.context.object.animation_data.nla_tracks[(len(bpy.context.object.animation_data.nla_tracks)-1)].strips.new(action.name,0,action)
        except:
            pass
        
    def flipUVIndex(self):
        try:
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
        except:
            pass

    def addCustomNormalsToSelected(self):
        a = bpy.context.active_object
        for i in bpy.context.selected_objects:
            try:
                bpy.context.view_layer.objects.active = i
                bpy.ops.mesh.customdata_custom_splitnormals_add()
            except:
                pass
        bpy.context.view_layer.objects.active = a

    def duplicate(self, name, old_obj, col):
        new_obj = bpy.data.objects.new(name, old_obj.data.copy())
        col.objects.link(new_obj)
        # new_obj.matrix_world = old_obj.matrix_world
        new_obj.location = old_obj.location
        # print(f"{new_obj} at {new_obj.location} and {old_obj} at {old_obj.location}")
        for vertexGroup in old_obj.vertex_groups:
            new_obj.vertex_groups.new(name=vertexGroup.name)
        if old_obj.FBXExportOffset:
            new_obj.FBXExportOffset = old_obj.FBXExportOffset
        return new_obj

    def lod(self, objects_to_lod, lod_collection, export_collection):
        for lod_obj in objects_to_lod:
            remove_source_object = False
            for element in lod_obj.vertex_groups:
                new_objects_to_make = [i for i in lod_collection.objects if element.name in i.name]
                for o in new_objects_to_make:
                    remove_source_object = True
                    new_obj = Utils.duplicate(self, o.name, lod_obj, export_collection)
                    Utils.copy_modifier(self, bpy.data.objects[o.name], new_obj)
                    names_to_delete_uvs = ["Frames", "Details", "Shell"]  # TODO: make global
                    if element.name in names_to_delete_uvs:
                        for u in new_obj.data.uv_layers:
                            new_obj.data.uv_layers.remove(u)
            if remove_source_object:
                export_collection.objects.unlink(lod_obj)
