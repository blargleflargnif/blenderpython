bl_info = {
    "name": "Render Tools",
    "description": "Useful and time-saving tools for rendering workflow",
    "author": "Aditia A. Pratama",
    "version": (0, 5),
    "blender": (2, 68),
    "location": "3D View > Property Panel (T-key)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/aditiapratama/myb3d_addons",
    "category": "3D View"}

import bpy

class SubsurfToggle(bpy.types.Operator):
    'Toggle subsurf visibility'
    bl_idname='subsurf.toggle'
    bl_label='Subsurf Toggle'
       
    def execute(self,context):
        state = bpy.context.active_object.modifiers['Subsurf'].show_viewport
        for e in bpy.context.selected_objects:
            try:
                if state==False:
                    e.modifiers['Subsurf'].show_viewport = True
                else:
                    e.modifiers['Subsurf'].show_viewport = False
            except KeyError:
                print ("No subsurf on "+e.name+" or it is not named Subsurf")
        return {'FINISHED'}

class SimplifyMenu(bpy.types.Operator):
    bl_idname = "scene.simplify"
    bl_label = "Simplify!"

    def execute(self, context):
        render = bpy.context.scene.render
        render.simplify_subdivision = 0
        
        if render.use_simplify:
            render.use_simplify = False
        else:
            render.use_simplify = True
        return {'FINISHED'}

            
class Visibility(bpy.types.Panel):
    bl_label = "Render Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
       
    def draw (self, context):
        layout=self.layout
                                                   
        col=layout.column()
        col.label(text="Display Subsurf Modifier ")
        col.operator("subsurf.toggle", text="On/Off", icon="MOD_SUBSURF")
        
        col.separator()
        
        view = context.scene.render
        scene = context.scene
          
        col.prop(view, "use_simplify", text="Simplify")
        col.prop(scene, "use_unsimplify_render", text="Unsimplify Render")
        sub = col.column()
        sub.active = view.use_simplify
        sub.prop(view, "simplify_subdivision", text="Subdivision")
        
        col.separator()
        
        ob = context.object
        
        layout.prop(ob, "dupli_group", text="Group")

# FEATURE: Simplify in k menu
class MenuSimplify(bpy.types.Menu):
    bl_idname = "menu.use_simplify"
    bl_label = "Simplify Menu"

    def draw(self, context):
        layout = self.layout

        col=layout.column()

        view = context.scene.render

        col.operator("scene.simplify", text="Simplify!", icon="META_CUBE")
        col.operator("subsurf.toggle", text="Subsurf ON/OFF", icon="MOD_SUBSURF")

addon_keymaps = []

def register():
   bpy.utils.register_module(__name__)

   wm = bpy.context.window_manager
    
   km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
   kmi = km.keymap_items.new('wm.call_menu', 'K', 'PRESS')
   kmi.properties.name = 'menu.use_simplify' 

   addon_keymaps.append(km)
   
def unregister():
    bpy.utils.unregister_module(__name__)

    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del addon_keymaps[:]
 
if __name__ == "__main__":
    register()
