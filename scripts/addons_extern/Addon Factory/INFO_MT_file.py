# 「情報」エリア > 「ファイル」メニュー

import bpy
import mathutils
import os.path
import os, sys, codecs
import subprocess
import fnmatch

################
# オペレーター #
################

class RestartBlender(bpy.types.Operator):
	bl_idname = "wm.restart_blender"
	bl_label = "Restart"
	bl_description = "Restart the Blender"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		py = os.path.join(os.path.dirname(__file__), "console_toggle.py")
		filepath = bpy.data.filepath
		if (filepath != ""):
			subprocess.Popen([sys.argv[0], filepath, '-P', py])
		else:
			subprocess.Popen([sys.argv[0],'-P', py])
		bpy.ops.wm.quit_blender()
		return {'FINISHED'}

class RecoverLatestAutoSave(bpy.types.Operator):
	bl_idname = "wm.recover_latest_auto_save"
	bl_label = "Load last AutoSave"
	bl_description = "Open the file automatically in order to restore the most recent file"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		tempPath = context.user_preferences.filepaths.temporary_directory
		if (not tempPath):
			return False
		for fileName in fnmatch.filter(os.listdir(tempPath), "*.blend"):
			if (fileName != "quit.blend"):
				return True
		return False
	
	def execute(self, context):
		tempPath = context.user_preferences.filepaths.temporary_directory
		lastFile = None
		for fileName in fnmatch.filter(os.listdir(tempPath), "*.blend"):
			path = os.path.join(tempPath, fileName)
			if (lastFile):
				mtime = os.stat(path).st_mtime
				if (lastTime < mtime and fileName != "quit.blend"):
					lastFile = path
					lastTime = mtime
			else:
				lastFile = path
				lastTime = os.stat(path).st_mtime
		bpy.ops.wm.recover_auto_save(filepath=lastFile)
		self.report(type={'INFO'}, message="Load last AutoSave file")
		return {'FINISHED'}

class SaveMainfileUnmassage(bpy.types.Operator):
	bl_idname = "wm.save_mainfile_unmassage"
	bl_label = "Save without prompting"
	bl_description = "Save the changes without displaying the confirmation message"
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		if (bpy.data.filepath):
			return True
		return False
	
	def execute(self, context):
		if (bpy.data.filepath != ""):
			bpy.ops.wm.save_mainfile()
			self.report(type={"INFO"}, message=bpy.path.basename(bpy.data.filepath)+" Has been saved")
		else:
			self.report(type={"ERROR"}, message="To save your find")
		return {'FINISHED'}

class LoadLastFile(bpy.types.Operator):
	bl_idname = "wm.load_last_file"
	bl_label = "Open the last used file"
	bl_description = "Opens the file at the top of the \"recent files\""
	bl_options = {'REGISTER'}
	
	@classmethod
	def poll(cls, context):
		recent_files = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		file = codecs.open(recent_files, 'r', 'utf-8-sig')
		path = file.readline().rstrip("\r\n")
		file.close()
		if (path != ""):
			return True
		return False
	
	def execute(self, context):
		recent_files = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		file = codecs.open(recent_files, 'r', 'utf-8-sig')
		path = file.readline().rstrip("\r\n")
		file.close()
		bpy.ops.wm.open_mainfile(filepath=path)
		return {'FINISHED'}

##########################
# オペレーター(全体処理) #
##########################

