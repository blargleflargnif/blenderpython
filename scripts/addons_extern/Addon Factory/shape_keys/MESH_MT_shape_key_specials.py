# プロパティ > 「オブジェクトデータ」タブ > シェイプキー一覧右の▼

import bpy

################
# オペレーター #
################

class CopyShape(bpy.types.Operator):
	bl_idname = "mesh.copy_shape"
	bl_label = "Duplicate shape key"
	bl_description = "I will duplicate the active shape key"
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
	bl_label = "I examine the shape block name"
	bl_description = "Displays the name of the shape block, and then copy it to the clipboard"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			shape_keys = obj.data.shape_keys
			if (shape_keys != None):
				self.report(type={"INFO"}, message="Shape key blanking drop names"+shape_keys.name+"Is ")
				context.window_manager.clipboard = shape_keys.name
			else:
				self.report(type={"ERROR"}, message="Shape key does not exist")
		else:
			self.report(type={"ERROR"}, message="Not a mesh object")
		return {'FINISHED'}

class RenameShapeBlockName(bpy.types.Operator):
	bl_idname = "mesh.rename_shape_block_name"
	bl_label = "The name of the shape block to object name"
	bl_description = "I will the name of the shape block the same as the object name"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		me.shape_keys.name = obj.name
		return {'FINISHED'}

class InsertKeyframeAllShapes(bpy.types.Operator):
	bl_idname = "mesh.insert_keyframe_all_shapes"
	bl_label = "I hit the key frames in all shapes"
	bl_description = "In the current frame, I insert the key frames of all shapes"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for shape in context.active_object.data.shape_keys.key_blocks:
			shape.keyframe_insert(data_path="value")
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SelectShapeTop(bpy.types.Operator):
	bl_idname = "object.select_shape_top"
	bl_label = "Select the top"
	bl_description = "I will select the top shape of key"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.active_object.active_shape_key_index = 0
		return {'FINISHED'}

class SelectShapeBottom(bpy.types.Operator):
	bl_idname = "object.select_shape_bottom"
	bl_label = "Select the bottom"
	bl_description = "I will select the bottom"
	
	def execute(self, context):
		context.active_object.active_shape_key_index = len(context.active_object.data.shape_keys.key_blocks) - 1
		return {'FINISHED'}

class ShapeKeyApplyRemoveAll(bpy.types.Operator):
	bl_idname = "object.shape_key_apply_remove_all"
	bl_label = "All shape delete"
	bl_description = "You can remove the whole shape key while maintaining the shape of the current mesh"
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
	for id in bpy.context.user_preferences.addons["Addon Factory"].preferences.disabled_menu.split(','):
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
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
