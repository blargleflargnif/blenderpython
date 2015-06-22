# 3Dビュー > オブジェクトモード > 「Ctrl+L」キー

import bpy, bmesh

################
# オペレーター #
################

class MakeLinkObjectName(bpy.types.Operator):
	bl_idname = "object.make_link_object_name"
	bl_label = "The object name is the same"
	bl_description = "I will link the name of the active object to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		name = context.active_object.name
		for obj in context.selected_objects:
			if (obj.name != name):
				obj.name = "temp"
				obj.name = name
		bpy.context.active_object.name = name
		return {'FINISHED'}

class MakeLinkLayer(bpy.types.Operator):
	bl_idname = "object.make_link_layer"
	bl_label = "The layer to the same"
	bl_description = "I will link the layers of active objects to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.name != context.active_object.name):
				obj.layers = context.active_object.layers
		return {'FINISHED'}

class MakeLinkDisplaySetting(bpy.types.Operator):
	bl_idname = "object.make_link_display_setting"
	bl_label = "The display settings of objects to the same"
	bl_description = "I will copy the settings of the display panel of the active object to other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	isSameType = bpy.props.BoolProperty(name="The same type of object only", default=True)
	show_name = bpy.props.BoolProperty(name="Given names", default=True)
	show_axis = bpy.props.BoolProperty(name="Coordinate axes", default=True)
	show_wire = bpy.props.BoolProperty(name="Wire frame", default=True)
	show_all_edges = bpy.props.BoolProperty(name="View all sides", default=True)
	show_bounds = bpy.props.BoolProperty(name="Bound", default=True)
	show_texture_space = bpy.props.BoolProperty(name="Texture space", default=True)
	show_x_ray = bpy.props.BoolProperty(name="X-ray", default=True)
	show_transparent = bpy.props.BoolProperty(name="Transmission", default=True)
	draw_bounds_type = bpy.props.BoolProperty(name="Bound type of", default=True)
	draw_type = bpy.props.BoolProperty(name="Best drawing type", default=True)
	color = bpy.props.BoolProperty(name="Object color", default=True)
	
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (not self.isSameType or activeObj.type == obj.type):
				if (obj.name != activeObj.name):
					if (self.show_name):
						obj.show_name = activeObj.show_name
					if (self.show_axis):
						obj.show_axis = activeObj.show_axis
					if (self.show_wire):
						obj.show_wire = activeObj.show_wire
					if (self.show_all_edges):
						obj.show_all_edges = activeObj.show_all_edges
					if (self.show_bounds):
						obj.show_bounds = activeObj.show_bounds
					if (self.show_texture_space):
						obj.show_texture_space = activeObj.show_texture_space
					if (self.show_x_ray):
						obj.show_x_ray = activeObj.show_x_ray
					if (self.show_transparent):
						obj.show_transparent = activeObj.show_transparent
					if (self.draw_bounds_type):
						obj.draw_bounds_type = activeObj.draw_bounds_type
					if (self.draw_type):
						obj.draw_type = activeObj.draw_type
					if (self.color):
						obj.color = activeObj.color
		return {'FINISHED'}

class MakeLinkUVNames(bpy.types.Operator):
	bl_idname = "object.make_link_uv_names"
	bl_label = "Link an empty UV map"
	bl_description = "Add in the UV of the active object in the sky to the other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		active_obj = context.active_object
		if (active_obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="Active object must be mesh")
			return {'CANCELLED'}
		target_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH' and active_obj.name != obj.name):
				target_objs.append(obj)
		if (len(target_objs) <= 0):
			self.report(type={'ERROR'}, message="There is no mesh object to be linked")
			return {'CANCELLED'}
		for obj in target_objs:
			for uv in active_obj.data.uv_layers:
				obj.data.uv_textures.new(uv.name)
		return {'FINISHED'}

