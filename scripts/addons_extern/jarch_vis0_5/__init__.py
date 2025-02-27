bl_info = {
    "name" : "JARCH Vis",
    "author" : "Jacob Morris",
    "version" : (0, 5),
    "blender" : (2, 74, 0),
    "location" : "View 3D > Toolbar > JARCH Vis",
    "description" : "Adds Architectural Objects Like Flooring, Siding, Stairs, and Roofing",
    "category" : "Add Mesh"
    }

if "bpy" in locals():
    import imp  
    imp.reload(jarch_siding)
    imp.reload(jarch_flooring)
    imp.reload(jarch_stairs)
    imp.reload(jarch_roofing)
else: 
    from . import jarch_siding
    from . import jarch_flooring
    from . import jarch_stairs
    from . import jarch_roofing

import bpy
from bpy.props import StringProperty, CollectionProperty, IntProperty, FloatProperty

class FaceGroup(bpy.types.PropertyGroup):
    data = StringProperty()
    num_faces = IntProperty()
    face_slope = FloatProperty()
    rot = FloatProperty(unit = "ROTATION")  

class INFO_MT_mesh_jarch_menu_add(bpy.types.Menu):
    bl_idname = "INFO_MT_mesh_jarch_menu_add"
    bl_label = "JARCH Vis"
    def draw(self, context):
        layout = self.layout       
        layout.operator("mesh.jarch_flooring_add", text = "Add Flooring", icon = "MESH_GRID")
        layout.operator("mesh.jarch_roofing_add", text = "Add Roofing", icon = "LINCURVE")
        layout.operator("mesh.jarch_siding_add", text = "Add Siding", icon = "UV_ISLANDSEL")
        layout.operator("mesh.jarch_stairs_add", text = "Add Stairs", icon = "MOD_ARRAY")        
                
def menu_add(self, context):
    self.layout.menu("INFO_MT_mesh_jarch_menu_add", icon = "PLUGIN")

def register():
    bpy.utils.register_module(__name__)   
    bpy.types.INFO_MT_mesh_add.append(menu_add)
    bpy.types.Object.face_groups = CollectionProperty(type=FaceGroup)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Object.face_groups
    
if __name__ == "__main__":
    register()
