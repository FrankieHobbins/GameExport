import bpy
from . import merge_collection
from . import utils
from . import make_list


class GLBExport(bpy.types.Operator):
    bl_label = "Export GLB"
    bl_idname = "gameexport.glbexport"
    bl_description = "Export current collection as GLB"
    bl_options = {"REGISTER", "UNDO"}

    def export(self, path, export_col):
        if self.process_without_export:
            return
        # Select all objects in the export collection before exporting
        # This is needed because glTF exporter's use_visible filter can exclude objects
        # from temporary collections that aren't properly visible in the view layer
        bpy.ops.object.select_all(action='DESELECT')
        for obj in export_col.objects:
            obj.select_set(True)
        # Set the active object to ensure proper export context
        if export_col.objects:
            bpy.context.view_layer.objects.active = export_col.objects[0]
        bpy.ops.export_scene.gltf(filepath=path, **GLBExport.export_glb_settings_godot(self))

    def export_glb_settings_godot(self):
        return {
            "export_import_convert_lighting_mode": 'SPEC',
            "gltf_export_id": '',
            "export_use_gltfpack": False,
            "export_gltfpack_tc": True,
            "export_gltfpack_tq": 8,
            "export_gltfpack_si": 1.0,
            "export_gltfpack_sa": False,
            "export_gltfpack_slb": False,
            "export_gltfpack_vp": 14,
            "export_gltfpack_vt": 12,
            "export_gltfpack_vn": 8,
            "export_gltfpack_vc": 8,
            "export_gltfpack_vpi": 'Integer',
            "export_gltfpack_noq": True,
            "export_gltfpack_kn": False,
            "export_format": 'GLB',
            "ui_tab": 'GENERAL',
            "export_copyright": '',
            "export_image_format": 'AUTO',
            "export_image_add_webp": False,
            "export_image_webp_fallback": False,
            "export_texture_dir": '',
            "export_jpeg_quality": 75,
            "export_image_quality": 75,
            "export_keep_originals": False,
            "export_texcoords": True,
            "export_normals": True,
            "export_gn_mesh": True,
            "export_draco_mesh_compression_enable": False,
            "export_draco_mesh_compression_level": 6,
            "export_draco_position_quantization": 14,
            "export_draco_normal_quantization": 10,
            "export_draco_texcoord_quantization": 12,
            "export_draco_color_quantization": 10,
            "export_draco_generic_quantization": 12,
            "export_tangents": False,
            "export_materials": 'EXPORT',
            "export_unused_images": False,
            "export_unused_textures": False,
            "export_vertex_color": 'MATERIAL',
            "export_vertex_color_name": 'Color',
            "export_all_vertex_colors": True,
            "export_active_vertex_color_when_no_material": True,
            "export_attributes": False,
            "use_mesh_edges": False,
            "use_mesh_vertices": False,
            "export_cameras": False,
            "use_selection": True,
            "use_visible": False,
            "use_renderable": False,
            "use_active_collection_with_nested": True,
            "use_active_collection": True,
            "use_active_scene": False,
            "collection": '',
            "at_collection_center": False,
            "export_extras": False,
            "export_yup": True,
            "export_apply": True,
            "export_shared_accessors": False,
            "export_animations": True,
            "export_frame_range": False,
            "export_frame_step": 1,
            "export_force_sampling": True,
            "export_sampling_interpolation_fallback": 'LINEAR',
            "export_pointer_animation": False,
            "export_animation_mode": 'ACTIONS',
            "export_nla_strips_merged_animation_name": 'Animation',
            "export_def_bones": False,
            "export_hierarchy_flatten_bones": False,
            "export_hierarchy_flatten_objs": False,
            "export_armature_object_remove": False,
            "export_leaf_bone": False,
            "export_optimize_animation_size": True,
            "export_optimize_animation_keep_anim_armature": True,
            "export_optimize_animation_keep_anim_object": False,
            "export_optimize_disable_viewport": False,
            "export_negative_frame": 'SLIDE',
            "export_anim_slide_to_zero": False,
            "export_bake_animation": False,
            "export_merge_animation": 'ACTION',
            "export_anim_single_armature": True,
            "export_reset_pose_bones": True,
            "export_current_frame": False,
            "export_rest_position_armature": True,
            "export_anim_scene_split_object": True,
            "export_skins": True,
            "export_influence_nb": 4,
            "export_all_influences": False,
            "export_morph": True,
            "export_morph_normal": True,
            "export_morph_tangent": False,
            "export_morph_animation": True,
            "export_morph_reset_sk_data": True,
            "export_lights": False,
            "export_try_sparse_sk": True,
            "export_try_omit_sparse_sk": False,
            "export_gpu_instances": False,
            "export_action_filter": False,
            "export_convert_animation_pointer": False,
            "export_nla_strips": True,
            "export_original_specular": False,
            "will_save_settings": True,
            "export_hierarchy_full_collections": False,
            "export_extra_animations": False,
            "export_loglevel": -1
        }
    


class FBXExport(bpy.types.Operator):
    bl_label = "Export FBX"
    bl_idname = "gameexport.fbxexport"
    bl_description = "This is where export gets called from"
    bl_options = {"REGISTER", "UNDO"}

    def export(self, path, export_col):
        if self.process_without_export:
            return
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
                if i.type == 'MESH':
                    if i.data.users > 1:
                        print(f"could not fix unity rotation on {i} as it is a multi user mesh")
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
        if bpy.context.preferences.addons['GameExport'].preferences.special_source_workflow and bpy.context.scene.FbxExportPath == "":
            bake_anim_use_nla_strips = True
            bake_anim_use_all_actions = False
            utils.Utils.actionstoNLA(self, "_STA_")
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
