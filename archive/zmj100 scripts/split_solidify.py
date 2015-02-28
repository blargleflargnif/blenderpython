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
    'name': 'split_solidify',
    'author': '',
    'version': (0, 1, 1),
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
from bpy.props import EnumProperty, FloatProperty, BoolProperty
import random
from math import cos

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

# ------ ------
def f_(me, list_0, b_rnd, rnd, opp, th, en0):

    for fi in list_0:
        f = me.faces[fi]
        list_1 = []
        list_2 = []
        
        # -- -- -- --
        if b_rnd == True:
            d = rnd * random.randrange(0, 10)
        elif b_rnd == False:
            d = opp
        
        # -- -- -- --
        for vi in f.vertices:
            v = me.vertices[vi]

            if en0 == 'opt0':
                p1 = (v.co).copy() +  ((f.normal).copy() * d)      # out
                p2 = (v.co).copy() +  ((f.normal).copy() * (d - th))      # in
            elif en0 == 'opt1':
                ang = ((v.normal).copy()).angle((f.normal).copy())
                h = th / cos(ang)
                p1 = (v.co).copy() +  ((f.normal).copy() * d)
                p2 = p1 + (-h * (v.normal).copy())

            me.vertices.add(2)
            me.vertices[-1].co = p1      # out
            me.vertices[-1].select = False
            me.vertices[-2].co = p2      # in
            me.vertices[-2].select = False

            list_1.append(me.vertices[-1].index)      # out
            list_2.append(me.vertices[-2].index)      # in

        # -- -- -- --
        n = len(list_1)
        if n == 3:
            me.faces.add(1)
            me.faces[-1].vertices = list_1    # out
            me.faces[-1].select = False
            for i in range(n):
                me.faces.add(1)
                me.faces[-1].vertices_raw = [ list_1[i], list_2[i], list_2[(i + 1) % n], list_1[(i + 1) % n]  ]
                me.faces[-1].select = False
            list_2.reverse()
            me.faces.add(1)
            me.faces[-1].vertices = list_2
            me.faces[-1].select = False
        elif n == 4:
            me.faces.add(1)
            me.faces[-1].vertices_raw = list_1
            me.faces[-1].select = False
            for i in range(n):
                me.faces.add(1)
                me.faces[-1].vertices_raw = [ list_1[i], list_2[i], list_2[(i + 1) % n], list_1[(i + 1) % n]  ]
                me.faces[-1].select = False
            me.faces.add(1)
            me.faces[-1].vertices_raw =[list_2[0], list_2[3], list_2[2], list_2[1]]
            me.faces[-1].select = False
        
        me.update(calc_edges = True)

# ------ panel 0 ------
class sp_sol_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'sp_sol_p0_id'
    bl_label = 'Split Solidify'
    bl_context = 'mesh_edit'

    def draw(self, context):
        layout = self.layout
        layout.operator('sp_sol.op0_id', text = 'Split solidify')

# ------ operator 0 ------
class sp_sol_op0(bpy.types.Operator):

    bl_idname = 'sp_sol.op0_id'
    bl_label = 'Split Solidify'
    bl_options = {'REGISTER', 'UNDO'}

    opp = FloatProperty( name = '', default = 0.4, min = -100.0, max = 100.0, step = 1, precision = 3 )
    th = FloatProperty( name = '', default = 0.04, min = -100.0, max = 100.0, step = 1, precision = 3 )
    rnd = FloatProperty( name = '', default = 0.06, min = -10.0, max = 10.0, step = 1, precision = 3 )

    b_rnd = BoolProperty( name = 'Random', default = False )
    b_del = BoolProperty( name = 'Delete original faces', default = True )

    en0 = EnumProperty( items =( ('opt0', 'Face', ''),
                                 ('opt1', 'Vertex', '') ),
                        name = 'Normal',
                        default = 'opt0' )

    def draw(self, context):

        layout = self.layout
        layout.label('Normal:')
        layout.prop(self, 'en0', expand = True)
        layout.prop(self, 'b_rnd')
        
        if self.b_rnd == False:
            layout.label('Distance:')
            layout.prop(self, 'opp')
        elif  self.b_rnd == True:
            layout.label('Random distance:')
            layout.prop(self, 'rnd')

        layout.label('Thickness:')
        layout.prop(self, 'th')
        layout.prop(self, 'b_del')

    def execute(self, context):

        b_rnd = self.b_rnd
        rnd = self.rnd
        opp = self.opp
        th = self.th
        b_del = self.b_del
        en0 = self.en0

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [ f.index for f in me.faces if f.select ]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No faces selected')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            f_(me, list_0, b_rnd, rnd, opp, th, en0)
            edit_mode_in()

            if b_del == True:
                bpy.ops.mesh.delete(type = 'FACE')
            else:
                pass
            return {'FINISHED'}

# ------ ------
class_list = [  sp_sol_op0, sp_sol_p0 ]

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