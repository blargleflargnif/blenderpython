# 3Dビュー > アーマチュア編集モード > 「アーマチュア」メニュー

import bpy

##############
# その他関数 #
##############

################
# オペレーター #
################

class DeleteUnmassage(bpy.types.Operator):
	bl_idname = "armature.delete_unmassage"
	bl_label = "確認無しでボーンを削除"
	bl_description = "ボーンを確認無しで削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.armature.delete()
		return {'FINISHED'}

class Move3DCursor(bpy.types.Operator):
	bl_idname = "armature.move_3d_cursor"
	bl_label = "ボーンをそのまま3Dカーソルの位置へ"
	bl_description = "相対的なボーンの尾(根本でも可)の位置をそのままに、ボーンを3Dカーソルの位置へ移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	isTail = bpy.props.BoolProperty(name="尾を移動", default=False)
	
	def execute(self, context):
		for bone in context.selected_bones:
			if (not self.isTail):
				co = bone.tail - bone.head
				bone.head = context.space_data.cursor_location
				bone.tail = context.space_data.cursor_location + co
			else:
				co = bone.head - bone.tail
				bone.head = context.space_data.cursor_location + co
				bone.tail = context.space_data.cursor_location
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
		self.layout.separator()
		self.layout.operator(DeleteUnmassage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(Move3DCursor.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
