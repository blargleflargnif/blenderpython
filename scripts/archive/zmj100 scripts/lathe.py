# -*- coding: utf-8 -*-

# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

# ------ ------
bl_info = {
    'name': 'lathe',
    'author': '',
    'version': (0, 1, 0),
    'blender': (2, 6, 1),
    'api': 43085,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy
from bpy.props import EnumProperty, IntProperty, FloatProperty
from mathutils import Vector, Matrix
from math import radians

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def a_rot(ang, rp, axis, q):
    mtrx = Matrix.Rotation(ang, 3, axis)
    tmp = q - rp
    tmp1 = mtrx * tmp
    tmp2 = tmp1 + rp
    return tmp2

# ------ ------
def f_(me, list_0, n_, en0, ang):

    list_1 = [e.key for e in me.edges if e.select]
    dict_0 = {}

    rp = Vector((0, 0, 0))

    if ang == 360:
        t = n_ - 1
    else:
        t = n_

    for vi in list_0:
        p = (me.vertices[vi].co).copy()
        dict_0[vi] = []
        dict_0[vi].append(vi)

        for j in range(t):
            ang_new = radians(ang) * (j + 1) / n_
            if en0 == 'opt0':
                p_new = a_rot(ang_new, rp, 'X', p)
            elif en0 == 'opt1':
                p_new = a_rot(ang_new, rp, 'Y', p)
            elif en0 == 'opt2':
                p_new = a_rot(ang_new, rp, 'Z', p)

            me.vertices.add(1)
            me.vertices[-1].co = p_new
            dict_0[vi].append(me.vertices[-1].index)

    for i in list_1:
        list_2 = dict_0[i[0]]
        list_3 = dict_0[i[1]]
        n1 = len(list_2)
        
        if ang == 360:
            t1 = n1
        else:
            t1 = n1 - 1
        
        for k in range(t1):
            me.faces.add(1)
            me.faces[-1].vertices_raw = [ list_2[k], list_2[(k + 1) % n1], list_3[(k + 1) % n1], list_3[k] ]

    me.update(calc_edges = True)

# ------ panel 0 ------
class lth_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'lth_p0_id'
    bl_label = 'Lathe'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        layout.operator('lth.op0_id', text = 'Lathe')

# ------ operator 0 ------
class lth_op0(bpy.types.Operator):
    bl_idname = 'lth.op0_id'
    bl_label = 'Lathe'
    bl_options = {'REGISTER', 'UNDO'}

    n_ = IntProperty( name = '', default = 3, min = 0, max = 360, step = 1 )
    ang = FloatProperty( name = '', default = 360.0, min = -360.0, max = 360.0, step = 100, precision = 3 )
    en0 = EnumProperty( items =( ('opt0', 'x', ''),
                                 ('opt1', 'y', ''),
                                 ('opt2', 'z', '') ),
                        name = 'Axis',
                        default = 'opt2' )

    def draw(self, context):
        layout = self.layout
        layout.label('Axis:')
        layout.prop(self, 'en0', expand = True)
        layout.label('Angle:')
        layout.prop(self, 'ang')
        layout.label('Number of sides:')
        layout.prop(self, 'n_')

    def execute(self, context):

        n_ = self.n_
        ang = self.ang
        en0 = self.en0

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No outline selected')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            f_(me, list_0, n_, en0, ang)

            edit_mode_in()
            bpy.ops.mesh.normals_make_consistent(inside = False)
            bpy.ops.mesh.remove_doubles(limit = 0.0001)
            return {'FINISHED'}

# ------ ------
class_list = [ lth_op0,lth_p0 ]
               
# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

# ------ ------
if __name__ == "__main__":
    register()