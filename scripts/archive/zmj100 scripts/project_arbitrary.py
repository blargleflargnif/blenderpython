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
    'name': 'project_arbitrary',
    'author': '',
    'version': (0, 0, 4),
    'blender': (2, 6, 1),
    'api': 42909,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy
from bpy.props import EnumProperty, PointerProperty, BoolProperty
from mathutils.geometry import intersect_point_line, intersect_line_plane
from mathutils import Vector

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

def get_mesh_data_():
    edit_mode_out()
    ob_act = bpy.context.active_object
    me = ob_act.data
    edit_mode_in()
    return me

def list_clear_(l):
    l[:] = []
    return l

def faces_copy_(me, dict_1):
    list_f = [ f.index for f in me.faces if f.select ]
    for fi in list_f:
        list_v = list(me.faces[fi].vertices[:])
        len_ = len(list_v)
        tmp = []
        for vi in list_v:
            tmp.append(dict_1[vi])
        tmp.reverse()
        me.faces.add(1)
        if len_ == 3:
            me.faces[-1].vertices = tmp
        elif len_ == 4:
            me.faces[-1].vertices_raw = tmp
    me.update(calc_edges = True)

def faces_copy_1(me, dict_1, n):
    list_f = [ f.index for f in me.faces if f.select ]
    
    for j in range(n):
        for fi in list_f:
            list_v = list(me.faces[fi].vertices[:])
            len_ = len(list_v)
            tmp = []
            for vi in list_v:
                tmp.append(dict_1[vi][j])
            tmp.reverse()
            me.faces.add(1)
            if len_ == 3:
                me.faces[-1].vertices = tmp
            elif len_ == 4:
                me.faces[-1].vertices_raw = tmp
    me.update(calc_edges = True)

def edge_copy_(me, dict_1):
    list_e = [ e.key for e in me.edges if e.select ]
    for i in list_e:
        me.edges.add(1)
        me.edges[-1].vertices = [dict_1[i[0]], dict_1[i[1]] ]

def edge_copy_1(me, dict_1, n):
    list_e = [ e.key for e in me.edges if e.select ]
    for i in list_e:
        for j in range(n):
            me.edges.add(1)
            me.edges[-1].vertices = [ dict_1[i[0]][j], dict_1[i[1]][j] ]

# ------ ------
class pt_p_group0(bpy.types.PropertyGroup):
    en0 = EnumProperty( items =( ('opt0', 'Face', ''),
                                 ('opt1', 'Edge', '') ),
                        name = 'Mode',
                        default = 'opt0' )

    en1 = EnumProperty( items =( ('opt0', 'Local', ''),
                                 ('opt1', 'Global', '') ),
                        name = 'Orientation',
                        default = 'opt0' )

    b0 = BoolProperty( name = 'Project Arbitrary', default = False )
    b = BoolProperty( name = 'Copy', default = False)

# ------ ------
class pt_buf():
    list_f = []
    list_e = []

# ------ project on plane ------
def f_(me, list_0, arg, context, ob_act):

    cb = context.scene.pt_custom_props.b
    cen1 = context.scene.pt_custom_props.en1

    dict_0 = {}
    dict_1 = {}
    
    if arg == 'x':
        pn = Vector((0, 1, 0))
        pp = Vector((1, 0, 0))
    elif arg == 'y':
        pn = Vector((1, 0, 0))
        pp = Vector((0, 1, 0))
    elif arg == 'z':
        pn = Vector((0, 0, 1))
        pp = Vector((0, 1, 0))

    if cb == False:
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
            p = v + (pn * 0.1)
            if cen1 == 'opt0':
                p3 = intersect_line_plane(v, p, pp, pn)
            elif cen1 == 'opt1':
                p1 = ob_act.matrix_world * v
                gp = p1 + (pn * 0.1)
                p2 = intersect_line_plane(p1, gp, pp, pn)
                p3 = (ob_act.matrix_world).inverted() * p2
            
            dict_0[vi] = p3

        for j in dict_0:
            me.vertices[j].co = dict_0[j]

    elif cb == True:
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
            p = v + (pn * 0.1)
            if cen1 == 'opt0':
                p3 = intersect_line_plane(v, p, pp, pn)
            elif cen1 == 'opt1':
                p1 = ob_act.matrix_world * v
                gp = p1 + (pn * 0.1)
                p2 = intersect_line_plane(p1, gp, pp, pn)
                p3 = (ob_act.matrix_world).inverted() * p2

            me.vertices.add(1)
            me.vertices[-1].co = p3
            me.vertices[-1].select = False
            dict_1[vi] = me.vertices[-1].index

        edge_copy_(me, dict_1)
        faces_copy_(me, dict_1)

