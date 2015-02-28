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
    'name': 'arch_tool',
    'author': '',
    'version': (0, 1, 5),
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
from bpy.props import EnumProperty, PointerProperty, FloatProperty, IntProperty
from mathutils.geometry import intersect_point_line, intersect_line_line
from mathutils import Matrix
from math import pi, tan, radians

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def list_clear_(l):
    l[:] = []
    return l

def get_adj_v_(list_):
        tmp = {}
        for i in list_:
                try:             tmp[i[0]].append(i[1])
                except KeyError: tmp[i[0]] = [i[1]]
                try:             tmp[i[1]].append(i[0])
                except KeyError: tmp[i[1]] = [i[0]]
        return tmp

def f1_(me, n, list_2, ang, rp, axis, p1):
    for i in range(n):
        if i == 0:
            pass
        else:
            new_angle = ang * i / n
            mtrx = Matrix.Rotation(-new_angle, 3, axis)
            tmp = p1 - rp
            tmp1 = mtrx * tmp
            tmp2 = tmp1 + rp

            me.vertices.add(1)
            me.vertices[-1].co = tmp2
            me.vertices[-1].select = False
            list_2.append(me.vertices[-1].index)

def f2_(me, n, list_2, ang, rp, axis, p1):
    list_ = []
    for i in range(n + 1):
        if i == 0:
            pass
        else:
            new_angle = ang * i / n
            mtrx = Matrix.Rotation(-new_angle, 3, axis)
            tmp = p1 - rp
            tmp1 = mtrx * tmp
            tmp2 = tmp1 + rp

            me.vertices.add(1)
            me.vertices[-1].co = tmp2
            me.vertices[-1].select = False
            list_.append(me.vertices[-1].index)
    list_.reverse()
    list_2.extend(list_)

def f3_(me, n, list_2, ang, rp, axis, p1):
    for i in range(n + 1):
        if i == 0:
            pass
        else:
            new_angle = ang * i / n
            mtrx = Matrix.Rotation(-new_angle, 3, axis)
            tmp = p1 - rp
            tmp1 = mtrx * tmp
            tmp2 = tmp1 + rp

            me.vertices.add(1)
            me.vertices[-1].co = tmp2
            me.vertices[-1].select = False
            list_2.append(me.vertices[-1].index)

def a_rot(ang, rp, axis, q):
    mtrx = Matrix.Rotation(ang, 3, axis)
    tmp = q - rp
    tmp1 = mtrx * tmp
    tmp2 = tmp1 + rp
    return tmp2

# ------ ------
class arch_p_group0(bpy.types.PropertyGroup):

    en0 = EnumProperty( items =( ('opt0', 'Semi-circular', ''),
                                 ('opt1', 'Segmental', ''),
                                 ('opt2', 'Horseshoe', ''),
                                 ('opt3', 'Equilateral', ''),
                                 ('opt4', 'Lancet', ''),
                                 ('opt5', 'Flat', '') ),
                        name = '',
                        default = 'opt0' )

