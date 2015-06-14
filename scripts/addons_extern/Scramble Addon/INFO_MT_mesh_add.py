# 3Dビュー > オブジェクト/メッシュ編集モード > 「追加」メニュー > 「メッシュ」メニュー

import bpy
import math

################
# オペレーター #
################

class AddSphereOnlySquare(bpy.types.Operator):
	bl_idname = "mesh.add_sphere_only_square"
	bl_label = "四角ポリゴン球"
	bl_description = "四角ポリゴンのみで構成された球体メッシュを追加します"
	bl_options = {'REGISTER', 'UNDO'}
	
	level = bpy.props.IntProperty(name="分割数", default=2, step=1, min=1, max=6, soft_min=1, soft_max=6)
	radius = bpy.props.FloatProperty(name="半径(大体)", default=1.0, step=10, precision=3, min=0.001, max=100, soft_min=0.001, soft_max=100)
	view_align = bpy.props.BoolProperty(name="視点に揃える", default=False)
	location = bpy.props.FloatVectorProperty(name="位置", default=(0.0, 0.0, 0.0), step=10, precision=3, subtype='XYZ', min=-100, max=100, soft_min=-100, soft_max=100)
	rotation = bpy.props.IntVectorProperty(name="回転", default=(0, 0, 0), step=1, subtype='XYZ', min=-360, max=360, soft_min=-360, soft_max=360)
	enter_editmode = False
	
	def execute(self, context):
		isEdited = False
		if (context.mode == 'EDIT_MESH'):
			isEdited = True
			activeObj = context.active_object
		try:
			bpy.ops.object.mode_set(mode="OBJECT")
		except RuntimeError: pass
		if (self.view_align):
			bpy.ops.mesh.primitive_cube_add(radius=self.radius, view_align=True, location=self.location)
		else:
			rotation = self.rotation
			rotation = (math.radians(rotation[0]), math.radians(rotation[1]), math.radians(rotation[2]))
			bpy.ops.mesh.primitive_cube_add(radius=self.radius, location=self.location, rotation=rotation)
		context.active_object.name = "四角ポリゴン球"
		subsurf = context.active_object.modifiers.new("temp", "SUBSURF")
		subsurf.levels = self.level
		bpy.ops.object.modifier_apply(apply_as="DATA", modifier=subsurf.name)
		bpy.ops.object.mode_set(mode="EDIT")
		bpy.ops.transform.tosphere(value=1)
		bpy.ops.object.mode_set(mode="OBJECT")
		if (isEdited and False):
			activeObj.select = True
			context.scene.objects.active = activeObj
			bpy.ops.object.join()
			bpy.ops.object.mode_set(mode="EDIT")
		return {'FINISHED'}

class AddVertexOnlyObject(bpy.types.Operator):
	bl_idname = "mesh.add_vertex_only_object"
	bl_label = "頂点のみ"
	bl_description = "1頂点のみのメッシュオブジェクトを3Dカーソルの位置に追加します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		if (context.mode != 'OBJECT'):
			bpy.ops.object.mode_set(mode="OBJECT")
		me = bpy.data.meshes.new("Vertex")
		me.from_pydata([(0, 0, 0)], [], [])
		me.update()
		obj = bpy.data.objects.new("Vertex", me)
		obj.data = me
		bpy.context.scene.objects.link(obj)
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.context.scene.objects.active = obj
		obj.location = context.space_data.cursor_location[:]
		bpy.ops.object.mode_set(mode="EDIT")
		context.tool_settings.mesh_select_mode = (True, False, False)
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
		self.layout.operator(AddVertexOnlyObject.bl_idname, icon="PLUGIN")
		self.layout.operator(AddSphereOnlySquare.bl_idname, icon="PLUGIN").location = context.space_data.cursor_location
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