class RenameDataBlocks(bpy.types.Operator):
	bl_idname = "file.rename_data_blocks"
	bl_label = "Data name to rename."
	bl_description = "Rename using all of the data is available"
	bl_options = {'REGISTER', 'UNDO'}
	
	actions = bpy.props.BoolProperty(name="Action", default=False)
	armatures = bpy.props.BoolProperty(name="Armature", default=False)
	brushes = bpy.props.BoolProperty(name="Brush", default=False)
	cameras = bpy.props.BoolProperty(name="Camera", default=False)
	curves = bpy.props.BoolProperty(name="Curve", default=False)
	fonts = bpy.props.BoolProperty(name="Font", default=False)
	grease_pencil = bpy.props.BoolProperty(name="Grease pencil", default=False)
	groups = bpy.props.BoolProperty(name="Group", default=False)
	images = bpy.props.BoolProperty(name="Images", default=False)
	lamps = bpy.props.BoolProperty(name="Lamp", default=False)
	lattices = bpy.props.BoolProperty(name="Lattice", default=False)
	libraries = bpy.props.BoolProperty(name="Library", default=False)
	linestyles = bpy.props.BoolProperty(name="Line style", default=False)
	masks = bpy.props.BoolProperty(name="Mask", default=False)
	materials = bpy.props.BoolProperty(name="Material", default=False)
	meshes = bpy.props.BoolProperty(name="Mesh", default=False)
	metaballs = bpy.props.BoolProperty(name="Metaballs", default=False)
	movieclips = bpy.props.BoolProperty(name="Movie clips", default=False)
	node_groups = bpy.props.BoolProperty(name="Node groups", default=False)
	objects = bpy.props.BoolProperty(name="Object", default=False)
	palettes = bpy.props.BoolProperty(name="Palette", default=False)
	particles = bpy.props.BoolProperty(name="Particle", default=False)
	scenes = bpy.props.BoolProperty(name="Scene", default=False)
	screens = bpy.props.BoolProperty(name="Screen", default=False)
	scripts = bpy.props.BoolProperty(name="Script", default=False)
	shape_keys = bpy.props.BoolProperty(name="Shape key", default=False)
	sounds = bpy.props.BoolProperty(name="Sound", default=False)
	speakers = bpy.props.BoolProperty(name="Speakers", default=False)
	texts = bpy.props.BoolProperty(name="Text", default=False)
	textures = bpy.props.BoolProperty(name="Texture", default=False)
	window_managers = bpy.props.BoolProperty(name="Window manager", default=False)
	worlds = bpy.props.BoolProperty(name="World", default=False)
	
	modifiers = bpy.props.BoolProperty(name="Modifier", default=False)
	constraints = bpy.props.BoolProperty(name="Constraint", default=False)
	
	vertex_groups = bpy.props.BoolProperty(name="Vertex groups", default=False)
	uvs = bpy.props.BoolProperty(name="UV", default=False)
	vertex_colors = bpy.props.BoolProperty(name="Vertex color", default=False)
	
	bones = bpy.props.BoolProperty(name="Bone", default=False)
	bone_constraints = bpy.props.BoolProperty(name="Bone constraint", default=False)
	
	prefix = bpy.props.StringProperty(name="Add to the top", default="")
	suffix = bpy.props.StringProperty(name="Add at the end", default="")
	
	source = bpy.props.StringProperty(name="Before the replacement", default="")
	replace = bpy.props.StringProperty(name="Replacement", default="")
	
	selected_only = bpy.props.BoolProperty(name="Selected objects only", default=False)
	show_log = bpy.props.BoolProperty(name="Show log", default=True)
	
	def draw(self, context):
		data_names = ['objects', 'meshes', 'curves', 'metaballs', 'fonts', 'armatures', 'lattices', 'cameras', 'lamps', 'speakers', 'materials', 'textures', 'images', 'actions', 'brushes', 'grease_pencil', 'groups', 'libraries', 'linestyles', 'masks', 'movieclips', 'node_groups', 'palettes', 'particles', 'scenes', 'screens', 'scripts', 'shape_keys', 'sounds', 'texts', 'window_managers', 'worlds']
		self.layout.label(text="To rename the data to check")
		for i, data_name in enumerate(data_names):
			if (i % 2 == 0):
				row = self.layout.row()
			row.prop(self, data_name)
		self.layout.label(text="Object")
		row = self.layout.row()
		row.prop(self, 'modifiers')
		row.prop(self, 'constraints')
		self.layout.label(text="Mesh")
		row = self.layout.row()
		row.prop(self, 'vertex_groups')
		row.prop(self, 'uvs')
		row = self.layout.row()
		row.prop(self, 'vertex_colors')
		self.layout.label(text="Armature")
		row = self.layout.row()
		row.prop(self, 'bones')
		row.prop(self, 'bone_constraints')
		self.layout.label(text="Renaming settings")
		row = self.layout.row()
		row.prop(self, 'prefix')
		row.prop(self, 'suffix')
		row = self.layout.row()
		row.prop(self, 'source')
		row.prop(self, 'replace')
		row = self.layout.row()
		row.prop(self, 'selected_only')
		row.prop(self, 'show_log')
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def rename(self, name):
		new_name = self.prefix + name.replace(self.source, self.replace) + self.suffix
		if (self.show_log):
			if (name != new_name):
				self.report(type={'INFO'}, message=name+" => "+new_name)
		return new_name
	def execute(self, context):
		data_names = ['objects', 'meshes', 'curves', 'metaballs', 'fonts', 'armatures', 'lattices', 'cameras', 'lamps', 'speakers', 'materials', 'textures', 'images', 'actions', 'brushes', 'grease_pencil', 'groups', 'libraries', 'linestyles', 'masks', 'movieclips', 'node_groups', 'palettes', 'particles', 'scenes', 'screens', 'scripts', 'shape_keys', 'sounds', 'texts', 'window_managers', 'worlds']
		for data_name in data_names:
			if (self.__getattribute__(data_name)):
				if (self.selected_only):
					if (data_name == 'objects'):
						for obj in context.selected_objects[:]:
							obj.name = self.rename(obj.name)
					elif (data_name == 'armatures'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'ARMATURE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'cameras'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'CAMERA'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'curves'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'CURVE' or obj.type == 'SURFACE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'fonts'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'FONT'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'lamps'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'LAMP'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'lattices'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'LATTICE'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'meshes'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'MESH'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'metaballs'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'META'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name == 'speakers'):
						for obj in context.selected_objects[:]:
							if (obj.type == 'SPEAKER'):
								obj.data.name = self.rename(obj.data.name)
					elif (data_name in 'materials'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									if (slot.material.name not in alreadys):
										slot.material.name = self.rename(slot.material.name)
										alreadys.append(slot.material.name)
					elif (data_name in 'textures'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									for tex_slot in slot.material.texture_slots:
										if (tex_slot):
											if (tex_slot.texture.name not in alreadys):
												tex_slot.texture.name = self.rename(tex_slot.texture.name)
												alreadys.append(tex_slot.texture.name)
					elif (data_name in 'images'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for slot in obj.material_slots:
								if (slot):
									for tex_slot in slot.material.texture_slots:
										if (tex_slot):
											if (tex_slot.texture.type == 'IMAGE'):
												if (tex_slot.texture.image):
													if (tex_slot.texture.image.name not in alreadys):
														tex_slot.texture.image.name = self.rename(tex_slot.texture.image.name)
														alreadys.append(tex_slot.texture.image.name)
					elif (data_name in 'grease_pencil'):
						alreadys = []
						for obj in context.selected_objects[:]:
							if (obj.grease_pencil):
								if (obj.grease_pencil.name not in alreadys):
									obj.grease_pencil.name = self.rename(obj.grease_pencil.name)
									alreadys.append(obj.grease_pencil.name)
					elif (data_name in 'particles'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for mod in obj.modifiers[:]:
								if (mod.type == 'PARTICLE_SYSTEM'):
									if (mod.particle_system.name not in alreadys):
										mod.particle_system.name = self.rename(mod.particle_system.name)
										alreadys.append(mod.particle_system.name)
					elif (data_name in 'groups'):
						alreadys = []
						for obj in context.selected_objects[:]:
							for group in obj.users_group[:]:
								if (group.name not in alreadys):
									group.name = self.rename(group.name)
									alreadys.append(group.name)
					elif (data_name in 'shape_keys'):
						alreadys = []
						for obj in context.selected_objects[:]:
							if (obj.type == 'MESH'):
								if (obj.data.shape_keys):
									if (obj.data.shape_keys.name not in alreadys):
										obj.data.shape_keys.name = self.rename(obj.data.shape_keys.name)
										alreadys.append(obj.data.shape_keys.name)
					else:
						self.report(type={'INFO'}, message="Ignored "+data_name+" data")
				else:
					for data in bpy.data.__getattribute__(data_name)[:]:
						data.name = self.rename(data.name)
		if (self.vertex_groups):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for vg in obj.vertex_groups[:]:
					vg.name = self.rename(vg.name)
		if (self.bones):
			if (self.selected_only):
				arms = []
				for obj in context.selected_objects:
					if (obj.type == 'ARMATURE'):
						arms.append(obj.data)
			else:
				arms = bpy.data.armatures[:]
			for arm in arms:
				for bone in arm.bones:
					bone.name = self.rename(bone.name)
		if (self.uvs):
			if (self.selected_only):
				mes = []
				for obj in context.selected_objects:
					if (obj.type == 'MESH'):
						mes.append(obj.data)
			else:
				mes = bpy.data.meshes[:]
			for me in mes:
				for uvl in me.uv_layers[:]:
					uvl.name = self.rename(uvl.name)
		if (self.vertex_colors):
			if (self.selected_only):
				mes = []
				for obj in context.selected_objects:
					if (obj.type == 'MESH'):
						mes.append(obj.data)
			else:
				mes = bpy.data.meshes[:]
			for me in mes:
				for vc in me.vertex_colors[:]:
					vc.name = self.rename(vc.name)
		if (self.modifiers):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for mod in obj.modifiers[:]:
					mod.name = self.rename(mod.name)
		if (self.constraints):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				for const in obj.constraints[:]:
					const.name = self.rename(const.name)
		if (self.bone_constraints):
			if (self.selected_only):
				objs = context.selected_objects[:]
			else:
				objs = bpy.data.objects[:]
			for obj in objs:
				if (obj.type == 'ARMATURE'):
					for bone in obj.pose.bones[:]:
						for const in bone.constraints:
							const.name = self.rename(const.name)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

##############################
# オペレーター(オブジェクト) #
##############################

class AllOnShowAllEdges(bpy.types.Operator):
	bl_idname = "object.all_on_show_all_edges"
	bl_label = "All show all sides turn"
	bl_description = "Show all sides of all objects (can be off) turn the display settings"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOn = bpy.props.BoolProperty(name="To turn on", default=True)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	
	def execute(self, context):
		for obj in bpy.data.objects:
			obj.show_all_edges = self.isOn
		return {'FINISHED'}

class AllSetDrawType(bpy.types.Operator):
	bl_idname = "object.all_set_draw_type"
	bl_label = "All the best drawing type schemes"
	bl_description = "\"Best drawing types in the object of all sets at once"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "Mesh", "", 1),
		("CURVE", "Curve", "", 2),
		("SURFACE", "Surface", "", 3),
		("META", "Metaballs", "", 4),
		("FONT", "Text", "", 5),
		("ARMATURE", "Armature", "", 6),
		("LATTICE", "Lattice", "", 7),
		("EMPTY", "Empty", "", 8),
		("CAMERA", "Camera", "", 9),
		("LAMP", "Lamp", "", 10),
		("SPEAKER", "Speakers", "", 11),
		("ALL", "All objects", "", 12),
		]
	objType = bpy.props.EnumProperty(items=items, name="The type of the object")
	items = [
		("TEXTURED", "Texture", "", 1),
		("SOLID", "Solid", "", 2),
		("WIRE", "Wire", "", 3),
		("BOUNDS", "Bound", "", 4),
		]
	type = bpy.props.EnumProperty(items=items, name="Drawing type")
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	
	def execute(self, context):
		for obj in bpy.data.objects:
			if (self.objType == obj.type or self.objType == "ALL"):
				obj.draw_type = self.type
		return {'FINISHED'}

class AllRenameObjectData(bpy.types.Operator):
	bl_idname = "object.all_rename_object_data"
	bl_label = "All the data name to object name and same"
	bl_description = "Replaces object name linked to name all the object data (mesh data etc)"
	bl_options = {'REGISTER', 'UNDO'}
	
	isSelected = bpy.props.BoolProperty(name="Only the selected object", default=False)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.objects)):
			return True
		return False
	
	def execute(self, context):
		if (self.isSelected):
			objs = context.selected_objects
		else:
			objs = bpy.data.objects
		for obj in objs:
			if (obj and obj.data):
				obj.data.name = obj.name
		return {'FINISHED'}

