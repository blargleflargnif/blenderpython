# wahooney_uv_normalize.py Copyright (C) 2009-2010, Keith "Wahooney" Boshoff
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

bl_info = {
    'name': 'Normalize UVs',
    'author': 'Keith (Wahooney) Boshoff',
    'version': '1.2',
    'blender': (2, 5, 5),
    'location': 'UVs > Normalize UVs',
    'url': '',
    'category': 'UV'}

import bpy
from bpy.props import *
from mathutils import Vector

def main(self, context):
    obj = context.active_object
    mesh = obj.data
    
    axis = self.properties.axis
    
    x_size = self.properties.x_size
    y_size = self.properties.y_size
    
    padding = self.properties.padding
    
    include_unselected = self.properties.include_unselected
    
    if self.properties.lock_size:
        y_size = x_size
    
    x_position = self.properties.x_position
    y_position = self.properties.y_position

    is_editmode = (obj.mode == 'EDIT')
    if is_editmode:
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    if not mesh.uv_textures.active:
        bpy.ops.mesh.uv_texture_add()

    min = Vector((10000, 10000, 0))
    max = Vector((-10000, -10000, 0))

    # get min/max uvs
    for i, uv in enumerate(mesh.uv_textures.active.data):
        if not mesh.faces[i].select:
            continue
            
        uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
        for j, v_idx in enumerate(mesh.faces[i].vertices):
            if uv.select_uv[j]: # and not uv.invisible:
                # find the absolutes
                if uvs[j][0] < min.x:
                    min.x = uvs[j][0]

                if uvs[j][1] < min.y:
                    min.y = uvs[j][1]

                if uvs[j][0] > max.x:
                    max.x = uvs[j][0]

                if uvs[j][1] > max.y:
                    max.y = uvs[j][1]

    # get uv bottom/left offsets
    offX = min.x
    offY = min.y

    # get multiplier to fit uvs into 0.0 - 1.0 space
    multX = 1.0 / (max.x - min.x)
    multY = 1.0 / (max.y - min.y)
    
    # copy multiplier from one to the other, based on axis restrictions
    if axis == 'X':
        multY = multX
    elif axis == 'Y':
        multX = multY
        
    multX = multX * x_size
    multY = multY * y_size
    
    # get remaining space (for positioning)
    sx = 1.0 - (max.x - min.x) * multX
    sy = 1.0 - (max.y - min.y) * multY
    
    # get padding inverse scaling
    padMult = 1.0 - padding * 2
        
    for i, uv in enumerate(mesh.uv_textures.active.data):
        if not mesh.faces[i].select:
            continue
        
        uvs = uv.uv1, uv.uv2, uv.uv3, uv.uv4
        for j, v_idx in enumerate(mesh.faces[i].vertices):
            if uv.select_uv[j] or include_unselected:
                # apply the location of the vertex as a UV
                uvs[j][0] = padding + ((uvs[j][0] - offX) * multX + sx * x_position) * padMult
                uvs[j][1] = padding + ((uvs[j][1] - offY) * multY + sy * y_position) * padMult

    if is_editmode:
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)

class NormalizeUV(bpy.types.Operator):
    ''''''
    bl_idname = "uv.normalize_uvs"
    bl_label = "Normalize UVs"
    bl_options = {'REGISTER', 'UNDO'}
    
    axis = EnumProperty(items=(
                        ('XY', "X & Y", "Both axis are affected"),
                        ('X', "X", "X is normalized, y is scaled proportionally"),
                        ('Y', "Y", "Y is normalized, x is scaled proportionally")),
                name="Axis",
                description="Normalization Axis",
                default='XY')

    x_size = FloatProperty(name="X Size", description="Total X Size",
            default=1.0,
            min=0.0,
            max=100,
            soft_min=0.0,
            soft_max=1.0)

    y_size = FloatProperty(name="Y Size", description="Total Y Size",
            default=1.0,
            min=0.0,
            max=100,
            soft_min=0.0,
            soft_max=1.0)

    lock_size = BoolProperty(name="Lock Size",
                description="Lock X and Y Size",
                default=True)
            
    x_position = FloatProperty(name="X Position", 
                description="Proportional position on the X axis",
                default=0.0,
                min=-100.0,
                max=100.0,
                soft_min=0.0,
                soft_max=1.0)
                
    y_position = FloatProperty(name="Y Position", 
                description="Proportional position on the Y axis",
                default=0.0,
                min=-100.0,
                max=100.0,
                soft_min=0.0,
                soft_max=1.0)

    padding = FloatProperty(name="Padding", 
                description="Edge padding",
                default=0.0,
                min=0.0,
                max=0.5,
                soft_min=0.0,
                soft_max=0.05)
                
    include_unselected = BoolProperty(name="Include unselected",
                description="Scales and positions unselected uv vertices, selected vertices are used to determine ranges.",
                default=False)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}
        
    def draw(self, context):
        layout = self.layout
        props = self.properties
        
        layout.prop(props, "axis", expand=True)
        
        row = layout.row()
        
        col = row.column(align=True)
        col.label(text="Size")
        
        if (self.properties.lock_size):
            col.prop(props, "x_size", text="Size")
        else:
            col.prop(props, "x_size")
            col.prop(props, "y_size")
            
        col.prop(props, "lock_size")

        col = layout.column(align=True)

        col.label(text="Position")
        col.prop(props, "x_position")
        col.prop(props, "y_position")
        
        col = layout.column()
        
        col.prop(props, "padding", slider=True)
        col.prop(props, "include_unselected")
        
def menu_func(self, context):
    self.layout.operator(NormalizeUV.bl_idname)

def register():
    #bpy.types.register(NormalizeUV)
    bpy.types.IMAGE_MT_uvs.append(menu_func)

def unregister():
    #bpy.types.unregister(NormalizeUV)
    bpy.types.IMAGE_MT_uvs.remove(menu_func)

if __name__ == "__main__":
    register()