# GPL # Originals by meta-androcto, Pablo Vazquez, Liero, Richard Wilks

import bpy
import bmesh
from bpy.props import StringProperty, FloatProperty, BoolProperty, FloatVectorProperty

        # add the mesh as an object into the scene with this utility module
from bpy_extras import object_utils

def centro(objetos):
    x = sum([obj.location[0] for obj in objetos])/len(objetos)
    y = sum([obj.location[1] for obj in objetos])/len(objetos)
    z = sum([obj.location[2] for obj in objetos])/len(objetos)
    return (x,y,z)

def object_origin(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [(+0.0, +0.0, +0.0)
             ]

    faces = []

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces

class AddVert(bpy.types.Operator):
    '''Add a Single Vertice to Edit Mode'''
    bl_idname = "mesh.primitive_vert_add"
    bl_label = "Single Vert"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Vert")
        mesh.vertices.add(1)
        
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)
        bpy.ops.object.mode_set(mode = 'EDIT')

        return {'FINISHED'}

class AddEmptyVert(bpy.types.Operator):
    '''Add an Object Origin to Edit Mode'''
    bl_idname = "mesh.primitive_emptyvert_add"
    bl_label = "Empty Object Origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Vert")
        mesh.vertices.add(1)
        
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.delete(type='VERT')

        return {'FINISHED'}

def Add_Symmetrical_Empty():

    bpy.ops.mesh.primitive_plane_add(enter_editmode = True)

    sempty = bpy.context.object
    sempty.name = "SymmEmpty"

    # check if we have a mirror modifier, otherwise add
    if (sempty.modifiers and sempty.modifiers['Mirror']):
        pass
    else:
        bpy.ops.object.modifier_add(type ='MIRROR')

    # Delete all!
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.delete(type ='VERT')

def Add_Symmetrical_Vert():

    bpy.ops.mesh.primitive_plane_add(enter_editmode = True)

    sempty = bpy.context.object
    sempty.name = "SymmVert"

    # check if we have a mirror modifier, otherwise add
    if (sempty.modifiers and sempty.modifiers['Mirror']):
        pass
    else:
        bpy.ops.object.modifier_add(type ='MIRROR')

    # Delete all!
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.merge(type='CENTER')

class AddSymmetricalEmpty(bpy.types.Operator):

    bl_idname = "mesh.primitive_symmetrical_empty_add"
    bl_label = "Add Symmetrical Object Origin"
    bl_description = "Object Origin with a Mirror Modifier for symmetrical modeling"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        mirror = bpy.context.object.modifiers['Mirror']

        layout.prop(mirror,'use_clip', text="Use Clipping")

        layout.label("Mirror Axis")
        row = layout.row(align=True)
        row.prop(mirror, "use_x")
        row.prop(mirror, "use_y")
        row.prop(mirror, "use_z")

    def execute(self, context):
        Add_Symmetrical_Empty()
        return {'FINISHED'}

class AddSymmetricalVert(bpy.types.Operator):

    bl_idname = "mesh.primitive_symmetrical_vert_add"
    bl_label = "Add Symmetrical Origin & Vert"
    bl_description = "Object Origin with a Mirror Modifier for symmetrical modeling"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        mirror = bpy.context.object.modifiers['Mirror']

        layout.prop(mirror,'use_clip', text="Use Clipping")

        layout.label("Mirror Axis")
        row = layout.row(align=True)
        row.prop(mirror, "use_x")
        row.prop(mirror, "use_y")
        row.prop(mirror, "use_z")

    def execute(self, context):
        Add_Symmetrical_Vert()
        return {'FINISHED'}

class P2E(bpy.types.Operator):
    bl_idname = 'object.parent_to_empty'
    bl_label = 'Parent Selected to Empty'
    bl_description = 'Parent selected objects to a new Empty'
    bl_options = {'REGISTER', 'UNDO'}

    nombre = StringProperty(name='', default='OBJECTS', description='Give the empty / group a name')
    grupo = bpy.props.BoolProperty(name='Create Group', default=False, description='Also link objects to a new group')
    cursor = bpy.props.BoolProperty(name='Cursor Location', default=False, description='Add the empty at cursor / selection center')
    renombrar = bpy.props.BoolProperty(name='Rename Objects', default=False, description='Rename child objects')

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.select)

    def draw(self, context):
        layout = self.layout
        layout.prop(self,'nombre')
        column = layout.column(align=True)
        column.prop(self,'grupo')
        column.prop(self,'cursor')
        column.prop(self,'renombrar')

    def execute(self, context):
        objs = bpy.context.selected_objects
        bpy.ops.object.mode_set()
        if self.cursor:
            loc = context.scene.cursor_location
        else:
            loc = centro(objs)
        bpy.ops.object.add(type='EMPTY',location=loc)
        bpy.context.object.name = self.nombre
        if self.grupo:
            bpy.ops.group.create(name=self.nombre)
            bpy.ops.group.objects_add_active()
        for o in objs:
            o.select = True
            if not o.parent:
                    bpy.ops.object.parent_set(type='OBJECT')
            if self.grupo:
                bpy.ops.group.objects_add_active()
            o.select = False
        for o in objs:
            if self.renombrar:
                o.name = self.nombre+'_'+o.name
        return {'FINISHED'}
