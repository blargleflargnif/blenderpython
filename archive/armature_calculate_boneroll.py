# -*- coding: utf-8 -*-

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

bl_info = {
    'name': 'Calculate Bone Roll',
    'author': 'chromoly',
    'version': (0, 0, 1),
    'blender': (2, 5, 6),
    'api': 34765,
    'location': 'View3D > Mouse > Menu',
    'description': '',
    'warning': '',
    'category': 'Armature'}


import sys
import math
import bpy
from bpy.props import *
from mathutils import Euler, Matrix, Quaternion, Vector

from va.math import MIN_NUMBER, axis_angle_to_quat
from va.armature import mat3_to_vec_roll, vec_roll_to_mat3, get_selected_bones

class ARMATURE_OT_recalculate_roll(bpy.types.Operator):
    ''' Calculate Bone Roll. Bug fix armature.calculate_roll'''
    bl_description = 'Calculate Bone Roll'
    bl_idname = 'armature.recalculate_roll'
    bl_label = 'Recalculate Roll'
    bl_options = {'REGISTER', 'UNDO'}

    boneaxis = EnumProperty(items=(('x', 'X', ''),
                                   ('z', 'Z', ''),
                                   ('-x', '-X', ''),
                                   ('-z', '-Z', '')),
                            name='Bone Axis',
                            description='',
                            default='z')
    axisto = EnumProperty(items=(('z', 'Z', ''),
                                 ('cur', 'Cursor', ''),
                                 ('vec', 'Vector', '')),
                          name='To',
                          description='',
                          default='z')
    vector = FloatVectorProperty(name='Axis to',
                                 description='',
                                 default=(0.0, 0.0, 1.0),
                                 min=-sys.float_info.max,
                                 max=sys.float_info.max,
                                 soft_min=-sys.float_info.max,
                                 soft_max=sys.float_info.max,
                                 subtype='DIRECTION', size=3)
    local = BoolProperty(name='Local Coordinate',
                         description='',
                         default=True)

    # ‘DIRECTION’, ‘VELOCITY’, ‘ACCELERATION’, ‘XYZ’


    @classmethod
    def poll(cls, context):
        actob = context.active_object
        return actob and actob.type == 'ARMATURE' and actob.mode == 'EDIT'

    def execute(self, context=None):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        actob = context.active_object
        v3d = context.scene
        # cursor: local coordinate
        imat = actob.matrix_world.inverted()
        cursor = v3d.cursor_location * imat
        if self.axisto == 'vec':
            if self.local:
                customvector = self.vector
            else:
                veczero = Vector([0, 0, 0])
                customvector = self.vector * imat - veczero * imat
        arm = actob.data
        #bones = arm.edit_bones
        #print(arm.edit_bones)
        #for bone in [b for b in arm.edit_bones if b.select and not b.hide]:
        for bone in get_selected_bones(actob):
            delta = bone.tail - bone.head
            if delta.length < MIN_NUMBER:
                continue
            curmat = vec_roll_to_mat3(delta, 0)
            if self.axisto == 'z':
                y = Vector(curmat[1])
                y.normalize()
                targetmat = Matrix(((1, 0, 0), y, (0, 0, 1)))
                bone.roll = mat3_to_vec_roll(targetmat, delta)
            else:
                '''
                # ソースを流用した物。誤計算。理由不明。
                mat = curmat.to_4x4()
                mat[3][:3] = bone.head[:]
                imat = mat.inverted()
                vec = cursor * imat
                if abs(vec[0]) >= MIN_NUMBER and abs(vec[2]) >= MIN_NUMBER:
                    rot = Euler([0, math.atan2(vec[0], vec[2]), 0])
                    rmat = rot.to_matrix().to_4x4()
                    tmat = rmat * mat
                    curmat = tmat.to_3x3()
                    bone.roll = mat3_to_vec_roll(curmat, delta)
                '''
                if self.axisto == 'cur':
                    vec = cursor - bone.head
                else:
                    vec = customvector
                proj = vec.project(delta)
                zaxis = vec - proj
                if zaxis.length >= MIN_NUMBER:
                    zaxis.normalize()
                    delta.normalize()
                    xaxis = delta.cross(zaxis)
                    xaxis.normalize()
                    mat = Matrix((xaxis, delta, zaxis))
                    bone.roll = mat3_to_vec_roll(mat, delta)
                else:
                    continue
            if self.boneaxis == 'x':
                bone.roll -= math.pi / 2
            elif self.boneaxis == 'z':
                pass
            elif self.boneaxis == '-x':
                bone.roll += math.pi / 2
            elif self.boneaxis == '-z':
                bone.roll += math.pi

        #bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    '''def draw(self, context=None):
        layout = self.layout
        layout.prop(self, 'vector')
        layout.prop(self, 'local', toggle=True)
    '''

    def invoke(self, context=None, event=None):
        if self.axisto == 'vec':
            wm = context.window_manager
            wm.invoke_props_dialog(self)
            return {'RUNNING_MODAL'}
        else:
            self.execute(context)
        return {'FINISHED'}


class ARMATURE_MT_recalculate_roll(bpy.types.Menu):
    ''' Calculate Bone roll '''
    bl_label = 'Recalculate Roll'  # The menu label

    @classmethod
    def poll(cls, context):
        actob = context.active_object
        return actob.type == 'ARMATURE' and actob.mode == 'EDIT'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN' # call invoke
        op = layout.operator('armature.recalculate_roll', text='Z-Axis UP')
        #op.boneaxis = 'z'
        op.axisto = 'z'
        op = layout.operator('armature.recalculate_roll',
                             text='Z-Axis to Cursor')
        #op.boneaxis = 'z'
        op.axisto = 'cur'
        op = layout.operator('armature.recalculate_roll',
                             text='Z-Axis to Vector')
        #op.boneaxis = 'z'
        op.axisto = 'vec'



# Register

def register():
    bpy.utils.register_module(__name__)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['Armature']
    for kmi in km.items:
        if kmi.idname == 'armature.calculate_roll':
            if kmi.type == 'N':
                kmi.shift = True
    kmi = km.items.new('wm.call_menu', 'N', 'PRESS', ctrl=True)
    kmi.properties.name = 'ARMATURE_MT_recalculate_roll'


def unregister():
    bpy.utils.unregister_module(__name__)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['Armature']
    for kmi in km.items:
        if kmi.idname == 'armature.calculate_roll':
            if kmi.type == 'N':
                kmi.shift = False
        elif kmi.idname == 'wm.call_menu':
            if kmi.properties.name == 'ARMATURE_MT_recalculate_roll':
                km.items.remove(kmi)


if __name__ == '__main__':
    register()
