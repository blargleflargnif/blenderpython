# 3D NAVIGATION TOOLBAR v1.2 - 3Dview Addon - Blender 2.5x
#
# THIS SCRIPT IS LICENSED UNDER GPL, 
# please read the license block.
#
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
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Gesture For Split/Join Areas",
    "author": "Martin Lindelof",
    "version": (0, 3),
    "blender": (2, 5, 5),
    "api": 33333,
    "location": "View3D > Operator",
    "description": "Split/Join areas with mouse cursor gesture, good for wacom tablet users",
    "warning": "join doesn't work yet",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UI"}

# import the basic library

import bpy
from bpy.props import *


# class for splitting area #
class GestureSplitOperator(bpy.types.Operator):
    '''Split the screen area with the move of mouse/tablet pen'''
    
    bl_idname = "screen.gesture_split_area"
    bl_label = "Split Area With Gesture"

    first_mouse_x = IntProperty()
    first_mouse_y = IntProperty()
    delta_mouse_x = IntProperty()
    delta_mouse_y = IntProperty()
    direction = StringProperty()
    factor = FloatProperty()
    
    
        
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            delta_mouse_x = self.first_mouse_x - event.mouse_x
            delta_mouse_y = self.first_mouse_y - event.mouse_y
            
            if delta_mouse_x > 50:#left
                self.factor = 1 - (context.region.height-event.mouse_region_y)/context.region.height
                bpy.ops.screen.area_split(direction='HORIZONTAL',factor=self.factor)
                return {'FINISHED'}
            elif delta_mouse_x < -50:#right
                self.factor = 1 - (context.region.height-event.mouse_region_y)/context.region.height
                bpy.ops.screen.area_split(direction='HORIZONTAL',factor=self.factor)        
                return {'FINISHED'}
            if delta_mouse_y > 50:#up
                self.factor = 1 - (context.region.width-event.mouse_region_x)/context.region.width
                bpy.ops.screen.area_split(direction='VERTICAL',factor=self.factor)
                return {'FINISHED'}
            elif delta_mouse_y < -50:#down
                self.factor = 1 - (context.region.width-event.mouse_region_x)/context.region.width
                bpy.ops.screen.area_split(direction='VERTICAL',factor=self.factor)
                return {'FINISHED'}

        elif event.type in ('RIGHTMOUSE', 'ESC'):
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        context.window_manager.add_modal_handler(self)
        self.first_mouse_x = event.mouse_x
        self.first_mouse_y = event.mouse_y
        self.delta_mouse_x = 0
        self.delta_mouse_y = 0
        self.factor = 0.5
        return {'RUNNING_MODAL'}
        
## registring
def register():
    pass

def unregister():
    pass

if __name__ == "__main__":
    register()
