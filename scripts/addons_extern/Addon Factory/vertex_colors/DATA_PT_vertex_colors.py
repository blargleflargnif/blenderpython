# プロパティ > "メッシュデータ"タブ > "頂点色"パネル

import bpy

################
# オペレーター #
################

class MoveActiveVertexColor(bpy.types.Operator):
	bl_idname = "object.move_active_vertex_color"
	bl_label = "頂点色を移動"
	bl_description = "アクティブなオブジェクトの頂点色を移動して並び替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('UP', "上へ", "", 1),
		('DOWN', "下へ", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="方向", default="UP")
	
	def execute(self, context):
		obj = context.active_object
		if (not obj):
			self.report(type={'ERROR'}, message="アクティブオブジェクトがありません")
			return {'CANCELLED'}
		if (obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="これはメッシュオブジェクトではありません")
			return {'CANCELLED'}
		me = obj.data
		if (len(me.vertex_colors) <= 1):
			self.report(type={'ERROR'}, message="頂点色数が1つ以下です")
			return {'CANCELLED'}
		if (self.mode == 'UP'):
			if (me.vertex_colors.active_index <= 0):
				return {'CANCELLED'}
			target_index = me.vertex_colors.active_index - 1
		elif (self.mode == 'DOWN'):
			target_index = me.vertex_colors.active_index + 1
			if (len(me.vertex_colors) <= target_index):
				return {'CANCELLED'}
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		vertex_color = me.vertex_colors.active
		vertex_color_target = me.vertex_colors[target_index]
		for data_name in dir(vertex_color):
			if (data_name[0] != '_' and data_name != 'bl_rna' and data_name != 'rna_type' and data_name != 'data'):
				temp = vertex_color.__getattribute__(data_name)
				temp_target = vertex_color_target.__getattribute__(data_name)
				vertex_color.__setattr__(data_name, temp_target)
				vertex_color_target.__setattr__(data_name, temp)
				vertex_color.__setattr__(data_name, temp_target)
				vertex_color_target.__setattr__(data_name, temp)
		for i in range(len(vertex_color.data)):
			temp = vertex_color.data[i].color[:]
			vertex_color.data[i].color = vertex_color_target.data[i].color[:]
			vertex_color_target.data[i].color = temp[:]
		me.vertex_colors.active_index = target_index
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class VertexColorSet(bpy.types.Operator):
	bl_idname = "object.vertex_color_set"
	bl_label = "頂点色を塗り潰す"
	bl_description = "アクティブなオブジェクトの頂点色を指定色で塗り潰します"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="頂点色", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=3, precision=10, subtype='COLOR')
	
	def invoke(self, context, event):
		obj = context.active_object
		if (not obj):
			self.report(type={'ERROR'}, message="アクティブオブジェクトがありません")
			return {'CANCELLED'}
		if (obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="これはメッシュオブジェクトではありません")
			return {'CANCELLED'}
		me = obj.data
		active_col = me.vertex_colors.active
		if (not active_col):
			self.report(type={'ERROR'}, message="頂点色が存在しません")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		obj = context.active_object
		pre_mode = obj.mode
		bpy.ops.object.mode_set(mode='OBJECT')
		me = obj.data
		active_col = me.vertex_colors.active
		for data in active_col.data:
			data.color = self.color[:]
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################
# メニュー追加 #
################

# メニューのオン/オフの判定
def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["Addon Factory"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True

# メニューを登録する関数
def menu(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		if (context.active_object.type == 'MESH'):
			if (context.active_object.data.vertex_colors.active):
				row = self.layout.row()
				sub = row.row(align=True)
				sub.operator(MoveActiveVertexColor.bl_idname, icon='TRIA_UP', text="").mode = 'UP'
				sub.operator(MoveActiveVertexColor.bl_idname, icon='TRIA_DOWN', text="").mode = 'DOWN'
				row.operator(VertexColorSet.bl_idname, icon="PLUGIN", text="塗り潰す")
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
