
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

import bpy
import multiprocessing

from . import render_layers

try:
    threads = multiprocessing.cpu_count()
    max_threads = threads
except:
    threads = 1
    max_threads = 16

def sun_enumerator( self, context):
    sun = []
    for object in context.scene.objects:
        if object.type == 'LAMP':
            if object.data.type == 'SUN':
                sun.append(( object.name, object.name, ""))
    return sun

def display_mode_changed( self, context):
    if self.display_mode == 'STUDIO':
        context.scene.render.display_mode = 'NONE'
    else:
        context.scene.render.display_mode = self.display_mode

class AppleseedRenderSettings( bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed = bpy.props.PointerProperty(
                name = "Appleseed Render Settings",
                description = "Appleseed render settings",
                type = cls)

        # settings
        cls.display_mode = bpy.props.EnumProperty(  name = "Display",
                                                    description = "Select where rendered images will be displayed",
                                                    items=(( 'NONE', "Keep UI", ""),
                                                           ( 'WINDOWS', "New Window", ""),
                                                           ( 'AREA', "Image Editor", ""),
                                                           ( 'SCREEN', "Full Screen", ""),
                                                           ( 'STUDIO', "Appleseed Studio", "")),
                                                    default = 'AREA',
                                                    update = display_mode_changed)

        
        cls.studio_rendering_mode = bpy.props.EnumProperty( name = "Mode",
                                                            description = "Rendering mode to be used after launching appleseed.studio",
                                                            items = (( "FINAL", "Final", "appleseed.studio will begin rendering in final render mode"),
                                                                     ( "PROGRESSIVE", "Progressive", "appleseed.studio will begin rendering using progrssive render mode")),
                                                            default = "PROGRESSIVE")

        cls.project_path = bpy.props.StringProperty( description = "Where to export project files. Rendered images are saved in .render", subtype = 'DIR_PATH')                                              

        cls.threads = bpy.props.IntProperty( name = "", description = "Number of threads to use for rendering", default = threads, min = 1, max = max_threads)

        cls.generate_mesh_files = bpy.props.BoolProperty( name="Write Meshes to Disk",
                                                 description="If unchecked, the mesh files (.obj files) won't be regenerated",
                                                 default = True)
        
        # sampling
        cls.decorrelate_pixels = bpy.props.BoolProperty( name = "Decorrelate Pixels", description = '', default = False)
        
        cls.pixel_filter = bpy.props.EnumProperty( name = "Filter",
                                                    description = "Pixel filter to use",
                                                    items = [( "box", "Box", "Box" ),
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
                                                    items = [( "uniform", "Uniform", "Uniform" ),
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
                                                      items = [( 'pt', "Path Tracing", "Full Global Illumination"),
                                                               ( 'drt', "Distributed Ray Tracing", "Direct Lighting Only")],
                                                     default = 'pt')

        # drt
        cls.ibl_enable = bpy.props.BoolProperty( name = "Image Based Lighting",
                                                 description = "Image based lighting",
                                                 default = False)
        cls.caustics_enable = bpy.props.BoolProperty( name = "Caustics",
                                                      description = "Caustics",
                                                      default = True)
        cls.direct_lighting = bpy.props.BoolProperty( name = "Direct Lighting",
                                                      description = "Use direct lighting",
                                                      default = True)
        cls.next_event_est = bpy.props.BoolProperty( name = "Next Event Estimation",
                                                     description = "Use next event estimation",
                                                     default = True)
        cls.max_bounces = bpy.props.IntProperty( name = "Max Bounces",
                                                 description = "Max bounces - 0 = Unlimited",
                                                 default = 0,
                                                 min = 0,
                                                 max = 512)
        cls.rr_start = bpy.props.IntProperty( name = "Russian Roulette Start Bounce",
                                              description = "Russian Roulette start bounce",
                                              default = 3,
                                              min = 0,
                                              max = 512)
        
        cls.dl_light_samples = bpy.props.IntProperty( name = "Direct Lighting Light Samples",
                                                      description = "Direct lighting light samples",
                                                      default =  1,
                                                      min = 0,
                                                      max = 512)
        
        cls.ibl_env_samples = bpy.props.IntProperty( name = "IBL Environment Samples",
                                                     description = "Image based lighting environment samples",
                                                     default = 1,
                                                     min = 0,
                                                     max = 512)

        cls.camera_type = bpy.props.EnumProperty( items = [('pinhole', 'Pinhole', 'Pinhole camera - no DoF'),
                                                           ('thinlens', 'Thin lens', 'Thin lens - enables DoF')],
                                                  name = "Camera type",
                                                  description = "Camera lens model",
                                                  default = 'pinhole')
                                            
        cls.premult_alpha = bpy.props.BoolProperty( name = "Premultiplied Alpha",
                                                    description = "Premultiplied alpha",
                                                    default = True)
                                            
        cls.camera_dof = bpy.props.FloatProperty( name = "F-stop", 
                                                  description = "Thin lens camera f-stop value", 
                                                  default = 32.0, 
                                                  min = 0.0, 
                                                  max = 32.0, 
                                                  step = 3, 
                                                  precision = 1)
        
        cls.export_emitting_obj_as_lights = bpy.props.BoolProperty( name = "Export Emitting Objects As Mesh Lights",
                                                                    description = "Export object with light-emitting materials as mesh (area) lights",
                                                                    default = True)
                                                           
        cls.enable_diagnostics = bpy.props.BoolProperty( name = "Enable diagnostics", 
                                                         description = '', 
                                                         default = False)
        
        cls.quality = bpy.props.FloatProperty( name = "Quality", 
                                               description = '', 
                                               default = 3.0, 
                                               min = 0.0, 
                                               max = 20.0, 
                                               precision = 3)

        cls.light_mats_exitance_mult = bpy.props.FloatProperty( name="Global Meshlight Energy Multiplier",
                                                                description="Multiply the exitance of light-emitting materials by this factor",
                                                                min=0.0,
                                                                max=100.0,
                                                                default=1.0)

        # passes
        cls.pass_main = bpy.props.BoolProperty( name = "Main",
                                                description = "Main pass",
                                                default = True)

        cls.pass_z = bpy.props.BoolProperty( name = "Z",
                                             description = "Deliver Z values pass",
                                             default = False)

        cls.pass_normal = bpy.props.BoolProperty( name = "Normal",
                                                  description = "Deliver normal pass",
                                                  default = False)

        cls.pass_uv = bpy.props.BoolProperty( name = "UV",
                                              description = "Deliver texture UV pass",
                                              default = False)
        
    @classmethod
    def unregister( cls):
        del bpy.types.Scene.appleseed

class AppleseedSkySettings( bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed_sky = bpy.props.PointerProperty( name = "Appleseed Sky",
                                                                   description = "Appleseed Sky",
                                                                   type = cls)
                
        cls.env_type = bpy.props.EnumProperty( items = [( "gradient", "Gradient", "Use sky color gradient"),
                                                        ( "constant", "Constant", "Use constant color for sky"),
                                                        ( "constant_hemisphere", "Per-Hemisphere Constant", "Use constant color per hemisphere"),
                                                        ( "latlong_map", "Latitude-Longitude Map", "Use latlong map texture -- texture must be .png or .exr format"), 
                                                        ( "mirrorball_map", "Mirror Ball Map", "Use mirror ball texture -- texture must be .png or .exr format"),  
                                                        ( "sunsky", "Physical Sun/Sky", "")],
                                               name = "Environment Type", 
                                               description = "Select environment type", 
                                               default = "gradient")
                    
        cls.sun_model = bpy.props.EnumProperty( items = [( "hosek_environment_edf", "Hosek-Wilkie", 'Hosek-Wilkie physical sun/sky model'),    
                                                         ( 'preetham_environment_edf', "Preetham", 'Preetham physical sun/sky model')],
                                                         name = "Sun Model", 
                                                         description = "Physical sun/sky model", 
                                                         default = "hosek_environment_edf")
                                        
        cls.env_tex = bpy.props.StringProperty( name = "Environment Texture", 
                                                description = "Texture to influence environment- -- texture must be .png or .exr format", 
                                                default = "")
        
        cls.env_tex_mult = bpy.props.FloatProperty( name = "Radiance Multiplier", 
                                                    description = "", 
                                                    default = 1.0, 
                                                    min = 0.0, 
                                                    max = 2.0)
                
        cls.sun_theta = bpy.props.FloatProperty( name = "Sun theta angle", 
                                                 description = '', 
                                                 default = 0.0, 
                                                 min = -180, 
                                                 max = 180)
        
        cls.sun_phi = bpy.props.FloatProperty( name = "Sun phi angle", 
                                               description = '', 
                                               default = 0.0, 
                                               min = -180, 
                                               max = 180)        
        
        cls.sun_lamp = bpy.props.EnumProperty( items = sun_enumerator, 
                                               name = "Sun Lamp", 
                                               description = "Sun lamp to export")                   
        
        cls.horiz_shift = bpy.props.FloatProperty( name = "Horizon shift", 
                                                   description = '', 
                                                   default = 0.0, 
                                                   min = -2.0, 
                                                   max = 2.0)
        
        cls.luminance_multiplier = bpy.props.FloatProperty( name = "Sky luminance multiplier", 
                                                            description ='', 
                                                            default = 1.0, 
                                                            min = 0.0, 
                                                            max = 20.0)
        
        cls.radiance_multiplier = bpy.props.FloatProperty( name = "Sun radiance multiplier", 
                                                           description = '', 
                                                           default = 0.05, 
                                                           min = 0.0, 
                                                           max = 1.0)
        
        cls.saturation_multiplier = bpy.props.FloatProperty( name= "Saturation multiplier", 
                                                             description = '', 
                                                             default = 1.0, 
                                                             min = 0.0, 
                                                             max = 10.0)
        
        cls.turbidity = bpy.props.FloatProperty( name = "Turbidity", 
                                                 description = '', 
                                                 default = 4.0, 
                                                 min = 0.0, 
                                                 max = 10.0)

        cls.turbidity_max = bpy.props.FloatProperty( name = "Turbidity max", 
                                                     description = '', 
                                                     default = 6.0, 
                                                     min = 0, 
                                                     max = 10.0)

        cls.turbidity_min = bpy.props.FloatProperty( name = "Turbidity min", 
                                                     description = '', 
                                                     default = 2.0, 
                                                     min = 0, 
                                                     max = 10.0)
        
        cls.ground_albedo = bpy.props.FloatProperty( name = "Ground albedo", 
                                                     description = '', 
                                                     default = 0.3, 
                                                     min = 0.0, 
                                                     max = 1.0)

    @classmethod
    def unregister( cls):
        del bpy.types.Scene.appleseed_sky

def register():
    bpy.types.Scene.appleseed_layers = bpy.props.PointerProperty( type = render_layers.AppleseedRenderLayerProps)

def unregister():
    del bpy.types.Scene.appleseed
