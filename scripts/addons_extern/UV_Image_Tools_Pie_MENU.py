bl_info = {
    "name": "UV-Image Tool Pie Menu",
    "author": "MKB",
    "version": (0,1),
    "blender": (2, 7, 1),
    "location": "Image Editor",
    "description": "Pie Menu for UV-Image Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UV"}



import bpy
from bpy import *
from rna_prop_ui import PropertyPanel
from bpy.types import Menu, Operator
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       )


class image_editor_uvspaceFA(Menu):
    bl_label = "META UV"
    bl_idname = "uv.editspaceFA" 

   
    @classmethod
    def poll(cls, context):
        sima = context.space_data
        return sima.show_uvedit and not context.tool_settings.use_uv_sculpt

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager
        scn = context.scene

        toolsettings = context.tool_settings
        settings = context.tool_settings
	
        #row.operator_context = 'INVOKE_REGION_WIN'
        
        pie = layout.menu_pie()

###########-#-- PIE-BLOCK ---- 1_Left ---------------------------------------------------- 
        box = pie.split().box().column()
        #box.scale_x = 0.65
        
        row = box.row(align=True)
        #row.scale_x = 0.9

        row.operator("uv.weld", text="Weld", icon="AUTOMERGE_ON")      
        row.operator("uv.stitch", text="Stitch")  
                    
        row = box.row(align=True)
        row.operator("uv.pin", text="Pin", icon ="PINNED").clear=False
        row.operator("uv.pin", text="UnPin", icon ="UNPINNED").clear=True

        row = box.row(align=True)
        row.operator("uv.uv_squares_by_shape", text="Shape Grid")
        row.operator("uv.uv_squares", text="Square Grid")
        
        row = box.column(align=True)        
        row.operator("uv.uv_snap_to_axis", text="Snap to X/Y-Axis")
        row.operator("uv.uv_snap_to_axis_and_equal", text="Snap with Equal Distance")
        row.operator("uv.uv_face_join", text="Snap to Closest Unselected")         



###########-#-- PIE-BLOCK ---- 2_Right ---------------------------------------------------
        box = pie.split().box().column()
        box.scale_x = 0.65        
        
        row = box.row(align=True)
        row.operator("view3d.pivot_bounding_box", " ", icon="ROTATE")
        row.operator("view3d.pivot_3d_cursor", " ", icon="CURSOR")
        row.operator("view3d.pivot_median", " ", icon="ROTATECENTER")
                    
                
        row = box.row()
        row.prop(toolsettings, "use_uv_select_sync", text=" ")            
        
        row.template_edit_mode_selection()
        
        row = box.row()
        row.operator("uv.select_border", text=" ", icon="BORDER_RECT").pinned=False
        row.prop(toolsettings, "uv_select_mode", text="")
        
        #row = box.row(align=True)
        #row.prop(uvedit, "sticky_select_mode", icon_only=True) 
                
              
      
        row = box.row()
        
        snap_meta = toolsettings.use_snap            
        if snap_meta == False:
            row.operator("wm.context_toggle", text=" ", icon="SNAP_OFF").data_path = "tool_settings.use_snap"
        else: 
            row.operator("wm.context_toggle", text=" ", icon="SNAP_ON").data_path = "tool_settings.use_snap"              

        row.operator("snape.vertex", " ", icon = "SNAP_VERTEX") 
        row.operator("snape.increment", " ", icon = "SNAP_INCREMENT")         
        
        row = box.row()             
        toolsettings = context.tool_settings            
        row.prop(toolsettings, "proportional_edit", icon_only=True)
        row.prop(toolsettings, "proportional_edit_falloff", icon_only=True) 
        
        mesh = context.edit_object.data
        row.prop_search(mesh.uv_textures, "active", mesh, "uv_textures", text="")          
        




###########-#-- PIE-BLOCK ---- 3_Bottom -------------------------------------------------- 
        box = pie.split().box().column()
        box.scale_x = 1.1
        
        row = box.row(align=True)
        #row.scale_x = 0.9

        row.operator("uv.unwrap", icon = "UV_FACESEL")
        row.operator("uv.pack_islands", icon="GRID")
        
        row = box.row(align=True)       
        row.operator("uv.mark_seam", icon = "UV_EDGESEL")
        row.operator("uv.seams_from_islands")        
                
        row = box.row(align=True)
        row.operator("uv.minimize_stretch", text="Minimize Stretch", icon="MOD_TRIANGULATE") 
        row.operator("mesh.faces_mirror_uv")
    
        row = box.row(align=True)
        row.operator("uv.average_islands_scale", text="Average Scale", icon ="CURVE_PATH")
        row.operator("uv.average_islands_scale")

        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.operator("uv.tube_uv_unwrap")



