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

import bpy
from bpy.props import *

import os
import math

import mathutils

__bpydoc__ = """
Fulldome Tool Addon by Jesse Cole Wilmot
FH Flensburg 2012/13


"""


class OBJECT_OT_create_movieplane(bpy.types.Operator):
    """Creates Movieplane"""
    bl_idname="object.create_movieplane"
    bl_label="Create a movieplane"
    bl_options = {'REGISTER'}

    objName = "My Movieplane"



    def execute(self, context):
        if bpy.context.scene.fulldome.use_alphatexture:
            alphacolormovie = bpy.data.materials.new('AlphaColorMovie')
            if bpy.context.scene.fulldome.set_MovieShine:
                alphacolormovie.emit = 1
            alphacolormovie.diffuse_color = (1,1,0)
            alphacolormovie.use_transparency = 1
            alphacolormovie.alpha = 0
            alphacolormovie.specular_intensity = 0

            atex = bpy.data.textures.new("Alphakanal Movie", type = "IMAGE")
            bpy.data.materials[alphacolormovie.name].texture_slots.add()
            bpy.data.materials[alphacolormovie.name].texture_slots[0].texture = atex
            bpy.data.materials[alphacolormovie.name].texture_slots[0].use_rgb_to_intensity = True
            bpy.data.materials[alphacolormovie.name].texture_slots[0].use_stencil = True
            bpy.data.materials[alphacolormovie.name].texture_slots[0].use_map_alpha = True

            if bpy.context.scene.fulldome.alphamovie_texture_path == '':
                self.report({'ERROR'}, "No selected Alphatexture!")
            else:
                alphamovie = bpy.data.images.load(bpy.context.scene.fulldome['alphamovie_texture_path'])
                bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image = alphamovie
                alpmoviewidth = bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image.pixels.data.size[0] / 1000
                alpmovieheight = bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image.pixels.data.size[1] / 1000
                bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image_user.frame_duration = alphamovie.frame_duration

        
            mtex = bpy.data.textures.new("Colorkanal Movie", type = "IMAGE")
            bpy.data.materials[alphacolormovie.name].texture_slots.add()
            bpy.data.materials[alphacolormovie.name].texture_slots[1].texture = mtex

            if bpy.context.scene.fulldome.movie_texture_path == '':
                self.report({'ERROR'}, "No selected Movietexture!")
                moviewidth = 1
                movieheight = 1
            else:
                movieImage = bpy.data.images.load(bpy.context.scene.fulldome['movie_texture_path'])
                bpy.data.materials[alphacolormovie.name].texture_slots[1].texture.image = movieImage
                moviewidth = bpy.data.materials[alphacolormovie.name].texture_slots[1].texture.image.pixels.data.size[0] / 1000
                movieheight = bpy.data.materials[alphacolormovie.name].texture_slots[1].texture.image.pixels.data.size[1] / 1000
                bpy.data.materials[alphacolormovie.name].texture_slots[1].texture.image_user.frame_duration = movieImage.frame_duration
        else:
            alphacolormovie = bpy.data.materials.new('AlphaColorMovie')
            if bpy.context.scene.fulldome.set_MovieShine:
                alphacolormovie.emit = 1
            alphacolormovie.diffuse_color = (1,1,0)
            alphacolormovie.use_transparency = 1
            alphacolormovie.alpha = 1
            alphacolormovie.specular_intensity = 0
        
            mtex = bpy.data.textures.new("Colorkanal Movie", type = "IMAGE")
            bpy.data.materials[alphacolormovie.name].texture_slots.add()
            bpy.data.materials[alphacolormovie.name].texture_slots[0].texture = mtex

            if bpy.context.scene.fulldome.movie_texture_path == '':
                self.report({'ERROR'}, "No selected Movietexture!")
                moviewidth = 1
                movieheight = 1
            else:
                movieImage = bpy.data.images.load(bpy.context.scene.fulldome['movie_texture_path'])
                bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image = movieImage
                moviewidth = bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image.pixels.data.size[0] / 1000
                movieheight = bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image.pixels.data.size[1] / 1000
                bpy.data.materials[alphacolormovie.name].texture_slots[0].texture.image_user.frame_duration = movieImage.frame_duration

        #Creates Movieplane
        bpy.ops.mesh.primitive_plane_add(location=(2,0,1))
        ob = bpy.context.active_object
        ob.name = "Movie_Plane"
        if not bpy.context.scene.fulldome.set_MovieSize:
            moviewidth = 1
            movieheight = 1
        bpy.ops.transform.resize(value=(moviewidth,movieheight,1))


        movpl = ob.data
        #adding of color with textur
        movpl.materials.append(alphacolormovie)
        #bpy.ops.transform.rotate(value = (1.570797,), axis=(0,1,0))
        #bpy.ops.transform.rotate(value = (1.570797,), axis=(1,0,0))
        bpy.data.objects['Movie_Plane'].location[0] = 2
        bpy.data.objects['Movie_Plane'].location[1] = 0
        bpy.data.objects['Movie_Plane'].location[2] = 1
        bpy.data.objects['Movie_Plane'].rotation_euler[0] = 1.570797
        bpy.data.objects['Movie_Plane'].rotation_euler[2] = 1.570797

        return {'FINISHED'}



