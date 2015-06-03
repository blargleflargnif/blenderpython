# プロパティ > 「オブジェクトデータ」タブ > シェイプキー一覧右の▼

import bpy

################
# オペレーター #
################

class CopyShape(bpy.types.Operator):
	bl_idname = "mesh.copy_shape"
	bl_label = "シェイプキーを複製"
	bl_description = "アクティブなシェイプキーを複製します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			me = obj.data
			keys = {}
			for key in me.shape_keys.key_blocks:
				keys[key.name] = key.value
				key.value = 0
			obj.active_shape_key.value = 1
			relativeKey = obj.active_shape_key.relative_key
			while relativeKey != relativeKey.relative_key:
				relativeKey.value = 1
				relativeKey = relativeKey.relative_key
			obj.shape_key_add(name=obj.active_shape_key.name, from_mix=True)
			obj.active_shape_key_index = len(me.shape_keys.key_blocks) - 1
			for k, v in keys.items():
				me.shape_keys.key_blocks[k].value = v
		return {'FINISHED'}

class ShowShapeBlockName(bpy.types.Operator):
	bl_idname = "mesh.show_shape_block_name"
	bl_label = "シェイプブロック名を調べる"
	bl_description = "シェイプブロックの名前を表示し、クリップボードにコピーします"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			shape_keys = obj.data.shape_keys
			if (shape_keys != None):
				self.report(type={"INFO"}, message="シェイプキーブロップ名は「"+shape_keys.name+"」です")
				context.window_manager.clipboard = shape_keys.name
			else:
				self.report(type={"ERROR"}, message="シェイプキーが存在しません")
		else:
			self.report(type={"ERROR"}, message="メッシュオブジェクトではありません")
		return {'FINISHED'}

class RenameShapeBlockName(bpy.types.Operator):
	bl_idname = "mesh.rename_shape_block_name"
	bl_label = "シェイプブロックの名前をオブジェクト名に"
	bl_description = "シェイプブロックの名前をオブジェクト名と同じにします"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		me.shape_keys.name = obj.name
		return {'FINISHED'}

class InsertKeyframeAllShapes(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_all_shapes"
	bl_label = "全てのシェイプにキーフレームを打つ"
	bl_description = "現在のフレームに、全てのシェイプのキーフレームを挿入します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for shape in context.active_object.data.shape_keys.key_blocks:
			shape.keyframe_insert(data_path="value")
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SelectShapeTop(bpy.types.Operator):
	bl_idname = "object.select_shape_top"
	bl_label = "最上段を選択"
	bl_description = "一番上のシェイプキーを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.active_shape_key_index = 0
		return {'FINISHED'}
class SelectShapeBottom(bpy.types.Operator):
	bl_idname = "object.select_shape_bottom"
	bl_label = "最下段を選択"
	bl_description = "一番下のシェイプキーを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.active_shape_key_index = len(context.active_object.data.shape_keys.key_blocks) - 1
		return {'FINISHED'}

class ShapeKeyApplyRemoveAll(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_remove_all"
	bl_label = "現在の形状を保持して全シェイプ削除"
	bl_description = "現在のメッシュの形状を保持しながら全シェイプキーを削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.object.shape_key_add(from_mix=True)
		bpy.ops.object.shape_key_move(type='DOWN')
		bpy.ops.object.mode_set(mode='EDIT', toggle=False)
		bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
		bpy.ops.object.shape_key_remove(all=True)
		return {'FINISHED'}

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
		column.operator(SelectShapeTop.bl_idname, icon="PLUGIN")
		column.operator(SelectShapeBottom.bl_idname, icon="PLUGIN")
		column.separator()
		column.operator(CopyShape.bl_idname, icon="PLUGIN")
		column.operator(ShapeKeyApplyRemoveAll.bl_idname, icon="PLUGIN")
		column.separator()
		column.operator(InsertKeyframeAllShapes.bl_idname, icon="PLUGIN")
		column.separator()
		column.operator(ShowShapeBlockName.bl_idname, icon="PLUGIN")
		column.operator(RenameShapeBlockName.bl_idname, icon="PLUGIN")
		if (not context.active_object.active_shape_key):
			column.enabled = False
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