###########-#-- PIE-BLOCK ---- 4_Top ----------------------------------------------------- 
        box = pie.split().box().column()
        box.scale_x = 0.7
        
        row = box.row(align=True)
        row.alignment = 'CENTER'
        row.scale_x = 1.55

        row.operator("uv.export_layout", text="Export UV")
        row.operator("ed.redo", text="", icon="LOOP_FORWARDS")                 
        
        row.menu("IMAGE_MT_uvs_showhide","", icon="VISIBLE_IPO_ON")        
        
        row.operator("ed.undo", text="", icon="LOOP_BACK")
        row.operator("ed.undo_history", text="History      ")        
        
        
        row = box.row(align=True)                
        row.operator("uv.select_linked", text="Linked", icon ="RESTRICT_SELECT_OFF")
        row.operator("uv.select_split", text="Split", icon ="RESTRICT_SELECT_OFF")
        row.operator("uv.select_pinned", text="Pinned", icon ="RESTRICT_SELECT_OFF")    


###########-#-- PIE-BLOCK ---- 5_Top_Left ------------------------------------------------ 
        box = pie.split().box().column()
        box.scale_x = 1
        
        row = box.row(align=True)
        #row.scale_x = 0.9
      
        row.operator("transform.mirror", text="Mirror X", icon="ARROW_LEFTRIGHT").constraint_axis=(True, False, False)
        row.operator("transform.mirror", text="Mirror Y", icon="ARROW_LEFTRIGHT").constraint_axis=(False, True, False)
         
        row = box.row(align=True)          
        row.operator("uv.rotatednineminus", text="Rot -90°", icon="FILE_REFRESH")           
        row.operator("uv.rotatednine", text="Rot 90°", icon="FILE_REFRESH") 

        row = box.row(align=True)
        row.operator("uv.reset", text="UV Reset", icon = "RECOVER_AUTO") 
        row.operator("uv.rotateoneeighty", text="Rot 180", icon="FILE_REFRESH")



###########-#-- PIE-BLOCK ---- 6_Top_Right -----------------------------------------------
        box = pie.split().box().column()
        box.scale_x = 1.05
        
        row = box.row(align=True)
        #row.scale_x = 0.9
        #row.menu("View_Custom_Menu", text = "Editor View", icon = "PLUG" )        
        row.operator("screen.screen_full_area", text = "FSc ", icon = "FULLSCREEN_ENTER") 
        row.operator("screen.screen_full_area", text = "FW  ", icon = "FULLSCREEN_ENTER").use_hide_panels = True        
        
        row = box.row(align=True)        
        row.prop(toolsettings, "use_uv_sculpt")
        row = box.row(align=True)
        row.operator("uv.remove_doubles", text="Remove Doubles", icon="PANEL_CLOSE") 




###########-#-- PIE-BLOCK ---- 7_Bottom_Left ---------------------------------------------
        box = pie.split().box().column()
        box.scale_x = 1.1
        
        row = box.row(align=True)
        #row.scale_x = 0.9


        row.operator("uv.align_left_margin" , "Align Left", icon="EDIT_VEC")
        row.operator("uv.align_right_margin", "Align Right", icon="EDIT_VEC")        

        row = box.row(align=True) 
        row.operator("uv.align_vertical_axis", "Align VAxis", icon="EDIT_VEC")
        row.operator("uv.align_horizontal_axis", "Align HAxis", icon="EDIT_VEC")

        row = box.row(align=True) 
        row.operator("uv.align_top_margin" , "Align Top", icon="EDIT_VEC")
        row.operator("uv.align_low_margin", "Align Low", icon="EDIT_VEC")  
        
        
        
        

###########-#-- PIE-BLOCK ---- 8_Bottom_Right --------------------------------------------
        box = pie.split().box().column()
        box.scale_x = 1.1
        
        row = box.row(align=True)
        #row.scale_x = 0.9

        row.operator("uv.align",text="Flatten X", icon="GRIP").axis='ALIGN_X'
        row.operator("uv.align",text="Flatten Y", icon="GRIP").axis='ALIGN_Y'
        
        row = box.row(align=True) 
        row.operator("uv.align",text="AutoAlign", icon="GRIP").axis='ALIGN_AUTO'                      
        row.operator("uv.align",text="Straighten", icon="COLLAPSEMENU").axis='ALIGN_S' 
        
        row = box.row(align=True)         
        row.operator("uv.align",text="Straighten X", icon="COLLAPSEMENU").axis='ALIGN_T'
        row.operator("uv.align",text="StraightenY", icon="COLLAPSEMENU").axis='ALIGN_U'        



 







      
