# プロパティ > 「オブジェクトデータ」タブ > 頂点グループ一覧右の▼

import bpy
import re

################
# オペレーター #
################

class RemoveEmptyVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_empty_vertex_groups"
	bl_label = "空の頂点グループを削除"
	bl_description = "メッシュにウェイトが割り当てられていない頂点グループを削除します"
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
	bl_label = "ミラーの対になる空頂点グループを追加"
	bl_description = ".L .R などミラーの命令規則に従って付けられたボーンの対になる空の新規ボーンを追加します"
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
	bl_label = "一番上を選択"
	bl_description = "頂点グループの一番上の項目を選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.vertex_groups.active_index = 0
		return {'FINISHED'}
class SelectVertexGroupsBottom(bpy.types.Operator):
	bl_idname = "mesh.select_vertex_groups_bottom"
	bl_label = "一番下を選択"
	bl_description = "頂点グループの一番下の項目を選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.vertex_groups.active_index = len(context.active_object.vertex_groups) - 1
		return {'FINISHED'}

class MoveVertexGroupTop(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_top"
	bl_label = "最上段へ"
	bl_description = "アクティブな頂点グループを一番上へ移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for i in range(context.active_object.vertex_groups.active_index):
			bpy.ops.object.vertex_group_move(direction='UP')
		return {'FINISHED'}
class MoveVertexGroupBottom(bpy.types.Operator):
	bl_idname = "mesh.move_vertex_group_bottom"
	bl_label = "最下段へ"
	bl_description = "アクティブな頂点グループを一番下へ移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for i in range(len(context.active_object.vertex_groups) - context.active_object.vertex_groups.active_index - 1):
			bpy.ops.object.vertex_group_move(direction='DOWN')
		return {'FINISHED'}

class RemoveSpecifiedStringVertexGroups(bpy.types.Operator):
	bl_idname = "mesh.remove_specified_string_vertex_groups"
	bl_label = "特定文字列が含まれる頂点グループ削除"
	bl_description = "指定した文字列が名前に含まれている頂点グループを全て削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	string = bpy.props.StringProperty(name="削除する名前の一部", default="")
	
	def execute(self, context):
		obj = context.active_object
		count = 0
		if (obj.type == "MESH"):
			for vg in obj.vertex_groups[:]:
				if (self.string in vg.name):
					obj.vertex_groups.remove(vg)
					count += 1
			self.report(type={'INFO'}, message=str(count)+"個の頂点グループを削除しました")
		else:
			self.report(type={'ERROR'}, message="メッシュオブジェクトで実行して下さい")
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
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
