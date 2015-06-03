# 3Dビュー > オブジェクトモード > 「選択」メニュー

import bpy, mathutils
import re

################
# オペレーター #
################

class SelectBoundBoxSize(bpy.types.Operator):
	bl_idname = "object.select_bound_box_size"
	bl_label = "サイズで比較してオブジェクトを選択"
	bl_description = "最大オブジェクトに対して大きい、もしくは小さいオブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('LARGE', "大きい物を選択", "", 1),
		('SMALL', "小さい物を選択", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="選択モード")
	items = [
		('MESH', "メッシュ", "", 1),
		('CURVE', "カーブ", "", 2),
		('SURFACE', "サーフェス", "", 3),
		('META', "メタボール", "", 4),
		('FONT', "テキスト", "", 5),
		('ARMATURE', "アーマチュア", "", 6),
		('LATTICE', "ラティス", "", 7),
		('ALL', "全て", "", 8),
		]
	select_type = bpy.props.EnumProperty(items=items, name="選択タイプ", default='MESH')
	threshold = bpy.props.FloatProperty(name="選択範囲", default=50, min=0, max=100, soft_min=0, soft_max=100, step=100, precision=1, subtype='PERCENTAGE')
	
	def execute(self, context):
		context.scene.update()
		max_volume = -1
		min_volume = 999999999999999
		min_obj = None
		objs = []
		for obj in context.visible_objects:
			if (self.select_type != 'ALL'):
				if (obj.type != self.select_type):
					continue
			bound_box = obj.bound_box[:]
			bound_box0 = mathutils.Vector(bound_box[0][:])
			x = (bound_box0 - mathutils.Vector(bound_box[4][:])).length * obj.scale.x
			y = (bound_box0 - mathutils.Vector(bound_box[3][:])).length * obj.scale.y
			z = (bound_box0 - mathutils.Vector(bound_box[1][:])).length * obj.scale.z
			volume = x + y + z
			objs.append((obj, volume))
			if (max_volume < volume):
				max_volume = volume
			if (volume < min_volume):
				min_volume = volume
				min_obj = obj
		if (self.mode == 'LARGE'):
			threshold_volume = max_volume * (1.0 - (self.threshold * 0.01))
		elif (self.mode == 'SMALL'):
			threshold_volume = max_volume * (self.threshold * 0.01)
		for obj, volume in objs:
			if (self.mode == 'LARGE'):
				if (threshold_volume <= volume):
					obj.select = True
			elif (self.mode == 'SMALL'):
				if (volume <= threshold_volume):
					obj.select = True
		if (min_obj and self.mode == 'SMALL'):
			min_obj.select = True
		return {'FINISHED'}

############################
# オペレーター(関係で選択) #
############################

class SelectGroupedName(bpy.types.Operator):
	bl_idname = "object.select_grouped_name"
	bl_label = "同じ名前のオブジェクトを選択"
	bl_description = "アクティブなオブジェクトと同じ名前 (X X.001 X.002など) の可視オブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		name_base = context.active_object.name
		if (re.search(r'\.\d+$', name_base)):
			name_base = re.search(r'^(.*)\.\d+$', name_base).groups()[0]
		for obj in context.selectable_objects:
			if (re.search('^'+name_base+r'\.\d+$', obj.name) or name_base == obj.name):
				obj.select = True
		return {'FINISHED'}

class SelectGroupedMaterial(bpy.types.Operator):
	bl_idname = "object.select_grouped_material"
	bl_label = "同じマテリアル構造のオブジェクトを選択"
	bl_description = "アクティブなオブジェクトのマテリアル構造と同じ可視オブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		def GetMaterialList(slots):
			list = []
			for slot in slots:
				if (slot.material):
					list.append(slot.material.name)
			return list
		activeMats = GetMaterialList(context.active_object.material_slots)
		if (0 < len(activeMats)):
			for obj in context.selectable_objects:
				if (activeMats == GetMaterialList(obj.material_slots)):
					obj.select = True
		return {'FINISHED'}

