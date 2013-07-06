#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
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
    "author": "Franz Beaune, Joel Daniels, Esteban Tovagliari",
    "version": (0, 2, 0),
    "blender": (2, 6, 7),
    "location": "Info Header (engine dropdown)",
    "description": "Appleseed integration",
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

#Path separator for the current platform
sep = os.path.sep
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
                
def is_uv_img(tex):
    if tex and tex.type == 'IMAGE' and tex.image:
        return True
    else:
        return False

            
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
        proj_name = (scene.appleseed.project_path).split(sep)[-1]


#Scene render function
#------------------------------    
def render_scene(engine, scene):
    #Export the scene
    bpy.ops.appleseed.export()
    
    DELAY = 0.1
    project_file = realpath(scene.appleseed.project_path)
    render_dir = 'render' + sep if scene.appleseed.project_path[-1] == sep else sep + 'render' + sep 
    render_output = os.path.join(realpath(scene.appleseed.project_path), render_dir)
    width = scene.render.resolution_x
    height = scene.render.resolution_y
    
    #Make the output directory, if it doesn't exist yet
    if not os.path.exists(project_file):
        try:
            os.mkdir(project_file)
        except:
            self.report({"INFO"}, "The project directory cannot be created. Check directory permissions.")
            return
    
    #Make the render directory, if it doesn't exist yet
    if not os.path.exists(render_output):
        try:
            os.mkdir(render_output)
        except:
            self.report({"INFO"}, "The project render directory cannot be created. Check directory permissions.")
            return
            
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
    
    appleseed_exe = "appleseed.cli" if scene.appleseed.renderer_type == 'CLI' else "appleseed.studio"
    
    
    #Start the Appleseed executable 
    if scene.appleseed.renderer_type == "CLI":        
        #Get the absolute path to the executable dir
        cmd = (os.path.join(realpath(scene.appleseed.appleseed_path), appleseed_exe), filename, '-o', (render_output + scene.name + '_' + str(scene.frame_current) + scene.render.file_extension))
        
    elif scene.appleseed.renderer_type == "GUI":
        if not scene.appleseed.new_build_options:
            cmd = (realpath(scene.appleseed.appleseed_path) + sep + appleseed_exe)
        else: 
            if scene.appleseed.interactive_mode:
                cmd = os.path.join(realpath(scene.appleseed.appleseed_path), appleseed_exe) + ' ' + filename + " --render interactive"
            else:
                cmd = os.path.join(realpath(scene.appleseed.appleseed_path), appleseed_exe) + ' ' + filename + " --render final"
            
    print("Rendering:", cmd)
    process = subprocess.Popen(cmd, cwd = render_output, stdout=subprocess.PIPE)
    
    
    #The rendered image name and path
    render_image = render_output + scene.name + '_' + str(scene.frame_current) + scene.render.file_extension
    # Wait for the file to be created
    while not os.path.exists( render_image):
        if engine.test_break():
            try:
                process.kill()
            except:
                pass
            break

        if process.poll() != None:
            engine.update_stats("", "Appleseed: Error")
            break

        time.sleep(DELAY)

    if os.path.exists(render_image):
        engine.update_stats("", "Appleseed: Rendering")

        prev_size = -1

        def update_image():
            result = engine.begin_result( 0, 0, width, height)
            lay = result.layers[0]
            # possible the image wont load early on.
            try:
                lay.load_from_file( render_image)
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
            new_size = os.path.getsize( render_image)

            if new_size != prev_size:
                update_image()
                prev_size = new_size

            time.sleep(DELAY)



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
    def compute_transparency_factor(material, index):
        layer = material.appleseed.layers[index]
        material_transp_factor = 0.0
        if layer.bsdf_type == "specular_btdf":
            material_transp_factor =  layer.spec_btdf_weight
   
                
        return material_transp_factor

    @staticmethod
    def is_material_transparent(material):
        return MatUtils.compute_transparency_factor(material, index) > 0.0


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
    
    textures_set = set()
    
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
            self.textures_set.clear()
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

        file_path = os.path.splitext(realpath(scene.appleseed.project_path) + sep + scene.name)[0] + ".appleseed"

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
            mesh_filepath = os.path.join(os.path.dirname(realpath(scene.appleseed.project_path) + sep  + scene.name), mesh_filename)
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
        self.__emit_object_element(object.name, mesh_filename, object)

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
            self.__emit_object_instance_element(part_name, instance_name, self.global_matrix * object_matrix, front_material_name, back_material_name, object)

    def __emit_object_element(self, object_name, mesh_filepath, object):
        self.__open_element('object name="' + object_name + '" model="mesh_object"')
        self.__emit_parameter("filename", mesh_filepath)
        self.__close_element("object")

    def __emit_object_instance_element(self, object_name, instance_name, instance_matrix, front_material_name, back_material_name, object):
        self.__open_element('object_instance name="{0}" object="{1}"'.format(instance_name, object_name))
        self.__emit_transform_element(instance_matrix)
        self.__emit_line('<assign_material slot="0" side="front" material="{0}" />'.format(front_material_name))
        self.__emit_line('<assign_material slot="0" side="back" material="{0}" />'.format(back_material_name))
        if bool(object.appleseed_render_layer):
            render_layer = object.appleseed_render_layer
            self.__emit_parameter("render_layer", render_layer)
        self.__close_element("object_instance")

    #----------------------------------------------------------------------------------------------
    # Materials.
    #----------------------------------------------------------------------------------------------

    def __is_light_emitting_material(self, material, scene):
        #if material.get('appleseed_arealight', False):
        #return True;
        asr_mat = material.appleseed
        
        return asr_mat.use_light_emission and scene.appleseed.export_emitting_obj_as_lights

    def __emit_physical_surface_shader_element(self):
        self.__emit_line('<surface_shader name="physical_surface_shader" model="physical_surface_shader" />')

    def __emit_default_material(self, scene):
        self.__emit_solid_linear_rgb_color_element("__default_material_bsdf_reflectance", [ 0.8 ], 1.0)

        self.__open_element('bsdf name="__default_material_bsdf" model="lambertian_brdf"')
        self.__emit_parameter("reflectance", "__default_material_bsdf_reflectance")
        self.__close_element("bsdf")

        self.__emit_material_element("__default_material", "__default_material_bsdf", "", "physical_surface_shader", scene, "")

    def __emit_material(self, material, scene):
        asr_mat = material.appleseed
        layers = asr_mat.layers
        front_material_name = ""
        
        if Verbose:
            self.__info("Translating material '{0}'...".format(material.name))
            
        #Need to iterate through layers only once, to find out if we have any specular btdfs
        for layer in layers:
            if layer.bsdf_type == "specular_btdf":
                front_material_name = material.name + "_front"
                back_material_name = material.name + "_back"
                self.__emit_front_material(material, front_material_name, scene, layers)
                self.__emit_back_material(material, back_material_name, scene, layers)
                break
        
        #If we didn't find any, then we're only exporting front material     #DEBUG
        if front_material_name == "":
            front_material_name = material.name
            self.__emit_front_material(material, front_material_name, scene, layers)
            if self.__is_light_emitting_material(material, scene):
                # Assign the default material to the back face if the front face emits light,
                # as we don't want mesh lights to emit from both faces.
                back_material_name = "__default_material"
            else: back_material_name = front_material_name

        return front_material_name, back_material_name

    def __emit_front_material(self, material, material_name, scene, layers):
        #material_name here is material.name + "_front" #DEBUG
        bsdf_name = self.__emit_front_material_bsdf_tree(material, material_name, scene, layers)

        if self.__is_light_emitting_material(material, scene):
            edf_name = "{0}_edf".format(material_name)
            self.__emit_edf(material, edf_name, scene)
        else: edf_name = ""

        self.__emit_material_element(material_name, bsdf_name, edf_name, "physical_surface_shader", scene, material)

    def __emit_back_material(self, material, material_name, scene, layers):
        #material_name here is material.name + "_back" #DEBUG
        bsdf_name = self.__emit_back_material_bsdf_tree(material, material_name, scene, layers)
        self.__emit_material_element(material_name, bsdf_name, "", "physical_surface_shader", scene, material)
    
    
    def __emit_front_material_bsdf_tree(self, material, material_name, scene, layers):
        #material_name here is material.name + "_front" #DEBUG
        bsdfs = []
        asr_mat = material.appleseed
        #Iterate through layers and export their types, append names and weights to bsdfs list
        for layer in layers:
            if layer.bsdf_type == "specular_btdf":
                transp_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_specular_btdf(material, transp_bsdf_name, 'front', layer)
                bsdfs.append([ transp_bsdf_name, layer.spec_btdf_weight ])

            elif layer.bsdf_type == "specular_brdf":
                mirror_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_specular_brdf(material, mirror_bsdf_name, scene, layer)
                bsdfs.append([ mirror_bsdf_name, layer.specular_weight ])

            elif layer.bsdf_type == "diffuse_btdf":   
                dt_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_diffuse_btdf(material, dt_bsdf_name, scene, layer)
                bsdfs.append([ dt_bsdf_name, layer.transmission_weight])
        
            elif layer.bsdf_type == "lambertian_brdf":
                lbrt_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_lambertian_brdf(material, lbrt_bsdf_name, scene, layer)
                bsdfs.append([ lbrt_bsdf_name, layer.lambertian_weight])
            
            elif layer.bsdf_type == "ashikhmin_brdf":
                ashk_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_ashikhmin_brdf(material, ashk_bsdf_name, scene, layer)
                bsdfs.append([ ashk_bsdf_name, layer.ashikhmin_weight ])
                
            elif layer.bsdf_type == "microfacet_brdf":
                mfacet_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_microfacet_brdf(material, mfacet_bsdf_name, scene, layer)
                bsdfs.append([ mfacet_bsdf_name, layer.microfacet_weight])
                
            elif layer.bsdf_type == "kelemen_brdf":
                kelemen_bsdf_name = "{0}|{1}".format(material_name, layer.name)
                self.__emit_kelemen_brdf(material, kelemen_bsdf_name, scene, layer)
                bsdfs.append([ kelemen_bsdf_name, layer.kelemen_weight])
                
            elif not layer:
                default_bsdf_name = "{0}|_default".format(material_name)
                self.__emit_lambertian_brdf(material, default_bsdf_name, scene, layer)
                bsdfs.append([default_bsdf_name, 1.0])
                  
        return self.__emit_bsdf_blend(bsdfs)
    
    #------------------------------------------------------------------------
    
    def __emit_back_material_bsdf_tree(self, material, material_name, scene, layers):
        #material_name = material.name  + "_back"
        #Need to include all instances of spec btdfs - iterate -> layers, find them, add to list
        spec_btdfs = []
        for layer in layers:
            if layer.bsdf_type == "specular_btdf":
                #This is a hack for now; just return the first one we find
                spec_btdfs.append([layer.name, layer.spec_btdf_weight])
                transp_bsdf_name = "{0}|{1}".format(material_name, spec_btdfs[0][0]) 
                
                self.__emit_specular_btdf(material, transp_bsdf_name, 'back', layer)
        

        
        return transp_bsdf_name
    
    #------------------------------------
    
    def __emit_bsdf_blend(self, bsdfs):
        
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
    
    #------------------------------------------------------------
    
    def __emit_lambertian_brdf(self, material, bsdf_name, scene, layer):
        asr_mat = material.appleseed
        
        reflectance_name = ""
        diffuse_list = []
                    
        if layer.lambertian_use_tex and layer.lambertian_diffuse_tex != '':
            if is_uv_img(bpy.data.textures[layer.lambertian_diffuse_tex]):
                reflectance_name = layer.lambertian_diffuse_tex + "_inst"
                if reflectance_name not in self.textures_set:
                    self.__emit_texture(bpy.data.textures[layer.lambertian_diffuse_tex], False, scene)
                    self.textures_set.add(reflectance_name)

                    
        if reflectance_name == "":            
            reflectance_name = "{0}_lambertian_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name,
                                                   layer.lambertian_reflectance,
                                                   layer.lambertian_multiplier)

        self.__open_element('bsdf name="{0}" model="lambertian_brdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__close_element("bsdf")
    #----------------------------------------------------------
    def __emit_diffuse_btdf(self, material, bsdf_name, scene, layer):      
        asr_mat = material.appleseed  
        
        transmittance_name = ""
        
        if layer.transmission_use_tex and layer.transmission_tex != "":
            if is_uv_img(bpy.data.textures[layer.transmission_tex]):    
                transmittance_name = layer.transmission_tex + "_inst"
                if transmittance_name not in self.textures_set:
                    self.textures_set.add(transmittance_name)
                    self.__emit_texture(bpy.data.textures[layer.transmission_tex], False, scene)
    
        if transmittance_name == "":
            transmittance_name = "{0}_diffuse_transmittance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(transmittance_name, 
                                                    layer.transmission_color,
                                                    layer.transmission_multiplier)
                                                    
        self.__open_element('bsdf name="{0}" model="diffuse_btdf"'.format(bsdf_name))
        self.__emit_parameter("transmittance", transmittance_name)
        self.__emit_parameter("transmittance_multiplier", layer.transmission_multiplier)
        self.__close_element("bsdf")
        
    #----------------------------------------------------------
    def __emit_ashikhmin_brdf(self, material, bsdf_name, scene, layer):
        asr_mat = material.appleseed
                
        diffuse_reflectance_name = ""
        glossy_reflectance_name = ""
        
        if layer.ashikhmin_use_diff_tex and layer.ashikhmin_diffuse_tex != "":
            if is_uv_img(bpy.data.textures[layer.ashikhmin_diffuse_tex]):    
                diffuse_reflectance_name = layer.ashikhmin_diffuse_tex + "_inst"
                if diffuse_reflectance_name not in self.textures_set:
                    self.textures_set.add(diffuse_reflectance_name)
                    self.__emit_texture(bpy.data.textures[layer.ashikhmin_diffuse_tex], False, scene)
                
        if layer.ashikhmin_use_gloss_tex and layer.ashikhmin_gloss_tex != "":
            if is_uv_img(bpy.data.textures[layer.ashikhmin_gloss_tex]):    
                glossy_reflectance_name = layer.ashikhmin_gloss_tex + "_inst"
                if glossy_reflectance_name not in self.textures_set:
                    self.__emit_texture(bpy.data.textures[layer.ashikhmin_gloss_tex], False, scene)
                    self.textures_set.add(glossy_reflectance_name)
            
        #Make sure we found some textures. If not, default to material color.
        if diffuse_reflectance_name == "":
            diffuse_reflectance_name = "{0}_ashikhmin_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(diffuse_reflectance_name,
                                                   layer.ashikhmin_reflectance,
                                                   layer.ashikhmin_multiplier)
        if glossy_reflectance_name == "":    
            glossy_reflectance_name = "{0}_ashikhmin_glossy_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(glossy_reflectance_name,
                                                   layer.ashikhmin_glossy,
                                                   layer.ashikhmin_glossy_multiplier)

        self.__open_element('bsdf name="{0}" model="ashikhmin_brdf"'.format(bsdf_name))
        self.__emit_parameter("diffuse_reflectance", diffuse_reflectance_name)
        self.__emit_parameter("glossy_reflectance", glossy_reflectance_name)
        self.__emit_parameter("shininess_u", layer.ashikhmin_shininess_u)
        self.__emit_parameter("shininess_v", layer.ashikhmin_shininess_v)
        self.__close_element("bsdf")
    
    #-----------------------------------------------------
    
    def __emit_specular_brdf(self, material, bsdf_name, scene, layer):
        asr_mat = material.appleseed
        
        reflectance_name = ""
        if layer.specular_use_gloss_tex and layer.specular_gloss_tex != "":
            if is_uv_img(bpy.data.textures[layer.specular_gloss_tex]):    
                reflectance_name = layer.specular_gloss_tex + "_inst"
                if reflectance_name not in self.textures_set:
                    self.textures_set.add(reflectance_name)
                    self.__emit_texture(bpy.data.textures[layer.specular_gloss_tex], False, scene)
        if reflectance_name == "":
            reflectance_name = "{0}_specular_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name, material.mirror_color, 1.0)

        self.__open_element('bsdf name="{0}" model="specular_brdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__close_element("bsdf")
    
    #-------------------------------------------------------

    def __emit_specular_btdf(self, material, bsdf_name, side, layer):
        assert side == 'front' or side == 'back'
        
        asr_mat = material.appleseed
        
        reflectance_name = ""
        transmittance_name = ""
        
        if layer.spec_btdf_use_tex and layer.spec_btdf_tex != "":
            if is_uv_img(bpy.data.textures[layer.spec_btdf_tex]):    
                reflectance_name = layer.spec_btdf_tex + "_inst"
                if reflectance_name not in self.textures_set:
                    self.textures_set.add(reflectance_name)
                    self.__emit_texture(bpy.data.textures[layer.spec_btdf_tex], False, scene)
        if reflectance_name == "":        
            reflectance_name = "{0}_transp_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name, layer.spec_btdf_reflectance, layer.spec_btdf_ref_mult)
        
        if layer.spec_btdf_use_trans_tex and layer.spec_btdf_trans_tex != "":
            if is_uv_img(bpy.data.textures[layer.spec_btdf_trans_tex]):    
                transmittance_name = layer.spec_btdf_trans_tex + "_inst"
                if transmittance_name not in self.textures_set:
                    self.textures_set.add(transmittance_name)
                    self.__emit_texture(bpy.data.textures[layer.spec_btdf_trans_tex], False, scene)
        
        if transmittance_name == "":            
            transmittance_name = "{0}_transp_transmittance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(transmittance_name, layer.spec_btdf_transmittance, layer.spec_btdf_trans_mult)

        if side == 'front':
            from_ior = 1.0
            to_ior = layer.spec_btdf_to_ior
        else:
            from_ior = layer.spec_btdf_from_ior
            to_ior = 1.0

        self.__open_element('bsdf name="{0}" model="specular_btdf"'.format(bsdf_name))
        self.__emit_parameter("reflectance", reflectance_name)
        self.__emit_parameter("transmittance", transmittance_name)
        self.__emit_parameter("from_ior", from_ior)
        self.__emit_parameter("to_ior", to_ior)
        self.__close_element("bsdf")
    
    #-------------------------------------------------------------------
    
    def __emit_microfacet_brdf(self, material, bsdf_name, scene, layer):
        asr_mat = material.appleseed
        reflectance_name = ""
        mdf_refl = ""
        
        if layer.microfacet_use_diff_tex and layer.microfacet_diff_tex != "":
            if is_uv_img(bpy.data.textures[layer.microfacet_diff_tex]):
                reflectance_name = layer.microfacet_diff_tex + "_inst"
                if reflectance_name not in self.textures_set:
                    self.__emit_texture(bpy.data.textures[layer.microfacet_diff_tex], False, scene)
                    self.textures_set.add(reflectance_name)
        
        if reflectance_name == "":
            reflectance_name = "{0}_microfacet_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name,
                                                   layer.microfacet_reflectance,
                                                   layer.microfacet_multiplier)
        if layer.microfacet_use_spec_tex and layer.microfacet_spec_tex != "":
            if is_uv_img(bpy.data.textures[layer.microfacet_spec_tex]):    
                mdf_refl = layer.microfacet_spec_tex + "_inst"
                if mdf_refl not in self.textures_set:
                    self.__emit_texture(bpy.data.textures[layer.microfacet_spec_tex], False, scene)
                    self.textures_set.add(mdf_refl)
        if mdf_refl == "":
            #This changes to a float, if it's not a texture
            mdf_refl = layer.microfacet_mdf_parameter
                       
        self.__open_element('bsdf name="{0}" model="microfacet_brdf"'.format(bsdf_name))
        self.__emit_parameter("fresnel_multiplier", layer.microfacet_fresnel)
        self.__emit_parameter("mdf", layer.microfacet_mdf)
        self.__emit_parameter("mdf_parameter", mdf_refl)
        self.__emit_parameter("reflectance", reflectance_name)
        self.__emit_parameter("reflectance_multiplier", layer.microfacet_multiplier)
        self.__close_element("bsdf")
               
    #---------------------------------------------------------------------
    
    def __emit_kelemen_brdf(self, material, bsdf_name, scene, layer):
        asr_mat = material.appleseed
        reflectance_name = ""
        spec_refl_name  = ""
        
        if layer.kelemen_use_diff_tex:
            if layer.kelemen_diff_tex != "":
                if is_uv_img(bpy.data.textures[layer.kelemen_diff_tex]):
                    reflectance_name = layer.kelemen_diff_tex + "_inst"
                    if reflectance_name not in self.textures_set:
                        self.textures_set.add(reflectance_name)
                        self.__emit_texture(bpy.data.textures[layer.kelemen_diff_tex], False, scene)
        
        if reflectance_name == "":
            reflectance_name = "{0}_kelemen_reflectance".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(reflectance_name,
                                                   layer.kelemen_matte_reflectance,
                                                   layer.kelemen_matte_multiplier)
        if layer.kelemen_use_spec_tex and layer.kelemen_spec_tex != "":
            if is_uv_img(bpy.data.textures[layer.kelemen_spec_tex]):    
                spec_refl_name = layer.kelemen_spec_tex + "_inst"
                if spec_refl_name not in self.textures_set:
                    self.textures_set.add(spec_refl_name)
                    self.__emit_texture(bpy.data.textures[layer.kelemen_spec_tex], False, scene)
        if spec_refl_name == "":
            spec_refl_name = "{0}_kelemen_specular".format(bsdf_name)
            self.__emit_solid_linear_rgb_color_element(spec_refl_name, 
                                                    layer.kelemen_specular_reflectance,
                                                    layer.kelemen_specular_multiplier)
                                                    
        self.__open_element('bsdf name="{0}" model="kelemen_brdf"'.format(bsdf_name))
        self.__emit_parameter("matte_reflectance", reflectance_name)
        self.__emit_parameter("matte_reflectance_multiplier", layer.kelemen_matte_multiplier)
        self.__emit_parameter("roughness", layer.kelemen_roughness)
        self.__emit_parameter("specular_reflectance", spec_refl_name)
        self.__emit_parameter("specular_reflectance_multiplier", layer.kelemen_specular_multiplier)
        self.__close_element("bsdf")
    
    #---------------------------------------------------------------------    
    
    def __emit_bsdf_mix(self, bsdf_name, bsdf0_name, bsdf0_weight, bsdf1_name, bsdf1_weight):
        self.__open_element('bsdf name="{0}" model="bsdf_mix"'.format(bsdf_name))
        self.__emit_parameter("bsdf0", bsdf0_name)
        self.__emit_parameter("weight0", bsdf0_weight)
        self.__emit_parameter("bsdf1", bsdf1_name)
        self.__emit_parameter("weight1", bsdf1_weight)
        self.__close_element("bsdf")
    
    #-----------------------------------------------
    
