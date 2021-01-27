import bpy
from . import merge_collection
from . import utils

merge_collection = merge_collection.MergeCollection
utils = utils.Utils


class MakeList(bpy.types.Operator):
    bl_label = "Make List"
    bl_idname = "gameexport.makelist"
    bl_description = "A demo operator"
    bl_options = {"UNDO"}

    list_of_collections_to_export = []
    list_of_collections = []
    list_of_all_viewlayers = []
    list_of_collections_to_merge = []
    list_of_collections_to_reparent = []
    list_of_collections_to_unparent = []
    exclude_character = "*"
    merge_character = "&"

    def reset(self):
        # make sure clean at start
        MakeList.list_of_collections_to_export = []
        MakeList.list_of_collections = []
        MakeList.list_of_all_viewlayers = []
        MakeList.list_of_collections_to_merge = []
        MakeList.list_of_collections_to_reparent = []
        MakeList.list_of_collections_to_unparent = []
        MakeList.exclude_character = "*"
        MakeList.merge_character = "&"

    def execute(self, context):
        self.reset()
        self.make_list()
        return {"FINISHED"}

    def make_list(self):
        # make collated list of all view layers and associated collection
        utils.list_all_layercollections_and_collections(self, MakeList.list_of_all_viewlayers, bpy.context.view_layer.layer_collection)
        # find collections that need to be merged and move to new list
        for col in list(MakeList.list_of_all_viewlayers):
            if MakeList.merge_character in col[1].name:
                MakeList.list_of_collections_to_merge.append(col[1])  # TODO: is this actually used?
        # make list of all collections in root
        for col in bpy.context.view_layer.layer_collection.children:
            MakeList.list_of_collections_to_export.append(col.collection)
        # if selected button is pressed make a list of selected object collections isntead
        if self.selected:
            # create set of collections with selected objects (set is like a list but can only contain each entry once
            new_list = {c for i in bpy.context.selected_objects for c in bpy.data.collections for o in c.objects if i == o}
            # create set of children collections inside selected objects TODO: make recusive
            new_list_1 = {j for i in new_list for j in i.children}
            # clean out selected children from main first list to avoid getting exported twice
            new_list_2 = {i for i in new_list if i not in new_list_1}
            # find parent collections
            new_list_3 = {utils.find_parent_recursive(self, i) for i in new_list_2}
            MakeList.list_of_collections_to_export = new_list_3

    def make_export_list(self, vlc, bake):
        export_list = []  # collection name and objects inside it
        objects_to_delete = []
        objects_to_not_delete = []
        for col in MakeList.list_of_collections_to_export:
            # validate
            if not utils.is_valid(self, col, bake):
                continue
            # definitions
            children_collections = []
            export_objects = []            
            # populate export collection with objects
            utils.get_all_children_collections(self, col, children_collections)
            children_collections.append(col)
            for child in children_collections:
                # validate children collectins
                if utils.is_valid(self, child, False):
                    # dont delete existing empties
                    for o in child.objects:
                        if o.type == "EMPTY":
                            objects_to_not_delete.append(o.name)
                    # if merge is needed do merge & put the new objects into the list
                    if utils.should_merge(self, child):
                        merged_objects = merge_collection.merge_specified(self, child)
                        for o in merged_objects:
                            objects_to_delete.append(o.name)
                            export_objects.append(o.name)
                            o.select_set(True)
                    # else put all objects into export list
                    else:
                        for object in child.objects:
                            export_objects.append(object.name)
            # dont export offset
            export_objects = [i for i in export_objects if "offset" not in i.lower()]
            export_list.append([col.name, export_objects])
        # if export as individuals is set, want to break the list up so we dont use collections and each individual object has its own list entry
        if bpy.context.scene.FBXExportSM:
            individual_export_list = []
            for i in export_list:
                for ii in i[1]:
                    individual_export_list.append([ii, [ii]])
            export_list = individual_export_list
        # dont delete empties that already existed
        for i in objects_to_not_delete:
            if i in objects_to_delete:
                objects_to_delete.remove(i)
        return export_list, objects_to_delete

    def merge_from_list(self):
        # duplicate collections in merge list and relink ready for export
        for col in MakeList.list_of_collections_to_merge:
            name = col.name.replace(MakeList.merge_character, "")
            self.merge(col, name)

    def merge(self, col, name):
        # copy and rename
        col_copy = utils.duplicate_collection(self, col)
        col_copy.name = name

        # replace col with copy in its parent
        # and make a list to reverse it later
        parent = utils.find_parent(self, col)
        if parent.children:
            parent.children.link(col_copy)
            parent.children.unlink(col)
            MakeList.list_of_collections_to_reparent.append([parent, col])
            MakeList.list_of_collections_to_unparent.append(
                [parent, col_copy])

        # parent all col children to col_copy
        # and make a list to reverse it later
        for child in list(col.children):
            MakeList.list_of_collections_to_reparent.append([col, child])
            MakeList.list_of_collections_to_unparent.append(
                [col_copy, child])
            col_copy.children.link(child)
            col.children.unlink(child)

        # merge all objects into one
        merge_collection.merge(self, col_copy)

    def clean_up(self):
        # put it after export
        for col in MakeList.list_of_collections_to_reparent:
            col[0].children.link(col[1])
        for col in MakeList.list_of_collections_to_unparent:
            col[0].children.unlink(col[1])
