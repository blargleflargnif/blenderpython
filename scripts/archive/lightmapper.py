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

# ########################################################
# Change Log:
#Ver 0.572 - 01/24/2011
#	Fix problems with Operation id_names [ before Crash with build 34473 ]
#
#Ver 0.57 - 01/24/2011
#    Fix Warnings in Blender 2.56a
#    Remove Dynamic Previews for now, need more work in that
#	 Work right as Add-on ( Add-on Pannel )
#
#Ver 0.56 - 09/22/2010
#   Improve the "Split Mode" to split the objects in final of Bake
#       - Right readd objects in group list after split objects
#   Improve the Dynamic Preview
#       - Now update all groups 
#       - Working with Slip Mode ON
#
#Ver 0.55 - 09/12/2010
#	Add Support do Blender 2.5.4 Beta
#
#Ver 0.54 - 09/04/2010
#	Add Group system
#	Fixed Bugs in Dynamic Preview 
###########################################################

# ########################################################
# Lightmapper 0.57
#
# Vitor Balbio
# Rio de Janeiro - Brasil
# 
# ########################################################

bl_info = {
    "name": "Lightmapper",
    "author": "Vitor Balbio",
    "version": (0,572),
    "blender": (2, 5, 6),
    "api": 34470,
    "location": "Render > Lightmapper",
    "description": "Make easy the workflow of lightmap generation",
    "warning": "Beta",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/Render/Lightmapper",
    "tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=24567",
    "category": "Render"}

import bpy

class LIGHTMAP_GEN(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_label = " "
    ListOB = []
    Groups = []

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="LightMapper", icon="WORLD")
        
    def draw(self, context):
        
        import bpy
        layout = self.layout
        Body = layout.column()
        Body.label(text="Object Groups: " + str(len(self.Groups))  , icon = "SCENE_DATA")
        
        Box = layout.box()
        Column = Box.column()
        Column.prop(context.scene,"GroupList")
        index = bpy.context.scene.GroupList
        
        Box2 = Box.box()
        ColumnIN = Box2.column()
                
        try:
            DysplayList = self.Groups[index]
        except:
            DysplayList = []
            
        if DysplayList != []:
            for i in range(len(self.Groups[index])):
                ob = self.Groups[index][i]
                if ob in context.selected_objects:
                    ColumnIN.label(text = ob.name, icon='EDIT')
                else:
                    ColumnIN.label(text = ob.name, icon='OBJECT_DATAMODE')
        else:
            ColumnIN.label(text ="Click in \"Add\" to add some objets to Bake", icon= "HELP")
                    
        Body2 = Column.row()
        Body2.operator(".addtolist",text="Add")
        Body2.operator(".remobjlist",text="Delete")
        Body2.operator(".clearobjlist",text="Update")
        Body22 = Column.row()
        Body22.operator(".selectobj",text="Select Objects")
                
        Body2_1 = layout.row()
        Body2_1.label(text="Configurations:",icon= 'EDIT')
        
        
        Div = layout.box()
        Body2_11=Div.row()
        Body2_11.label(text="Object Setings:",icon="OBJECT_DATAMODE")
        Body2_111 = Div.row()
        Body2_111.prop(context.scene,"NameGroup")
        Body2_111.prop(context.scene,"SEPONFIN",icon = "OBJECT_DATAMODE")
        
        Div1 = layout.box()
        Body2_2 = Div1.row()
        Body2_2.label(text="UV Setings:",icon="GRID")
        Body3 = Div1.row()
        Body3.prop(context.scene,"UVAng")
        Body3.prop(context.scene,"UVIslandMargin")
        Body3_1 = Div1.row()
        Body2_2.prop(context.scene,"PRESUV",icon = "TEXTURE")

        Div2 = layout.box()
        Body4 = Div2.row()
        Body4.label(text="Texture Setings:",icon="TEXTURE")
        Body4_1 = Div2.row()
        Body4.prop(context.scene,"LMRES")
        
        Div3 = layout.box()
        Body5 = Div3.row()
        Body5.label(text= "Maps Setings:",icon="IMAGEFILE")
        Body5_1 = Div3.row()
        Body5_1.prop(context.scene,"MAPSHADOW",icon="TEXTURE")
        Body5_1.prop(context.scene,"MAPAO",icon="TEXTURE")  
        Body5_2 = Div3.row()
        
        GENButton = layout.row()
        GENButton.operator(".lightmapgen",text="Make Lightmap", icon = "RENDER_STILL")
		
