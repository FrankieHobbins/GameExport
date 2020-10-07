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

    fbx_prefix: bpy.props.StringProperty(
        name="fbx_prefix",
        default=""
    )

    def execute(self, context):
        make_list.MakeList.reset(self)
        make_list.MakeList.make_list(self)
        bpy.ops.object.mode_set(mode='OBJECT')
        # for baking
        if self.bake:
            print("exporting bake")
            path = ut.setpath(self, bpy.path.basename(bpy.context.blend_data.filepath.replace(".blend", "")))
            self.call_export("high")
            self.call_export("low")
        # for special up workflow
        # TODO check this works properly on new installs
        elif bpy.context.preferences.addons['GameExport'].preferences.special_source_workflow and bpy.context.scene.FbxExportPath == "":
            print("exporting standard - special source workflow")
            path = ut.setpathspecialcases(self, "", False)
            bpy.ops.export_scene.fbx(filepath=path, **export.FBXExport.export_fbx_settings_entire_scene(self))
        else:
            print("exporting standard")
            self.call_export("")
        # standard export
        
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
        # go though the export list and do the export
        for i in export_list:
            export_col = self.create_export_col(vlc)
            path = ut.setpath(self, i[0])
            self.prepare_objects_for_export(i[1], export_col, obj_and_pos_list)
            export.FBXExport.export(self, path, export_col)
            self.cleanup(i[1], export_col, obj_and_pos_list)
        # restore cached data
        self.cleanup_merged(objects_to_delete)
        self.status_reset(active_vlc, active_object, selected_objects)

    def prepare_objects_for_export(self, list, export_col, obj_and_pos_list):
        origin_object = False
        for object in list:
            if "origin" in object.lower():
                origin_object = bpy.data.objects[object]
        if origin_object:
            for object in list:
                if bpy.data.objects[object].type == "EMPTY" or "COL_BOX" in object or "OUTLINE" in object:
                    if "origin" not in object.lower():
                        if not bpy.data.objects[object].parent:
                            o = bpy.data.objects[object]
                            o.FBXExportOffset = (o.location[0] - origin_object.location[0],
                                                 o.location[1] - origin_object.location[1],
                                                 o.location[2] - origin_object.location[2])
        # here we link objects from the list to the export collision
        for i in list:
            o = bpy.data.objects[i]
            if o == origin_object and o.type == "EMPTY":  # dont export origin object
                continue
            export_col.objects.link(o)
            if bpy.context.scene.FBXExportCentreMeshes and not o.parent:
                o = bpy.data.objects[i]
                o_pos = o.location.copy()
                obj_and_pos_list.append([o, o_pos])
                o.location = (0, 0, 0)
                if o.FBXExportOffset:
                    o.location = o.FBXExportOffset
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
        for o in bpy.data.objects:
            if "_CONFLICT__" in o.name:
                o.name = o.name.replace("_CONFLICT__", "")
        for c in bpy.data.collections:
            if "_MERGED_" in c.name:
                bpy.data.collections.remove(c)

    def status_reset(self, active_vlc, active_object, selected_objects):
        bpy.context.view_layer.active_layer_collection = active_vlc
        bpy.context.view_layer.objects.active = active_object
        for ob in selected_objects:
            ob.select_set(state=True)
