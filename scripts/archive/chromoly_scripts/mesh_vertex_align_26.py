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
    'name': 'Vertex Align 26',
    'author': 'chromoly',
    'version': (0, 0, 2),
    'blender': (2, 5, 6),
    'api': 34890,
    'location': 'View3D > Mouse > Menu',
    'description': '',
    'warning': '',
    'category': 'Mesh'}

'''
mesh_vertex_align_25.pyを置き換えるつもりで書き始めたのに、一向に手付かず
'''


import time
import os
#import cProfile
#import pstats
import math
import sys
#import time
from functools import reduce
#from collections import OrderedDict, Counter
from itertools import combinations  # , permutations

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils import geometry as geo
import blf
import bgl

from va.mesh import PyMesh, path_vertices_list, get_mirrored_mesh
from va.math import MIN_NUMBER, removed_same_coordinate
from va.view import Shortcut, MouseCoordinate, check_shortcuts
from va.utils import SaveProperties, WatchProperties, Null

op_prop_values = SaveProperties()


class MESH_OT_va_solidify(bpy.types.Operator):
    '''
    使用用途は限定的。
    '''
    bl_idname = 'mesh.va_solidify'
    bl_label = 'Solidify'
    bl_options = {'REGISTER', 'UNDO'}

    dist = FloatProperty(name='Dist',
                         description='distance',
                         default=0.0,
                         step=1,
                         precision=3,
                         subtype='DISTANCE',
                         unit='LENGTH')
    normalbyselected = BoolProperty(name='Calc normals by selected',
                          description='Calculate normal selected & not hide',
                          default=True)
    outline_normal_by_another_face = BoolProperty(name = 'OutlineNormalType',
        description = '非選択面・選択面を一つずつ持つ辺において、' + \
                      'その辺の法線は非選択面の方を使う',
        default = False)
    outlinemode = EnumProperty(items=(('all', 'All', ''),
                                      ('sel', 'Selected', ''),
                                      ('desel', 'Deselected', '')),
                               name='Outline Mode', description='',
                               default='all')
    precedeoutline = BoolProperty(name='Precede Outline',
                                  default=False)
    usehidden = BoolProperty(name='Calc also Hidden', description='',
                             default=True)
    threthold = FloatProperty(name='Threthold',
                              description='Face1.normal.angle(Face2.normal)',
                              default=math.radians(2.0),
                              min=0, max=math.pi, soft_min=0, soft_max=math.pi,
                              step=1, precision=2,
                              subtype='ANGLE')
    threthold2 = FloatProperty(name='Threthold2',
                               description='intersect_line_lineを行うかどうかの閾値',
                              default=math.radians(2.0),
                              min=0, max=math.pi, soft_min=0, soft_max=math.pi,
                              step=1, precision=2,
                              subtype='ANGLE')
    lock = BoolVectorProperty(name='Lock',
                              description='Lock axis',
                              default=(False, False, False), size=3,
                              subtype='XYZ')

    mirror = BoolProperty(name='Apply mirror modifiers',
                          description='',
                          default=True)
    '''keepdist = BoolProperty(name='Keep dist',
                            description='Keep dist when locked',
                            default=False,
                            options={'HIDDEN'})
    mirror = BoolVectorProperty(name = 'Mirror',
                              description = 'as Mirror',
                              default=(False, False, False),
                              subtype='XYZ')
    mirrorthrethold = FloatProperty(name='Mirror Threthold',
                                    description='',
                                    default=0.01,
                                    min=0, soft_min=0,
                                    step=1, precision=4)
    '''

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw_callback_px(self, context):
        if context.region.id != self.region_id:
            return
        # init
        font_id = 0
        #blf.position(font_id, 80, 30, 0)
        blf.size(font_id, 11, context.user_preferences.system.dpi)
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)

        ofsx = 70
        # draw Dist
        blf.position(font_id, ofsx, 50, 0)
        text_dist = '{0:>6.4f}'.format(float(self.dist))
        blf.draw(font_id, text_dist)

        # draw Expression
        if self.mc.inputexp:
            text_width, text_height = blf.dimensions(font_id, text_dist)
            posx = max(ofsx + text_width + 15, 150)
            self.mc.exp.draw_exp_strings(font_id, posx, 50,
                                         start='Exp: ',end='',
                                         col=(1.0, 1.0, 1.0, 1.0),
                                         errcol=(1.0, 0.6, 0.5, 1.0))
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)

        # draw Help
        l = ['{Tab}:InputString',
             '{M-Mouse}:Lock',
             '{R}:ResetOrig',
             '{X,Y,Z}:Lock',
             '{M}:Mirror',
             '{WHEEL UP-DOWN, E}:OutlineMode',
             '{W}:PrecedeOutline']
        blf.position(font_id, 70, 30, 0)
        blf.draw(font_id, ', '.join(l))

        # draw State
        l = []
        if self.mirror:
            l.append('Mirror')
        l.append('OutlineMode:' + self.outlinemode.title())
        if self.precedeoutline:
            l.append('PreceedOutline')
        if True in self.lock[:]:
            l.append('Lock:[{0:d},{1:d},{2:d}]'.format(*self.lock))
        if l:
            blf.position(font_id, 70, 70, 0)
            blf.draw(font_id, ', '.join(l))

        bgl.glEnable(bgl.GL_BLEND)

        # draw mouseco_init
        self.mc.draw_origin(5, raydirections=[0, math.pi], raylength=[10, 10])

        # draw mouseco_rerative
        self.mc.draw_relative(5)

        # draw mouseco_lock
        self.mc.draw_lock_arrow(8, math.radians(110))

        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        blf.size(0, 11, context.user_preferences.system.dpi)

    def reset_vertices(self, context):
        editmode = context.active_object.mode == 'EDIT'
        if editmode:
            bpy.ops.object.mode_set(mode='OBJECT')
        me = context.active_object.data
        for vert, co in zip(me.vertices, self.original_coordinats):
            vert.co = co
        me.update()
        if editmode:
            bpy.ops.object.mode_set(mode='EDIT')

    def generate_mirrored_pymesh(self, context=None):
        if not context:
            context = bpy.context
        self.reset_vertices(context)

        if self.mirror and self.meshchache_m1:
            print('get chache Mirrored')
            return self.meshchache_m1
        elif not self.mirror and self.meshchache_m0:
            print('get chache')
            return self.meshchache_m0
        elif self.mirror:
            dm, me_dm, dm_me = get_mirrored_mesh(context.scene, context.object)
            pymesh = PyMesh(dm)
            bpy.data.meshes.remove(dm)
            self.meshchache_m1 = pymesh
            for v in pymesh.vertices:
                v.original_index = dm_me[v.index]
        else:
            pymesh = PyMesh(context.active_object.data)
            self.meshchache_m0 = pymesh
            for v in pymesh.vertices:
                v.original_index = v.index
        for v in pymesh.vertices:
            v.no = Vector()
        for e in pymesh.edges:
            e.no = Vector()
        #pymesh.calc_same_coordinate()
        return pymesh

    def outline_normal(self, edge, face, center_to_edge=None):
        # outlineとedgeが平面ならcenter_to_edgeを返す
        vec1, vec2 = edge.vertices[0].co, edge.vertices[1].co
        if center_to_edge is None:  # 外部でまだ計算していない場合
            v1c = face.center - vec1
            center_to_edge = v1c.project(vec2 - vec1) - v1c
            center_to_edge.normalize()  # == normal
        # normal長を調整
        cvs = [None, None]
        for i, v in enumerate(edge.vertices):
            for e in (e for e in v.edges if e != edge):
                if (e.vertices[0].co - e.vertices[1].co).length > MIN_NUMBER:
                    if not self.usehidden and e.hide:
                        if len(e.faces) == 1:
                            cv = e.vert_another(v)
                            cvs[i] = cv.co
                            break
        if cvs[0] is None and cvs[1] is None:  # 隣接無し。普通は有り得ない
            return center_to_edge
        elif cvs[0] and cvs[1]:  # 2
            if geo.area_tri(vec1, vec2, cvs[1]) >= MIN_NUMBER or \
               geo.area_tri(vec2, cvs[1], cvs[0]) >= MIN_NUMBER:
                edge_normal = geo.normal(vec1, vec2, cvs[1], cvs[0])
            else:
                return center_to_edge
        else:  # 1
            if cvs[0] and geo.area_tri(cvs[0], vec1, vec2):
                edge_normal = geo.normal(cvs[0], vec1, vec2)
            elif cvs[1] and geo.area_tri(vec1, vec2, cvs[1]):
                edge_normal = geo.normal(vec1, vec2, cvs[1])
            else:
                return center_to_edge
        if edge_normal.dot(center_to_edge) < 0.0:
            edge_normal.negate()
        angle = center_to_edge.angle(edge_normal)
        if math.pi / 2 - angle >= self.threthold:  # 平行でない
            center_to_edge /= math.cos(angle)
        return edge_normal

    def edge_normal_by_two_faces(self, edge, fa1, fa2):
        if (fa1.normal + fa2.normal).length < MIN_NUMBER:
            return None
        else:
            no = (fa1.normal + fa2.normal).normalized()
            angle = fa1.normal.angle(fa2.normal)
            if angle < self.threthold:
                return None
            else:
                if math.cos(angle / 2):
                    no /= math.cos(angle / 2)
                return no

    def calc_normal_mode_all(self, edge):
        faces = [f for f in edge.faces_no_ex if f.f1]
        if len(faces) == 1:
            face = faces[0]
            if face.area == 0.0:
                edge.f1 = False
            else:
                edge.no = face.normal.copy()
        elif len(faces) == 2:
            fa1, fa2 = faces
            if fa1.area < MIN_NUMBER and fa2.area < MIN_NUMBER:
                edge.f1 = False
            elif fa1.area < MIN_NUMBER:
                edge.no = fa2.normal.copy()
            elif fa2.area < MIN_NUMBER:
                edge.no = fa1.normal.copy()
            else:
                no = self.edge_normal_by_two_faces(edge, fa1, fa2)
                if no is None:
                    edge.f1 = False
                else:
                    edge.no = no
        else:
            edge.f1 = False

    def calc_normal_mode_sel(self, edge):
        faces = [f for f in edge.faces_no_ex if f.f1]
        if len(faces) == 1:
            face = faces[0]
            if face.area < MIN_NUMBER:
                edge.f1 = False
            elif len([f for f in edge.faces if f.f1]) == 2:
                # 押し出し時の元のエッジに対する処理。問題あり？
                if face.select:
                    edge.no = face.normal.copy()
                else:
                    edge.f1 = False
            else:
                '''
                if face.select:
                    edge.no = face.normal.copy()
                else:
                    edge.no = self.outline_normal(edge, face)
                '''
                # outline_normal()はdeselの方で使うからここではいいか
                edge.no = face.normal.copy()
                edge.f2 = True
        elif len(faces) == 2:
            fa1, fa2 = faces
            fa1_available = fa1.select and fa1.area >= MIN_NUMBER
            fa2_available = fa2.select and fa2.area >= MIN_NUMBER
            if fa1_available and fa2_available:
                no = self.edge_normal_by_two_faces(edge, fa1, fa2)
                if no is None:
                    edge.f1 = False
                else:
                    edge.no = no
            elif fa1_available:
                edge.no = fa1.normal.copy()
                edge.f2 = True
            elif fa2_available:
                edge.no = fa2.normal.copy()
                edge.f2 = True
            else:
                edge.f1 = False
        else:
            edge.f1 = False

    def calc_normal_mode_desel(self, edge):
        faces = [f for f in edge.faces_no_ex if f.f1]
        if len(faces) == 1:
            face = faces[0]
            if face.area < MIN_NUMBER:
                edge.f1 = False
            elif face.select:
                edge.f1 = False  # 保留
            else:
                v1, v2 = edge.vertices[0].co, edge.vertices[1].co
                v1c = face.center - v1
                center_to_edge = v1c.project(v2 - v1) - v1c
                center_to_edge.normalize()  # == normal
                # 長さ調整
                edge.no = self.outline_normal(edge, face, center_to_edge)
                edge.f2 = True
        elif len(faces) == 2:
            fa1, fa2 = faces
            faces_available = [f for f in faces if f.area >= MIN_NUMBER]
            if len(faces_available) == 0:
                edge.f1 = False
            elif len(faces_available) == 1:
                # 未確定
                face = faces_available[0]
                #edge.no = face.normal.copy()
                if face.select:
                    edge.f1 = False
                else:
                    edge.no = face.normal.copy()
                    edge.f2 = True  # ここでは不要か？
            else:
                if fa1.select and fa2.select:
                    no = self.edge_normal_by_two_faces(edge, fa1, fa2)
                    if no is None:
                        edge.f1 = False
                    else:
                        edge.no = no
                elif fa1.select or fa2.select:
                    if fa1.select:
                        face_sel, face_desel = fa1, fa2
                    else:
                        face_sel, face_desel = fa2, fa1
                    proj = face_sel.normal.project(face_desel.normal)
                    if (face_sel.normal - proj).length < MIN_NUMBER or \
                       face_sel.normal.angle(face_desel.normal) < MIN_NUMBER:
                        # どうするか未定
                        #edge.f1 = False
                        edge.no = face_sel.normal.copy()
                    else:
                        no = (face_sel.normal - proj).normalized()
                        angle = face_sel.normal.angle(no)
                        edge.no = no / math.cos(angle)
                        edge.f2 = True
                else:
                    edge.f1 = False
        else:
            edge.f1 = False

    def calc_normal(self, context):
        '''
        face.f1: type:Bool. hideを除去
        edge.f1: type:Bool, 最初にedgeの長さによって判定
        vert.f1: type:Bool, executeで適用する頂点。
        edge.faces_no_ex: type:List 押しだし直後に生成された面を無視したリスト
        '''
        pymesh = self.pymesh

        # 初期化
        for face in pymesh.faces:
            if not self.usehidden and face.hide:
                face.f1 = False
            else:
                face.f1 = True
        for edge in pymesh.edges:
            edge.no.zero()
            edge.f1 = (edge.vertices[0].co - edge.vertices[1].co).length > MIN_NUMBER
            edge.faces_no_ex = []  # area<MIN_NUMBERをExtrude後とみなす。例外が予想される。
            for face in edge.faces:
                if len(face.vertices) == 4 and face.area < MIN_NUMBER:
                    e = face.edges[face.edges.index(edge) - 2]
                    fs = [f for f in e.faces if f != face]
                    edge.faces_no_ex.extend(fs)
                else:
                    edge.faces_no_ex.append(face)
            edge.f2 = False  # outlineを優先するフラグ
        for vert in pymesh.vertices:  #(v for v in pymesh.vertices if v.no):
            vert.no.zero()
            vert.f1 = False

        # calc edge normal and length
        for edge in (e for e in pymesh.edges if e.f1):
            if self.outlinemode == 'all':
                self.calc_normal_mode_all(edge)
            elif self.outlinemode == 'sel':
                self.calc_normal_mode_sel(edge)
            else:
                self.calc_normal_mode_desel(edge)

        # calc vertex normal and length
        for vert in (v for v in pymesh.vertices if v.is_selected):
            seq = [e for e in vert.edges if e.f1]
            if len(seq) == 0:
                vert.no = vert.normal.copy()  # 面が非選択の場合でも動作する...
            elif len(seq) == 1:
                vert.no = seq[0].no.copy()
            else:
                if self.precedeoutline:
                    outlines = [e for e in seq if e.f2]
                    if len(outlines) == 2:
                        seq = outlines
                vec = Vector()
                i = 0
                for e1, e2 in combinations(seq, 2):
                    v1, v2 = e1.vertices
                    if v1 != vert:
                        v1, v2 = v2, v1
                    v3, v4 = e2.vertices
                    if v3 != vert:
                        v3, v4 = v4, v3
                    vec1 = v1.co + e1.no
                    vec2 = v2.co + e1.no
                    vec3 = v3.co + e2.no
                    vec4 = v4.co + e2.no
                    if (vec1 - vec2).angle((vec4 - vec3)) < self.threthold2:
                        closest = (vec1 + vec3) / 2
                    else:
                        closestpoints = geo.intersect_line_line(vec1, vec2,
                                                          vec3, vec4)
                        if closestpoints:
                            closest = (closestpoints[0] + closestpoints[1]) / 2
                        else:
                            closest = (vec1 + vec3) / 2
                    vec += closest
                    i += 1
                vec /= i
                vert.no = vec - vert.co
            vert.f1 = True

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        changed = self.watchprop.update()
        if changed:
            if 'mirror' in changed:
                self.pymesh = self.generate_mirrored_pymesh(context)
            self.calc_normal(context)
            op_prop_values.update(self)

        scene = context.scene
        ob = context.active_object
        me = ob.data
        pymesh = self.pymesh
        dist = self.dist

        #for vert, pyvert in zip(me.vertices, pymesh.vertices):
        #    if pyvert.f1:
        for pyvert in pymesh.vertices:
            if pyvert.f1 and pyvert.original_index is not None:
                vert = me.vertices[pyvert.original_index]
                lock = self.lock
                if True not in lock:
                    vert.co = pyvert.co + pyvert.no * dist
                else:
                    vec = pyvert.no * dist
                    vec = Vector([vec[i] * int(not lock[i]) for i in range(3)])
                    vert.co = pyvert.co + vec
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

    def modal(self, context=None, event=None):
        inputexp = self.mc.inputexp  # handling_eventで更新されるため、ここで取得

        handled, execute_immediately = self.mc.handling_event(context, event)
        if execute_immediately:
            self.execute(context)
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}

        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
        region = context.region
        sx, sy = region.width, region.height
        if 0 <= mouseco[0] <= sx and 0 <= mouseco[1] <= sy:
            inregion = True
        else:
            inregion = False

        shortcut_name = check_shortcuts(self.shortcuts, event)

        if shortcut_name == 'mirror':
            self.mirror = not self.mirror
        elif shortcut_name == 'normal':
            self.normalbyselected = not self.normalbyselected
        elif shortcut_name == 'outlinemode+':
            modes = ('all', 'sel', 'desel', 'all')
            self.outlinemode = modes[modes.index(self.outlinemode) + 1]
        elif shortcut_name == 'outlinemode-':
            modes = ('all', 'sel', 'desel')
            self.outlinemode = modes[modes.index(self.outlinemode) - 1]
        elif shortcut_name == 'precedeoutline':
            self.precedeoutline = not self.precedeoutline
        elif shortcut_name == 'lockx':
            self.lock[0] = not self.lock[0]
        elif shortcut_name == 'locky':
            self.lock[1] = not self.lock[1]
        elif shortcut_name == 'lockz':
            self.lock[2] = not self.lock[2]
        elif shortcut_name == 'fin':
            #if inregion:  # QuadView?
            # <Finish>
            # self.execute(context)  # 不要？
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            return {'FINISHED'}

        if check_shortcuts(self.shortcuts, event, 'cancel'):
            if not inputexp:
                self.reset_vertices(context)
                context.region.callback_remove(self._handle)
                context.area.tag_redraw()
                return {'CANCELLED'}

        if event.type in ('MOUSEMOVE', 'LEFT_SHIFT', 'RIGHT_SHIFT', \
                          'LEFT_CTRL', 'RIGHT_CTRL') or \
           event.value == 'PRESS':
            #if inregion:  # QuadView?
            self.execute(context)
            context.area.tag_redraw()

        if inregion:
            return {'RUNNING_MODAL'}
        else:
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')

        # Save & Load properties
        '''op_prop_values.read(self, ('outlinemode', 'threthold',
                                   'threthold2', 'lock', 'mirror',
                                   'precedeoutline'))
        '''
        op_prop_values.read(self, ('threthold', 'threthold2', 'mirror'))
        self.meshchache_m0 = self.meshchache_m1 = None
        op_prop_values.set(self, 'meshchache_m0', None)
        op_prop_values.set(self, 'meshchache_m1', None)

        # Watch attrs (if changed, recalc normals)
        self.watchprop = WatchProperties(self,
                                         ('outlinemode', 'threthold',
                                          'threthold2','lock', 'mirror',
                                          'precedeoutline'))

        # MouseCoordinate & InputExpression
        shortcuts = [Shortcut('lock', 'MIDDLEMOUSE'),
                     Shortcut('reset', 'R'),
                     Shortcut('mirror', 'M'),
                     Shortcut('outlinemode+', 'WHEELDOWNMOUSE',
                              shift=None, ctrl=None),
                     Shortcut('outlinemode-', 'WHEELUPMOUSE',
                              shift=None, ctrl=None),
                     Shortcut('outlinemode+', 'E', shift=None, ctrl=None),
                     Shortcut('precedeoutline', 'W', shift=None, ctrl=None),
                     Shortcut('lockx', 'X'),
                     Shortcut('locky', 'Y'),
                     Shortcut('lockz', 'Z'),
                     Shortcut('fin', 'LEFTMOUSE', shift=None, ctrl=None),
                     Shortcut('fin', 'RET', shift=None, ctrl=None),
                     Shortcut('fin', 'NUMPAD_ENTER', shift=None, ctrl=None),
                     Shortcut('cancel', 'RIGHTMOUSE'),
                     Shortcut('cancel', 'ESC')]
        self.shortcuts = shortcuts
        self.mc = MouseCoordinate(context, event, expnames=('eval( {exp} )',))
        exptargets = {'dist':[(self.mc, 'dist', self, 'dist', 0.0),
                              (self.mc.exp, 0, self, 'dist', Null())]}
        self.mc.set_exptargets(exptargets)
        self.mc.lock = Vector((event.mouse_region_x + 50,
                               event.mouse_region_y,
                               0.0))  # 最初から負の値を入力できるようにしておく
        self.mc.set_shortcuts(shortcuts)

        # Generate Pymesh, calc Normal
        self.original_coordinats = [v.co.copy() for v in \
                                    context.active_object.data.vertices]
        #t = time.time()
        self.pymesh = self.generate_mirrored_pymesh(context)
        #print(time.time() - t)
        self.calc_normal(context)

        bpy.ops.object.mode_set(mode='EDIT')

        # 3DView ?
        self.region_id = context.region.id
        if context.area.type != 'VIEW_3D':
            '''self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
            '''
            context.area.tag_redraw()
            self.execute(context)
            return {'FINISHED'}
        else:
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(
                                          self.__class__.draw_callback_px,
                                          (self, context), 'POST_PIXEL')
            context.area.tag_redraw()
            return {'RUNNING_MODAL'}


