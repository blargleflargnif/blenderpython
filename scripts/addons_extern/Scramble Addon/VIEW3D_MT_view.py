# 3Dビュー > 「ビュー」メニュー

import bpy, mathutils
import os, csv
import collections

################
# オペレーター #
################

class LocalViewEx(bpy.types.Operator):
	bl_idname = "view3d.local_view_ex"
	bl_label = "グローバルビュー/ローカルビュー(非ズーム)"
	bl_description = "選択したオブジェクトのみを表示し、視点の中央に配置します(ズームはしません)"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		pre_smooth_view = context.user_preferences.view.smooth_view
		context.user_preferences.view.smooth_view = 0
		pre_view_distance = context.region_data.view_distance
		pre_view_location = context.region_data.view_location.copy()
		pre_view_rotation = context.region_data.view_rotation.copy()
		pre_cursor_location = context.space_data.cursor_location.copy()
		bpy.ops.view3d.localview()
		context.space_data.cursor_location = pre_cursor_location
		context.region_data.view_distance = pre_view_distance
		context.region_data.view_location = pre_view_location
		context.region_data.view_rotation = pre_view_rotation
		context.user_preferences.view.smooth_view = pre_smooth_view
		#bpy.ops.view3d.view_selected_ex()
		return {'FINISHED'}

