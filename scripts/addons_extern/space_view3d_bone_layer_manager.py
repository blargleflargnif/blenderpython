# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
#
bl_info = {
    'name': 'Bone Layer Manager',
    'description': 'Display and Edit Bones Layer Name',
    'author': 'Alfonso Annarumma, Paolo Acampora',
    'version': (0, 6),
    'blender': (2, 6, 3),
    'location': 'View3D > Properties  > Bone Layers',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'}

import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty
import random


## Utility functions ##
def get_bones(arm, context, selected):
    """
    Get armature bones according to current context

        get_bones(bpy.data.armature, bpy.context, boolean)

    returns list

        [bpy_types.Bone]
    """
    if context.mode == 'EDIT_ARMATURE':
        if selected:
            bones = context.selected_bones
        else:
            bones = arm.edit_bones
    elif context.mode == 'OBJECT':
        if selected:
            bones = []
        else:
            bones = arm.bones
    else:
        if selected:
            pose_bones = context.selected_pose_bones
            bones = [arm.bones[b.name] for b in pose_bones]
        else:
            bones = arm.bones

    return bones


def check_used_layer(arm, layer_idx, context):
    """
    Check wether the given layer is used
    """
    bones = get_bones(arm, context, False)

    is_use = 0

    for bone in bones:
        if bone.layers[layer_idx]:
            is_use = 1
            break

    return is_use


def check_selected_layer(arm, layer_idx, context):
    """
    Check wether selected bones are in layer
    """
    bones = get_bones(arm, context, True)

    is_sel = 0

    for bone in bones:
        if bone.layers[layer_idx]:
            is_sel = 1
            break

    return is_sel


## Operators ##
class createNameId(bpy.types.Operator):
    """Assign and store a name for this layer as ID prop"""
    bl_idname = "bone_layer_man.layout_do_name"
    bl_label = "Assign Name"
    bl_description = "Assign and store a name for this layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_idx = IntProperty(name="Layer Index",
                            description="Index of the layer to be named",
                            default=0, min=0, max=31)

    layer_name = StringProperty(name="Layer Name",
                                description="Name of the layer",
                                default="")

    def execute(self, context):
        arm = bpy.context.active_object.data
        # Create ID prop by setting it
        arm["layer_name_%s" % self.layer_idx] = self.layer_name

        return {'FINISHED'}


class SelectBonesLayer(bpy.types.Operator):
    """\
    Select All Bones in given Layer,\
    Shift+Click to add to selection\
    """
    bl_idname = "bone_layer_man.selectboneslayer"
    bl_label = "Select bones in a layer"

    layer_idx = IntProperty(name="Layer Index",
                            description="Index of the layer to select",
                            default=0, min=0, max=31)

    def execute(self, context):
        ob = bpy.context.active_object
        arm = ob.data
        bones = get_bones(arm, context, False)

        layer_idx = self.layer_idx

        # Non additive selection
        if not self.shift:
            if context.mode == 'EDIT_ARMATURE':
                bpy.ops.armature.select_all(action='DESELECT')
            else:
                bpy.ops.pose.select_all(action='DESELECT')

        for bone in bones:
            if bone.layers[layer_idx]:
                bone.select = True

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift

        return self.execute(context)


class BoneLockSelected(bpy.types.Operator):
    """Loock All bones on this Layer"""
    bl_idname = "bone_layer_man.bonelockselected"
    bl_label = "Restric Selection of bones in a layer"

    layer_idx = IntProperty(name="Layer Index",
                            description="Index of the layer to lock",
                            default=0, min=0, max=31)

    lock = BoolProperty(name="Lock Status",
                        description="Wether to lock or not")

    def execute(self, context):
        ob = bpy.context.active_object
        arm = ob.data

        bones = get_bones(arm, context, False)

        for bone in bones:
            if bone.layers[self.layer_idx]:
                bone.select = False
                bone.hide_select = self.lock

                # set lock ID property
                arm["layer_lock_%s" % self.layer_idx] = self.lock

        return {'FINISHED'}


class BLMergeSelected(bpy.types.Operator):
    """\
    Move Selected Bones to this Layer, \
    Shift-Click to assign to multiple layers\
    """
    bl_idname = "bone_layer_man.blmergeselected"
    bl_label = "Merge Selected bones to this layer"

    layer_idx = IntProperty(name="Layer Index",
                            description="Index of the layer to assign",
                            default=0, min=0, max=31)

    def execute(self, context):
        arm = bpy.context.active_object.data

        bones = get_bones(arm, context, True)

        for bone in bones:
            if not self.shift:
                is_layers = [False] * (self.layer_idx)
                is_layers.append(True)
                is_layers.extend([False] * (len(bone.layers)
                                 - self.layer_idx - 1))

                bone.layers = is_layers
            else:
                bone.layers[self.layer_idx] ^= True

        return {'FINISHED'}

    def invoke(self, context, event):
        self.shift = event.shift

        return self.execute(context)


