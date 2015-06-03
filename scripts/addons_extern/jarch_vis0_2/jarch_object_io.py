import bpy
from bpy.props import StringProperty
from datetime import datetime
from time import tzname
import xml.etree.cElementTree as ET
import ast
from xml.dom.minidom import parse as pretty_parse
from os import path
from mathutils import Color

def export_object(self, context):
    epath = context.scene.jarch_save_path_export #export path
    error = True
    if "//" in epath:
        epath = bpy.path.abspath(epath)
    if path.exists(epath):
        error = False    
        
    #if path exists
    if error == False:
        ob = context.object
        epath += "\\" + (ob.name).replace(".", "_") + ".jarch"
        root = ET.Element("object")
        
        t = datetime.now()
        date_string = "{}/{}/{} at {}:{}:{} in {}".format(t.month, t.day, t.year, t.hour, t.minute, t.second, tzname[0])
        root.attrib = {"Date_Created":date_string, "Mesh_Name":ob.data.name, "Object_Name":ob.name}                       
    
        #create XML tree
        properties = ET.SubElement(root, "properties")        
            
        #properties
        props = ["mat", "if_tin", "if_wood", "if_vinyl", "is_cut", "cut_name", "object_add", "from_dims", "is_slope", "over_height", "over_width", "board_width", 
                "batten_width", "board_space", "slope", "is_width_vary", "width_vary", "is_cutout", "num_cutouts", "is_length_vary", "length_vary", "max_boards", 
                "res", "is_screws", "bevel_width", "x_offset", "b_width", "b_height", "b_ran_offset", "b_offset", "b_gap", "m_depth", "b_vary", "is_bevel", 
                "bump_type", "color_style", "mat_color2", "mat_color3", "color_sharp", "mortar_color", "mortar_bump", "brick_bump", "color_scale", "bump_scale", 
                "is_corner", "is_invert", "is_soldier", "is_left", "is_right", "av_width", "av_height", "s_random", "b_random", "s_mortar", "s_mat", "is_material", 
                "mat_color", "is_preview", "im_scale", "col_image", "is_bump", "norm_image", "bump_amo", "unwrap", "is_rotate", "random_uv", "nc1", "nc2", "nc3", 
                "nc4", "nc5", "nc6", "f_object_add", "f_cut_name", "f_is_cut", "f_mat", "f_if_wood", "f_if_tile", "f_over_width", "f_over_length", "f_b_width", 
                "f_b_length", "f_b_length2", "f_is_length_vary", "f_length_vary", "f_max_boards", "f_is_width_vary", "f_width_vary", "f_num_boards", "f_space_l", 
                "f_space_w", "f_spacing", "f_is_bevel", "f_res", "f_bevel_amo", "f_is_ran_height", "f_ran_height", "f_t_width", "f_t_length", "f_grout_depth", 
                "f_is_offset", "f_offset", "f_is_random_offset", "f_offset_vary", "f_t_width2", "f_is_material", "f_is_preview", "f_im_scale", "f_col_image", 
                "f_is_bump", "f_norm_image", "f_bump_amo", "f_unwrap", "f_mortar_color", "f_mortar_bump", "f_is_rotate", "f_random_uv", "s_object_add", "s_style", 
                "s_overhang", "s_num_steps", "s_num_steps2", "s_tread_width", "s_riser_height", "s_over_front", "s_over_sides", "s_width", "s_is_riser", 
                "s_num_land", "s_is_close", "s_is_set_in", "s_is_landing", "s_is_light", "s_num_steps0", "s_tread_width0", "s_riser_height0", "s_landing_depth0", 
                "s_landing_rot0", "s_over_front0", "s_over_sides0", "s_overhang0", "s_is_back0", "s_num_steps1", "s_landing_rot1", "s_tread_width1", 
                "s_riser_height1", "s_landing_depth1", "s_over_front1", "s_over_sides1", "s_overhang1", "s_is_back1", "s_w_rot", "s_num_rot", "s_rot", 
                "s_pole_dia", "s_pole_res", "s_tread_res", "s_is_material", "s_is_preview", "s_im_scale", "s_col_image", "s_is_bump", "s_norm_image", 
                "s_bump_amo", "s_is_rotate", "s_im_scale2", "s_col_image2", "s_is_bump2", "s_norm_image2", "s_bump_amo2", "s_is_rotate2", "s_unwrap", 
                "s_random_uv"]                
                
        for prop in props:
            #determine type
            val = eval("ob." + prop)
            if type(val) is int:
                t = "int"
            elif type(val) is float:
                t = "float"
            elif type(val) is str:
                t = "str"
            elif type(val) is Color:
                t = "Color"
                val = tuple(val)
            elif type(val) is bool:
                t = "bool"
                    
            ET.SubElement(properties, "prop", {"value":str(val), "name":prop, "type":t})
            
        #save file
        tree = ET.ElementTree(root)
        error2 = True
        try:
            tree.write(epath)
            error2 = False
        except (PermissionError, FileNotFoundError):
           self.report({"ERROR"}, "Permission Denied At That Location")
           
        #make text pretty
        if error2 == False:
            pretty_file = pretty_parse(epath)
            pretty_text = pretty_file.toprettyxml()
            file = open(epath, "w")
            file.write(pretty_text)
            file.close()
        

def import_object(self, context):
    ipath = context.scene.jarch_save_path_import
    if ipath != "" and path.exists(bpy.path.abspath(ipath)) == True and ipath.endswith(".jarch"):
        tree = ET.parse(ipath)
        root = tree.getroot()        
        
        bpy.ops.mesh.primitive_cube_add()
        ob = context.object
        ob.name = root.attrib["Object_Name"]
        
        #get properties
        properties = root.findall("properties")[0]
        for prop in properties:
            #figure out what to do with value
            val = prop.attrib["value"]
            t = prop.attrib["type"]
            
            if t == "str":                   
                temp = "ob." + prop.attrib["name"] + " = " + "\"" + val + "\""
            else:
                temp = "ob." + prop.attrib["name"] + " = " + str(val)
                
            exec(temp)
    else:
        self.report({"ERROR"}, "Either No Path Was Selected, Or That Path Doesn't Exist, Or This Is Not A JARCH Vis File")
            

bpy.types.Scene.jarch_save_path_export = StringProperty(name = "Export Path", subtype = "DIR_PATH")
bpy.types.Scene.jarch_save_path_import = StringProperty(name = "Import Path", subtype = "FILE_PATH")

class ObjectIOPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_object_io_panel"
    bl_label = "JARCH Vis: Object IO"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "JARCH Vis"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        o = context.object
        if o != None:
            if o.object_add not in ("none", "mesh") or o.s_object_add not in ("none", "mesh") or o.f_object_add not in ("none", "mesh"):
                layout.prop(context.scene, "jarch_save_path_export")
                layout.operator("export.object_io_export")
            else:
                layout.label("This Is Not A JARCH Vis Object", icon = "ERROR")
        layout.separator()
        layout.prop(context.scene, "jarch_save_path_import")
        layout.operator("import.object_io_import")        
    
class ObjectIOExport(bpy.types.Operator):
    bl_idname = "export.object_io_export"
    bl_label = "Export Object"
    
    def execute(self, context):
        export_object(self, context)
        return {"FINISHED"}

class ObjectIOImport(bpy.types.Operator):
    bl_idname = "import.object_io_import"
    bl_label = "Import Object"
    
    def execute(self, context):
        import_object(self, context)
        return {"FINISHED"}                   