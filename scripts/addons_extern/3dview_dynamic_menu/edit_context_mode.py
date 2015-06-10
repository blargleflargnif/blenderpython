# Save as mesh_context_menu.py and put it into addons directory
# (or use Blender's Install From File... function).

bl_info = {
    "name": "Mesh Context Menu",
    "author": "Stanislav Blinov",
    "version": (1, 0, 0),
    "blender": (2, 74, 0),
    "description": "Context-sensitive mesh menu",
    "category": "Mesh",
}

import bpy
from bpy_extras import view3d_utils

class MESH_MT_CombinedMenu(bpy.types.Menu):
    bl_idname = "mesh.addon_combined_component_menu"
    bl_label = "Components"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        
        mode = context.tool_settings.mesh_select_mode
        if mode[0]: layout.menu("VIEW3D_MT_edit_mesh_vertices")
        if mode[1]: layout.menu("VIEW3D_MT_edit_mesh_edges")
        if mode[2]: layout.menu("VIEW3D_MT_edit_mesh_faces")

class MESH_OT_CallContextMenu(bpy.types.Operator):
    bl_idname = "mesh.addon_call_context_menu"
    bl_label = "Context Menu"
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        mode = context.tool_settings.mesh_select_mode
        num = sum(int(m) for m in mode)
        if num == 1:
            if mode[0]: return bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_vertices")
            if mode[1]: return bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_edges")
            if mode[2]: return bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_faces")
        else:
            return bpy.ops.wm.call_menu(name=MESH_MT_CombinedMenu.bl_idname)
        