# ------ project on line ------
def f_1(me, list_0, arg, context, ob_act):

    cb = context.scene.pt_custom_props.b
    cen1 = context.scene.pt_custom_props.en1

    dict_0 = {}
    dict_1 = {}

    if arg == 'x':
        lp1 = Vector((0, 0, 0))
        lp2 = Vector((1, 0, 0))
    elif arg == 'y':
        lp1 = Vector((0, 0, 0))
        lp2 = Vector((0, 1, 0))
    elif arg == 'z':
        lp1 = Vector((0, 0, 0))
        lp2 = Vector((0, 0, 1))

    if cb == False:
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
            if cen1 == 'opt0':
                p3 = intersect_point_line( v, lp1, lp2)[0]
            elif cen1 == 'opt1':
                p1 = ob_act.matrix_world * v
                p2 = intersect_point_line( p1, lp1, lp2)[0]
                p3 = (ob_act.matrix_world).inverted() * p2

            dict_0[vi] = p3

        for j in dict_0:
            me.vertices[j].co = dict_0[j]

    elif cb == True:
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
            if cen1 == 'opt0':
                p3 = intersect_point_line( v, lp1, lp2)[0]
            elif cen1 == 'opt1':
                p1 = ob_act.matrix_world * v
                p2 = intersect_point_line( p1, lp1, lp2)[0]
                p3 = (ob_act.matrix_world).inverted() * p2

            me.vertices.add(1)
            me.vertices[-1].co = p3
            me.vertices[-1].select = False
            dict_1[vi] = me.vertices[-1].index

        edge_copy_(me, dict_1)
        faces_copy_(me, dict_1)

# ------ project on arbitrary plane ------
def f_3(me, list_f, list_0):
    
    dict_1 = {vi: [] for vi in list_0}

    for fi in list_f:
        f = me.faces[fi]
        pp = (me.vertices[f.vertices[0]].co).copy()
        pn = (f.normal).copy()
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
            p = v + ((f.normal).copy() * 0.1)

            p1 =  intersect_line_plane(v, p, pp, pn)

            me.vertices.add(1)
            me.vertices[-1].co = p1
            me.vertices[-1].select = False
            dict_1[vi].append(me.vertices[-1].index)

    n = len(list_f)
    edge_copy_1(me, dict_1, n)
    faces_copy_1(me, dict_1, n)

# ------ project on arbitrary line ------
def f_4(me, list_e, list_0):

    dict_1 = {vi: [] for vi in list_0}

    for i in list_e:
        lp1 = (me.vertices[i[0]].co).copy()
        lp2 = (me.vertices[i[1]].co).copy()
        for vi in list_0:
            v = (me.vertices[vi].co).copy()
        
            p1 = intersect_point_line( v, lp1, lp2)[0]
        
            me.vertices.add(1)
            me.vertices[-1].co = p1
            me.vertices[-1].select = False
            dict_1[vi].append(me.vertices[-1].index)

    n = len(list_e)
    edge_copy_1(me, dict_1, n)
    faces_copy_1(me, dict_1, n)

