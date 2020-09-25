import bpy
from . import merge_collection
from . import utils
from . import make_list


class FBXExport(bpy.types.Operator):
    bl_label = "Export FBX"
    bl_idname = "gameexport.fbxexport"
    bl_description = "This is where export gets called from"
    bl_options = {"REGISTER", "UNDO"}

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
            for i in export_col.objects:
                if "COL_BOX" in i.name:
                    continue
                if set:
                    if i.type == 'MESH':
                        bpy.ops.object.select_all(action='DESELECT')
                        # bpy.context.view_layer.objects.active = i
                        i.select_set(True)
                        i.rotation_euler[0] -= 1.5708  # 90 deg in radians
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                        i.rotation_euler[0] += 1.5708  # 90 deg in radians
                elif not set:
                    if i.type == 'MESH':
                        bpy.ops.object.select_all(action='DESELECT')
                        # bpy.context.view_layer.objects.active = i
                        i.select_set(True)
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                        i.select_set(False)

    def export_fbx_settings_unity(self):
        object_types = {'OTHER', 'MESH', 'ARMATURE'}
        if bpy.context.scene.FBXKeepEmpties:
            object_types = {'OTHER', 'MESH', 'ARMATURE', 'EMPTY'}
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