class image_editor_uvsculpt(Menu):
    bl_label = "META UV"
    bl_idname = "uv.sculpt" 


    
    def draw(self, context):
        layout = self.layout        
        
        toolsettings = context.tool_settings
        uvsculpt = toolsettings.uv_sculpt
        brush = uvsculpt.brush


        settings = context.tool_settings
	
        #row.operator_context = 'INVOKE_REGION_WIN'
        
        pie = layout.menu_pie()



###########-#-- PIE-BLOCK ---- 1_Left ---------------------------------------------------- 
        box = pie.split().box().column()
        box.scale_x = 1
                
        row = box.row(align=True)
        row.prop(uvsculpt, "show_brush")

        row = box.row(align=True)
        row.prop(toolsettings, "uv_sculpt_lock_borders")

        row = box.row(align=True)
        row.prop(toolsettings, "uv_sculpt_all_islands")





###########-#-- PIE-BLOCK ---- 2_Right ---------------------------------------------------        
        box = pie.split().box().column()
        box.scale_x = 1
        
        row = box.row(align=True)
        #row.scale_x = 1.55          

        row.prop(toolsettings, "use_uv_sculpt")
        
        row = box.row(align=True)
        
        
        row.prop(toolsettings, "uv_sculpt_tool","")
        
        if toolsettings.uv_sculpt_tool == 'RELAX':
            row = box.row(align=True)
            row.prop(toolsettings, "uv_relax_method","")
        
 





###########-#-- PIE-BLOCK ---- 3_Bottom -------------------------------------------------- 
        box = pie.split().box().column()
        box.scale_x = 0.65
        
        row = box.row(align=True)
        #row.scale_x = 1.55   

        
        row = box.row(align=True)
        row.scale_x = 1.55        
        upr = context.tool_settings.unified_paint_settings 
        row.prop(upr, "size", text="Radius", slider=False)         
        row.prop(upr, "use_pressure_size", text="") 


        row = box.row(align=True)
        row.scale_x = 1.55
        ups = context.tool_settings.uv_sculpt.brush             
        row.prop(ups, "strength", text="Strength", slider=False) 
        row.prop(upr, "use_pressure_strength", text="") 




###########-#-- PIE-BLOCK ---- 4_Top ----------------------------------------------------- 
        box = pie.split().box().column()

        row = box.row(1)
        row.alignment ='CENTER'
        row.scale_x = 1.55              
        
        row.operator("screen.screen_full_area", text = "", icon = "FULLSCREEN_ENTER").use_hide_panels = True                     
        row.operator("ed.redo", text="", icon="LOOP_FORWARDS")            
        row.operator("uv.select_border", text="", icon='BORDER_RECT')                                     
        row.operator("ed.undo", text="", icon="LOOP_BACK")                                                                     
        row.operator("screen.screen_full_area", text = "", icon = "FULLSCREEN_ENTER")     


        row = box.row(1)
        row.alignment ='CENTER'

        row.scale_y = 1.25             

        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text=" ").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text=" ").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text=" ").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text=" ").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text=" ").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text=" ").shape = 'MAX'   



######------------################################################################################################################
######  Registry  ################################################################################################################
######  Registry  ################################################################################################################
######------------################################################################################################################



def register():
    bpy.utils.register_class(image_editor_uvspaceFA)    
    bpy.utils.register_class(image_editor_uvsculpt) 
 
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Image', space_type='IMAGE_EDITOR')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'PRESS')
        kmi.properties.name = "uv.editspaceFA"      


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='UV Sculpt')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'SPACE', 'PRESS')
        kmi.properties.name = "uv.sculpt"  



def unregister():
    bpy.utils.unregister_class(image_editor_uvspaceFA)    
    bpy.utils.unregister_class(image_editor_uvsculpt) 

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['Image']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "":
                    km.keymap_items.remove(kmi)
                    break 


    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps['UV Sculpt']
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu_pie':
                if kmi.properties.name == "":
                    km.keymap_items.remove(kmi)
                    break 

if __name__ == "__main__":
    register() 	

    # The menu can also be called from scripts
    bpy.ops.wm.call_menu_pie(name=image_editor_uvspaceFA.bl_idname)
    #bpy.ops.wm.call_menu_pie(name=image_editor_uvsculpt.bl_idname)