# ------ panel 0 ------
class pt_p0(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'pt_p0_id'
    bl_label = 'Project'
    bl_context = 'mesh_edit'

    def draw(self, context):
        c_en0 = context.scene.pt_custom_props.en0
        c_b0 = context.scene.pt_custom_props.b0
        
        layout = self.layout
        layout.prop(context.scene.pt_custom_props, 'en0', expand = True)
        layout.prop(context.scene.pt_custom_props, 'b0')
        
        if c_b0 == False:
            layout.prop(context.scene.pt_custom_props, 'en1', expand = False)
            layout.prop(context.scene.pt_custom_props, 'b')
            row = layout.row(align = True)
            row.operator('pt.op5_id', text = 'x')
            row.operator('pt.op6_id', text = 'y')
            row.operator('pt.op7_id', text = 'z')
        elif c_b0 == True:
            row = layout.split(0.60)
            row.label('Store data:')
            if c_en0 == 'opt0':
                row.operator('pt.op0_id', text = 'face')
            elif c_en0 == 'opt1':
                row.operator('pt.op1_id', text = 'edge')
            row1 = layout.split(0.80)
            row1.operator('pt.op2_id', text = 'Project')
            row1.operator('pt.op3_id', text = '?')

# ------ operator 0 ------
class pt_op0(bpy.types.Operator):
    bl_idname = 'pt.op0_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(pt_buf.list_f)
        for f in me.faces:
            if f.select:
                pt_buf.list_f.append(f.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 1 ------
class pt_op1(bpy.types.Operator):

    bl_idname = 'pt.op1_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(pt_buf.list_e)
        for e in me.edges:
            if e.select:
                pt_buf.list_e.append(e.key)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 2 ------ project_arb
class pt_op2(bpy.types.Operator):
    bl_idname = 'pt.op2_id'
    bl_label = 'Project'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        
    def execute(self, context):

        c_en0 = context.scene.pt_custom_props.en0

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            if c_en0 == 'opt0':
                list_f = pt_buf.list_f
                if len(list_f) == 0:
                    self.report({'INFO'}, 'No faces stored in memory can not continue.')
                    edit_mode_in()
                    return {'CANCELLED'}
                else:
                    f_3(me, list_f, list_0)
                
            elif c_en0 == 'opt1':
                list_e = pt_buf.list_e
                if len(list_e) == 0:
                    self.report({'INFO'}, 'No edges stored in memory can not continue.')
                    edit_mode_in()
                    return {'CANCELLED'}
                else:
                    f_4(me, list_e, list_0)

            edit_mode_in()
            return {'FINISHED'}

# ------ operator 3 ------
class pt_op3(bpy.types.Operator):
    bl_idname = 'pt.op3_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('To use:')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 4 ------
class pt_op4(bpy.types.Operator):
    bl_idname = 'pt.op4_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.pt.op3_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ operator 5 ------ project_x
class pt_op5(bpy.types.Operator):
    bl_idname = 'pt.op5_id'
    bl_label = 'Project'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        c_en0 = context.scene.pt_custom_props.en0

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'x'
            if c_en0 == 'opt0':
                f_(me, list_0, arg, context, ob_act)
            elif c_en0 == 'opt1':
                f_1(me, list_0, arg, context, ob_act)

            edit_mode_in()
            return {'FINISHED'}

# ------ operator 6 ------ project_y
class pt_op6(bpy.types.Operator):
    bl_idname = 'pt.op6_id'
    bl_label = 'Project'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        c_en0 = context.scene.pt_custom_props.en0

        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'y'
            if c_en0 == 'opt0':
                f_(me, list_0, arg, context, ob_act)
            elif c_en0 == 'opt1':
                f_1(me, list_0, arg, context, ob_act)

            edit_mode_in()
            return {'FINISHED'}

# ------ operator 7 ------ project_z
class pt_op7(bpy.types.Operator):
    bl_idname = 'pt.op7_id'
    bl_label = 'Project'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout

    def execute(self, context):

        c_en0 = context.scene.pt_custom_props.en0
        
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'Nothing selected can not continue.')
            edit_mode_in()
            return {'CANCELLED'}
        else:
            arg = 'z'
            if c_en0 == 'opt0':
                f_(me, list_0, arg, context, ob_act)
            elif c_en0 == 'opt1':
                f_1(me, list_0, arg, context, ob_act)

            edit_mode_in()
            return {'FINISHED'}

# ------ ------
class_list = [ pt_p0, pt_op0, pt_op1, pt_op2, pt_op3, pt_op4, pt_op5, pt_op6, pt_op7, pt_p_group0 ]

# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)

    bpy.types.Scene.pt_custom_props = PointerProperty(type = pt_p_group0)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)

    del bpy.context.scene['pt_custom_props']

# ------ ------
if __name__ == "__main__":
    register()