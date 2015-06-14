# プロパティ > モディファイアタブ

import bpy

################
# オペレーター #
################

class ApplyAllModifiers(bpy.types.Operator):
	bl_idname = "object.apply_all_modifiers"
	bl_label = "Apply All"
	bl_description = "Apply All modifiers to selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers[:]:
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		return {'FINISHED'}

class DeleteAllModifiers(bpy.types.Operator):
	bl_idname = "object.delete_all_modifiers"
	bl_label = "Delete All"
	bl_description = "Delete All modifiers on selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			modifiers = obj.modifiers[:]
			for modi in modifiers:
				obj.modifiers.remove(modi)
		return {'FINISHED'}

class ToggleApplyModifiersView(bpy.types.Operator):
	bl_idname = "object.toggle_apply_modifiers_view"
	bl_label = "Apply Modifier View"
	bl_description = "Show Hide Viewport Modifiers"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		is_apply = True
		for mod in context.active_object.modifiers:
			if (mod.show_viewport):
				is_apply = False
				break
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				mod.show_viewport = is_apply
		if is_apply:
			self.report(type={"INFO"}, message="ビューにモディファイアを適用しました")
		else:
			self.report(type={"INFO"}, message="ビューへのモディファイア適用を解除しました")
		return {'FINISHED'}

