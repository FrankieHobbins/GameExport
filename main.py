import bpy
from . import merge_collection
from . import utils
from . import make_list

merge_collection = merge_collection.MergeCollection
ut = utils.Utils
makelist = make_list.MakeList


class Main(bpy.types.Operator):
    bl_label = "Main"
    bl_idname = "gameexport.export"
    bl_description = "This is where export gets called from"

    bake: bpy.props.BoolProperty(
        name="bake",
        default=False
    )

    selected: bpy.props.BoolProperty(
        name="selected",
        default=False
    )

    fbx_prefix: bpy.props.StringProperty(
        name="fbx_prefix",
        default=""
    )

    def execute(self, context):
        make_list.MakeList.reset(self)
        make_list.MakeList.make_list(self)
        print(self.selected)
        bpy.ops.object.mode_set(mode='OBJECT')
        # for baking
        if self.bake:
            print("exporting bake")
            path = ut.setpath(self, bpy.path.basename(bpy.context.blend_data.filepath.replace(".blend", "")))
            self.call_export("high")
            self.call_export("low")
        else:
            print("exporting standard")
            self.call_export("")
        # for special up workflow
        # TODO check this works properly on new installs
        """
        elif bpy.context.preferences.addons['GameExport'].preferences['special_source_workflow'] and bpy.context.scene.FbxExportPath == "":
            print("exporting standard - special source workflow")
            path = ut.setpathspecialcases(self, "", False)
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_entire_scene(self))
        # standard export
        """
        make_list.MakeList.clean_up(self)
        return {"FINISHED"}

    def call_export(self, bake):
        # cache state to revert later
        vlc, active_vlc, active_object, selected_objects = self.status_cache()
        # make a list of tuples I want to export
        export_list, objects_to_delete = self.make_export_list(vlc, bake)
        obj_and_pos_list = []
        # go though the export list and do the export
        for i in export_list:
            export_col = self.create_export_col(vlc)
            path = ut.setpath(self, i[0])
            self.prepare_objects_for_export(i[1], export_col, obj_and_pos_list)
            FBXExport.export(self, path, export_col)
            self.cleanup(i[1], export_col, obj_and_pos_list)
        # restore cached data
        self.cleanup_merged(objects_to_delete)
        self.status_reset(active_vlc, active_object, selected_objects)

    def make_export_list(self, vlc, bake):
        export_list = []
        objects_to_delete = []
        for col in make_list.MakeList.list_of_collections_in_root:
            # validate
            if not ut.is_valid(self, col, bake, [], False):
                continue
            # definitions
            children_collections = []
            export_objects = []
            # populate export collection with objects
            ut.get_all_children_collections(self, col, children_collections)
            children_collections.append(col)
            for child in children_collections:
                # validate children collectins
                if ut.is_valid(self, child, False, bpy.context.selected_objects, self.selected):
                    # if merge is needed do merge & put the new objects into the list
                    if ut.should_merge(self, child):
                        merged_object = merge_collection.merge_specified(self, child)
                        objects_to_delete.append(merged_object.name)
                        export_objects.append(merged_object.name)
                        merged_object.select_set(True)
                    # else put all objects into export list
                    else:
                        for object in child.objects:
                            export_objects.append(object.name)
            export_list.append([col.name, export_objects])
        # if export as individuals is set, want to break the list up so we dont use collections and each individual object has its own list entry
        if bpy.context.scene.FBXExportSM:
            individual_export_list = []
            for i in export_list:
                for ii in i[1]:
                    individual_export_list.append([ii, [ii]])
            export_list = individual_export_list
        # if export selected is used, remove all objects that arn't selected
        if self.selected:
            selected_export_list = []
            for i in export_list:
                for ii in i[1]:
                    if bpy.data.objects[ii] in bpy.context.selected_objects:
                        selected_export_list.append([ii, [ii]])
            export_list = selected_export_list
        return export_list, objects_to_delete

    def prepare_objects_for_export(self, list, export_col, obj_and_pos_list):
        # here we link objects from the list to the export collision
        for i in list:
            o = bpy.data.objects[i]
            export_col.objects.link(o)
            if bpy.context.scene.FBXExportCentreMeshes:
                o = bpy.data.objects[i]
                o_pos = o.location.copy()
                obj_and_pos_list.append([o, o_pos])
                o.location = (0, 0, 0)
            if bpy.context.scene.FBXFlipUVIndex:
                bpy.context.view_layer.objects.active = bpy.data.objects[i]
                ut.flipUVIndex(self)

    def cleanup(self, list, export_col, obj_and_pos_list):
        for ii in obj_and_pos_list:
            ii[0].location = ii[1]

        if bpy.context.scene.FBXFlipUVIndex:
            for i in list:
                bpy.context.view_layer.objects.active = bpy.data.objects[i]
                ut.flipUVIndex(self)

        if not bpy.context.scene.FBXLeaveExport:
            export_col.name = "Collection To Delete"
            bpy.data.collections.remove(export_col)

    def create_export_col(self, vlc):
        # make new collection to export to & link to scene
        export_col = bpy.data.collections.new("EXPORT")
        vlc.collection.children.link(export_col)
        # find view layer collection of export_col and set it active
        ecl_list = []
        ut.find_view_layer_collection(self, export_col, vlc, ecl_list)
        bpy.context.view_layer.active_layer_collection = ecl_list[0]
        return export_col

    def status_cache(self):
        vlc = bpy.context.view_layer.layer_collection
        active_vlc = bpy.context.view_layer.active_layer_collection
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        return vlc, active_vlc, active_object, selected_objects

    def cleanup_merged(self, objects_to_delete):
        if bpy.context.scene.FBXLeaveExport:
            return
        for ob in objects_to_delete:
            bpy.data.objects.remove(bpy.data.objects[ob])
            bpy.data.collections.remove(bpy.data.collections[ob + "__MERGED_"])
        for o in bpy.data.objects:
            if "_CONFLICT__" in o.name:
                o.name = o.name.replace("_CONFLICT__", "")

    def status_reset(self, active_vlc, active_object, selected_objects):
        return
        bpy.context.view_layer.active_layer_collection = active_vlc
        bpy.context.view_layer.objects.active = active_object
        for ob in selected_objects:
            ob.select_set(state=True)


