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

class TogglePanelsA(bpy.types.Operator):
	bl_idname = "image.toggle_panels_a"
	bl_label = "パネル表示切り替え(モードA)"
	bl_description = "プロパティ/ツールシェルフの「両方表示」/「両方非表示」をトグルします"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (1 < toolW or 1 < uiW):
			if (1 < toolW):
				bpy.ops.image.toolshelf()
			if (1 < uiW):
				bpy.ops.image.properties()
		else:
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		return {'FINISHED'}

class TogglePanelsB(bpy.types.Operator):
	bl_idname = "image.toggle_panels_b"
	bl_label = "パネル表示切り替え(モードB)"
	bl_description = "「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」→「パネル両方表示」のトグル"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (toolW <= 1 and uiW <= 1):
			bpy.ops.image.toolshelf()
		elif (toolW <= 1 and 1 < uiW):
			bpy.ops.image.toolshelf()
		else:
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		return {'FINISHED'}

class TogglePanelsC(bpy.types.Operator):
	bl_idname = "image.toggle_panels_c"
	bl_label = "パネル表示切り替え(モードC)"
	bl_description = "「パネル両方非表示」→「ツールシェルフのみ表示」→「プロパティのみ表示」... のトグル"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		toolW = 0
		uiW = 0
		for region in context.area.regions:
			if (region.type == 'TOOLS'):
				toolW = region.width
			if (region.type == 'UI'):
				uiW = region.width
		if (toolW <= 1 and uiW <= 1):
			bpy.ops.image.toolshelf()
		elif (1 < toolW and uiW <= 1):
			bpy.ops.image.toolshelf()
			bpy.ops.image.properties()
		else:
			bpy.ops.image.properties()
		return {'FINISHED'}

################
# サブメニュー #
################

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_view_shortcuts"
	bl_label = "ショートカット登録用"
	bl_description = "ショートカットに登録すると便利かもしれない機能群です"
	
	def draw(self, context):
		self.layout.operator(TogglePanelsA.bl_idname, icon="PLUGIN")
		self.layout.operator(TogglePanelsB.bl_idname, icon="PLUGIN")
		self.layout.operator(TogglePanelsC.bl_idname, icon="PLUGIN")

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
		self.layout.separator()
		self.layout.menu(ShortcutsMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
