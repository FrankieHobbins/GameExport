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

    def execute(self, context):
        if bpy.context.preferences.addons['GameExport'].preferences['source_workflow'] and bpy.context.scene.FbxExportPath == "":
            path = ut.setpathspecialcases(self, "")
            FBXExport.export_entire_scene(self, path)

        else:
            make_list.MakeList.reset(self)
            make_list.MakeList.make_list(self)        
            self.call_export()
            make_list.MakeList.clean_up(self)
        return {"FINISHED"}

    def call_export(self):
        vlc = bpy.context.view_layer.layer_collection
        # for each collection in root of scene
        for col in make_list.MakeList.list_of_collections_in_root:
            objects_to_delete = []
            if not ut.is_valid(self, col):
                continue
            # make new collection to export to & link to scene
            export_col = bpy.data.collections.new("EXPORT")
            vlc.collection.children.link(export_col)
            # find view layer collection of export_col and set it active
            ecl_list = []
            ut.find_view_layer_collection(self, export_col, vlc, ecl_list)
            bpy.context.view_layer.active_layer_collection = ecl_list[0]
            # populate export collection with objects
            children = []
            ut.get_all_children_collections(self, col, children)
            children.append(col)
            for child in children:
                if ut.is_valid(self, child):
                    if ut.should_merge(self, child):
                        ut.do_merge(self, child, export_col)
                        objects_to_delete.append(bpy.context.active_object)
                    else:
                        for object in child.objects:
                            export_col.objects.link(object)
            # set path and do export
            path = ut.setpath(self, col.name)
            FBXExport.export(self, path)
            # cleanup
            for ob in objects_to_delete:
                bpy.data.objects.remove(ob)
            bpy.data.collections.remove(export_col)


class FBXExport(bpy.types.Operator):
    bl_label = "Export FBX"
    bl_idname = "gameexport.fbxexport"
    bl_description = "This is where export gets called from"

    def export(self, path):
        if (bpy.context.scene.FbxExportEngine == 'default'): # TODO make work good
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unity())

        elif (bpy.context.scene.FbxExportEngine == 'unity'):
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unity())

        elif (bpy.context.scene.FbxExportEngine == 'unreal'):
            bpy.ops.export_scene.fbx(filepath=path, **FBXExport.export_fbx_settings_unreal())

    def export_fbx_settings_unity():
        return {
            "use_selection": False,
            "use_active_collection": True,
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
        bpy.ops.export_scene.fbx(
            filepath=path,
            **FBXExport.export_fbx_settings_entire_scene()
            )

    def export_fbx_settings_entire_scene():
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
