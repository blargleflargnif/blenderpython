bl_info = {
    'name' : 'Hide / Unhide by Type',
    'author' : 'Felix Schlitter',
    'version' : (0, 1),
    'blender' : (2, 56, 2),
    'api' : 35391,
    'location' : 'View3D > Object > Show/Hide',
    'description' : 'Hide and Show Objects by type',
    'category' : '3D View'}
    
import bpy


class OBJECT_OT_HideShowByTypeTemplate():

    bl_options = {'UNDO','REGISTER'}
    
    type = bpy.props.EnumProperty(items=(
                        ('MESH', 'Mesh', ''),
                        ('CURVE', 'Curve', ''),
                        ('SURFACE', 'Surface', ''),
                        ('META', 'Meta', ''),
                        ('FONT', 'Font', ''),
                        ('ARMATURE', 'Armature', ''),
                        ('LATTICE', 'Lattice', ''),
                        ('EMPTY', 'Empty', ''),
                        ('CAMERA', 'Camera', ''),
                        ('LAMP', 'Lamp', ''),
                        ('ALL', 'All', '')),
            name='Type',
            description='Type',
            default='LAMP',
            options={'ANIMATABLE'})
            
    def execute(self, context):
    
        scene = bpy.context.scene
        objects = []
        eligible_objects = []
        
        # Only Selected?
        if self.hide_selected:
            objects = bpy.context.selected_objects
        else:
            objects = scene.objects 
        
        # Only Specific Types? + Filter layers
        for obj in objects: 
            for i in range(0,20):
                if obj.layers[i] & scene.layers[i]:
                    if self.type == 'ALL' or obj.type == self.type:
                        if obj not in eligible_objects:
                            eligible_objects.append(obj)                     
        objects = eligible_objects
        eligible_objects = []
        
        
        # Only Render Restricted?
        if self.hide_render_restricted:
            for obj in objects:
                if obj.hide_render == self.hide_or_show:
                    eligible_objects.append(obj)
            objects = eligible_objects
            eligible_objects = []

        # Perform Hiding / Showing
        for obj in objects:
            obj.hide = self.hide_or_show

        return {'FINISHED'}
        
    def invoke(self, context, event):
        return self.execute(context)
           


class OBJECT_OT_HideByType(OBJECT_OT_HideShowByTypeTemplate, bpy.types.Operator):
    bl_idname = 'object.hide_by_type'
    bl_label = 'Hide By Type'
    hide_or_show = bpy.props.BoolProperty(
        name="Hide",
        description="Inverse effect",
        options={'HIDDEN'},
        default=1
        )
    hide_selected = bpy.props.BoolProperty(
        name="Selected",
        description="Hide only selected objects",
        default=0
        )
    hide_render_restricted = bpy.props.BoolProperty(
        name="Only Render-Restricted",
        description="Hide only render restricted objects",
        default=0
        )
    
class OBJECT_OT_ShowByType(OBJECT_OT_HideShowByTypeTemplate, bpy.types.Operator):
    bl_idname = 'object.show_by_type'
    bl_label = 'Show By Type'
    hide_or_show = bpy.props.BoolProperty(
        name="Hide",
        description="Inverse effect",
        options={'HIDDEN'},
        default=0
        )
    hide_selected = bpy.props.BoolProperty(
        name="Selected",
        options={'HIDDEN'},
        default=0
        )
    hide_render_restricted = bpy.props.BoolProperty(
        name="Only Renderable",
        description="Show only non render restricted objects",
        default=0
        )


def DRAW_hide_by_type_MENU(self, context):
    self.layout.operator_menu_enum(
        "object.hide_by_type",
        "type", text="Hide By Type"
        )
    self.layout.operator_menu_enum(
        "object.show_by_type",
        "type", text="Show By Type"
        )   
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object_showhide.append(DRAW_hide_by_type_MENU)
    
def unregister():
    bpy.types.VIEW3D_MT_object_showhide.remove(DRAW_hide_by_type_MENU)
    bpy.utils.unregister_module(__name__)

if __name__ == "main" :
    register()
