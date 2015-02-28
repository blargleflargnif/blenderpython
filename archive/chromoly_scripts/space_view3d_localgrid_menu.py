# coding: utf-8

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
    'name': 'Local grid menu',
    'author': 'chromoly',
    'version': (0, 4, 0),
    'blender': (2, 5, 6),
    'api': 34926,
    'location': 'View3D > Ctrl + D',
    'category': '3D View'}


import time
import sys
import math

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Euler, Matrix, Vector, Quaternion

from va.object import sort_parent_and_child
from va.view import check_view_context, world_to_window_coordinate
from va.utils import flatten_matrix



'''
0.3からの変更点:
    名称変更:
        SpaceView3D.localgrid -> use_local_grid
        SpaceView3D.localgrid_orig -> local_grid_origin
        SpaceView3D.localgrid_quat -> local_grid_rotation
    Quaternionの内部での処理方法を変更:
        (旧)localgrid_quat.inverted() == (新)local_grid_rotation
        例: ob基準のグリッド作成
            SpaceView3D.local_grid_origin = Vector(ob.matrix_world[3][:3])
            quat = ob.matrix_world.to_3x3().to_quaternion()
            SpaceView3D.local_grid_rotation = quat
    メニューアイテムの記録方法の変更:
        旧来のデータ、'localgrid_menu_items_float'と
        'localgrid_menu_items_strings'がCustomPropertiesに記録してある場合、
        'local_grid'に変換した後消去。
'''


icon_items = (('GRID', 'Grid', ''),
              ('MUTE_IPO_OFF', 'Eye', ''),
              ('ROTACTIVE', 'Active', ''),
              ('OBJECT_DATA', 'Object', ''),
              ('MESH_DATA', 'Mesh', ''),
              ('EMPTY_DATA', 'Empty', ''),
              ('ARMATURE_DATA', 'Armature', ''),
              ('BONE_DATA', 'Bone', ''),
              ('OBJECT_DATAMODE', 'Object Mode', ''),
              ('EDITMODE_HLT', 'Edit Mode', ''),
              ('POSE_HLT', 'Pose Mode', ''),
              ('MANIPUL', 'Manipulator', ''))


class LGMenuItem(bpy.types.PropertyGroup):
    item_name = StringProperty(name='Name')
    icon = EnumProperty(items=icon_items,
                        name='Icon', default='GRID')
    orig = FloatVectorProperty(name='Origin',
                               description='v3d.local_grid_origin',
                               default=(0.0, 0.0, 0.0), step=3, precision=2,
                               subtype='XYZ', size=3)
    quat = FloatVectorProperty(name='Rotation',
                               description='v3d.local_grid_rotation',
                               default=(1.0, 0.0, 0.0, 0.0),
                               step=3, precision=2,
                               subtype='QUATERNION', size=4)


class LGData(bpy.types.PropertyGroup):
    items = CollectionProperty(name='MenuItems', type=LGMenuItem)



class VIEW3D_OT_local_grid_menu_convert_old_new(bpy.types.Operator):
    bl_label = 'Convert'
    bl_idname = 'view3d.local_grid_menu_convert_old_new'
    bl_options = {'REGISTER'}
    def execute(self, context):
        scn = context.scene
        if 'localgrid_menu_items_strings' in scn and \
           'localgrid_menu_items_float' in scn:
            strings_dict = scn['localgrid_menu_items_strings']
            float_dict = scn['localgrid_menu_items_float']
            for i in range(len(strings_dict.keys())):
                strings = strings_dict[str(i)]
                icon, name = strings.split(',', 1)
                ls = float_dict[str(i)]
                orig = Vector([ls[0], ls[1], ls[2]])
                quat = Quaternion([ls[3], ls[4], ls[5], ls[6]])


                item = scn.local_grid.items.add()
                item.item_name = name
                item.icon = icon
                item.orig = orig
                item.quat = quat.inverted()
        if 'localgrid_menu_items_strings' in scn:
            del(scn['localgrid_menu_items_strings'])
        if 'localgrid_menu_items_float' in scn:
            del(scn['localgrid_menu_items_float'])
        if hasattr(scn, 'localgrid_menu_items_strings'):
            del(scn.localgrid_menu_items_strings)
        if hasattr(scn, 'localgrid_menu_items_float'):
            del(scn.localgrid_menu_items_float)
        return {'FINISHED'}


viewdict = {'right':'RIGHT', 'front':'FRONT', 'top':'TOP',
            'left':'LEFT', 'back':'BACK', 'bottom':'BOTTOM',
            'user':'TOP'}



