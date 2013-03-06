# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {'name': 'Item Panel & Batch Naming',
           'author': 'proxe',
           'version': (0, 7, 0),
           'blender': (2, 66, 0),
           'location': '3D View > Properties Panel',
           'warning': 'Work in Progress',
           #'wiki_url': '',
           #'tracker_url': '',
           'description': "An improved item panel for the 3D View with include"
                          "d batch naming tools.",
           'category': '3D View'}

import bpy

# ##### BEGIN INFO BLOCK #####
#
#    Author: Trentin Frederick (a.k.a, proxe)
#    Contact: trentin.frederick@gmail.com, proxe.err0r@gmail.com
#    Version: 0.7.2
#
# ##### END INFO BLOCK #####

# ##### BEGIN VERSION BLOCK #####
#
#    0.7
#    - Updated Object_type, constraint_type and modifier_type enumProperty
#    formats to 2.66
#    - Restored ability to populate panel for the active objects/bones
#    constraints, modifiers, bone constraints.
#    - Create target menu allowing user to rename specific types of objects,
#    constraints, modifiers, object data and bone constraints.
#    0.6
#    - Removed ability to populate the item panel with all selected objects,
#    objects constraints, modifiers, object's data, bones and bone constraints.
#    - Removed visibility and select-ability options from the left and right of
#    active bone name input field in favor of the default item panel's format.
#    - Code cleanup
#    0.5
#    - Optimized code, followed many PEP8 guidelines.
#    - Altered batch naming functions and operators to account for all selected
#    object's constraints's and modifiers, and to account for all selected bone
#    constraints.
#    0.4
#    - Created batch naming functions and operator, added ui prop to access
#    this located next to active object input field.
#    - Added visibility and select-ability options for active bone, located to
#    the left and right of the name input field for active bone.
#    0.3
#    - Added item panel property group, used to control visibility options of
#    selected objects/bones, by allowing them to populate the panel when
#    selected.
#    - Made the item panel display all selected objects, object constraints,
#    modifiers, object data, bones and bone constraints
#    - Added visibility controls for displayed constraints and modifiers
#    0.2
#    - Replaced the item panel's input field for object and active object with
#    the template_ID used in properties window for both items.
#    - Added a blank Icon for active_bone, for visual separation.
#    0.1
#    - Created the item panel add-on.
#    - Added object data naming field to item panel.
#
#    Todo: 
#    0.8
#    - Add ability to populate the panel with active objects materials, and
#    their textures if applicable.
#    - Add ability to populate the panel with the active objects particle
#    systems.
#    - Account for batch naming materials, textures and particle systems in
#    the batch naming functions
#    - Include the materials, textures and particle systems in the batch
#    naming operator.
#    0.9
#    - See if there is something I can do to make the menus for types a bit
#    more easily readable, i.e. recreate the same menu that operator_menu_enum
#    of object.add_modifier would create.
#    - If everything is working well, remove some of the props default values
#    so that the value is stored for the next time it is called.
#    - Unregister blenders default item panel when this add-on is active
#    1.0
#    - Add ability to display vertex groups and shape-keys in item panel,
#    vertex groups should have a quick select and deselect option, shape-keys
#    ideally would have the slider available but just where it should be placed
#    is unclear.
#    - Create batch naming functionality for vertex groups & shape-keys,
#    ideally this would be accessed from within a menu rather then as part of
#    the 'target row', may as well include options for UV maps and vertex
#    colors.
#    - add a global rename option, renaming all objects, this may or may not be
#    ideal, the menu is going to get much longer, as it would have a menu for
#    which scenes would be effected if not all, and would use a bpy.data
#    structure, which will lengthen the code and brings up the question as to
#    whether or not I should use that structure throughout the add-on, rather
#    then its current form, arguably this would be the better option in the
#    end.
#    - Commit add-on
#
# ##### END VERSION BLOCK #####

  # PEP8 Compliant

###############
## FUNCTIONS ##
###############
  # Imports
import re


  # Rename
def rename(self, data_path, batch_name, find, replace, prefix, suffix,
           trim_start, trim_end):
    """
    Renames single proper data_path variable received from batch_rename, check
    variable values from operator class.
    """
    if not batch_name:  # Not using name field in GUI.
        target = data_path.name[trim_start:]  # Trim start is always performed.
    else:  # Name field in GUI if in use.
        target = batch_name
        target = target[trim_start:]
    if trim_end > 0:  # Skip trim end if its not in use, i.e. 0.
        target = target[:-trim_end]
    target = re.sub(find, replace, target)  # TODO: Tool-shelf RE error.
                                            # RE will send an error if using
                                            # tool-shelf in the find field
                                            # while typing out the expression.
    target = prefix + target + suffix  # Final target value.
    if data_path in {'constraint', 'modifier'}:
        data_path.name = target
    else:
        data_path.name = target[:]


  # Batch Rename
