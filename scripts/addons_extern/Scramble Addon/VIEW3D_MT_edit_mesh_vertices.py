# 3Dビュー > メッシュ編集モード > 「Ctrl+V」キー

import bpy

################
# オペレーター #
################

class CellMenuSeparateEX(bpy.types.Operator):
	bl_idname = "mesh.cell_menu_separate_ex"
	bl_label = "別オブジェクトに分離 (拡張)"
	bl_description = "「別オブジェクトに分離」の拡張メニューを呼び出します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		bpy.ops.wm.call_menu(name=SeparateEXMenu.bl_idname)
		return {'FINISHED'}

class SeparateSelectedEX(bpy.types.Operator):
	bl_idname = "mesh.separate_selected_ex"
	bl_label = "選択物 (分離側をアクティブ)"
	bl_description = "「選択物で分離」した後に分離した側のエディトモードに入ります"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		objs = []
		for obj in context.selectable_objects:
			objs.append(obj.name)
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		for obj in context.selectable_objects:
			if (not obj.name in objs):
				obj.select = True
				context.scene.objects.active = obj
				break
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		return {'FINISHED'}

class DuplicateNewParts(bpy.types.Operator):
	bl_idname = "mesh.duplicate_new_parts"
	bl_label = "選択部を複製/新オブジェクトに"
	bl_description = "選択部分を複製・分離し新オブジェクトにしてからエディトモードに入ります"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		objs = []
		for obj in context.selectable_objects:
			objs.append(obj.name)
		bpy.ops.mesh.duplicate()
		bpy.ops.mesh.separate(type='SELECTED')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		for obj in context.selectable_objects:
			if (not obj.name in objs):
				obj.select = True
				context.scene.objects.active = obj
				break
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='SELECT')
		return {'FINISHED'}

class QuickShrinkwrap(bpy.types.Operator):
	bl_idname = "mesh.quick_shrinkwrap"
	bl_label = "クイック・シュリンクラップ"
	bl_description = "もう1つの選択メッシュに、選択頂点をぺったりとくっつけます"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('NEAREST_SURFACEPOINT', "最近接表面の点", "", 1),
		('PROJECT', "投影", "", 2),
		('NEAREST_VERTEX', "最近接頂点", "", 3),
		]
	wrap_method = bpy.props.EnumProperty(items=items, name="モード", default='PROJECT')
	offset = bpy.props.FloatProperty(name="オフセット", default=0.0, min=-10, max=10, soft_min=-10, soft_max=10, step=1, precision=5)
	
	def execute(self, context):
		if (len(context.selected_objects) != 2):
			self.report(type={"ERROR"}, message="メッシュオブジェクトを2つ選択状態で実行して下さい")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={"ERROR"}, message="メッシュオブジェクトを2つ選択状態で実行して下さい")
				return {'CANCELLED'}
		active_obj = context.active_object
		pre_mode = active_obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_obj = obj
				break
		new_vg = active_obj.vertex_groups.new(name="TempGroup")
		selected_verts = []
		for vert in active_obj.data.vertices:
			if (vert.select):
				selected_verts.append(vert.index)
		if (len(selected_verts) <= 0):
			bpy.ops.object.mode_set(mode=pre_mode)
			self.report(type={'ERROR'}, message="1つ以上は頂点を選択して実行して下さい")
			return {'CANCELLED'}
		new_vg.add(selected_verts, 1.0, 'REPLACE')
		new_mod = active_obj.modifiers.new("temp", 'SHRINKWRAP')
		for i in range(len(active_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=new_mod.name)
		new_mod.target = target_obj
		new_mod.offset = self.offset
		new_mod.vertex_group = new_vg.name
		new_mod.wrap_method = self.wrap_method
		if (self.wrap_method == 'PROJECT'):
			new_mod.use_negative_direction = True
		bpy.ops.object.modifier_apply(modifier=new_mod.name)
		active_obj.vertex_groups.remove(new_vg)
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# メニュー追加 #
################

class SeparateEXMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_edit_mesh_separate_ex"
	bl_label = "別オブジェクトに分離 (拡張)"
	bl_description = "「別オブジェクトに分離」の拡張メニューです"
	
	def draw(self, context):
		self.layout.operator("mesh.separate", text="選択物").type = 'SELECTED'
		self.layout.operator(SeparateSelectedEX.bl_idname, icon="PLUGIN")
		self.layout.operator(DuplicateNewParts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator("mesh.separate", text="マテリアルで").type = 'MATERIAL'
		self.layout.operator("mesh.separate", text="構造的に分離したパーツで").type = 'LOOSE'

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
		self.layout.operator(QuickShrinkwrap.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CellMenuSeparateEX.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(DuplicateNewParts.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
