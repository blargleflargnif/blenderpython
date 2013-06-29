
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2012 Esteban Tovagliari.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

bl_info = {
    "name": "Appleseed",
    "author": "Joel Daniels",
    "version": (0, 1, 0),
    "blender": (2, 6, 7),
    "location": "Info Header (engine dropdown)",
    "description": "Appleseed integration - this is an unofficial fork of Esteban Tovagliari's addon",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Render"}

import bpy, bl_ui, bl_operators
import math, mathutils
import cProfile, dis
from shutil import copyfile
from datetime import datetime
import os, subprocess, time
from extensions_framework import util as efutil
from bpy_extras.io_utils import ExportHelper, ImportHelper
#from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
#from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, CollectionProperty


#A global list for keeping track of exported textures
textures_set = set()

#--------------------------------------------------------------------------------------------------
# Settings.
#--------------------------------------------------------------------------------------------------

Verbose = False
EnableProfiling = False

script_name = "render_appleseed.py"
def get_version_string():
    return "version " + ".".join(map(str, bl_info["version"]))

#--------------------------------------------------------------------------------------------------
# Generic utilities.
#--------------------------------------------------------------------------------------------------
def realpath(path):
    return os.path.realpath(efutil.filesystem_path(path))
    
def render_init(engine):
    pass


def update_preview(engine, data, scene):
    pass

def render_preview(engine, scene):
    pass


def update_scene( engine, data, scene):
    if os.path.isdir(realpath(scene.appleseed.project_path)):
        proj_name = None
    else:
        proj_name = (scene.appleseed.project_path).split('\\')[-1]
    
def render_scene(engine, scene):
    bpy.ops.appleseed.export()
    DELAY = 0.1

    project_file = realpath(scene.appleseed.project_path)
    render_dir = 'render\\' if scene.appleseed.project_path[-1] == '\\' else '\\render\\' 
    render_output = realpath(scene.appleseed.project_path) + render_dir
    
    width = scene.render.resolution_x
    height = scene.render.resolution_y



    try:
        for item in os.listdir(render_output):
            if item == scene.name + '_' + str(scene.frame_current) + scene.render.file_extension:
                os.remove( render_output + item)
    except:
        pass
    
    #Set filename to render
    filename = scene.name
    
    if not filename.endswith( ".appleseed"):
        filename += ".appleseed"
        
    filename = os.path.join(realpath(scene.appleseed.project_path), filename)
    
    appleseed_exe = "appleseed.cli.exe" if scene.appleseed.renderer_type == 'CLI' else "appleseed.studio.exe"
    
    #Start the Appleseed executable
    if scene.appleseed.renderer_type == 'CLI':
        #Get the absolute path to the executable dir
        cmd = (os.path.realpath(efutil.filesystem_path(scene.appleseed.appleseed_path)) + '\\'+ appleseed_exe, filename, '-o', (render_dir + scene.name + '_' + str(scene.frame_current) + scene.render.file_extension))
    else:    
        cmd = (os.path.realpath(efutil.filesystem_path(scene.appleseed.appleseed_path)) + '\\'+ appleseed_exe, filename)
    print("Rendering with ", cmd[0])
    print("Filename: ", cmd[1])
    cdir = os.path.dirname( project_file)
    process = subprocess.Popen( cmd, cwd = cdir, stdout=subprocess.PIPE)
    
    
    # Wait for the file to be created
    while not os.path.exists( render_output):
        if engine.test_break():
            try:
                process.kill()
            except:
                pass
            break

        if process.poll() != None:
            engine.update_stats("", "Appleseed: Error")
            break

        time.sleep( DELAY)

    if os.path.exists(render_output):
        engine.update_stats("", "Appleseed: Rendering")

        prev_size = -1

        def update_image():
            result = engine.begin_result( 0, 0, width, height)
            lay = result.layers[0]
            # possible the image wont load early on.
            try:
                lay.load_from_file( render_output + scene.name + '_' + str(scene.frame_current) + scene.render.file_extension)
            except:
                pass

            engine.end_result( result)

        # Update while rendering
        while True:
            if process.poll() != None:
                update_image()
                break

            # user exit
            if engine.test_break():
                try:
                    process.kill()
                except:
                    pass
                break

            # check if the file updated
            new_size = os.path.getsize( render_output)

            if new_size != prev_size:
                update_image()
                prev_size = new_size

            time.sleep( DELAY)

def update_start(engine, data, scene):
    if engine.is_preview:
        update_preview( engine, data, scene)
    else:
        update_scene( engine, data, scene)
        
def render_start(engine, scene):
    if engine.is_preview:
        render_preview( engine, scene)
    else:
        render_scene( engine, scene)


def square(x):
    return x * x

def rad_to_deg(rad):
    return rad * 180.0 / math.pi

def is_black(color):
    return color[0] == 0.0 and color[1] == 0.0 and color[2] == 0.0

def add(color1, color2):
    return [ color1[0] + color2[0], color1[1] + color2[1], color1[2] + color2[2] ]

def mul(color, multiplier):
    return [ color[0] * multiplier, color[1] * multiplier, color[2] * multiplier ]

def scene_enumerator(self, context):
    matches = []
    for scene in bpy.data.scenes:
        matches.append((scene.name, scene.name, ""))
    return matches

def camera_enumerator(self, context):
    return object_enumerator('CAMERA')

def object_enumerator(type):
    matches = []
    for object in bpy.data.objects:
        if object.type == type:
            matches.append((object.name, object.name, ""))
    return matches

def sun_enumerator(self, context):
    sun = []
    for object in context.scene.objects:
        if object.type == 'LAMP':
            if object.data.type == 'SUN':
                sun.append((object.name, object.name, ""))
    return sun
                
        
def texture_list(self, context):
    tex_list = [('0', '', '')]      #0 is a default, so there are no RNA warnings 
    for tex in context.object.active_material.texture_slots:
        if tex:
            if tex.use:
                if tex.texture.type == 'IMAGE' and tex.uv_layer != '' and tex.texture_coords == 'UV' and tex.texture.image.name != '':
                    tex_list.append((tex.name, tex.name, ''))
    return tex_list    
#--------------------------------------------------------------------------------------------------
# Material-related utilities.
#--------------------------------------------------------------------------------------------------

class MatUtils:
    @staticmethod
    def compute_reflection_factor(material):
        return material.raytrace_mirror.reflect_factor if material.raytrace_mirror.use else 0.0

    @staticmethod
    def is_material_reflective(material):
        return MatUtils.compute_reflection_factor(material) > 0.0

    @staticmethod
    def compute_transparency_factor(material):
        material_transp_factor = (1.0 - material.alpha) if material.use_transparency else 0.0
        # We don't really support the Fresnel parameter yet, hack something together...
        material_transp_factor += material.raytrace_transparency.fresnel / 3.0
        return material_transp_factor

    @staticmethod
    def is_material_transparent(material):
        return MatUtils.compute_transparency_factor(material) > 0.0


#--------------------------------------------------------------------------------------------------
# Write a mesh object to disk in Wavefront OBJ format.
#--------------------------------------------------------------------------------------------------

def get_array2_key(v):
    return int(v[0] * 1000000), int(v[1] * 1000000)

def get_vector2_key(v):
    w = v * 1000000
    return int(w.x), int(w.y)

def get_vector3_key(v):
    w = v * 1000000
    return int(w.x), int(w.y), int(w.z)

def write_mesh_to_disk(mesh, mesh_faces, mesh_uvtex, filepath):
    with open(filepath, "w") as output_file:
        # Write file header.
        output_file.write("# File generated by %s %s.\n" % (script_name, get_version_string()))

        vertices = mesh.vertices
        faces = mesh_faces
        uvtex = mesh_uvtex
        uvset = uvtex.active.data if uvtex else None

        # Sort the faces by material.
        sorted_faces = [ (index, face) for index, face in enumerate(faces) ]
        sorted_faces.sort(key = lambda item: item[1].material_index)

        # Write vertices.
        output_file.write("# %d vertices.\n" % len(vertices))
        for vertex in vertices:
            v = vertex.co
            output_file.write("v %.15f %.15f %.15f\n" % (v.x, v.y, v.z))

        # Deduplicate and write normals.
        output_file.write("# Vertex normals.\n")
        normal_indices = {}
        vertex_normal_indices = {}
        face_normal_indices = {}
        current_normal_index = 0
        for face_index, face in sorted_faces:
            if face.use_smooth:
                for vertex_index in face.vertices:
                    vn = vertices[vertex_index].normal
                    vn_key = get_vector3_key(vn)
                    if vn_key in normal_indices:
                        vertex_normal_indices[vertex_index] = normal_indices[vn_key]
                    else:
                        output_file.write("vn %.15f %.15f %.15f\n" % (vn.x, vn.y, vn.z))
                        normal_indices[vn_key] = current_normal_index
                        vertex_normal_indices[vertex_index] = current_normal_index
                        current_normal_index += 1
            else:
                vn = face.normal
                vn_key = get_vector3_key(vn)
                if vn_key in normal_indices:
                    face_normal_indices[face_index] = normal_indices[vn_key]
                else:
                    output_file.write("vn %.15f %.15f %.15f\n" % (vn.x, vn.y, vn.z))
                    normal_indices[vn_key] = current_normal_index
                    face_normal_indices[face_index] = current_normal_index
                    current_normal_index += 1

        # Deduplicate and write texture coordinates.
        if uvset:
            output_file.write("# Texture coordinates.\n")
            vt_indices = {}
            vertex_texcoord_indices = {}
            current_vt_index = 0
            for face_index, face in sorted_faces:
                assert len(uvset[face_index].uv) == len(face.vertices)
                for vt_index, vt in enumerate(uvset[face_index].uv):
                    vertex_index = face.vertices[vt_index]
                    vt_key = get_array2_key(vt)
                    if vt_key in vt_indices:
                        vertex_texcoord_indices[face_index, vertex_index] = vt_indices[vt_key]
                    else:
                        output_file.write("vt %.15f %.15f\n" % (vt[0], vt[1]))
                        vt_indices[vt_key] = current_vt_index
                        vertex_texcoord_indices[face_index, vertex_index] = current_vt_index
                        current_vt_index += 1

        mesh_parts = []

        # Write faces.
        output_file.write("# %d faces.\n" % len(sorted_faces))
        current_material_index = -1
        for face_index, face in sorted_faces:
            if current_material_index != face.material_index:
                current_material_index = face.material_index
                mesh_name = "part_%d" % current_material_index
                mesh_parts.append((current_material_index, mesh_name))
                output_file.write("o {0}\n".format(mesh_name))
            line = "f"
            if uvset and len(uvset[face_index].uv) > 0:
                if face.use_smooth:
                    for vertex_index in face.vertices:
                        texcoord_index = vertex_texcoord_indices[face_index, vertex_index]
                        normal_index = vertex_normal_indices[vertex_index]
                        line += " %d/%d/%d" % (vertex_index + 1, texcoord_index + 1, normal_index + 1)
                else:
                    normal_index = face_normal_indices[face_index]
                    for vertex_index in face.vertices:
                        texcoord_index = vertex_texcoord_indices[face_index, vertex_index]
                        line += " %d/%d/%d" % (vertex_index + 1, texcoord_index + 1, normal_index + 1)
            else:
                if face.use_smooth:
                    for vertex_index in face.vertices:
                        normal_index = vertex_normal_indices[vertex_index]
                        line += " %d//%d" % (vertex_index + 1, normal_index + 1)
                else:
                    normal_index = face_normal_indices[face_index]
                    for vertex_index in face.vertices:
                        line += " %d//%d" % (vertex_index + 1, normal_index + 1)
            output_file.write(line + "\n")

        return mesh_parts
    

#--------------------------------------------------------------------------------------------------
# AppleseedExportOperator class.
#--------------------------------------------------------------------------------------------------

class AppleseedExportOperator(bpy.types.Operator):
    bl_idname = "appleseed.export"
    bl_label = "Export"

    
    selected_scene = bpy.props.EnumProperty(name="Scene",
                                            description="Select the scene to export",
                                            items=scene_enumerator)

    selected_camera = bpy.props.EnumProperty(name="Camera",
                                             description="Select the camera to export",
                                             items=camera_enumerator)





    point_lights_exitance_mult = bpy.props.FloatProperty(name="Point Lights Energy Multiplier",
                                                         description="Multiply the exitance of point lights by this factor",
                                                         min=0.0,
                                                         max=1000.0,
                                                         default=1.0,
                                                         subtype='FACTOR')

    spot_lights_exitance_mult = bpy.props.FloatProperty(name="Spot Lights Energy Multiplier",
                                                        description="Multiply the exitance of spot lights by this factor",
                                                        min=0.0,
                                                        max=1000.0,
                                                        default=1.0,
                                                        subtype='FACTOR')

    light_mats_exitance_mult = bpy.props.FloatProperty(name="Light-Emitting Materials Energy Multiplier",
                                                       description="Multiply the exitance of light-emitting materials by this factor",
                                                       min=0.0,
                                                       max=1000.0,
                                                       default=1.0,
                                                       subtype='FACTOR')

    env_exitance_mult = bpy.props.FloatProperty(name="Environment Energy Multiplier",
                                                description="Multiply the exitance of the environment by this factor",
                                                min=0.0,
                                                max=1000.0,
                                                default=1.0,
                                                subtype='FACTOR')

    specular_mult = bpy.props.FloatProperty(name="Specular Components Multiplier",
                                            description="Multiply the intensity of specular components by this factor",
                                            min=0.0,
                                            max=1000.0,
                                            default=1.0,
                                            subtype='FACTOR')


    recompute_vertex_normals = bpy.props.BoolProperty(name="Recompute Vertex Normals",
                                                      description="If checked, vertex normals will be recomputed during tessellation",
                                                      default=True)



    # Transformation matrix applied to all entities of the scene.
    global_scale = 0.1
    global_matrix = mathutils.Matrix.Scale(global_scale, 4)

    def execute(self, context):
        if EnableProfiling:
            dis.dis(get_vector3_key)
            cProfile.runctx("self.export()", globals(), locals())
        else: 
            global textures_set
            textures_set.clear()
            scene = context.scene
            self.export(scene)
            
        return { 'FINISHED' }


    def __get_selected_scene(self):
        if self.selected_scene is not None and self.selected_scene in bpy.data.scenes:
            return bpy.data.scenes[self.selected_scene]
        else: return None

    def __get_selected_camera(self):
        if self.selected_camera is not None and self.selected_camera in bpy.data.objects:
            return bpy.data.objects[self.selected_camera]
        else: return None

    def export(self, scene):
        #scene = self.__get_selected_scene()

        if scene is None:
            self.__error("No scene to export.")
            return

        # Blender material -> front material name, back material name.
        self._emitted_materials = {}

        # Object name -> instance count.
        self._instance_count = {}

        # Object name -> (material index, mesh name).
        self._mesh_parts = {}

        file_path = os.path.splitext(realpath(scene.appleseed.project_path) + '\\' + scene.name)[0] + ".appleseed"

        self.__info("")
        self.__info("Starting export of scene '{0}' to {1}...".format(scene.name, file_path))

        start_time = datetime.now()

        try:
            with open(file_path, "w") as self._output_file:
                self._indent = 0
                self.__emit_file_header()
                self.__emit_project(scene)
        except IOError:
            self.__error("Could not write to {0}.".format(file_path))
            return

        elapsed_time = datetime.now() - start_time
        self.__info("Finished exporting in {0}".format(elapsed_time))
        

    def __emit_file_header(self):
        self.__emit_line("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        self.__emit_line("<!-- File generated by {0} {1}. -->".format(script_name, get_version_string()))

    def __emit_project(self, scene):
        self.__open_element("project")
        self.__emit_scene(scene)
        self.__emit_output(scene)
        self.__emit_configurations(scene)
        self.__close_element("project")

    #----------------------------------------------------------------------------------------------
    # Scene.
    #----------------------------------------------------------------------------------------------

    def __emit_scene(self, scene):
        self.__open_element("scene")
        self.__emit_camera(scene)
        self.__emit_environment(scene)
        self.__emit_assembly(scene)
        self.__emit_assembly_instance_element(scene)
        self.__close_element("scene")

    def __emit_assembly(self, scene):
        self.__open_element('assembly name="' + scene.name + '"')
        self.__emit_physical_surface_shader_element()
        self.__emit_default_material(scene)
        self.__emit_objects(scene)
        self.__close_element("assembly")

    def __emit_assembly_instance_element(self, scene):
        self.__open_element('assembly_instance name="' + scene.name + '_instance" assembly="' + scene.name + '"')
        self.__close_element("assembly_instance")

    def __emit_objects(self, scene):
        inscenelayer = lambda o:scene.layers[next((i for i in range(len(o.layers)) if o.layers[i]))]
        for object in scene.objects:
            if inscenelayer(object) and not object.hide:            
                # Skip objects marked as non-renderable.
                if object.hide_render:
                    if Verbose:
                        self.__info("Skipping object '{0}' because it is marked as non-renderable.".format(object.name))
                    continue
    
                # Skip cameras since they are exported separately.
                if object.type == 'CAMERA':
                    if Verbose:
                        self.__info("Skipping object '{0}' because its type is '{1}'.".format(object.name, object.type))
                    continue
    
                if object.type == 'LAMP':
                    self.__emit_light(scene, object)
                else:
                    self.__emit_geometric_object(scene, object)

    #----------------------------------------------------------------------------------------------
    # Camera.
    #----------------------------------------------------------------------------------------------

    def __emit_camera(self, scene):
        camera = self.__get_selected_camera()

        if camera is None:
            self.__warning("No camera in the scene, exporting a default camera.")
            self.__emit_default_camera_element()
            return

        render = scene.render

        film_width = camera.data.sensor_width / 1000
        aspect_ratio = self.__get_frame_aspect_ratio(render)
        lens_unit = "focal_length" if camera.data.lens_unit == 'MILLIMETERS' else "horizontal_fov"
        focal_length = camera.data.lens / 1000.0                # Blender's camera focal length is expressed in mm
        fov = math.degrees(camera.data.angle)
        

        camera_matrix = self.global_matrix * camera.matrix_world
        origin = camera_matrix.col[3]
        forward = -camera_matrix.col[2]
        up = camera_matrix.col[1]
        target = origin + forward
        
        if camera.data.dof_object is not None:
            cam_target = bpy.data.objects[camera.data.dof_object.name]
            focal_distance = (cam_target.location - camera.location).magnitude * 0.1
        else:
            focal_distance = camera.data.dof_distance * 0.1
        
        cam_model = scene.appleseed.camera_type
        self.__open_element('camera name="' + camera.name + '" model="{}_camera"'.format(cam_model))
        if cam_model == "thinlens":
            self.__emit_parameter("f_stop", scene.appleseed.camera_dof)
            self.__emit_parameter("focal_distance", focal_distance)
        self.__emit_parameter("film_width", film_width)
        self.__emit_parameter("aspect_ratio", aspect_ratio)
        self.__emit_parameter(lens_unit, focal_length if camera.data.lens_unit == 'MILLIMETERS' else fov)
        self.__open_element("transform")
        self.__emit_line('<look_at origin="{0} {1} {2}" target="{3} {4} {5}" up="{6} {7} {8}" />'.format( \
                         origin[0], origin[2], -origin[1],
                         target[0], target[2], -target[1],
                         up[0], up[2], -up[1]))
        self.__close_element("transform")
        self.__close_element("camera")

    def __emit_default_camera_element(self):
        self.__open_element('camera name="camera" model="pinhole_camera"')
        self.__emit_parameter("film_width", 0.024892)
        self.__emit_parameter("film_height", 0.018669)
        self.__emit_parameter("focal_length", 0.035)
        self.__close_element("camera")
        return

    #----------------------------------------------------------------------------------------------
    # Environment.
    #----------------------------------------------------------------------------------------------

    def __emit_environment(self, scene):    
        horizon_exitance = [ 0.0, 0.0, 0.0 ]
        zenith_exitance = [ 0.0, 0.0, 0.0 ]

        # Add the contribution of the first hemi light found in the scene.
        found_hemi_light = False
        for object in scene.objects:
            if object.hide_render:
                continue
            if object.type == 'LAMP' and object.data.type == 'HEMI':
                if not found_hemi_light:
                    self.__info("Using hemi light '{0}' for environment lighting.".format(object.name))
                    hemi_exitance = mul(object.data.color, object.data.energy)
                    horizon_exitance = add(horizon_exitance, hemi_exitance)
                    zenith_exitance = add(zenith_exitance, hemi_exitance)
                    found_hemi_light = True
                else:
                    self.__warning("Ignoring hemi light '{0}', multiple hemi lights are not supported yet.".format(object.name))

        # Add the contribution of the sky.
        if scene.world is not None:
            horizon_exitance = add(horizon_exitance, scene.world.horizon_color)
            zenith_exitance = add(zenith_exitance, scene.world.zenith_color)

        # Emit the environment EDF and environment shader if necessary.
        if is_black(horizon_exitance) and is_black(zenith_exitance) and not scene.appleseed_sky.use_sunsky:
            env_edf_name = ""
            env_shader_name = ""
        else:
            # Emit the exitances.
            self.__emit_solid_linear_rgb_color_element("horizon_exitance", horizon_exitance, self.env_exitance_mult)
            self.__emit_solid_linear_rgb_color_element("zenith_exitance", zenith_exitance, self.env_exitance_mult)

            # Emit the environment EDF.
            env_edf_name = "environment_edf"
            if not scene.appleseed_sky.use_sunsky:
                self.__open_element('environment_edf name="{0}" model="gradient_environment_edf"'.format(env_edf_name))
                self.__emit_parameter("horizon_exitance", "horizon_exitance")
                self.__emit_parameter("zenith_exitance", "zenith_exitance")
                self.__close_element('environment_edf')
            elif scene.appleseed_sky.use_sunsky:
                asr_sky = scene.appleseed_sky
                self.__open_element('environment_edf name="{0}" model="{1}"'.format(env_edf_name, asr_sky.sun_model))
                if asr_sky.sun_model == "hosek_environment_edf":
                    self.__emit_parameter("ground_albedo", asr_sky.ground_albedo)
                self.__emit_parameter("horizon_shift", asr_sky.horiz_shift)
                self.__emit_parameter("luminance_multiplier", asr_sky.luminance_multiplier)
                self.__emit_parameter("saturation_multiplier", asr_sky.saturation_multiplier)
                self.__emit_parameter("sun_phi", asr_sky.sun_phi)
                self.__emit_parameter("sun_theta", asr_sky.sun_theta)
                self.__emit_parameter("turbidity", asr_sky.turbidity)
                self.__emit_parameter("turbidity_max", asr_sky.turbidity_max)
                self.__emit_parameter("turbidity_min", asr_sky.turbidity_min)
                self.__close_element('environment_edf')

            # Emit the environment shader.
            env_shader_name = "environment_shader"
            self.__open_element('environment_shader name="{0}" model="edf_environment_shader"'.format(env_shader_name))
            self.__emit_parameter("environment_edf", env_edf_name)
            self.__close_element('environment_shader')

        # Emit the environment element.
        self.__open_element('environment name="environment" model="generic_environment"')
        if len(env_edf_name) > 0:
            self.__emit_parameter("environment_edf", env_edf_name)
        if len(env_shader_name) > 0:
            self.__emit_parameter("environment_shader", env_shader_name)
        self.__close_element('environment')

    #----------------------------------------------------------------------------------------------
    # Geometry.
    #----------------------------------------------------------------------------------------------

    def __emit_geometric_object(self, scene, object):
        # Print some information about this object in verbose mode.
        if Verbose:
            if object.parent:
                self.__info("------ Object '{0}' (type '{1}') child of object '{2}' ------".format(object.name, object.type, object.parent.name))
            else: self.__info("------ Object '{0}' (type '{1}') ------".format(object.name, object.type))

        # Skip children of dupli objects.
        if object.parent and object.parent.dupli_type in { 'VERTS', 'FACES' }:      # todo: what about dupli type 'GROUP'?
            if Verbose:
                self.__info("Skipping object '{0}' because its parent ('{1}') has dupli type '{2}'.".format(object.name, object.parent.name, object.parent.dupli_type))
            return

        # Create dupli list and collect dupli objects.
        if Verbose:
            self.__info("Object '{0}' has dupli type '{1}'.".format(object.name, object.dupli_type))
        if object.dupli_type != 'NONE':
            object.dupli_list_create(scene)
            dupli_objects = [ (dupli.object, dupli.matrix) for dupli in object.dupli_list ]
            if Verbose:
                self.__info("Object '{0}' has {1} dupli objects.".format(object.name, len(dupli_objects)))
        else:
            dupli_objects = [ (object, object.matrix_world) ]

        # Emit the dupli objects.
        for dupli_object in dupli_objects:
            self.__emit_dupli_object(scene, dupli_object[0], dupli_object[1])

        # Clear dupli list.
        if object.dupli_type != 'NONE':
            object.dupli_list_clear()

    def __emit_dupli_object(self, scene, object, object_matrix):
        # Emit the object the first time it is encountered.
        if object.name in self._instance_count:
            if Verbose:
                self.__info("Skipping export of object '{0}' since it was already exported.".format(object.name))
        else:
            try:
                # Tessellate the object.
                mesh = object.to_mesh(scene, True,'RENDER')

                if hasattr(mesh, 'polygons'):
                    # Blender 2.63 and newer: handle BMesh.
                    mesh.calc_tessface()
                    mesh_faces = mesh.tessfaces
                    mesh_uvtex = mesh.tessface_uv_textures
                else:
                    # Blender 2.62 and older.
                    mesh_faces = mesh.faces
                    mesh_uvtex = mesh.uv_textures
 
                # Write the geometry to disk and emit a mesh object element.
                self._mesh_parts[object.name] = self.__emit_mesh_object(scene, object, mesh, mesh_faces, mesh_uvtex)

                # Delete the tessellation.
                bpy.data.meshes.remove(mesh)
            except RuntimeError:
                self.__info("Skipping object '{0}' of type '{1}' because it could not be converted to a mesh.".format(object.name, object.type))
                return

        # Emit the object instance.
        self.__emit_mesh_object_instance(object, object_matrix, scene)

    def __emit_mesh_object(self, scene, object, mesh, mesh_faces, mesh_uvtex):
        if len(mesh_faces) == 0:
            self.__info("Skipping object '{0}' since it has no faces once converted to a mesh.".format(object.name))
            return []

        mesh_filename = object.name + ".obj"

        if scene.appleseed.generate_mesh_files:
            # Recalculate vertex normals.
            if self.recompute_vertex_normals:
                mesh.calc_normals()

            # Export the mesh to disk.
            self.__progress("Exporting object '{0}' to {1}...".format(object.name, mesh_filename))
            mesh_filepath = os.path.join(os.path.dirname(realpath(scene.appleseed.project_path) + '\\' + scene.name), mesh_filename)
            try:
                mesh_parts = write_mesh_to_disk(mesh, mesh_faces, mesh_uvtex, mesh_filepath)
                if Verbose:
                    self.__info("Object '{0}' exported as {1} meshes.".format(object.name, len(mesh_parts)))
            except IOError:
                self.__error("While exporting object '{0}': could not write to {1}, skipping this object.".format(object.name, mesh_filepath))
                return []
        else:
            # Build a list of mesh parts just as if we had exported the mesh to disk.
            material_indices = set()
            for face in mesh_faces:
                material_indices.add(face.material_index)
            mesh_parts = map(lambda material_index : (material_index, "part_%d" % material_index), material_indices)

        # Emit object.
        self.__emit_object_element(object.name, mesh_filename)

        return mesh_parts

    def __emit_mesh_object_instance(self, object, object_matrix, scene):
        # Emit BSDFs and materials if they are encountered for the first time.
        for material_slot_index, material_slot in enumerate(object.material_slots):
            material = material_slot.material
            if material is None:
                self.__warning("While exporting instance of object '{0}': material slot #{1} has no material.".format(object.name, material_slot_index))
                continue
            if material not in self._emitted_materials:
                self._emitted_materials[material] = self.__emit_material(material, scene)

        # Figure out the instance number of this object.
        if object.name in self._instance_count:
            instance_index = self._instance_count[object.name] + 1
        else:
            instance_index = 0
        self._instance_count[object.name] = instance_index
        if Verbose:
            self.__info("This is instance #{0} of object '{1}', it has {2} material slot(s).".format(instance_index, object.name, len(object.material_slots)))

        # Emit object parts instances.
        for (material_index, mesh_name) in self._mesh_parts[object.name]:
            part_name = "{0}.{1}".format(object.name, mesh_name)
            instance_name = "{0}.instance_{1}".format(part_name, instance_index)
            front_material_name = "__default_material"
            back_material_name = "__default_material"
            if material_index < len(object.material_slots):
                material = object.material_slots[material_index].material
                if material:
                    front_material_name, back_material_name = self._emitted_materials[material]
            self.__emit_object_instance_element(part_name, instance_name, self.global_matrix * object_matrix, front_material_name, back_material_name)

    def __emit_object_element(self, object_name, mesh_filepath):
        self.__open_element('object name="' + object_name + '" model="mesh_object"')
        self.__emit_parameter("filename", mesh_filepath)
        self.__close_element("object")

    def __emit_object_instance_element(self, object_name, instance_name, instance_matrix, front_material_name, back_material_name):
        self.__open_element('object_instance name="{0}" object="{1}"'.format(instance_name, object_name))
        self.__emit_transform_element(instance_matrix)
        self.__emit_line('<assign_material slot="0" side="front" material="{0}" />'.format(front_material_name))
        self.__emit_line('<assign_material slot="0" side="back" material="{0}" />'.format(back_material_name))
        self.__close_element("object_instance")

    #----------------------------------------------------------------------------------------------
    # Materials.
    #----------------------------------------------------------------------------------------------

    def __is_light_emitting_material(self, material, scene):
        #if material.get('appleseed_arealight', False):
        #return True;

        return material.emit > 0.0 and scene.appleseed.export_emitting_obj_as_lights

    def __emit_physical_surface_shader_element(self):
        self.__emit_line('<surface_shader name="physical_surface_shader" model="physical_surface_shader" />')

    def __emit_default_material(self, scene):
        self.__emit_solid_linear_rgb_color_element("__default_material_bsdf_reflectance", [ 0.8 ], 1.0)

        self.__open_element('bsdf name="__default_material_bsdf" model="lambertian_brdf"')
        self.__emit_parameter("reflectance", "__default_material_bsdf_reflectance")
        self.__close_element("bsdf")

        self.__emit_material_element("__default_material", "__default_material_bsdf", "", "physical_surface_shader", scene, "")

    def __emit_material(self, material, scene):
        if Verbose:
            self.__info("Translating material '{0}'...".format(material.name))

        if MatUtils.is_material_transparent(material):
            front_material_name = material.name + "_front"
            back_material_name = material.name + "_back"
            self.__emit_front_material(material, front_material_name, scene)
            self.__emit_back_material(material, back_material_name, scene)
        else:
            front_material_name = material.name
            self.__emit_front_material(material, front_material_name, scene)
            if self.__is_light_emitting_material(material, scene):
                # Assign the default material to the back face if the front face emits light,
                # as we don't want mesh lights to emit from both faces.
                back_material_name = "__default_material"
            else: back_material_name = front_material_name

        return front_material_name, back_material_name

    def __emit_front_material(self, material, material_name, scene):
        bsdf_name = self.__emit_front_material_bsdf_tree(material, material_name, scene)

        if self.__is_light_emitting_material(material, scene):
            edf_name = "{0}_edf".format(material_name)
            self.__emit_edf(material, edf_name)
        else: edf_name = ""

        self.__emit_material_element(material_name, bsdf_name, edf_name, "physical_surface_shader", scene, material)

    def __emit_back_material(self, material, material_name, scene):
        bsdf_name = self.__emit_back_material_bsdf_tree(material, material_name, scene)
        self.__emit_material_element(material_name, bsdf_name, "", "physical_surface_shader", scene, material)

    def __emit_front_material_bsdf_tree(self, material, material_name, scene):
        bsdfs = []

        # Transparent component.
        material_transp_factor = MatUtils.compute_transparency_factor(material)
        if material_transp_factor > 0.0:
            transp_bsdf_name = "{0}|transparent".format(material_name)
            self.__emit_specular_btdf(material, transp_bsdf_name, 'front')
            bsdfs.append([ transp_bsdf_name, material_transp_factor ])

        # Mirror component.
        material_refl_factor = MatUtils.compute_reflection_factor(material)
        if material_refl_factor > 0.0:
            mirror_bsdf_name = "{0}|specular".format(material_name)
            self.__emit_specular_brdf(material, mirror_bsdf_name)
            bsdfs.append([ mirror_bsdf_name, material_refl_factor ])

        # Diffuse/glossy component.
        dg_bsdf_name = "{0}|diffuseglossy".format(material_name)
        if is_black(material.specular_color * material.specular_intensity):
            self.__emit_lambertian_brdf(material, dg_bsdf_name, scene)
            
        else:
            self.__emit_ashikhmin_brdf(material, dg_bsdf_name, scene)
        material_dg_factor = 1.0 - max(material_transp_factor, material_refl_factor)
        bsdfs.append([ dg_bsdf_name, material_dg_factor ])

        return self.__emit_bsdf_blend(bsdfs)

    def __emit_back_material_bsdf_tree(self, material, material_name, scene):
        transp_bsdf_name = "{0}|transparent".format(material_name)
        self.__emit_specular_btdf(material, transp_bsdf_name, 'back')
        return transp_bsdf_name

    def __emit_bsdf_blend(self, bsdfs):
        assert len(bsdfs) > 0

        # Only one BSDF, no blending.
        if len(bsdfs) == 1:
            return bsdfs[0][0]

        # Normalize weights if necessary.
        total_weight = 0.0
        for bsdf in bsdfs:
            total_weight += bsdf[1]
        if total_weight > 1.0:
            for bsdf in bsdfs:
                bsdf[1] /= total_weight

        # The left branch is simply the first BSDF.
        bsdf0_name = bsdfs[0][0]
        bsdf0_weight = bsdfs[0][1]

        # The right branch is a blend of all the other BSDFs (recurse).
        bsdf1_name = self.__emit_bsdf_blend(bsdfs[1:])
        bsdf1_weight = 1.0 - bsdf0_weight

        # Blend the left and right branches together.
        mix_name = "{0}+{1}".format(bsdf0_name, bsdf1_name)
        self.__emit_bsdf_mix(mix_name, bsdf0_name, bsdf0_weight, bsdf1_name, bsdf1_weight)

        return mix_name
    
    
    
    def __emit_lambertian_brdf(self, material, bsdf_name, scene):
        reflectance_name = ""
        diffuse_list = []
        for tex in material.texture_slots:
            if tex:    
                if tex.use:
                    if tex.texture.type == 'IMAGE' and tex.uv_layer != '' and tex.texture.image.name != '':
                        if tex.use_map_color_diffuse:
                            diffuse_list.append(tex.texture.name) 
        if diffuse_list != []:
            #Only add color contribution of first color texture
            reflectance_name = diffuse_list[0] + "_inst"
            print("\nLambertian reflectance name: ", diffuse_list[0])    #DEBUG
            if reflectance_name not in textures_set:
                self.__emit_texture(bpy.data.textures[diffuse_list[0]], False, scene)
                textures_set.add(reflectance_name)
                    
        if reflectance_name == "":            
            reflectance_name = "{0}_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name,
                                                   material.diffuse_color,
                                                   material.diffuse_intensity)

        self.__open_element('bsdf name="{0}" model="lambertian_brdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__close_element("bsdf")
    
    #---------------------------------------------------
    def __emit_ashikhmin_brdf(self, material, bsdf_name, scene):
        diffuse_reflectance_name = ""
        glossy_reflectance_name = ""
        diffuse_list = []
        glossy_list = []
        
        for tex in material.texture_slots:
            if tex:
                if tex.use:
                    if tex.texture.type == 'IMAGE' and tex.uv_layer != '' and tex.texture.image.name != '':
                        if tex.use_map_color_diffuse:
                            diffuse_list.append(tex.texture.name)
                        if tex.use_map_specular:
                            glossy_list.append(tex.texture.name)
        if diffuse_list != []:
            diffuse_reflectance_name = diffuse_list[0] + "_inst"
            if diffuse_reflectance_name not in textures_set:
                self.__emit_texture(bpy.data.textures[diffuse_list[0]], False, scene)
                textures_set.add(diffuse_reflectance_name)
                
        if glossy_list != []:
            glossy_reflectance_name = glossy_list[0] + "_inst"
            if glossy_reflectance_name != diffuse_reflectance_name:
                if glossy_reflectance_name not in textures_set:
                    self.__emit_texture(bpy.data.textures[glossy_list[0]], False, scene)
                    textures_set.add(glossy_reflectance_name)
            else:
                pass
            
        #Make sure we found some textures. If not, default to material color.
        if diffuse_reflectance_name == "":
            diffuse_reflectance_name = "{0}_diffuse_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(diffuse_reflectance_name,
                                                   material.diffuse_color,
                                                   material.diffuse_intensity)
        if glossy_reflectance_name == "":    
            glossy_reflectance_name = "{0}_glossy_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(glossy_reflectance_name,
                                                   material.specular_color,
                                                   material.specular_intensity * self.specular_mult)

        self.__open_element('bsdf name="{0}" model="ashikhmin_brdf"'.format(bsdf_name))
        self.__emit_parameter("diffuse_reflectance", diffuse_reflectance_name)
        self.__emit_parameter("glossy_reflectance", glossy_reflectance_name)
        self.__emit_parameter("shininess_u", material.shininess_u)
        self.__emit_parameter("shininess_v", material.shininess_v)
        self.__close_element("bsdf")

    def __emit_specular_brdf(self, material, bsdf_name):
        reflectance_name = "{0}_reflectance".format(bsdf_name)
        self.__emit_solid_linear_rgb_color_element(reflectance_name, material.mirror_color, 1.0)

        self.__open_element('bsdf name="{0}" model="specular_brdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__close_element("bsdf")

    def __emit_specular_btdf(self, material, bsdf_name, side):
        assert side == 'front' or side == 'back'

        reflectance_name = "{0}_reflectance".format(bsdf_name)
        self.__emit_solid_linear_rgb_color_element(reflectance_name, [ 1.0 ], 1.0)

        transmittance_name = "{0}_transmittance".format(bsdf_name)
        self.__emit_solid_linear_rgb_color_element(transmittance_name, [ 1.0 ], 1.0)

        if material.transparency_method == 'RAYTRACE':
            if side == 'front':
                from_ior = 1.0
                to_ior = material.raytrace_transparency.ior
            else:
                from_ior = material.raytrace_transparency.ior
                to_ior = 1.0
        else:
            from_ior = 1.0
            to_ior = 1.0

        self.__open_element('bsdf name="{0}" model="specular_btdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__emit_parameter("transmittance", transmittance_name)
        self.__emit_parameter("from_ior", from_ior)
        self.__emit_parameter("to_ior", to_ior)
        self.__close_element("bsdf")

    def __emit_bsdf_mix(self, bsdf_name, bsdf0_name, bsdf0_weight, bsdf1_name, bsdf1_weight):
        self.__open_element('bsdf name="{0}" model="bsdf_mix"'.format(bsdf_name))
        self.__emit_parameter("bsdf0", bsdf0_name)
        self.__emit_parameter("weight0", bsdf0_weight)
        self.__emit_parameter("bsdf1", bsdf1_name)
        self.__emit_parameter("weight1", bsdf1_weight)
        self.__close_element("bsdf")

    def __emit_edf(self, material, edf_name):
        self.__emit_diffuse_edf(material, edf_name)

    def __emit_diffuse_edf(self, material, edf_name):
        exitance_name = "{0}_exitance".format(edf_name)
        emit_factor = material.emit if material.emit > 0.0 else 1.0
        self.__emit_solid_linear_rgb_color_element(exitance_name,
                                                   material.diffuse_color,
                                                   emit_factor * self.light_mats_exitance_mult)
        self.__emit_diffuse_edf_element(edf_name, exitance_name)

    def __emit_diffuse_edf_element(self, edf_name, exitance_name):
        self.__open_element('edf name="{0}" model="diffuse_edf"'.format(edf_name))
        self.__emit_parameter("exitance", exitance_name)
        self.__close_element("edf")

    #---------------------------------------------
    #Export textures, if any exist on the material
    def __emit_texture(self, tex, bump_bool, scene):        
            #Check that the image texture does not already exist in the folder
            if tex.image.filepath.split('\\')[-1] not in os.listdir(realpath(scene.appleseed.project_path)):    
                src_path = os.path.realpath(efutil.filesystem_path(tex.image.filepath))
                dest_path = realpath(scene.appleseed.project_path) + '\\' + tex.image.filepath.split('\\')[-1]
                #If not, then copy the image
                copyfile(src_path, dest_path)       
            else:
                pass
            color_space = 'linear_rgb' if tex.image.colorspace_settings.name == 'Linear' else 'srgb'      
            self.__open_element('texture name="{0}" model="disk_texture_2d"'.format(tex.name if bump_bool == False else tex.name + "_bump"))
            self.__emit_parameter("color_space", color_space)
            self.__emit_parameter("filename", tex.image.filepath.split('\\')[-1])
            self.__close_element("texture")
            #Now create texture instance
            self.__emit_texture_instance(tex, bump_bool)

    def __emit_texture_instance(self, texture, bump_bool):
        texture_name = texture.name if bump_bool == False else texture.name + "_bump"
        
        self.__open_element('texture_instance name="{0}_inst" texture="{1}"'.format(texture_name, texture_name))
        self.__emit_parameter("addressing_mode", "wrap" if texture.extension == "REPEAT" else "clamp")
        self.__emit_parameter("filtering_mode", "bilinear")
        self.__close_element("texture_instance")   
        
        
        
    #----------------------------------------------------------#
    #----------------------------------------------------------#   
    #Create the material                                       #
    #----------------------------------------------------------#
    #----------------------------------------------------------#
    def __emit_material_element(self, material_name, bsdf_name, edf_name, surface_shader_name, scene, material):
        
        diffuse_list = []
        glossy_list = []
        bump_list = []
        sss_shader = ""
        
        #Make sure we're not evaluating the default material.
        if material != "":
            print("\nWriting material element for material: ", material.name, '\n')
            #Check if we're using an SSS surface shader
            if material.subsurface_scattering.use == True:
                sss_shader = "fastsss_{0}".format(material.name)
                self.__emit_sss_shader(sss_shader, material.name, scene)   
                print("\nCreating SSS shader for material: ", material.name, "sss shader", sss_shader, '\n') 
            
            for tex in material.texture_slots:
                if tex:
                    if tex.use:
                        if tex.texture.type == 'IMAGE' and tex.uv_layer != '' and tex.texture.image.name != '':
                            if tex.use_map_color_diffuse:
                                diffuse_list.append(tex.texture.name)
                            if tex.use_map_specular:
                                glossy_list.append(tex.texture.name)   
                            if tex.use_map_normal:
                                bump_list.append((tex.texture.name, tex.normal_factor))
            if bump_list != []:
                if bump_list[0][0] not in textures_set:
                    self.__emit_texture(bpy.data.textures[bump_list[0][0]], True, scene)
                    textures_set.add(bump_list[0][0])
                    
        self.__open_element('material name="{0}" model="generic_material"'.format(material_name))
        if len(bsdf_name) > 0:
            self.__emit_parameter("bsdf", bsdf_name)
        if len(edf_name) > 0:
            self.__emit_parameter("edf", edf_name)
        if material != "":      #In case we're evaluating "__default_material"
            if bump_list != []:     
                as_normal_map = bpy.data.textures[bump_list[0][0]].use_normal_map                   
                self.__emit_parameter("bump_amplitude", bump_list[0][1])
                self.__emit_parameter("displacement_map", bump_list[0][0] +"_bump_inst")
                self.__emit_parameter("displacement_method", "normal" if as_normal_map else "bump")
                self.__emit_parameter("normal_map_up", "z")
        else:
            pass
        self.__emit_parameter("surface_shader", sss_shader if sss_shader != "" else surface_shader_name)
        self.__close_element("material")
    
    #-------------------------------------        
    def __emit_sss_shader(self, sss_shader_name, material_name, scene):
        material = bpy.data.materials[material_name]
        
        if material.sss_albedo_use_tex and material.sss_albedo_tex != '0':
            #Then assign the name of the texture to albedo_name
            albedo_name = material.sss_albedo_tex + '_inst'
            #Make sure the texture isn't the same as any of the others before writing texture instance
            if material.sss_albedo_tex != material.diffuse_tex:
                if material.sss_albedo_tex != material.specular_tex:
                    if material.sss_albedo_tex != material.bump_tex:                    
                        self.__emit_texture(bpy.data.textures[material.sss_albedo_tex], scene)
        else:
            self.__emit_solid_linear_rgb_color_element(material_name + "_albedo", material.subsurface_scattering.color, 1.0)
            albedo_name = material_name + "_albedo"
            
        self.__open_element('surface_shader name="{0}" model="fast_sss_surface_shader"'.format(sss_shader_name))
        self.__emit_parameter("albedo", albedo_name)
        self.__emit_parameter("ambient_sss", material.sss_ambient)
        self.__emit_parameter("diffuse", material.sss_diffuse)
        self.__emit_parameter("distortion", material.sss_distortion)
        self.__emit_parameter("light_samples", material.sss_light_samples)
        self.__emit_parameter("occlusion_samples", material.sss_occlusion_samples)
        self.__emit_parameter("power", material.sss_power)
        self.__emit_parameter("scale", material.sss_scale)
        self.__emit_parameter("view_dep_sss", material.sss_view_dep)
        self.__close_element("surface_shader")
    #----------------------------------------------------------------------------------------------
    # Lights.
    #----------------------------------------------------------------------------------------------

    def __emit_light(self, scene, object):
        light_type = object.data.type

        if light_type == 'POINT':
            self.__emit_point_light(scene, object)
        elif light_type == 'SPOT':
            self.__emit_spot_light(scene, object)
        elif light_type == 'HEMI':
            # Handle by the environment handling code.
            pass
        elif light_type == 'SUN' and scene.appleseed_sky.use_sunsky:
            self.__emit_sun_light(scene, object)
        elif light_type == 'SUN' and not scene.appleseed_sky.use_sunsky:
            self.__warning("Sun lamp '{0}' exists in the scene, but sun/sky is not enabled".format(object.name))
        else:
            self.__warning("While exporting light '{0}': unsupported light type '{1}', skipping this light.".format(object.name, light_type))

    def __emit_sun_light(self, scene, lamp):
        environment_edf = "environment_edf"
        self.__open_element('light name="{0}" model="sun_light"'.format(lamp.name))
        self.__emit_parameter("environment_edf", environment_edf)
        self.__emit_parameter("radiance_multiplier", scene.appleseed_sky.radiance_multiplier)
        self.__emit_parameter("turbidity", 4.0)
        self.__emit_transform_element(self.global_matrix * lamp.matrix_world)
        self.__close_element("light")
        
    def __emit_point_light(self, scene, lamp):
        exitance_name = "{0}_exitance".format(lamp.name)
        self.__emit_solid_linear_rgb_color_element(exitance_name, lamp.data.color, lamp.data.energy * self.point_lights_exitance_mult)

        self.__open_element('light name="{0}" model="point_light"'.format(lamp.name))
        self.__emit_parameter("exitance", exitance_name)
        self.__emit_transform_element(self.global_matrix * lamp.matrix_world)
        self.__close_element("light")

    def __emit_spot_light(self, scene, lamp):
        exitance_name = "{0}_exitance".format(lamp.name)
        self.__emit_solid_linear_rgb_color_element(exitance_name, lamp.data.color, lamp.data.energy * self.spot_lights_exitance_mult)

        outer_angle = math.degrees(lamp.data.spot_size)
        inner_angle = (1.0 - lamp.data.spot_blend) * outer_angle

        self.__open_element('light name="{0}" model="spot_light"'.format(lamp.name))
        self.__emit_parameter("exitance", exitance_name)
        self.__emit_parameter("inner_angle", inner_angle)
        self.__emit_parameter("outer_angle", outer_angle)
        self.__emit_transform_element(self.global_matrix * lamp.matrix_world)
        self.__close_element("light")

    #----------------------------------------------------------------------------------------------
    # Output.
    #----------------------------------------------------------------------------------------------

    def __emit_output(self, scene):
        self.__open_element("output")
        self.__emit_frame_element(scene)
        self.__close_element("output")

    def __emit_frame_element(self, scene):
        camera = self.__get_selected_camera()
        width, height = self.__get_frame_resolution(scene.render)
        self.__open_element("frame name=\"beauty\"")
        self.__emit_parameter("camera", "camera" if camera is None else camera.name)
        self.__emit_parameter("resolution", "{0} {1}".format(width, height))
        self.__emit_custom_prop(scene, "color_space", "srgb")
        self.__close_element("frame")

    def __get_frame_resolution(self, render):
        scale = render.resolution_percentage / 100.0
        width = int(render.resolution_x * scale)
        height = int(render.resolution_y * scale)
        return width, height

    def __get_frame_aspect_ratio(self, render):
        width, height = self.__get_frame_resolution(render)
        xratio = width * render.pixel_aspect_x
        yratio = height * render.pixel_aspect_y
        return xratio / yratio

    #----------------------------------------------------------------------------------------------
    # Configurations.
    #----------------------------------------------------------------------------------------------

    def __emit_configurations(self, scene):
        self.__open_element("configurations")
        self.__emit_interactive_configuration_element(scene)
        self.__emit_final_configuration_element(scene)
        self.__close_element("configurations")

    def __emit_interactive_configuration_element(self, scene):
        self.__open_element('configuration name="interactive" base="base_interactive"')
        self.__emit_common_configuration_parameters(scene, "interactive")
        self.__close_element("configuration")

    def __emit_final_configuration_element(self, scene):
        self.__open_element('configuration name="final" base="base_final"')
        self.__emit_common_configuration_parameters(scene, "final")
        self.__open_element('parameters name="generic_tile_renderer"')
        self.__emit_parameter("min_samples", scene.appleseed.sampler_min_samples)
        self.__emit_parameter("max_samples", scene.appleseed.sampler_max_samples)
        self.__close_element("parameters")
        self.__close_element("configuration")

    def __emit_common_configuration_parameters(self, scene, type):
        #Interactive: always use drt
        lighting_engine = 'drt' if type == "interactive" else scene.appleseed.lighting_engine
        
        self.__emit_parameter("lighting_engine", lighting_engine)
        self.__emit_parameter("pixel_renderer", scene.appleseed.pixel_sampler)
        self.__open_element('parameters name="adaptive_pixel_renderer"')
        self.__emit_parameter("enable_diagnostics", scene.appleseed.enable_diagnostics)
        self.__emit_parameter("max_samples", scene.appleseed.sampler_max_samples)
        self.__emit_parameter("min_samples", scene.appleseed.sampler_min_samples)
        self.__emit_parameter("quality", scene.appleseed.quality)
        self.__close_element("parameters")

        self.__open_element('parameters name="uniform_pixel_renderer"')
        self.__emit_parameter("decorrelate_pixels", scene.appleseed.decorrelate_pixels)
        self.__emit_parameter("samples", scene.appleseed.sampler_max_samples)
        self.__close_element("parameters")
        
        self.__open_element('parameters name="{0}"'.format(scene.appleseed.lighting_engine))
        self.__emit_parameter("dl_light_samples", scene.appleseed.dl_light_samples)
        self.__emit_parameter("enable_ibl", "true" if scene.appleseed.ibl_enable else "false")
        self.__emit_parameter("ibl_env_samples", scene.appleseed.ibl_env_samples)
        if scene.appleseed.lighting_engine == 'pt':
            self.__emit_parameter("enable_dl", "true" if scene.appleseed.direct_lighting else "false")
            self.__emit_parameter("enable_caustics", "true" if scene.appleseed.caustics_enable else "false")
            self.__emit_parameter("max_path_length", scene.appleseed.max_bounces)
            self.__emit_parameter("next_event_estimation", "true" if scene.appleseed.next_event_est else "false")
        self.__emit_parameter("rr_min_path_length", scene.appleseed.rr_start)
        self.__close_element('parameters')

    #----------------------------------------------------------------------------------------------
    # Common elements.
    #----------------------------------------------------------------------------------------------

    def __emit_color_element(self, name, color_space, values, alpha, multiplier):
        self.__open_element('color name="{0}"'.format(name))
        self.__emit_parameter("color_space", color_space)
        self.__emit_parameter("multiplier", multiplier)
        self.__emit_line("<values>{0}</values>".format(" ".join(map(str, values))))
        if alpha:
            self.__emit_line("<alpha>{0}</alpha>".format(" ".join(map(str, alpha))))
        self.__close_element("color")

    #
    # A note on color spaces:
    #
    # Internally, Blender stores colors as linear RGB values, and the numeric color values
    # we get from color pickers are linear RGB values, although the color swatches and color
    # pickers show gamma corrected colors. This explains why we pretty much exclusively use
    # __emit_solid_linear_rgb_color_element() instead of __emit_solid_srgb_color_element().
    #

    def __emit_solid_linear_rgb_color_element(self, name, values, multiplier):
        self.__emit_color_element(name, "linear_rgb", values, None, multiplier)

    def __emit_solid_srgb_color_element(self, name, values, multiplier):
        self.__emit_color_element(name, "srgb", values, None, multiplier)

    def __emit_transform_element(self, m):
        #
        # We have the following conventions:
        #
        #   Both Blender and appleseed use right-hand coordinate systems.
        #   Both Blender and appleseed use column-major matrices.
        #   Both Blender and appleseed use pre-multiplication.
        #   In Blender, given a matrix m, m[i][j] is the element at the i'th row, j'th column.
        #
        # The only difference between the coordinate systems of Blender and appleseed is the up vector:
        # in Blender, up is Z+; in appleseed, up is Y+. We can go from Blender's coordinate system to
        # appleseed's one by rotating by +90 degrees around the X axis. That means that Blender objects
        # must be rotated by -90 degrees around X before being exported to appleseed.
        #

        self.__open_element("transform")
        self.__open_element("matrix")
        self.__emit_line("{0} {1} {2} {3}".format( m[0][0],  m[0][1],  m[0][2],  m[0][3]))
        self.__emit_line("{0} {1} {2} {3}".format( m[2][0],  m[2][1],  m[2][2],  m[2][3]))
        self.__emit_line("{0} {1} {2} {3}".format(-m[1][0], -m[1][1], -m[1][2], -m[1][3]))
        self.__emit_line("{0} {1} {2} {3}".format( m[3][0],  m[3][1],  m[3][2],  m[3][3]))
        self.__close_element("matrix")
        self.__close_element("transform")

    def __emit_custom_prop(self, object, prop_name, default_value):
        value = self.__get_custom_prop(object, prop_name, default_value)
        self.__emit_parameter(prop_name, value)

    def __get_custom_prop(self, object, prop_name, default_value):
        if prop_name in object:
            return object[prop_name]
        else:
            return default_value

    def __emit_parameter(self, name, value):
        self.__emit_line("<parameter name=\"" + name + "\" value=\"" + str(value) + "\" />")

    #----------------------------------------------------------------------------------------------
    # Utilities.
    #----------------------------------------------------------------------------------------------

    def __open_element(self, name):
        self.__emit_line("<" + name + ">")
        self.__indent()

    def __close_element(self, name):
        self.__unindent()
        self.__emit_line("</" + name + ">")

    def __emit_line(self, line):
        self.__emit_indent()
        self._output_file.write(line + "\n")

    def __indent(self):
        self._indent += 1

    def __unindent(self):
        assert self._indent > 0
        self._indent -= 1

    def __emit_indent(self):
        IndentSize = 4
        self._output_file.write(" " * self._indent * IndentSize)

    def __error(self, message):
        self.__print_message("error", message)
        self.report({ 'ERROR' }, message)

    def __warning(self, message):
        self.__print_message("warning", message)
        self.report({ 'WARNING' }, message)

    def __info(self, message):
        if len(message) > 0:
            self.__print_message("info", message)
        else: print("")
        self.report({ 'INFO' }, message)

    def __progress(self, message):
        self.__print_message("progress", message)

    def __print_message(self, severity, message):
        max_length = 8  # length of the longest severity string
        padding_count = max_length - len(severity)
        padding = " " * padding_count
        print("{0}{1} : {2}".format(severity, padding, message))
    
    
    
#----------------------------------------------
#RENDER ENGINE/SETTINGS CLASSES
#----------------------------------------------

#----------------------------------------------
#REGISTER RENDER ENGINE
class RenderAppleseed( bpy.types.RenderEngine):
    bl_idname = "APPLESEED"
    bl_label = "Appleseed"
    bl_use_preview = False
    
    def __init__( self):
        render_init(self)


    # final rendering
    def update( self, data, scene):
        update_start( self, data, scene)

    def render( self, scene):
        render_start( self, scene)
        
    #Need a function for rendering animation
#    frame_current = scene.frame_current
#    frame_start = scene.frame_start
#    frame_end = scene.frame_end
#    step = scene.frame_step
#    
#    frame_current = frame_start
#    
#    while frame_current <= frame_end:
#        render_start(self, scene)
#        frame_current += frame_step
        
#-----------------------------------------------------    

class AppleseedRenderSettings( bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed = bpy.props.PointerProperty(
                name = "Appleseed Render Settings",
                description = "Appleseed render settings",
                type = cls
                )
        cls.generate_mesh_files = bpy.props.BoolProperty(name="Write Meshes to Disk",
                                                 description="If unchecked, the mesh files (.obj files) won't be regenerated",
                                                 default=True)
                                                 
        cls.renderer_type = bpy.props.EnumProperty(items = [('CLI', 'Internal', ''), ('GUI', 'External', '')], name = 'Renderer Interface', description = '', default = 'GUI')
                                                    
        cls.appleseed_path = bpy.props.StringProperty(description = "Path to the appleseed executable directory", subtype = 'DIR_PATH')
        cls.project_path = bpy.props.StringProperty(description = "Where to export project files. Rendered images are saved in .\\render", subtype = 'DIR_PATH')                                              
        
        # sampling
        cls.decorrelate_pixels = bpy.props.BoolProperty(name = "Decorrelate Pixels", description = '', default = False)
        
        cls.pixel_filter = bpy.props.EnumProperty( name = "Filter",
                                                    description = "Pixel filter to use",
                                                    items = [ ( "box", "Box", "Box" ),
                                                              ( "gaussian", "Gaussian", "Gaussian"),
                                                              ( "mitchell", "Mitchell", "Mitchell")],
                                                    default = "mitchell")

        cls.filter_size = bpy.props.IntProperty( name = "Filter Size",
                                                 description = "Filter size",
                                                 min = 1,
                                                 max = 64,
                                                 default = 2,
                                                 subtype = 'UNSIGNED')

        cls.pixel_sampler = bpy.props.EnumProperty( name = "Sampler",
                                                    description = "Sampler",
                                                    items = [ ( "uniform", "Uniform", "Uniform" ),
                                                              ( "adaptive", "Adaptive", "Adaptive")],
                                                    default = "adaptive")

        cls.sampler_min_samples = bpy.props.IntProperty( name = "Min Samples",
                                                 description = "Min Samples",
                                                 min = 1,
                                                 max = 1000000,
                                                 default = 2,
                                                 subtype = 'UNSIGNED')

        cls.sampler_max_samples = bpy.props.IntProperty( name = "Max Samples",
                                                 description = "Max Samples",
                                                 min = 1,
                                                 max = 1000000,
                                                 default = 64,
                                                 subtype = 'UNSIGNED')

        cls.sampler_max_contrast = bpy.props.FloatProperty( name = "Max Contrast",
                                                 description = "Max contrast",
                                                 min = 0,
                                                 max = 1000,
                                                 default = 1)

        cls.sampler_max_variation = bpy.props.FloatProperty( name = "Max Variation",
                                                 description = "Max variation",
                                                 min = 0,
                                                 max = 1000,
                                                 default = 1)

        # lighting
        cls.lighting_engine = bpy.props.EnumProperty( name = "Lighting Engine",
                    								 description = "Select the lighting engine to use",
                            						 items = [ ( 'pt', "Path Tracing", "Full Global Illumination"),
                                    						( 'drt', "Distributed Ray Tracing", "Direct Lighting Only")],
                                            		 default = 'pt')

        # drt
        cls.ibl_enable = bpy.props.BoolProperty( name = "Image Based Lighting",
                                            description = "Image based lighting",
                                            default = False)
        cls.caustics_enable = bpy.props.BoolProperty(name = "Caustics",
                                            description = "Caustics",
                                            default = True)
        cls.direct_lighting = bpy.props.BoolProperty(name = "Direct Lighting",
                                            description = "Use direct lighting",
                                            default = True)
        cls.next_event_est = bpy.props.BoolProperty(name = "Next Event Estimation",
                                            description = "Use next event estimation",
                                            default = True)
        cls.max_bounces = bpy.props.IntProperty(name = "Max Bounces",
                                            description = "Max bounces - 0 = Unlimited",
                                            default = 0,
                                            min = 0,
                                            max = 512)
        cls.rr_start = bpy.props.IntProperty(name = "Russian Roulette Start Bounce",
                                            description = "Russian Roulette start bounce",
                                            default = 3,
                                            min = 0,
                                            max = 512)
        cls.dl_light_samples = bpy.props.IntProperty(name = "Direct Lighting Light Samples",
                                            description = "Direct lighting light samples",
                                            default =  1,
                                            min = 0,
                                            max = 512)
        cls.ibl_env_samples = bpy.props.IntProperty(name = "IBL Environment Samples",
                                            description = "Image based lighting environment samples",
                                            default = 1,
                                            min = 0,
                                            max = 512)
                                            
        cls.f_stop = bpy.props.FloatProperty(name = "F-Stop Number",
                                            description = "Camera F-Stop value",
                                            default = 1.0)
        cls.camera_type = bpy.props.EnumProperty(items = [('pinhole', 'Pinhole', 'Pinhole camera - no DoF'),
                                                ('thinlens', 'Thin lens', 'Thin lens - enables DoF')],
                                            name = "Camera type",
                                            description = "Camera lens model",
                                            default = 'thinlens')
        cls.premult_alpha = bpy.props.BoolProperty(name = "Premultiplied Alpha",
                                            description = "Premultiplied alpha",
                                            default = True)
                                            
        cls.camera_dof = bpy.props.FloatProperty(name = "F-stop", description = "Thin lens camera f-stop value", default = 7.0, min = 0.0, max = 32.0, step =3, precision = 1)
        
        cls.export_emitting_obj_as_lights = bpy.props.BoolProperty(name="Export Emitting Objects As Mesh Lights",
                                                           description="Export object with light-emitting materials as mesh (area) lights",
                                                           default=True)
                                                           
        cls.enable_diagnostics = bpy.props.BoolProperty(name = "Enable diagnostics", description = '', default = False)
        
        cls.quality = bpy.props.FloatProperty(name = "Quality", description = '', default = 3.0, min = 0.0, max = 20.0, precision = 3)
        

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.appleseed
        
#-------------------------------------------------------
class AppleseedSunSkySettings( bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed_sky = bpy.props.PointerProperty(
                name = "Appleseed Sun Sky",
                description = "Appleseed Sun Sky Model",
                type = cls)
        cls.use_sunsky = bpy.props.BoolProperty(name = "", description = 'Use Appleseed Sun/Sky', default = False)
                
        cls.sun_theta = bpy.props.FloatProperty(name = "Sun theta angle", description = '', default = 0.0, min = -180, max = 180)
        cls.sun_phi = bpy.props.FloatProperty(name = "Sun phi angle", description = '', default = 0.0, min = -180, max = 180)        
        cls.sun_lamp = bpy.props.EnumProperty(items = sun_enumerator, name = "Sun Lamp", description = "Sun lamp to export")                                    
        
        cls.sun_model = bpy.props.EnumProperty(items = [('hosek_environment_edf', "Hosek-Wilkie", ''),
        ('preetham_environment_edf', "Preetham", '')], name = "Physical sky model", description = "Physical sky model for environment EDF", default = 'hosek_environment_edf')
        
        cls.horiz_shift = bpy.props.FloatProperty(name = "Horizon shift", description = '', default = 0.0, min = -2.0, max = 2.0)
        
        cls.luminance_multiplier = bpy.props.FloatProperty(name = "Sky luminance multiplier", description ='', default = 1.0, min = 0.0, max = 20.0)
        
        cls.radiance_multiplier = bpy.props.FloatProperty(name = "Sun radiance multiplier", description = '', default = 0.05, min = 0.0, max = 1.0)
        
        cls.saturation_multiplier = bpy.props.FloatProperty(name= "Saturation multiplier", description = '', default = 1.0, min = 0.0, max = 10.0)
        
        cls.turbidity = bpy.props.FloatProperty(name = "Turbidity", description = '', default = 4.0, min = 0.0, max = 10.0)
        cls.turbidity_max = bpy.props.FloatProperty(name = "Turbidity max", description = '', default = 6.0, min = 0, max = 10.0)
        cls.turbidity_min = bpy.props.FloatProperty(name = "Turbidity min", description = '', default = 2.0, min = 0, max = 10.0)
        
        cls.ground_albedo = bpy.props.FloatProperty(name = "Ground albedo", description = '', default = 0.3, min = 0.0, max = 1.0)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.appleseed_sky
                
            

######################################################################

# Use some of the existing buttons.

import bl_ui.properties_scene as properties_scene
properties_scene.SCENE_PT_scene.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_audio.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_physics.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_keying_sets.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_keying_set_paths.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_unit.COMPAT_ENGINES.add( 'APPLESEED')
properties_scene.SCENE_PT_custom_props.COMPAT_ENGINES.add( 'APPLESEED')
del properties_scene

import bl_ui.properties_world as properties_world
properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add( 'APPLESEED')
properties_world.WORLD_PT_world.COMPAT_ENGINES.add('APPLESEED')
properties_world.WORLD_PT_preview.COMPAT_ENGINES.add('APPLESEED')
del properties_world

import bl_ui.properties_material as properties_material
properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add( 'APPLESEED')
properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add( 'APPLESEED')
properties_material.MATERIAL_PT_custom_props.COMPAT_ENGINES.add( 'APPLESEED')
del properties_material
        
import bl_ui.properties_texture as properties_texture
properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add( 'APPLESEED')
for member in dir(properties_texture):
        subclass = getattr(bl_ui.properties_texture, member)
        try:
            subclass.COMPAT_ENGINES.add('APPLESEED')
        except:
            pass
del properties_texture

import bl_ui.properties_data_lamp as properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add( 'APPLESEED')
properties_data_lamp.DATA_PT_spot.COMPAT_ENGINES.add( 'APPLESEED')
properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.add('APPLESEED')
properties_data_lamp.DATA_PT_sunsky.COMPAT_ENGINES.add('APPLESEED')
#for member in dir(properties_data_lamp):
#    subclass = getattr(bl_ui.properties_data_lamp, member)
#    try:
#        subclass.COMPAT_ENGINES.add('APPLESEED')
#    except:
#        pass
del properties_data_lamp


import bl_ui.properties_data_camera as properties_data_camera
properties_data_camera.DATA_PT_context_camera.COMPAT_ENGINES.add('APPLESEED')
properties_data_camera.CAMERA_MT_presets.COMPAT_ENGINES.add('APPLESEED')
properties_data_camera.DATA_PT_camera.COMPAT_ENGINES.add('APPLESEED')
properties_data_camera.DATA_PT_camera_display.COMPAT_ENGINES.add('APPLESEED')
properties_data_camera.DATA_PT_lens.COMPAT_ENGINES.add('APPLESEED')
del properties_data_camera

# Enable all existing panels for these contexts
import bl_ui.properties_data_mesh as properties_data_mesh
for member in dir( properties_data_mesh):
    subclass = getattr( properties_data_mesh, member)
    try: subclass.COMPAT_ENGINES.add( 'APPLESEED')
    except: pass
del properties_data_mesh

import bl_ui.properties_object as properties_object
for member in dir( properties_object):
    subclass = getattr( properties_object, member)
    try: subclass.COMPAT_ENGINES.add( 'APPLESEED')
    except: pass
del properties_object

import bl_ui.properties_data_mesh as properties_data_mesh
for member in dir( properties_data_mesh):
    subclass = getattr( properties_data_mesh, member)
    try: subclass.COMPAT_ENGINES.add( 'APPLESEED')
    except: pass
del properties_data_mesh

import bl_ui.properties_particle as properties_particle
for member in dir( properties_particle):
    if member == 'PARTICLE_PT_render': continue

    subclass = getattr( properties_particle, member)
    try: subclass.COMPAT_ENGINES.add( 'APPLESEED')
    except:  pass
del properties_particle
        
        
######################################################################

class AppleseedRenderPanelBase( object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED'

#-----------------------------------
#A class for camera DoF
class AppleseedCameraDoF(bpy.types.Panel):
    bl_label = "Appleseed Depth of Field"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED'}
    bl_context = "data"
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.active_object.type == 'CAMERA'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        
        row = layout.row()
        row.prop(context.active_object.data, "dof_object", text = 'Focal object')

        row = layout.row()
        row.prop(asr_scene_props, "camera_dof", text = "F-stop")
        row.prop(asr_scene_props, "camera_type", text = 'Camera')

        row = layout.row()
        row.prop(context.active_object.data, "dof_distance", text = "Focal distance")
        row.active = context.active_object.data.dof_object is None

#---------------------------------
#A class for World Panel
class AppleseedWorldPanel(bpy.types.Panel):
    bl_label = "Appleseed Sun/Sky"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED'}
    bl_context = "world"
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED'
    
    def draw_header(self, context):
        asr_sky_props = context.scene.appleseed_sky
        header = self.layout
        header.scale_y = 1.0
        header.prop(asr_sky_props, "use_sunsky")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_sky_props = scene.appleseed_sky
        
        layout.active = asr_sky_props.use_sunsky
        
        split = layout.split()
        col = split.column()
        col.label("Sun to export:")
        col.prop(asr_sky_props, "sun_lamp", text = '')
        
        col = split.column()
        col.label("Physical sky model:")
        col.prop(asr_sky_props, "sun_model", text = '')
        
        layout.prop(asr_sky_props, "luminance_multiplier")
        layout.prop(asr_sky_props, "radiance_multiplier")
        layout.prop(asr_sky_props, "saturation_multiplier")
        row = layout.row(align = True)
        row.prop(asr_sky_props, "sun_theta")
        row.prop(asr_sky_props, "sun_phi")
        layout.prop(asr_sky_props, "turbidity")
        row = layout.row(align = True)
        row.prop(asr_sky_props, "turbidity_min")
        row.prop(asr_sky_props, "turbidity_max")
        layout.prop(asr_sky_props, "horiz_shift")
        if asr_sky_props.sun_model == "hosek_environment_edf":
            layout.prop(asr_sky_props, "ground_albedo")
            
#----------------------------------    
#A class for Render buttons panel
class AppleseedRenderButtons(bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Appleseed Render"
    COMPAT_ENGINES = {'APPLESEED'}
    
    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        
        row = layout.row(align=True)
        row.operator("render.render", text = "Render", icon = "RENDER_STILL")
#        row.operator("render.render_animation", text = "Render Animation") 
        row.operator("appleseed.export", text = "Export Only", icon = 'EXPORT')
    
#---------------------------------------------------------------------------    
#Add the dimensions panel
from bl_ui import properties_render
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add( 'APPLESEED')
del properties_render

#---------------------------------------------------------------------------    

class AppleseedRenderSettingsPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Appleseed Render Settings"
    bl_options = {'DEFAULT_CLOSED'}

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        
        layout.prop(asr_scene_props, "renderer_type")
        layout.prop(asr_scene_props, "appleseed_path", text = "Path to Appleseed")
        layout.prop(asr_scene_props, "project_path", text = "Project path")
        layout.prop(asr_scene_props, "generate_mesh_files")
        
        layout.prop(scene.render.image_settings, "file_format")
    
#---------------------------------------------------------------------    
class AppleseedSamplesPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Appleseed Samples"
    COMPAT_ENGINES = {'APPLESEED'}

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column()
        row = col.row( align=True)
        row.prop( asr_scene_props, "pixel_filter")
        row.prop( asr_scene_props, "filter_size")

        col.separator()
        col.prop( asr_scene_props, "pixel_sampler")

        if asr_scene_props.pixel_sampler == 'adaptive':
            col.prop( asr_scene_props, "sampler_min_samples")
            col.prop( asr_scene_props, "sampler_max_samples")
            col.prop( asr_scene_props, "sampler_max_contrast")
            col.prop( asr_scene_props, "sampler_max_variation")
        else:
            col.prop(asr_scene_props, "decorrelate_pixels")
            col.prop( asr_scene_props, "sampler_max_samples")
                        
        col.prop(asr_scene_props, "rr_start")
        
        
        
#--------------------------------------------------------------------------        
class AppleseedLightingPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Appleseed Lighting"
    COMPAT_ENGINES = {'APPLESEED'}

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column()
        col.prop( asr_scene_props, "lighting_engine")
        split = layout.split()

        col.prop(asr_scene_props, "export_emitting_obj_as_lights")        
        if asr_scene_props.lighting_engine == 'pt':
            col = split.column()
            col.prop(asr_scene_props, "caustics_enable")
            col.prop(asr_scene_props, "next_event_est")
            col = split.column()
            col.prop(asr_scene_props, "enable_diagnostics")
            col.prop(asr_scene_props, "quality")
            if asr_scene_props.next_event_est == True:
                row = layout.row()
                row.prop( asr_scene_props, "ibl_enable")
                if asr_scene_props.ibl_enable == True:
                    row.prop(asr_scene_props, "ibl_env_samples")
                row = layout.row()
                row.prop(asr_scene_props, "direct_lighting")
                if asr_scene_props.direct_lighting == True:
                    row.prop(asr_scene_props, "dl_light_samples")
            col = layout.column()
          
        else:
            row = layout.row()
            row.prop(asr_scene_props, "ibl_enable")
            if asr_scene_props.ibl_enable == True:
                row.prop(asr_scene_props, "ibl_env_samples")
            layout.prop(asr_scene_props, "decorrelate_pixels")
        col = layout.column()
        col.prop(asr_scene_props, "max_bounces")  
        
#-------------------------            
class AppleseedMaterialShading(bpy.types.Panel):
    bl_label = 'Appleseed Surface Shading'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED'}
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
    
    
    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        
        split = layout.split(percentage = 0.65)
        col = split.column()
        layout.label("Diffuse Color:")
        layout.prop(material, "diffuse_color", text = "")    
        layout.prop(material, "diffuse_intensity", "Intensity")
        
        layout.separator()    
        split = layout.split(percentage = 0.65)    
        col = split.column()
        layout.label("Specular Color:")
        layout.prop(material, "specular_color", text = "")
        row = layout.row(align = True)
        row.prop(material, "shininess_u", "Shininess U", slider=True)
        row.prop(material, "shininess_v", "Shininess V", slider = True)
        
        layout.separator()
        layout.label("Light emission:")
        layout.prop(material, "emit", text = "Emission strength", slider = True)
        
#----------------------------------------------        
class AppleseedMaterialMirror(bpy.types.Panel):
    bl_label = 'Appleseed Specular Mirror'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED'}
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
    
    def draw_header(self, context):
        material = context.object.active_material
        header = self.layout
        header.scale_y = 1.0
        header.prop(material.raytrace_mirror, "use", text = "")
    
    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        
        layout.active = material.raytrace_mirror.use
        
        split= layout.split()
        col = split.column()
        col.prop(material.raytrace_mirror, "reflect_factor")
        col.prop(material, "mirror_color", text = "")
        
        col = split.column()
        col.prop(material.raytrace_mirror, "fresnel")
        col.prop(material.raytrace_mirror, "fresnel_factor")

#----------------------------------------------------
class AppleseedMaterialTransparency(bpy.types.Panel):
    bl_label = 'Appleseed Transparency'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED'}
        
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None
    
    
    def draw_header(self, context):
        material = context.object.active_material
        header = self.layout
        header.scale_y = 1.0
        header.prop(material, "use_transparency", text = "")
    
    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material    
        
        layout.active = material.use_transparency
        
        row = layout.row()
        row.prop(material, "transparency_method", expand = True)
        if material.transparency_method == 'MASK':
            layout.label("Mask transparency is not supported. Using Z Transparency.")
        elif material.transparency_method == 'Z_TRANSPARENCY':
            layout.label("Using alpha transparency: IOR = 1.0")
            layout.prop(material, "alpha")
        elif material.transparency_method == 'RAYTRACE':
            row = layout.row()
            row.prop(material, "alpha")
            row.prop(material.raytrace_transparency, "fresnel")
            layout.prop(material.raytrace_transparency, "ior")
        
#-------------------------------------------------------
class AppleseedFastSSSPanel(bpy.types.Panel):
    bl_label = "Appleseed Fast Subsurface Scattering"
    COMPAT_ENGINES = {'APPLESEED'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None        
    
    def draw_header(self, context):
        material = context.object.active_material
        header = self.layout
        header.scale_y = 1.0
        header.prop(material.subsurface_scattering, "use", text = "")
        
    def draw(self, context):
        layout = self.layout
        material = context.object.active_material
        layout.active = material.subsurface_scattering.use
        
        split = layout.split()
        col = split.column()
        
        col.prop(material, "sss_power", text = "SSS Power")

        layout.prop(material.subsurface_scattering, "color", text = "Albedo Color")
        
        col = split.column()
        col.prop(material, "sss_scale")
#        col.label("")
#        col.prop(material, "sss_albedo_use_tex", toggle = True, text = "Use Albedo Texture")
#        if material.sss_albedo_use_tex:
#            if texture_list(self, context) != [('0', '', '')]:
#                layout.prop(material, "sss_albedo_tex", text = "Albedo Color Texture")
#            else:
#                col.label("No UV image textures.")
        

        
        split = layout.split()
        col = split.column()
        col.prop(material, "sss_ambient")    
        col.prop(material, "sss_diffuse")    
        col.prop(material, "sss_light_samples")
        
        col = split.column()
        col.prop(material, "sss_view_dep")
        col.prop(material, "sss_distortion")
        col.prop(material, "sss_occlusion_samples")
        
        
#Register the script
#-------------------
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Material.diffuse_tex = bpy.props.EnumProperty(items = texture_list, name = '', description = '')
    bpy.types.Material.specular_tex = bpy.props.EnumProperty(items = texture_list, name = '', description = '')
    bpy.types.Material.bump_tex = bpy.props.EnumProperty(items = texture_list, name = '', description = '')
    bpy.types.Material.use_diffuse_tex = bpy.props.BoolProperty(name = "", description = "Use a texture influence diffuse color", default = False)
    bpy.types.Material.use_specular_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence specular values", default = False)
    bpy.types.Material.use_bump_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence bump / normal", default = False)
    bpy.types.Material.use_normalmap = bpy.props.BoolProperty(name = "", description = "Use as normal map", default = False)
    bpy.types.Material.bump_amplitude  = bpy.props.FloatProperty(name = "Bump Amplitude", description = "Maximum height influence of bump / normal map", default = 1.0, min = 0.0, max = 1.0)
    bpy.types.Material.sss_albedo_tex = bpy.props.EnumProperty(items = texture_list, name = '', description = '')
    bpy.types.Material.sss_albedo_use_tex = bpy.props.BoolProperty(name = "", description = "Use a texture influence SSS color", default = False)
    bpy.types.Material.sss_ambient = bpy.props.FloatProperty(name = "Ambient SSS", description = "Ambient SSS value", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.sss_diffuse = bpy.props.FloatProperty(name = "Diffuse Lighting", description = "", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.sss_distortion = bpy.props.FloatProperty(name = "Normal Distortion", description = "", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.sss_light_samples = bpy.props.IntProperty(name = "Light Samples", description = "", default = 1, min = 0, max = 100)
    bpy.types.Material.sss_occlusion_samples = bpy.props.IntProperty(name = "Occlusion Samples", description = "", default = 1, min = 0, max = 100)
    bpy.types.Material.sss_power = bpy.props.FloatProperty(name = "Power", description = "", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.sss_scale = bpy.props.FloatProperty(name = "Geometric Scale", description = "", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.sss_view_dep = bpy.props.FloatProperty(name = "View-dependent SSS", description = "", default = 1.0, min = 0.0, max = 10.0)
    bpy.types.Material.shininess_u = bpy.props.FloatProperty(name = "Shininess U", description = "", default = 200.0, min = 0.0, max = 1000.0)
    bpy.types.Material.shininess_v = bpy.props.FloatProperty(name = "Shininess V", description = "", default = 200.0, min = 0.0, max = 1000.0)
    
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()