class OBJECT_OT_create_mirrorcam(bpy.types.Operator):
    """Creates Fulldome Rig"""
    bl_idname="object.create_mirrorcam"
    bl_label="Create a mirrorcam"
    bl_options = {'REGISTER'}

    objName = "my_mirrorcam"
    handler = None
    exists = False


    def execute(self, context):

    # Create empty
        bpy.ops.object.add(type='EMPTY')
        bpy.ops.transform.translate(value=(0,0,0))
        empty = bpy.context.active_object
        empty.name = "FulldomeCameraRig"
        # On this position the existance of an empty with the same name is checked, to prevent multiple instances. Furtherone just the settings are actualized
        if not empty.name == "FulldomeCameraRig":
            bpy.ops.object.delete()
            if bpy.context.scene.fulldome.set_SkyShine:
                bpy.data.materials['BlueSkySphere'].emit = 1
            else:
                bpy.data.materials['BlueSkySphere'].emit = 0
            bpy.data.materials['BlueSkySphere'].texture_slots[0].use = bpy.context.scene.fulldome.use_skytexture
            if bpy.context.scene.fulldome.texture_path_skysphere == '':
                self.report({'ERROR'}, "No selected Skytexture!")
            else:
                skyImageTex = bpy.data.images.load(bpy.context.scene.fulldome['texture_path_skysphere'])
                bpy.data.materials['BlueSkySphere'].texture_slots[0].texture.image = skyImageTex
                skymoviewidth = bpy.data.materials['BlueSkySphere'].texture_slots[0].texture.image.pixels.data.size[0] / 1000
                skymovieheight = bpy.data.materials['BlueSkySphere'].texture_slots[0].texture.image.pixels.data.size[1] / 1000
                bpy.data.materials['BlueSkySphere'].texture_slots[0].texture.image_user.frame_duration = skyImageTex.frame_duration
            if bpy.context.scene.fulldome.use_orthographic:
                bpy.data.objects["fulldomeCam"].location = (0,0,0.2)
                bpy.data.objects["fulldomeCam"].scale = (-0.1,0.1,0.1)
                bpy.data.objects["fulldomeCam"].data.name = 'FulldomeOrthoCamera'
                bpy.data.objects["fulldomeCam"].data.type = 'ORTHO'
                bpy.data.objects["fulldomeCam"].data.ortho_scale = 0.85
                bpy.data.objects["fulldomeCam"].data.clip_start = 0.001
                bpy.data.objects["fulldomeCam"].data.clip_end = 1
            else:
                bpy.data.objects["fulldomeCam"].location = (0,0,0.853)
                bpy.data.objects["fulldomeCam"].scale = (-1,1,1)
                bpy.data.objects["fulldomeCam"].data.name = 'FulldomePerspCamera'
                bpy.data.objects["fulldomeCam"].data.type = 'PERSP'
                bpy.data.objects["fulldomeCam"].data.lens = 36
                bpy.data.objects["fulldomeCam"].data.clip_start = 0.001
                bpy.data.objects["fulldomeCam"].data.clip_end = 3
            # rendersettings are actualized here 
            if (bpy.context.scene.fulldome.render_size == 'OPT_A'):
                rend_resolution = 1024
            if (bpy.context.scene.fulldome.render_size == 'OPT_B'):
                rend_resolution = 2048
            if (bpy.context.scene.fulldome.render_size == 'OPT_C'):
                rend_resolution = 3072
            if (bpy.context.scene.fulldome.render_size == 'OPT_D'):
                rend_resolution = 4096
            if (bpy.context.scene.fulldome.render_size == 'OPT_E'):
                rend_resolution = 8192

            bpy.context.scene.render.resolution_x = rend_resolution
            bpy.context.scene.render.resolution_y = rend_resolution

        else:
            empty.hide = 1
            self.handler = empty

            # Create mirrormaterial
            redm = bpy.data.materials.new('RedFulldomeMirror')
            redm.diffuse_color = (1,0,0)
            redm.raytrace_mirror.use = 1
            redm.raytrace_mirror.reflect_factor = 100

             # Create cubematerial
            black = bpy.data.materials.new('BlackCameraCube')
            black.diffuse_color = (0,0,0)
            black.diffuse_intensity = 0.1
            black.specular_intensity = 0.01

            # Create skyspherematerial
            blue = bpy.data.materials.new('BlueSkySphere')    
            blue.diffuse_color = (0.530,0.607,1)
            blue.diffuse_intensity = 1
            if bpy.context.scene.fulldome.set_SkyShine:
                blue.emit = 1
            else:
                blue.emit = 0
            skytex = bpy.data.textures.new("SkyColorkanal Movie", type = "IMAGE")
            bpy.data.materials[blue.name].texture_slots.add()
            bpy.data.materials[blue.name].texture_slots[0].texture = skytex
            bpy.data.materials['BlueSkySphere'].texture_slots[0].use = bpy.context.scene.fulldome.use_skytexture
            if bpy.context.scene.fulldome.texture_path_skysphere == '':
                self.report({'ERROR'}, "No selected Skytexture!")
            else:
                skyImageTex = bpy.data.images.load(bpy.context.scene.fulldome['texture_path_skysphere'])
                bpy.data.materials[blue.name].texture_slots[0].texture.image = skyImageTex
                skymoviewidth = bpy.data.materials[blue.name].texture_slots[0].texture.image.pixels.data.size[0] / 1000
                skymovieheight = bpy.data.materials[blue.name].texture_slots[0].texture.image.pixels.data.size[1] / 1000
                bpy.data.materials[blue.name].texture_slots[0].texture.image_user.frame_duration = skyImageTex.frame_duration
            
            #Create reflecting MirrorSphere so that the Camera gets a 360 degres roundview
            bpy.ops.mesh.primitive_uv_sphere_add(segments = 64, ring_count = 32, location=(0,0,-0.42421))  
            bpy.ops.transform.resize(value=(0.6,0.6,0.6))
            bpy.ops.object.shade_smooth()

            ob = bpy.context.object
            ob.name = 'MirrorSphere'
            ob.parent = self.handler
            #ob.hide = 1
            ob.hide_select = 1
            mir = ob.data
            mir.materials.append(redm)

            # Create Skysphere 
            bpy.ops.mesh.primitive_uv_sphere_add(segments = 64, ring_count = 32, location=(0,0,0))
            bpy.ops.transform.resize(value=(60,60,60))
            bpy.ops.object.shade_smooth()

            ob = bpy.context.object
            ob.name = 'Skysphere'
            ob.parent = self.handler
            ob.hide = 1
            ob.hide_select = 1
            skysp = ob.data
            skysp.materials.append(blue)
            if bpy.context.scene.fulldome.use_orthographic:
                bpy.ops.object.camera_add(location=(0,0,0.2))#orthographic camerasetting is similar to the Ott-Planetary camera rig
                bpy.ops.object.rotation_clear()
                cam = bpy.context.active_object
                cam.name = "fulldomeCam"
                bpy.data.objects[cam.name].scale = (-0.1,0.1,0.1)
                bpy.data.objects[cam.name].data.name = 'FulldomeOrthoCamera'
                bpy.data.objects[cam.name].data.type = 'ORTHO'
                bpy.data.objects[cam.name].data.ortho_scale = 0.85
                bpy.data.objects[cam.name].data.clip_start = 0.001
                bpy.data.objects[cam.name].data.clip_end = 1
            else:
                bpy.ops.object.camera_add(location=(0,0,0.853)) #perspektiv camerasetting shows more from the bottom around
                bpy.ops.object.rotation_clear()
                cam = bpy.context.active_object
                cam.name = "fulldomeCam"
                bpy.data.objects[cam.name].scale = (-1,1,1)
                bpy.data.objects[cam.name].data.name = 'FulldomePerspCamera'
                bpy.data.objects[cam.name].data.type = 'PERSP'
                bpy.data.objects[cam.name].data.lens = 36
                bpy.data.objects[cam.name].data.clip_start = 0.001
                bpy.data.objects[cam.name].data.clip_end = 3
                

            scene = bpy.context.scene
            scene.camera = cam
            cam.parent = self.handler
            cam.hide = 1
            cam.hide_select = 1

            # additional rendersettings have to be added here and above where the settings are actualizedn as well as in:  _init__.py
            rend_resolution = 1024

            if (bpy.context.scene.fulldome.render_size == 'OPT_A'):
                rend_resolution = 1024

            if (bpy.context.scene.fulldome.render_size == 'OPT_B'):
                rend_resolution = 2048

            if (bpy.context.scene.fulldome.render_size == 'OPT_C'):
                rend_resolution = 3072

            if (bpy.context.scene.fulldome.render_size == 'OPT_D'):
                rend_resolution = 4096

            if (bpy.context.scene.fulldome.render_size == 'OPT_E'):
                rend_resolution = 8192

            bpy.context.scene.render.resolution_x = rend_resolution
            bpy.context.scene.render.resolution_y = rend_resolution
            bpy.context.scene.render.display_mode = "WINDOW"   # renderresult in new window
            #bpy.context.scene.render.display_mode = "AREA"    # renderresult in actual windowarea
            bpy.context.scene.render.resolution_percentage = 100
            bpy.context.scene.render.use_stamp = 1
            #bpy.context.scene.render.
            bpy.context.scene.render.fps = 30   # here the framerate is set to the usual 30 fps. If you prefer other settins feel free to change 
            bpy.context.scene.render.use_stamp_note = 1
            bpy.context.scene.render.use_stamp_filename = False
            bpy.context.scene.render.stamp_note_text = "Fulldome Tool Addon by Jesse Cole Wilmot" # would be nice if you would leave this note as it is.. programming this addon was work enough and I did not get any money for it. If you like this Addon feel free to contact me. Currently I might still be somehow related to the Fh Flensburg Medieninformatik, Professor Hoefs, Prof. Hartmann, Mr.Zimmermann and Mr. Hiep should have an idea to get hold on me

            # Create blackCameraCube
            bpy.ops.mesh.primitive_cube_add(location=(0,0,-1))
            ob = bpy.context.object
            ob.name = "CameraCube"
            ob.parent = self.handler
            ob.hide_select = 1
            cube = ob.data
            cube.materials.append(black)
            bpy.ops.object.select_all()
            bpy.data.objects['FulldomeCameraRig'].location[0] = 0
            bpy.data.objects['FulldomeCameraRig'].location[1] = 0
            bpy.data.objects['FulldomeCameraRig'].location[2] = 0
        return {'FINISHED'}



