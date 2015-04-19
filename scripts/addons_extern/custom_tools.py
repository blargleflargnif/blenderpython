bl_info = {
    "name": "Custom Tools",
    "description": "Adds a tab to the toolbar with some custom tools",
    "author": "TARDIS Maker",
    "version": (0, 0, 0),
    "blender": (2, 72, 2),
    "location": "Tool Shelf > Custom Tools",
    "warning": "",
    "category": "Custom"}

import bpy
from bpy.types import Menu, Panel, UIList

def main(context):
    #SCENE CONVINIENCE VARIABLES
    scene = bpy.context.scene
    object = bpy.ops.object
    
    #ACTIVE CAMERA
    camera = bpy.context.scene.camera
    
    object.select_all(action="DESELECT")
    scene.objects.active = camera
    camera.select = True    
    

class SelectCamera(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "select.camera"
    bl_label = "Select Active Camera"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        return {'FINISHED'}
    
    
    

########### TOOLSHELF TAB ##############
class VIEW3D_Test_Tab(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Custom Tools"
    bl_context = "objectmode"
    bl_label = "Select Camera"
    
    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        col.operator("select.camera")
        #col.operator("select.cameras")



def register():
    bpy.utils.register_class(SelectCamera)
    bpy.utils.register_class(VIEW3D_Test_Tab)


def unregister():
    bpy.utils.unregister_class(SelectCamera)
    bpy.utils.unregister_class(VIEW3D_Test_Tab)


if __name__ == "__main__":
    register()

    #bpy.ops.select.camera()
