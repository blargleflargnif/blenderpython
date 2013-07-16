
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
import os
import subprocess

#Operator for adding material layers
class AppleseedAddMatLayer( bpy.types.Operator):
    bl_label = "Add Layer"
    bl_description = "Add new BSDF layer"
    bl_idname = "appleseed.add_matlayer"
    
    def invoke( self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.add()
        num = collection.__len__()
        collection[num-1].name = "BSDF Layer " + str(num)
        
            
        return {'FINISHED'}
    
#Operator for removing material layers
class AppleseedRemoveMatLayer( bpy.types.Operator):
    bl_label = "Remove Layer"
    bl_description = "Remove BSDF layer"
    bl_idname = "appleseed.remove_matlayer"
        
    def invoke( self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.remove( index)
        num = collection.__len__()
        if index >= num:
            index = num -1
        if index < 0:
            index = 0
        material.appleseed.layer_index = index
            
        return {'FINISHED'}

class AppleseedAddRenderLayer( bpy.types.Operator):
    bl_label = "Add Layer"
    bl_idname = "appleseed.add_renderlayer"
    
    def invoke( self, context, event):
        scene = context.scene
        collection = scene.appleseed_layers.layers
        index = scene.appleseed_layers.layer_index

        collection.add()
        num = collection.__len__()
        collection[num-1].name = "Render Layer " + str(num)
            
        return {'FINISHED'}

class AppleseedRemoveRenderLayer( bpy.types.Operator):
    bl_label = "Remove Layer"
    bl_idname = "appleseed.remove_renderlayer"
        
    def invoke( self, context, event):
        scene = context.scene
        collection = scene.appleseed_layers.layers
        index = scene.appleseed_layers.layer_index

        collection.remove( index)
        num = collection.__len__()
        if index >= num:
            index = num -1
        if index < 0:
            index = 0
        scene.appleseed_layers.layer_index = index
        
        return {'FINISHED'}

class AppleseedRenderFrame( bpy.types.Operator):
    """Render active scene"""
    bl_idname = "appleseed.render_frame"
    bl_label = "Appleseed Render Frame"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def execute( self, context):
        scene = context.scene

        if scene.appleseed.display_mode != 'STUDIO':
            scene.render.display_mode = scene.appleseed.display_mode
            bpy.ops.render.render()
        else:
            # export scene here...
            # launch appleseed studio here
            as_bin_path = context.user_preferences.addons['render_appleseed'].preferences.appleseed_bin_path
            cmd = os.path.join( as_bin_path, 'appleseed.studio')
            process = subprocess.Popen( cmd, stdout=subprocess.PIPE)
            #os.system( cmd)

        return {'FINISHED'}

def register():
    bpy.utils.register_class( AppleseedRenderFrame)

def unregister():
    bpy.utils.unregister_class( AppleseedRenderFrame)
