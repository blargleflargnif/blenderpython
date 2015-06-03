bl_info = {"name": "Parametric Model Generator", "category": "Object"}
# load blender python library
import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty, StringProperty, BoolProperty, CollectionProperty, EnumProperty
from math import radians
import json
import copy
from bpy.app.handlers import persistent



#File path for models
models_file_path = bpy.utils.script_paths()[1].replace('scripts','config/pmg.json')
# dictionary to store all models
models_database = {}
# dictionary to store 1 model

models = {}
# flag for active model
active_model_name = ''
# flag for active face
active_model_face = ''
# model name
update_model_in_progress = False
change_model_name_in_progress = False


def fill_models_database(file_path):
    global models_database
    try:
         with open(file_path, 'r') as f:
             models_database = json.load(f)
             for model_name in models_database:
                 for model in models_database[model_name]:
                    face_list = []
                    for face in models_database[model_name][model]['faces']:
                        face_list.append(face)

                    for face in face_list:
                        models_database[model_name][model]['faces'][int(face)] = models_database[model_name][model]['faces'][face]
                        del models_database[model_name][model]['faces'][face]
         print(models_database)
    except FileNotFoundError:
        models_database = {}
        print('error loading models database')

def draw_model_on_scene(self, context, model_name):
    #change scene to object mode
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        print('object mode')
    except:
        pass
    # save modifiers to dictionary
    try:
        modifiers = {}
        for c, i in enumerate(bpy.data.objects[model_name].modifiers):
            if i.type == 'WIREFRAME':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'thickness': i.thickness,
                    'offset': i.offset,
                    'use_even_offset': i.use_even_offset,
                    'use_relative_offset': i.use_relative_offset,
                    'use_boundary': i.use_boundary,
                    'use_replace': i.use_replace,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                }
            elif i.type == 'MIRROR':
                if i.mirror_object is None:
                    mirror_object_name = None
                else:
                    mirror_object_name = i.mirror_object.name
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'use_x': i.use_x,
                    'use_y': i.use_y,
                    'use_z': i.use_z,
                    'use_clip': i.use_clip,
                    'use_mirror_merge': i.use_mirror_merge,
                    'use_mirror_vertex_groups': i.use_mirror_vertex_groups,
                    'use_mirror_u': i.use_mirror_u,
                    'use_mirror_v': i.use_mirror_v,
                    'merge_threshold': i.merge_threshold,
                    'mirror_object': mirror_object_name,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                }
            elif i.type == 'SUBSURF':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'levels': i.levels,
                    'render_levels': i.render_levels,
                    'subdivision_type': i.subdivision_type,
                    'use_subsurf_uv': i.use_subsurf_uv,
                    'show_render': i.show_render,
                    'show_only_control_edges': i.show_only_control_edges,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                }
            elif i.type == 'BOOLEAN':
                if i.object is None:
                    object_name = None
                else:
                    object_name = i.object.name
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'operation': i.operation,
                    'object': object_name,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                }
            elif i.type == 'BUILD':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'frame_start': i.frame_start,
                    'frame_duration': i.frame_duration,
                    'use_reverse': i.use_reverse,
                    'use_random_order': i.use_random_order,
                    'seed': i.seed,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                }
            elif i.type == 'BEVEL':
                print('BEVEL1')
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'width': i.width,
                    'segments': i.segments,
                    'profile': i.profile,
                    'material': i.material,
                    'use_clamp_overlap': i.use_clamp_overlap,
                    'use_only_vertices': i.use_only_vertices,
                    'limit_method': i.limit_method,
                    'angle_limit': i.angle_limit,
                    'offset_type': i.offset_type,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                }
            elif i.type == 'DECIMATE':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'decimate_type': i.decimate_type,
                    'iterations': i.iterations,
                    'angle_limit': i.angle_limit,
                    'use_dissolve_boundaries': i.use_dissolve_boundaries,
                    'delimit': i.delimit,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                }
            elif i.type == 'EDGE_SPLIT':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'use_edge_angle': i.use_edge_angle,
                    'use_edge_sharp': i.use_edge_sharp,
                    'split_angle': i.split_angle,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                }
            elif i.type == 'MULTIRES':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'levels': i.levels,
                    'sculpt_levels': i.sculpt_levels,
                    'render_levels': i.render_levels,
                    'use_subsurf_uv': i.use_subsurf_uv,
                    'show_only_control_edges': i.show_only_control_edges,
                    'subdivision_type': i.subdivision_type,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                }
            elif i.type == 'REMESH':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'mode': i.mode,
                    'octree_depth': i.octree_depth,
                    'scale': i.scale,
                    'sharpness': i.sharpness,
                    'use_smooth_shade': i.use_smooth_shade,
                    'use_remove_disconnected': i.use_remove_disconnected,
                    'threshold': i.threshold,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                }
            elif i.type == 'SCREW':
                if i.object is None:
                    object_name = None
                else:
                    object_name = i.object.name
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'screw_offset': i.screw_offset,
                    'angle': i.angle,
                    'steps': i.steps,
                    'render_steps': i.render_steps,
                    'use_smooth_shade': i.use_smooth_shade,
                    'axis': i.axis,
                    'object': object_name,
                    'use_object_screw_offset': i.use_object_screw_offset,
                    'use_normal_calculate': i.use_normal_calculate,
                    'use_normal_flip': i.use_normal_flip,
                    'use_stretch_u': i.use_stretch_u,
                    'use_stretch_v': i.use_stretch_v,
                    'iterations': i.iterations,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                }
            elif i.type == 'SKIN':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'branch_smoothing': i.branch_smoothing,
                    'use_smooth_shade': i.use_smooth_shade,
                    'use_x_symmetry': i.use_x_symmetry,
                    'use_y_symmetry': i.use_y_symmetry,
                    'use_z_symmetry': i.use_z_symmetry,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                }
            elif i.type == 'TRIANGULATE':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'quad_method': i.quad_method,
                    'ngon_method': i.ngon_method,
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                }
            elif i.type == 'SOLIDIFY':
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                    'thickness': i.thickness,
                    'thickness_clamp': i.thickness_clamp,
                    'offset': i.offset,
                    'edge_crease_inner': i.edge_crease_inner,
                    'edge_crease_outer': i.edge_crease_outer,
                    'edge_crease_rim': i.edge_crease_rim,
                    'use_even_offset': i.use_even_offset,
                    'use_quality_normals': i.use_quality_normals,
                    'use_flip_normals': i.use_flip_normals,
                    'use_rim': i.use_rim,
                    'use_rim_only': i.use_rim_only,
                }
            elif i.type == 'ARRAY':
                if i.offset_object is None:
                    offset_object_name = None
                else:
                    offset_object_name = i.offset_object.name
                if i.start_cap is None:
                    start_cap_name = None
                else:
                    start_cap_name = i.start_cap.name
                if i.end_cap is None:
                    end_cap_name = None
                else:
                    end_cap_name = i.end_cap.name
                modifiers[c] = {
                    'type': i.type,
                    'name': str(c),
                    'show_render': i.show_render,
                    'show_viewport': i.show_viewport,
                    'show_in_editmode': i.show_in_editmode,
                    'show_on_cage': i.show_on_cage,
                    'fit_type': i.fit_type,
                    'count': i.count,
                    'fit_length': i.fit_length,
                    'curve': i.curve,
                    'use_constant_offset': i.use_constant_offset,
                    'constant_offset_displace_x': i.constant_offset_displace[0],
                    'constant_offset_displace_y': i.constant_offset_displace[1],
                    'constant_offset_displace_z': i.constant_offset_displace[2],
                    'use_relative_offset': i.use_relative_offset,
                    'relative_offset_displace_x': i.relative_offset_displace[0],
                    'relative_offset_displace_y': i.relative_offset_displace[1],
                    'relative_offset_displace_z': i.relative_offset_displace[2],
                    'use_object_offset': i.use_object_offset,
                    'offset_object': offset_object_name,
                    'use_merge_vertices': i.use_merge_vertices,
                    'use_merge_vertices_cap': i.use_merge_vertices_cap,
                    'merge_threshold': i.merge_threshold,
                    'start_cap': start_cap_name,
                    'end_cap': end_cap_name,
                }
        models[model_name]['modifiers'] = modifiers
    except:
        pass
    #remove object with model name if exist
    try:
        bpy.context.scene.objects.active = None
        obj = bpy.context.scene.objects[model_name]
        bpy.data.scenes[0].objects.unlink(obj)
        bpy.data.objects.remove(obj)
    except:
        pass
    #set location, rotation, scale from model face
    dirx = models[model_name]['faces'][0]['dirx']
    diry = models[model_name]['faces'][0]['diry']
    dirz = models[model_name]['faces'][0]['dirz']

    rotx = models[model_name]['faces'][0]['rotx']
    roty = models[model_name]['faces'][0]['roty']
    rotz = models[model_name]['faces'][0]['rotz']

    scalex = models[model_name]['faces'][0]['scalex']
    scaley = models[model_name]['faces'][0]['scaley']
    scalez = models[model_name]['faces'][0]['scalez']

    #create primitive circle and set it location, rotation, scale
    if models[model_name]['type'] == 'circle':
        bpy.ops.mesh.primitive_circle_add(view_align=False,
                                          enter_editmode=True, location=(dirx, diry, dirz))
    else:
        bpy.ops.mesh.primitive_plane_add(view_align=False,
                                         enter_editmode=True, location=(dirx, diry, dirz))
    scale = (scalex, scaley, 1)
    bpy.ops.transform.resize(value=scale)
    bpy.ops.transform.rotate(value=rotx, axis=(1, 0, 0))
    bpy.ops.transform.rotate(value=roty, axis=(0, 1, 0))
    bpy.ops.transform.rotate(value=rotz, axis=(0, 0, 1))
    #set active_object name to model name
    try:
        bpy.context.active_object.name = model_name
    except:
        pass
    # iterate over model faces
    for face in sorted(models[model_name]['faces']):
        if face == 0:
            continue
        # set location, rotation, scale from model face
        dirx = models[model_name]['faces'][face]['dirx']
        diry = models[model_name]['faces'][face]['diry']
        dirz = models[model_name]['faces'][face]['dirz']
        rotx = models[model_name]['faces'][face]['rotx']
        roty = models[model_name]['faces'][face]['roty']
        rotz = models[model_name]['faces'][face]['rotz']

        scalex = models[model_name]['faces'][face]['scalex']
        scaley = models[model_name]['faces'][face]['scaley']
        scalez = models[model_name]['faces'][face]['scalez']

        loc = (dirx, diry, dirz)
        scale = (scalex, scaley, scalez)
        # extrude face
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": loc})
        bpy.ops.transform.resize(value=scale)
        bpy.ops.transform.rotate(value=rotx, axis=(1, 0, 0))
        bpy.ops.transform.rotate(value=roty, axis=(0, 1, 0))
        bpy.ops.transform.rotate(value=rotz, axis=(0, 0, 1))
        # deselect all
    bpy.ops.mesh.select_all(action='TOGGLE')
    # go to object mode
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    # add modifiers to object
    for modifier_name in sorted(models[model_name]['modifiers']):
        mod = models[model_name]['modifiers'][modifier_name]
        modifiers = bpy.data.objects[model_name].modifiers
        if mod['type'] == 'WIREFRAME':
            modifiers.new(type='WIREFRAME', name=mod['name'])
            modifiers[mod['name']].thickness = mod['thickness']
            modifiers[mod['name']].offset = mod['offset']
            modifiers[mod['name']].use_even_offset = mod['use_even_offset']
            modifiers[mod['name']].use_relative_offset = mod['use_relative_offset']
            modifiers[mod['name']].use_boundary = mod['use_boundary']
            modifiers[mod['name']].use_replace = mod['use_replace']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
        elif mod['type'] == 'SUBSURF':
            modifiers.new(type='SUBSURF', name=mod['name'])
            modifiers[mod['name']].levels = mod['levels']
            modifiers[mod['name']].render_levels = mod['render_levels']
            modifiers[mod['name']].subdivision_type = mod['subdivision_type']
            modifiers[mod['name']].use_subsurf_uv = mod['use_subsurf_uv']
            modifiers[mod['name']].show_only_control_edges = mod['show_only_control_edges']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
        elif mod['type'] == 'SOLIDIFY':
            modifiers.new(type='SOLIDIFY', name=mod['name'])
            modifiers[mod['name']].thickness = mod['thickness']
            modifiers[mod['name']].thickness_clamp = mod['thickness_clamp']
            modifiers[mod['name']].offset = mod['offset']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
            modifiers[mod['name']].edge_crease_inner = mod['edge_crease_inner']
            modifiers[mod['name']].edge_crease_outer = mod['edge_crease_outer']
            modifiers[mod['name']].edge_crease_rim = mod['edge_crease_rim']
            modifiers[mod['name']].use_even_offset = mod['use_even_offset']
            modifiers[mod['name']].use_quality_normals = mod['use_quality_normals']
            modifiers[mod['name']].use_flip_normals = mod['use_flip_normals']
            modifiers[mod['name']].use_rim = mod['use_rim']
            modifiers[mod['name']].use_rim_only = mod['use_rim_only']
        elif mod['type'] == 'BUILD':
            modifiers.new(type='BUILD', name=mod['name'])
            modifiers[mod['name']].frame_start = mod['frame_start']
            modifiers[mod['name']].frame_duration = mod['frame_duration']
            modifiers[mod['name']].use_reverse = mod['use_reverse']
            modifiers[mod['name']].use_random_order = mod['use_random_order']
            modifiers[mod['name']].seed = mod['seed']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'DECIMATE':
            modifiers.new(type='DECIMATE', name=mod['name'])
            modifiers[mod['name']].decimate_type = mod['decimate_type']
            modifiers[mod['name']].iterations = mod['iterations']
            modifiers[mod['name']].angle_limit = mod['angle_limit']
            modifiers[mod['name']].use_dissolve_boundaries = mod['use_dissolve_boundaries']
            modifiers[mod['name']].delimit = mod['delimit']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'EDGE_SPLIT':
            modifiers.new(type='EDGE_SPLIT', name=mod['name'])
            modifiers[mod['name']].use_edge_angle = mod['use_edge_angle']
            modifiers[mod['name']].use_edge_sharp = mod['use_edge_sharp']
            modifiers[mod['name']].split_angle = mod['split_angle']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
        elif mod['type'] == 'MULTIRES':
            modifiers.new(type='MULTIRES', name=mod['name'])
            modifiers[mod['name']].levels = mod['levels']
            modifiers[mod['name']].sculpt_levels = mod['sculpt_levels']
            modifiers[mod['name']].render_levels = mod['render_levels']
            modifiers[mod['name']].use_subsurf_uv = mod['use_subsurf_uv']
            modifiers[mod['name']].show_only_control_edges = mod['show_only_control_edges']
            modifiers[mod['name']].subdivision_type = mod['subdivision_type']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'REMESH':
            modifiers.new(type='REMESH', name=mod['name'])
            modifiers[mod['name']].octree_depth = mod['octree_depth']
            modifiers[mod['name']].scale = mod['scale']
            modifiers[mod['name']].sharpness = mod['sharpness']
            modifiers[mod['name']].mode = mod['mode']
            modifiers[mod['name']].use_smooth_shade = mod['use_smooth_shade']
            modifiers[mod['name']].use_remove_disconnected = mod['use_remove_disconnected']
            modifiers[mod['name']].threshold = mod['threshold']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'SCREW':
            modifiers.new(type='SCREW', name=mod['name'])
            modifiers[mod['name']].screw_offset = mod['screw_offset']
            modifiers[mod['name']].angle = mod['angle']
            modifiers[mod['name']].steps = mod['steps']
            modifiers[mod['name']].render_steps = mod['render_steps']
            modifiers[mod['name']].use_smooth_shade = mod['use_smooth_shade']
            modifiers[mod['name']].axis = mod['axis']
            modifiers[mod['name']].use_object_screw_offset = mod['use_object_screw_offset']
            modifiers[mod['name']].use_normal_calculate = mod['use_normal_calculate']
            modifiers[mod['name']].use_normal_flip = mod['use_normal_flip']
            modifiers[mod['name']].use_stretch_u = mod['use_stretch_u']
            modifiers[mod['name']].use_stretch_v = mod['use_stretch_v']
            modifiers[mod['name']].iterations = mod['iterations']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            if mod['object'] is None:
                modifiers[mod['name']].object = None
            else:
                modifiers[mod['name']].object = bpy.data.objects[mod['object']]
        elif mod['type'] == 'SKIN':
            modifiers.new(type='SKIN', name=mod['name'])
            modifiers[mod['name']].branch_smoothing = mod['branch_smoothing']
            modifiers[mod['name']].use_smooth_shade = mod['use_smooth_shade']
            modifiers[mod['name']].use_x_symmetry = mod['use_x_symmetry']
            modifiers[mod['name']].use_y_symmetry = mod['use_y_symmetry']
            modifiers[mod['name']].use_z_symmetry = mod['use_z_symmetry']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'TRIANGULATE':
            modifiers.new(type='TRIANGULATE', name=mod['name'])
            modifiers[mod['name']].quad_method = mod['quad_method']
            modifiers[mod['name']].ngon_method = mod['ngon_method']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
        elif mod['type'] == 'BOOLEAN':
            modifiers.new(type='BOOLEAN', name=mod['name'])
            modifiers[mod['name']].operation = mod['operation']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            if mod['object'] is None:
                modifiers[mod['name']].object = None
            else:
                modifiers[mod['name']].object = bpy.data.objects[mod['object']]
        elif mod['type'] == 'MIRROR':
            modifiers.new(type='MIRROR', name=mod['name'])
            modifiers[mod['name']].use_x = mod['use_x']
            modifiers[mod['name']].use_y = mod['use_y']
            modifiers[mod['name']].use_z = mod['use_z']
            modifiers[mod['name']].use_clip = mod['use_clip']
            modifiers[mod['name']].use_mirror_merge = mod['use_mirror_merge']
            modifiers[mod['name']].use_mirror_vertex_groups = mod['use_mirror_vertex_groups']
            modifiers[mod['name']].use_mirror_u = mod['use_mirror_u']
            modifiers[mod['name']].use_mirror_v = mod['use_mirror_v']
            modifiers[mod['name']].merge_threshold = mod['merge_threshold']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
            if mod['mirror_object'] is None:
                modifiers[mod['name']].mirror_object = None
            else:
                modifiers[mod['name']].mirror_object = bpy.data.objects[mod['mirror_object']]
        elif mod['type'] == 'BEVEL':
            modifiers.new(type='BEVEL', name=mod['name'])
            modifiers[mod['name']].width = mod['width']
            modifiers[mod['name']].segments = mod['segments']
            modifiers[mod['name']].profile = mod['profile']
            modifiers[mod['name']].material = mod['material']
            modifiers[mod['name']].use_clamp_overlap = mod['use_clamp_overlap']
            modifiers[mod['name']].use_only_vertices = mod['use_only_vertices']
            modifiers[mod['name']].limit_method = mod['limit_method']
            modifiers[mod['name']].angle_limit = mod['angle_limit']
            modifiers[mod['name']].offset_type = mod['offset_type']
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
        elif mod['type'] == 'ARRAY':
            modifiers.new(type='ARRAY', name=mod['name'])
            modifiers[mod['name']].show_render = mod['show_render']
            modifiers[mod['name']].show_in_editmode = mod['show_in_editmode']
            modifiers[mod['name']].show_viewport = mod['show_viewport']
            modifiers[mod['name']].show_on_cage = mod['show_on_cage']
            modifiers[mod['name']].fit_type = mod['fit_type']
            modifiers[mod['name']].count = mod['count']
            modifiers[mod['name']].fit_length = mod['fit_length']
            modifiers[mod['name']].curve = mod['curve']
            modifiers[mod['name']].use_constant_offset = mod['use_constant_offset']
            modifiers[mod['name']].constant_offset_displace[0] = mod['constant_offset_displace_x']
            modifiers[mod['name']].constant_offset_displace[1] = mod['constant_offset_displace_y']
            modifiers[mod['name']].constant_offset_displace[2] = mod['constant_offset_displace_z']
            modifiers[mod['name']].use_relative_offset = mod['use_relative_offset']
            modifiers[mod['name']].relative_offset_displace[0] = mod['relative_offset_displace_x']
            modifiers[mod['name']].relative_offset_displace[1] = mod['relative_offset_displace_y']
            modifiers[mod['name']].relative_offset_displace[2] = mod['relative_offset_displace_z']
            modifiers[mod['name']].use_object_offset = mod['use_object_offset']
            if mod['offset_object'] is None:
                modifiers[mod['name']].offset_object = None
            else:
                modifiers[mod['name']].offset_object = bpy.data.objects[mod['offset_object']]
            modifiers[mod['name']].use_merge_vertices = mod['use_merge_vertices']
            modifiers[mod['name']].use_merge_vertices_cap = mod['use_merge_vertices_cap']
            modifiers[mod['name']].merge_threshold = mod['merge_threshold']
            if mod['start_cap'] is None:
                modifiers[mod['name']].start_cap = None
            else:
                modifiers[mod['name']].start_cap = bpy.data.objects[mod['start_cap']]
            if mod['end_cap'] is None:
                modifiers[mod['name']].end_cap = None
            else:
                modifiers[mod['name']].end_cap = bpy.data.objects[mod['end_cap']]


