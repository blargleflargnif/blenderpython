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
    'name': 'face_inset_fillet',
    'author': '',
    'version': (0, 0, 8),
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
from bpy.props import FloatProperty, IntProperty, BoolProperty
from math import tan, cos
from mathutils import Matrix

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def get_adj_v_(list_):
        tmp = {}
        for i in list_:
                try:             tmp[i[0]].append(i[1])
                except KeyError: tmp[i[0]] = [i[1]]
                try:             tmp[i[1]].append(i[0])
                except KeyError: tmp[i[1]] = [i[0]]
        return tmp

def f_2(frst, list_):      # edge loop
    fi = frst
    tmp = [frst]
    while list_ != []:
        for i in list_:
            if i[0] == fi:
                tmp.append(i[1])
                fi = i[1]
                list_.remove(i)
            elif i[1] == fi:
                tmp.append(i[0])
                fi = i[0]
                list_.remove(i)
        if tmp[-1] == frst:
            break
    return tmp

# ------ ------
class fif_buf():
    me_data = []

# ------ ------ ------ ------
def f_(me, me_tmp, opp, list_0, n_, adj1, out):

    for fi in list_0:
        f = me_tmp.faces[fi]

        list_1 = [list(eks) for eks in f.edge_keys]
        frst = list_1[0][0]
        list_2 = f_2(frst, list_1)
        del list_2[-1]

        dict_1 = {}
        list_3 = []

        n = len(list_2)
        for i in list_2:
            dict_1[i] = []
            q = list_2.index(i)      # q - item index

            p = (me.vertices[i].co).copy()
            p1 = (me.vertices[list_2[(q - 1) % n]].co).copy()
            p2 = (me.vertices[list_2[(q + 1) % n]].co).copy()

            vec1 = p - p1
            vec2 = p - p2

            ang = vec1.angle(vec2, any)

            adj = opp / tan(ang / 2)
            h = (adj ** 2 + opp ** 2) ** 0.5

            p3 = p - (vec1.normalized() * adj)
            p4 = p - (vec2.normalized() * adj)

            if out:
                p5 = p + ((p - ((p3 + p4) * 0.5)).normalized() * h)
            else:
                p5 = p - ((p - ((p3 + p4) * 0.5)).normalized() * h)

            h1 = adj1 * (1 / cos(ang * 0.5))

            p6 = p5 - (vec1.normalized() * adj1)
            p7 = p5 - (vec2.normalized() * adj1)

            rp = p5 - ((p - ((p3 + p4) * 0.5)).normalized() * h1)

            vec3 = rp - p6
            vec4 = rp - p7

            axis = vec1.cross(vec2)
            rot_ang = vec3.angle(vec4)

            for j in range(n_ + 1):
                new_angle = rot_ang * j / n_
                mtrx = Matrix.Rotation(new_angle, 3, axis)

                tmp = p7 - rp
                tmp1 = mtrx * tmp
                tmp2 = tmp1 + rp

                me.vertices.add(1)
                me.vertices[-1].co = tmp2
                #me.vertices[-1].select = False

                dict_1[i].append(me.vertices[-1].index)

            list_3.append([ i, dict_1[i] ])

        n2 = len(list_3)
        for o in range(n2):
            n1 = len(list_3[o][1])
            for k in range(n1 - 1):
                me.faces.add(1)
                me.faces[-1].vertices = [ list_3[o][1][k], list_3[o][1][(k + 1) % n1], list_3[o][0] ]
            me.faces.add(1)
            me.faces[-1].vertices_raw = [ list_3[o][0], list_3[(o + 1) % n2][0], list_3[(o + 1) % n2][1][-1], list_3[o][1][0] ]

        me.update(calc_edges = True)

# ------ panel 0 ------
class fif_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'fif_p0_id'
    bl_label = 'Face Inset Fillet'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        layout.operator('fif.op0_id', text = 'Inset fillet')

# ------ operator 0 ------
class fif_op0(bpy.types.Operator):

    bl_idname = 'fif.op0_id'
    bl_label = 'Face Inset Fillet'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.04, min = 0, max = 100.0, step = 1, precision = 3 )      # inset amount
    n_ = IntProperty( name = '', default = 4, min = 1, max = 100, step = 1 )      # number of sides
    adj1 = FloatProperty( name = '', default = 0.04, min = 0.00001, max = 100.0, step = 1, precision = 3 )
    out = BoolProperty( name = 'Out', default = False )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'out')
        layout.label('Inset amount:')
        layout.prop(self, 'opp')
        layout.label('Number of sides:')
        layout.prop(self, 'n_', slider = True)
        layout.label('Distance:')
        layout.prop(self, 'adj1')

    def execute(self, context):
        opp = self.opp
        n_ = self.n_
        adj1 = self.adj1
        out = self.out
        
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        
        fif_buf.me_data = me.copy()
        
        edit_mode_in()
        bpy.ops.mesh.delete(type = 'ONLY_FACE')
        edit_mode_out()

        me_tmp = fif_buf.me_data
        list_0 = [ f.index for f in me_tmp.faces if f.select ]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No faces selected.')
            edit_mode_in()
            return {'CANCELLED'}
        
        elif len(list_0) != 0:
            f_(me, me_tmp, opp, list_0, n_, adj1, out)

        edit_mode_in()
        bpy.data.meshes.remove(fif_buf.me_data)
        bpy.ops.mesh.normals_make_consistent(inside = False)
        return {'FINISHED'}

# ------ ------
class_list = [ fif_op0, fif_p0 ]

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