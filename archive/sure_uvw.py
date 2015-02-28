bl_info = {
    "name": "Sure UVW Map Addon v.0.3",
    "author": "Alexander Milovsky (www.3dmaster.ru)",
    "version": (0, 3),
    "blender": (2, 6, 0),
    "api": 36079,
    "location": "Properties > Object Data (below UV Texture), parameters in Tool Properties",
    "description": "Box/Best Planar UVW Map (Make Material With Raster Texture First!)",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/",
    "tracker_url": "https://projects.blender.org/tracker/index.php",
    "category": "Mesh"}

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty, FloatVectorProperty
from math import sin, cos, pi
from mathutils import Vector

# globals for Box Mapping
all_scale_def = 1
x_offset_def = 0
y_offset_def = 0
z_offset_def = 0
x_rot_def = 0
y_rot_def = 0
z_rot_def = 0


# globals for Best Planar Mapping
xoffset_def = 0
yoffset_def = 0
zrot_def = 0


def main():    
    global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def
    obj = bpy.context.active_object
    mesh = obj.data

    is_editmode = (obj.mode == 'EDIT')

    # if in EDIT Mode switch to OBJECT
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # if no UVtex - create it
    if not mesh.uv_textures:
        uvtex = bpy.ops.mesh.uv_texture_add()
    uvtex = mesh.uv_textures.active
    uvtex.active_render = True
    
    img = None    
    aspect = 1.0
    mat = obj.active_material
    try:
        if mat:
            img = mat.active_texture
            aspect = img.image.size[0]/img.image.size[1]
            for f in mesh.faces:  
                if not is_editmode or f.select:
                    uvtex.data[f.index].image = img.image
        else:
            img = None        
    except:
        pass

                
    
    #
    # Main action
    #
    if all_scale_def:
        sc = 1.0/all_scale_def
    else:
        sc = 1.0   

    sx = 1 * sc
    sy = 1 * sc
    sz = 1 * sc
    ofx = x_offset_def
    ofy = y_offset_def
    ofz = z_offset_def
    rx = x_rot_def / 180 * pi
    ry = y_rot_def / 180 * pi
    rz = z_rot_def / 180 * pi
    for i, uv in enumerate(uvtex.data):
        if not is_editmode or mesh.faces[i].select:
            uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
            for j, v_idx in enumerate(mesh.faces[i].vertices):
                n = mesh.faces[i].normal
                co = mesh.vertices[v_idx].co
                x = co.x * sx
                y = co.y * sy
                z = co.z * sz
                if abs(n[0]) > abs(n[1]) and abs(n[0]) > abs(n[2]):
                    # X
                    if n[0] >= 0:
                        uvs[j][0] =  y * cos(rx) + z * sin(rx)                    - ofy * cos(rx) - ofz*sin(rx) # ok 
                        uvs[j][1] = -y * aspect * sin(rx) + z * aspect * cos(rx)  + ofy * sin(rx) - ofz*cos(rx) # ok
                    else:
                        uvs[j][0] = -y * cos(rx) + z * sin(rx)                    + ofy * cos(rx) - ofz*sin(rx) # ok 
                        uvs[j][1] =  y * aspect * sin(rx) + z * aspect * cos(rx)  - ofy * sin(rx) - ofz*cos(rx) # ok 
                elif abs(n[1]) > abs(n[0]) and abs(n[1]) > abs(n[2]):
                    # Y
                    if n[1] >= 0:
                        uvs[j][0] =  -x * cos(ry) + z * sin(ry)                   + ofx * cos(ry) - ofz*sin(ry) # ok
                        uvs[j][1] =   x * aspect * sin(ry) + z * aspect * cos(ry) - ofx * sin(ry) - ofz*cos(ry) # ok
                    else:
                        uvs[j][0] =   x * cos(ry) + z * sin(ry)                   - ofx * cos(ry) - ofz*sin(ry) # ok
                        uvs[j][1] =  -x * aspect * sin(ry) + z * aspect * cos(ry) + ofx * sin(ry) - ofz*cos(ry) # ok
                else:
                    # Z
                    if n[2] >= 0:
                        uvs[j][0] =   x * cos(rz) + y * sin(rz) +                 - ofx * cos(rz) - ofy*sin(rz)
                        uvs[j][1] =  -x * aspect * sin(rz) + y * aspect * cos(rz) + ofx * sin(rz) - ofy*cos(rz)
                    else:
                        uvs[j][0] =  -y * sin(rz) - x * cos(rz)                   + ofx * cos(rz) - ofy*sin(rz)
                        uvs[j][1] =   y * aspect * cos(rz) - x * aspect * sin(rz) - ofx * sin(rz) - ofy*cos(rz)
    
    # Back to EDIT Mode
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

