# space_view3d_weight_tool.py (c) 2009, 2010 Gabriel Beaudin (gabhead)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****

import bpy
from bpy.props import *

bl_info = {
    'name': 'Edit Weight',
    'author': 'Gabriel Beaudin (gabhead)',
    'version': (1,0),
    'blender': (2, 5, 4),
    'location': 'Object Tools',
    'description': 'Tool to assign normalised weight over vertex groups and display the weight in the view3D.',
    'url': 'not',
    'category': '3D View'}

# operator
class UtilsMesh:
    def DoesVertHaveGroup(Vert,groupId):
        Id = 0
        for i in Vert.groups:
            Id+=1
            if i.group == groupId:
                return Id
        return False
    
    def ColorVert(VertexColor):
        obj = bpy.context.object
        Faces = bpy.context.object.data.faces#Dat Faces
        Verts = bpy.context.object.data.vertices
        Vc=bpy.context.object.data.vertex_colors[VertexColor].data
        ActiveVertexGroupId = obj.vertex_groups.active.index
        ColorRampEvaluate = bpy.context.user_preferences.system.weight_color_range.evaluate
        for face in range (len(bpy.context.object.data.faces)):#loop Faces
            CurrentFace = (Faces[face])#define current Face
            for Fv in range(len(CurrentFace.vertices)):
                Dvert = UtilsMesh.DoesVertHaveGroup(Verts[CurrentFace.vertices[Fv]],ActiveVertexGroupId)
                if Dvert != False:
                    Dvert -= 1 #Previous Test Falis if Test does (0 == False)it ansers True ...need to OffSet
                    VertId = CurrentFace.vertices[Fv]
                    VertWeight =Verts[VertId].groups[Dvert].weight
                    theColor = ColorRampEvaluate(VertWeight)
                    theColor = (theColor[0],theColor[1],theColor[2])
                    if Fv == 0:
                        Vc[face].color1 = theColor
                    elif Fv == 1:
                        Vc[face].color2 = theColor
                    elif Fv == 2:
                        Vc[face].color3 = theColor
                    elif Fv == 3:
                        Vc[face].color4 = theColor
                else:
                    theColor = ColorRampEvaluate(0)
                    theColor = (theColor[0],theColor[1],theColor[2])
                    if Fv == 0:
                        Vc[face].color1 = theColor
                    elif Fv == 1:
                        Vc[face].color2 = theColor
                    elif Fv == 2:
                        Vc[face].color3 = theColor
                    elif Fv == 3:
                        Vc[face].color4 = theColor
        
    def VColorFromWeight():
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.game_settings.material_mode = 'TEXTURE_FACE'
        obj = bpy.context.object
        if "WeightColor" in obj.data.vertex_colors:
            ActiveVG = obj.vertex_groups.active
            UtilsMesh.ColorVert('WeightColor')
        else:
            bpy.ops.mesh.vertex_color_add()
            obj.data.vertex_colors[len(obj.data.vertex_colors)-1].name = "WeightColor"
            UtilsMesh.VColorFromWeight()
        bpy.ops.object.mode_set(mode='EDIT')
        TheGroupId = obj.vertex_groups.active_index
        bpy.types.Scene.WeightRedraw = TheGroupId
    
    def GetSelectedVerts():
        if len(bpy.context.selected_objects) == 1:
            ArrayVerts = [];
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.editmode_toggle()
            for i in range(0,(len(bpy.context.object.data.vertices))):
                if bpy.context.object.data.vertices[i].select == True:
                    ArrayVerts.append(i);
            return(ArrayVerts);

    def AssingNormalizedWeight(weight,update):
        obj = bpy.context.object
        IndexKeeper = (obj.vertex_groups.active_index)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.area.type = "PROPERTIES"
        bpy.context.scene.tool_settings.vertex_group_weight = weight
        bpy.ops.object.vertex_group_assign()
        bpy.context.area.type = "VIEW_3D"
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        obj.vertex_groups.active_index = IndexKeeper
        for i in UtilsMesh.GetSelectedVerts():
            sum = 0
            for k in obj.data.vertices[i].groups:
                if k.group != obj.vertex_groups.active_index:
                    sum += k.weight
            for k in obj.data.vertices[i].groups:
                if k.group != obj.vertex_groups.active_index:
                        if sum != 0:
                            k.weight *= (1 - weight)/sum
                        else:
                            k.weight = (1 - weight)/(len(obj.data.vertices[i].groups)-1)
        if update:
            UtilsMesh.VColorFromWeight()
    
    def NormalizedOffset(weight):
        obj = bpy.context.object
        IndexKeeper = (obj.vertex_groups.active_index)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        obj.vertex_groups.active_index = IndexKeeper
        ArrayVertThatDoesNotHaveTheGroup = []
        IniSel = UtilsMesh.GetSelectedVerts()
        for i in IniSel:
            sum = 0
            HaveTheGroup = False
            theOffSetGroupWeight = 33
            for j in obj.data.vertices[i].groups:
                if j.group != obj.vertex_groups.active_index:
                    sum += j.weight
                else:
                    HaveTheGroup = True
                    theOffSetGroupWeight = j.weight
            
            if  HaveTheGroup:# The vert got the group to offset
                realoffset = 33
                if theOffSetGroupWeight + weight > 1 and weight >= 0:
                    realoffset = 1 -theOffSetGroupWeight
                elif theOffSetGroupWeight + weight < 0 and weight <= 0:
                    realoffset = -(theOffSetGroupWeight)
                elif theOffSetGroupWeight + weight <= 1 and theOffSetGroupWeight + weight >= 0:
                    realoffset = weight
                for k in obj.data.vertices[i].groups:
                    if k.group != obj.vertex_groups.active_index:## To normalize
                        if sum != 0:
                            k.weight *= ((1 -(theOffSetGroupWeight+realoffset))/sum)
                        else:
                            if theOffSetGroupWeight + weight > 1 and weight >= 0:
                                pass
                            else:
                                k.weight = (1 - realoffset)/(len(obj.data.vertices[i].groups)-1)
                    else:#To assign
                        k.weight += realoffset
            else:# Must Add the group and add the offSet
                append = ArrayVertThatDoesNotHaveTheGroup.append
                append(i)
        if len(ArrayVertThatDoesNotHaveTheGroup)>0:
            #Select None
            bpy.ops.object.mode_set(mode='OBJECT')
            for v in bpy.context.object.data.vertices:
                v.select = False
            #Select Array
            for v in ArrayVertThatDoesNotHaveTheGroup:
                obj.data.vertices[v].select = True
            #Assing Weight
            UtilsMesh.AssingNormalizedWeight(weight,False)
            #Select None
            bpy.ops.object.mode_set(mode='OBJECT')
            for v in bpy.context.object.data.vertices:
                v.select = False
            #GetBack To Initial Selection
            for v in IniSel:
                obj.data.vertices[v].select = True
        UtilsMesh.VColorFromWeight()

