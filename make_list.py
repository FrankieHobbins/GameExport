import bpy
from . import merge_collection
from . import utils

merge_collection = merge_collection.MergeCollection
utils = utils.Utils


class MakeList(bpy.types.Operator):
    bl_label = "Make List"
    bl_idname = "gameexport.makelist"
    bl_description = "A demo operator"

    list_of_collections_in_root = []
    list_of_collections = []
    list_of_all_viewlayers = []
    list_of_collections_to_merge = []
    list_of_collections_to_reparent = []
    list_of_collections_to_unparent = []
    exclude_character = "*"
    merge_character = "&"

    def reset(self):
        # make sure clean at start
        MakeList.list_of_collections_in_root = []
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
        # self.merge()
        # self.clean_up()
        return {"FINISHED"}

    def make_list(self):
        # make collated list of all view layers and associated collection
        utils.list_all_layercollections_and_collections(
            self, MakeList.list_of_all_viewlayers,
            bpy.context.view_layer.layer_collection)

        # find collections that need to be merged and move to new list
        for col in list(MakeList.list_of_all_viewlayers):
            if MakeList.merge_character in col[1].name:
                MakeList.list_of_collections_to_merge.append(col[1])

        # make list of all collections in root
        for col in bpy.context.view_layer.layer_collection.children:
            MakeList.list_of_collections_in_root.append(col.collection)

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