class SyncShowModifiers(bpy.types.Operator):
	bl_idname = "object.sync_show_modifiers"
	bl_label = "Sync View Levels"
	bl_description = "Match Modifier Render/View levels"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("1", "レンダリング → ビュー", "", 1),
		("0", "ビュー → レンダリング", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Level", default="0")
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if (int(self.mode)):
					mod.show_viewport = mod.show_render
				else:
					mod.show_render = mod.show_viewport
		return {'FINISHED'}

class ToggleAllShowExpanded(bpy.types.Operator):
	bl_idname = "wm.toggle_all_show_expanded"
	bl_label = "Expand/Collapse Modifiers"
	bl_description = "Expand/Collapse Modifiers Stack"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		obj = context.active_object
		if (len(obj.modifiers)):
			vs = 0
			for mod in obj.modifiers:
				if (mod.show_expanded):
					vs += 1
				else:
					vs -= 1
			is_close = False
			if (0 < vs):
				is_close = True
			for mod in obj.modifiers:
				mod.show_expanded = not is_close
		else:
			self.report(type={'WARNING'}, message="モディファイアが1つもありません")
			return {'CANCELLED'}
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ApplyModifiersAndJoin(bpy.types.Operator):
	bl_idname = "object.apply_modifiers_and_join"
	bl_label = "Apply & Join Objects"
	bl_description = "Apply All Modifiers to selected Objects & Join them"
	bl_options = {'REGISTER', 'UNDO'}
	
	unapply_subsurf = bpy.props.BoolProperty(name="Use Subsurf", default=True)
	unapply_armature = bpy.props.BoolProperty(name="Use Armature", default=True)
	unapply_mirror = bpy.props.BoolProperty(name="Use mirror", default=False)
	
	def execute(self, context):
		pre_active_object = context.active_object
		for obj in context.selected_objects:
			context.scene.objects.active = obj
			for mod in obj.modifiers[:]:
				if (self.unapply_subsurf and mod.type == 'SUBSURF'):
					continue
				if (self.unapply_armature and mod.type == 'ARMATURE'):
					continue
				if (self.unapply_mirror and mod.type == 'MIRROR'):
					continue
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		context.scene.objects.active = pre_active_object
		bpy.ops.object.join()
		return {'FINISHED'}

class AutoRenameModifiers(bpy.types.Operator):
	bl_idname = "object.auto_rename_modifiers"
	bl_label = "Rename Modifiers"
	bl_description = "(broken) Rename Modifier name to match Object name"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				try:
					if (mod.subtarget):
						mod.name = mod.subtarget
					continue
				except AttributeError: pass
				try:
					if (mod.target):
						mod.name = mod.target.name
					continue
				except AttributeError: pass
				try:
					if (mod.object):
						mod.name = mod.object.name
					continue
				except AttributeError: pass
				try:
					if (mod.vertex_group):
						mod.name = mod.vertex_group
					continue
				except AttributeError: pass
		return {'FINISHED'}

############################
# オペレーター(ブーリアン) #
############################

class AddBoolean(bpy.types.Operator):
	bl_idname = "object.add_boolean"
	bl_label = "Add Boolean"
	bl_description = "Add Boolean Modifier to selected object(s)"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("INTERSECT", "Intersect", "", 1),
		("UNION", "Union", "", 2),
		("DIFFERENCE", "Difference", "", 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="Mode")
	
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH" and activeObj.name != obj.name):
				modi = activeObj.modifiers.new("Boolean", "BOOLEAN")
				modi.object = obj
				modi.operation = self.mode
				obj.draw_type = "BOUNDS"
		return {'FINISHED'}

class ApplyBoolean(bpy.types.Operator):
	bl_idname = "object.apply_boolean"
	bl_label = "Apply Boolean"
	bl_description = "Apply Boolean to selected Object(s)"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("INTERSECT", "Intersect", "", 1),
		("UNION", "Union", "", 2),
		("DIFFERENCE", "Difference", "", 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="Mode")
	
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH" and activeObj.name != obj.name):
				modi = activeObj.modifiers.new("Boolean", "BOOLEAN")
				modi.object = obj
				modi.operation = self.mode
				bpy.ops.object.modifier_apply (modifier=modi.name)
				bpy.ops.object.select_all(action='DESELECT')
				obj.select = True
				bpy.ops.object.delete()
				activeObj.select = True
		return {'FINISHED'}

############################
# Subdivision Surface #
############################

class SetRenderSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.set_render_subsurf_level"
	bl_label = "Render Subsurf Level"
	bl_description = "Set the Render Level"
	bl_options = {'REGISTER', 'UNDO'}
	
	level = bpy.props.IntProperty(name="Level", default=2, min=0, max=6)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						modi.render_levels = self.level
		return {'FINISHED'}

class EqualizeSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.equalize_subsurf_level"
	bl_label = "Match View/Render Levels"
	bl_description = "Match View/Render Levels"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("ToRender", "To Render", "", 1),
		("ToPreview", "To View", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Match Levels")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						if (self.mode == "ToRender"):
							modi.render_levels = modi.levels
						else:
							modi.levels = modi.render_levels
		return {'FINISHED'}

class SetSubsurfOptimalDisplay(bpy.types.Operator):
	bl_idname = "object.set_subsurf_optimal_display"
	bl_label = "Set optimal Display"
	bl_description = "Toggle Optimal Display"
	bl_options = {'REGISTER', 'UNDO'}
	
	mode =  bpy.props.BoolProperty(name="Optimal Display")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						modi.show_only_control_edges = self.mode
		return {'FINISHED'}

class DeleteSubsurf(bpy.types.Operator):
	bl_idname = "object.delete_subsurf"
	bl_label = "Delete Subsurf"
	bl_description = "Remove Subsurf Modifier from Selected Object(s)"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						obj.modifiers.remove(modi)
		return {'FINISHED'}

class AddSubsurf(bpy.types.Operator):
	bl_idname = "object.add_subsurf"
	bl_label = "Add Subsurf"
	bl_description = "Add Subsurf to Selected Object(s)"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	subdivision_type = bpy.props.EnumProperty(items=[("CATMULL_CLARK", "Catmull-Clark", "", 1), ("SIMPLE", "Simple", "", 2)], name="Subdivision Level")
	levels = bpy.props.IntProperty(name="Levels", default=2, min=0, max=6)
	render_levels = bpy.props.IntProperty(name="Render Levels", default=2, min=0, max=6)
	use_subsurf_uv =  bpy.props.BoolProperty(name="Subdivide UV", default=True)
	show_only_control_edges =  bpy.props.BoolProperty(name="Optimal Display")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				modi = obj.modifiers.new("Subsurf", "SUBSURF")
				modi.subdivision_type = self.subdivision_type
				modi.levels = self.levels
				modi.render_levels = self.render_levels
				modi.use_subsurf_uv = self.use_subsurf_uv
				modi.show_only_control_edges = self.show_only_control_edges
		return {'FINISHED'}

##############################
# オペレーター(アーマチュア) #
##############################

class SetArmatureDeformPreserveVolume(bpy.types.Operator):
	bl_idname = "object.set_armature_deform_preserve_volume"
	bl_label = "Armature Preserve Volume"
	bl_description = "Armature Deform Preserve Volume"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_deform_preserve_volume =  bpy.props.BoolProperty(name="Preserve Volume", default=True)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				for mod in obj.modifiers:
					if (mod.type == 'ARMATURE'):
						mod.use_deform_preserve_volume = self.use_deform_preserve_volume
		return {'FINISHED'}

################
# サブメニュー #
################

class ModifierMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_modifier"
	bl_label = "Modifier Specials"
	bl_description = "Fast Modifier Tools"
	
	def draw(self, context):
		self.layout.menu(SubsurfMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(ArmatureMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(BooleanMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.separator()
		self.layout.operator(ApplyModifiersAndJoin.bl_idname, icon="PLUGIN")
		self.layout.separator()

class SubsurfMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_subsurf"
	bl_label = "Fast Subsurf"
	bl_description = "Subsurf Extras"
	
	def draw(self, context):
		self.layout.operator(AddSubsurf.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteSubsurf.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SetRenderSubsurfLevel.bl_idname, icon="PLUGIN")
		self.layout.operator(EqualizeSubsurfLevel.bl_idname, icon="PLUGIN")
		self.layout.operator(SetSubsurfOptimalDisplay.bl_idname, icon="PLUGIN")

class BooleanMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_boolean"
	bl_label = "Fast Boolean"
	bl_description = "Boolean Extras"
	
	def draw(self, context):
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Intersect").mode = "INTERSECT"
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Union").mode = "UNION"
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Difference").mode = "DIFFERENCE"
		self.layout.separator()
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Apply Intersect").mode = "INTERSECT"
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Apply Union").mode = "UNION"
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Apply Difference").mode = "DIFFERENCE"

class ArmatureMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_armature"
	bl_label = "Fast Armature"
	bl_description = "Aramature Extras"
	
	def draw(self, context):
		self.layout.operator(SetArmatureDeformPreserveVolume.bl_idname, icon="PLUGIN")

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
		if (context.active_object):
			if (len(context.active_object.modifiers)):
				row = self.layout.row(align=True)
				row.operator(AutoRenameModifiers.bl_idname, icon='SCRIPT', text="Rename All")
				row.operator(ApplyAllModifiers.bl_idname, icon='IMPORT', text="Apply All")
				row.operator(DeleteAllModifiers.bl_idname, icon='X', text="Delete All")
				row = self.layout.row(align=True)
				row.operator(ToggleApplyModifiersView.bl_idname, icon='RESTRICT_VIEW_OFF', text="View Toggle")
				row.operator(ToggleAllShowExpanded.bl_idname, icon='FULLSCREEN_ENTER', text="Expand Collapse")
				row.operator(SyncShowModifiers.bl_idname, icon='LINKED', text="Match View")
		self.layout.menu(ModifierMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