class TogglePanelsA(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_a"
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
				bpy.ops.view3d.toolshelf()
			if (1 < uiW):
				bpy.ops.view3d.properties()
		else:
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
		return {'FINISHED'}

class TogglePanelsB(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_b"
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
			bpy.ops.view3d.toolshelf()
		elif (toolW <= 1 and 1 < uiW):
			bpy.ops.view3d.toolshelf()
		else:
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
		return {'FINISHED'}

class TogglePanelsC(bpy.types.Operator):
	bl_idname = "view3d.toggle_panels_c"
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
			bpy.ops.view3d.toolshelf()
		elif (1 < toolW and uiW <= 1):
			bpy.ops.view3d.toolshelf()
			bpy.ops.view3d.properties()
		else:
			bpy.ops.view3d.properties()
		return {'FINISHED'}

class ToggleViewportShadeA(bpy.types.Operator):
	bl_idname = "view3d.toggle_viewport_shade_a"
	bl_label = "シェーディング切り替え(モードA)"
	bl_description = "シェーディングを 「ワイヤーフレーム」→「ソリッド」→「テクスチャ」... と切り替えていきます"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		if (context.space_data.viewport_shade == 'SOLID'):
			context.space_data.viewport_shade = 'TEXTURED'
		elif (context.space_data.viewport_shade == 'TEXTURED'):
			context.space_data.viewport_shade = 'WIREFRAME'
		else:
			context.space_data.viewport_shade = 'SOLID'
		return {'FINISHED'}

class SaveView(bpy.types.Operator):
	bl_idname = "view3d.save_view"
	bl_label = "視点のセーブ"
	bl_description = "現在の3Dビューの視点をセーブします"
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.StringProperty(name="視点セーブデータ名", default="視点セーブデータ")
	
	def execute(self, context):
		data = ""
		for line in context.user_preferences.addons["Scramble Addon"].preferences.view_savedata.split('|'):
			if (line == ""):
				continue
			try:
				index = line.split(':')[0]
			except ValueError:
				context.user_preferences.addons["Scramble Addon"].preferences.view_savedata = ""
				self.report(type={'ERROR'}, message="視点の読み込みに失敗しました、セーブデータをリセットします")
				return {'CANCELLED'}
			if (str(self.index) == index):
				continue
			data = data + line + '|'
		text = data + str(self.index) + ':'
		co = context.region_data.view_location
		text = text + str(co[0]) + ',' + str(co[1]) + ',' + str(co[2]) + ':'
		ro = context.region_data.view_rotation
		text = text + str(ro[0]) + ',' + str(ro[1]) + ',' + str(ro[2]) + ',' + str(ro[3]) + ':'
		text = text + str(context.region_data.view_distance) + ':'
		text = text + context.region_data.view_perspective
		context.user_preferences.addons["Scramble Addon"].preferences.view_savedata = text
		self.report(type={'INFO'}, message="現在の視点をセーブデータ"+str(self.index)+"に保存しました")
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class LoadView(bpy.types.Operator):
	bl_idname = "view3d.load_view"
	bl_label = "視点のロード"
	bl_description = "現在の3Dビューに視点をロードします"
	bl_options = {'REGISTER', 'UNDO'}
	
	index = bpy.props.StringProperty(name="視点セーブデータ名", default="視点セーブデータ")
	
	def execute(self, context):
		for line in context.user_preferences.addons["Scramble Addon"].preferences.view_savedata.split('|'):
			if (line == ""):
				continue
			try:
				index, loc, rot, distance, view_perspective = line.split(':')
			except ValueError:
				context.user_preferences.addons["Scramble Addon"].preferences.view_savedata = ""
				self.report(type={'ERROR'}, message="視点の読み込みに失敗しました、セーブデータをリセットします")
				return {'CANCELLED'}
			if (str(self.index) == index):
				for i, v in enumerate(loc.split(',')):
					context.region_data.view_location[i] = float(v)
				for i, v in enumerate(rot.split(',')):
					context.region_data.view_rotation[i] = float(v)
				context.region_data.view_distance = float(distance)
				context.region_data.view_perspective = view_perspective
				self.report(type={'INFO'}, message="視点セーブデータ"+str(self.index)+"を読み込みました")
				break
		else:
			self.report(type={'WARNING'}, message="視点のセーブデータ"+str(self.index)+"が存在しませんでした")
		return {'FINISHED'}

class DeleteViewSavedata(bpy.types.Operator):
	bl_idname = "view3d.delete_view_savedata"
	bl_label = "視点セーブデータを破棄"
	bl_description = "全ての視点セーブデータを削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.user_preferences.addons["Scramble Addon"].preferences.view_savedata = ""
		return {'FINISHED'}

################
# パイメニュー #
################

class PieMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_view_pie"
	bl_label = "パイメニュー"
	bl_description = "3Dビュー関係のパイメニューです"
	
	def draw(self, context):
		self.layout.operator(ViewNumpadPieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(ViewportShadePieOperator.bl_idname, icon="PLUGIN")
		self.layout.operator(LayerPieOperator.bl_idname, text="レイヤー", icon="PLUGIN")

class ViewNumpadPieOperator(bpy.types.Operator):
	bl_idname = "view3d.view_numpad_pie_operator"
	bl_label = "プリセットビュー"
	bl_description = "プリセットビュー(テンキー1,3,7とか)のパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewNumpadPie.bl_idname)
		return {'FINISHED'}
class ViewNumpadPie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_view_numpad"
	bl_label = "プリセットビュー"
	bl_description = "プリセットビュー(テンキー1,3,7とか)のパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator("view3d.viewnumpad", text="左", icon="TRIA_LEFT").type = "LEFT"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="右", icon="TRIA_RIGHT").type = "RIGHT"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="下", icon="TRIA_DOWN").type = "BOTTOM"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="上", icon="TRIA_UP").type = "TOP"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="後", icon="BBOX").type = "BACK"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="カメラ", icon="CAMERA_DATA").type = "CAMERA"
		self.layout.menu_pie().operator("view3d.viewnumpad", text="前", icon="SOLID").type = "FRONT"
		self.layout.menu_pie().operator("view3d.view_persportho", text="透視投影/平行投影", icon="BORDERMOVE")

class ViewportShadePieOperator(bpy.types.Operator):
	bl_idname = "view3d.viewport_shade_pie_operator"
	bl_label = "シェーディング切り替え"
	bl_description = "シェーディング切り替えパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=ViewportShadePie.bl_idname)
		return {'FINISHED'}
class ViewportShadePie(bpy.types.Menu): #
	bl_idname = "VIEW3D_MT_view_pie_viewport_shade"
	bl_label = "シェーディング切り替え"
	bl_description = "シェーディング切り替えパイメニューです"
	
	def draw(self, context):
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="バウンディングボックス", icon="BBOX").mode = "BOUNDBOX"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="レンダー", icon="SMOOTH").mode = "RENDERED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="ソリッド", icon="SOLID").mode = "SOLID"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="テクスチャ", icon="POTATO").mode = "TEXTURED"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="ワイヤーフレーム", icon="WIRE").mode = "WIREFRAME"
		self.layout.menu_pie().operator(SetViewportShade.bl_idname, text="マテリアル", icon="MATERIAL").mode = "MATERIAL"
class SetViewportShade(bpy.types.Operator): #
	bl_idname = "view3d.set_viewport_shade"
	bl_label = "シェーディング切り替え"
	bl_description = "シェーディングを切り替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	mode = bpy.props.StringProperty(name="シェーディング", default="SOLID")
	
	def execute(self, context):
		context.space_data.viewport_shade = self.mode
		return {'FINISHED'}

class LayerPieOperator(bpy.types.Operator):
	bl_idname = "view3d.layer_pie_operator"
	bl_label = "レイヤーのパイメニュー"
	bl_description = "レイヤー表示切り替えのパイメニューです"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu_pie(name=LayerPie.bl_idname)
		return {'FINISHED'}
class LayerPie(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_pie_layer"
	bl_label = "レイヤーのパイメニュー"
	bl_description = "レイヤー表示切り替えのパイメニューです"
	
	def draw(self, context):
		box = self.layout.box()
		column = box.column()
		row = column.row()
		row.label(text="切り替えるレイヤーを選択して下さい (+Shiftで追加選択 +Ctrlで半選択 +Altで半選択解除)", icon='PLUGIN')
		row = column.row()
		operator = row.operator(LayerPieRun.bl_idname, text="01", icon=self.GetIcon(0))
		operator.nr = 1
		operator = row.operator(LayerPieRun.bl_idname, text="02", icon=self.GetIcon(1))
		operator.nr = 2
		operator = row.operator(LayerPieRun.bl_idname, text="03", icon=self.GetIcon(2))
		operator.nr = 3
		operator = row.operator(LayerPieRun.bl_idname, text="04", icon=self.GetIcon(3))
		operator.nr = 4
		operator = row.operator(LayerPieRun.bl_idname, text="05", icon=self.GetIcon(4))
		operator.nr = 5
		row.separator()
		operator = row.operator(LayerPieRun.bl_idname, text="06", icon=self.GetIcon(5))
		operator.nr = 6
		operator = row.operator(LayerPieRun.bl_idname, text="07", icon=self.GetIcon(6))
		operator.nr = 7
		operator = row.operator(LayerPieRun.bl_idname, text="08", icon=self.GetIcon(7))
		operator.nr = 8
		operator = row.operator(LayerPieRun.bl_idname, text="09", icon=self.GetIcon(8))
		operator.nr = 9
		operator = row.operator(LayerPieRun.bl_idname, text="10", icon=self.GetIcon(9))
		operator.nr = 10
		row = column.row()
		operator = row.operator(LayerPieRun.bl_idname, text="11", icon=self.GetIcon(10))
		operator.nr = 11
		operator = row.operator(LayerPieRun.bl_idname, text="12", icon=self.GetIcon(11))
		operator.nr = 12
		operator = row.operator(LayerPieRun.bl_idname, text="13", icon=self.GetIcon(12))
		operator.nr = 13
		operator = row.operator(LayerPieRun.bl_idname, text="14", icon=self.GetIcon(13))
		operator.nr = 14
		operator = row.operator(LayerPieRun.bl_idname, text="15", icon=self.GetIcon(14))
		operator.nr = 15
		row.separator()
		operator = row.operator(LayerPieRun.bl_idname, text="16", icon=self.GetIcon(15))
		operator.nr = 16
		operator = row.operator(LayerPieRun.bl_idname, text="17", icon=self.GetIcon(16))
		operator.nr = 17
		operator = row.operator(LayerPieRun.bl_idname, text="18", icon=self.GetIcon(17))
		operator.nr = 18
		operator = row.operator(LayerPieRun.bl_idname, text="19", icon=self.GetIcon(18))
		operator.nr = 19
		operator = row.operator(LayerPieRun.bl_idname, text="20", icon=self.GetIcon(19))
		operator.nr = 20
	def GetIcon(self, layer):
		isIn = False
		isHalf = False
		objs = []
		for obj in bpy.data.objects:
			if (obj.layers[layer]):
				isIn = True
				objs.append(obj)
		if (objs):
			for obj in objs:
				if (obj.draw_type != 'WIRE'):
					break
			else:
				isHalf = True
		if (bpy.context.scene.layers[layer]):
			if (isHalf):
				return 'WIRE'
			if (isIn):
				return 'RADIOBUT_ON'
			return 'RADIOBUT_OFF'
		else:
			if (isHalf):
				return 'SOLID'
			if (isIn):
				return 'DOT'
			return 'BLANK1'
class LayerPieRun(bpy.types.Operator): #
	bl_idname = "view3d.layer_pie_run"
	bl_label = "レイヤーのパイメニュー"
	bl_description = "レイヤーを切り替えます (+Shiftで追加選択 +Ctrlで半選択 +Altで半選択解除)"
	bl_options = {'REGISTER', 'UNDO'}
	
	nr = bpy.props.IntProperty(name="レイヤー番号")
	extend = bpy.props.BoolProperty(name="選択拡張", default=False)
	half = bpy.props.BoolProperty(name="半選択", default=False)
	unhalf = bpy.props.BoolProperty(name="半選択解除", default=False)
	
	def execute(self, context):
		nr = self.nr - 1
		if (self.half):
			context.scene.layers[nr] = True
			for obj in context.blend_data.objects:
				if (obj.layers[nr]):
					obj.show_all_edges = True
					obj.draw_type = 'WIRE'
		elif (self.unhalf):
			context.scene.layers[nr] = True
			for obj in context.blend_data.objects:
				if (obj.layers[nr]):
					obj.draw_type = 'TEXTURED'
		elif (self.extend):
			context.scene.layers[nr] = not context.scene.layers[nr]
		else:
			context.scene.layers[nr] = not context.scene.layers[nr]
			for i in range(len(context.scene.layers)):
				if (nr != i):
					context.scene.layers[i] = False
		return {'FINISHED'}
	def invoke(self, context, event):
		if (event.ctrl):
			self.extend = False
			self.half = True
			self.unhalf = False
		elif (event.shift):
			self.extend = True
			self.half = False
			self.unhalf = False
		elif (event.alt):
			self.extend = False
			self.half = False
			self.unhalf = True
		else:
			self.extend = False
			self.half = False
			self.unhalf = False
		return self.execute(context)

################
# サブメニュー #
################

class ShortcutsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_view_shortcuts"
	bl_label = "ショートカット登録用"
	bl_description = "ショートカットに登録すると便利かもしれない機能群です"
	
	def draw(self, context):
		self.layout.operator(LocalViewEx.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(TogglePanelsA.bl_idname, icon="PLUGIN")
		self.layout.operator(TogglePanelsB.bl_idname, icon="PLUGIN")
		self.layout.operator(TogglePanelsC.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ToggleViewportShadeA.bl_idname, icon="PLUGIN")

class ViewSaveAndLoadMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_view_save_and_load"
	bl_label = "視点のセーブ/ロード"
	bl_description = "視点のセーブ/ロード操作のメニューです"
	
	def draw(self, context):
		self.layout.operator(SaveView.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteViewSavedata.bl_idname, icon="PLUGIN")
		self.layout.separator()
		for line in context.user_preferences.addons["Scramble Addon"].preferences.view_savedata.split('|'):
			if (line == ""):
				continue
			try:
				index = line.split(':')[0]
			except ValueError:
				pass
			self.layout.operator(LoadView.bl_idname, text=index+" をロード", icon="PLUGIN").index = index

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
		self.layout.menu(ViewSaveAndLoadMenu.bl_idname, icon="PLUGIN")
		self.layout.prop(context.user_preferences.view, "use_rotate_around_active", icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(ShortcutsMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(PieMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