#
#    def __emit_edf(self, material, edf_name):
#        self.__emit_diffuse_edf(material, edf_name)
    
    #This was called _emit_diffuse_edf
    def __emit_edf(self, material, edf_name, scene):
        asr_mat = material.appleseed
        exitance_name = "{0}_exitance".format(edf_name)
        emit_factor = asr_mat.light_emission if asr_mat.light_emission > 0.0 else 1.0
        self.__emit_solid_linear_rgb_color_element(exitance_name,
                                                   asr_mat.light_color,
                                                   emit_factor * scene.appleseed.light_mats_exitance_mult)
        self.__emit_diffuse_edf_element(edf_name, exitance_name)
    
    #------------------------
    
    def __emit_diffuse_edf_element(self, edf_name, exitance_name):
        self.__open_element('edf name="{0}" model="diffuse_edf"'.format(edf_name))
        self.__emit_parameter("exitance", exitance_name)
        self.__close_element("edf")

    #---------------------------------------------
    #Export textures, if any exist on the material
    def __emit_texture(self, tex, bump_bool, scene):        
            #Check that the image texture does not already exist in the folder
            if tex.image.filepath.split(sep)[-1] not in os.listdir(realpath(scene.appleseed.project_path)):    
                src_path = realpath(tex.image.filepath)
                dest_path = os.path.join(realpath(scene.appleseed.project_path), tex.image.filepath.split(sep)[-1])
                #If not, then copy the image
                copyfile(src_path, dest_path)       
            else:
                pass
            color_space = 'linear_rgb' if tex.image.colorspace_settings.name == 'Linear' else 'srgb'      
            self.__open_element('texture name="{0}" model="disk_texture_2d"'.format(tex.name if bump_bool == False else tex.name + "_bump"))
            self.__emit_parameter("color_space", color_space)
            self.__emit_parameter("filename", tex.image.filepath.split(sep)[-1])
            self.__close_element("texture")
            #Now create texture instance
            self.__emit_texture_instance(tex, bump_bool)
            
            print('Emitting texture', tex.name)

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
        if material != "":
            asr_mat = material.appleseed
        bump_map = ""
        sss_shader = ""
        
        #Make sure we're not evaluating the default material.
        if material != "":
            print("\nWriting material element for material: ", material.name, '\n')
            #Check if we're using an SSS surface shader
            if asr_mat.sss_use_shader:
                sss_shader = "fastsss_{0}".format(material.name)
                self.__emit_sss_shader(sss_shader, material.name, scene)   
                print("\nCreating SSS shader for material: ", material.name, "sss shader", sss_shader, '\n') 
            
            if asr_mat.material_use_bump_tex:
                if asr_mat.material_bump_tex != "":
                    if is_uv_img(bpy.data.textures[asr_mat.material_bump_tex]):
                        bump_map = asr_mat.material_bump_tex + "_bump"
                                
            if bump_map != "":
                if bump_map not in self.textures_set:
                    self.__emit_texture(bpy.data.textures[asr_mat.material_bump_tex], True, scene)
                    self.textures_set.add(bump_map)

        self.__open_element('material name="{0}" model="generic_material"'.format(material_name))
        if len(bsdf_name) > 0:
            self.__emit_parameter("bsdf", bsdf_name)
        if len(edf_name) > 0:
            self.__emit_parameter("edf", edf_name)
            
        if material != "":      #In case we're evaluating "__default_material"
            #If we're using a bump map on the material
            if bump_map != "":                        
                self.__emit_parameter("bump_amplitude", asr_mat.material_bump_amplitude)
                self.__emit_parameter("displacement_map", bump_map + "_inst")
                self.__emit_parameter("displacement_method", "normal" if asr_mat.material_use_normalmap else "bump")
                self.__emit_parameter("normal_map_up", "z")
            
            #If we're using an alpha map    
            if asr_mat.material_use_alpha:
                if asr_mat.material_alpha_map != "":
                    self.__emit_parameter("alpha_map", asr_mat.material_alpha_map + "_inst")
                    if asr_mat.material_alpha_map + "_inst" not in self.textures_set:
                        self.__emit_texture(bpy.data.textures[asr_mat.material_alpha_map], False, scene)
                        self.textures_set.add(asr_mat.material_alpha_map + "_inst")
        else:
            pass
        self.__emit_parameter("surface_shader", sss_shader if sss_shader != "" else surface_shader_name)
        self.__close_element("material")
    
    #-------------------------------------        
    def __emit_sss_shader(self, sss_shader_name, material_name, scene):
        material = bpy.data.materials[material_name]
        asr_mat = material.appleseed
        
        albedo_list = []
        
        #Get color texture, if any exist and we're using an albedo texture
        if asr_mat.sss_albedo_use_tex and not asr_mat.sss_albedo_tex != "":
            if is_uv_img(bpy.data.textures[asr_mat.sss_albedo_tex]):
                albedo_name = asr_mat.sss_albedo_tex + "_inst"
                if albedo_name not in self.textures_set:   
                    self.__emit_texture(bpy.data.textures[albedo_list[0]], scene)
                    self.textures_set.add(albedo_name)
            
            #If no texture was found        
            elif albedo_list == []:
                albedo_name = material_name + "_albedo"
                self.__emit_solid_linear_rgb_color_element(material_name + "_albedo", material.subsurface_scattering.color, 1.0)
        
        #If not using albedo textures        
        else:
            self.__emit_solid_linear_rgb_color_element(material_name + "_albedo", material.subsurface_scattering.color, 1.0)
            albedo_name = material_name + "_albedo"
            
        self.__open_element('surface_shader name="{0}" model="fast_sss_surface_shader"'.format(sss_shader_name))
        self.__emit_parameter("albedo", albedo_name)
        self.__emit_parameter("ambient_sss", asr_mat.sss_ambient)
        self.__emit_parameter("diffuse", asr_mat.sss_diffuse)
        self.__emit_parameter("distortion", asr_mat.sss_distortion)
        self.__emit_parameter("light_samples", asr_mat.sss_light_samples)
        self.__emit_parameter("occlusion_samples", asr_mat.sss_occlusion_samples)
        self.__emit_parameter("power", asr_mat.sss_power)
        self.__emit_parameter("scale", asr_mat.sss_scale)
        self.__emit_parameter("view_dep_sss", asr_mat.sss_view_dep)
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
            self.__emit_sun_light(scene, object)
        else:
            self.__warning("While exporting light '{0}': unsupported light type '{1}', skipping this light.".format(object.name, light_type))

    def __emit_sun_light(self, scene, lamp):
        sunsky = scene.appleseed_sky
        use_sunsky = sunsky.use_sunsky
        environment_edf = "environment_edf"
        
        self.__open_element('light name="{0}" model="sun_light"'.format(lamp.name))
        if bool(lamp.appleseed_render_layer):
            render_layer = lamp.appleseed_render_layer
            self.__emit_parameter("render_layer", render_layer)
        if use_sunsky:    
            self.__emit_parameter("environment_edf", environment_edf)
        self.__emit_parameter("radiance_multiplier", sunsky.radiance_multiplier if use_sunsky else 0.04)
        self.__emit_parameter("turbidity", 4.0)
        self.__emit_transform_element(self.global_matrix * lamp.matrix_world)
        self.__close_element("light")
        
    def __emit_point_light(self, scene, lamp):
        exitance_name = "{0}_exitance".format(lamp.name)
        self.__emit_solid_linear_rgb_color_element(exitance_name, lamp.data.color, lamp.data.energy * self.point_lights_exitance_mult)

        self.__open_element('light name="{0}" model="point_light"'.format(lamp.name))
        if bool(lamp.appleseed_render_layer):
            render_layer = lamp.appleseed_render_layer
            self.__emit_parameter("render_layer", render_layer)
        self.__emit_parameter("exitance", exitance_name)
        self.__emit_transform_element(self.global_matrix * lamp.matrix_world)
        self.__close_element("light")

    def __emit_spot_light(self, scene, lamp):
        exitance_name = "{0}_exitance".format(lamp.name)
        self.__emit_solid_linear_rgb_color_element(exitance_name, lamp.data.color, lamp.data.energy * self.spot_lights_exitance_mult)

        outer_angle = math.degrees(lamp.data.spot_size)
        inner_angle = (1.0 - lamp.data.spot_blend) * outer_angle

        self.__open_element('light name="{0}" model="spot_light"'.format(lamp.name))
        if bool(lamp.appleseed_render_layer):
            render_layer = lamp.appleseed_render_layer
            self.__emit_parameter("render_layer", render_layer)
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
        cls.project_path = bpy.props.StringProperty(description = "Where to export project files. Rendered images are saved in .render", subtype = 'DIR_PATH')                                              
        
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
                                            

        cls.camera_type = bpy.props.EnumProperty(items = [('pinhole', 'Pinhole', 'Pinhole camera - no DoF'),
                                                ('thinlens', 'Thin lens', 'Thin lens - enables DoF')],
                                            name = "Camera type",
                                            description = "Camera lens model",
                                            default = 'pinhole')
                                            
        cls.premult_alpha = bpy.props.BoolProperty(name = "Premultiplied Alpha",
                                            description = "Premultiplied alpha",
                                            default = True)
                                            
        cls.camera_dof = bpy.props.FloatProperty(name = "F-stop", description = "Thin lens camera f-stop value", default = 32.0, min = 0.0, max = 32.0, step =3, precision = 1)
        
        cls.export_emitting_obj_as_lights = bpy.props.BoolProperty(name="Export Emitting Objects As Mesh Lights",
                                                           description="Export object with light-emitting materials as mesh (area) lights",
                                                           default=True)
                                                           
        cls.enable_diagnostics = bpy.props.BoolProperty(name = "Enable diagnostics", description = '', default = False)
        
        cls.quality = bpy.props.FloatProperty(name = "Quality", description = '', default = 3.0, min = 0.0, max = 20.0, precision = 3)
        
        cls.new_build_options = bpy.props.BoolProperty(name = "appleseed.studio options", description = "Enable automatic rendering when appleseed.studio starts -- this requires a build of appleseed.studio that supports automatic loading of .appleseed files", default = False)
        
        cls.interactive_mode = bpy.props.BoolProperty(name = "Interactive rendering", description = "appleseed.studio will begin rendering in final render mode.  If left unchecked, appleseed.studio will begin rendering using interactive render mode", default = False)
        
        cls.light_mats_exitance_mult = bpy.props.FloatProperty(name="Global Meshlight Energy Multiplier",
                                                       description="Multiply the exitance of light-emitting materials by this factor",
                                                       min=0.0,
                                                       max=100.0,
                                                       default=1.0)
        
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
properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add('APPLESEED')
properties_texture.TEXTURE_PT_image_mapping.COMPAT_ENGINES.add('APPLESEED')
properties_texture.TEXTURE_PT_mapping.COMPAT_ENGINES.add('APPLESEED')
properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add('APPLESEED')
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

