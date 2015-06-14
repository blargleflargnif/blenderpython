# 3Dビュー > メッシュ編集モード > 「メッシュ」メニュー > 「表示/隠す」メニュー

import bpy

################
# オペレーター #
################

class InvertHide(bpy.types.Operator):
	bl_idname = "mesh.invert_hide"
	bl_label = "The inverted Show / Hide"
	bl_description = "To reverse the display state and a non-display state"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			bpy.ops.object.mode_set(mode="OBJECT")
			me = obj.data
			for v in me.vertices:
				v.hide = not v.hide
			for e in me.edges:
				for i in e.vertices:
					if (me.vertices[i].hide == True):
						e.hide = True
						break
				else:
					e.hide = False
			for f in me.polygons:
				for i in f.vertices:
					if (me.vertices[i].hide == True):
						f.hide = True
						break
				else:
					f.hide = False
			bpy.ops.object.mode_set(mode="EDIT")
		else:
			self.report(type={"ERROR"}, message="Please execute mesh object is in an active state")
		return {'FINISHED'}

class HideVertexOnly(bpy.types.Operator):
	bl_idname = "mesh.hide_vertex_only"
	bl_label = "I hide the vertex only"
	bl_description = "To secure and hide the only vertex of selected state"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			bpy.ops.object.mode_set(mode="OBJECT")
			me = obj.data
			for vert in me.vertices:
				if (vert.select):
					vert.hide = True
			bpy.ops.object.mode_set(mode="EDIT")
		else:
			self.report(type={"ERROR"}, message="Please execute mesh object is in an active state")
		return {'FINISHED'}

class HideParts(bpy.types.Operator):
	bl_idname = "mesh.hide_parts"
	bl_label = "Hide parts that are selected"
	bl_description = "I will hide the mesh parts you have selected more than one vertex"
	bl_options = {'REGISTER', 'UNDO'}
	
	unselected = bpy.props.BoolProperty(name="Non-selection unit", default=False)
	
	def execute(self, context):
		isSelecteds = []
		for vert in context.active_object.data.vertices:
			isSelecteds.append(vert.select)
		bpy.ops.mesh.select_linked(limit=False)
		bpy.ops.mesh.hide(unselected=self.unselected)
		bpy.ops.mesh.select_all(action='DESELECT')
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
		self.layout.operator(HideParts.bl_idname, icon="PLUGIN", text="Hide parts that are selected").unselected = False
		self.layout.operator(HideParts.bl_idname, icon="PLUGIN", text="Hide the parts you do not select").unselected = True
		self.layout.separator()
		self.layout.operator(InvertHide.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(HideVertexOnly.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
