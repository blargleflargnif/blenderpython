bl_info = {
    'name': 'Edge unbend',
    'author': 'chromoly',
    'version': (0, 0, 2),
    'blender': (2, 5, 6),
    'api': 34890,
    'location': 'Search "Unbend Edges"',
    'description': '',
    'warning': '',
    'category': 'Mesh'}

import time
import os
import math
import sys
from functools import reduce
from itertools import combinations  # , permutations

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Euler, Matrix, Quaternion, Vector
from mathutils import geometry as geo
import blf
import bgl

from va_mesh import path_vertices_list, key_edge_dict, vert_verts_dict
from va_utils import SaveProperties

op_prop_values = SaveProperties()

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

    def execute(self, context):
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
        
        setattr(self, "tmp_intervaltype", 0)
        
        self.prepare(context)
        self.execute(context)
        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}


# Register
def menu_function(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator('mesh.va_edge_unbend',
                         text="Edge Unbend", icon='EDGESEL')
    self.layout.separator()

def register():
    bpy.utils.register_module(__name__)

    #bpy.types.MESH_MT_vertex_align.append(menu_function)
    bpy.types.VIEW3D_MT_edit_mesh_edges.prepend(menu_function)

def unregister():
    bpy.utils.unregister_module(__name__)

    #bpy.types.MESH_MT_vertex_align.remove(menu_function)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(menu_function)

if __name__ == '__main__':
    register()