############################
# オペレーター(マテリアル) #
############################

class AllSetMaterialReceiveTransparent(bpy.types.Operator):
	bl_idname = "material.all_set_material_receive_transparent"
	bl_label = "On receiving the Semitransparent Shadow material of all"
	bl_description = "You to receive a semi-transparent shadow?\"of all material (off) on the"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOff = bpy.props.BoolProperty(name="To turn off", default=False)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False
	
	def execute(self, context):
		for mat in bpy.data.materials:
			mat.use_transparent_shadows = not self.isOff
		return {'FINISHED'}

class AllSetMaterialColorRamp(bpy.types.Operator):
	bl_idname = "material.all_set_material_color_ramp"
	bl_label = "Copy the material color ramp settings"
	bl_description = "Color ramp settings of the active material is all material other (only selected objects are allowed) to copy"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Only the selected object", default=False)
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (len(bpy.data.materials)):
			return True
		return False
	
	def execute(self, context):
		activeMat = context.active_object.active_material
		if (not activeMat):
			self.report(type={"ERROR"}, message="Not active")
			return {"CANCELLED"}
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			if (mat.name != activeMat.name):
				mat.use_diffuse_ramp = activeMat.use_diffuse_ramp
				mat.diffuse_ramp.color_mode = activeMat.diffuse_ramp.color_mode
				mat.diffuse_ramp.hue_interpolation = activeMat.diffuse_ramp.hue_interpolation
				mat.diffuse_ramp.interpolation = activeMat.diffuse_ramp.interpolation
				for i in range(len(activeMat.diffuse_ramp.elements)):
					if (len(mat.diffuse_ramp.elements) < i+1):
						color = mat.diffuse_ramp.elements.new(color.position)
					else:
						color = mat.diffuse_ramp.elements[i]
					color.position = activeMat.diffuse_ramp.elements[i].position
					color.alpha = activeMat.diffuse_ramp.elements[i].alpha
					color.color = activeMat.diffuse_ramp.elements[i].color
				mat.diffuse_ramp_input = activeMat.diffuse_ramp_input
				mat.diffuse_ramp_blend = activeMat.diffuse_ramp_blend
				mat.diffuse_ramp_factor = activeMat.diffuse_ramp_factor
		return {'FINISHED'}

