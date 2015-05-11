from asyncio.windows_events import NULL
bl_info = {
    "name" : "Align utils",
    "description": "A module for hastly aligning one object to enough either with quick align or full align",
    "author" : "Smoke Fumus <smokethehedgehog@gmail.com>",
    "version": (0,1),
    "blender": (2,74,0),
    "location": "Spacebar > Align util",
    "warning": "",
    "wiki_url": "none yet",
    "category": "Object",
}



import bpy

from mathutils import Vector, Matrix, Quaternion, Euler, Color
from bpy_extras import view3d_utils

def main(context, event, ray_max=1000.0):
    """Run this function on left mouse, execute the ray cast"""
    # get the context arguments
    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    # get the ray from the viewport and mouse
    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    ray_target = ray_origin + (view_vector * ray_max)

    def visible_objects_and_duplis():
        """Loop over (object, matrix) pairs (mesh only)"""

        for obj in context.visible_objects:
            if obj.type == 'MESH':
                yield (obj, obj.matrix_world.copy())

            if obj.dupli_type != 'NONE':
                obj.dupli_list_create(scene)
                for dob in obj.dupli_list:
                    obj_dupli = dob.object
                    if obj_dupli.type == 'MESH':
                        yield (obj_dupli, dob.matrix.copy())

            obj.dupli_list_clear()

    def obj_ray_cast(obj, matrix):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv * ray_origin
        ray_target_obj = matrix_inv * ray_target

        # cast the ray
        hit, normal, face_index = obj.ray_cast(ray_origin_obj, ray_target_obj)

        if face_index != -1:
            return hit, normal, face_index
        else:
            return None, None, None

    # cast rays and find the closest object
    best_length_squared = ray_max * ray_max
    best_obj = None

    for obj, matrix in visible_objects_and_duplis():
        if obj.type == 'MESH':
            hit, normal, face_index = obj_ray_cast(obj, matrix)
            if hit is not None:
                hit_world = matrix * hit
                scene.cursor_location = hit_world
                length_squared = (hit_world - ray_origin).length_squared
                if length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = obj

    # now we have the object under the mouse cursor,
    # we could do lots of stuff but for the example just select.
    if best_obj is not None:
        return best_obj
    else:
        return NULL

  
class AlignUtil(bpy.types.Operator):  
    bl_idname = "object.align_util"  
    bl_label = "Align Util"  
    bl_options = {'REGISTER', 'UNDO'}
    alignX=bpy.props.BoolProperty(name="Align by X", description="Nil", default=True)
    alignY=bpy.props.BoolProperty(name="Align by Y", description="Nil", default=True)
    alignZ=bpy.props.BoolProperty(name="Align by Z", description="Nil", default=True)
    

    def invoke(self, context, event):
        if bpy.context.mode != 'OBJECT' and len(bpy.context.selected_objects)==0 :
            return {'CANCELLED'} 
        
        print(context.window_manager.modal_handler_add(self))
        return {'RUNNING_MODAL'}
    
    
    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':  # Confirm
            self.alignObject=main(context, event)
            if self.alignObject==NULL:
                return {'CANCELLED'} 
            self.execute(context)
            #print("click")
            return {'FINISHED'}
        elif event.type in ('RIGHTMOUSE', 'ESC'):  # Cancel
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}
    
    
    def execute(self, context):
        try:
            pPoint
        except NameError:
            self.pPoint=context.active_object.location

        
        if self.alignX:
            context.active_object.location.x=self.alignObject.location.x
        else:
            context.active_object.location.x=self.pPoint.x
        if self.alignY:
            context.active_object.location.y=self.alignObject.location.y
        else:
            context.active_object.location.y=self.pPoint.y
        if self.alignZ:
            context.active_object.location.z=self.alignObject.location.z
        else:
            context.active_object.location.z=self.pPoint.z
        return {'FINISHED'}
  

def register():
    bpy.utils.register_module(__name__)
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('object.align_util', 'A', 'PRESS', shift=True)

  
def unregister():
    bpy.utils.unregister_module(__name__) 
    if kc:
        km = kc.keymaps["3D View"]
        for kmi in km.keymap_items:
            if kmi.idname == 'object.align_util':
                km.keymap_items.remove(kmi)
                break
  
if __name__ == "__main__":
    try:
        unregister()
    except:
        pass
    register()