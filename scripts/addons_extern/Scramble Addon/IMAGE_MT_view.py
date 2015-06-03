# UV/画像エディター > 「ビュー」メニュー

import bpy

################
# オペレーター #
################

class Reset2DCursor(bpy.types.Operator):
	bl_idname = "image.reset_2d_cursor"
	bl_label = "カーソルの位置をリセット"
	bl_description = "2Dカーソルの位置を左下に移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("C", "中央", "", 1),
		("U", "上", "", 2),
		("RU", "右上", "", 3),
		("R", "右", "", 4),
		("RD", "右下", "", 5),
		("D", "下", "", 6),
		("LD", "左下", "", 7),
		("L", "左", "", 8),
		("LU", "左上", "", 9),
		]
	mode = bpy.props.EnumProperty(items=items, name="位置", default="LD")
	
	def execute(self, context):
		if (bpy.context.edit_image):
			x, y = bpy.context.edit_image.size
		else:
			x = 256
			y = 256
		if (self.mode == "C"):
			bpy.context.space_data.cursor_location = [x/2, y/2]
		elif (self.mode == "U"):
			bpy.context.space_data.cursor_location = [x/2, y]
		elif (self.mode == "RU"):
			bpy.context.space_data.cursor_location = [x, y]
		elif (self.mode == "R"):
			bpy.context.space_data.cursor_location = [x, y/2]
		elif (self.mode == "RD"):
			bpy.context.space_data.cursor_location = [x, 0]
		elif (self.mode == "D"):
			bpy.context.space_data.cursor_location = [x/2, 0]
		elif (self.mode == "LD"):
			bpy.context.space_data.cursor_location = [0, 0]
		elif (self.mode == "L"):
			bpy.context.space_data.cursor_location = [0, y/2]
		elif (self.mode == "LU"):
			bpy.context.space_data.cursor_location = [0, y]
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

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
		self.layout.operator(Reset2DCursor.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
