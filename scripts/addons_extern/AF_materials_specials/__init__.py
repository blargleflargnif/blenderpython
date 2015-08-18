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
# by meta-androcto, parts based on work by Saidenka #

bl_info = {
    "name": "Materials Specials",
    "author": "Meta Androcto",
    "version": (0, 2),
    "blender": (2, 75, 0),
    "location": "Materials Specilas Menu",
    "description": "Extended Specials: Materials Properties",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6"\
        "/Py/Scripts",
    "tracker_url": "",
    "category": "Addon Factory"}



if "bpy" in locals():
    import importlib
    importlib.reload(space_view3d_materials_utils)


else:
    from . import space_view3d_materials_utils

import bpy

class RemoveNoAssignMaterial(bpy.types.Operator):
	bl_idname = "material.remove_no_assign_material"
	bl_label = "Delete non-assignment material"
	bl_description = "Delete all one assigned to a surface material"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (len(obj.material_slots) <= 0):
			return False
		return True
	def execute(self, context):
		preActiveObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				context.scene.objects.active = obj
				preActiveMaterial = obj.active_material
				slots = []
				for slot in obj.material_slots:
					slots.append((slot.name, 0))
				me = obj.data
				for face in me.polygons:
					slots[face.material_index] = (slots[face.material_index][0], slots[face.material_index][1] + 1)
				for name, count in slots:
					if (name != "" and count == 0):
						i = 0
						for slot in obj.material_slots:
							if (slot.name == name):
								break
							i += 1
						obj.active_material_index = i
						bpy.ops.object.material_slot_remove()
		context.scene.objects.active = preActiveObj
		return {'FINISHED'}

class RemoveAllMaterialSlot(bpy.types.Operator):
	bl_idname = "material.remove_all_material_slot"
	bl_label = "Remove all material slots"
	bl_description = "Delete all material slots for this object"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (len(obj.material_slots) <= 0):
			return False
		return True
	def execute(self, context):
		activeObj = context.active_object
		if (activeObj.type == "MESH"):
			while True:
				if (0 < len(activeObj.material_slots)):
					bpy.ops.object.material_slot_remove()
				else:
					break
		return {'FINISHED'}

class RemoveEmptyMaterialSlot(bpy.types.Operator):
	bl_idname = "material.remove_empty_material_slot"
	bl_label = "Delete empty material slots"
	bl_description = "Delete all material of this object has not been assigned material slots"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		for slot in obj.material_slots:
			if (not slot.material):
				return True
		return False
	def execute(self, context):
		activeObj = context.active_object
		if (activeObj.type == "MESH"):
			slots = activeObj.material_slots[:]
			slots.reverse()
			i = 0
			for slot in slots:
				active_material_index = i
				if (not slot.material):
					bpy.ops.object.material_slot_remove()
				i += 1
		return {'FINISHED'}

class SetTransparentBackSide(bpy.types.Operator):
	bl_idname = "material.set_transparent_back_side"
	bl_label = "Transparent back (BI)."
	bl_description = "Creates BI nodes transparently mesh background"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		mat = context.material
		if (not mat):
			return False
		if (mat.node_tree):
			if (len(mat.node_tree.nodes) == 0):
				return True
		if (not mat.use_nodes):
			return True
		return False
	def execute(self, context):
		mat = context.material
		mat.use_nodes = True
		if (mat.node_tree):
			for node in mat.node_tree.nodes:
				if (node):
					mat.node_tree.nodes.remove(node)
		mat.use_transparency = True
		node_mat = mat.node_tree.nodes.new('ShaderNodeMaterial')
		node_out = mat.node_tree.nodes.new('ShaderNodeOutput')
		node_geo = mat.node_tree.nodes.new('ShaderNodeGeometry')
		node_mat.material = mat
		node_out.location = [node_out.location[0]+500, node_out.location[1]]
		node_geo.location = [node_geo.location[0]+150, node_geo.location[1]-150]
		mat.node_tree.links.new(node_mat.outputs[0], node_out.inputs[0])
		mat.node_tree.links.new(node_geo.outputs[8], node_out.inputs[1])
		return {'FINISHED'}