# Best Planar Mapping
def main2():
    global all_scale_def,xoffset_def,yoffset_def,zrot_def
    
    obj = bpy.context.active_object
    mesh = obj.data

    is_editmode = (obj.mode == 'EDIT')

    # if in EDIT Mode switch to OBJECT
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # if no UVtex - create it
    if not mesh.uv_textures:
        uvtex = bpy.ops.mesh.uv_texture_add()
    uvtex = mesh.uv_textures.active
    uvtex.active_render = True
    
    img = None    
    aspect = 1.0
    mat = obj.active_material
    try:
        if mat:
            img = mat.active_texture
            aspect = img.image.size[0]/img.image.size[1]
            for f in mesh.faces:  
                if not is_editmode or f.select:
                    uvtex.data[f.index].image = img.image
        else:
            img = None        
    except:
        pass

                
    
    #
    # Main action
    #
    if all_scale_def:
        sc = 1.0/all_scale_def
    else:
        sc = 1.0   

    # Calculate Average Normal
    v = Vector((0,0,0))
    cnt = 0
    for f in mesh.faces:  
        if f.select:
            cnt += 1
            v = v + f.normal
    
    zv = Vector((0,0,1))
    q = v.rotation_difference(zv)
            

    sx = 1 * sc
    sy = 1 * sc
    sz = 1 * sc
    ofx = xoffset_def
    ofy = yoffset_def
    rz = zrot_def / 180 * pi


    for i, uv in enumerate(uvtex.data):
        if mesh.faces[i].select:
            uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
            for j, v_idx in enumerate(mesh.faces[i].vertices):
                n = mesh.faces[i].normal
                co = q * mesh.vertices[v_idx].co
                x = co.x * sx
                y = co.y * sy
                z = co.z * sz
                uvs[j][0] =  x * cos(rz) - y * sin(rz) + xoffset_def
                uvs[j][1] =  aspect*(- x * sin(rz) - y * cos(rz)) + yoffset_def



    # Back to EDIT Mode
    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)


class SureBoxUVWOperator(bpy.types.Operator):
    bl_idname = "object.sureboxuvw_operator"
    bl_label = "Sure UVW Map"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    
    bl_options = {'REGISTER', 'UNDO'}

    
    action = StringProperty()  

    size = FloatProperty(name="Size", default=1.0)
    rot = FloatVectorProperty(name="XYZ Rotation")
    offset = FloatVectorProperty(name="XYZ offset")

    zrot = FloatProperty(name="Z rotation", default=0.0)
    xoffset = FloatProperty(name="X offset", default=0.0)
    yoffset = FloatProperty(name="Y offset", default=0.0)

    flag90 = BoolProperty()
    flag90ccw = BoolProperty()

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def, xoffset_def, yoffset_def, zrot_def
        all_scale_def = self.size
        x_offset_def = self.offset[0]
        y_offset_def = self.offset[1]
        z_offset_def = self.offset[2]
        x_rot_def = self.rot[0]
        y_rot_def = self.rot[1]
        z_rot_def = self.rot[2]

        xoffset_def = self.xoffset
        yoffset_def = self.yoffset
        zrot_def = self.zrot

        
        if self.flag90:
          self.zrot += 90
          zrot_def += 90
          self.flag90 = False

        if self.flag90ccw:
          self.zrot += -90
          zrot_def += -90
          self.flag90ccw = False

        
        if self.action == 'bestplanar':
            main2()
        elif self.action == 'box':
            main()

        return {'FINISHED'}

    def invoke(self, context, event):
        global all_scale_def,x_offset_def,y_offset_def,z_offset_def,x_rot_def,y_rot_def,z_rot_def, xoffset_def, yoffset_def, zrot_def
        
        self.size = all_scale_def
        self.offset[0] = x_offset_def
        self.offset[1] = y_offset_def
        self.offset[2] = z_offset_def
        self.rot[0] = x_rot_def
        self.rot[1] = y_rot_def
        self.rot[2] = z_rot_def

        
        self.xoffset = xoffset_def
        self.yoffset = yoffset_def
        self.zrot = zrot_def
        
        if self.action == 'bestplanar':
            main2()
        elif self.action == 'box':
            main()
            
        return {'FINISHED'}

    def draw(self, context):
        if self.action == 'bestplanar' or self.action == 'rotatecw' or self.action == 'rotateccw':
            self.action = 'bestplanar'
            layout = self.layout
            layout.label("Size - "+self.action)
            layout.prop(self,'size',text="")
            layout.label("Z rotation")
            col = layout.column()
            col.prop(self,'zrot',text="")
            row = layout.row()
            row.prop(self,'flag90ccw',text="-90 (CCW)")
            row.prop(self,'flag90',text="+90 (CW)")
            layout.label("XY offset")
            col = layout.column()
            col.prop(self,'xoffset', text="")
            col.prop(self,'yoffset', text="")
        elif self.action == 'box':          
            layout = self.layout
            layout.label("Size")
            layout.prop(self,'size',text="")
            layout.label("XYZ rotation")
            col = layout.column()
            col.prop(self,'rot', text="")
            layout.label("XYZ offset")
            col = layout.column()
            col.prop(self,'offset', text="")
             

class SureBoxUVWPanel(bpy.types.Panel):
    bl_label = "Sure UVW Box Mapping v.0.3"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    #bl_space_type = "VIEW_3D"
    #bl_region_type = "TOOLS"
    #bl_region_type = "TOOL_PROPS"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def draw(self, context):
        self.layout.operator("object.sureboxuvw_operator",text="UVW Box Map").action='box'
        self.layout.operator("object.sureboxuvw_operator",text="Best Planar Map").action='bestplanar'

#
# Registration
#

def register():
    bpy.utils.register_class(SureBoxUVWOperator)
    bpy.utils.register_class(SureBoxUVWPanel)


def unregister():
    bpy.utils.unregister_class(SureBoxUVWOperator)
    bpy.utils.unregister_class(SureBoxUVWPanel)


if __name__ == "__main__":
    register()