# ------ ------
def f_(me, context, list_0, n, d):

    cen0 = context.scene.arch_custom_props.en0

    dict_0 = get_adj_v_(list_0)
    list_1 = [[dict_0[i][0], i, dict_0[i][1]] for i in dict_0 if (len(dict_0[i]) == 2)][0]

    p = (me.vertices[list_1[1]].co).copy()
    p1 = (me.vertices[list_1[0]].co).copy()
    p2 = (me.vertices[list_1[2]].co).copy()

    me.vertices[list_1[0]].select = False      # deselect p1
    me.vertices[list_1[2]].select = False      # deselect p2

    vec1 = p - p1
    vec2 = p - p2
    axis = vec1.cross(vec2)      # axis    
    
    vec3 = p2 - p1

    ip = intersect_point_line( p, p1, p2)[0]
    vec4 = p - ip

    p3 = (p1 + p2) * 0.5
    aw = vec3.length      # arch width
    half_aw = aw * 0.5
    
    list_2 = []      # tmp list
    list_3 = list_1[:]

    # -- -- Semi_circular -- --
    if cen0 == 'opt0':

        rp = p3
        ang = pi      # 180 deg

        f1_(me, n, list_2, ang, rp, axis, p1)

    # -- -- Segmental -- --
    elif cen0 == 'opt1':

        r = (d / 2) + ((aw ** 2) / (8 * d))
        c = (r ** 2 - half_aw ** 2) ** 0.5

        if d == half_aw:
            rp = p3
        else:
            rp = p3 - ( vec4.normalized() * c )

        ang = (rp - p1).angle((rp - p2), any)

        f1_(me, n, list_2, ang, rp, axis, p1)

    # -- -- Horseshoe -- --
    elif cen0 == 'opt2':

        r = (d / 2) + ((aw ** 2) / (8 * d))
        c = (r ** 2 - half_aw ** 2) ** 0.5

        rp = p3 + ( vec4.normalized() * c )
        ang = (2 * pi) - ((rp - p1).angle((rp - p2), any))

        f1_(me, n, list_2, ang, rp, axis, p1)

    # -- -- Equilateral -- --
    elif cen0 == 'opt3':

        r = (vec3).length
        t_d = (r ** 2 - half_aw ** 2) ** 0.5

        ang = pi / 3
        rp1 = p1
        rp2 = p2

        f1_(me, n, list_2, ang, rp2, axis, p1)
        f2_(me, n, list_2, -ang, rp1, axis, p2)

    # -- -- Lancet -- --
    elif cen0 == 'opt4':
        
        p4 = p3 + ( vec4.normalized() * d )
        
        p5_l = (p4 + p1) * 0.5
        p5_r = (p4 + p2) * 0.5
        
        tmp2_l = a_rot((pi * 0.5), p5_l, axis, p1)
        tmp2_r = a_rot(-(pi * 0.5), p5_r, axis, p2)

        rp_l = intersect_line_line(tmp2_l, p5_l, p1, p2)[0]
        rp_r = intersect_line_line(tmp2_r, p5_r, p1, p2)[0]

        ang = (rp_l - p1).angle((rp_l - p4), any)

        f1_(me, n, list_2, ang, rp_l, axis, p1)
        f2_(me, n, list_2, -ang, rp_r, axis, p2)

    # -- -- Flat -- --
    elif cen0 == 'opt5':

        rp1 = p1 + ( vec3.normalized() * (aw / 4) )
        rp2 = p2 - ( vec3.normalized() * (aw / 4) )
        
        ang0 = radians(90)
        
        f3_(me, n, list_2, ang0, rp1, axis, p1)
        f2_(me, n, list_2, -ang0, rp2, axis, p2)

    list_3[1:2] = list_2
    n1 = len(list_3)
    for j in range(n1 - 1):
        me.edges.add(1)
        me.edges[-1].vertices = [ list_3[j], list_3[(j + 1) % n1] ]

# ------ panel 0 ------
class arch_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'arch_p0_id'
    bl_label = 'Arch Tool'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        layout.operator('arch.op0_id', text = 'Arch')

# ------ operator 0 ------
class arch_op0(bpy.types.Operator):

    bl_idname = 'arch.op0_id'
    bl_label = 'Arch'
    bl_options = {'REGISTER', 'UNDO'}

    d = FloatProperty( name = '', default = 2.0, min = 0.00001, max = 100, step = 1, precision = 3 )
    n = IntProperty( name = '', default = 8, min = 1, max = 100, step = 1 )

    def draw(self, context):
        cen0 = context.scene.arch_custom_props.en0
        
        layout = self.layout
        layout.label('Arch type:')
        layout.prop(context.scene.arch_custom_props, 'en0', expand = False)
        layout.label('Number of sides:')
        layout.prop(self, 'n', slider = True)
        
        if cen0 == 'opt0':
            pass
        elif cen0 == 'opt1':
            layout.label('Height:')
            layout.prop(self, 'd')
        elif cen0 == 'opt2':
            layout.label('Height:')
            layout.prop(self, 'd')
        elif cen0 == 'opt3':
            pass
        elif cen0 == 'opt4':
            layout.label('Height:')
            layout.prop(self, 'd')
        elif cen0 == 'opt5':
            pass

    def execute(self, context):
        cen0 = context.scene.arch_custom_props.en0

        n = self.n
        d = self.d

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 =[list(e.key) for e in me.edges if e.select]

        if len(list_0) != 2:
            self.report({'INFO'}, 'Two adjacent edges must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            f_(me, context, list_0, n, d)
        
        edit_mode_in()
        bpy.ops.mesh.delete(type = 'VERT')   
        return {'FINISHED'}

# ------ ------
class_list = [ arch_p0, arch_op0, arch_p_group0 ]

# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.arch_custom_props = PointerProperty(type = arch_p_group0)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

    del bpy.context.scene['arch_custom_props']

# ------ ------
if __name__ == "__main__":
    register()