class MakeLinkArmaturePose(bpy.types.Operator):
	bl_idname = "object.make_link_armature_pose"
	bl_label = "Link the movement of the armature"
	bl_description = "By constraint, and to imitate the movement of the active armature to other selection armature"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		active_obj = context.active_object
		if (active_obj.type != 'ARMATURE'):
			self.report(type={'ERROR'}, message="Active object must be the armature")
			return {'CANCELLED'}
		target_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'ARMATURE' and active_obj.name != obj.name):
				target_objs.append(obj)
		if (len(target_objs) <= 0):
			self.report(type={'ERROR'}, message="There is no armature object to be imitated")
			return {'CANCELLED'}
		for obj in target_objs:
			for bone in active_obj.pose.bones:
				try:
					target_bone = obj.pose.bones[bone.name]
				except KeyError:
					continue
				consts = target_bone.constraints
				for const in consts[:]:
					consts.remove(const)
				const = consts.new('COPY_TRANSFORMS')
				const.target = active_obj
				const.subtarget = bone.name
		return {'FINISHED'}

class MakeLinkSoftbodySettings(bpy.types.Operator):
	bl_idname = "object.make_link_softbody_settings"
	bl_label = "Link the setting of soft body"
	bl_description = "The setting of the soft body of active objects, I will copy it to the other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		active_obj = context.active_object
		if (not active_obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		active_softbody = None
		for mod in active_obj.modifiers:
			if (mod.type == 'SOFT_BODY'):
				active_softbody = mod
				break
		else:
			self.report(type={'ERROR'}, message="Soft body is not set in the Active Object")
			return {'CANCELLED'}
		if (len(context.selected_objects) < 2):
			self.report(type={'ERROR'}, message="Run by selecting two or more objects")
			return {'CANCELLED'}
		target_objs = []
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			target_softbody = None
			for mod in obj.modifiers:
				if (mod.type == 'SOFT_BODY'):
					target_softbody = mod
					break
			else:
				target_softbody = obj.modifiers.new("Softbody", 'SOFT_BODY')
			for name in dir(active_softbody.settings):
				if (name[0] != '_'):
					try:
						value = active_softbody.settings.__getattribute__(name)
						target_softbody.settings.__setattr__(name, value)
					except AttributeError:
						pass
			for name in dir(active_softbody.point_cache):
				if (name[0] != '_'):
					try:
						value = active_softbody.point_cache.__getattribute__(name)
						target_softbody.point_cache.__setattr__(name, value)
					except AttributeError:
						pass
		return {'FINISHED'}

class MakeLinkClothSettings(bpy.types.Operator):
	bl_idname = "object.make_link_cloth_settings"
	bl_label = "Link cross-setting of"
	bl_description = "The cloth simulation setting of active objects, I will copy it to the other selected objects"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		active_obj = context.active_object
		if (not active_obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		active_cloth = None
		for mod in active_obj.modifiers:
			if (mod.type == 'CLOTH'):
				active_cloth = mod
				break
		else:
			self.report(type={'ERROR'}, message="Cross has not been set in the Active Object")
			return {'CANCELLED'}
		if (len(context.selected_objects) < 2):
			self.report(type={'ERROR'}, message="Run by selecting two or more objects")
			return {'CANCELLED'}
		target_objs = []
		for obj in context.selected_objects:
			if (active_obj.name != obj.name):
				target_objs.append(obj)
		for obj in target_objs:
			target_cloth = None
			for mod in obj.modifiers:
				if (mod.type == 'CLOTH'):
					target_cloth = mod
					break
			else:
				target_cloth = obj.modifiers.new("Cloth", 'CLOTH')
			for name in dir(active_cloth.settings):
				if (name[0] != '_'):
					try:
						value = active_cloth.settings.__getattribute__(name)
						target_cloth.settings.__setattr__(name, value)
					except AttributeError:
						pass
			for name in dir(active_cloth.point_cache):
				if (name[0] != '_'):
					try:
						value = active_cloth.point_cache.__getattribute__(name)
						target_cloth.point_cache.__setattr__(name, value)
					except AttributeError:
						pass
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
		self.layout.separator()
		self.layout.operator(MakeLinkObjectName.bl_idname, text="Object name", icon="PLUGIN")
		self.layout.operator(MakeLinkLayer.bl_idname, text="Layer", icon="PLUGIN")
		self.layout.operator(MakeLinkDisplaySetting.bl_idname, text="Display Settings", icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(MakeLinkSoftbodySettings.bl_idname, text="Soft body set", icon="PLUGIN")
		self.layout.operator(MakeLinkClothSettings.bl_idname, text="Cross set", icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(MakeLinkUVNames.bl_idname, text="Sky UV", icon="PLUGIN")
		self.layout.operator(MakeLinkArmaturePose.bl_idname, text="Movement of the armature", icon="PLUGIN")
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]

