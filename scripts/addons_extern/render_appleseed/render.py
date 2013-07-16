
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

import os
import subprocess
import time

import bpy
from extensions_framework import util as efutil

from . import util

def update_start( engine, data, scene):
    if engine.is_preview:
        update_preview( engine, data, scene)
    else:
        update_scene( engine, data, scene)
        
def render_start( engine, scene):
    if engine.is_preview:
        render_preview( engine, scene)
    else:
        render_scene( engine, scene)
        
def render_init( engine):
    pass

def update_preview( engine, data, scene):
    pass

def render_preview( engine, scene):
    pass


def update_scene( engine, data, scene):
    if os.path.isdir( scene.appleseed.project_path):
        proj_name = None
    else:
        proj_name = scene.appleseed.project_path.split( os.path.sep)[-1]

def render_scene( engine, scene):
    #Export the scene
    bpy.ops.appleseed.export()
    
    DELAY = 0.1
    project_file = util.realpath( scene.appleseed.project_path)
    render_dir = 'render' + os.path.sep if scene.appleseed.project_path[-1] == os.path.sep else os.path.sep + 'render' + os.path.sep 
    render_output = os.path.join( util.realpath(scene.appleseed.project_path), render_dir)
    width = scene.render.resolution_x
    height = scene.render.resolution_y
    
    #Make the output directory, if it doesn't exist yet
    if not os.path.exists( project_file):
        try:
            os.mkdir( project_file)
        except:
            self.report( {"INFO"}, "The project directory cannot be created. Check directory permissions.")
            return
    
    #Make the render directory, if it doesn't exist yet
    if not os.path.exists( render_output):
        try:
            os.mkdir( render_output)
        except:
            self.report( {"INFO"}, "The project render directory cannot be created. Check directory permissions.")
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
        
    filename = os.path.join( util.realpath( scene.appleseed.project_path), filename)
    
    appleseed_exe = "appleseed.cli" #if scene.appleseed.renderer_type == 'CLI' else "appleseed.studio"
    
    
    #Start the Appleseed executable 
    #if scene.appleseed.renderer_type == "CLI":        
        #Get the absolute path to the executable dir
    as_bin_path = bpy.context.user_preferences.addons['render_appleseed'].preferences.appleseed_bin_path
    #cmd = ( os.path.join( util.realpath( as_bin_path), appleseed_exe), filename, '-o', ( render_output + scene.name + '_' + str( scene.frame_current) + scene.render.file_extension), '--threads', str( scene.appleseed.threads), '--continuous-saving')
    cmd = ( os.path.join( util.realpath( as_bin_path), appleseed_exe), filename, '-o', ( render_output + scene.name + '_' + str( scene.frame_current) + scene.render.file_extension), '--threads', str( scene.appleseed.threads))

    #elif scene.appleseed.renderer_type == "GUI":
    #    if not scene.appleseed.new_build_options:
    #        cmd = ( util.realpath( scene.appleseed.appleseed_path) + os.path.sep + appleseed_exe)
    #    else: 
            #if scene.appleseed.rendering_mode == "interactive":
            #    cmd = os.path.join( util.realpath(scene.appleseed.appleseed_path), appleseed_exe) + ' ' + filename + " --render interactive"
            #else:
            #    cmd = os.path.join( util.realpath(scene.appleseed.appleseed_path), appleseed_exe) + ' ' + filename + " --render final"
            
    print( "Rendering:", cmd)
    process = subprocess.Popen( cmd, cwd = render_output, stdout=subprocess.PIPE)
    
    #The rendered image name and path
    render_image = render_output + scene.name + '_' + str( scene.frame_current) + scene.render.file_extension
    # Wait for the file to be created
    while not os.path.exists( render_image):
        if engine.test_break():
            try:
                process.kill()
            except:
                pass
            break

        if process.poll() != None:
            engine.update_stats( "", "Appleseed: Error")
            break

        time.sleep( DELAY)

    if os.path.exists(render_image):
        engine.update_stats( "", "Appleseed: Rendering")

        prev_size = -1

        def update_image():
            result = engine.begin_result( 0, 0, width, height)
            lay = result.layers[0]
            # it's possible the image wont load early on.
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

            time.sleep( DELAY)

class RenderAppleseed( bpy.types.RenderEngine):
    bl_idname = 'APPLESEED_RENDER'
    bl_label = 'Appleseed'
    bl_use_preview = False
    
    def __init__( self):
        render_init( self)

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
