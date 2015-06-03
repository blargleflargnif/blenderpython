# 情報 > 「ウィンドウ」メニュー

import bpy

################
# パイメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie"
	bl_label = "パイメニュー"
	bl_description = "ウィンドウ関係のパイメニューです"
	
	def draw(self, context):
		self.layout.operator(AreaTypePieOperator.bl_idname, icon="PLUGIN")

class AreaTypePieOperator(bpy.types.Operator):
	bl_idname = "wm.area_type_pie_operator"
	bl_label = "エディタータイプ"
	bl_description = "エディタータイプ変更のパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=AreaTypePie.bl_idname)
		return {'FINISHED'}
class AreaTypePie(bpy.types.Menu): #
	bl_idname = "INFO_MT_window_pie_area_type"
	bl_label = "エディタータイプ"
	bl_description = "エディタータイプ変更のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="テキストエディター", icon="TEXT").type = "TEXT_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="アウトライナー", icon="OOPS").type = "OUTLINER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="プロパティ", icon="BUTS").type = "PROPERTIES"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="3Dビュー", icon="MESH_CUBE").type = "VIEW_3D"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="UV/画像エディター", icon="IMAGE_COL").type = "IMAGE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ノードエディター", icon="NODETREE").type = "NODE_EDITOR"
		self.layout.menu_pie().operator("wm.call_menu_pie", text="アニメ関係", icon="ACTION").name = AreaTypePieAnim.bl_idname
		self.layout.menu_pie().operator("wm.call_menu_pie", text="その他", icon="QUESTION").name = AreaTypePieOther.bl_idname
		

class AreaTypePieAnim(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_anim"
	bl_label = "エディタータイプ(アニメーション)"
	bl_description = "エディタータイプ(アニメーション関係)変更のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="NLAエディター", icon="NLA").type = "NLA_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ドープシート", icon="ACTION").type = "DOPESHEET_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="グラフエディター", icon="IPO").type = "GRAPH_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="タイムライン", icon="TIME").type = "TIMELINE"
class AreaTypePieOther(bpy.types.Menu):
	bl_idname = "INFO_MT_window_pie_area_type_other"
	bl_label = "エディタータイプ(その他)"
	bl_description = "エディタータイプ(その他)変更のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ロジックエディター", icon="LOGIC").type = "LOGIC_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ビデオシーケンスエディター", icon="SEQUENCE").type = "SEQUENCE_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="動画クリップエディター", icon="RENDER_ANIMATION").type = "CLIP_EDITOR"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ファイルブラウザー", icon="FILESEL").type = "FILE_BROWSER"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="Pythonコンソール", icon="CONSOLE").type = "CONSOLE"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="情報", icon="INFO").type = "INFO"
		self.layout.menu_pie().operator(SetAreaType.bl_idname, text="ユーザー設定", icon="PREFERENCES").type = "USER_PREFERENCES"
class SetAreaType(bpy.types.Operator): #
	bl_idname = "wm.set_area_type"
	bl_label = "エディタータイプ変更"
	bl_description = "エディタータイプを変更します"
	bl_options = {'REGISTER'}
	
	type = bpy.props.StringProperty(name="エリアタイプ")
	
	def execute(self, context):
		context.area.type = self.type
		return {'FINISHED'}

################
# オペレーター #
################

class ToggleJapaneseInterface(bpy.types.Operator):
	bl_idname = "wm.toggle_japanese_interface"
	bl_label = "UIの英語・日本語 切り替え"
	bl_description = "インターフェイスの英語と日本語を切り替えます"
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
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
