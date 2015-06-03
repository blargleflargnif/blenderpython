# 3Dビュー > オブジェクトモード > 「オブジェクト」メニュー > 「表示/隠す」メニュー

import bpy

################
# オペレーター #
################

class InvertHide(bpy.types.Operator):
	bl_idname = "object.invert_hide"
	bl_label = "表示/隠すを反転"
	bl_description = "オブジェクトの表示状態と非表示状態を反転させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		objs = []
		for obj in bpy.data.objects:
			for i in range(len(bpy.context.scene.layers)):
				if (bpy.context.scene.layers[i] and obj.layers[i]):
					for obj2 in objs:
						if (obj.name == obj2.name):
							break
					else:
						objs.append(obj)
		for obj in objs:
			obj.hide = not obj.hide
		return {'FINISHED'}

class HideOnlyType(bpy.types.Operator):
	bl_idname = "object.hide_only_mesh"
	bl_label = "特定の種類のオブジェクトのみを隠す"
	bl_description = "表示されている特定タイプのオブジェクトを隠します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "メッシュ", "", 1),
		("CURVE", "カーブ", "", 2),
		("SURFACE", "サーフェイス", "", 3),
		("META", "メタボール", "", 4),
		("FONT", "テキスト", "", 5),
		("ARMATURE", "アーマチュア", "", 6),
		("LATTICE", "ラティス", "", 7),
		("EMPTY", "エンプティ", "", 8),
		("CAMERA", "カメラ", "", 9),
		("LAMP", "ランプ", "", 10),
		("SPEAKER", "スピーカー", "", 11),
		]
	type = bpy.props.EnumProperty(items=items, name="隠すオブジェクトのタイプ")
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == self.type):
				obj.hide = True
		return {'FINISHED'}

class HideExceptType(bpy.types.Operator):
	bl_idname = "object.hide_except_mesh"
	bl_label = "特定の種類のオブジェクト以外を隠す"
	bl_description = "表示されている特定タイプのオブジェクト以外を隠します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "メッシュ", "", 1),
		("CURVE", "カーブ", "", 2),
		("SURFACE", "サーフェイス", "", 3),
		("META", "メタボール", "", 4),
		("FONT", "テキスト", "", 5),
		("ARMATURE", "アーマチュア", "", 6),
		("LATTICE", "ラティス", "", 7),
		("EMPTY", "エンプティ", "", 8),
		("CAMERA", "カメラ", "", 9),
		("LAMP", "ランプ", "", 10),
		("SPEAKER", "スピーカー", "", 11),
		]
	type = bpy.props.EnumProperty(items=items, name="残すオブジェクトのタイプ")
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type != self.type):
				obj.hide = True
		return {'FINISHED'}

class ShowLayerGroupMenu(bpy.types.Operator):
	bl_idname = "view3d.show_layer_group_menu"
	bl_label = "グループで表示/非表示を切り替え"
	bl_description = "所属しているグループで表示/非表示を切り替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu(name=LayerGroupMenu.bl_idname)
		return {'FINISHED'}
class LayerGroupMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_layer_group"
	bl_label = "グループで表示/非表示を切り替え"
	bl_description = "所属しているグループで表示/非表示を切り替えます"
	
	def draw(self, context):
		objs = []
		for obj in bpy.data.objects:
			for l1 in obj.layers:
				for l2 in context.scene.layers:
					if (l1 and l2):
						for obj2 in objs:
							if (obj.name == obj2.name):
								break
						else:
							objs.append(obj)
		groups = []
		for obj in objs:
			for group in obj.users_group:
				if (not group in groups):
					groups.append(group)
		self.layout.operator(ApplyLayerGroup.bl_idname, icon="PLUGIN", text="グループ無所属").group = ""
		self.layout.separator()
		for group in groups:
			self.layout.operator(ApplyLayerGroup.bl_idname, icon="PLUGIN", text=group.name).group = group.name
class ApplyLayerGroup(bpy.types.Operator): #
	bl_idname = "view3d.apply_layer_group"
	bl_label = "グループで表示/非表示を切り替え実行"
	bl_description = "所属しているグループで表示/非表示を切り替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	group = bpy.props.StringProperty(name="グループ名")
	
	def execute(self, context):
		for obj in bpy.data.objects:
			for l1 in obj.layers:
				for l2 in context.scene.layers:
					if (l1 and l2):
						if (self.group != ""):
							for group in obj.users_group:
								if (group.name == self.group):
									obj.hide = False
									break
							else:
								obj.hide = True
						else:
							if (len(obj.users_group) == 0):
								obj.hide = False
							else:
								obj.hide = True
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
		self.layout.operator(InvertHide.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(HideOnlyType.bl_idname, icon="PLUGIN")
		self.layout.operator(HideExceptType.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ShowLayerGroupMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