# Dynamic Previews Do not working in blender 2.56 - removed for now    
# 
#        Div4 = layout.box()
#        
#        Body6 = Div4.row()
#        Body6.prop(context.scene,"DYNPRE", icon ="RENDER_STILL")
#        Body6_1 = Div4.row()
#        Body6_1.prop(context.scene,"DYNSDON",icon="TEXTURE")
#        Body6_1.prop(context.scene,"DYNAOON",icon="TEXTURE")   
#        
#        Down = layout.column()
#        Down.label(text=" ver 0.5", icon="LIGHTPAINT")
#        
#
#
#        Render = context.scene.render
#
#            
#        if context.scene.DYNPRE and bpy.context.active_object.HAS_LIGHTMAP :
#            for i in range(len(bpy.data.objects)):
#                if bpy.data.objects[i].GroupLM != 99:
#                    bpy.data.objects[i].select = True # Torna o Objeto Selecionado
#                    bpy.context.scene.objects.active = bpy.data.objects[i] # Torna o objeto selecionado ativo
#                                
#            try:
#                if context.scene.DYNAOON:
#                    Render.bake_type = "AO"
#                    bpy.ops.object.bake_image()
#                if context.scene.DYNSDON:
#                    Render.bake_type = "SHADOW"
#                    bpy.ops.object.bake_image()
#                    
#            except:
#                pass
#            
#            
#            bpy.context.scene.objects.active = None # Desativa Todos

        if index > len(self.Groups):
            bpy.context.scene.GroupList = len(self.Groups)
    
class LIGHTMAP_GEN_ADDTOLIST(bpy.types.Operator):
	bl_label = "Add Object"
	bl_idname = ".addtolist"
	bl_description = "Add object to Lightmap Generator List"
    
	def invoke(self, context, event):
         import bpy
        
         index = bpy.context.scene.GroupList
         Groups = bpy.types.LIGHTMAP_GEN.Groups
         try:
             Groups[index] =  Groups[index] 
         except:
             Groups.append([])
        
         for i in range(len(context.selected_objects)):
             if context.selected_objects[i] not in Groups[index]:
                 if context.selected_objects[i].type == "MESH":
                     Groups[index].append(context.selected_objects[i])
        
         return{"FINISHED"}

class LIGHTMAP_GEN_REMOVETOLIST(bpy.types.Operator):
     bl_label = "Remove Object"
     bl_idname = ".remobjlist"
     bl_description = "Remove object to Lightmap Generator List"
    
     def invoke(self, context, event):
         import bpy
        
         index = bpy.context.scene.GroupList
         Groups = bpy.types.LIGHTMAP_GEN.Groups
         for i in range(len(context.selected_objects)):
             if context.selected_objects[i] in Groups[index]:
                 Groups[index].remove(context.selected_objects[i])
        
         if Groups[index] == []:
             Groups.remove(Groups[index])
           
         return{"FINISHED"}
        
    
class LIGHTMAP_ClearList(bpy.types.Operator):
    bl_label = "Clear Object"
    bl_idname = ".clearobjlist"
    bl_description = "Update the objects data to Lightmap Generator List"

    def invoke(self, context, event):
        import bpy
        index = bpy.context.scene.GroupList
        Groups = bpy.types.LIGHTMAP_GEN.Groups
        
        j = 0 
        
        if Groups[index] != []:
            
           for i in range(len(bpy.data.objects)):
               bpy.data.objects[i].select = True
            
           count_objs = len(Groups[index])
           
            
           while j < count_objs :
                if Groups[index][j] not in context.selected_objects:
                    Groups[index].remove(Groups[index][j])
                    count_objs -= 1
                    j -= 1
                    
                j += 1
           
           for k in range(len(bpy.data.objects)):
                bpy.data.objects[k].select = False
           
        if Groups[index] == []:
           Groups.remove(Groups[index])
                
        return{"FINISHED"}
    
class LIGHTMAP_SELECTFROMLIST(bpy.types.Operator):
    bl_label = "Select Objects"
    bl_idname = ".selectobj"
    bl_description = "Select Objects From List"
    
    def invoke(self, context, event):
        import bpy
        
        #Desceleciona todo mundo
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = None
            
        index = bpy.context.scene.GroupList
        Groups = bpy.types.LIGHTMAP_GEN.Groups
        
        for obj in Groups[index]:
            obj.select = True
           
        return{"FINISHED"}
    