class SelectGroupedModifiers(bpy.types.Operator):
	bl_idname = "object.select_grouped_modifiers"
	bl_label = "同じモディファイア構造のオブジェクトを選択"
	bl_description = "アクティブなオブジェクトのモディファイア構造が同じ可視オブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		def GetModifiersString(obj):
			str = ""
			for mod in obj.modifiers:
				str = str + mod.type
			return str
		active_modifiers = GetModifiersString(context.active_object)
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (GetModifiersString(obj) == active_modifiers and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.select_grouped_subsurf_level"
	bl_label = "同じサブサーフレベルのオブジェクトを選択"
	bl_description = "アクティブなオブジェクトのサブサーフレベルが同じ可視オブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		def GetSubsurfLevel(obj):
			level = 0
			for mod in obj.modifiers:
				if (mod.type == 'SUBSURF'):
					level += mod.levels
			return level
		active_subsurf_level = GetSubsurfLevel(context.active_object)
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (GetSubsurfLevel(obj) == active_subsurf_level and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedArmatureTarget(bpy.types.Operator):
	bl_idname = "object.select_grouped_armature_target"
	bl_label = "同じアーマチュアで変形しているオブジェクトを選択"
	bl_description = "アクティブなオブジェクトと同じアーマチュアで変形している可視オブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		def GetArmatureTarget(obj):
			target = []
			for mod in obj.modifiers:
				if (mod.type == 'ARMATURE'):
					if (mod.object):
						target.append(mod.object.name)
					else:
						target.append("")
			return set(target)
		active_armature_targets = GetArmatureTarget(context.active_object)
		if (len(active_armature_targets) == 0):
			self.report(type={"ERROR"}, message="アクティブオブジェクトにアーマチュアモディファイアがありません")
			return {"CANCELLED"}
		active_type = context.active_object.type
		for obj in context.selectable_objects:
			if (len(GetArmatureTarget(obj).intersection(active_armature_targets)) == len(active_armature_targets) and active_type == obj.type):
				obj.select= True
		return {'FINISHED'}

class SelectGroupedSizeThan(bpy.types.Operator):
	bl_idname = "object.select_grouped_size_than"
	bl_label = "サイズで比較してオブジェクトを選択"
	bl_description = "アクティブオブジェクトより大きい、もしくは小さいオブジェクトを追加選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('LARGER', "より大きい物を選択", "", 1),
		('SMALLER', "より小さい物を選択", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="選択モード")
	select_same_size = bpy.props.BoolProperty(name="同じサイズも選択", default=True)
	items = [
		('MESH', "メッシュ", "", 1),
		('CURVE', "カーブ", "", 2),
		('SURFACE', "サーフェス", "", 3),
		('META', "メタボール", "", 4),
		('FONT', "テキスト", "", 5),
		('ARMATURE', "アーマチュア", "", 6),
		('LATTICE', "ラティス", "", 7),
		('ALL', "全て", "", 8),
		('SAME', "同じタイプ", "", 9),
		]
	select_type = bpy.props.EnumProperty(items=items, name="選択タイプ", default='SAME')
	size_multi = bpy.props.FloatProperty(name="基準サイズ オフセット", default=1.0, min=0, max=10, soft_min=0, soft_max=10, step=10, precision=3)
	
	def execute(self, context):
		def GetSize(obj):
			bound_box = obj.bound_box[:]
			bound_box0 = mathutils.Vector(bound_box[0][:])
			bound_box0 = mathutils.Vector(bound_box[0][:])
			x = (bound_box0 - mathutils.Vector(bound_box[4][:])).length * obj.scale.x
			y = (bound_box0 - mathutils.Vector(bound_box[3][:])).length * obj.scale.y
			z = (bound_box0 - mathutils.Vector(bound_box[1][:])).length * obj.scale.z
			return x + y + z
		
		active_obj = context.active_object
		if (not active_obj):
			self.report(type={'ERROR'}, message="アクティブオブジェクトがありません")
			return {'CANCELLED'}
		context.scene.update()
		active_obj_size = GetSize(active_obj) * self.size_multi
		for obj in context.selectable_objects:
			if (self.select_type != 'ALL'):
				if (self.select_type == 'SAME'):
					if (obj.type != active_obj.type):
						continue
				else:
					if (obj.type != self.select_type):
						continue
			size = GetSize(obj)
			if (self.mode == 'LARGER'):
				if (active_obj_size < size):
					obj.select = True
			elif (self.mode == 'SMALLER'):
				if (size < active_obj_size):
					obj.select = True
			if (self.select_same_size):
				if (active_obj_size == size):
					obj.select = True
		return {'FINISHED'}

##########################
# オペレーター(メッシュ) #
##########################

class SelectMeshFaceOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_face_only"
	bl_label = "面のあるメッシュを選択"
	bl_description = "面が1つ以上あるメッシュを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (0 < len(me.polygons)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshEdgeOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_edge_only"
	bl_label = "辺のみのメッシュを選択"
	bl_description = "面が無く、辺のみのメッシュを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and 0 < len(me.edges)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshVertexOnly(bpy.types.Operator):
	bl_idname = "object.select_mesh_vertex_only"
	bl_label = "頂点のみのメッシュを選択"
	bl_description = "面と辺が無く、頂点のみのメッシュを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and 0 < len(me.vertices)):
					obj.select = True
		return {'FINISHED'}

class SelectMeshNone(bpy.types.Operator):
	bl_idname = "object.select_mesh_none"
	bl_label = "頂点すら無いメッシュを選択"
	bl_description = "面と辺と頂点が無い空のメッシュオブジェクトを選択します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selectable_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				if (len(me.polygons) == 0 and len(me.edges) == 0 and len(me.vertices) == 0):
					obj.select = True
		return {'FINISHED'}

################
# サブメニュー #
################

class SelectGroupedEX(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_grouped_ex"
	bl_label = "関係で選択 (拡張)"
	bl_description = "プロパティによってグループ化されたすべての可視オブジェクトを選択します"
	
	def draw(self, context):
		self.layout.operator("object.select_grouped", text="子").type = 'CHILDREN_RECURSIVE'
		self.layout.operator("object.select_grouped", text="直接の子").type = 'CHILDREN'
		self.layout.operator("object.select_grouped", text="親").type = 'PARENT'
		self.layout.operator("object.select_grouped", text="兄弟").type = 'SIBLINGS'
		self.layout.operator("object.select_grouped", text="タイプ").type = 'TYPE'
		self.layout.operator("object.select_grouped", text="レイヤー").type = 'LAYER'
		self.layout.operator("object.select_grouped", text="グループ").type = 'GROUP'
		self.layout.operator("object.select_grouped", text="パス").type = 'PASS'
		self.layout.operator("object.select_grouped", text="カラー").type = 'COLOR'
		self.layout.operator("object.select_grouped", text="プロパティ").type = 'PROPERTIES'
		self.layout.operator("object.select_grouped", text="キーイングセット").type = 'KEYINGSET'
		self.layout.operator("object.select_grouped", text="ランプタイプ").type = 'LAMP_TYPE'
		self.layout.separator()
		self.layout.operator(SelectGroupedSizeThan.bl_idname, text="より大きい", icon="PLUGIN").mode = 'LARGER'
		self.layout.operator(SelectGroupedSizeThan.bl_idname, text="より小さい", icon="PLUGIN").mode = 'SMALLER'
		self.layout.separator()
		self.layout.operator(SelectGroupedName.bl_idname, text="オブジェクト名", icon="PLUGIN")
		self.layout.operator(SelectGroupedMaterial.bl_idname, text="マテリアル", icon="PLUGIN")
		self.layout.operator(SelectGroupedModifiers.bl_idname, text="モディファイア", icon="PLUGIN")
		self.layout.operator(SelectGroupedSubsurfLevel.bl_idname, text="サブサーフレベル", icon="PLUGIN")
		self.layout.operator(SelectGroupedArmatureTarget.bl_idname, text="同アーマチュア変形", icon="PLUGIN")

class SelectMesh(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_select_object_mesh"
	bl_label = "メッシュの特徴で選択"
	bl_description = "可視メッシュオブジェクトを選択する機能のメニューです"
	
	def draw(self, context):
		self.layout.operator(SelectMeshFaceOnly.bl_idname, text="面あり", icon="PLUGIN")
		self.layout.operator(SelectMeshEdgeOnly.bl_idname, text="辺のみ", icon="PLUGIN")
		self.layout.operator(SelectMeshVertexOnly.bl_idname, text="頂点のみ", icon="PLUGIN")
		self.layout.operator(SelectMeshNone.bl_idname, text="頂点すら無し", icon="PLUGIN")

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
		self.layout.operator(SelectBoundBoxSize.bl_idname, text="小さなものを選択", icon="PLUGIN").mode = 'SMALL'
		self.layout.operator(SelectBoundBoxSize.bl_idname, text="大きなものを選択", icon="PLUGIN").mode = 'LARGE'
		self.layout.separator()
		self.layout.menu(SelectMesh.bl_idname, icon="PLUGIN")
		self.layout.menu(SelectGroupedEX.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
