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
    "name": "Hair Lab",
    "author": "Ondrej Raha(lokhorn)",
    "version": (0,5),
    "blender": (2, 6, 0),
    "api": 42149,
    "location": "View3D > Tool Shelf > Hair Preset Panel",
    "description": "Creates particle hair with material",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Object/Hair_Lab",
    "tracker_url": "",
    "category": "Object"}


import bpy
from bpy.props import *

# Returns the action we want to take
def getActionToDo(obj):
    if not obj or obj.type != 'MESH':
        return 'NOT_OBJ_DO_NOTHING'
    elif obj.type == 'MESH':
        return 'GENERATE'
    else:
        return "DO_NOTHING"

# TO DO
"""
class saveSelectionPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    bl_label = "Selection Save"
    bl_options = {"DEFAULT_CLOSED"}
    bl_context = "particlemode"
    

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        col.operator("save.selection", text="Save Selection 1")
"""
class HairLabPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    bl_label = "Hair Preset"
    bl_context = "objectmode"
    

    def draw(self, context):
        active_obj = bpy.context.active_object
        active_scn = bpy.context.scene.name
        layout = self.layout
        col = layout.column(align=True)
        
        WhatToDo = getActionToDo(active_obj)
      
        
        if WhatToDo == "GENERATE":
            col.operator("hair.generate_hair", text="Create Hair")

            col.prop(context.scene, "hair_type")
        else:
            col.label(text="Select mesh object")
        
        if active_scn == "TestHairScene":
            col.operator("hair.switch_back", text="Switch back to scene")
        else:
            col.operator("hair.test_scene", text="Create Test Scene")

# TO DO
"""
class saveSelection(bpy.types.Operator):
    bl_idname = "save.selection"
    bl_label = "Save Selection"
    bl_description = "Save selected particles"
    bl_register = True
    bl_undo = True
    
    def execute(self, context):
        
        return {"FINISHED"}
"""
class testScene(bpy.types.Operator):
    bl_idname = "hair.switch_back"
    bl_label = "Switch back to scene"
    bl_description = "If you want keep this scene, switch scene in info window"
    bl_register = True
    bl_undo = True
    
    def execute(self, context):
        scene = bpy.context.scene
        bpy.data.scenes.remove(scene)
        
        return {"FINISHED"}
        
        
class testScene(bpy.types.Operator):
    bl_idname = "hair.test_scene"
    bl_label = "Create test scene"
    bl_description = "You can switch scene in info panel"
    bl_register = True
    bl_undo = True
    
    def execute(self, context):
        # add new scene
        bpy.ops.scene.new(type="NEW")
        scene = bpy.context.scene
        scene.name = "TestHairScene"
        # render settings
        render = scene.render
        render.resolution_x = 1080
        render.resolution_y = 1080
        render.resolution_percentage = 50
        # add new world
        world = bpy.data.worlds.new("HairWorld")
        scene.world = world
        world.use_sky_blend = True
        world.zenith_color = (0.25,0.25,0.25)
        
        # add sphere
        bpy.ops.mesh.primitive_uv_sphere_add(size=0.1)
        
        # add text
        bpy.ops.object.text_add(location=(-0.321,0,-0.307), rotation =(1.571,0,0))
        text = bpy.context.active_object
        text.scale = (0.08,0.08,0.08)
        text.data.body = "1 units is 1 meter!!!"
        
        # add material to text
        textMaterial = bpy.data.materials.new('textMaterial')
        text.data.materials.append(textMaterial)
        textMaterial.use_shadeless = True
        
        # add camera
        bpy.ops.object.camera_add(location = (0,-1,0),rotation = (1.571,0,0))
        cam = bpy.context.active_object.data
        cam.lens = 50
        cam.draw_size = 0.1
        
        # add spot lamp
        bpy.ops.object.lamp_add(type="SPOT", location = (-0.7,-0.5,0.3), rotation =(1.223,0,-0.960))
        lamp1 = bpy.context.active_object.data
        lamp1.name = "Key Light"
        lamp1.energy = 1.5
        lamp1.distance = 1.5
        lamp1.shadow_buffer_soft = 5
        lamp1.shadow_buffer_size = 8192
        lamp1.shadow_buffer_clip_end = 1.5
        lamp1.spot_blend = 0.5
        
        # add spot lamp2
        bpy.ops.object.lamp_add(type="SPOT", location = (0.7,-0.6,0.1), rotation =(1.571,0,0.785))
        lamp2 = bpy.context.active_object.data
        lamp2.name = "Fill Light"
        lamp2.color = (0.874,0.874,1)
        lamp2.energy = 0.5
        lamp2.distance = 1.5
        lamp2.shadow_buffer_soft = 5
        lamp2.shadow_buffer_size = 4096
        lamp2.shadow_buffer_clip_end = 1.5
        lamp2.spot_blend = 0.5
        
        # light Rim
        """
        # add spot lamp3
        bpy.ops.object.lamp_add(type="SPOT", location = (0.191,0.714,0.689), rotation =(0.891,0,2.884))
        lamp3 = bpy.context.active_object.data
        lamp3.name = "Rim Light"
        lamp3.color = (0.194,0.477,1)
        lamp3.energy = 3
        lamp3.distance = 1.5
        lamp3.shadow_buffer_soft = 5
        lamp3.shadow_buffer_size = 4096
        lamp3.shadow_buffer_clip_end = 1.5
        lamp3.spot_blend = 0.5
        """
        
        return {"FINISHED"}