class OBJECT_OT_clear_scene(bpy.types.Operator):
    """Clear Scene"""
    bl_idname="object.clear_scene"
    bl_label="Clear Szene"
    bl_options = {'REGISTER'}

    objName = "my_mirrorcam"
    handler = None
    exists = False


    def execute(self, context):
        if bpy.context.scene.fulldome.activate_Clear:
            bpy.ops.object.select_all()
            bpy.ops.object.select_all()
            bpy.ops.object.delete()
            #here the created FulldomeCameraRig is set visible and selectable so that it can be deleted 
            if bpy.context.scene.fulldome.clear_complete_Rig:
                bpy.context.scene.fulldome.clear_complete_Rig = False
                bpy.data.objects['CameraCube'].hide_select = False
                bpy.data.objects['MirrorSphere'].hide_select = False
                bpy.data.objects['Skysphere'].hide_select = False
                bpy.data.objects['Skysphere'].hide = False
                bpy.data.objects['fulldomeCam'].hide_select = False
                bpy.data.objects['fulldomeCam'].hide = False
                bpy.data.objects['FulldomeCameraRig'].hide_select = False
                bpy.data.objects['FulldomeCameraRig'].hide = False
                bpy.ops.object.select_all()
                bpy.ops.object.select_all()
                bpy.ops.object.select_all()
                bpy.ops.object.delete()
                bpy.data.materials.remove(bpy.data.materials['BlueSkySphere'])
                bpy.data.materials.remove(bpy.data.materials['BlackCameraCube'])
                bpy.data.materials.remove(bpy.data.materials['RedFulldomeMirror'])
            else:
                bpy.ops.object.select_all()
                bpy.ops.object.select_all()
                bpy.ops.object.delete()
            bpy.context.scene.fulldome.activate_Clear = False
            bpy.context.scene.fulldome.clear_complete_Rig = False
            bpy.ops.object.select_all()
            bpy.ops.object.delete()

        return {'FINISHED'}


