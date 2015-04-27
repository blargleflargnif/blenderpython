# 3Dビュー > ウェイトペイントモード > 「ウェイト」メニュー

import bpy

################
# オペレーター #
################

class MargeSelectedVertexGroup(bpy.types.Operator):
	bl_idname = "paint.marge_selected_vertex_group"
	bl_label = "Synthesis of weight between"
	bl_description = "I will synthesize the weight of the same vertex group as the bone of the selected"
	bl_options = {'REGISTER', 'UNDO'}
	
	isNewVertGroup = bpy.props.BoolProperty(name="New vertex group created", default=False)
	ext = bpy.props.StringProperty(name="The end of the new vertex group name", default="Synthesis of ... etc.")
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		if (self.isNewVertGroup):
			newVg = obj.vertex_groups.new(name=context.active_pose_bone.name+self.ext)
		else:
			newVg = obj.vertex_groups[context.active_pose_bone.name]
		boneNames = []
		if (not context.selected_pose_bones or len(context.selected_pose_bones) < 2):
			self.report(type={"ERROR"}, message="Run to select the bone two or more")
			return {"CANCELLED"}
		for bone in context.selected_pose_bones:
			boneNames.append(bone.name)
		for vert in me.vertices:
			for vg in vert.groups:
				if (self.isNewVertGroup or newVg.name != obj.vertex_groups[vg.group].name):
					if (obj.vertex_groups[vg.group].name in boneNames):
						newVg.add([vert.index], vg.weight, 'ADD')
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		obj.vertex_groups.active_index = newVg.index
		return {'FINISHED'}

class RemoveSelectedVertexGroup(bpy.types.Operator):
	bl_idname = "paint.remove_selected_vertex_group"
	bl_label = "Subtraction of weight between"
	bl_description = "I subtract the weight of the same vertex group as the bone of the selected"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		obj = context.active_object
		me = obj.data
		newVg = obj.vertex_groups[context.active_pose_bone.name]
		boneNames = []
		if (not context.selected_pose_bones or len(context.selected_pose_bones) < 2):
			self.report(type={"ERROR"}, message="Run to select the bone two or more")
			return {"CANCELLED"}
		for bone in context.selected_pose_bones:
			boneNames.append(bone.name)
		for vert in me.vertices:
			for vg in vert.groups:
				if (newVg.name != obj.vertex_groups[vg.group].name):
					if (obj.vertex_groups[vg.group].name in boneNames):
						newVg.add([vert.index], vg.weight, 'SUBTRACT')
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
		return {'FINISHED'}

class VertexGroupAverageAll(bpy.types.Operator):
	bl_idname = "mesh.vertex_group_average_all"
	bl_label = "I fill in the average weight of all vertices"
	bl_description = "The average of all of the weight, I will fill all the vertices"
	bl_options = {'REGISTER', 'UNDO'}
	
	strength = bpy.props.FloatProperty(name="Strength", default=1, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
	def execute(self, context):
		pre_mode = context.mode
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				vgs = []
				for i in range(len(obj.vertex_groups)):
					vgs.append([])
				vertCount = 0
				for vert in obj.data.vertices:
					for vg in vert.groups:
						vgs[vg.group].append(vg.weight)
					vertCount += 1
				vg_average = []
				for vg in vgs:
					vg_average.append(0)
					for w in vg:
						vg_average[-1] += w
					vg_average[-1] /= vertCount
				i = 0
				for vg in obj.vertex_groups:
					for vert in obj.data.vertices:
						for g in vert.groups:
							if (obj.vertex_groups[g.group] == vg):
								w = g.weight
								break
						else:
							w = 0
						w = (vg_average[i] * self.strength) + (w * (1-self.strength))
						vg.add([vert.index], w, "REPLACE")
					i += 1
		bpy.ops.object.mode_set(mode="OBJECT")
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class ApplyDynamicPaint(bpy.types.Operator):
	bl_idname = "mesh.apply_dynamic_paint"
	bl_label = "I paint the part objects are overlapped"
	bl_description = "I will paint the weight of the portion that overlaps with other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	isNew = bpy.props.BoolProperty(name="The new vertex group", default=False)
	distance = bpy.props.FloatProperty(name="Distance", default=1.0, min=0, max=100, soft_min=0, soft_max=100, step=10, precision=3)
	items = [
		("ADD", "Add", "", 1),
		("SUBTRACT", "Subtract", "", 2),
		("REPLACE", "Replace", "", 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="How to fill")
	
	def execute(self, context):
		activeObj = context.active_object
		preActiveVg = activeObj.vertex_groups.active
		isNew = self.isNew
		if (not preActiveVg):
			isNew = True
		brushObjs = []
		for obj in context.selected_objects:
			if (activeObj.name != obj.name):
				brushObjs.append(obj)
		bpy.ops.object.mode_set(mode="OBJECT")
		for obj in brushObjs:
			context.scene.objects.active = obj
			bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
			obj.modifiers[-1].ui_type = 'BRUSH'
			bpy.ops.dpaint.type_toggle(type='BRUSH')
			obj.modifiers[-1].brush_settings.paint_source = 'VOLUME_DISTANCE'
			obj.modifiers[-1].brush_settings.paint_distance = self.distance
		context.scene.objects.active = activeObj
		bpy.ops.object.modifier_add(type='DYNAMIC_PAINT')
		bpy.ops.dpaint.type_toggle(type='CANVAS')
		activeObj.modifiers[-1].canvas_settings.canvas_surfaces[-1].surface_type = 'WEIGHT'
		bpy.ops.dpaint.output_toggle(output='A')
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier=activeObj.modifiers[-1].name)
		dpVg = activeObj.vertex_groups[-1]
		if (not isNew):
			me = activeObj.data
			for vert in me.vertices:
				for vg in vert.groups:
					if (activeObj.vertex_groups[vg.group].name == dpVg.name):
						preActiveVg.add([vert.index], vg.weight, self.mode)
						break
			activeObj.vertex_groups.remove(dpVg)
			activeObj.vertex_groups.active_index = preActiveVg.index
		bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
		for obj in brushObjs:
			obj.modifiers.remove(obj.modifiers[-1])
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
		self.layout.operator(MargeSelectedVertexGroup.bl_idname, icon="PLUGIN")
		self.layout.operator(RemoveSelectedVertexGroup.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(VertexGroupAverageAll.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ApplyDynamicPaint.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