class GenerateHair(bpy.types.Operator):
    bl_idname = "hair.generate_hair"
    bl_label = "Generate Hair"
    bl_description = "Create a Hair"
    bl_register = True
    bl_undo = True
    
    def execute(self, context):
        # Make variable that is the current .blend file main data blocks
        blend_data = context.blend_data
        ob = bpy.context.active_object
        scene = context.scene

        ######################################################################
        ########################Long Red Straight Hair########################
        if scene.hair_type == '0':              
            
            ###############Create New Material##################
            # add new material
            hairMaterial = bpy.data.materials.new('LongRedStraightHairMat')
            ob.data.materials.append(hairMaterial)
            
            #Material settings
            hairMaterial.preview_render_type = "HAIR"
            hairMaterial.diffuse_color = (0.287, 0.216, 0.04667)
            hairMaterial.specular_color = (0.604, 0.465, 0.136)
            hairMaterial.specular_intensity = 0.3
            hairMaterial.ambient = 0
            hairMaterial.use_cubic = True
            hairMaterial.use_transparency = True
            hairMaterial.alpha = 0
            hairMaterial.use_transparent_shadows = True
            #strand
            hairMaterial.strand.use_blender_units = True
            hairMaterial.strand.root_size = 0.00030
            hairMaterial.strand.tip_size = 0.00010
            hairMaterial.strand.size_min = 0.7
            hairMaterial.strand.width_fade = 0.1
            hairMaterial.strand.shape = 0.061
            hairMaterial.strand.blend_distance = 0.001
            
            
            # add texture
            hairTex = bpy.data.textures.new("LongRedStraightHairTex", type='BLEND')
            hairTex.use_preview_alpha = True
            hairTex.use_color_ramp = True
            ramp = hairTex.color_ramp
            rampElements = ramp.elements
            rampElements[0].position = 0
            rampElements[0].color = [0.114,0.05613,0.004025,0.38]
            rampElements[1].position = 1
            rampElements[1].color = [0.267,0.155,0.02687,0]
            rampElement1 = rampElements.new(0.111)
            rampElement1.color = [0.281,0.168,0.03157,0.65]
            rampElement2 = rampElements.new(0.366)
            rampElement2.color = [0.288,0.135,0.006242,0.87]
            rampElement3 = rampElements.new(0.608)
            rampElement3.color = [0.247,0.113,0.006472,0.8]
            rampElement4 = rampElements.new(0.828)
            rampElement4.color = [0.253,0.09919,0.01242,0.64]
    
            # add texture to material
            MTex = hairMaterial.texture_slots.add()
            MTex.texture = hairTex
            MTex.texture_coords = "STRAND"
            MTex.use_map_alpha = True
            
            
            
            ###############Create Particles##################
            # Add new particle system
            
            NumberOfMaterials = 0
            for i in ob.data.materials:
                NumberOfMaterials +=1
            
            
            bpy.ops.object.particle_system_add()
            #Particle settings setting it up!
            hairParticles = bpy.context.object.particle_systems.active
            hairParticles.name = "LongRedStraightHairPar"
            hairParticles.settings.type = "HAIR"
            hairParticles.settings.use_advanced_hair = True
            hairParticles.settings.count = 500
            hairParticles.settings.normal_factor = 0.05
            hairParticles.settings.factor_random = 0.001
            hairParticles.settings.use_dynamic_rotation = True
            
            hairParticles.settings.material = NumberOfMaterials
            
            hairParticles.settings.use_strand_primitive = True
            hairParticles.settings.use_hair_bspline = True
            hairParticles.settings.render_step = 5
            hairParticles.settings.length_random = 0.5
            hairParticles.settings.draw_step = 5
            # children
            hairParticles.settings.child_type = "INTERPOLATED"
            hairParticles.settings.create_long_hair_children = True
            hairParticles.settings.clump_factor = 0.55
            hairParticles.settings.roughness_endpoint = 0.005
            hairParticles.settings.roughness_end_shape = 5
            hairParticles.settings.roughness_2 = 0.003
            hairParticles.settings.roughness_2_size = 0.230
        
        
        ######################################################################
        ########################Long Brown Curl Hair##########################
        if scene.hair_type == '1':
            ###############Create New Material##################
            # add new material
            hairMaterial = bpy.data.materials.new('LongBrownCurlHairMat')
            ob.data.materials.append(hairMaterial)
            
            #Material settings
            hairMaterial.preview_render_type = "HAIR"
            hairMaterial.diffuse_color = (0.662, 0.518, 0.458)
            hairMaterial.specular_color = (0.351, 0.249, 0.230)
            hairMaterial.specular_intensity = 0.3
            hairMaterial.specular_hardness = 100
            hairMaterial.use_specular_ramp = True
            
            ramp = hairMaterial.specular_ramp
            rampElements = ramp.elements
            rampElements[0].position = 0
            rampElements[0].color = [0.0356,0.0152,0.009134,0]
            rampElements[1].position = 1
            rampElements[1].color = [0.352,0.250,0.231,1]
            rampElement1 = rampElements.new(0.255)
            rampElement1.color = [0.214,0.08244,0.0578,0.31]
            rampElement2 = rampElements.new(0.594)
            rampElement2.color = [0.296,0.143,0.0861,0.72]
            
            hairMaterial.ambient = 0
            hairMaterial.use_cubic = True
            hairMaterial.use_transparency = True
            hairMaterial.alpha = 0
            hairMaterial.use_transparent_shadows = True
            #strand
            hairMaterial.strand.use_blender_units = True
            hairMaterial.strand.root_size = 0.00030
            hairMaterial.strand.tip_size = 0.00015
            hairMaterial.strand.size_min = 0.450
            hairMaterial.strand.width_fade = 0.1
            hairMaterial.strand.shape = 0.02
            hairMaterial.strand.blend_distance = 0.001
            
            
            # add texture
            hairTex = bpy.data.textures.new("HairTex", type='BLEND')
            hairTex.name = "LongBrownCurlHairTex"
            hairTex.use_preview_alpha = True
            hairTex.use_color_ramp = True
            ramp = hairTex.color_ramp
            rampElements = ramp.elements
            rampElements[0].position = 0
            rampElements[0].color = [0.009721,0.006049,0.003677,0.38]
            rampElements[1].position = 1
            rampElements[1].color = [0.04231,0.02029,0.01444,0.16]
            rampElement1 = rampElements.new(0.111)
            rampElement1.color = [0.01467,0.005307,0.00316,0.65]
            rampElement2 = rampElements.new(0.366)
            rampElement2.color = [0.0272,0.01364,0.01013,0.87]
            rampElement3 = rampElements.new(0.608)
            rampElement3.color = [0.04445,0.02294,0.01729,0.8]
            rampElement4 = rampElements.new(0.828)
            rampElement4.color = [0.04092,0.0185,0.01161,0.64]
            
            # add texture to material
            MTex = hairMaterial.texture_slots.add()
            MTex.texture = hairTex
            MTex.texture_coords = "STRAND"
            MTex.use_map_alpha = True
            
            
            ###############Create Particles##################
            # Add new particle system
            
            NumberOfMaterials = 0
            for i in ob.data.materials:
                NumberOfMaterials +=1
            
            
            bpy.ops.object.particle_system_add()
            #Particle settings setting it up!
            hairParticles = bpy.context.object.particle_systems.active
            hairParticles.name = "LongBrownCurlHairPar"
            hairParticles.settings.type = "HAIR"
            hairParticles.settings.use_advanced_hair = True
            hairParticles.settings.count = 500
            hairParticles.settings.normal_factor = 0.05
            hairParticles.settings.factor_random = 0.001
            hairParticles.settings.use_dynamic_rotation = True
            
            hairParticles.settings.material = NumberOfMaterials
            
            hairParticles.settings.use_strand_primitive = True
            hairParticles.settings.use_hair_bspline = True
            hairParticles.settings.render_step = 7
            hairParticles.settings.length_random = 0.5
            hairParticles.settings.draw_step = 5
            # children
            hairParticles.settings.child_type = "INTERPOLATED"
            hairParticles.settings.create_long_hair_children = True
            hairParticles.settings.clump_factor = 0.523
            hairParticles.settings.clump_shape = 0.383
            hairParticles.settings.roughness_endpoint = 0.002
            hairParticles.settings.roughness_end_shape = 5
            hairParticles.settings.roughness_2 = 0.003
            hairParticles.settings.roughness_2_size = 2
            
            hairParticles.settings.kink = "CURL"
            hairParticles.settings.kink_amplitude = 0.007597
            hairParticles.settings.kink_frequency = 6
            hairParticles.settings.kink_shape = 0.4
            hairParticles.settings.kink_flat = 0.8
        
        
        ######################################################################
        ########################Short Dark Hair##########################
        elif scene.hair_type == '2':
            ###############Create New Material##################
            # add new material
            hairMaterial = bpy.data.materials.new('ShortDarkHairMat')
            ob.data.materials.append(hairMaterial)
            
            #Material settings
            hairMaterial.preview_render_type = "HAIR"
            hairMaterial.diffuse_color = (0.560, 0.536, 0.506)
            hairMaterial.specular_color = (0.196, 0.177, 0.162)
            hairMaterial.specular_intensity = 0.5
            hairMaterial.specular_hardness = 100
            hairMaterial.ambient = 0
            hairMaterial.use_cubic = True
            hairMaterial.use_transparency = True
            hairMaterial.alpha = 0
            hairMaterial.use_transparent_shadows = True
            #strand
            hairMaterial.strand.use_blender_units = True
            hairMaterial.strand.root_size = 0.0002
            hairMaterial.strand.tip_size = 0.0001
            hairMaterial.strand.size_min = 0.3
            hairMaterial.strand.width_fade = 0.1
            hairMaterial.strand.shape = 0
            hairMaterial.strand.blend_distance = 0.001
            
            # add texture
            hairTex = bpy.data.textures.new("ShortDarkHair", type='BLEND')
            hairTex.use_preview_alpha = True
            hairTex.use_color_ramp = True
            ramp = hairTex.color_ramp
            rampElements = ramp.elements
            rampElements[0].position = 0
            rampElements[0].color = [0.004025,0.002732,0.002428,0.38]
            rampElements[1].position = 1
            rampElements[1].color = [0.141,0.122,0.107,0.2]
            rampElement1 = rampElements.new(0.202)
            rampElement1.color = [0.01885,0.0177,0.01827,0.65]
            rampElement2 = rampElements.new(0.499)
            rampElement2.color = [0.114,0.109,0.09822,0.87]
            rampElement3 = rampElements.new(0.828)
            rampElement3.color = [0.141,0.127,0.117,0.64]
            
            # add texture to material
            MTex = hairMaterial.texture_slots.add()
            MTex.texture = hairTex
            MTex.texture_coords = "STRAND"
            MTex.use_map_alpha = True
            
            
            ###############Create Particles##################
            # Add new particle system
            
            NumberOfMaterials = 0
            for i in ob.data.materials:
                NumberOfMaterials +=1
            
            
            bpy.ops.object.particle_system_add()
            #Particle settings setting it up!
            hairParticles = bpy.context.object.particle_systems.active
            hairParticles.name = "ShortDarkHair"
            hairParticles.settings.type = "HAIR"
            hairParticles.settings.use_advanced_hair = True
            hairParticles.settings.hair_step = 2
            hairParticles.settings.count = 450
            hairParticles.settings.normal_factor = 0.007
            hairParticles.settings.factor_random = 0.001
            hairParticles.settings.use_dynamic_rotation = True
            
            hairParticles.settings.material = NumberOfMaterials
            
            hairParticles.settings.use_strand_primitive = True
            hairParticles.settings.use_hair_bspline = True
            hairParticles.settings.render_step = 3
            hairParticles.settings.length_random = 0.3
            hairParticles.settings.draw_step = 3
            # children
            hairParticles.settings.child_type = "INTERPOLATED"
            hairParticles.settings.rendered_child_count = 200
            hairParticles.settings.virtual_parents = 1
            hairParticles.settings.clump_factor = 0.425
            hairParticles.settings.clump_shape = 0.1
            hairParticles.settings.roughness_endpoint = 0.003
            hairParticles.settings.roughness_end_shape = 5
            
            
        
        return {'FINISHED'}


        
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.hair_type = EnumProperty(
        name="Type",
        description="Select the type of hair",
        items=[("0","Long Red Straight Hair","Generate particle Hair"),
               ("1","Long Brown Curl Hair","Generate particle Hair"),
               ("2","Short Dark Hair","Generate particle Hair"),
        
              ],
        default='0')
        
def unregister():
    bpy.utils.register_module(__name__)
    del bpy.types.Scene.hair_type
    
if __name__ == "__main__":
    register()
    
    