def batch_rename(self, context, batch_name, find, replace, prefix, suffix,
                 trim_start, trim_end, batch_objects, batch_object_constraints,
                 batch_modifiers, batch_objects_data, batch_bones,
                 batch_bone_constraints, object_type, constraint_type,
                 modifier_type):
    """
    Send data_path values to rename, check variable values from operator class.
    """
  # Objects
    if batch_objects:
        for object in context.selected_objects:
            if object_type in 'ALL':
                data_path = object
            else:
                if object_type in object.type:
                    data_path = object
                else:
                    pass
            try:
                rename(self, data_path, batch_name, find, replace, prefix,
                       suffix, trim_start, trim_end)
            except:
                pass
    else:
        pass  # Unnecessary, python does this automatically, used here for
              # clarification purposes, as a personal preference. If it turns
              # out that this is a cost in performance I will remove,
              # otherwise, it stays.
  # Object Constraints
    if batch_object_constraints:
        for object in context.selected_objects:
            for constraint in object.constraints[:]:
                if constraint_type in 'ALL':
                    data_path = constraint
                else:
                    if constraint_type in constraint.type:
                        data_path = constraint
                    else:
                        pass
                try:
                    rename(self, data_path, batch_name, find, replace, prefix,
                           suffix, trim_start, trim_end)
                except:
                    pass
    else:
        pass
  # Object Modifiers
    if batch_modifiers:
        for object in context.selected_objects:
            for modifier in object.modifiers[:]:
                if modifier_type in 'ALL':
                    data_path = modifier
                else:
                    if modifier_type in modifier.type:
                        data_path = modifier
                    else:
                        pass
                try:
                    rename(self, data_path, batch_name, find, replace, prefix,
                           suffix, trim_start, trim_end)
                except:
                    pass
    else:
        pass
  # Objects Data
    if batch_objects_data:
        for object in context.selected_objects:
            if object_type in 'ALL':
                data_path = object.data
            else:
                if object_type in object.type:
                    data_path = object.data
                else:
                    pass
            try:
                rename(self, data_path, batch_name, find, replace, prefix,
                       suffix, trim_start, trim_end)
            except:
                pass
    else:
        pass
  # Bones
    if batch_bones:
        if context.selected_editable_bones:
            selected_bones = context.selected_editable_bones
        else:
            selected_bones = context.selected_pose_bones
        for bone in selected_bones:
            data_path = bone
            try:
                rename(self, data_path, batch_name, find, replace, prefix,
                       suffix, trim_start, trim_end)
            except:
                pass
    else:
        pass
  # Bone Constraints
    if batch_bone_constraints:
        for bone in context.selected_pose_bones:
            for constraint in bone.constraints[:]:
                if constraint_type in 'ALL':
                    data_path = constraint
                else:
                    if constraint_type in contraint.type:
                        data_path = constraint
                    else:
                        pass
                try:
                    rename(self, data_path, batch_name, find, replace, prefix,
                           suffix, trim_start, trim_end)
                except:
                    pass
    else:
        pass

###############
## OPERATORS ##
###############
  # Imports
from bpy.props import *
from bpy.types import Operator


  # View 3D Batch Naming (OT)