class MoveMaterialSlotTop(bpy.types.Operator):
	bl_idname = "material.move_material_slot_top"
	bl_label = "Slot to the top"
	bl_description = "Move the active material slots on top"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (len(obj.material_slots) <= 2):
			return False
		if (obj.active_material_index <= 0):
			return False
		return True
	def execute(self, context):
		activeObj = context.active_object
		for i in range(activeObj.active_material_index):
			bpy.ops.object.material_slot_move(direction='UP')
		return {'FINISHED'}

class MoveMaterialSlotBottom(bpy.types.Operator):
	bl_idname = "material.move_material_slot_bottom"
	bl_label = "Slots to the bottom"
	bl_description = "Move the active material slot at the bottom"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		if (not obj):
			return False
		if (len(obj.material_slots) <= 2):
			return False
		if (len(obj.material_slots)-1 <= obj.active_material_index):
			return False
		return True
	def execute(self, context):
		activeObj = context.active_object
		lastSlotIndex = len(activeObj.material_slots) - 1
		for i in range(lastSlotIndex - activeObj.active_material_index):
			bpy.ops.object.material_slot_move(direction='DOWN')
		return {'FINISHED'}

class MATERIAL_OT_link_to_base_names(bpy.types.Operator):
    bl_idname = "material.link_to_base_names"
    bl_label = "Link materials to base names"
    bl_description = "Replace .001, .002 slots with Original Material/Name"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for ob in context.scene.objects:
            for slot in ob.material_slots:
                self.fixup_slot(slot)

        return {'FINISHED'}

    def split_name(self, material):
        name = material.name

        if not '.' in name:
            return name, None

        base, suffix = name.rsplit('.', 1)
        try:
            num = int(suffix, 10)
        except ValueError:
            # Not a numeric suffix
            return name, None

        return base, suffix

    def fixup_slot(self, slot):
        if not slot.material:
            return

        base, suffix = self.split_name(slot.material)
        if suffix is None:
            return

        try:
            base_mat = bpy.data.materials[base]
        except KeyError:
            print('Base material %r not found' % base)
            return

        slot.material = base_mat

class VIEW3D_MT_delete_material(bpy.types.Menu):
    bl_label = "Delete Materials"
    bl_idname = "VIEW3D_MT_delete_material"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.separator()
        layout.operator("view3d.clean_material_slots",
                        text="Clean Material Slots",
                        icon='CANCEL')
        layout.operator("view3d.material_remove",
                        text="Remove Material Slots",
                        icon='CANCEL')

        self.layout.separator()
        self.layout.operator(RemoveAllMaterialSlot.bl_idname, icon='CANCEL', text="Remove All")
        self.layout.operator("material.remove_empty_material_slot", icon='CANCEL', text="Remove Empty")
        self.layout.operator("material.remove_no_assign_material", icon='CANCEL', text="Delete Unused")

def menu_func(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_REGION_WIN'

    layout.separator()
    layout.menu("VIEW3D_MT_assign_material", icon='ZOOMIN')
    layout.menu("VIEW3D_MT_select_material", icon='HAND')

    layout.separator()
    layout.menu("VIEW3D_MT_delete_material", icon="CANCEL")
    layout.operator("material.link_to_base_names", icon='LINKED', text="Link Base Names")

    layout.separator()
    layout.operator("view3d.replace_material",
                    text='Replace Material',
                    icon='ARROW_LEFTRIGHT')

    layout.operator("view3d.fake_user_set",
                    text='Set Fake User',
                    icon='UNPINNED')

    self.layout.separator()
    self.layout.operator("material.move_material_slot_top", icon='TRIA_UP', text="Slot to top")
    self.layout.operator("material.move_material_slot_bottom", icon='TRIA_DOWN', text="Slot to bottom")

    self.layout.separator()
    layout.operator("view3d.material_to_texface",
                    text="Material to Texface",
                    icon='MATERIAL_DATA')
    layout.operator("view3d.texface_to_material",
                    text="Texface to Material",
                    icon='MATERIAL_DATA')

    self.layout.separator()
    self.layout.operator("material.set_transparent_back_side", icon='PLUGIN', text="Transparent back (BI)")


def register():
    bpy.utils.register_module(__name__)
    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.MATERIAL_MT_specials.append(menu_func)





def unregister():

    # Remove "Extras" menu from the "Add Mesh" menu.
	bpy.types.MATERIAL_MT_specials.remove(menu_func)

	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

