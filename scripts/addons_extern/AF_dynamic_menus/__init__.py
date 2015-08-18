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
    "category": "Addon Factory",
}

if "bpy" in locals():
    import importlib
    importlib.reload(spacebar_menu)
    importlib.reload(manipulator_Menu)
    importlib.reload(multiselect_menu)
    importlib.reload(edit_context_mode)
    importlib.reload(toolshelf_menu)
    importlib.reload(navigation)
    importlib.reload(materials_utils)
    importlib.reload(snap_menu)



else:
    from . import spacebar_menu
    from . import manipulator_Menu
    from . import multiselect_menu
    from . import edit_context_mode
    from . import toolshelf_menu
    from . import navigation
    from . import materials_utils
    from . import snap_menu

import bpy
from math import *
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty, PointerProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup

#//////////////////////////////// - Black Hole by Crocodillian- ///////////////////////////   
def Update_ObjectOrigin(self, context):
    
    # Create an array to store all found objects
    objects_to_select = []
    
    sel = context.active_object
    
    print("---Inside Update_ObjectOrigin---")
    
    if sel.BHObj.update_toggle is False:
    
        # Store the active object
        active = context.active_object
            
        # Find all the selected objects in the scene and store them
        for object in context.selected_objects:
            if object.name != active.name:
                print("! - Found Selected Object")
                objects_to_select.append(object) 
                
        # First, we need to process the active object, as it already has the correct enum.
        print("# - Active Object Name")
        print(active)
        FocusObject(active) 
        
        # Get the origin point and call the respective def
        newInt = int(active.BHObj.origin_point)
        enum = active.BHObj.origin_point
        
        SetObjectOrigin(active, newInt, context)
            
        # Now were going to focus each selected object using the update loop, to prevent a recursion
        # loop
        for object in objects_to_select:
            object.BHObj.update_toggle = True
            FocusObject(object)
            object.BHObj.origin_point = enum
        
        active.BHObj.update_toggle = False
        FocusObject(active)
            
        # Now were at the end, re-select the objects in the correct order.  
        for object in objects_to_select:
            SelectObject(object)
            object.BHObj.update_toggle = False
            
        return None
        
    else:
        # Focus on the object
        print("# - Selected Object Name")
        FocusObject(sel) 
        print(sel.name)
        
        # Get the origin point and call the respective def
        newEnum = int(context.active_object.BHObj.origin_point)
        SetObjectOrigin(sel, newEnum, context)
        
        return None
        
    
        
    return None 
    
def Update_ObjectVGOrigin(self, context):
    
    # Create an array to store all found objects
    objects_to_select = []
    objects_to_make_active = []
    
    print("Rawr?")
    
    # Store the active object
    objects_to_make_active.append(bpy.context.active_object)
            
    # Find all the selected objects in the scene and store them
    for object in context.selected_objects:
        objects_to_select.append(object)
        
    # Focus on the object with the newly selected vertex group
    FocusObject(bpy.context.active_object.object) 
        
    # Get the origin point and call the respective def
    newEnum = int(self.origin_point)
    VGSelect = int(bpy.context.active_object.GTMnu.vertex_groups)
    
    # If the index isnt one (which is the None selection), change the origin!)
    if VGSelect != 1:    
        SetObjectOrigin(object, newEnum, context)
        
    bpy.ops.object.select_all(action='DESELECT') 
        
    # Re-select all stored objects         
    for objectSelect in objects_to_select:
        bpy.ops.object.select_pattern(pattern=objectSelect.name)
             
    for objectActive in objects_to_make_active:
        bpy.ops.object.select_pattern(pattern=objectActive.name)
        bpy.context.scene.objects.active = objectActive
        
    return None 

#//////////////////////////////// - PROPERTY DEFINITIONS - ///////////////////////////  
    