class VIEW3D_OT_batch_naming(Operator):
    """Invoke the batch naming operator."""
    bl_idname = 'view3d.batch_naming'
    bl_label = 'Batch Naming'
    bl_options = {'REGISTER', 'UNDO'}

    batch_name = StringProperty(name='Name', description="Designate a new name"
                                ", if blank, the current names are effected by"
                                " any changes to the parameters below.")

    find = StringProperty(name='Find', description="Find this text and remove "
                          "it from the names.")

    replace = StringProperty(name='Replace', description="Replace found text w"
                             "ithin the names with the text entered here.")

    prefix = StringProperty(name='Prefix', description="Designate a prefix to "
                            "use for the names.")

    suffix = StringProperty(name='Suffix', description="Designate a suffix to "
                            "use for the names")

    trim_start = IntProperty(name='Trim Start', description="Trim the beginnin"
                             "g of the names by this amount.", min=0, max=50,
                             default=0)

    trim_end = IntProperty(name='Trim End', description="Trim the ending of th"
                           "e names by this amount.", min=0, max=50, default=0)

    batch_objects = BoolProperty(name='Objects', description="Apply batch nami"
                                 "ng to the selected objects.", default=False)

    batch_object_constraints = BoolProperty(name='Object Constraints',
                                            description="Apply batch naming to"
                                            " the constraints of the selected "
                                            "objects.", default=False)

    batch_modifiers = BoolProperty(name='Modifiers', description="Apply batch "
                                   "naming to the modifiers of the selected ob"
                                   "jects.", default=False)

    batch_objects_data = BoolProperty(name='Object Data', description="Apply b"
                                      "atch naming to the object data of the s"
                                      "elected objects.", default=False)

    batch_bones = BoolProperty(name='Bones', description="Apply batch naming t"
                               "o the selected bones.", default=False)

    batch_bone_constraints = BoolProperty(name='Bone Constraints',
                                          description="Apply batch naming to t"
                                          "he constraints of the selected bone"
                                          "s.", default=False)

    object_type = EnumProperty(name='Type', description="The type of object th"
                               "at the batch naming operations will be perform"
                               "ed on.",
                               items=[('LAMP',
                                       'Lamp',
                                       "",
                                       '', 11),
                                      ('CAMERA',
                                        'Camera',
                                        "",
                                       '', 10),
                                      ('SPEAKER',
                                        'Speaker',
                                        "",
                                       '', 9),
                                      ('EMPTY',
                                        'Empty',
                                        "",
                                       '', 8),
                                      ('LATTICE',
                                        'Lattice',
                                        "",
                                       '', 7),
                                      ('ARMATURE',
                                        'Armature',
                                        "",
                                       '', 6),
                                      ('FONT',
                                        'Font',
                                        "",
                                       '', 5),
                                      ('META',
                                        'Meta',
                                        "",
                                       '', 4),
                                      ('SURFACE',
                                        'Surface',
                                        "",
                                       '', 3),
                                      ('CURVE',
                                        'Curve',
                                        "",
                                       '', 2),
                                      ('MESH',
                                        'Mesh',
                                        "",
                                       '', 1),
                                      ('ALL',
                                        'All Objects',
                                        "",
                                       '', 0)], default='ALL')

    constraint_type = EnumProperty(name='Type', description="The type of const"
                                   "raint that the batch naming operations wil"
                                   "l be performed on.",
                                   items=[('SHRINKWRAP',
                                            'Shrinkwrap',
                                            "",
                                           '', 28),
                                          ('SCRIPT',
                                            'Script',
                                            "",
                                           '', 27),
                                          ('RIGID_BODY_JOINT',
                                            'Rigid Body Joint',
                                            "",
                                           '', 26),
                                          ('PIVOT',
                                            'Pivot',
                                            "",
                                           '', 25),
                                          ('FOLLOW_PATH',
                                            'Follow Path',
                                            "",
                                           '', 24),
                                          ('FLOOR',
                                            'Floor',
                                            "",
                                           '', 23),
                                          ('CHILD_OF',
                                            'ChildOf',
                                            "",
                                           '', 22),
                                          ('ACTION',
                                            'Action',
                                            "",
                                           '', 21),
                                          ('TRACK_TO',
                                            'TrackTo',
                                            "",
                                           '', 20),
                                          ('STRETCH_TO',
                                            'Stretch To',
                                            "",
                                           '', 19),
                                          ('SPLINE_IK',
                                            'Spline IK',
                                            "",
                                           '', 18),
                                          ('LOCKED_TRACK',
                                            'Locked Track',
                                            "",
                                           '', 17),
                                          ('IK',
                                            'IK',
                                            "",
                                           '', 16),
                                          ('DAMPED_TRACK',
                                            'Damped Track',
                                            "",
                                           '', 15),
                                          ('CLAMP_TO',
                                            'Clamp To',
                                            "",
                                           '', 14),
                                          ('TRANSFORM',
                                            'Transformation',
                                            "",
                                           '', 13),
                                          ('MAINTAIN_VOLUME',
                                            'Maintain Volume',
                                            "",
                                           '', 12),
                                          ('LIMIT_SCALE',
                                            'Limit Scale',
                                            "",
                                           '', 11),
                                          ('LIMIT_ROTATION',
                                            'Limit Rotation',
                                            "",
                                           '', 10),
                                          ('LIMIT_LOCATION',
                                            'Limit Location',
                                            "",
                                           '', 9),
                                          ('LIMIT_DISTANCE',
                                            'Limit Distance',
                                            "",
                                           '', 8),
                                          ('COPY_TRANSFORMS',
                                            'Copy Transforms',
                                            "",
                                           '', 7),
                                          ('COPY_SCALE',
                                            'Copy Scale',
                                            "",
                                           '', 6),
                                          ('COPY_ROTATION',
                                            'Copy Rotation',
                                            "", 
                                           '', 5),
                                          ('COPY_LOCATION',
                                            'Copy Location',
                                            "",
                                           '', 4),
                                          ('FOLLOW_TRACK',
                                            'Follow Track',
                                            "",
                                           '', 3),
                                          ('OBJECT_SOLVER',
                                            'Object Solver',
                                            "",
                                           '', 2),
                                          ('CAMERA_SOLVER',
                                            'Camera Solver',
                                            "",
                                           '', 1),
                                          ('ALL',
                                            'All Constraints',
                                            "",
                                           '', 0)], default='ALL')

    modifier_type = EnumProperty(name='Type', description="The type of modifie"
                                 "r that the batch naming operations will be p"
                                 "erformed on.",
                                 items=[('SOFT_BODY', 
                                          'Soft Body', 
                                          "", 
                                         '', 43),
                                        ('SMOKE',
                                          'Smoke',
                                          "",
                                         '', 42),
                                        ('PARTICLE_SYSTEM', 
                                          'Particle System', 
                                          "", 
                                         '', 41),
                                        ('PARTICLE_INSTANCE', 
                                          'Particle Instance', 
                                          "", 
                                         '', 40),
                                        ('OCEAN', 
                                          'Ocean', 
                                          "", 
                                         '', 39),
                                        ('FLUID_SIMULATION', 
                                          'Fluid Simulation', 
                                          "", 
                                         '', 38),
                                        ('EXPLODE', 
                                          'Explode', 
                                          "", 
                                         '', 37),
                                        ('DYNAMIC_PAINT', 
                                          'Dynamic Paint', 
                                          "", 
                                         '', 36),
                                        ('COLLISION', 
                                          'Collision', 
                                          "", 
                                         '', 35),
                                        ('CLOTH', 
                                          'Cloth', 
                                          "", 
                                         '', 34),
                                        ('WAVE', 
                                          'Wave', 
                                          "", 
                                         '', 33),
                                        ('WARP', 
                                          'Warp', 
                                          "", 
                                         '', 32),
                                        ('SMOOTH', 
                                          'Smooth', 
                                          "", 
                                         '', 31),
                                        ('SIMPLE_DEFORM', 
                                          'Simple Deform', 
                                          "", 
                                         '', 30),
                                        ('SHRINKWRAP', 
                                          'Shrinkwrap', 
                                          "", 
                                         '', 29),
                                        ('MESH_DEFORM', 
                                          'Mesh Deform', 
                                          "", 
                                         '', 28),
                                        ('LATTICE', 
                                          'Lattice', 
                                          "", 
                                         '', 27),
                                        ('LAPLACIANSMOOTH', 
                                          'Laplacian Smooth', 
                                          "", 
                                         '', 26),
                                        ('HOOK', 
                                          'Hook', 
                                          "", 
                                         '', 25),
                                        ('DISPLACE', 
                                          'Displace', 
                                          "", 
                                         '', 24),
                                        ('CURVE', 
                                        'Curve', 
                                        "", 
                                        '', 23),
                                        ('CAST', 
                                          'Cast', 
                                          "", 
                                         '', 22),
                                        ('ARMATURE', 
                                          'Armature', 
                                          "", 
                                         '', 21),
                                        ('TRIANGULATE', 
                                          'Triangulate', 
                                          "", 
                                         '', 20),
                                        ('SUBSURF', 
                                          'Subdivision Surface', 
                                          "", 
                                         '', 19),
                                        ('SOLIDIFY', 
                                          'Solidify', 
                                          "", 
                                         '', 18),
                                        ('SKIN', 
                                          'Skin', 
                                          "", 
                                         '', 17),
                                        ('SCREW', 
                                          'Screw', 
                                          "", 
                                         '', 16),
                                        ('REMESH', 
                                          'Remesh', 
                                          "", 
                                         '', 15),
                                        ('MULTIRES', 
                                          'Multiresolution', 
                                          "", 
                                         '', 14),
                                        ('MIRROR', 
                                          'Mirror', 
                                          "", 
                                         '', 13),
                                        ('MASK', 
                                          'Mask', 
                                          "", 
                                         '', 12),
                                        ('EDGE_SPLIT', 
                                          'Edge Split', 
                                          "", 
                                         '', 11),
                                        ('DECIMATE', 
                                          'Decimate', 
                                          "", 
                                         '', 10),
                                        ('BUILD', 
                                          'Build', 
                                          "", 
                                         '', 9),
                                        ('BOOLEAN', 
                                          'Boolean', 
                                          "", 
                                         '', 8),
                                        ('BEVEL', 
                                          'Bevel', 
                                          "", 
                                         '', 7),
                                        ('ARRAY', 
                                          'Array', 
                                          "", 
                                         '', 6),
                                        ('VERTEX_WEIGHT_PROXIMITY', 
                                          'Vertex Weight Proximity', 
                                          "", 
                                         '', 5),
                                        ('VERTEX_WEIGHT_EDIT', 
                                          'Vertex Weight Edit', 
                                          "", 
                                         '', 4),
                                        ('UV_WARP', 
                                          'UV Warp', 
                                          "", 
                                         '', 3),
                                        ('UV_PROJECT', 
                                          'UV Project', 
                                          "", 
                                         '', 2),
                                        ('MESH_CACHE', 
                                          'Mesh Cache', 
                                          "", 
                                         '', 1),
                                        ('ALL', 
                                          'All Modifiers', 
                                          "", 
                                         '', 0)], default='ALL')

    @classmethod
    def poll(cls, context):
        """Space data type must be in 3D view."""
        return context.space_data.type in 'VIEW_3D'

    def draw(self, context):
        """Draw the operator panel/menu."""
        layout = self.layout
        col = layout.column()
        props = self.properties
        row = col.row(align=True)
  # Target Row
        split = col.split(align=True)
        split.prop(props, 'batch_objects', text="", icon='OBJECT_DATA')
        split.prop(props, 'batch_object_constraints', text="",
                   icon='CONSTRAINT')
        split.prop(props, 'batch_modifiers', text="", icon='MODIFIER')
        split.prop(props, 'batch_objects_data', text="", icon='MESH_DATA')
        if context.object.mode in 'POSE' or 'EDIT_ARMATURE':
            split.prop(props, 'batch_bones', text="", icon='BONE_DATA')
            if context.selected_pose_bones:
                split.prop(props, 'batch_bone_constraints', text="",
                           icon='CONSTRAINT_BONE')
            else:
                pass
        else:
            pass
  # Target Types
        col.prop(props, 'object_type', text="", icon='OBJECT_DATA')
        col.prop(props, 'constraint_type', text="", icon='CONSTRAINT')
        col.prop(props, 'modifier_type', text="", icon='MODIFIER')
  # Input Fields
        col.separator()
        col.prop(props, 'batch_name')
        col.separator()
        col.prop(props, 'find', icon='VIEWZOOM')
        col.separator()
        col.prop(props, 'replace', icon='FILE_REFRESH')
        col.separator()
        col.prop(props, 'prefix', icon='LOOP_BACK')
        col.separator()
        col.prop(props, 'suffix', icon='LOOP_FORWARDS')
        col.separator()
        row = col.row()
        row.label(text="Trim Start:")
        row.prop(props, 'trim_start', text="")
        row = col.row()
        row.label(text="Trim End:")
        row.prop(props, 'trim_end', text="")

    def execute(self, context):
        """Execute the operator."""
        batch_rename(self, context, self.batch_name, self.find, self.replace,
                     self.prefix, self.suffix, self.trim_start, self.trim_end,
                     self.batch_objects, self.batch_object_constraints,
                     self.batch_modifiers, self.batch_objects_data,
                     self.batch_bones, self.batch_bone_constraints,
                     self.object_type, self.constraint_type,
                     self.modifier_type)
        return {'FINISHED'}

    def invoke(self, context, event):
        """Invoke the operator panel/menu, control its width."""
        wm = context.window_manager
        wm.invoke_props_dialog(self, width=225)

        return {'RUNNING_MODAL'}

