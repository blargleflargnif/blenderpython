
bl_info = {
    "name": "Import-Export Metasequoia Format (.mqo)",
    "author": "Ze10",
    "version": (1, 0, 6),
    "blender": (2, 5, 7),
    "api": 36147,
    "location": "File > Import-Export",
    "description": "Import-Export to the Metasequoia Format (.mqo)",
    "warning": "",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    
    if "import_mqo" in locals():
    	imp.reload(import_mqo)
    	
    if "export_mqo" in locals():
    	imp.reload(export_mqo)
    	
else:
    from . import import_mqo
    from . import export_mqo
    
import bpy
import os

def menu_func_import(self, context): 
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mqo"
    self.layout.operator(import_mqo.MetasequoiaImporter.bl_idname, text="Metasequoia (.mqo)", icon='PLUGIN').filepath = default_path

def menu_func_export(self, context): 
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".mqo"
    self.layout.operator(export_mqo.MetasequoiaExporter.bl_idname, text="Metasequoia (.mqo)", icon='PLUGIN').filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__=="__main__":
    register()