def update_model_properties(self, context):
    global update_model_in_progress
    update_model_in_progress = True
    if active_model_name != '' and active_model_face != '':
        if 'desc' in models[active_model_name]['faces'][active_model_face]:
            context.scene.pm_desc = models[active_model_name]['faces'][active_model_face]['desc']
        else:
            context.scene.pm_desc = ''
        context.scene.pm_dirx = models[active_model_name]['faces'][active_model_face]['dirx']
        context.scene.pm_diry = models[active_model_name]['faces'][active_model_face]['diry']
        context.scene.pm_dirz = models[active_model_name]['faces'][active_model_face]['dirz']
        context.scene.pm_rotx = models[active_model_name]['faces'][active_model_face]['rotx']
        context.scene.pm_roty = models[active_model_name]['faces'][active_model_face]['roty']
        context.scene.pm_rotz = models[active_model_name]['faces'][active_model_face]['rotz']
        context.scene.pm_scalex = models[active_model_name]['faces'][active_model_face]['scalex']
        context.scene.pm_scaley = models[active_model_name]['faces'][active_model_face]['scaley']
        context.scene.pm_scalez = models[active_model_name]['faces'][active_model_face]['scalez']
    update_model_in_progress = False


def change_face_desc(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['desc'] = context.scene.pm_desc


def change_model_dirx(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['dirx'] = round(context.scene.pm_dirx, 2)
            draw_model_on_scene(self, context, active_model_name)


def change_model_diry(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['diry'] = round(context.scene.pm_diry, 2)
            draw_model_on_scene(self, context, active_model_name)


def change_model_dirz(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['dirz'] = round(context.scene.pm_dirz, 2)
            draw_model_on_scene(self, context, active_model_name)


def change_model_rotx(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['rotx'] = context.scene.pm_rotx
            draw_model_on_scene(self, context, active_model_name)


def change_model_roty(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['roty'] = context.scene.pm_roty
            draw_model_on_scene(self, context, active_model_name)


def change_model_rotz(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['rotz'] = context.scene.pm_rotz
            draw_model_on_scene(self, context, active_model_name)


def change_model_scalex(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['scalex'] = round(context.scene.pm_scalex, 2)
            draw_model_on_scene(self, context, active_model_name)


def change_model_scaley(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['scaley'] = round(context.scene.pm_scaley, 2)
            draw_model_on_scene(self, context, active_model_name)


def change_model_scalez(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '':
            models[active_model_name]['faces'][active_model_face]['scalez'] = round(context.scene.pm_scalez, 2)
            draw_model_on_scene(self, context, active_model_name)



def save_model_to_database(self, context):
    if update_model_in_progress is False:
        if active_model_name != '' and active_model_face != '' and bpy.context.scene.pms_name != '':
            global models_database
            model_name = bpy.context.scene.pms_name
            models_database[model_name] = copy.deepcopy(models)
            global models_file_path
            try:
                with open(models_file_path, 'w') as f:
                    json.dump(models_database, f,indent=4)
            except:
                print('Error saving models database')

bpy.types.Scene.export_filepath = bpy.props.StringProperty(
    name="",
    subtype='FILE_PATH',
)
bpy.types.Scene.import_filepath = bpy.props.StringProperty(
    name="",
    subtype='FILE_PATH',
)
# Model name
bpy.types.Scene.pms_name = StringProperty(name='Type name and enter to save current model',
                                          update=save_model_to_database, default='modelName')
# Object name
bpy.types.Scene.pm_name = StringProperty(name='Object name', default='objectName')
# Description of the face
bpy.types.Scene.pm_desc = StringProperty(name='Face description', default='',update=change_face_desc)
# model location x,y,z
bpy.types.Scene.pm_dirx = FloatProperty(name="X", step=10, subtype="DISTANCE",
                                        description="Enter move of X direction", default=0.0, update=change_model_dirx)
bpy.types.Scene.pm_diry = FloatProperty(name="Y", step=10, subtype="DISTANCE",
                                        description="Enter move of Y direction", default=0.0, update=change_model_diry)
bpy.types.Scene.pm_dirz = FloatProperty(name="Z", step=10, subtype="DISTANCE",
                                        description="Enter move of Z direction", default=0.0, update=change_model_dirz)
# model scale x,y,z
bpy.types.Scene.pm_scalex = FloatProperty(name="X scale", min=0.0, max=100.0, step=10,
                                          description="Enter scale of X", default=1.0, update=change_model_scalex)
bpy.types.Scene.pm_scaley = FloatProperty(name="Y scale", min=0.0, max=100.0, step=10,
                                          description="Enter scale of Y", default=1.0, update=change_model_scaley)
bpy.types.Scene.pm_scalez = FloatProperty(name="Z scale", min=0.0, max=100.0, step=10,
                                          description="Enter scale of Z", default=1.0, update=change_model_scalez)
# model rotation x,y,z
bpy.types.Scene.pm_rotx = FloatProperty(name="X rot", step=10, subtype="ANGLE",
                                        min=radians(-360), max=radians(360), description="Enter rotation of X",
                                        default=radians(0), update=change_model_rotx)
bpy.types.Scene.pm_roty = FloatProperty(name="Y rot", step=10, subtype="ANGLE",
                                        min=radians(-360), max=radians(360), description="Enter rotation of Y",
                                        default=radians(0), update=change_model_roty)
bpy.types.Scene.pm_rotz = FloatProperty(name="Z rot", step=10, subtype="ANGLE",
                                        min=radians(-360), max=radians(360), description="Enter rotation of Z",
                                        default=radians(0), update=change_model_rotz)


class RefreshDatabase(bpy.types.Operator):
    bl_label = "Refresh Database"
    bl_idname = "wm.refresh_database"

    def execute(self, context):
        global models_file_path
        fill_models_database(models_file_path)

        return {'FINISHED'}


class ExportModelToFile(bpy.types.Operator):
    bl_label = "Export Model"
    bl_idname = "wm.export_model"

    def execute(self, context):
        with open(context.scene.export_filepath, 'w') as f:
            json.dump(models, f,indent=4)
        return {'FINISHED'}


class ImportModelFromFile(bpy.types.Operator):
    bl_label = "Import Model"
    bl_idname = "wm.import_model"

    def execute(self, context):
        try:
            global models
            #models = pickle.load(open(context.scene.import_filepath, "r"))
            with open(context.scene.import_filepath, 'r') as f:
                models = json.load(f)
                print(models)
            for model in models:
                face_list = []
                for face in models[model]['faces']:
                    face_list.append(face)

                for face in face_list:
                    models[model]['faces'][int(face)] = models[model]['faces'][face]
                    del models[model]['faces'][face]

                draw_model_on_scene(self, context, model)
            global active_model_name
            active_model_name = ''
            global active_model_face
            active_model_face = ''

        except KeyError:
            print('error loading model')
        return {'FINISHED'}


class AddCircleModel(bpy.types.Operator):
    bl_label = "Add Circle"
    bl_idname = "wm.add_circle"

    def execute(self, context):
        models.update({context.scene.pm_name: {'name': context.scene.pm_name, 'modifiers': {},
                                               'type': 'circle', 'faces': {0: {'dirx': 0,
                                                                               'diry': 0,
                                                                               'dirz': 0,
                                                                               'rotx': radians(
                                                                                   0),
                                                                               'roty': radians(
                                                                                   0),
                                                                               'rotz': radians(
                                                                                   0),
                                                                               'scalex': 1,
                                                                               'scaley': 1,
                                                                               'scalez': 1}}}})
        global active_model_name
        active_model_name = context.scene.pm_name
        global active_model_face
        active_model_face = 0
        update_model_properties(self, context)
        draw_model_on_scene(self, context, active_model_name)
        return {'FINISHED'}


class AddPlaneModel(bpy.types.Operator):
    bl_label = "Add Plane"
    bl_idname = "wm.add_plane"

    def execute(self, context):
        models.update({context.scene.pm_name: {'name': context.scene.pm_name, 'modifiers': {},
                                               'type': 'plane', 'faces': {0: {'dirx': 0,
                                                                              'diry': 0,
                                                                              'dirz': 0,
                                                                              'rotx': radians(
                                                                                  0),
                                                                              'roty': radians(
                                                                                  0),
                                                                              'rotz': radians(
                                                                                  0),
                                                                              'scalex': 1,
                                                                              'scaley': 1,
                                                                              'scalez': 1}}}})
        global active_model_name
        active_model_name = context.scene.pm_name
        global active_model_face
        active_model_face = 0
        update_model_properties(self, context)
        draw_model_on_scene(self, context, active_model_name)
        return {'FINISHED'}


class SelectModelName(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.select_model_name"

    text = bpy.props.StringProperty()

    def execute(self, context):
        global change_model_name_in_progress
        change_model_name_in_progress = True
        global active_model_name
        active_model_name = self.text
        global active_model_face
        active_model_face = 0
        update_model_properties(self, context)
        #c
        change_model_name_in_progress = False
        try:
            context.scene.objects.active = bpy.data.objects[active_model_name]
        except:
            pass
        #bpy.ops.mesh.select_all(action='TOGGLE')
        return {'FINISHED'}


class SelectModelFace(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.select_model_face"

    text = bpy.props.StringProperty()

    def execute(self, context):
        self.report({'INFO'}, self.text)
        global active_model_face
        active_model_face = int(self.text)
        update_model_properties(self, context)
        return {'FINISHED'}


class AddNewModelFace(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.add_model_face"

    text = bpy.props.StringProperty()

    def execute(self, context):
        global active_model_name
        i = 1
        while True:
            face_name = i
            if face_name in models[active_model_name]['faces']:
                i += 1
            else:
                models[active_model_name]['faces'][face_name] = {'dirx': 0, 'diry': 0, 'dirz': 0,
                                                                 'rotx': radians(0), 'roty': radians(0),
                                                                 'rotz': radians(0), 'scalex': 1, 'scaley': 1,
                                                                 'scalez': 1}
                global active_model_face
                active_model_face = face_name
                break

        update_model_properties(self, context)
        return {'FINISHED'}


class RemoveModelFace(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.remove_model_face"

    text = bpy.props.StringProperty()

    def execute(self, context):
        global active_model_name
        global active_model_face
        for face in sorted(models[active_model_name]['faces']):
            if face >= active_model_face:
                if (face + 1) in models[active_model_name]['faces']:
                    models[active_model_name]['faces'][face] = models[active_model_name]['faces'][face + 1]
                else:
                    del models[active_model_name]['faces'][face]
                    active_model_face = face - 1

        update_model_properties(self, context)
        draw_model_on_scene(self, context, active_model_name)

        return {'FINISHED'}



class RemoveModel(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.remove_model"

    def execute(self, context):
        global models
        models = {}
        global active_model_name
        active_model_name = ''
        global active_model_face
        active_model_face = ''
        return {'FINISHED'}


class SelectModelFromDatabase(bpy.types.Operator):
    bl_label = "Report"
    bl_idname = "wm.select_model_from_database"

    text = bpy.props.StringProperty()

    def execute(self, context):
        global models
        global models_database
        models = {}
        models = copy.deepcopy(models_database[self.text])
        for model in models:
            draw_model_on_scene(self, context, model)
        global active_model_name
        active_model_name = ''
        global active_model_face
        active_model_face = ''
        return {'FINISHED'}


class SelectModelMenu(bpy.types.Menu):
    bl_idname = "SelectModelMenu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        for model_name in sorted(models_database):
            layout.operator("wm.select_model_from_database", text=model_name).text = model_name
        layout.prop(context.scene, "pms_name")


class SelectFaceMenu(bpy.types.Menu):
    bl_idname = "SelectFaceMenu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        if active_model_name in models:
            faces = models[active_model_name]['faces']
            for face in sorted(faces):
                if 'desc' in faces[face]:
                    layout.operator("wm.select_model_face", text=str(face)+' : '+faces[face]['desc']).text = str(face)
                else:
                    layout.operator("wm.select_model_face", text=str(face)).text = str(face)


@persistent
def load_database(scene):
    fill_models_database(models_file_path)

bpy.app.handlers.load_post.clear()
bpy.app.handlers.load_post.append(load_database)


class ParametricModelGeneratorPanel(bpy.types.Panel):
    bl_idname = "mesh.generate_parametric_model"
    bl_label = "Parametric Model Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Model Generator'

    def draw(self, context):

        layout = self.layout
        row = layout.row()
        box = layout.box()
        row = box.row()
        split = row.split(percentage=0.92, align=True)
        split.menu('SelectModelMenu', text='Local models database')
        # manual refresh local database of models
        split.operator("wm.refresh_database",text="R")
        row = box.row()
        row.operator("wm.remove_model", text="Remove model from panel (Not scene)")
        row = box.row()
        row.prop(context.scene, 'pm_name')
        row = box.row()
        row.operator("wm.add_plane", text="Add Plane")
        row.operator("wm.add_circle", text="Add Circle")
        row = box.row()
        split = row.split(percentage=0.75, align=True)
        split.prop(context.scene, 'export_filepath')
        split.operator("wm.export_model", text="Save Model")
        row = box.row()
        split = row.split(percentage=0.75, align=True)
        split.prop(context.scene, 'import_filepath')
        split.operator("wm.import_model", text="Open Model")
        row = box.row()
        if len(models) > 0:
            row.label('Objects :')
            row = box.row()
        model_nr = 1
        for model in models:
            global active_model_name
            if active_model_name == model:
                row.box().operator("wm.select_model_name", icon='COLOR', text=model).text = model
            else:
                row.box().operator("wm.select_model_name", text=model).text = model
            if model_nr % 3 == 0:
                row = box.row()
            model_nr += 1
        row = box.row()

        if active_model_name in models:
            row.label('Faces ( 0 is base) :')
            row = box.row()
            face_nr = 1
            select_face_text = 'Select face, active face is : ' + str(active_model_face)
            row.menu("SelectFaceMenu", text=select_face_text)
            row = box.row()
            for face in sorted(models[active_model_name]['faces']):
                if face == active_model_face:
                    row.operator("wm.select_model_face", icon='SNAP_FACE', text=str(face)).text = str(face)
                else:
                    row.operator("wm.select_model_face", text=str(face)).text = str(face)
                if face_nr % 8 == 0:
                    row = box.row()
                face_nr += 1

        row = box.row()
        if active_model_name in models:
            row.operator("wm.add_model_face", text="Add new face")
            row = box.row()
            row.prop(context.scene,'pm_desc')
            row = box.row()
            if active_model_face > 0:
                row.operator("wm.remove_model_face", text="Remove active face")
                row = box.row()
        row.prop(context.scene, 'pm_dirx')
        row.prop(context.scene, 'pm_diry')
        row.prop(context.scene, 'pm_dirz')
        row = box.row()
        row.prop(context.scene, 'pm_rotx')
        row.prop(context.scene, 'pm_roty')
        row.prop(context.scene, 'pm_rotz')
        row = box.row()
        row.prop(context.scene, 'pm_scalex')
        row.prop(context.scene, 'pm_scaley')
        row.prop(context.scene, 'pm_scalez')



def register():
    bpy.utils.register_class(ParametricModelGeneratorPanel)
    bpy.utils.register_class(SelectModelFace)
    bpy.utils.register_class(SelectModelName)
    bpy.utils.register_class(AddNewModelFace)
    bpy.utils.register_class(AddPlaneModel)
    bpy.utils.register_class(ExportModelToFile)
    bpy.utils.register_class(ImportModelFromFile)
    bpy.utils.register_class(AddCircleModel)
    bpy.utils.register_class(RemoveModelFace)
    bpy.utils.register_class(SelectModelMenu)
    bpy.utils.register_class(SelectModelFromDatabase)
    bpy.utils.register_class(RemoveModel)
    bpy.utils.register_class(SelectFaceMenu)
    bpy.utils.register_class(RefreshDatabase)


def unregister():
    bpy.utils.unregister_class(ParametricModelGeneratorPanel)
    bpy.utils.unregister_class(AddNewModelFace)
    bpy.utils.unregister_class(SelectModelFace)
    bpy.utils.unregister_class(SelectModelName)
    bpy.utils.unregister_class(AddPlaneModel)
    bpy.utils.unregister_class(ExportModelToFile)
    bpy.utils.unregister_class(ImportModelFromFile)
    bpy.utils.unregister_class(AddCircleModel)
    bpy.utils.unregister_class(RemoveModelFace)
    bpy.utils.unregister_class(SelectModelMenu)
    bpy.utils.unregister_class(SelectModelFromDatabase)
    bpy.utils.unregister_class(RemoveModel)
    bpy.utils.unregister_class(SelectFaceMenu)
    bpy.utils.unregister_class(RefreshDatabase)


if __name__ == "__main__":
    register()
    fill_models_database(models_file_path)
