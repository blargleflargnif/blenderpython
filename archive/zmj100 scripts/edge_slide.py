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
    'name': 'edge_slide',
    'author': '',
    'version': (0, 1, 0),
    'blender': (2, 6, 0),
    'api': 41985,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy
from bpy.props import FloatProperty, BoolProperty
from math import sin, cos, pi

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def get_f_sh_e_(me):
    tmp = dict([ (e.key, []) for e in me.edges ])
    for f in me.faces:
        for k in f.edge_keys:
            if k in tmp:
                tmp[k].append(f.index)
    return tmp

def get_eks_ns_( f, ek0, ek1 ):
    list_eks = [list(eks) for eks in f.edge_keys]
    ek0n = [i for i in list_eks if ek0 in i and ek1 not in i][0]
    if ek0 in ek0n:
        ek0n.remove(ek0)
    ek1n = [i for i in list_eks if ek1 in i and ek0 not in i][0]
    if ek1 in ek1n:
        ek1n.remove(ek1)
    return ek0n[0], ek1n[0]

def get_d1_(ev0_ang, h_pi, d):
    d1 = 0
    if ev0_ang == h_pi:
        d1 = d
    elif ev0_ang != h_pi:
        if ev0_ang < h_pi:
            d1 = d / sin(ev0_ang)
        elif ev0_ang > h_pi:
            d1 = d / cos(ev0_ang - h_pi)
    return d1

def get_d2_(ev1_ang, h_pi, d):
    d2 = 0
    if ev1_ang == h_pi:
        d2 = d
    elif ev1_ang != h_pi:
        if ev1_ang < h_pi:
            d2 = d / sin(ev1_ang)
        elif ev1_ang > h_pi:
            d2 = d / cos(ev1_ang - h_pi)
    return d2

# ------ ------
def f_(me, list_0, dict_0, d, prc, b_0, b_1, n):

    ev0_tmp = None
    ev1_tmp = None
    
    one_face = False
    if n < 2:
        one_face = True

    ek0 = list_0[0][0]
    ek1 = list_0[0][1]

    ev0 = (me.vertices[ek0].co).copy()
    ev1 = (me.vertices[ek1].co).copy()

    # -- -- -- --
    if one_face == True:

        f1 = me.faces[dict_0[list_0[0]][0]]
        ek0n0, ek1n0 = get_eks_ns_( f1, ek0, ek1 )

        ev0n0 = (me.vertices[ek0n0].co).copy()
        ev1n0 = (me.vertices[ek1n0].co).copy()

        vec0 = (ev0n0 - ev0)
        vec1 = (ev1n0 - ev1)

        ev0_an = vec0.angle((ev1 - ev0), any)
        ev1_an = vec1.angle((ev0 - ev1), any)

        # -- -- -- --
        ev0_ang = round(ev0_an, 6)
        ev1_ang = round(ev1_an, 6)
        h_pi = round(pi * 0.5, 6)

        d1 = get_d1_(ev0_ang, h_pi, d)
        d2 = get_d2_(ev1_ang, h_pi, d)

        # -- -- -- --
        if b_0 == True:
            ev0_tmp = ev0 + (vec0 * (prc / 100))
            ev1_tmp = ev1 + (vec1 * (prc / 100))

        elif b_0 == False:
            ev0_tmp = ev0 + (vec0.normalized() * d1)
            ev1_tmp = ev1 + (vec1.normalized() * d2)

    # -- -- -- --
    if one_face == False:
        if n == 2:

            f1 = me.faces[dict_0[list_0[0]][0]]
            ek0n0, ek1n0 = get_eks_ns_( f1, ek0, ek1 )

            f2 = me.faces[dict_0[list_0[0]][1]]
            ek0n1, ek1n1 = get_eks_ns_( f2, ek0, ek1 )

            if b_0 == True:
                val = prc
            elif b_0 == False:
                val = d

            # -- -- -- --
            if val > 0:
                ev0n0 = (me.vertices[ek0n0].co).copy()
                ev1n0 = (me.vertices[ek1n0].co).copy()

                vec0 = (ev0n0 - ev0)
                vec1 = (ev1n0 - ev1)

                # -- -- -- --
                ev0_ang = round((vec0.angle((ev1 - ev0), any)), 6)
                ev1_ang = round((vec1.angle((ev0 - ev1), any)), 6)
                h_pi = round(pi * 0.5, 6)

                d1 = get_d1_(ev0_ang, h_pi, d)
                d2 = get_d2_(ev1_ang, h_pi, d)

                # -- -- -- --
                if b_0 == True:
                    ev0_tmp = ev0 + (vec0 * (val / 100))
                    ev1_tmp = ev1 + (vec1 * (val / 100))
        
                elif b_0 == False:
                    ev0_tmp = ev0 + (vec0.normalized() * d1)
                    ev1_tmp = ev1 + (vec1.normalized() * d2)

            # -- -- -- --
            elif val < 0:
                ev0n1 = (me.vertices[ek0n1].co).copy()
                ev1n1 = (me.vertices[ek1n1].co).copy()

                vec0 = (ev0n1 - ev0)
                vec1 = (ev1n1 - ev1)

                # -- -- -- --
                ev0_ang = round((vec0.angle((ev1 - ev0), any)), 6)
                ev1_ang = round((vec1.angle((ev0 - ev1), any)), 6)
                h_pi = round(pi * 0.5, 6)

                d1 = get_d1_(ev0_ang, h_pi, d)
                d2 = get_d2_(ev1_ang, h_pi, d)

                # -- -- -- --
                if b_0 == True:
                    ev0_tmp = ev0 - (vec0 * (val / 100))
                    ev1_tmp = ev1 - (vec1 * (val / 100))
        
                elif b_0 == False:
                    ev0_tmp = ev0 - (vec0.normalized() * d1)
                    ev1_tmp = ev1 - (vec1.normalized() * d2)

    # -- -- -- --
    if  ev0_tmp == None:
        pass
    else:
        if b_1 == True:
            tmp = []
            me.vertices.add(1)
            me.vertices[-1].co = ev0_tmp
            tmp.append(me.vertices[-1].index)
            me.vertices[-1].select = False

            me.vertices.add(1)
            me.vertices[-1].co = ev1_tmp
            tmp.append(me.vertices[-1].index)
            me.vertices[-1].select = False
    
            me.edges.add(1)
            me.edges[-1].vertices = tmp
    
        elif b_1 == False:
            me.vertices[ek0].co = ev0_tmp
            me.vertices[ek1].co = ev1_tmp