class MESH_OT_va_edge_unbend(bpy.types.Operator):
    ''' Unbend selected vertices path '''
    bl_description = 'Unbend selected edges'
    bl_idname = 'mesh.va_edge_unbend'
    bl_label = 'Unbend Edges'
    bl_options = {'REGISTER', 'UNDO'}

    fac = FloatProperty(name='Factor', description='',
                        default=1.0, soft_min=0.0, soft_max=1.0,
                        subtype='FACTOR', unit='NONE')
    intervaltype = EnumProperty(items=(('ignore', 'Ignore', ''),
                                       ('shrink', 'Shrink', ''),
                                       ('equal', 'Equal', '')),
                                name='Interval', description='',
                                default='ignore')
    lock = BoolVectorProperty(name='Lock Axis', description='Lock axis',
                              default=[False, False, False],
                              subtype='XYZ', size=3)
    locklocal = BoolProperty(name='Local Coordinate', default=True)

    @classmethod
    def poll(cls, context):
        #actob = context.active_object
        #return actob and actob.type == 'MESH' and actob.mode == 'EDIT'
        return context.mode == 'EDIT_MESH'

    def prepare(self, context):
        me = context.active_object.data
        paths = self.paths
        vert_vector = self.vert_vector
        for path in (p for p in paths if len(p) >= 3 and p[0] != p[-1]):
            positions = [0.0]
            for i1, i2 in zip(path, path[1:]):
                vec1, vec2 = me.vertices[i1].co, me.vertices[i2].co
                positions.append(positions[-1] + (vec1 - vec2).length)
            vec1, vec2 = me.vertices[path[0]].co, me.vertices[path[-1]].co
            vec12 = vec2 - vec1
            for i in range(1, len(path)):
                vertco = me.vertices[path[i]].co
                if self.intervaltype == 'ignore':
                    tagvec = vec1 + (vertco - vec1).project(vec12)
                elif self.intervaltype == 'shrink':
                    position = positions[i]
                    tagvec = vec1 + vec12 * (position / positions[-1])
                else:  # equal
                    tagvec = vec1 + vec12 / (len(path) - 1) * i
                vec = tagvec - vertco
                vert_vector[path[i]] = vec

    def execute(self, context=None):
        bpy.ops.object.mode_set(mode='OBJECT')
        if self.intervaltype != self.tmp_intervaltype:
            self.prepare(context)
            self.tmp_intervaltype = self.intervaltype
        fac = self.fac
        lock = self.lock
        actob = context.active_object
        mat = actob.matrix_world
        invmat = mat.inverted()
        me = actob.data
        vert_vector = self.vert_vector
        for i, vec in vert_vector.items():
            vert = me.vertices[i]
            if self.locklocal:
                vecfinal = Vector([vec[j] * float(not lock[j]) for j in \
                                                                     range(3)])
            else:
                vecworld = vec * mat
                vecfinal = Vector([vecworld[j] * float(not lock[j]) for j in \
                                                                     range(3)])
                vecfinal = vecfinal * invmat
            vert.co = vert.co + vecfinal * self.fac
        bpy.ops.object.mode_set(mode='EDIT')
        op_prop_values.update(self, ('intervaltype', 'lock', 'locklocal'))
        return {'FINISHED'}

    def invoke(self, context=None, event=None):
        op_prop_values.read(self, ('intervaltype', 'lock', 'locklocal'))
        bpy.ops.object.mode_set(mode='OBJECT')
        me = context.active_object.data
        self.paths = path_vertices_list(me, select=True, hide=False)
        self.vert_vector = {v.index: Vector() for v in me.vertices if \
                                                       v.select and not v.hide}
        self.tmp_intervaltype = self.intervaltype
        self.prepare(context)
        self.execute(context)
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


# Register
def menu_function(self, context):
    self.layout.operator('mesh.va_edge_unbend',
                         text="Edge Unbend", icon='EDGESEL')

def register():
    bpy.utils.register_module(__name__)

    bpy.types.MESH_MT_vertex_align.append(menu_function)

def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.MESH_MT_vertex_align.remove(menu_function)
    print('unregister')


if __name__ == '__main__':
    register()