class AllSetMaterialFreestyleColor(bpy.types.Operator):
	bl_idname = "material.all_set_material_freestyle_color"
	bl_label = "FreeStyle color of an active copy to other"
	bl_description = "FreeStyle material active color for all materials other (only selected objects are allowed) to copy"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Only the selected object", default=False)
	isColor = bpy.props.BoolProperty(name="Color", default=True)
	isAlpha = bpy.props.BoolProperty(name="Alpha", default=True)
	
	@classmethod
	def poll(cls, context):
		if (not context.object):
			return False
		if (not context.object.active_material):
			return False
		if (len(bpy.data.materials)):
			return True
		return False
	
	def execute(self, context):
		activeMat = context.active_object.active_material
		if (not activeMat):
			self.report(type={"ERROR"}, message="Not active")
			return {"CANCELLED"}
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			if (mat.name != activeMat.name):
				col = list(mat.line_color[:])
				if (self.isColor):
					col[0] = activeMat.line_color[0]
					col[1] = activeMat.line_color[1]
					col[2] = activeMat.line_color[2]
				if (self.isAlpha):
					col[3] = activeMat.line_color[3]
				mat.line_color = tuple(col)
		return {'FINISHED'}

class AllSetMaterialFreestyleColorByDiffuse(bpy.types.Operator):
	bl_idname = "material.all_set_material_freestyle_color_by_diffuse"
	bl_label = "FreeStyle color of all material diffuse color"
	bl_description = "All material (only selected objects are allowed) for FreeStyle line color of the material diffuse color + a blend to replace the"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Only the selected object", default=False)
	blendColor = bpy.props.FloatVectorProperty(name="Blend color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype="COLOR")
	items = [
		("MIX", "Mix", "", 1),
		("MULTI", "Multiplication", "", 2),
		("SCREEN", "Screen", "", 3),
		]
	blendMode = bpy.props.EnumProperty(items=items, name="Blend mode")
	blendValue = bpy.props.FloatProperty(name="Blends strength", default=0.5, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False
	
	def execute(self, context):
		mats = []
		if (self.isOnlySelected):
			for obj in context.selected_objects:
				for mslot in obj.material_slots:
					if (mslot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(mslot.material)
		else:
			mats = bpy.data.materials
		for mat in mats:
			c = (mat.diffuse_color[0], mat.diffuse_color[1], mat.diffuse_color[2], mat.line_color[3])
			b = self.blendColor
			v = self.blendValue
			if (self.blendMode == "MIX"):
				c = ( (c[0]*(1-v))+(b[0]*v), (c[1]*(1-v))+(b[1]*v), (c[2]*(1-v))+(b[2]*v), c[3] )
			if (self.blendMode == "MULTI"):
				c = ( (c[0]*(1-v))+((c[0]*b[0])*v), (c[1]*(1-v))+((c[1]*b[1])*v), (c[2]*(1-v))+((c[2]*b[2])*v), c[3] )
			if (self.blendMode == "SCREEN"):
				c = ( (c[0]*(1-v))+(1-((1-c[0])*(1-b[0]))*v), (c[1]*(1-v))+(1-((1-c[1])*(1-b[1]))*v), (c[2]*(1-v))+(1-((1-c[2])*(1-b[2]))*v), c[3] )
			mat.line_color = c
		return {'FINISHED'}

class AllSetMaterialObjectColor(bpy.types.Operator):
	bl_idname = "material.all_set_material_object_color"
	bl_label = "To enable object color for all materials"
	bl_description = "The select or clear all object color settings"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_object_color = bpy.props.BoolProperty(name="Turn on/off", default=True)
	only_selected = bpy.props.BoolProperty(name="Only the selected object", default=False)
	
	@classmethod
	def poll(cls, context):
		if (len(bpy.data.materials)):
			return True
		return False
	
	def execute(self, context):
		mats = []
		if (self.only_selected):
			for obj in context.selected_objects:
				for slot in obj.material_slots:
					if (slot.material):
						for mat in mats:
							if (mat.name == mslot.material.name):
								break
						else:
							mats.append(slot.material)
		else:
			mats = bpy.data.materials[:]
		for mat in mats:
			mat.use_object_color = self.use_object_color
		return {'FINISHED'}

############################
# オペレーター(テクスチャ) #
############################

class AllSetBumpMethod(bpy.types.Operator):
	bl_idname = "texture.all_set_bump_method"
	bl_label = "Set the bump of all quality"
	bl_description = "Bump-map texture of all quality sets in bulk"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("BUMP_ORIGINAL", "Original", "", 1),
		("BUMP_COMPATIBLE", "Compatibility", "", 2),
		("BUMP_LOW_QUALITY", "Low quality", "", 3),
		("BUMP_MEDIUM_QUALITY", "In the quality", "", 4),
		("BUMP_BEST_QUALITY", "Highest quality", "", 5),
		]
	method = bpy.props.EnumProperty(items=items, name="Quality bump", default="BUMP_BEST_QUALITY")
	
	@classmethod
	def poll(cls, context):
		if (not len(bpy.data.materials)):
			return False
		for mat in  bpy.data.materials:
			for slot in mat.texture_slots:
				if (slot):
					return True
		return False
	
	def execute(self, context):
		for mat in bpy.data.materials:
			for slot in mat.texture_slots:
				try:
					slot.bump_method = self.method
				except AttributeError: pass
		return {'FINISHED'}

class AllRenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.all_rename_texture_file_name"
	bl_label = "All image file names using the texture name"
	bl_description = "The names of all textures use external image file name"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Including the extension", default=True)
	
	@classmethod
	def poll(cls, context):
		for tex in bpy.data.textures:
			if (tex.type == "IMAGE"):
				if (tex.image):
					if (tex.image.filepath != ""):
						return True
		return False
	
	def execute(self, context):
		for tex in  bpy.data.textures:
			if (tex.type == "IMAGE"):
				if (not tex.image):
					self.report(type={'WARNING'}, message=tex.name+"The image is not specified")
					continue
				if (tex.image.filepath_raw != ""):
					name = bpy.path.basename(tex.image.filepath_raw)
					if (not self.isExt):
						name, ext = os.path.splitext(name)
					try:
						tex.name = name
					except: pass
		return {'FINISHED'}

class FixEmptyTextureUVLayer(bpy.types.Operator):
	bl_idname = "texture.fix_empty_texture_uv_layer"
	bl_label = "UV is a blank if you fill the active UV"
	bl_description = "Under active UV texture UV specified fields linked to an empty mesh object fills"
	bl_options = {'REGISTER', 'UNDO'}
	
	isSelectedOnly = bpy.props.BoolProperty(name="Only the selected object", default=False)
	
	@classmethod
	def poll(cls, context):
		for obj in bpy.data.objects:
			if (obj.type == 'MESH'):
				if (len(obj.data.uv_layers)):
					for mslot in obj.material_slots:
						if (mslot.material):
							for tslot in mslot.material:
								if (tslot):
									if (tslot.texture_coords == 'UV'):
										if(tslot.uv_layer == ""):
											return True
		return False
	
	def execute(self, context):
		objs = bpy.data.objects
		if (self.isSelectedOnly):
			objs = context.selected_objects
		for obj in objs:
			if (obj.type == "MESH"):
				me = obj.data
				if (len(me.uv_layers) > 0):
					uv = me.uv_layers.active
					for mslot in obj.material_slots:
						mat = mslot.material
						if (mat):
							for tslot in mat.texture_slots:
								if (tslot != None):
									if (tslot.texture_coords == "UV"):
										if(tslot.uv_layer == ""):
											tslot.uv_layer = uv.name
		return {'FINISHED'}

##########################
# オペレーター(物理演算) #
##########################

class AllSetPhysicsFrames(bpy.types.Operator):
	bl_idname = "scene.all_set_physics_frames"
	bl_label = "Set physical operation start / end frames at once"
	bl_description = "Assign render start / end frames portions to set start / end frames, such as physics"
	bl_options = {'REGISTER', 'UNDO'}
	
	startOffset = bpy.props.IntProperty(name="Start offset", default=0, step=1)
	endOffset = bpy.props.IntProperty(name="Start offset", default=0, step=1)
	
	isRigidBody = bpy.props.BoolProperty(name="Was that body", default=True)
	isCloth = bpy.props.BoolProperty(name="Fabric (cloth)", default=True)
	isSoftBody = bpy.props.BoolProperty(name="Soft body", default=True)
	isFluid = bpy.props.BoolProperty(name="Fluid", default=True)
	isDynamicPaint = bpy.props.BoolProperty(name="Dynamic paint", default=True)
	
	isParticle = bpy.props.BoolProperty(name="Particle", default=False)
	
	def execute(self, context):
		start = context.scene.frame_start + self.startOffset
		end = context.scene.frame_end + self.endOffset
		if (self.isRigidBody and context.scene.rigidbody_world):
			context.scene.rigidbody_world.point_cache.frame_start = start
			context.scene.rigidbody_world.point_cache.frame_end = end
		if (self.isFluid):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'FLUID_SIMULATION'):
						modi.settings.start_time = (1.0 / context.scene.render.fps) * start
						modi.settings.end_time = (1.0 / context.scene.render.fps) * end
		if (self.isSoftBody):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'SOFT_BODY'):
						modi.point_cache.frame_start = start
						modi.point_cache.frame_end = end
		if (self.isDynamicPaint):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'DYNAMIC_PAINT'):
						if (modi.canvas_settings):
							for surface in modi.canvas_settings.canvas_surfaces:
								surface.frame_start = start
								surface.frame_end = end
		if (self.isCloth):
			for obj in bpy.data.objects:
				for modi in obj.modifiers:
					if (modi.type == 'CLOTH'):
						modi.point_cache.frame_start = start
						modi.point_cache.frame_end = end
		
		if (self.isParticle):
			for particle in bpy.data.particles:
				particle.frame_start = start
				particle.frame_end = end
		return {'FINISHED'}

