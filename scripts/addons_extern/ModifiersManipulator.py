bl_info = {
    "name": "Modifiers Manipulator",
    "author": "kilbee",  
    "version": (0, 1),  
    "blender": (2, 6, 9),  
    "description": "Adds simple functionality for modifiers manipulation",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Object",
}

import bpy
import time



class DrawPanel(bpy.types.Panel):
    bl_label = "Object Modifier Management"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"


    def draw(self, context):
        objects = bpy.context.selected_objects
        active = bpy.context.active_object
        obj = context.object
        
        layout = self.layout
        row = layout.row()
        column = layout.column()
        box = column.box()
        box.operator("modifiers.copy", text = "Copy Modifiers from Active to Selected")
        box.operator("modifiers.remove", text = "Delete All Modifiers from Selected")

        column.operator_menu_enum("scene.select_objects", "select_objects", text = "Select object")
        # modifier select:
        column.label("Select objects by Modifier name:")
        row = layout.row()
#        column.prop(context.scene, '[""]')
        column.menu("dropdown.menu",text="Pick Modifier")
        # menu:
        if not objects: 
            column.label(text="Selection is empty")
            return

        #box.alignment = 'CENTER'
        column.label(text="Active object: ")
        box = column.box()
        box.prop(active, "name", icon='OBJECT_DATA')
        box.separator()
        for modifier in active.modifiers:
            if modifier.type != "PARTICLE_SYSTEM":
                box.prop(modifier, "name", icon='MODIFIER')
        for particle_system in active.particle_systems:
            box.prop(particle_system.settings, "name", icon='PARTICLES')
        ### this is for material listing:
        #for material_slot in active.material_slots:
        #    if not material_slot.material:
        #        pass
        #    else:
        #        box.prop(material_slot.material, "name", icon='MATERIAL')
        
        # if only active object is selected:
        if len(objects) == 1:
            column.label(text="Only Active selected.")
            return

        # if more than 1 objects are selected
        column.label(text="Selected objects:")
        for sobject in objects:
            if sobject != bpy.context.active_object:
                box = column.box()
                box.prop(sobject, "name", icon='OBJECT_DATA')
                box.operator("make.active", text = "Make [{}] active object".format(sobject.name)).name=sobject.name
                box.separator()
                for modifier in sobject.modifiers:
                    if modifier.type != "PARTICLE_SYSTEM":
                        box.prop(modifier, "name", icon='MODIFIER')
                for particle_system in sobject.particle_systems:
                    box.prop(particle_system.settings, "name", icon='PARTICLES')



class DropDownMenuOperator(bpy.types.Menu):
    bl_idname = "dropdown.menu"
    bl_label = "Show Modifier in Scene"

    def draw(self, context):
        objects = context.scene.objects
        layout = self.layout        
        modifier_list = self.make_list()        
        layout.label("Select Modifier")
        for item in modifier_list:
            text = item
            layout.operator("scene.select_objects", text=text).name=text # define var after dot to pass additional argument to operator

    def make_list(self):
        modifier_list = []
        for obj in bpy.data.objects:
            for modifier in obj.modifiers:
            # add object do the list
                if modifier.name in modifier_list:
                    pass
                else:
                    modifier_list.append(modifier.name)                
        modifier_list.sort()
        return modifier_list



class SelectObjectOperator(bpy.types.Operator):
    bl_idname = "scene.select_objects"
    bl_label = "Select Object Operator"
    name = bpy.props.StringProperty()   # additional argument passed form menu list button

    def execute(self, context):
        context.scene[""] = self.name
        bpy.ops.object.select_all(action='DESELECT')    #deselect all objects first
        modifier_name = self.name
        object_list = self.make_object_list(modifier_name)
        self.select_objs(object_list, modifier_name)
        return {'FINISHED'}

    def make_object_list(self, modifier_name):
        objects = []
        for obj in bpy.data.objects:
            for modifier in obj.modifiers:
                if modifier.name == modifier_name:
                    # appends object do the list:
                    if not modifier.name in objects:
                        objects.append(obj.name)
        objects.sort()
        return objects

    def select_objs(self, object_list, modifier_name):
        if not object_list:
            return
        else:
            for obj in object_list:
                bpy.data.objects[obj].select = True
                bpy.context.scene.objects.active = bpy.data.objects[obj]   # also make last object active



class MakeActiveOperator(bpy.types.Operator):
    bl_idname = "make.active"
    bl_label = "Make Object an Active"
    bl_options = {"UNDO"}
    name = bpy.props.StringProperty()   #passed additional var
    def invoke(self, context, event):
        bpy.context.scene.objects.active = bpy.data.objects[self.name]
        self.report({'INFO'}, "{} {} {}".format(time.strftime("%H:%M:%S"), bpy.context.scene.objects.active.name, 'is now Active Object'))
        return {"FINISHED"}



class RemoveModifiersOperator(bpy.types.Operator):
    bl_idname = "modifiers.remove"
    bl_label = "Remove Modifiers"
    bl_options = {"UNDO"}
    def invoke(self, context, event):
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                obj.modifiers.clear()   #remove modifiers
        self.report({'INFO'}, "{} {}".format(time.strftime("%H:%M:%S"), 'Modifiers removed from selected Objects'))
        return {"FINISHED"}



class CopyModifiersModifier(bpy.types.Operator):
    bl_idname = "modifiers.copy"
    bl_label = "Copy Modifiers"
    bl_options = {"UNDO"}
    def invoke(self, context, event):
        try:
            bpy.ops.object.make_links_data(type='MODIFIERS') # copies modifiers from active to selected
            self.report({'INFO'}, "{} {}".format(time.strftime("%H:%M:%S"), 'Modifiers copied Active Object'))
        except:
            pass
        return {"FINISHED"}



def register():
    bpy.utils.register_class(DrawPanel)
    bpy.utils.register_class(DropDownMenuOperator)
    bpy.utils.register_class(MakeActiveOperator)
    bpy.utils.register_class(SelectObjectOperator)
    bpy.utils.register_class(RemoveModifiersOperator)
    bpy.utils.register_class(CopyModifiersModifier)

def unregister():
    bpy.utils.unregister_class(DrawPanel)
    bpy.utils.unregister_class(DropDownMenuOperator)
    bpy.utils.unregister_class(MakeActiveOperator)
    bpy.utils.unregister_class(SelectObjectOperator)
    bpy.utils.unregister_class(RemoveModifiersOperator)
    bpy.utils.unregister_class(CopyModifiersModifier)

if __name__ == "__main__":
    register()  