class BoneLayerGroup(bpy.types.Operator):
    '''Create a Bone Group for the bones in this layer'''
    bl_idname = "bone_layer_man.bonelayergroup"
    bl_label = "Hide Select of Selected"

    layer_idx = IntProperty(name="Layer Index",
                            description="Index of the layer to assign",
                            default=0, min=0, max=31)

    def execute(self, context):

        ac_ob = context.active_object
        arm = ac_ob.data
        layer_idx = self.layer_idx
        scene = context.scene
        pose = context.active_object.pose

        #create the empty group
        bpy.ops.pose.group_add()

        name_id_prop = "layer_name_%s" % layer_idx
        try:
            grp_name = ac_ob.data[name_id_prop]
        except KeyError:
            grp_name = "Layer %s" % (layer_idx + 1)

        groups = pose.bone_groups
        groups[-1].name = grp_name

        n = random.randrange(1, 20)
        # bone_group color_set is two padded
        Nstr = ("{0:0%sd}" % 2).format(n)

        groups[-1].color_set = 'THEME%s' % Nstr

        #cycle all bones in the layer
        for bone in pose.bones:
            if bone.bone.layers[layer_idx]:
                print(bone.name, "is in")
                bone.bone_group = groups[-1]
            else:
                print(bone.name, "is not")

        return {'FINISHED'}


## UI ##
def store_props():
    """
    Store properties in the scene for UI settings
    """
    scn_type = bpy.types.Scene

    scn_type.BLM_LayerVisibility = BoolProperty(name="Hide Empty",
                                                description="Do not show\
                                                             empty layers",
                                                default=False)

    scn_type.BLM_ExtraOptions = BoolProperty(name="Show Options",
                                             description="Show extra options",
                                             default=True)

    scn_type.BLM_LayerIndex = BoolProperty(name="Show Index",
                                           description="Show Layer Index",
                                           default=False)

    scn_type.BLM_ShowNamed = BoolProperty(name="Show Named",
                                          description="Show Named Layers Only",
                                          default=False)

    scn_type.BLM_GroupBy = IntProperty(name="Group By",
                                       description="How many layers per list",
                                       min=1,
                                       max=32,
                                       default=8)


class BoneLayerManagerPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Bone Layers"
    bl_idname = "bone_layer_man.BONE_LAYER_MANAGER_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    store_props()

    @classmethod
    def poll(self, context):
        if context.object and context.object.type == 'ARMATURE':
            return context.object.data

    def draw(self, context):
        ac_ob = context.active_object
        scn = context.scene

        layout = self.layout

        row = layout.row()
        row.prop(scn, "BLM_ExtraOptions", text="Show Options")
        row.prop(scn, "BLM_LayerVisibility", text="Hide Empty")

        row = layout.row()
        row.prop(scn, "BLM_LayerIndex", text="Show Index")
        row.prop(scn, "BLM_ShowNamed", text="Hide Nameless")

        row = layout.row()
        row.prop(scn, "BLM_GroupBy", text="Group by")

        col = layout.column(align=True)

        for i in range(len(ac_ob.data.layers)):
            # layer id property
            name_id_prop = "layer_name_%s" % i

            # conditionals needed for interface drawing
            # layer is used
            is_use = check_used_layer(ac_ob.data, i, context)
            # layer is named
            layer_name = None
            try:
                layer_name = ac_ob.data[name_id_prop]
            except KeyError:
                do_name_operator = "bone_layer_man.layout_do_name"

            # Add layer line
            if ((is_use or not scn.BLM_LayerVisibility) and
                    (layer_name or not scn.BLM_ShowNamed)):
                # Group every GroupBy layers
                if i % scn.BLM_GroupBy == 0:
                    col.separator()

                # Fill entries
                row = col.row()
                # visibility, show layer index as text if queried
                row.prop(ac_ob.data, "layers", index=i, emboss=True,
                         icon=('RESTRICT_VIEW_ON',
                               'RESTRICT_VIEW_OFF')[ac_ob.data.layers[i]],
                         toggle=True,
                         text=("", "%s" % (i + 1))[scn.BLM_LayerIndex])

                # protected layer
                row.prop(ac_ob.data, "layers_protected", index=i, emboss=True,
                         icon=('NONE', 'LINK')[ac_ob.data.layers_protected[i]],
                         toggle=True, text="")

                # name if any, else naming operator
                if layer_name is not None:
                    row.prop(ac_ob.data, '["%s"]' % name_id_prop, text="")
                else:
                    name_op = row.operator(do_name_operator)
                    name_op.layer_idx = i
                    name_op.layer_name = "Layer %s" % (i + 1)

                # Select, Lock and Merge are optional
                if scn.BLM_ExtraOptions and context.mode != 'OBJECT':
                    # bones select
                    sel_op = row.operator("bone_layer_man.selectboneslayer",
                                          icon='RESTRICT_SELECT_OFF',
                                          text="", emboss=True)
                    sel_op.layer_idx = i

                    # lock operator
                    #col = lock_col
                    lock_id_prop = "layer_lock_%s" % i
                    # assume layer was never locked if has no lock property
                    try:
                        lock = ac_ob.data[lock_id_prop]
                    except KeyError:
                        lock = False

                    lock_op = row.operator("bone_layer_man.bonelockselected",
                                           text="", emboss=True,
                                           icon=('UNLOCKED', 'LOCKED')[lock])

                    lock_op.layer_idx = i
                    lock_op.lock = not lock

                    #col = move_col
                    if is_use:
                        is_use += check_selected_layer(ac_ob.data, i, context)
                    merge_op = row.operator("bone_layer_man.blmergeselected",
                                            text="", emboss=True,
                                            icon=('RADIOBUT_OFF',
                                                  'LAYER_USED',
                                                  'LAYER_ACTIVE')[is_use])
                    merge_op.layer_idx = i

                # groups operator
                grp_op = row.operator("bone_layer_man.bonelayergroup",
                                      text="",
                                      emboss=True, icon='GROUP_BONE')
                grp_op.layer_idx = i


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register