def record_local(context):
    ob = context.active_object
    if ob:
        mat = ob.matrix_world
        orig = mat.to_translation()
        #quat = mat.to_quaternion().inverted()
        quat = mat.to_3x3().to_quaternion() # ViewMatrixと同義。上記と同様の結果
    else:
        orig = quat = None
    return orig, quat


def record_view(context):
    rv3d = context.region_data
    viewmat = rv3d.view_matrix
    imat = viewmat.inverted()
    orig = Vector([0, 0, 0]) * imat
    quat = viewmat.to_3x3().to_quaternion().inverted()
    quat.normalize()
    return orig, quat


def check_local_grid_rotation_zero(context):
    v3d = context.space_data
    if v3d.local_grid_rotation.magnitude < 1E-6:
        v3d.local_grid_rotation = [1, 0, 0, 0]


class VIEW3D_OT_corsor_to_orig(bpy.types.Operator):
    '''Reset Cursor Position'''
    bl_label = 'Corsor to Local Grid Orig'
    bl_idname = 'view3d.cursor_to_orig'
    bl_options = {'REGISTER', 'UNDO'}

    zero = BoolProperty(name = 'Global',
                        description = '',
                        default = False)

    def execute(self, context):
        scn = context.scene
        v3d = context.space_data
        if v3d.use_local_grid and not self.zero:
            scn.cursor_location[:] = v3d.local_grid_origin[:]
        else:
            scn.cursor_location = [0.0, 0.0, 0.0]

        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_reset_location(bpy.types.Operator):
    '''Reset Object's Location'''
    bl_label = "Reset Object's Location"
    bl_idname = 'object.reset_location'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        scn = context.scene
        v3d = context.space_data
        cursor_location = list(scn.cursor_location)
        if v3d.use_local_grid:
            scn.cursor_location[:] = v3d.local_grid_origin[:]
        else:
            scn.cursor_location[:] = [0.0, 0.0, 0.0]
        # Error Totblock: wmOperatorReportList len: 40 0x***...
        bpy.ops.view3d.snap_selected_to_cursor()
        scn.cursor_location[:] = cursor_location
        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_rotation_euler_clear(bpy.types.Operator):
    '''Reset Object's rotation_euler (indivisually)'''
    # オペレータとして実行しないとworld_matrixが更新されない為、分離
    bl_label = "Reset Object's Rotation Euler"
    bl_idname = 'object.rotation_euler_clear'
    bl_options = {'REGISTER', 'UNDO'}

    obname = StringProperty(name='Object Name')

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        if self.obname in context.scene.objects:
            ob = context.scene.objects[self.obname]
            ob.rotation_euler = [0, 0, 0]
        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_reset_rotation(bpy.types.Operator):
    '''Reset Object's Rotation'''
    bl_label = "Reset Object's Rotation"
    bl_idname = 'object.reset_rotation'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        # object_copy_attributes.pyから
        '''
        m1 * m2 = m3
        m1 = m3 * m2.inverted()
        m2 = m1.inverted() * m3
        '''
        scn = context.scene
        v3d = context.space_data

        bpy.ops.object.rotation_clear()
        #bpy.ops.object.rotation_euler_clear()

        if v3d.use_local_grid:
            quat = v3d.local_grid_rotation
            basemat = quat.to_matrix()
            #basemat.invert()
        else:
            #basemat = Math.Matrix.Rotation(0, 3, 'X')
            #basemat = basemat.identity()
            basemat = Math.Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

        #bpy.ops.object.align_to_3x3matrix(mat=flatten_matrix(basemat))
        for ob in sort_parent_and_child(context.selected_objects):
            bpy.ops.object.align_to_3x3matrix_indivisually(obname=ob.name,
                                                   mat=flatten_matrix(basemat))

        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_align_to_3x3matrix_indivisually(bpy.types.Operator):
    '''Rotate Object and align to 3x3Matrix (indivisually)'''
    bl_label = "Align Object's Rotation Matrix"
    bl_idname = 'object.align_to_3x3matrix_indivisually'
    bl_options = {'REGISTER', 'UNDO'}

    obname = StringProperty(name='Object Name')
    mat = FloatVectorProperty(name='Matrix',
                              description='(mat[0][0], mat[0][1], ...)',
                              default=(1.0, 0.0, 0.0,
                                       0.0, 1.0, 0.0,
                                       0.0, 0.0, 1.0),
                              min=-sys.float_info.max,
                              max=sys.float_info.max,
                              soft_min=-sys.float_info.max,
                              soft_max=sys.float_info.max,
                              subtype='MATRIX',
                              size=9)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        if self.obname in context.scene.objects:
            ob = context.scene.objects[self.obname]
        else:
            return {'FINISHED'}

        # reset rotation
        bpy.ops.object.rotation_euler_clear(obname=self.obname)

        # set rotmat
        if ob.parent:
            # ※ to_3x3()はScaleを含む。 to_euler, to_quaternionで除去
            obrotmat = ob.matrix_world.to_3x3()
            #↓どの道、scale[2, 1, 1]等の場合に誤差が出る。
            #obrotmat = ob.matrix_world.to_3x3().to_quaternion().to_matrix()
            rotmat = obrotmat.inverted() * self.mat
        else:
            rotmat = self.mat

        # align
        rotation_mode = ob.rotation_mode
        if rotation_mode in ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']:
            eul = rotmat.to_euler(rotation_mode)
            ob.rotation_euler[:] = eul[:]
        else:
            quat = rotmat.to_quaternion()
            if rotation_mode == 'QUATERNION':
                ob.rotation_quaternion = quat
            else: # 'AXIS_ANGLE'
                angle = quat.angle
                axis = quat.axis
                axis_angle = [angle, axis[0], axis[1], axis[2]]
                ob.rotation_axis_angle[:] = axis_angle[:]
        return {'FINISHED'}


    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_align_to_3x3matrix(bpy.types.Operator):
    '''Objectを回転させてrotmatに揃える'''
    '''Align Object's Rotation Matrix'''
    bl_label = "Align Object's Rotation Matrix"
    bl_idname = 'object.align_to_3x3matrix'
    bl_options = {'REGISTER', 'UNDO'}

    mat = FloatVectorProperty(name='Matrix',
                              description='(mat[0][0], mat[0][1], ...',
                              default=(1.0, 0.0, 0.0,
                                       0.0, 1.0, 0.0,
                                       0.0, 0.0, 1.0),
                              min=-sys.float_info.max,
                              max=sys.float_info.max,
                              soft_min=-sys.float_info.max,
                              soft_max=sys.float_info.max,
                              subtype='MATRIX',
                              size=9)
    except_actob = BoolProperty(name='Except active object', default=False)

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        '''
        m1 * m2 = m3
        m1 = m3 * m2.inverted()
        m2 = m1.inverted() * m3
        '''
        except_actob = self.except_actob
        mat = self.mat

        # reset rotation
        actobselect = False
        if except_actob:
            actob = context.active_object
            if actob:
                if actob.select:
                    actobselect = True
        if actobselect:
            actob.select = False
        bpy.ops.object.rotation_clear()
        if actobselect:
            actob.select = True

        if except_actob:
            selobs = (ob for ob in context.selected_objects if ob != actob)
        else:
            selobs = (ob for ob in context.selected_objects)

        for ob in selobs:
            if ob.parent:
                # ※ to_3x3()はScaleを含む。 to_euler, to_quaternionで除去
                obrotmat = ob.matrix_world.to_3x3()
                #↓どの道、scale[2, 1, 1]等の場合に誤差が出る。
                #obrotmat = ob.matrix_world.to_3x3().to_quaternion().to_matrix()
                rotmat = obrotmat.inverted() * mat
            else:
                rotmat = mat

            rotation_mode = ob.rotation_mode
            if rotation_mode in ['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']:
                eul = rotmat.to_euler(rotation_mode)
                ob.rotation_euler[:] = eul[:]
            else:
                quat = rotmat.to_quaternion()
                if rotation_mode == 'QUATERNION':
                    ob.rotation_quaternion = quat
                else: # 'AXIS_ANGLE'
                    angle = quat.angle
                    axis = quat.axis
                    axis_angle = [angle, axis[0], axis[1], axis[2]]
                    ob.rotation_axis_angle[:] = axis_angle[:]
        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class OBJECT_OT_custom_rotation_apply(bpy.types.Operator):
    """Apply object's rotation. ObData keeps world coordinate"""
    bl_label = "Align Object's Rotation Matrix"
    bl_idname = 'object.custom_rotation_apply'
    bl_options = {'REGISTER', 'UNDO'}

    target_is_active = BoolProperty(name="Use active object's coordinate",
                                    description='ActiveObject or Grid',
                                    default=True)

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return context.active_object.mode == 'OBJECT'
        else:
            return False

    def execute(self, context):
        # object_copy_attributes.pyから
        '''
        m1 * m2 = m3
        m1 = m3 * m2.inverted()
        m2 = m1.inverted() * m3
        '''
        target_is_active = self.target_is_active
        actob = context.active_object
        selobs = context.selected_objects
        if len(selobs) == 0 or \
           target_is_active and (len(selobs) == 1 and selobs[0] == actob):
            return {'FINISHED'}

        ## mat用意
        scn = context.scene
        v3d = context.space_data
        if target_is_active:
            tagmat = actob.matrix_world.to_3x3()
        else:
            if v3d.use_local_grid:
                quat = v3d.local_grid_rotation
                tagmat = quat.to_matrix()
                #tagmat.invert()
            else:
                #basemat = Math.Matrix.Rotation(0, 3, 'X')
                #basemat = basemat.identity()
                tagmat = Math.Matrix(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        invtagmat = tagmat.inverted()

        actobselect = actob.select
        if target_is_active and actobselect:
            actob.select = False

        ## object毎に処理。applyを一度に行うと親子関係がある場合に問題が出る。対策不明
        selobs = [ob for ob in context.selected_objects]
        for ob in selobs:
            ob.select = False
        for ob in sort_parent_and_child(selobs):
            originmat = ob.matrix_world.to_3x3()
            ## rotation clear
            bpy.ops.object.rotation_euler_clear(obname=ob.name)

            clearmat = ob.matrix_world.to_3x3()
            clear_to_tag_mat = clearmat.inverted() * tagmat
            applymat = clear_to_tag_mat.inverted() * originmat

            bpy.ops.object.align_to_3x3matrix_indivisually(obname=ob.name,
                                                  mat=flatten_matrix(applymat))

            ## apply
            ob.select = True
            bpy.ops.object.rotation_apply()
            ob.select = False

            ## align
            bpy.ops.object.align_to_3x3matrix_indivisually(obname=ob.name,
                                        mat=flatten_matrix(tagmat))

        for ob in selobs:
            ob.select = True
        '''
        ## Apply
        bpy.ops.object.rotation_apply()

        ## 回転
        #bpy.ops.object.align_to_3x3matrix(mat=flatten_matrix(tagmat))
        for ob in sort_parent_and_child(selobs):
            print('after', ob.name)
            bpy.ops.object.align_to_3x3matrix_indivisually(obname=ob.name,
                                                    mat=flatten_matrix(tagmat))
        '''
        ## 終了処理
        #for ob in sort_parent_and_child(selobs):
        #    del(ob['matrix_world_3x3'])
        if target_is_active and actobselect:
            actob.select = True

        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        self.execute(context)
        return {'FINISHED'}


class VIEW3D_OT_local_grid_edit(bpy.types.Operator):
    '''Rotate local_grid_rotation by two verts'''
    bl_label = 'Local Grid Edit'
    bl_idname = 'view3d.local_grid_edit'
    bl_options = {'REGISTER', 'UNDO'}

    axis = EnumProperty(items=(('x', 'View X', ''),
                               ('y', 'View Y', '')),
                        name='Axis',
                        description='',
                        default='x',
                        options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        actob = context.active_object
        if actob and context.space_data.use_local_grid:
            if actob.type == 'MESH' and actob.mode == 'EDIT':
                return True
        return False

    def execute(self, context):
        threthold = 1E-6

        axis = self.axis
        v3d = context.space_data
        rv3d = context.region_data
        if rv3d is None:
            if not v3d.region_quadview:
                if hasattr(context, 'region_data_3d'):
                    rv3d = context.region_data_3d
        if rv3d is None:
            return
        view = check_view_context(context)
        viewmat = rv3d.view_matrix
        viewinv = viewmat.inverted()

        ob = context.active_object
        obmat = ob.matrix_world
        me = ob.data
        bpy.ops.object.mode_set(mode='OBJECT')
        verts = [v.co * obmat for v in me.vertices if v.select and not v.hide]
        bpy.ops.object.mode_set(mode='EDIT')
        if len(verts) != 2:
            self.report({'INFO'}, 'Select 2 vertices')
            return
        vec = verts[1] * viewmat - verts[0] * viewmat
        vec.z = 0.0
        if vec.length < threthold:
            return {'FINISHED'}
        if axis == 'x':
            axisvec = Vector([1, 0, 0])
            if vec.x < 0.0:
                vec.negate()
        else:
            axisvec = Vector([0, 1, 0])
            if vec.y < 0.0:
                vec.negate()
        angle = vec.angle(axisvec)
        if angle == 0.0:
            return {'FINISHED'}
        cross = vec.cross(axisvec)
        if cross.z <= 0.0:
            angle = -angle
        a = math.cos(angle / 2)
        v = Vector(viewinv[2][:3]) * math.sin(angle / 2)
        invquat = v3d.local_grid_rotation.inverted()
        quat = invquat * Quaternion([a, v.x, v.y, v.z])
        quat.invert().normalize()
        v3d.local_grid_rotation = quat

        bpy.ops.view3d.viewnumpad(type=viewdict[view])

        return {'FINISHED'}


class VIEW3D_OT_local_grid_toggle(bpy.types.Operator):
    '''
    Toggle RegionView3D.use_local_grid. Set RegionView3D.local_grid_rotation
    and local_grid_origin
    '''
    bl_label = 'Local Grid Toggle'
    bl_idname = 'view3d.local_grid_toggle'
    bl_options = {'REGISTER', 'UNDO'}

    #def poll(self, context):
    #    return context.active_object != None

    type = EnumProperty(items=(('object', 'Object', ''),
                               ('manipulator', 'Manipulator', ''),
                               ('view', 'View', '')),
                        name='Type',
                        description='',
                        default='object',
                        options={'HIDDEN'})


    mode = EnumProperty(items = (('enable', 'Enable', ''),
                                 ('disable', 'Disable', ''),
                                 ('toggle', 'Toggle', ''),
                                 ('none', 'None', '')),
                        name='Mode',
                        description='mode',
                        default='toggle',
                        options={'HIDDEN'})
    record = bpy.props.BoolProperty(name='Record',
                                    default=True,
                                    options={'HIDDEN'})
    setquat = bpy.props.BoolProperty(name='Set Rotation', default=True)
    defquat = bpy.props.BoolProperty(name='Quaternion is (1,0,0,0)', default=False)
    setorig = bpy.props.BoolProperty(name='Set Origin', default=True)
    deforig = bpy.props.BoolProperty(name='Origin is (0,0,0)', default=False)

    '''
    recordmode = EnumProperty(items = (('all', 'RecordAll', ''),
                                       ('enable', 'OnlyEnable', ''),
                                       ('none', 'None', '')),
                              name='RecordMode',
                              description='record',
                              default='enable',
                              options={'HIDDEN'})
    '''

    def execute(self, context):
        lgtype = self.type
        mode = self.mode
        #recordmode = self.recordmode
        v3d = context.space_data
        rv3d = context.region_data
        ob = context.active_object

        # check local grid
        use_local_grid = v3d.use_local_grid
        use_local_grid_bak = use_local_grid
        view = check_view_context(context)

        if ob:
            if ob.mode in ('EDIT', 'POSE'):
                is_selected = True
            else:
                is_selected = ob.select
        else:
            is_selected = False

        rec = False
        if self.record:
            if mode == 'enable' or mode == 'toggle' and not use_local_grid:
                rec = True
        if rec:
            if lgtype == 'object':
                if is_selected:
                    orig, quat = record_local(context)
            elif lgtype == 'manipulator':
                #mat = rv3d.manipulator_matrix
                mat = self.manipulator_matrix
                orig = Vector(mat[3][:3])
                quat = mat.to_3x3().to_quaternion()
            else:  # view
                orig, quat = record_view(context)
            quat.normalize()
            if self.setorig:
                if self.deforig:
                    v3d.local_grid_origin = [0, 0, 0]
                else:
                    v3d.local_grid_origin = orig
            else:
                v3d.local_grid_origin = self.local_grid_origin_bak
            if self.setquat:
                if self.defquat:
                    v3d.local_grid_rotation = [1, 0, 0, 0]
                else:
                    v3d.local_grid_rotation = quat
            else:
                v3d.local_grid_rotation = self.local_grid_rotation_bak.copy()

        if mode == 'enable':
            if is_selected or lgtype == 'view':
                v3d.use_local_grid = True
        elif mode == 'toggle':
            v3d.use_local_grid = False if self.use_local_grid_bak else True
        elif mode == 'disable':
            v3d.use_local_grid = False

        if context.region.type == 'WINDOW':
            if lgtype in ('object', 'manipulator'):
                if is_selected or mode == 'toggle' and use_local_grid_bak is True:
                    bpy.ops.view3d.viewnumpad(type=viewdict[view])
            else:
                bpy.ops.view3d.viewnumpad(type='TOP')
        return {'FINISHED'}

    def invoke(self, context, event):
        context.area.tag_redraw()
        v3d = context.space_data
        check_local_grid_rotation_zero(context)
        self.use_local_grid_bak = v3d.use_local_grid
        self.local_grid_origin_bak = v3d.local_grid_origin.copy()
        self.local_grid_rotation_bak = v3d.local_grid_rotation.copy()
        self.manipulator_matrix = context.region_data.manipulator_matrix.copy()
        self.execute(context)
        return {'FINISHED'}


class VIEW3D_OT_local_grid_menu_add_item(bpy.types.Operator):
    '''Add Menu Item'''
    bl_label = 'Add to local grid menu'
    bl_idname = 'view3d.local_grid_menu_add_item'
    bl_options = {'REGISTER', 'UNDO'} # Toolに表示するには'UNDO'が必要

    item_name = StringProperty(name='Name', description='')

    icon = EnumProperty(items = icon_items,
                        name='icon',
                        description='',
                        default='GRID')

    orig = FloatVectorProperty(name='Orig', description='',
                               min=-sys.float_info.max,
                               max=sys.float_info.max,
                               soft_min=-sys.float_info.max,
                               soft_max=sys.float_info.max,
                               step=3, precision=3,
                               subtype='XYZ', size=3)

    quat = FloatVectorProperty(name='Quat', description='',
                               min=-sys.float_info.max,
                               max=sys.float_info.max,
                               soft_min=-sys.float_info.max,
                               soft_max=sys.float_info.max,
                               step=3, precision=3,
                               subtype='QUATERNION', size=4)

    mode = EnumProperty(items = (('current', 'Current', ''),
                                 ('local', 'Local', ''),
                                 ('manipulator', 'Manipulator', ''),
                                 ('view', 'View', '')),
                        name='Mode',
                        description='add mode',
                        default='current',
                        options={'HIDDEN'})

    #def poll(self, context):
    #    return context.active_object != None

    def execute(self, context):
        if not self.add:
            return {'FINISHED'}
        if len(context.scene.local_grid.items) == self.item_num:
            item = context.scene.local_grid.items.add()  # ObjectMode
        else:
            item = context.scene.local_grid.items[-1]  # EditMode
        item.item_name = self.item_name
        item.icon = self.icon
        item.orig= Vector(self.orig)
        item.quat = Quaternion(self.quat)
        check_local_grid_rotation_zero(context)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.add = True # mode=='local'でactobが無い場合に False

        scn = context.scene
        ob = context.active_object
        if ob:
            is_selected = True if ob.mode in ('EDIT', 'POSE') else ob.select
        else:
            is_selected = False

        mode = self.mode
        if mode == 'current':
            check_local_grid_rotation_zero(context)
            self.orig = context.space_data.local_grid_origin
            self.quat = context.space_data.local_grid_rotation
            if is_selected:
                name = 'Data {0}'.format(ob.name)
            else:
                name = 'Data'
            icon = 'GRID'
        elif mode == 'local':
            if is_selected:
                self.orig, self.quat = record_local(context)
                name = ob.name
                if ob.type == 'MESH':
                    icon = 'MESH_DATA'
                elif ob.type == 'ARMATURE':
                    icon = 'ARMATURE_DATA'
                elif ob.type == 'EMPTY':
                    icon = 'EMPTY_DATA'
                else:
                    icon = 'OBJECT_DATA'
            else:
                self.add = False
                return {'FINISHED'}
        elif mode == 'manipulator':
            v3d = context.space_data
            rv3d = context.region_data
            mat = rv3d.manipulator_matrix
            self.orig = Vector(mat[3][:3])
            self.quat = mat.to_3x3().to_quaternion()
            orientation_name = v3d.transform_orientation.title()
            if is_selected:
                name = (orientation_name + ' {0}').format(ob.name)
            else:
                name = orientation_name
            icon = 'MANIPUL'
        elif mode == 'view':
            self.orig, self.quat = record_view(context)
            if is_selected:
                name = 'View {0}'.format(ob.name)
            else:
                name = 'View'
            icon = 'MUTE_IPO_OFF'
        self.item_name = name
        self.icon = icon

        #context.area.tag_redraw()
        self.item_num = len(scn.local_grid.items)
        self.execute(context)

        return {'FINISHED'}


class VIEW3D_OT_local_grid_menu_select_item(bpy.types.Operator):
    '''Change Local Grid. SHIFTKEY+LEFTMOUSE:Remove. These items saved BlendFile'''
    bl_label = 'Select local grid'
    bl_idname = 'view3d.local_grid_menu_select_item'
    bl_options = {'REGISTER', 'UNDO'}

    item_name = StringProperty(name='Name', description='')

    icon = EnumProperty(items = icon_items,
                        name='icon',
                        description='',
                        default='GRID')

    orig = FloatVectorProperty(name='Orig', description='',
                               min=-sys.float_info.max,
                               max=sys.float_info.max,
                               soft_min=-sys.float_info.max,
                               soft_max=sys.float_info.max,
                               step=3, precision=3,
                               subtype='XYZ', size=3)

    quat = FloatVectorProperty(name='Quat', description='',
                               min=-sys.float_info.max,
                               max=sys.float_info.max,
                               soft_min=-sys.float_info.max,
                               soft_max=sys.float_info.max,
                               step=3, precision=3,
                               subtype='QUATERNION', size=4)

    active = IntProperty(name='index', description='-1==Global',
                        default=0, min=-1, max=50,
                        soft_min=-1, soft_max=50, step=1,
                        options = {'HIDDEN'})

    shift = BoolProperty(name='shift', description='hold shiftkey',
                         default=False, options = {'HIDDEN'})

    def execute(self, context):
        scn = context.scene
        active = self.active
        if active == -1:
            context.space_data.use_local_grid = False
            return {'FINISHED'}
        elif self.shift:
            if len(scn.local_grid.items) == self.item_num:  # Not EditMode
                scn.local_grid.items.remove(active)
            return {'FINISHED'}

        v3d = context.space_data
        item = scn.local_grid.items[active]
        item.item_name = self.item_name
        item.icon = self.icon
        v3d.local_grid_origin = item.orig = self.orig.copy()
        v3d.local_grid_rotation = item.quat = self.quat.copy()
        return {'FINISHED'}

    def invoke(self, context, event):
        scn = context.scene
        active = self.active

        if active == -1:
            context.space_data.use_local_grid = False
        else:
            if event.shift:
                # delete item
                self.shift = True
                self.item_num = len(scn.local_grid.items)
                self.execute(context)
                return {'FINISHED'}

            if not context.space_data.use_local_grid:
                context.space_data.use_local_grid = True
            item = scn.local_grid.items[active]
            self.item_name = item.item_name
            self.icon = item.icon
            self.orig = item.orig
            self.quat = item.quat

            #context.area.tag_redraw()
            self.execute(context)
        view = check_view_context(context)
        view = viewdict[view]
        bpy.ops.view3d.viewnumpad(type=view)

        return {'FINISHED'}


class VIEW3D_MT_local_grid_add(bpy.types.Menu):
    bl_label = "Local Grid Menu sub"
    #bl_idname = 'view3d.local_grid_menu_sub'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN' # call invoke

        ## Add Current
        op = layout.operator('view3d.local_grid_menu_add_item', text='Current Data', icon='GRID')
        op.mode = 'current'
        op = layout.operator('view3d.local_grid_menu_add_item', text='Object Local', icon='OBJECT_DATA')
        op.mode = 'local'
        op = layout.operator('view3d.local_grid_menu_add_item', text='Manipulator', icon='MANIPUL')
        op.mode = 'manipulator'
        op = layout.operator('view3d.local_grid_menu_add_item', text='View Matrix', icon='MUTE_IPO_OFF')
        op.mode = 'view'


class VIEW3D_MT_local_grid_reset(bpy.types.Menu):
    '''Local Grid Menu'''
    bl_label = "Local Grid Menu sub reset"
    #bl_idname = 'view3d.local_grid_menu_sub_reset'
    bl_options = {'REGISTER'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN' # call invoke

        op = layout.operator('view3d.cursor_to_orig',
                             text='Reset 3D Cursor',
                             icon='CURSOR')
        op = layout.operator('object.reset_location',
                             #text='Object Location',
                             icon='MAN_TRANS')
        op = layout.operator('object.reset_rotation',
                             #text='Object Rotation',
                             icon='MAN_ROT')
        #layout.separator()
        op = layout.operator('object.custom_rotation_apply',
                             text='Apply rotation use Active object',
                             icon='MANIPUL')
        op.target_is_active = True
        op = layout.operator('object.custom_rotation_apply',
                             text='Apply rotation use Grid',
                             icon='MANIPUL')
        op.target_is_active = False
        #layout.separator()
        op = layout.operator('view3d.local_grid_edit',
                             text='Align View X',
                             icon='GRID')
        op.axis = 'x'
        op = layout.operator('view3d.local_grid_edit',
                             text='Align View Y',
                             icon='GRID')
        op.axis = 'y'

"""
class VIEW3D_MT_local_grid_menu_sub_edit(bpy.types.Menu):
    '''Rotate local_grid_rotation by two verts'''
    bl_label = "Local Grid Menu sub edit"
    bl_idname = 'view3d.local_grid_menu_sub_edit'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        actob = context.active_object
        if actob and context.space_data.use_local_grid:
            if actob.type == 'MESH' and actob.mode == 'EDIT':
                return True
        return False

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN' # call invoke

        op = layout.operator('view3d.local_grid_edit',
                             text='Align View X')
        op.axis = 'x'
        op = layout.operator('view3d.local_grid_edit',
                             text='Align View Y')
        op.axis = 'y'
"""

class VIEW3D_MT_local_grid(bpy.types.Menu):
    '''Local Grid Menu'''
    bl_label = "Local Grid Menu"
    #bl_idname = 'view3d.local_grid_menu'
    bl_options = {'REGISTER'}

    '''@classmethod
    def poll(cls, context):
        return True
    '''

    def __init__(self):
        # bpy.tyeps.Menu内でのデータの書き換えは不可。オペレータ作って呼ぶべし。
        bpy.ops.view3d.local_grid_menu_convert_old_new()

    def draw(self, context):
        view = check_view_context(context)
        view = viewdict[view]

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN' # call invoke

        # Reset
        layout.menu('VIEW3D_MT_local_grid_reset', text='Utility',
                    icon='CURSOR')
        layout.separator()

        ## toggle
        op = layout.operator('view3d.local_grid_toggle',text='Toggle',
                             icon='ARROW_LEFTRIGHT')
        op.mode = 'toggle'
        #op.recordmode = 'none'
        op.record = False
        ## local
        op = layout.operator('view3d.local_grid_toggle',text='Object Local',
                             icon='OBJECT_DATA')
        op.mode = 'enable'
        '''## active
        op = layout.operator('view3d.local_grid_toggle',text='Active Element',
                              icon='ROTACTIVE')
        op.mode = 'enable'
        op.type = 'active'
        '''
        ## Manipulator
        op = layout.operator('view3d.local_grid_toggle',text='Manipulator',
                             icon='MANIPUL')
        op.mode = 'enable'
        op.type = 'manipulator'
        ## view
        op = layout.operator('view3d.local_grid_toggle',text='View Matrix',
                             icon='MUTE_IPO_OFF')
        op.mode = 'enable'
        op.type = 'view'

        '''
        ## edit
        layout.menu('view3d.local_grid_menu_sub_edit', text='Rotate LocalGrid',
                    icon='GRID')
        '''

        ## Add
        layout.separator()
        layout.menu('VIEW3D_MT_local_grid_add', text='Add Item',
                    icon='TRIA_DOWN')

        ## user list
        for i, item in enumerate(context.scene.local_grid.items):
            #txt = '{0}. {1}'.format(i, item.name)
            txt = item.item_name
            icon = item.icon
            op = layout.operator('view3d.local_grid_menu_select_item',
                                 text=txt, icon=icon)
            op.active = i


# Register
def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.local_grid = PointerProperty(name='Local Grid', type=LGData)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.items.new('wm.call_menu', 'D', 'PRESS', ctrl=True)
    kmi.properties.name = 'VIEW3D_MT_local_grid'

    kmi = km.items.new('view3d.local_grid_toggle', 'E', 'PRESS', shift=True, ctrl=True)
    kmi.properties.mode = 'toggle'  # 'enable', 'disable', 'toggle', 'none'
    kmi = km.items.new('view3d.local_grid_toggle', 'E', 'PRESS', shift=True, alt=True)
    kmi.properties.mode = 'toggle'
    kmi.properties.record = False
    kmi = km.items.new('view3d.local_grid_toggle', 'E', 'PRESS', ctrl=True, alt=True)
    kmi.properties.mode = 'enable'
    #kmi = km.items.new('view3d.local_grid_toggle', 'E', 'PRESS', shift=True, ctrl=True, alt=True)
    #kmi.properties.mode = 'none'
    #kmi.properties.recordmode = 'none'



def unregister():
    bpy.utils.unregister_module(__name__)

    km = bpy.context.window_manager.keyconfigs.active.keymaps["3D View"]
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == 'VIEW3D_MT_local_grid':
                km.items.remove(kmi)
        elif kmi.idname == 'view3d.local_grid_toggle':
            km.items.remove(kmi)


if __name__ == '__main__':
    register()