class LIGHTMAP_GEN_BAKE(bpy.types.Operator):
    bl_label = "Bake Lightmap"
    bl_idname = ".lightmapgen"
    bl_description = " Start The Lightmap Generation"
    allOBj = []
        
    def invoke(self,context,event):
        import bpy
        
        
        index = 0
        while index <= len(bpy.types.LIGHTMAP_GEN.Groups)-1 :
            
            OBJList = []
            OBJList = bpy.types.LIGHTMAP_GEN.Groups[index]
            
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = None
                       
            
            if len(OBJList)> 1 :
                for j in range(len(OBJList)):
                    OBJList[j].select = True
                bpy.context.scene.objects.active = OBJList[len(OBJList)-1]
                bpy.ops.object.join()
            else:
                OBJList[0].select = True
                bpy.context.scene.objects.active = OBJList[0]
                            
            LM = context.selected_objects[0]
            bpy.types.LIGHTMAP_GEN.Groups[index]
            
            if context.scene.NameGroup:
                LM.name = context.scene.NameGroup + " " + str(index)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
            
            LM.HAS_LIGHTMAP = True
            LM.GroupLM = index
            
            
            PASS_LIST = []
            if context.scene.MAPAO:
                PASS_LIST.append("AO")
            if context.scene.MAPSHADOW:
                PASS_LIST.append("SD")
                          
            for PASS in PASS_LIST:
                 
                OBMesh = LM.data
                HaveUV = False 
                for texture in OBMesh.uv_textures:
                    if texture.name == "LightMap":
                        HaveUV = True
                        UV = texture    
                    
                if HaveUV == False:     
                    UV = OBMesh.uv_textures.new(name= "LightMap")
                    
                OBMesh.uv_textures.active = UV
                UV.active_render = True
                    
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.select_all(action='SELECT')
                if not context.scene.PRESUV: 
                    bpy.ops.uv.smart_project(angle_limit= context.scene.UVAng,island_margin = context.scene.UVIslandMargin)  
                bpy.ops.object.editmode_toggle()
                
                
                
                
                HaveImage = False
                for image in bpy.data.images:
                    if image.name == str(LM.name) + "LightMap_" + PASS:
                        HaveImage = True
                        LMImage = image
                
                if not HaveImage:
                    LMImage = bpy.data.images.new(name= str(LM.name) + "LightMap_" + PASS, width=context.scene.LMRES, height=context.scene.LMRES)    
                
                if LMImage.size[0] != context.scene.LMRES: 
                    LMImage.generated_width = context.scene.LMRES
                    LMImage.generated_height = context.scene.LMRES
                
                
                
                HaveTex = False
                for texture in bpy.data.textures:
                    if texture.name == str(LM.name) + "LM_" + PASS:
                        HaveTex = True
                        LMTexture = texture
                
                if not HaveTex:
                    LMTexture = bpy.data.textures.new(name= str(LM.name) + "LM_" + PASS, type = "IMAGE")
                
                        
               
                
                
                for Material in OBMesh.materials:
                    LMSlot = False
                    Material.active_texture_index = 0 
                    while Material.active_texture_index < 18:
                        if Material.active_texture == LMTexture:
                            LMSlot = True
                        if Material.active_texture == None:
                            break   
                        Material.active_texture_index += 1
                
                    if not LMSlot:
                        Material.active_texture = LMTexture
                        
                        
                        TexSlot = Material.texture_slots[Material.active_texture_index]    
                        TexSlot.texture_coords = "UV"
                        TexSlot.uv_layer = "LightMap"
                        TexSlot.use_map_color_diffuse  = True
                        TexSlot.blend_type  = "MULTIPLY"
                        LMTexture.image = LMImage
                    else:
                        TexSlot = Material.texture_slots[Material.active_texture_index-1]   
                
                 
                
                UV_Face = OBMesh.uv_textures.active.data[:]
                for face in UV_Face:
                    face.image = LMImage
                    face.use_image = True 
                
                   
                Render = context.scene.render
                Render.use_bake_normalize = True
                if PASS == "AO":
                    Render.bake_type = "AO"
                else:
                    if PASS == "SD":
                        Render.bake_type = "SHADOW"
                
                Render.bake_margin = 7
                bpy.ops.object.bake_image()
            
            
            if context.scene.SEPONFIN:
                bpy.ops.object.editmode_toggle()
                bpy.ops.mesh.separate(type="LOOSE")
                bpy.types.LIGHTMAP_GEN.Groups[index] = []
                bpy.ops.object.editmode_toggle()
                
                       
                for i in range(len(bpy.data.objects)):
                    if bpy.data.objects[i].GroupLM == index:
                                                                  
                        bpy.types.LIGHTMAP_GEN.Groups[index].append(bpy.data.objects[i])
                        
                        bpy.ops.object.select_all(action='DESELECT') 
                        bpy.context.scene.objects.active = None 
                        bpy.data.objects[i].select = True 
                        bpy.context.scene.objects.active = bpy.data.objects[i] 
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN') 
                    
            else:
                bpy.types.LIGHTMAP_GEN.Groups[index] = []
                bpy.types.LIGHTMAP_GEN.Groups[index].append(LM)
            
            print ("LightMap Suceess in Group " + str(index))
            index +=1
        bpy.ops.object.select_all(action='DESELECT') 
        bpy.context.scene.objects.active = None   
        return{"FINISHED"}
 
 

