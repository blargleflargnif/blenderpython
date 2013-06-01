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
    'name': 'vertex_slide',
    'author': '',
    'version': (0, 1, 6),
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
from bpy.props import EnumProperty, PointerProperty, FloatProperty, BoolProperty, IntProperty
from mathutils.geometry import intersect_line_plane

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

# -- -- -- --
class vs_p_group0(bpy.types.PropertyGroup):

    en0 = EnumProperty( items =( ('opt0', 'Vertex normal', ''),
                                 ('opt1', 'Edge', ''),
                                 ('opt2', 'Face normal', '') ),
                        name = 'Slide along',
                        default = 'opt1' )

# ------ ------
class vs_buf():
    list_0 = []
    list_1 = []

# ------ panel 0 ------
class vs_p0(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'vs_p0_id'
    bl_label = 'Vertex slide'
    bl_context = 'mesh_edit'

    def draw(self, context):
        c_en0 = context.scene.vs_custom_props.en0

        layout = self.layout
        layout.prop(context.scene.vs_custom_props, 'en0', expand = False)

        row = layout.split(0.60)
        row.label('Store data:')
        if c_en0 == 'opt0':
            row.operator('vs.op0_id', text = 'Vertex')
        elif c_en0 == 'opt1':
            row.operator('vs.op0_id', text = 'Edge')
        elif c_en0 == 'opt2':
            row.operator('vs.op1_id', text = 'Face')
        row1 = layout.split(0.80)
        row1.operator('vs.op2_id', text = 'Slide')
        row1.operator('vs.op3_id', text = '?')

# ------ operator 0 ------
class vs_op0(bpy.types.Operator):

    bl_idname = 'vs.op0_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(vs_buf.list_0)
        for v in me.vertices:
            if v.select:
                vs_buf.list_0.append(v.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 1 ------
class vs_op1(bpy.types.Operator):

    bl_idname = 'vs.op1_id'
    bl_label = ''

    def execute(self, context):
        me = get_mesh_data_()
        list_clear_(vs_buf.list_1)
        for f in me.faces:
            if f.select:
                vs_buf.list_1.append(f.index)
                bpy.ops.mesh.select_all(action = 'DESELECT')
        return {'FINISHED'}

# ------ operator 2 ------
class vs_op2(bpy.types.Operator):

    bl_idname = 'vs.op2_id'
    bl_label = 'Vertex slide'
    bl_options = {'REGISTER', 'UNDO'}
    
    b0 = BoolProperty( name = 'Percent', default = False )
    b1 = BoolProperty( name = 'Steps', default = False )

    d = FloatProperty( name = '', default = 0.0, min = -100.0, max = 100.0, step = 1, precision = 3 )
    prc = FloatProperty( name = '% ', default = 0.0, min = -100.0, max = 100.0, step = 100, precision = 3 )
    stp = IntProperty( name = 'Steps ', default = 0, min = -100, max = 100, step = 1 )

    def draw(self, context):
        layout = self.layout
        c_en0 = context.scene.vs_custom_props.en0

        box = layout.box()
        row = box.row()
        if c_en0 == 'opt1':
            row.prop(self, 'b0')
        row.prop(self, 'b1')

        if self.b0 == False:
            box.label('Distance :')
            box.prop(self, 'd')
        elif self.b0 == True:
            box.label('Distance % of edge length :')
            box.prop(self, 'prc')

        if self.b1 == True:
            box.prop(self, 'stp')

    def execute(self, context):

        c_en0 = context.scene.vs_custom_props.en0
        edit_mode_out()
        ob_act = context.active_object
        me = ob_act.data

        if self.b1 == True:
            t = self.stp
        else:
            t = 1

        if c_en0 == 'opt0':
            if len(vs_buf.list_0) == 0 or len(vs_buf.list_0) > 1:
                self.report({'INFO'}, 'No vertex stored in memory unable to get vertex normal.')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(vs_buf.list_0) == 1:
                vec = (me.vertices[vs_buf.list_0[0]].normal).copy()

        elif c_en0 == 'opt1':
            if len(vs_buf.list_0) != 2:
                self.report({'INFO'}, 'No vertices stored in memory unable to calculate vector.')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(vs_buf.list_0) == 2:
                p = (me.vertices[vs_buf.list_0[0]].co).copy()
                p1 = (me.vertices[vs_buf.list_0[1]].co).copy()
                vec = p - p1

        elif c_en0 == 'opt2':
            if len(vs_buf.list_1) != 1:
                self.report({'INFO'}, 'No face stored in memory unable to get face normal.')
                edit_mode_in()
                return {'CANCELLED'}
            elif len(vs_buf.list_1) == 1:
                vec = (me.faces[vs_buf.list_1[0]].normal).copy()

        no_vec = vec.normalized()

        list_0 = [v.index for v in me.vertices if v.select]

        if len(list_0) == 0:
            self.report({'INFO'}, 'No vertices selected.')
            edit_mode_in()
            return {'CANCELLED'}
        elif len(list_0) != 0:
            for vi in list_0:
                v = (me.vertices[vi].co).copy()
                
                if self.b0 == False:
                    me.vertices[vi].co = v + (no_vec * (t * self.d))
                
                elif self.b0 == True:
                    me.vertices[vi].co = v + (vec * (t * self.prc / 100))
        
        edit_mode_in()
        return {'FINISHED'}

# ------ operator 3 ------
class vs_op3(bpy.types.Operator):

    bl_idname = 'vs.op3_id'
    bl_label = ''

    def draw(self, context):
        layout = self.layout
        layout.label('Help:')
        layout.label('To use select whatever you want to use for sliding ')
        layout.label('and click button next to store data label. ')
        layout.label('Select vertex or vertices that you want to slide and click Slide button. ')
    
    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width = 400)

# ------ operator 4 ------
class vs_op4(bpy.types.Operator):
    bl_idname = 'vs.op4_id'
    bl_label = ''

    def execute(self, context):
        bpy.ops.vs.op3_id('INVOKE_DEFAULT')
        return {'FINISHED'}

# ------ ------
class_list = [ vs_p0, vs_op0, vs_op1, vs_op2, vs_op3, vs_op4, vs_p_group0 ]

# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)

    bpy.types.Scene.vs_custom_props = PointerProperty(type = vs_p_group0)

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)
    
    del bpy.context.scene['vs_custom_props']

# ------ ------
if __name__ == "__main__":
    register()