class AddOffSetNormalizedMore(bpy.types.Operator):
    bl_idname = "OffSetWeight +"
    bl_label = "OffSetWeight +"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.NormalizedOffset(bpy.context.scene.Offset_Weight)
        return {'FINISHED'}

class AddOffSetNormalizedLess(bpy.types.Operator):
    bl_idname = "OffSetWeight -"
    bl_label = "OffSetWeight -"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.NormalizedOffset(-(bpy.context.scene.Offset_Weight))
        return {'FINISHED'}

class WeightSelectMore(bpy.types.Operator):
    bl_idname = "Weight Select More"
    bl_label = "Weight Select More"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        bpy.ops.mesh.select_more()
        return {'FINISHED'}

class WeightSelectLess(bpy.types.Operator):
    bl_idname = "Weight Select Less"
    bl_label = "Weight Select Less"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        bpy.ops.mesh.select_less()
        return {'FINISHED'}

class WeightOperatorsO(bpy.types.Operator):
    bl_idname = "Weight 0"
    bl_label = "Weight 0"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0,True)
        return {'FINISHED'}
    
class WeightOperatorsA(bpy.types.Operator):
    bl_idname = "Weight .1"
    bl_label = "Weight .1"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0.1,True)
        return {'FINISHED'}
class WeightOperatorsB(bpy.types.Operator):
    bl_idname = "Weight .25"
    bl_label = "Weight .25"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0.25,True)
        return {'FINISHED'}
    
class WeightOperatorsC(bpy.types.Operator):
    bl_idname = "Weight .5"
    bl_label = "Weight .5"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0.5,True)
        return {'FINISHED'}
    
class WeightOperatorsD(bpy.types.Operator):
    bl_idname = "Weight .75"
    bl_label = "Weight .75"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0.75,True)
        return {'FINISHED'}
    
class WeightOperatorsE(bpy.types.Operator):
    bl_idname = "Weight .9"
    bl_label = "Weight .9"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(0.9,True)
        return {'FINISHED'}

class WeightOperatorsF(bpy.types.Operator):
    bl_idname = "Weight 1"
    bl_label = "Weight 1"
    @classmethod
    def poll(self, context):
        return context.active_object != None
    def execute(self, context):
        UtilsMesh.AssingNormalizedWeight(1,True)
        return {'FINISHED'}
    
bpy.types.Scene.WeightRedraw=IntProperty(
            name="WeightRedraw",
            attr="WeightRedraw",
            description="WeightRedraw",
            default=0,
            min=0,
            max=1
            )
class WeightTable(bpy.types.Panel):
    bl_label = "WeightTool"
    bl_context = "mesh_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        bpy.types.Scene.Offset_Weight=FloatProperty(
            name="Offset",
            attr="Offset_Weight",
            description="Offset_Weight",
            default=0.1,
            min=0,
            max=1
            )
        if len(bpy.context.object.vertex_groups)!=0:
            if bpy.types.Scene.WeightRedraw != bpy.context.object.vertex_groups.active.index:
                UtilsMesh.VColorFromWeight()
        if obj != None:
            FirstRow = layout.row(align=True)
            FirstRow.operator("Weight Select Less",text="Select Less -")
            FirstRow.operator("Weight Select More",text="Select More +")
            if len(bpy.context.object.vertex_groups) > 0:
                SecoundRow = layout.row(align=True)
                SecoundRow.operator("Weight 0",text="0")
                SecoundRow.operator("Weight .1",text="0.1")
                SecoundRow.operator("Weight .25",text="0.25")
                SecoundRow.operator("Weight .5",text="0.5")
                SecoundRow.operator("Weight .75",text="0.75")
                SecoundRow.operator("Weight .9",text="0.9")
                SecoundRow.operator("Weight 1",text="1")
                ThirdRow = layout.row(align=True)
                ThirdRow.prop(data=bpy.context.scene,property="Offset_Weight")
                ThirdRow.operator("OffSetWeight -",text="-")
                ThirdRow.operator("OffSetWeight +",text="+")
            TheCol = layout.column()
            TheCol.template_list(bpy.context.object, "vertex_groups", bpy.context.object.vertex_groups, "active_index", rows=2)
            TheCol.template_color_ramp(bpy.context.user_preferences.system, "weight_color_range", expand=True)
            
def register():
    pass

def unregister():
    pass

if __name__ == "__main__":
    register()