class FBXExport(bpy.types.Operator):
    bl_label = "Export FBX"
    bl_idname = "gameexport.fbxexport"
    bl_description = "This is where export gets called from"

    def export(self, path, export_col):        
        if (bpy.context.scene.FbxExportEngine == 'default'):  # TODO make work good
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unity(self))
        elif (bpy.context.scene.FbxExportEngine == 'unity'):
            FBXExport.unity_export_rotation(export_col, set=True, do=bpy.context.scene.FBXFixUnityRotation)
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unity(self))
            FBXExport.unity_export_rotation(export_col, set=False, do=bpy.context.scene.FBXFixUnityRotation)
        elif (bpy.context.scene.FbxExportEngine == 'unreal'):
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unreal())

    def unity_export_rotation(export_col, set, do):
        if do:
            if set:
                for i in export_col.objects:
                    if i.type == 'MESH':
                        bpy.ops.object.select_all(action='DESELECT')
                        # bpy.context.view_layer.objects.active = i
                        i.select_set(True)
                        i.rotation_euler[0] -= 1.5708  # 90 deg in radians
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                        i.rotation_euler[0] += 1.5708  # 90 deg in radians
                        return
            elif not set:
                for i in export_col.objects:
                    if i.type == 'MESH':
                        bpy.ops.object.select_all(action='DESELECT')
                        # bpy.context.view_layer.objects.active = i
                        i.select_set(True)
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                        i.select_set(False)
                        return

    def export_fbx_settings_unity(self):
        object_types = {'OTHER', 'MESH', 'ARMATURE'}
        if self.bake:
            object_types = {'OTHER', 'MESH', 'ARMATURE', 'EMPTY'}
        return {
            "use_selection": False,
            "use_active_collection": True,
            "global_scale": bpy.context.scene.FbxExportScale,
            "apply_unit_scale": True,
            # "apply_scale_options": 'FBX_SCALE_NONE',
            "apply_scale_options": 'FBX_SCALE_ALL',
            "bake_space_transform": False,
            "object_types": object_types,
            "use_mesh_modifiers": True,
            "use_mesh_modifiers_render": True,
            "mesh_smooth_type": 'OFF',
            "use_subsurf": False,
            "use_mesh_edges": False,
            "use_tspace": False,
            "use_custom_props": False,
            "add_leaf_bones": False,
            "primary_bone_axis": 'Y',
            "secondary_bone_axis": 'X',
            "use_armature_deform_only": True,
            "armature_nodetype": 'NULL',
            "bake_anim": True,
            "bake_anim_use_all_bones": True,
            "bake_anim_use_nla_strips": False,
            "bake_anim_use_all_actions": True,
            "bake_anim_force_startend_keying": True,
            "bake_anim_step": 1.0,
            "bake_anim_simplify_factor": 1.0,
            "path_mode": 'AUTO',
            "embed_textures": False,
            "batch_mode": 'OFF',
            "use_batch_own_dir": True,
            "axis_forward": '-Z',
            "axis_up": 'Y',
        }

    def export_fbx_settings_unreal():
        return {
            "use_selection": False,
            "use_active_collection": True,
            "global_scale": bpy.context.scene.FbxExportScale,
            "apply_unit_scale": True,
            "apply_scale_options": 'FBX_SCALE_NONE',
            "bake_space_transform": False,
            "object_types": {'OTHER', 'MESH', 'ARMATURE', 'EMPTY'},
            "use_mesh_modifiers": True,
            "use_mesh_modifiers_render": True,
            "mesh_smooth_type": 'OFF',
            "use_subsurf": False,
            "use_mesh_edges": False,
            "use_tspace": False,
            "use_custom_props": False,
            "add_leaf_bones": False,
            "primary_bone_axis": 'Y',
            "secondary_bone_axis": 'X',
            "use_armature_deform_only": True,
            "armature_nodetype": 'NULL',
            "bake_anim": True,
            "bake_anim_use_all_bones": True,
            "bake_anim_use_nla_strips": False,
            "bake_anim_use_all_actions": True,
            "bake_anim_force_startend_keying": True,
            "bake_anim_step": 1.0,
            "bake_anim_simplify_factor": 1.0,
            "path_mode": 'AUTO',
            "embed_textures": False,
            "batch_mode": 'OFF',
            "use_batch_own_dir": True,
            "axis_forward": '-Z',
            "axis_up": 'Y',
        }

    def export_entire_scene(self, path):
        bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_entire_scene(self))

    def export_fbx_settings_entire_scene(self):
        bake_anim_use_nla_strips = False
        bake_anim_use_all_actions = True
        if bpy.context.preferences.addons['GameExport'].preferences['source_workflow'] and bpy.context.scene.FbxExportPath == "":
            bake_anim_use_nla_strips = True
            bake_anim_use_all_actions = False
            ut.actionstoNLA(self, "_STA_")
        return {
            "use_selection": False,
            "use_active_collection": False,
            "global_scale": bpy.context.scene.FbxExportScale,
            "apply_unit_scale": True,
            # "apply_scale_options": 'FBX_SCALE_NONE',
            "apply_scale_options": 'FBX_SCALE_ALL',
            "bake_space_transform": False,
            "object_types": {'OTHER', 'MESH', 'ARMATURE', 'EMPTY'},
            "use_mesh_modifiers": True,
            "use_mesh_modifiers_render": True,
            "mesh_smooth_type": 'OFF',
            "use_subsurf": False,
            "use_mesh_edges": False,
            "use_tspace": False,
            "use_custom_props": False,
            "add_leaf_bones": False,
            "primary_bone_axis": 'Y',
            "secondary_bone_axis": 'X',
            "use_armature_deform_only": True,
            "armature_nodetype": 'NULL',
            "bake_anim": True,
            "bake_anim_use_all_bones": True,
            "bake_anim_use_nla_strips": bake_anim_use_nla_strips,
            "bake_anim_use_all_actions": bake_anim_use_all_actions,
            "bake_anim_force_startend_keying": True,
            "bake_anim_step": 1.0,
            "bake_anim_simplify_factor": 1.0,
            "path_mode": 'AUTO',
            "embed_textures": False,
            "batch_mode": 'OFF',
            "use_batch_own_dir": True,
            "axis_forward": '-Z',
            "axis_up": 'Y',
        }