##########################
# サブメニュー(Modifier) #
##########################

class EntireProcessMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process"
	bl_label = "Whole process (use care)"
	bl_description = "Is all data processing functions"
	
	def draw(self, context):
		self.layout.operator(RenameDataBlocks.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.menu(EntireProcessObjectMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(EntireProcessMaterialMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(EntireProcessTextureMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(EntireProcessImageMenu.bl_idname, icon='PLUGIN')
		self.layout.menu(EntireProcessPhysicsMenu.bl_idname, icon='PLUGIN')

class EntireProcessObjectMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_object"
	bl_label = "Object"
	bl_description = "Is a set of batch processing all the objects and features"
	
	def draw(self, context):
		self.layout.operator(AllOnShowAllEdges.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetDrawType.bl_idname, icon='PLUGIN')
		self.layout.operator(AllRenameObjectData.bl_idname, icon='PLUGIN')

class EntireProcessMaterialMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_material"
	bl_label = "Material"
	bl_description = "Is all material processing functions"
	
	def draw(self, context):
		self.layout.operator(AllSetMaterialReceiveTransparent.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialColorRamp.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialFreestyleColor.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialFreestyleColorByDiffuse.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetMaterialObjectColor.bl_idname, icon='PLUGIN')

class EntireProcessTextureMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_texture"
	bl_label = "Texture"
	bl_description = "All is a set of batch processing and texture feature"
	
	def draw(self, context):
		self.layout.operator(AllRenameTextureFileName.bl_idname, icon='PLUGIN')
		self.layout.operator(AllSetBumpMethod.bl_idname, icon='PLUGIN')
		self.layout.operator(FixEmptyTextureUVLayer.bl_idname, icon='PLUGIN')

class EntireProcessImageMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_image"
	bl_label = "Images"
	bl_description = "Is the set of all image processing features"
	
	def draw(self, context):
		self.layout.operator('image.all_rename_image_file_name', icon='PLUGIN')

class EntireProcessPhysicsMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_physics"
	bl_label = "Physical operation"
	bl_description = "Is the relationship between physical operation of data processing functions"
	
	def draw(self, context):
		self.layout.operator(AllSetPhysicsFrames.bl_idname, icon='PLUGIN')

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
		self.layout.operator(LoadLastFile.bl_idname, icon='PLUGIN')
		self.layout.operator(RecoverLatestAutoSave.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(SaveMainfileUnmassage.bl_idname, icon='PLUGIN')
		self.layout.operator('wm.save_userpref', icon='PLUGIN')
		self.layout.separator()
		self.layout.operator(RestartBlender.bl_idname, icon='PLUGIN')
		self.layout.separator()
		self.layout.separator()
		self.layout.separator()
		self.layout.menu(EntireProcessMenu.bl_idname, icon='PLUGIN')
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
