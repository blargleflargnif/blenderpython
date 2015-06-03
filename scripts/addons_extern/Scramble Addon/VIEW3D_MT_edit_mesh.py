# 3Dビュー > メッシュ編集モード > 「メッシュ」メニュー

import bpy

################
# オペレーター #
################

class ToggleMeshSelectMode(bpy.types.Operator):
	bl_idname = "mesh.toggle_mesh_select_mode"
	bl_label = "メッシュ選択モードの切り替え"
	bl_description = "メッシュ選択モードを頂点→辺→面…と切り替えます"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		mode = context.tool_settings.mesh_select_mode
		if (mode[2]):
			context.tool_settings.mesh_select_mode = (True, False, False)
			self.report(type={"INFO"}, message="「頂点」選択モード")
		elif (mode[1]):
			context.tool_settings.mesh_select_mode = (False, False, True)
			self.report(type={"INFO"}, message="「面」選択モード")
		else:
			context.tool_settings.mesh_select_mode = (False, True, False)
			self.report(type={"INFO"}, message="「辺」選択モード")
		return {'FINISHED'}

################
# パイメニュー #
################

class SelectModePieOperator(bpy.types.Operator):
	bl_idname = "mesh.select_mode_pie_operator"
	bl_label = "メッシュ選択モード"
	bl_description = "メッシュの選択のパイメニューです"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=SelectModePie.bl_idname)
		return {'FINISHED'}
class SelectModePie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_edit_mesh_pie_select_mode"
	bl_label = "メッシュ選択モード"
	bl_description = "メッシュの選択のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator("mesh.select_mode", text="頂点", icon='VERTEXSEL').type = 'VERT'
		self.layout.menu_pie().operator("mesh.select_mode", text="面", icon='FACESEL').type = 'FACE'
		self.layout.menu_pie().operator("mesh.select_mode", text="辺", icon='EDGESEL').type = 'EDGE'

class ProportionalPieOperator(bpy.types.Operator):
	bl_idname = "mesh.proportional_pie_operator"
	bl_label = "プロポーショナル編集"
	bl_description = "プロポーショナル編集のパイメニューです"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		if (context.scene.tool_settings.proportional_edit == "DISABLED"):
			bpy.ops.wm.call_menu_pie(name=ProportionalPie.bl_idname)
		else:
			context.scene.tool_settings.proportional_edit = "DISABLED"
		return {'FINISHED'}
class ProportionalPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_edit_mesh_pie_proportional"
	bl_label = "プロポーショナル編集"
	bl_description = "プロポーショナル編集のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="有効化", icon="PROP_ON").mode = "ENABLED"
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="投影(2D)", icon="PROP_ON").mode = "PROJECTED"
		self.layout.menu_pie().operator(SetProportionalEdit.bl_idname, text="接続", icon="PROP_CON").mode = "CONNECTED"
class SetProportionalEdit(bpy.types.Operator): #
	bl_idname = "mesh.set_proportional_edit"
	bl_label = "プロポーショナル編集のモードを設定"
	bl_description = "プロポーショナル編集のモードを設定します"
	bl_options = {'REGISTER'}
	
	mode = bpy.props.StringProperty(name="モード", default="DISABLED")
	
	def execute(self, context):
		context.scene.tool_settings.proportional_edit = self.mode
		return {'FINISHED'}

################
# サブメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_pie_menu"
	bl_label = "パイメニュー"
	bl_description = "メッシュ編集に関するパイメニューです"
	
	def draw(self, context):
		self.layout.operator(SelectModePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ProportionalPieOperator.bl_idname, icon="PLUGIN")

class ShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_shortcut"
	bl_label = "ショートカット登録用"
	bl_description = "ショートカットに登録すると便利そうな機能群です"
	
	def draw(self, context):
		self.layout.operator(ToggleMeshSelectMode.bl_idname, icon="PLUGIN")

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
		self.layout.menu(ShortcutMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