###############
## INTERFACE ##
###############
  # Imports
from bpy.types import Panel, PropertyGroup


  # Item Panel Property Group
class Item(PropertyGroup):
    """Property group for item panel."""
    view_options = BoolProperty(name='Show/hide view options',
                                description="Toggle view options for this pane"
                                "l, the state that they are in is uneffected b"
                                "y this action.", default=False)
    view_constraints = BoolProperty(name='View object constraints',
                                    description="Display the object constraint"
                                    "s of the active object.", default=False)
    view_modifiers = BoolProperty(name='View object modifiers', description="D"
                                  "isplay the object modifiers of the active o"
                                  "bject.", default=False)
    view_bone_constraints = BoolProperty(name='View bone constraints',
                                         description="Display the bone constra"
                                         "ints of the active pose bone.",
                                         default=False)


  # View 3D Item (PT)
class VIEW3D_PT_item(Panel):
    """Item panel, props created in Item property group, stored in wm.item."""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Item'

    @classmethod
    def poll(cls, context):
        """There must be an active object."""
        return bpy.context.active_object

    def draw_header(self, context):
        """Item panel header."""
        layout = self.layout
        wm_props = context.window_manager.item

        layout.prop(wm_props, 'view_options', text="")

    def draw(self, context):
        """Item panel body."""
        layout = self.layout
        col = layout.column()
        wm_props = context.window_manager.item
  # View options row
        split = col.split(align=True)
        if wm_props.view_options:
            split.prop(wm_props, 'view_constraints', text="",
                       icon='CONSTRAINT')
            split.prop(wm_props, 'view_modifiers', text="", icon='MODIFIER')
            if context.object.mode in 'POSE':
                split.prop(wm_props, 'view_bone_constraints', text="",
                           icon='CONSTRAINT_BONE')
            else:
                pass
        else:
            pass
  # Data block list
        row = col.row(align=True)
        row.template_ID(context.scene.objects, 'active')
        row.operator('view3d.batch_naming', text="", icon='AUTO')
        if wm_props.view_constraints:
            for constraint in context.active_object.constraints:
                row = col.row(align=True)
                sub = row.row()
                sub.scale_x = 1.6
                sub.label(text="", icon='DOT')
                if constraint.mute:
                    ico = 'RESTRICT_VIEW_ON'
                else:
                    ico = 'RESTRICT_VIEW_OFF'
                row.prop(constraint, 'mute', text="", icon=ico)
                row.prop(constraint, 'name', text="")
        else:
            pass
        if wm_props.view_modifiers:
            for modifier in context.active_object.modifiers:
                row = col.row(align=True)
                sub = row.row()
                sub.scale_x = 1.6
                sub.label(text="", icon='DOT')
                if modifier.show_viewport:
                    ico = 'RESTRICT_VIEW_OFF'
                else:
                    ico = 'RESTRICT_VIEW_ON'
                row.prop(modifier, 'show_viewport', text="", icon=ico)
                row.prop(modifier, 'name', text="")
        else:
            pass
        if context.object.type in 'EMPTY':
            if context.object.empty_draw_type in 'IMAGE':
                row = col.row(align=True)
                row.template_ID(context.active_object, 'data',
                                open='image.open', unlink='image.unlink')
            else:
                pass
        else:
            row = col.row(align=True)
            row.template_ID(context.active_object, 'data')
        if context.active_bone:
            row = col.row(align=True)
            sub = row.row()
            sub.scale_x = 1.6
            sub.label(text="", icon='BONE_DATA')
            row.prop(context.active_bone, 'name', text="")
            if context.object.mode in 'POSE':
                if wm_props.view_bone_constraints:
                    for constraint in context.active_pose_bone.constraints:
                        row = col.row(align=True)
                        sub = row.row()
                        sub.scale_x = 1.6
                        sub.label(text="", icon='DOT')
                        if constraint.mute:
                            ico = 'RESTRICT_VIEW_ON'
                        else:
                            ico = 'RESTRICT_VIEW_OFF'
                        row.prop(constraint, 'mute', text="", icon=ico)
                        row.prop(constraint, 'name', text="")
                else:
                    pass
            else:
                pass
        else:
            pass

##############
## REGISTER ##
##############


def register():
    """Register"""
    wm = bpy.types.WindowManager
    bpy.utils.register_module(__name__)
    wm.item = bpy.props.PointerProperty(type=Item)
    bpy.context.window_manager.item.name = 'Item Panel Properties'


def unregister():
    """Unregister"""
    wm = bpy.types.WindowManager
    bpy.utils.unregister_module(__name__)
    try:
        del wm.item
    except:
        pass

if __name__ in '__main__':
    register()