class AppleseedMatLayerProps(bpy.types.PropertyGroup):
    
    bsdf_type = bpy.props.EnumProperty(items = [
                                    ("lambertian_brdf", "Lambertian BRDF", ""),
                                    ("ashikhmin_brdf", "Ashikhmin-Shirley BRDF", ""),
                                    ("diffuse_btdf", "Diffuse BTDF", ""),
                                    ("kelemen_brdf", "Kelemen BRDF", ""),
                                    ("microfacet_brdf", "Microfacet BRDF", ""),
                                    ("specular_brdf", "Specular BRDF (mirror)", ""),
                                    ("specular_btdf", "Specular BTDF (glass)", "")],
                                    name = "BSDF Model", 
                                    description = "BSDF model for current material layer", 
                                    default = "lambertian_brdf")
    #---------------------
    
    use_diffuse_btdf = bpy.props.BoolProperty(name = "Diffuse BTDF", description = "Enable blending of diffuse BTDF", default = False)
        
    transmission_multiplier = bpy.props.FloatProperty(name = "Transmittance multiplier", description = "Multiplier for material transmission", default = 0.0, min = 0.0, max = 2.0)
    
    transmission_color = bpy.props.FloatVectorProperty(name = "Transmittance color", description = "Transmittance color", default = (0.8, 0.8, 0.8), subtype = 'COLOR',min = 0.0, max = 1.0)
    
    transmission_use_tex = bpy.props.BoolProperty(name = "", description = "Use texture to influence diffuse color", default = False)
    
    transmission_tex = bpy.props.StringProperty(name = "", description = "Texture to influence diffuse color", default = "")
    
    transmission_weight = bpy.props.FloatProperty(name = "Diffuse BTDF Blending Weight", description = "Blending weight of Diffuse BTDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    #-----------------------

    
    use_kelemen = bpy.props.BoolProperty(name = "Kelemen BRDF", description = "Enable blending of Kelemen BRDF", default = False)
    
    kelemen_matte_reflectance = bpy.props.FloatVectorProperty(name = "Matte Reflectance", description = "Kelemen matte reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    kelemen_use_diff_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence matte reflectance", default = False)
    
    kelemen_diff_tex = bpy.props.StringProperty(name = "", description = "Texture to influence matte reflectance", default = "")
    
    kelemen_matte_multiplier = bpy.props.FloatProperty(name = "Matte Reflectance Multiplier", description = "Kelemen matte reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    kelemen_roughness = bpy.props.FloatProperty(name = "Roughness", description = "Kelemen roughness", default = 0.0, min = 0.0, max = 1.0)
    
    kelemen_specular_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Kelemen specular reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    kelemen_use_spec_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence specular reflectance", default = False)
    
    kelemen_spec_tex = bpy.props.StringProperty(name = "", description = "Texture to influence specular reflectance", default = "")
    
    kelemen_specular_multiplier = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Kelemen specular reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)       
    
    kelemen_weight = bpy.props.FloatProperty(name = "Kelemen Blending Weight", description = "Blending weight of Kelemen BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)
    
    #-------------------------
    
    use_microfacet = bpy.props.BoolProperty(name = "Microfacet BRDF", description = "Enable blending of Microfacet BRDF", default = False)
    
    microfacet_fresnel = bpy.props.FloatProperty(name = "Fresnel Multiplier", description = "Microfacet fresnel multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    microfacet_mdf = bpy.props.EnumProperty(items = [
                                    ("ggx", "GGX", ""),
                                    ("ward", "Ward", ""),
                                    ("beckmann", "Beckmann", ""),
                                    ("blinn", "Blinn", "")],
                                    name = "Microfacet model", description = "Microfacet distribution function model", default = "beckmann")
                                    
    microfacet_mdf_parameter = bpy.props.FloatProperty(name = "Distribution Function", description = "Microfacet distribution function (glossiness: lower values = more glossy)", default = 0.5, min = 0.0, max = 1.0)
    
    microfacet_reflectance = bpy.props.FloatVectorProperty(name = "Microfacet Reflectance", description = "Microfacet reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    microfacet_multiplier = bpy.props.FloatProperty(name = "Microfacet Reflectance Multiplier", description = "Microfacet reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    microfacet_use_diff_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence reflectance", default = False)
    
    microfacet_diff_tex = bpy.props.StringProperty(name = "", description = "Texture to influence reflectance", default = "")
    
    microfacet_use_spec_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence distribution function (glossiness)", default = False)
    
    microfacet_spec_tex = bpy.props.StringProperty(name = "", description = "Texture to influence distribution function (glossiness)", default = "")
    
    microfacet_weight = bpy.props.FloatProperty(name = "Microfacet Blending Weight", description = "Blending weight of Microfacet BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)
    
    #------------------------------
    
    use_ashikhmin = bpy.props.BoolProperty(name = "Ashikhmin-Shirley BRDF", description = "Enable blending of Ashikhmin-Shirley BRDF", default = False)
    ashikhmin_reflectance = bpy.props.FloatVectorProperty(name = "Diffuse Reflectance", description = "Ashikhmin-Shirley diffuse reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    ashikhmin_use_diff_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence diffuse reflectance", default = False)
    
    ashikhmin_diffuse_tex = bpy.props.StringProperty(name = "", description = "Diffuse reflectance texture", default = "")
    
    ashikhmin_multiplier = bpy.props.FloatProperty(name= "Diffuse Reflectance Multiplier", description = "Ashikhmin-Shirley diffuse reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    ashikhmin_fresnel = bpy.props.FloatProperty(name = "Fresnel Multiplier", description = "", default = 1.0, min = 0.0, max = 2.0)
    ashikhmin_glossy = bpy.props.FloatVectorProperty(name = "Glossy Reflectance", description = "Ashikhmin-Shirley glossy reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    ashikhmin_use_gloss_tex = bpy.props.BoolProperty(name= "", description = "Use a texture to influence gglossy reflectance", default = False)
    
    ashikhmin_gloss_tex = bpy.props.StringProperty(name= "", description = "Texture to influence glossy reflectance", default = "")
    
    ashikhmin_glossy_multiplier = bpy.props.FloatProperty(name = "Glossy Reflectance Multiplier", description = "Ashikhmin-Shirley glossy reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    ashikhmin_shininess_u = bpy.props.FloatProperty(name = "Shininess U", description = "", default = 200.0, min = 0.0, max = 1000.0)
    
    ashikhmin_shininess_v = bpy.props.FloatProperty(name = "Shininess V", description = "", default = 200.0, min = 0.0, max = 1000.0)
    ashikhmin_weight = bpy.props.FloatProperty(name = "Ashikhmin Blending Weight", description = "Blending weight of Ashikhmin-Shirley BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)
    
    #--------------------------------
    
    use_lambertian = bpy.props.BoolProperty(name = "Lambertian BRDF", description = "Enable blending of Lambertian BRDF", default = True)
    
    lambertian_reflectance = bpy.props.FloatVectorProperty(name = "Lambertian Reflectance", description = "Lambertian diffuse reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    lambertian_multiplier = bpy.props.FloatProperty(name = "Reflectance Multiplier", description = "Lambertian reflectance multiplier", default = 1.0, min = 0.0, max = 2.0)
    
    lambertian_weight = bpy.props.FloatProperty(name = "Lambertian Blending Weight", description = "Blending weight of Lambertian BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    lambertian_use_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence diffuse color", default = False)
    
    lambertian_diffuse_tex = bpy.props.StringProperty(name = "", description = "Diffuse color texture", default = "")
    
    #---------------------------------
    
    use_specular_brdf = bpy.props.BoolProperty(name = "Specular BRDF", description = "Enable blending of Specular BRDF (mirror)", default = False)
    
    specular_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Specular BRDF reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    specular_use_gloss_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular reflectance", default = False)
    
    specular_gloss_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular reflectance", default = "")
    
    specular_multiplier = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Specular BRDF relectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    specular_weight = bpy.props.FloatProperty(name = "Specular Blending Weight", description = "Blending weight of Specular BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0) 
    
    #---------------------------------
    
    use_specular_btdf = bpy.props.BoolProperty(name = "Specular BTDF", description = "Enable blending of Specular BTDF (glass)", default = False)
    
    spec_btdf_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Specular BTDF reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    spec_btdf_use_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular reflectance", default = False)
    
    spec_btdf_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular reflectance", default = "")
    
    spec_btdf_ref_mult = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Specular BTDF reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    spec_btdf_transmittance = bpy.props.FloatVectorProperty(name = "Specular Transmittance", description = "Specular BTDF transmittance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    spec_btdf_use_trans_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular transmittance", default = False)
    
    spec_btdf_trans_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular transmittance", default = "")
    
    spec_btdf_trans_mult = bpy.props.FloatProperty(name = "Specular Transmittance Multiplier", description = "Specular BTDF transmittance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    spec_btdf_from_ior = bpy.props.FloatProperty(name = "From IOR", description = "From index of refraction", default = 1.0, min = 1.0, max = 4.01)
    
    spec_btdf_to_ior = bpy.props.FloatProperty(name = "To IOR", description = "To index of refraction", default = 1.0, min = 1.0, max = 4.01)
    
    spec_btdf_weight = bpy.props.FloatProperty(name = "Specular BTDF Blending Weight", description = "Blending weight of Specular BTDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0) 
    


#--------------------------------------------------

class AppleseedWorldProps(bpy.types.PropertyGroup):    
    env_type = bpy.props.EnumProperty(items = [
                    ("gradient", "Gradient", "Use sky color gradient"),
                    ("constant", "Constant", "Use constant color for sky"),
                    ("constant_hemisphere", "Per-Hemisphere Constant", "Use constant color per hemisphere"),
                    ("latlong_map", "Latitude-Longitude Map", "Use latlong map texture"), 
                    ("mirrorball_map", "Mirror Ball Map", "Use mirror ball texture")], 
                    name = "Environment Type", description = "Select environment type", default = "gradient")
                    
    env_tex = bpy.props.StringProperty(name = "Environment Texture", description = "Texture to influence environment", default = "")
    
#------------------------------------------------    
    
class AppleseedMatProps(bpy.types.PropertyGroup):
    
    #Per layer properties are stored in AppleseedMatLayerProps
    layers = bpy.props.CollectionProperty(type = AppleseedMatLayerProps, name = "Appleseed Material Layers", description = "")
    
    layer_index = bpy.props.IntProperty(name = "Layer Index", description = "", default = 0, min = 0, max = 16)
    
    
    use_light_emission = bpy.props.BoolProperty(name = "Light Emitter", description = "Enable material light emission", default = False)
    
    light_emission = bpy.props.FloatProperty(name = "Emission strength", description = "Light emission strength", default = 0.0, min = 0.0, max = 5.0)
    
    light_color = bpy.props.FloatVectorProperty(name = "Emission Color", description = "Light emission color", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    sss_use_shader = bpy.props.BoolProperty(name = "FastSSS", description = "Enable Appleseed FastSSS shader (experimental)", default = False)
    
    sss_albedo_use_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence SSS color", default = False)
    
    sss_ambient = bpy.props.FloatProperty(name = "Ambient SSS", description = "Ambient SSS value", default = 1.0, min = 0.0, max = 10.0)
    
    sss_diffuse = bpy.props.FloatProperty(name = "Diffuse Lighting", description = "", default = 1.0, min = 0.0, max = 10.0)
    
    sss_distortion = bpy.props.FloatProperty(name = "Normal Distortion", description = "", default = 1.0, min = 0.0, max = 10.0)
    
    sss_light_samples = bpy.props.IntProperty(name = "Light Samples", description = "", default = 1, min = 0, max = 100)
    
    sss_occlusion_samples = bpy.props.IntProperty(name = "Occlusion Samples", description = "", default = 1, min = 0, max = 100)
    
    sss_power = bpy.props.FloatProperty(name = "Power", description = "", default = 1.0, min = 0.0, max = 10.0)
    
    sss_scale = bpy.props.FloatProperty(name = "Geometric Scale", description = "", default = 1.0, min = 0.0, max = 10.0)
    
    sss_view_dep = bpy.props.FloatProperty(name = "View-dependent SSS", description = "", default = 1.0, min = 0.0, max = 10.0)
    
    sss_albedo_tex = bpy.props.StringProperty(name = '', description = 'Texture to influence SSS albedo', default = "")

    material_use_bump_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence bump / normal", default = False)
    
    material_bump_tex = bpy.props.StringProperty(name = "", description = "Bump / normal texture", default = "")
    
    material_use_normalmap = bpy.props.BoolProperty(name = "", description = "Use texture as normal map", default = False)
    
    material_bump_amplitude  = bpy.props.FloatProperty(name = "Bump Amplitude", description = "Maximum height influence of bump / normal map", default = 1.0, min = 0.0, max = 1.0)
    
    material_use_alpha = bpy.props.BoolProperty(name = "", description = "Use a texture to influence alpha", default = False)
    
    material_alpha_map = bpy.props.StringProperty(name = "", description = "Alpha texture", default = "")
    
    
#-------------------------------------------------    
    
#Operator for adding material layers
class AppleseedAddMatLayer(bpy.types.Operator):
    bl_label = "Add Layer"
    bl_description = "Add new BSDF layer"
    bl_idname = "appleseed.add_matlayer"
    
    def invoke(self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.add()
        num = collection.__len__()
        collection[num-1].name = "BSDF Layer " + str(num)
        
            
        return {'FINISHED'}
    
#---------------------------------------------
#Operator for removing material layers
class AppleseedRemoveMatLayer(bpy.types.Operator):
    bl_label = "Remove Layer"
    bl_description = "Remove BSDF layer"
    bl_idname = "appleseed.remove_matlayer"
        
    def invoke(self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.remove(index)
        num = collection.__len__()
        if index >= num:
            index = num -1
        if index < 0:
            index = 0
        material.appleseed.layer_index = index
            
        return {'FINISHED'}    
#-------------------------------------------------    
    
#Operator for adding render layers
class AppleseedAddRenderLayer(bpy.types.Operator):
    bl_label = "Add Layer"
    bl_idname = "appleseed.add_renderlayer"
    
    def invoke(self, context, event):
        scene = context.scene
        collection = scene.appleseed_layers.layers
        index = scene.appleseed_layers.layer_index

        collection.add()
        num = collection.__len__()
        collection[num-1].name = "Render Layer " + str(num)
            
        return {'FINISHED'}

#---------------------------------------------
#Operator for removing render layers
class AppleseedRemoveRenderLayer(bpy.types.Operator):
    bl_label = "Remove Layer"
    bl_idname = "appleseed.remove_renderlayer"
        
    def invoke(self, context, event):
        scene = context.scene
        collection = scene.appleseed_layers.layers
        index = scene.appleseed_layers.layer_index

        collection.remove(index)
        num = collection.__len__()
        if index >= num:
            index = num -1
        if index < 0:
            index = 0
        scene.appleseed_layers.layer_index = index
            
        return {'FINISHED'}
    
                        
#---------------------------------------
#Render Panels                    
class AppleseedRenderPanelBase( object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED'


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
        if asr_scene_props.renderer_type == "GUI":
            layout.prop(asr_scene_props, "new_build_options")
            if asr_scene_props.new_build_options:    
                layout.prop(asr_scene_props, "interactive_mode")
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
        col.prop(asr_scene_props, "light_mats_exitance_mult")   
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

#-------------------------------------------

class AppleseedRenderLayers(bpy.types.PropertyGroup):
    pass

#---------------------------------------------------

class AppleseedRenderLayerProps(bpy.types.PropertyGroup):
    layers = bpy.props.CollectionProperty(type = AppleseedRenderLayers, name = "Appleseed Render Layers", description = "")
    layer_index = bpy.props.IntProperty(name = "Layer Index", description = "", default = 0, min = 0, max = 16)

#-------------------------------------------------
#Render layers panel 
class AppleseedRenderLayers(bpy.types.Panel):
    bl_label = "Appleseed Render Layers"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render_layer"    
    COMPAT_ENGINES = {'APPLESEED'}
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        appleseed_layers = scene.appleseed_layers
        
        layout.label("Render Layers:", icon = 'RENDERLAYERS')
       
        row = layout.row()
        row.template_list("UI_UL_list", "appleseed_render_layers", appleseed_layers, "layers", appleseed_layers, "layer_index")
        
        row = layout.row(align=True)
        row.operator("appleseed.add_renderlayer", icon = "ZOOMIN")
        row.operator("appleseed.remove_renderlayer", icon = "ZOOMOUT")
                
        if appleseed_layers.layers:
            current_layer = appleseed_layers.layers[appleseed_layers.layer_index]   
            layout.prop(current_layer, "name", text = "Layer Name")
        
#--------------------------------------------------
class AppleseedObjRenderLayerPanel(bpy.types.Panel):
    bl_label = "Appleseed Render Layers"
    COMPAT_ENGINES = {'APPLESEED'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED' and context.object is not None and context.object.type != 'CAMERA'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        object = context.object
        appleseed_layers = scene.appleseed_layers
        
        layout.label("Appleseed Render Layers:", icon = 'RENDERLAYERS')
       
        row = layout.row()
        row.template_list("UI_UL_list", "appleseed_render_layers", appleseed_layers, "layers", appleseed_layers, "layer_index")

        row = layout.row(align=True)
        row.operator("appleseed.add_renderlayer", icon = "ZOOMIN")
        row.operator("appleseed.remove_renderlayer", icon = "ZOOMOUT")
                
        if appleseed_layers.layers:
            current_layer = appleseed_layers.layers[appleseed_layers.layer_index]   
            layout.prop(current_layer, "name", text = "Layer name")
        
        layout.label("Constrain object to render layer:", icon = 'OBJECT_DATA')
        layout.prop_search(object, "appleseed_render_layer", appleseed_layers, "layers", text = "")        
             
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


#---------------------------------------------
class MATERIAL_UL_BSDF_slots(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        BSDF = item
        bsdf_type = BSDF.bsdf_type
        bsdf_type_name = bsdf_type[0].upper() + bsdf_type[1:-5] + " " + bsdf_type[-4:].upper()
        if 'DEFAULT' in self.layout_type:            
            layout.label(text = BSDF.name + "  |  " + bsdf_type_name, translate=False, icon_value=icon)
#---------------------------------------------
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
        asr_mat = material.appleseed
        
        layout.label("BSDF Layers:", icon = 'MATERIAL')

       
        row = layout.row()
        row.template_list("MATERIAL_UL_BSDF_slots", "appleseed_material_layers", asr_mat, "layers", asr_mat, "layer_index", maxrows = 16, type = "DEFAULT")
        
        row = layout.row(align=True)
        row.operator("appleseed.add_matlayer", icon = "ZOOMIN")
        row.operator("appleseed.remove_matlayer", icon = "ZOOMOUT")
                
        if asr_mat.layers:
            current_layer = asr_mat.layers[asr_mat.layer_index]   
            layout.prop(current_layer, "bsdf_type")
#            layout.prop(current_layer, "name", text = "Layer Name")
            
            #Draw the layout if the current type is Lambertian
            if current_layer.bsdf_type == "lambertian_brdf":
                layout.prop(current_layer, "lambertian_weight")
                layout.label("Lambertian Reflectance:")
                
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "lambertian_reflectance", text = "")
                if current_layer.lambertian_use_tex:    
                    col.prop_search(current_layer, "lambertian_diffuse_tex", material, "texture_slots")
                
                col = split.column()
                col.prop(current_layer, "lambertian_use_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "lambertian_multiplier")
                
            elif current_layer.bsdf_type == "ashikhmin_brdf":
                layout.prop(current_layer, "ashikhmin_weight")
                
                layout.label("Diffuse Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "ashikhmin_reflectance", text = "")
                if current_layer.ashikhmin_use_diff_tex:
                    col.prop_search(current_layer, "ashikhmin_diffuse_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "ashikhmin_use_diff_tex", text = "Use Texture", toggle = True)    
                row = layout.row()
                row.prop(current_layer, "ashikhmin_multiplier")
                
                layout.label("Glossy Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()    
                col.prop(current_layer, "ashikhmin_glossy", text = "")
                if current_layer.ashikhmin_use_gloss_tex:
                    col.prop_search(current_layer, "ashikhmin_gloss_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "ashikhmin_use_gloss_tex", text = "Use Texture", toggle = True)
                row = layout.row()
                row.prop(current_layer, "ashikhmin_glossy_multiplier")
                
                col = layout.column()
                col.prop(current_layer, "ashikhmin_fresnel")
                row = layout.row(align=True)
                row.prop(current_layer, "ashikhmin_shininess_u")
                row.prop(current_layer, "ashikhmin_shininess_v")
            
            elif current_layer.bsdf_type == "diffuse_btdf":
                layout.prop(current_layer, "transmission_weight")
                
                layout.label("Transmittance Color:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "transmission_color", text = "")
                if current_layer.transmission_use_tex:    
                    col.prop_search(current_layer, "transmission_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "transmission_use_tex", text = "Use Texture", toggle = True)            
                row = layout.row()
                row.prop(current_layer, "transmission_multiplier", text = "Transmittance Multiplier")
            elif current_layer.bsdf_type == "kelemen_brdf":
                layout.prop(current_layer, "kelemen_weight")
                layout.label("Matte Reflectance:")
                
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "kelemen_matte_reflectance", text = "")
                if current_layer.kelemen_use_diff_tex:
                    col.prop_search(current_layer, "kelemen_diff_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "kelemen_use_diff_tex", text = "Use Texture", toggle = True)            
                row = layout.row()
                row.prop(current_layer, "kelemen_matte_multiplier")
                
                layout.label("Specular Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "kelemen_specular_reflectance", text = "")    
                if current_layer.kelemen_use_spec_tex:
                    col.prop_search(current_layer, "kelemen_spec_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "kelemen_use_spec_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "kelemen_specular_multiplier")
                layout.prop(current_layer, "kelemen_roughness")
            
            elif current_layer.bsdf_type == "microfacet_brdf":
                layout.prop(current_layer, "microfacet_weight")
                layout.prop(current_layer, "microfacet_mdf")
                layout.label("Microfacet Reflectance:")
                
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "microfacet_reflectance", text = "")
                if current_layer.microfacet_use_diff_tex:
                    col.prop_search(current_layer, "microfacet_diff_tex", material, "texture_slots", text = "")
                
                col = split.column()
                col.prop(current_layer, "microfacet_use_diff_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "microfacet_multiplier")
                
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "microfacet_mdf_parameter")
                if current_layer.microfacet_use_spec_tex:
                    col.prop_search(current_layer, "microfacet_spec_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "microfacet_use_spec_tex", text = "Use Texture", toggle = True)
                    
                layout.prop(current_layer, "microfacet_fresnel")
            
            elif current_layer.bsdf_type == "specular_brdf":
                layout.prop(current_layer, "specular_weight")
                layout.label("Specular Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "specular_reflectance", text = "")
                if current_layer.specular_use_gloss_tex:
                    col.prop_search(current_layer, "specular_gloss_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "specular_use_gloss_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "specular_multiplier")
                
            elif current_layer.bsdf_type == "specular_btdf":
                layout.prop(current_layer, "spec_btdf_weight")
                layout.label("Specular Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "spec_btdf_reflectance", text = "")
                if current_layer.spec_btdf_use_tex:
                    col.prop_search(current_layer, "spec_btdf_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "spec_btdf_use_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "spec_btdf_ref_mult")
                
                layout.label("Transmittance Reflectance:")
                split = layout.split(percentage = 0.65)
                col = split.column()
                col.prop(current_layer, "spec_btdf_transmittance", text = "")
                if current_layer.spec_btdf_use_trans_tex:
                    col.prop_search(current_layer, "spec_btdf_trans_tex", material, "texture_slots", text = "")
                col = split.column()
                col.prop(current_layer, "spec_btdf_use_trans_tex", text = "Use Texture", toggle = True)
                layout.prop(current_layer, "spec_btdf_trans_mult")
                
                row = layout.row(align= True)
                row.prop(current_layer, "spec_btdf_from_ior")
                row.prop(current_layer, "spec_btdf_to_ior")
        
        #Per material alpha/bump
        layout.separator()
        layout.label("Per-material Alpha / Bump Mapping", icon = "TEXTURE_SHADED")
        box = layout.box()
        split = box.split(percentage = 0.65)
        col = split.column()
        col.prop(asr_mat, "material_use_bump_tex", text = "Use Bump Texture", toggle= True)
        col = split.column()
        if asr_mat.material_use_bump_tex:
            col.prop(asr_mat, "material_use_normalmap", text = "Normal Map", toggle = True)
        if asr_mat.material_use_bump_tex:
            box.prop_search(asr_mat, "material_bump_tex", material, "texture_slots", text = "")
            box.prop(asr_mat, "material_bump_amplitude")
            
        split = box.split(percentage = 0.65)
        col = split.column()
        col.prop(asr_mat, "material_use_alpha", text = "Use Alpha Texture", toggle = True)
        col = split.column()
        if asr_mat.material_use_alpha:    
            col.prop_search(asr_mat, "material_alpha_map", material, "texture_slots", text = "")
        
                     
        #Light emission properties                  
        layout.separator()
        layout.label("Appleseed Material Light Emission", icon = "LAMP_AREA")
        box = layout.box()
        box.prop(asr_mat, "use_light_emission", "Use Light Emission")
        row = box.row()
        row.active = asr_mat.use_light_emission
        row.prop(asr_mat, "light_emission", text = "Emission Strength")
        row = box.row()
        row.prop(asr_mat, "light_color", text = "Light Color")
        
        layout.separator()
        
        layout.prop(asr_mat, "sss_use_shader", text = "Appleseed FastSSS Shading")
        box = layout.box()
        box.active = asr_mat.sss_use_shader
        
        row = box.row(align=True)
        row.prop(asr_mat, "sss_power", text = "SSS Power")
        row.prop(asr_mat, "sss_scale")
        
        box.label("Albedo Color:")
        row = box.row()
        row.prop(material.subsurface_scattering, "color", text = "")
        row.prop(asr_mat, "sss_albedo_use_tex", text = "Use Texture", toggle = True)
        if asr_mat.sss_albedo_use_tex:
            box.prop_search(asr_mat, "sss_albedo_tex", material, "texture_slots", text = "")
        
        box.separator()
        
        row = box.row(align=True)
        row.prop(asr_mat, "sss_ambient")  
        row.prop(asr_mat, "sss_view_dep")  
        
        row = box.row(align=True)
        row.prop(asr_mat, "sss_diffuse")    
        row.prop(asr_mat, "sss_distortion")
        
        row = box.row(align=True)
        row.prop(asr_mat, "sss_light_samples")
        row.prop(asr_mat, "sss_occlusion_samples")

                
#-------------------        
#Register the script
#-------------------
def register():
    bpy.utils.register_module(__name__)
        
    bpy.types.Object.appleseed_render_layer = bpy.props.StringProperty(name = "Render Layer", description = "The object's contribution to the scene lighting will be constrained to this render layer", default = '')    
    bpy.types.Scene.appleseed_layers = bpy.props.PointerProperty(type=AppleseedRenderLayerProps)
    bpy.types.Material.appleseed = bpy.props.PointerProperty(type = AppleseedMatProps)
    bpy.types.World.appleseed = bpy.props.PointerProperty(type = AppleseedWorldProps)
    
def unregister():
    bpy.utils.unregister_module(__name__)

