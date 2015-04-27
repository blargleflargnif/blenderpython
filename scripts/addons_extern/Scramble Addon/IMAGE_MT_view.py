# UV/画像エディター > 「ビュー」メニュー

import bpy

################
# オペレーター #
################

class Reset2DCursor(bpy.types.Operator):
	bl_idname = "image.reset_2d_cursor"
	bl_label = "Reset the position of the cursor"
	bl_description = "2D cursor moves in the lower left"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("C", "Center", "", 1),
		("U", "Vertical direction", "", 2),
		("RU", "Top Right", "", 3),
		("R", "Relative direction", "", 4),
		("RD", "右下", "", 5),
		("D", "Subscript", "", 6),
		("LD", "Bottom Left", "", 7),
		("L", "Relative direction", "", 8),
		("LU", "Padding Top", "", 9),
		]
	mode = bpy.props.EnumProperty(items=items, name="Position", default="LD")
	
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