class OBJECT_OT_create_text_in_space(bpy.types.Operator):
    """Creates 3D Text in Space"""
    bl_idname="object.create_text_in_space"
    bl_label="Create text in space"
    bl_options = {'REGISTER'}

    objName = "my_mirrorcam"
    handler = None
    exists = False


    def execute(self, context):
        # Create 3D Textobject
        if bpy.context.scene.fulldome.set_TextObject_path == '':
                self.report({'ERROR'}, "No selected Textfile!")
        else:
            SkyText = bpy.data.texts.load(bpy.context.scene.fulldome['set_TextObject_path'])
            bpy.ops.object.text_add(location=(5,5,5))
            ob = bpy.context.object
            TextObjekt = bpy.context.object
            ob.name = 'Sky_Text'
            ob = SkyText
            bpy.data.objects['Sky_Text'].scale = (-1,1,1)
            
            bpy.ops.object.mode_set(mode='EDIT', toggle=False)
            skytextstring = SkyText.as_string()
            bpy.ops.font.text_insert(text= skytextstring, accent= False)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.context.object.data.name = 'FulldomeText'
            TextObjDataName = bpy.context.object.data.name
            #Changes 2D to 3D text
            if bpy.context.scene.fulldome.set_TextObject:
                bpy.data.curves[TextObjDataName].offset = 0.011
                bpy.data.curves[TextObjDataName].extrude = 0.2
            #Creates complete sample setting with texture and two lamps from underneath 
            if bpy.context.scene.fulldome.set_sampleSetting:
                bpy.ops.object.lamp_add(type='SUN', location=(-2.18586,28.98223,-1.54069), rotation =(4.23209,0.50001,-0.283137))
                sunlamp = bpy.context.object
                sunlamp.name = 'SunLamp'
                bpy.ops.object.lamp_add(type='POINT', location=(-0.57539,45.39541,-0.30459))
                pointlamp = bpy.context.object
                pointlamp.name = 'PointLamp'
                
                stonet = bpy.data.materials.new('StoneColor')
                stonet.diffuse_color = (0.458,0.439,0.439)
                stonet.diffuse_intensity = 0.614
                stonet.emit = 0.32
                stonetex = bpy.data.textures.new("StoneTexture", type = "DISTORTED_NOISE")
                bpy.data.materials[stonet.name].texture_slots.add()
                bpy.data.materials[stonet.name].texture_slots[0].texture = stonetex
                bpy.data.materials[stonet.name].texture_slots[0].texture.contrast = 4.162
                bpy.data.materials[stonet.name].texture_slots[0].texture.saturation = 0
                bpy.data.materials[stonet.name].texture_slots[0].texture.intensity = 1.264
                bpy.data.materials[stonet.name].texture_slots[0].texture.distortion = 10
                bpy.data.materials[stonet.name].texture_slots[0].texture.noise_scale = 0.86
                bpy.data.materials[stonet.name].texture_slots[0].texture.nabla = 0.001
                bpy.data.materials[stonet.name].texture_slots[0].scale = (80,10,60)
                bpy.data.materials[stonet.name].texture_slots[0].use_map_color_diffuse = True
                bpy.data.materials[stonet.name].texture_slots[0].diffuse_color_factor = 1
                bpy.data.materials[stonet.name].texture_slots[0].use_map_normal = True
                bpy.data.materials[stonet.name].texture_slots[0].normal_factor = 0.1
                bpy.data.materials[stonet.name].texture_slots[0].use_map_displacement = True
                bpy.data.materials[stonet.name].texture_slots[0].displacement_factor = 0.0002
                bpy.data.materials[stonet.name].texture_slots[0].use_stencil = True
                bpy.data.materials[stonet.name].texture_slots[0].color = (0.254717081785202, 0.21599413454532623, 0.24963471293449402)
                bpy.data.materials[stonet.name].texture_slots[0].blend_type = 'OVERLAY'
                TextObjekt.data.materials.append(stonet)

        return {'FINISHED'}


