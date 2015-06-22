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
    "name": "Dynamic Menus",
    "author": "Multiple Authors",
    "version": (0, 3, 0),
    "blender": (2, 74, 5),
    "location": "See Preferences",
    "description": "Add Extended Menu's",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

if "bpy" in locals():
    import importlib
    importlib.reload(spacebar_menu)
    importlib.reload(manipulator_Menu)
    importlib.reload(multiselect_menu)
    importlib.reload(edit_context_mode)
    importlib.reload(toolshelf_menu)
    importlib.reload(navigation)


else:
    from . import spacebar_menu
    from . import manipulator_Menu
    from . import multiselect_menu
    from . import edit_context_mode
    from . import toolshelf_menu
    from . import navigation

import bpy

# Register all operators and panels
class AddonPreferences1(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	def draw(self, context):
		layout = self.layout
		layout.label(text="Key Maps:")
		layout.label(text="Dynamic Spacebar Menu: Hotkey: spacebar")
		layout.label(text="Multi Select Menu: Hotkey ctrl/tab")
		layout.label(text="Manipulator Menu: Hotkey ctrl/spacebar")
		layout.label(text="Select Vert Edge Face Menu: Hotkey, Right Mouse/Double Click")


def register():
    bpy.utils.register_module(__name__)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu', 'SPACE', 'PRESS')
        kmi.properties.name = "VIEW3D_MT_Space_Dynamic_Menu"
    #add multiselect keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    kmi = km.keymap_items.new('wm.call_menu', 'TAB', 'PRESS', ctrl=True)
    kmi.properties.name = "VIEW3D_MT_Multiselect_Menu"

    #remove default keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "VIEW3D_MT_edit_mesh_select_mode":
                km.keymap_items.remove(kmi)
                break
    #add manipulator keybinding
    km = wm.keyconfigs.addon.keymaps.new(name='3D View Generic', space_type='VIEW_3D')
    kmi = km.keymap_items.new('wm.call_menu', 'SPACE', 'PRESS', ctrl=True)
    kmi.properties.name = "VIEW3D_MT_ManipulatorMenu"

    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('mesh.addon_call_context_menu', 'RIGHTMOUSE', 'DOUBLE_CLICK')

def unregister():


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['3D View']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                if kmi.properties.name == "VIEW3D_MT_Space_Dynamic_Menu":
                    km.keymap_items.remove(kmi)
                    break

    #remove multiselect keybinding
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "VIEW3D_MT_Multiselect_Menu":
                km.keymap_items.remove(kmi)
                break

    #replace default keymap
    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    kmi = km.keymap_items.new('wm.call_menu', 'TAB', 'PRESS', ctrl=True)
    kmi.properties.name = "mesh.addon_call_context_menu"

    #remove manipulator
    km = wm.keyconfigs.addon.keymaps['3D View Generic']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "VIEW3D_MT_ManipulatorMenu":
                km.keymap_items.remove(kmi)
                break

    #remove manipulator
    km = wm.keyconfigs.addon.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'wm.call_menu':
            if kmi.properties.name == "mesh.addon_call_context_menu":
                km.keymap_items.remove(kmi)
                break

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
