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
    "name": "Mesh Check",
    "author": "Clarkx, Cedric Lepiller, CoDEmanX",
    "version": (0, 0, 1),
    "blender": (2, 74, 0),
    "description": "Custom Menu to show faces, tri, Ngons on the mesh",
    "category": "3D View",}




import bpy
from bpy.props import EnumProperty


bpy.types.Scene.show_faces = bpy.props.BoolProperty(default=False)


##CoDEmanX's code to select Ngons, tri  
class DATA_OP_facetype_select(bpy.types.Operator):
    """Select all faces of a certain type"""
    bl_idname = "data.facetype_select"
    bl_label = "Select by face type"
    bl_options = {'REGISTER', 'UNDO'}


    face_type = EnumProperty(name="Select faces:",
                             items = (("3","Triangles","Faces made up of 3 vertices"),
                                      ("4","Quads","Faces made up of 4 vertices"),
                                      ("5","Ngons","Faces made up of 5 and more vertices")),
                             default = "5")
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'


    def execute(self, context):


        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        context.tool_settings.mesh_select_mode=(False, False, True)


        if self.face_type == "3":
            bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
        elif self.face_type == "4":
            bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
        else:
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')


        return {'FINISHED'}


#Clarkx's code to show faces, Ngons and Tris with the vertex paint mode.
class Show_Faces(bpy.types.Operator):
    bl_idname = "object.showfaces"
    bl_label = "Show Faces"
    bl_description = "Show Tri, Ngons and Faces"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        scn = context.scene
        
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        bpy.ops.object.mode_set(mode="VERTEX_PAINT")


        bpy.ops.mesh.vertex_color_remove()
        # Objet actif
        mesh = context.active_object.data


        # Creation d'un nouveau vertex color
        vertex_colors = mesh.vertex_colors.new().data


        # Pour chaque polygon de l'object
        for poly in mesh.polygons:
            
            # Recupration du nombre de vertices
            nbvert = len(poly.vertices)
            
            # Pour chaque vertex on assigne une couleur :
            for loop_index in poly.loop_indices:


                # Rouge : Si le polygon a trois vertices
                if nbvert == 3: # Triangle
                    vertex_colors[loop_index].color =  [0.603, 0.500, 0.117]


                # Vert : Si le polygon a quatre vertices
                if nbvert == 4: # Quad
                    vertex_colors[loop_index].color =  [0.5, 0.5, 0.5]


                # Bleu : Si le polygon a un nombre de vertices > 4
                if nbvert > 4: # Ngons
                    vertex_colors[loop_index].color =  [0.8, 0.146, 0.146]
                    
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.context.space_data.viewport_shade = 'TEXTURED'  
        
        scn.show_faces = True
        
        
        
        return {"FINISHED"}    


class Remove_Vertex_Color(bpy.types.Operator):
    bl_idname = "object.removevertexcolor"
    bl_label = "Remove Vertex Color"
    bl_description = "Remove Vertex Color to clean the List"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        scn = context.scene
        
        bpy.ops.mesh.vertex_color_remove()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.space_data.viewport_shade = 'SOLID'
        scn.show_faces = False


        return {"FINISHED"} 


class Show_Faces_Menu(bpy.types.Panel):
    bl_idname = "view3D.show_faces_menu"
    bl_label = "Mesh Check"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Mesh Check"
    
    
    
    @classmethod
    def poll(self, context):          
        return context.active_object is not None and context.active_object.type == 'MESH'
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        
        if scn.show_faces == False:
            
            layout.operator("object.showfaces", text='Show Faces', icon='COLOR')
            
        else:
            row = layout.row(align=True)
            row.operator("object.removevertexcolor", text='Hide Faces', icon='GHOST_ENABLED') 
            row.operator("object.showfaces", text='Refresh', icon='FILE_REFRESH')  
        
        
        #code by CoDEmanX to select Ngons, tri   
        ob = context.active_object
        
        info_str = ""
        tris = quads = ngons = 0


        for p in ob.data.polygons:
            count = p.loop_total
            if count == 3:
                tris += 1
            elif count == 4:
                quads += 1
            else:
                ngons += 1


        info_str = "  Ngons: %i  Quads: %i  Tris: %i" % (ngons, quads, tris)
        
        col = layout.column()
        col.label(info_str, icon='MESH_DATA')


        col = layout.column()
        col.label("Select faces by type:")


        row = layout.row(align=True)
        row.operator("data.facetype_select", text="Ngons").face_type = "5"
        row.operator("data.facetype_select", text="Quads").face_type = "4"
        row.operator("data.facetype_select", text="Tris").face_type = "3"   
        


def register():
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()