# ------ panel 0 ------
class es_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'es_p0_id'
    bl_label = 'Edge slide'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        layout.operator('es.op0_id', text = 'Slide')

# ------ operator 0 ------
class es_op0(bpy.types.Operator):

    bl_idname = 'es.op0_id'
    bl_label = 'Edge Slide'
    bl_options = {'REGISTER', 'UNDO'}

    d = FloatProperty( default = 0.1, min = -100.0, max = 100.0, step = 1, precision = 3 )
    prc = FloatProperty( default = 10.0, min = -100.0, max = 100.0, step = 1000, precision = 3 )
    b_0 = BoolProperty( name = 'Percent', default = False )
    b_1 = BoolProperty( name = 'New edge', default = True )
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'b_1')
        layout.prop(self, 'b_0')

        if self.b_0 == True:
            layout.label(text = 'Percent:')
            layout.prop(self, 'prc', slider = True)
        else:
            layout.label(text = 'Distance:')
            layout.prop(self, 'd', slider = False)
        
    def execute(self, context):

        d = self.d
        prc = self.prc
        b_0 = self.b_0
        b_1 = self.b_1

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data
        
        list_0 = [e.key for e in me.edges if e.select]
        dict_0 = get_f_sh_e_(me)
        n = len(dict_0[list_0[0]])
        
        if len(list_0) != 1:
            self.report({'INFO'}, 'One edge must be selected.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) == 1:
            if n == 1 or n == 2:
                f_(me, list_0, dict_0, d, prc, b_0, b_1, n)
            else:
                self.report({'INFO'}, 'Selected edge must belong to one or two faces.')
                edit_mode_in()
                return {'CANCELLED'}
            edit_mode_in()
            return {'FINISHED'}

# ------ ------
class_list = [ es_op0, es_p0 ]

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