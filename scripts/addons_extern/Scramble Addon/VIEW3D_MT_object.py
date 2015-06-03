# 3Dビュー > オブジェクトモード > 「オブジェクト」メニュー

import bpy, bmesh

################
# パイメニュー #
################

class CopyPieOperator(bpy.types.Operator):
	bl_idname = "object.copy_pie_operator"
	bl_label = "コピー"
	bl_description = "オブジェクトに関するコピーのパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=CopyPie.bl_idname)
		return {'FINISHED'}
class CopyPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_copy"
	bl_label = "コピー"
	bl_description = "オブジェクトに関するコピーのパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator("view3d.copybuffer", icon="COPY_ID")
		self.layout.menu_pie().operator(CopyObjectName.bl_idname, icon="MONKEY")

class ObjectModePieOperator(bpy.types.Operator):
	bl_idname = "object.object_mode_pie_operator"
	bl_label = "オブジェクト対話モード"
	bl_description = "オブジェクト対話モードのパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ObjectModePie.bl_idname)
		return {'FINISHED'}
class ObjectModePie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_object_mode"
	bl_label = "オブジェクト対話モード"
	bl_description = "オブジェクト対話モードのパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="ポーズ", icon="POSE_HLT").mode = "POSE"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="スカルプト", icon="SCULPTMODE_HLT").mode = "SCULPT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="ウェイトペイント", icon="WPAINT_HLT").mode = "WEIGHT_PAINT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="オブジェクト", icon="OBJECT_DATAMODE").mode = "OBJECT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="パーティクル編集", icon="PARTICLEMODE").mode = "PARTICLE_EDIT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="編集", icon="EDITMODE_HLT").mode = "EDIT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="テクスチャペイント", icon="TPAINT_HLT").mode = "TEXTURE_PAINT"
		self.layout.menu_pie().operator(SetObjectMode.bl_idname, text="頂点ペイント", icon="VPAINT_HLT").mode = "VERTEX_PAINT"
class SetObjectMode(bpy.types.Operator): #
	bl_idname = "object.set_object_mode"
	bl_label = "オブジェクト対話モードを設定"
	bl_description = "オブジェクトの対話モードを設定します"
	bl_options = {'REGISTER'}
	
	mode = bpy.props.StringProperty(name="対話モード", default="OBJECT")
	
	def execute(self, context):
		if (context.active_object):
			try:
				bpy.ops.object.mode_set(mode=self.mode)
			except TypeError:
				self.report(type={"WARNING"}, message=context.active_object.name+" はその対話モードに入る事が出来ません")
		else:
			self.report(type={"WARNING"}, message="アクティブなオブジェクトがありません")
		return {'FINISHED'}

class SubdivisionSetPieOperator(bpy.types.Operator):
	bl_idname = "object.subdivision_set_pie_operator"
	bl_label = "サブサーフ設定"
	bl_description = "サブサーフのレベルを設定するパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=SubdivisionSetPie.bl_idname)
		return {'FINISHED'}
class SubdivisionSetPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_subdivision_set"
	bl_label = "サブサーフ設定"
	bl_description = "サブサーフのレベルを設定するパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:2", icon="MOD_SUBSURF").level = 2
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:6", icon="MOD_SUBSURF").level = 6
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:0", icon="MOD_SUBSURF").level = 0
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:4", icon="MOD_SUBSURF").level = 4
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:3", icon="MOD_SUBSURF").level = 3
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:5", icon="MOD_SUBSURF").level = 5
		self.layout.menu_pie().operator("object.subdivision_set", text="レベル:1", icon="MOD_SUBSURF").level = 1

class DrawTypePieOperator(bpy.types.Operator):
	bl_idname = "object.draw_type_pie_operator"
	bl_label = "最高描画タイプ"
	bl_description = "最高描画タイプを設定するパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=DrawTypePie.bl_idname)
		return {'FINISHED'}
class DrawTypePie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_draw_type"
	bl_label = "最高描画タイプ"
	bl_description = "最高描画タイプを設定するパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="バウンド", icon="BBOX").type = "BOUNDS"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="ワイヤーフレーム", icon="WIRE").type = "WIRE"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="ソリッド", icon="SOLID").type = "SOLID"
		self.layout.menu_pie().operator(SetDrawType.bl_idname, text="テクスチャ", icon="POTATO").type = "TEXTURED"
class SetDrawType(bpy.types.Operator): #
	bl_idname = "object.set_draw_type"
	bl_label = "最高描画タイプ設定"
	bl_description = "最高描画タイプを設定します"
	bl_options = {'REGISTER'}
	
	type = bpy.props.StringProperty(name="描画タイプ", default="OBJECT")
	
	def execute(self, context):
		for obj in context.selected_objects:
			obj.draw_type = self.type
		return {'FINISHED'}

################
# オペレーター #
################

class DeleteUnmassage(bpy.types.Operator):
	bl_idname = "object.delete_unmassage"
	bl_label = "確認せずに削除"
	bl_description = "削除する時の確認メッセージを表示せずにオブジェクトを削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_global = bpy.props.BoolProperty(name="全体的に削除", default=False)
	
	def execute(self, context):
		if (context.active_object):
			self.report(type={"INFO"}, message=context.active_object.name+"などを削除しました")
		bpy.ops.object.delete(use_global=self.use_global)
		return {'FINISHED'}

################
# サブメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_menu"
	bl_label = "パイメニュー"
	bl_description = "オブジェクト操作に関するパイメニューです"
	
	def draw(self, context):
		self.layout.operator(CopyPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ObjectModePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(SubdivisionSetPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(DrawTypePieOperator.bl_idname, icon="PLUGIN")

class ShortcutMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_shortcut"
	bl_label = "ショートカット登録用"
	bl_description = "ショートカットに登録すると便利そうな機能群です"
	
	def draw(self, context):
		self.layout.operator(DeleteUnmassage.bl_idname, icon="PLUGIN")
		self.layout.operator(ApplyModifiersAndJoin.bl_idname, icon="PLUGIN")

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
