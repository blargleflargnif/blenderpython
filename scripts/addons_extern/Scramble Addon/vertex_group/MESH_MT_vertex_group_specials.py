# プロパティ > 「オブジェクトデータ」タブ > 頂点グループ一覧右の▼

import bpy
import re

################
# オペレーター #
################

class RemoveEmptyVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_empty_vertex_groups"
	bl_label = "Remove empty vertex group"
	bl_description = "I will delete the vertex groups that are not weight is assigned to the mesh"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			for vg in obj.vertex_groups:
				for vert in obj.data.vertices:
					try:
						if (vg.weight(vert.index) > 0.0):
							break
					except RuntimeError:
						pass
				else:
					obj.vertex_groups.remove(vg)
		return {'FINISHED'}

class AddOppositeVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.add_opposite_vertex_groups"
	bl_label = "Add an empty vertex group to become a pair of mirror"
	bl_description = ".L .R Etc. I'll add a new empty bone to become a pair of bones attached in accordance with the instruction rules of mirror"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			vgs = obj.vertex_groups[:]
			for vg in vgs:
				oldName = vg.name
				newName = re.sub(r'([_\.-])L$', r'\1R', vg.name)
				if (oldName == newName):
					newName = re.sub(r'([_\.-])R$', r'\1L', vg.name)
					if (oldName == newName):
						newName = re.sub(r'([_\.-])l$', r'\1r', vg.name)
						if (oldName == newName):
							newName = re.sub(r'([_\.-])r$', r'\1l', vg.name)
							if (oldName == newName):
								newName = re.sub(r'[lL][eE][fF][tT]$', r'Right', vg.name)
								if (oldName == newName):
									newName = re.sub(r'[rR][iI][gG][hH][tT]$', r'Left', vg.name)
									if (oldName == newName):
										newName = re.sub(r'^[lL][eE][fF][tT]', r'Right', vg.name)
										if (oldName == newName):
											newName = re.sub(r'^[rR][iI][gG][hH][tT]', r'Left', vg.name)
				for v in vgs:
					if (newName.lower() == v.name.lower()):
						break
				else:
					obj.vertex_groups.new(newName)
		return {'FINISHED'}

class SelectVertexGroupsTop(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_top"
	bl_label = "Select the top"
	bl_description = "I will select the top item of the vertex group"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.vertex_groups.active_index = 0
		return {'FINISHED'}

class SelectVertexGroupsBottom(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_bottom"
	bl_label = "Select the bottom"
	bl_description = "I choose the item at the bottom of the list of vertex group"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.vertex_groups.active_index = len(context.active_object.vertex_groups) - 1
		return {'FINISHED'}

class MoveVertexGroupTop(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_top"
	bl_label = "To the top"
	bl_description = "I will move the active vertex group to the top"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for i in range(context.active_object.vertex_groups.active_index):
			bpy.ops.object.vertex_group_move(direction='UP')
		return {'FINISHED'}

class MoveVertexGroupBottom(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_bottom"
	bl_label = "To the bottom"
	bl_description = "I will move to the bottom of the active vertex group"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for i in range(len(context.active_object.vertex_groups) - context.active_object.vertex_groups.active_index - 1):
			bpy.ops.object.vertex_group_move(direction='DOWN')
		return {'FINISHED'}

class RemoveSpecifiedStringVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_specified_string_vertex_groups"
	bl_label = "Vertex group Delete that contains specific string"
	bl_description = "Remove all the vertex groups that the specified string is included in the name"
	bl_options = {'REGISTER', 'UNDO'}
	
	string = bpy.props.StringProperty(name="Part of the name that you want to delete", default="")
	
	def execute(self, context):
		obj = context.active_object
		count = 0
		if (obj.type == "MESH"):
			for vg in obj.vertex_groups[:]:
				if (self.string in vg.name):
					obj.vertex_groups.remove(vg)
					count += 1
			self.report(type={'INFO'}, message=str(count)+"I have removed the number of vertex group")
		else:
			self.report(type={'ERROR'}, message="Please run a mesh object")
			return {'CANCELLED'}
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Scramble Addon"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		column = self.layout.column()
		column.separator()
		column.operator(SelectVertexGroupsTop.bl_idname, icon="PLUGIN")
		column.operator(SelectVertexGroupsBottom.bl_idname, icon="PLUGIN")
		column.separator()
		column.operator(MoveVertexGroupTop.bl_idname, icon="PLUGIN")
		column.operator(MoveVertexGroupBottom.bl_idname, icon="PLUGIN")
		column.separator()
		operator = column.operator('object.vertex_group_normalize_all', icon="PLUGIN")
		operator.group_select_mode = 'ALL'
		operator.lock_active = False
		operator = column.operator('object.vertex_group_clean', icon="PLUGIN")
		operator.group_select_mode = 'ALL'
		operator.limit = 0
		operator.keep_single = False
		column.separator()
		column.operator(RemoveSpecifiedStringVertexGroups.bl_idname, icon="PLUGIN")
		column.operator(RemoveEmptyVertexGroups.bl_idname, icon="PLUGIN")
		column.separator()
		column.operator(AddOppositeVertexGroups.bl_idname, icon="PLUGIN")
		if (len(context.active_object.vertex_groups) <= 0):
			column.enabled = False
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