def register():
    bpy.utils.register_module(__name__)   
    bpy.types.Scene.UVAng = bpy.props.IntProperty(name = "Angle", description = "Angle Limit Betwen Polys to UV Generation ", default = 50, min = 0, max = 99)
    bpy.types.Scene.UVIslandMargin = bpy.props.FloatProperty(name = "Margin", description = "Angle Limit Betwen Polys to UV Generation ", default = 0.100, min = 0.000, max = 1.000)
    bpy.types.Scene.LMRES = bpy.props.IntProperty(name = "Resolution", description = "Resolution of Texture to Bake", default = 512, min = 0, max = 4096)
    bpy.types.Scene.PRESUV = bpy.props.BoolProperty(name = "Preserve UV", description = "Keep the UV without new unwarp ( to save time and manual uv editing cases )")
    bpy.types.Scene.MAPAO = bpy.props.BoolProperty(name = "AO", description = "Add the Projected Shadows to render list ")
    bpy.types.Scene.MAPSHADOW = bpy.props.BoolProperty(name = "SHADOW", description = "Add the Ambient Occlusion to render List")
    bpy.types.Scene.DYNAOON = bpy.props.BoolProperty(name = "AO", description = "Dynamic Shadow Update")
    bpy.types.Scene.DYNSDON = bpy.props.BoolProperty( name = "SHADOW", description = "Dynamic AO Update")
    bpy.types.Scene.SEPONFIN = bpy.props.BoolProperty(name = " Split Mode", description = "Separate the Objects on Finish")
    bpy.types.Scene.NameGroup = bpy.props.StringProperty(name = "Name", description = "Name of group after lightmap generation ")
    bpy.types.Scene.DYNPRE = bpy.props.BoolProperty(name = "Dynamic Preview", description = "Automatic Update Render")
    bpy.types.Scene.GroupList = bpy.props.IntProperty(name = "Group Slot", description = "Groups of Objects to Render",default = 0,min = 0,max = 99)
    bpy.types.Object.HAS_LIGHTMAP = bpy.props.BoolProperty(name = "Lightmap", description = "The Object have Lightmaps")
    bpy.types.Object.GroupLM = bpy.props.IntProperty(name = "GroupLM", description = "The Object Group of Lightmaps",default = 99,min = 0, max = 99)
        

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.Scene.RemoveProperty("UVAng")
    bpy.types.Scene.RemoveProperty("UVIslandMargin")
    bpy.types.Scene.RemoveProperty("PRESUV")
    bpy.types.Scene.RemoveProperty("MAPSHADOW")
    bpy.types.Scene.RemoveProperty("DYNAOON")
    bpy.types.Scene.RemoveProperty("DYNSDON")
    bpy.types.Scene.RemoveProperty("SEPONFIN")
    bpy.types.Scene.RemoveProperty("NameGroup")
    bpy.types.Scene.RemoveProperty("DYNPRE")
    bpy.types.Scene.RemoveProperty("GroupList")
    

if __name__ == "__main__":
    register() 