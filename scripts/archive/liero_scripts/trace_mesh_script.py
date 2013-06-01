####################################################################
# creates a curve with a modulated radius joining points of a mesh #
# this emulates some brush traces - maybe work on a copy of object #
####################################################################

ruido_vertices = False  # add pre-noise to geometry
modular_curva = True    # modulate the resulting curve

import bpy, random, mathutils
from mathutils import Vector

# add noise to mesh // modify scale value
def mover(obj):
    scale = 0.05
    for v in obj.data.vertices:
        for u in range(3):
            v.co[u] += scale * (random.random() - .5)

# continuous edge through all vertices
def trazar(obj):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='EDGE_FACE')
    bpy.ops.mesh.select_all(action='DESELECT')
    ver = obj.data.vertices
    bpy.ops.object.mode_set()
    li = []
    p1 = int(random.random() * (1 + len(ver)))
    for v in ver: li.append(v.index)
    li.remove(p1)
    for z in range(len(li)):
        x = 999
        for px in li:
            d = ver[p1].co - ver[px].co
            if d.length < x:
                x = d.length
                p2 = px
        ver[p1].select = ver[p2].select = True
        bpy.ops.object.editmode_toggle()
        bpy.context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.editmode_toggle()
        ver[p1].select = ver[p2].select = False
        li.remove(p2)
        p1 = p2

# convert edges to curve and add a material
def curvar(obj):
    bpy.ops.object.mode_set()
    bpy.ops.object.convert(target='CURVE')
    bpy.ops.object.editmode_toggle()
    bpy.ops.curve.spline_type_set(type='BEZIER')
    bpy.ops.curve.handle_type_set(type='AUTOMATIC')
    bpy.ops.object.editmode_toggle()
    try: obj.data.fill_mode = 'FULL'
    except: obj.data.use_fill_front = obj.data.use_fill_back = False
    obj.data.bevel_resolution = 4
    obj.data.resolution_u = 12
    obj.data.bevel_depth = .0125
    if 'mate' not in bpy.data.materials:
        mate = bpy.data.materials.new('mate')
        mate.diffuse_color = ([.02] * 3)
        mate.specular_intensity = 0
    obj.data.materials.append(bpy.data.materials.get('mate'))

# modulate curve radius // modify scale value
def modular(obj):
    scale = 3
    for u in obj.data.splines:
        for v in u.bezier_points:
            v.radius = scale * round(random.random(),3)

# start the program
obj = bpy.context.object
if obj and obj.type == 'MESH':
    if ruido_vertices: 
        mover(obj)
    trazar (obj)
    curvar(obj)
    if modular_curva: 
        modular(obj)