# All properties relating to a specific object
class BH_Object(PropertyGroup):
    
    origin_point = EnumProperty(
        name="Set Object Origin",
        items=(
        ('1', 'Origin to Object Base', 'Sets the origin to the lowest point of the object, using the object Z axis.'),   
        ('2', 'Origin to Lowest Point', 'Sets the origin to the lowest point of the object, using the scene Z axis'),  
        ('3', 'Origin to Centre of Mass', 'Sets the origin using the objects centre of mass.'),
        ('4', 'Origin to Vertex Group', 'Sets the origin using a given vertex group'),
        ('5', 'Origin to 3D Cursor', 'Sets the origin using a given vertex group'),
        ),
        update = Update_ObjectOrigin)
        
    update_toggle = BoolProperty(
        name = "Update Toggle",
        description = "Prevents recursion loops in specific, multi-select operations",
        default = False)
    
# Used to get the vertex groups of a selected object
def GetVertexGroups(scene, context):
    
    items = [
        ("1", "None",  "", 0),
    ]

    ob = bpy.context.active_object
    u = 1

    for i,x in enumerate(ob.vertex_groups):
        
        items.append((str(i+1), x.name, x.name))

    return items
    
# Used to generate the menu enumerator for vertex groups
class BH_Menu(PropertyGroup):
    
    vertex_groups = EnumProperty(
        name="Select Vertex Group",
        items=GetVertexGroups,
        update=Update_ObjectVGOrigin)

    
#//////////////////////////////// - USER INTERFACE - ///////////////////////////  

class VIEW3D_PT_tools_object_Interface(bpy.types.Menu):
    bl_label = "Object Origin"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            return True
                
        return False
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.origin_set",
                        text="Geometry to Origin").type = 'GEOMETRY_ORIGIN'
        layout.operator("object.origin_set",
                        text="Origin to Geometry").type = 'ORIGIN_GEOMETRY'
        layout.operator("object.origin_set",
                        text="Origin to 3D Cursor").type = 'ORIGIN_CURSOR'        
        obj = context.object.BHObj
        mnu = context.object.BHMnu
        
        # Core user interface for the plugin
        
        col_object = layout.column(align=True)
        col_object.alignment = 'EXPAND'
        row_object = col_object.row(align=True)
        row_object.prop(obj, "origin_point", text="", icon = "CURSOR")
        row_object.operator("object.bh_update_origin", icon = "ROTATE")
        
        if int(obj.origin_point) is 4:
            row_object = layout.row(align=True)
            row_object.prop(mnu, "vertex_groups",text = "",  icon = "GROUP_VERTEX")
            
#//////////////////////////////// - DEFINITIONS - ///////////////////////////  
def FocusObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')  
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name) 
    
def SelectObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    target.select = True
    
def ActivateObject(target):
    
    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False
        
    if target.hide_select is True:
        target.hide_select = False
    
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
        
        
#//////////////////////////////// - CLASSES - ///////////////////////////  
class BH_Update_Origin(bpy.types.Operator):
    """Updates the origin point based on each object's origin setting, for all selected objects"""
    
    bl_idname = "object.bh_update_origin"
    bl_label = ""
    
    def execute(self, context):
        print(self)
        
        atv = context.active_object
        sel = context.selected_objects
        
        for obj in sel:
            
            FocusObject(obj)
            Update_ObjectOrigin(obj, context)
            
        FocusObject(atv)
        Update_ObjectOrigin(atv, context)
        
        for obj in sel:
            SelectObject(obj)
            
        ActivateObject(atv)
        
        return {'FINISHED'}
        
