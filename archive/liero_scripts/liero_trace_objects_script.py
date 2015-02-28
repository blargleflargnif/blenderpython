#################################################################
# join selected objects with a curve + hooks to each node v 0.2 #
#################################################################

bl_info = {
    "name": "Connect Objects",
    "author": "liero",
    "version": (0, 2),
    "blender": (2, 5, 7),
    "location": "View3D > Tool Shelf",
    "description": "Connect selected objects with a curve + hooks",
    "category": "Animation"}

import bpy

class TraceObjs(bpy.types.Operator):
    bl_idname = 'objects.trace'
    bl_label = 'Connect'
    bl_description = 'Connect selected objects with a curve + hooks'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (len(bpy.context.selected_objects) > 1)

    def execute(self, context):
        # list objects
        lista = []
        sce = bpy.context.scene
        wm = bpy.context.window_manager
        for a in bpy.context.selected_objects:
            lista.append(a)
            a.select = False

        # trace the origins
        tracer = bpy.data.curves.new('tracer','CURVE')
        tracer.dimensions = '3D'
        spline = tracer.splines.new('BEZIER')
        spline.bezier_points.add(len(lista)-1)
        curva = bpy.data.objects.new('curva',tracer)
        bpy.context.scene.objects.link(curva)

        # render ready curve
        tracer.resolution_u = 64
        tracer.bevel_resolution = 3
        try: tracer.fill_mode = 'FULL'
        except: tracer.use_fill_front = tracer.use_fill_back = False
        tracer.bevel_depth = 0.025
        if 'mat' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat')
            mat.diffuse_color = [0,.5,1]
            mat.use_shadeless = True
        tracer.materials.append(bpy.data.materials.get('mat'))

        # move nodes to objects
        for i in range(len(lista)):
            p = spline.bezier_points[i]
            p.co = lista[i].location
            p.handle_right_type=wm.tipo
            p.handle_left_type=wm.tipo

        sce.objects.active = curva
        bpy.ops.object.mode_set()

        # place hooks
        for i in range(len(lista)):
            lista[i].select = True
            curva.data.splines[0].bezier_points[i].select_control_point = True
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.hook_add_selob()
            bpy.ops.object.editmode_toggle()
            curva.data.splines[0].bezier_points[i].select_control_point = False
            lista[i].select = False

        for a in lista:
            a.select = True
        return{'FINISHED'}

class PanelCO(bpy.types.Panel):
    bl_label = 'Connect Objects'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        obj = bpy.context.object
        layout = self.layout
        column = layout.column()
        column.operator('objects.trace')
        column.prop(context.window_manager, 'tipo')
        if obj.type == 'CURVE' and obj.data.name.startswith('tracer'):
            column = layout.column(align=True)
            column.label(text='Active tracer settings:')
            column.prop(obj.data, 'bevel_depth')
            column.prop(obj.data, 'bevel_resolution')
            column.prop(obj.data, 'resolution_u')

bpy.types.WindowManager.tipo = bpy.props.EnumProperty( name="", items=[('Select','Select','Select'),('FREE','Free','Free'),( 'AUTO','Auto','Auto'),('VECTOR','Vector','Vector'),('ALIGNED','Aligned','Aligned')], description='Spline Type for the bezier points', default='VECTOR')

def register():
    bpy.utils.register_class(TraceObjs)
    bpy.utils.register_class(PanelCO)

def unregister():
    bpy.utils.unregister_class(TraceObjs)
    bpy.utils.unregister_class(PanelCO)

if __name__ == '__main__':
    register()