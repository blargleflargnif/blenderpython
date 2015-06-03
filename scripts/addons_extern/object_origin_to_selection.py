bl_info = {
    "name": "Set Origin to Selected",
    "description": "Set origin directly with edit mode selection",
    "author": "Ghislain Jeanneau",
    "version": (1,0),
    "blender": (2, 6, 0),
    "api": 39307,
    "location": "Edit Mode -> Alt + C",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": ""
                "",
    "tracker_url": ""
                   "",
    "category": "Object"
    }
    
import bpy

def main(context):
    cursorPositionX = bpy.context.scene.cursor_location[0]
    cursorPositionY = bpy.context.scene.cursor_location[1]
    cursorPositionZ = bpy.context.scene.cursor_location[2]
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.object.mode_set()
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.scene.cursor_location[0] = cursorPositionX
    bpy.context.scene.cursor_location[1] = cursorPositionY
    bpy.context.scene.cursor_location[2] = cursorPositionZ
    
class SetOriginToSelected(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "object.setorigintoselected"
    bl_label = "Set Origin to Selected"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(context)
        
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(SetOriginToSelected)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.active
    km = kc.keymaps.find("Mesh")
    for lmi in kc.keymaps:
        print(lmi.name)
    kmi = km.keymap_items.new('object.setorigintoselected','C','PRESS',False,False,False,True,False)

    
def unregister():
    bpy.utils.unregister_class(SetOriginToSelected)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.active
    km = kc.keymaps.find("Mesh",'VIEW_3D')
    kmi = km.keymap_items.find('object.setorigintoselected').remove()
    
if __name__ == "__main__":
    register()