def SetObjectOrigin(object, enum, context):
    
    print("Inside ASKETCH_SetObjectOrigin")
        
    # Set to Object Base
    if enum == 1:
        print("Setting to Object Base")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        i = -1
        lowestZ = 0
        
        # First find the lowest Z value in the object
        for vertex in object_data.vertices:
            i += 1
            #print (i)
            
            # Used to define a reference point for the first vertex, in case 0 is
            # lower than any vertex on the model.
            if i == 0:
                lowestZ = vertex.co.z
            
            else:
                if vertex.co.z < lowestZ:
                    lowestZ = vertex.co.z
        
        # Now select all vertices with lowestZ
        
        for vertex in object_data.vertices:
            if vertex.co.z == lowestZ:
                vertex.select = True
                #print("Vertex Selected!")

        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
    # Set to Absolute Lowest
    elif enum == 2:
        print("Setting to Absolute Lowest")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        i = -1
        lowestZ = 0
        
        # First find the lowest Z value in the object
        for vertex in object_data.vertices:
            i += 1
            #print (i)
            
            # This code converts vertex coordinates from object space to world space.
            vertexWorld = object.matrix_world * vertex.co
            
            # Used to define a reference point for the first vertex, in case 0 is
            # lower than any vertex on the model.
            if i == 0:
                lowestZ = vertexWorld.z
            
            else:
                if vertexWorld.z < lowestZ:
                    lowestZ = vertexWorld.z
        
        # Now select all vertices with lowestZ
        
        for vertex in object_data.vertices:
            vertexWorld = object.matrix_world * vertex.co
            
            if vertexWorld.z == lowestZ:
                vertex.select = True
                #print("Vertex Selected!")

        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
                
    # Set to COM
    elif enum == 3:
        print("Setting to COM")
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        
    elif enum == 4:
        print("Setting to Vertex Group")
        
        # Enter the object!
        object_data = bpy.context.object.data
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        #Setup the correct tools to select vertices
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        sel_mode = context.tool_settings.mesh_select_mode
        context.tool_settings.mesh_select_mode = [True, False, False]
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        index = int(bpy.context.active_object.GTMnu.vertex_groups) - 1
        
        #Search through all vertices in the object to find the ones belonging to the
        #Selected vertex group
        for vertex in object_data.vertices:
            for group in vertex.groups:
                if group.group == index:
                    vertex.select = True
                    #print("Vertex Selected!")
                    
        #Restore previous settings
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        context.tool_settings.mesh_select_mode = sel_mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                  
        
        # Saves the current cursor location
        cursor_loc = bpy.data.scenes[bpy.context.scene.name].cursor_location
        previous_cursor_loc = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]
        
        # Snap the cursor
        bpy.ops.object.editmode_toggle()
        bpy.ops.view3D.snap_cursor_to_selected()
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.editmode_toggle()
        
        # Set the origin
        FocusObject(object)
        bpy.ops.object.origin_set(type ='ORIGIN_CURSOR')
        
        # Restore the original cursor location
        bpy.data.scenes[bpy.context.scene.name].cursor_location = previous_cursor_loc
        
    # Set to COM
    elif enum == 5:
        print("Setting to 3D Cursor")
        
        # Set the origin
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

def panel_func(self, context):
    self.layout.label(text="Object Origin:")
    self.layout.menu("VIEW3D_PT_tools_object_Interface", text="Origin Tools")

#//////////////////////// - REGISTER/UNREGISTER DEFINITIONS - ////////////////////////
property_classes = (BH_Object, BH_Menu)

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
		layout.label(text="Snap Menu: Hotkey, shift/s")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_snap.append(snap_menu.menu)

    # Register the properties first
        
    bpy.types.Object.BHObj = PointerProperty(type=BH_Object)
    bpy.types.Object.BHMnu = PointerProperty(type=BH_Menu)
    bpy.types.VIEW3D_PT_tools_object.append(panel_func)
    bpy.types.VIEW3D_MT_snap.append(panel_func)	

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

    #materials utils keybinding
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('wm.call_menu', 'Q', 'PRESS', shift=True)
        kmi.properties.name = "VIEW3D_MT_master_material"

def unregister():
    bpy.types.VIEW3D_MT_snap.remove(snap_menu.menu)

    del bpy.types.Object.BHObj
    del bpy.types.Object.BHMnu
    bpy.types.VIEW3D_PT_tools_object.remove(panel_func)    
    bpy.types.VIEW3D_MT_snap.remove(panel_func)

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

    #remove materials utils keybinding
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps["3D View"]
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                if kmi.properties.name == "VIEW3D_MT_master_material":
                    km.keymap_items.remove(kmi)
                    break

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
