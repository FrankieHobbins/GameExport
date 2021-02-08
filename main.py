import bpy
from . import merge_collection
from . import utils
from . import make_list
from . import export

merge_collection = merge_collection.MergeCollection
ut = utils.Utils
makelist = make_list.MakeList


class Main(bpy.types.Operator):
    bl_label = "Main"
    bl_idname = "gameexport.export"
    bl_description = "This is where export gets called from"
    bl_options = {"REGISTER", "UNDO"}

    bake: bpy.props.BoolProperty(
        name="bake",
        default=False
    )

    selected: bpy.props.BoolProperty(
        name="selected",
        default=False
    )

    process_without_export: bpy.props.BoolProperty(
        name="process_without_export",
        default=False
    )

    fbx_prefix: bpy.props.StringProperty(
        name="fbx_prefix",
        default=""
    )

    def execute(self, context):
        # make lists
        make_list.MakeList.reset(self)
        make_list.MakeList.make_list(self)
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except:
            if self.selected:
                print("nothing selected so not exporting anything")
                return {"FINISHED"}
            
        # for baking
        if self.bake:
            print("exporting bake")
            path = ut.setpath(self, bpy.path.basename(bpy.context.blend_data.filepath.replace(".blend", "")))
            self.call_export("high")
            self.call_export("low")
        # for special UP workflow
        elif bpy.context.preferences.addons['GameExport'].preferences.special_source_workflow and bpy.context.scene.FbxExportPath == "":
            print("exporting standard - special source workflow")
            path = ut.setpathspecialcases(self, "", False)
            bpy.ops.export_scene.fbx(filepath=path, **export.FBXExport.export_fbx_settings_entire_scene(self))
        # standard export
        else:
            print("exporting standard")
            self.call_export("")
        # clean up
        make_list.MakeList.clean_up(self)
        return {"FINISHED"}

    def call_export(self, bake):
        # cache state to revert later
        vlc, active_vlc, active_object, selected_objects = self.status_cache()
        # deselect everything
        for o in bpy.context.selected_objects:
            o.select_set(False)
        # make a list of everything I want to export, keep a list of things I want to delete later, merging gets done in here
        export_list, objects_to_delete = make_list.MakeList.make_export_list(self, vlc, bake)
        obj_and_pos_list = []
        obj_and_instance_type = []
        # go though the export list and do the export
        for i in export_list:
            export_col = self.create_export_col(vlc)
            path = ut.setpath(self, i[0])
            self.prepare_objects_for_export(i[0], i[1], export_col, obj_and_pos_list, obj_and_instance_type)
            export.FBXExport.export(self, path, export_col)
            self.cleanup(i[1], export_col, obj_and_pos_list, obj_and_instance_type)
        # restore cached data
        self.cleanup_merged(objects_to_delete)
        self.status_reset(active_vlc, active_object, selected_objects)

    def prepare_objects_for_export(self, old_col, obj_list, export_col, obj_and_pos_list, obj_and_instance_type):
        try:
            export_col.FBXExportOffset = bpy.data.collections[old_col].FBXExportOffset
        except:
            export_col.FBXExportOffset = (0, 0, 0)
        # here we link objects from the list to the export collision
        for i in obj_list:
            o = bpy.data.objects[i]
            if "origin" in i.lower() and o.type == "EMPTY":  # dont export origin object
                continue
            export_col.objects.link(o)
            if bpy.context.scene.FBXExportCentreMeshes and not o.parent:
                o = bpy.data.objects[i]
                o_pos = o.location.copy()
                obj_and_pos_list.append([o, o_pos])
                if export_col.FBXExportOffset and o.type == "EMPTY" or "COL_BOX" in i or "COL_MESH" in i or "OUTLINE" in i or "!" in i:
                    o.location = (o.location[0] - export_col.FBXExportOffset[0],
                                  o.location[1] - export_col.FBXExportOffset[1],
                                  o.location[2] - export_col.FBXExportOffset[2])
                else:
                    o.location = (0, 0, 0)
            if bpy.context.scene.FBXFlipUVIndex:
                bpy.context.view_layer.objects.active = bpy.data.objects[i]
                ut.flipUVIndex(self)
            if o.instance_type != "NONE" and bpy.context.scene.FBXCullInstanceCollections:
                obj_and_instance_type.append([o, o.instance_type])
                o.instance_type = "NONE"
        lod_collection = [i for i in bpy.data.collections if "LODS" in i.name]
        if len(lod_collection) and not bpy.context.scene.FBXDontLod:
            objects = [i for i in export_col.objects if i.type == "MESH"]
            utils.Utils.lod(self, objects, lod_collection[0], export_col)

    def cleanup(self, obj_list, export_col, obj_and_pos_list, obj_and_instance_type):
        if bpy.context.scene.FBXLeaveExport:
            return
        for ii in obj_and_pos_list:
            ii[0].location = ii[1]
        if bpy.context.scene.FBXFlipUVIndex:
            for i in obj_list:
                bpy.context.view_layer.objects.active = bpy.data.objects[i]
                ut.flipUVIndex(self)
        if bpy.context.scene.FBXLeaveExport or self.process_without_export:
            return
        for o in obj_and_instance_type:
            o[0].instance_type = o[1]
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
            if not self.process_without_export:
                bpy.data.objects.remove(bpy.data.objects[ob])
        for o in bpy.data.objects:
            if "_CONFLICT__" in o.name:
                o.name = o.name.replace("_CONFLICT__", "")
        for c in bpy.data.collections:
            if "_MERGED_" in c.name:
                bpy.data.collections.remove(c)

    def status_reset(self, active_vlc, active_object, selected_objects):
        if bpy.context.scene.FBXLeaveExport:
            return
        bpy.context.view_layer.active_layer_collection = active_vlc
        bpy.context.view_layer.objects.active = active_object
        for ob in selected_objects:
            ob.select_set(state=True)