#panel design is following

class VIEW3D_OT_fulldome_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_label = "Fulldome Tools"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene

        col = layout.column()
        col = layout.column(align=True)
        col.prop(scene.fulldome, "set_TextObject")
        col.prop(scene.fulldome, "set_TextObject_path")
        col.prop(scene.fulldome, "set_sampleSetting")
        layout.operator("object.create_text_in_space", "Create Text In Space")

        col = layout.column()
        col = layout.column(align=True)
        col.prop(scene.fulldome, "set_MovieShine")
        col.prop(scene.fulldome, "set_MovieSize")
        col.prop(scene.fulldome, "movie_texture_path")
        col.prop(scene.fulldome, "use_alphatexture")
        col = layout.column()
        col = layout.column(align=True)
        col.enabled = scene.fulldome.use_alphatexture
        col.prop(scene.fulldome, "alphamovie_texture_path")


        # create a basemesh
        col = layout.column()
        col = layout.column(align=True)
        layout.operator("object.create_movieplane", "Create Movieplane")
        
        col = layout.column()
        col = layout.column(align= True)
        col.prop(scene.fulldome, "set_SkyShine")
        col.prop(scene.fulldome, "use_skytexture")
        col = layout.column()
        col = layout.column(align= True)
        col.enabled = scene.fulldome.use_skytexture
        col.prop(scene.fulldome, "texture_path_skysphere")
        col = layout.column()
        col = layout.column(align= True)
        col.prop(scene.fulldome, "render_size")
        col.prop(scene.fulldome, "use_orthographic")
        layout.operator("object.create_mirrorcam", "Set Fulldome Camera Rig")
        


        col = layout.column(align= True)
        col.prop(scene.fulldome, "activate_Clear") 
        col = layout.column(align=True)
        col.enabled = scene.fulldome.activate_Clear
        col.prop(scene.fulldome, "clear_complete_Rig")
        layout.operator("object.clear_scene", "Clear Szene")


