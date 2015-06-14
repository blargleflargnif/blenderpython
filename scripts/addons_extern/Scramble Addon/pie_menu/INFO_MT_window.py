# 情報 > 「ウィンドウ」メニュー

import bpy

################
# パイメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie"
	bl_label = "Pie menu"
	bl_description = "This is a pie menu of window relationship"
	
	def draw(self, context):
		self.layout.operator(AreaTypePieOperator.bl_idname, icon="PLUGIN")

class AreaTypePieOperator(bpy.types.Operator):
	bl_idname = "wm.area_type_pie_operator"
	bl_label = "Editor type"
	bl_description = "This is a pie menu editor type change"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=AreaTypePie.bl_idname)
		return {'FINISHED'}

class AreaTypePie(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type"
	bl_label = "エディタータイプ"
	bl_description = "エディタータイプ変更のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Text Editor", icon="TEXT").type = "TEXT_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Outliner", icon="OOPS").type = "OUTLINER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Properties", icon="BUTS").type = "PROPERTIES"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="3D View", icon="MESH_CUBE").type = "VIEW_3D"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="UV/Image Editor", icon="IMAGE_COL").type = "IMAGE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Node editor", icon="NODETREE").type = "NODE_EDITOR"
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Anime relationship", icon="ACTION").name = AreaTypePieAnim.bl_idname
		self.layout.menu_pie().operator("wm.call_menu_pie", text="Other", icon="QUESTION").name = AreaTypePieOther.bl_idname
		

class AreaTypePieAnim(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_anim"
	bl_label = "Editor type (animation)"
	bl_description = "Editor type (animation relationship) is a change pie menu of"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="NLA Editor", icon="NLA").type = "NLA_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Action Editor", icon="ACTION").type = "DOPESHEET_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Graph editor", icon="IPO").type = "GRAPH_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Timeline", icon="TIME").type = "TIMELINE"

class AreaTypePieOther(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_other"
	bl_label = "Editor type (animation)"
	bl_description = "Editor type (others) is a change pie menu of"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Logic", icon="LOGIC").type = "LOGIC_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Sequence Editor", icon="SEQUENCE").type = "SEQUENCE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Clip Editor", icon="RENDER_ANIMATION").type = "CLIP_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="File Browser", icon="FILESEL").type = "FILE_BROWSER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Python Console", icon="CONSOLE").type = "CONSOLE"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Info", icon="INFO").type = "INFO"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="User Preferences", icon="PREFERENCES").type = "USER_PREFERENCES"

class SetAreaType(bpy.types.Operator): #
	bl_idname = "wm.set_area_type"
	bl_label = "Change editor type"
	bl_description = "I will change the editor type"
	bl_options = {'REGISTER'}
	
	type = bpy.props.StringProperty(name="Area type")
	
	def execute(self, context):
		context.area.type = self.type
		return {'FINISHED'}

################
# オペレーター #
################

class ToggleJapaneseInterface(bpy.types.Operator):
	bl_idname = "wm.toggle_japanese_interface"
	bl_label = "English and Japanese switching of UI"
	bl_description = "English and Japanese switching of UI"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		if (not bpy.context.user_preferences.system.use_international_fonts):
			bpy.context.user_preferences.system.use_international_fonts = True
		if (bpy.context.user_preferences.system.language != "ja_JP"):
			bpy.context.user_preferences.system.language = "ja_JP"
		bpy.context.user_preferences.system.use_translate_interface = not bpy.context.user_preferences.system.use_translate_interface
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
		self.layout.operator(ToggleJapaneseInterface.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
