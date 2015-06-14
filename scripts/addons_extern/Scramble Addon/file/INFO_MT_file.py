# 情報 > 「ファイル」メニュー

import bpy
import mathutils
import os.path
import os, sys
import subprocess
import fnmatch

################
# オペレーター #
################

class RestartBlender(bpy.types.Operator):
	bl_idname = "wm.restart_blender"
	bl_label = "Reboot"
	bl_description = "Blender Restart"
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
		self.report(type={"INFO"}, message="Load last AutoSave file")
		return {'FINISHED'}

class SaveMainfileUnmassage(bpy.types.Operator):
	bl_idname = "wm.save_mainfile_unmassage"
	bl_label = "Save without prompting"
	bl_description = "Save the changes without displaying the confirmation message"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		if (bpy.data.filepath != ""):
			bpy.ops.wm.save_mainfile()
			self.report(type={"INFO"}, message=bpy.path.basename(bpy.data.filepath)+" Has been saved")
		else:
			self.report(type={"ERROR"}, message="To save your find")
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
	
	def execute(self, context):
		for obj in bpy.data.objects:
			obj.show_all_edges = self.isOn
		return {'FINISHED'}

class AllSetDrawType(bpy.types.Operator):
	bl_idname = "object.all_set_draw_type"
	bl_label = "All the best drawing type schemes"
	bl_description = "Best drawing types in the object of all sets at once"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("MESH", "Mesh", "", 1),
		("CURVE", "Curve", "", 2),
		("SURFACE", "Surface", "", 3),
		("META", "Meta", "", 4),
		("FONT", "Font", "", 5),
		("ARMATURE", "Armature", "", 6),
		("LATTICE", "Lattice", "", 7),
		("EMPTY", "Empty", "", 8),
		("CAMERA", "Camera", "", 9),
		("LAMP", "Lamp", "", 10),
		("SPEAKER", "Speaker", "", 11),
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
	bl_description = "Make the settings on receive a semi-transparent shadow all materials on (off)"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOff = bpy.props.BoolProperty(name="Turn Off", default=False)
	
	def execute(self, context):
		for mat in bpy.data.materials:
			mat.use_transparent_shadows = not self.isOff
		return {'FINISHED'}

class AllSetMaterialColorRamp(bpy.types.Operator):
	bl_idname = "material.all_set_material_color_ramp"
	bl_label = "Copy the color ramp setting of active material in other"
	bl_description = "copy the active material color lamp configuration to all other material (can be selected object only)"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Selected object only", default=False)
	
	def execute(self, context):
		activeMat = context.active_object.active_material
		if (not activeMat):
			self.report(type={"ERROR"}, message="No active material")
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
	bl_label = "Copy FreeStyle color of the active material in other"
	bl_description = "copy the color settings of FreeStyle of active material in all other material (can be selected object only)"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Selected object only", default=False)
	isColor = bpy.props.BoolProperty(name="Color", default=True)
	isAlpha = bpy.props.BoolProperty(name="Alpha", default=True)
	
	def execute(self, context):
		activeMat = context.active_object.active_material
		if (not activeMat):
			self.report(type={"ERROR"}, message="No active material")
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
	bl_label = "The FreeStyle color of all material to diffuse color"
	bl_description = "The FreeStyle line color of all material replace the color that has diffuse color + blend the material"
	bl_options = {'REGISTER', 'UNDO'}
	
	isOnlySelected = bpy.props.BoolProperty(name="Selected object only", default=False)
	blendColor = bpy.props.FloatVectorProperty(name="Blend color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype="COLOR")
	items = [
		("MIX", "Mix", "", 1),
		("MULTI", "Multi", "", 2),
		("SCREEN", "Screen", "", 3),
		]
	blendMode = bpy.props.EnumProperty(items=items, name="Blend mode")
	blendValue = bpy.props.FloatProperty(name="Blend strength", default=0.5, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
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
	bl_label = "全マテリアルのオブジェクトカラーを有効に"
	bl_description = "全マテリアルのオブジェクトカラーの設定をオンもしくはオフにします"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_object_color = bpy.props.BoolProperty(name="オン/オフ", default=True)
	only_selected = bpy.props.BoolProperty(name="選択オブジェクトのみ", default=False)
	
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
	bl_label = "Set Bump Method"
	bl_description = "Set the Bump Method"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("BUMP_ORIGINAL", "Original", "", 1),
		("BUMP_COMPATIBLE", "Compatible", "", 2),
		("BUMP_LOW_QUALITY", "Low Quality", "", 3),
		("BUMP_MEDIUM_QUALITY", "Medium Quality", "", 4),
		("BUMP_BEST_QUALITY", "High Quality", "", 5),
		]
	method = bpy.props.EnumProperty(items=items, name="Type", default="BUMP_BEST_QUALITY")
	
	def execute(self, context):
		for mat in  bpy.data.materials:
			for slot in mat.texture_slots:
				try:
					slot.bump_method = self.method
				except AttributeError: pass
		return {'FINISHED'}

class AllRenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.all_rename_texture_file_name"
	bl_label = "Rename Texture File Name"
	bl_description = "The names of all of the texture, I want to file name of the external image that you are using"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Also including extension", default=True)
	
	def execute(self, context):
		for tex in  bpy.data.textures:
			if (tex.type == "IMAGE"):
				if (not tex.image):
					self.report(type={'WARNING'}, message=tex.name+"Image has not been specified")
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
	bl_label = "Fix Empty UV Layer"
	bl_description = "If UV specified field of texture is blank, and fill in the active UV name of mesh objects that link"
	bl_options = {'REGISTER', 'UNDO'}
	
	isSelectedOnly = bpy.props.BoolProperty(name="Selected object only", default=False)
	
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

######################
# オペレーター(画像) #
######################

class AllRenameImageFileName(bpy.types.Operator):
	bl_idname = "image.all_rename_image_file_name"
	bl_label = "Rename Image File Name"
	bl_description = "The names of all of the image, I want to file name of the external image that you are using"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Also including extension", default=True)
	
	def execute(self, context):
		for img in  bpy.data.images:
			name = bpy.path.basename(img.filepath_raw)
			if (not self.isExt):
				name, ext = os.path.splitext(name)
			try:
				img.name = name
			except: pass
		return {'FINISHED'}

##########################
# オペレーター(物理演算) #
##########################

class AllSetPhysicsFrames(bpy.types.Operator):
	bl_idname = "scene.all_set_physics_frames"
	bl_label = "Collectively set the start / end frame of physics"
	bl_description = "Assign the number of rendering start / end frame to the part you want to set the start / end frames, such as physics"
	bl_options = {'REGISTER', 'UNDO'}
	
	startOffset = bpy.props.IntProperty(name="Start Offset", default=0, step=1)
	endOffset = bpy.props.IntProperty(name="End Offset", default=0, step=1)
	
	isRigidBody = bpy.props.BoolProperty(name="Rigid body", default=True)
	isCloth = bpy.props.BoolProperty(name="Cloth", default=True)
	isSoftBody = bpy.props.BoolProperty(name="Softbody", default=True)
	isFluid = bpy.props.BoolProperty(name="Fluid", default=True)
	isDynamicPaint = bpy.props.BoolProperty(name="Dynamic Paint", default=True)
	
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

class FreeRigidBodyBake(bpy.types.Operator):
	bl_idname = "world.free_rigid_body_bake"
	bl_label = "Clear cache of RigidBody"
	bl_description = "setting will re-create the rigid world by maintaining"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		group = context.scene.rigidbody_world.group
		constraints = context.scene.rigidbody_world.constraints
		time_scale = context.scene.rigidbody_world.time_scale
		steps_per_second = context.scene.rigidbody_world.steps_per_second
		use_split_impulse = context.scene.rigidbody_world.use_split_impulse
		solver_iterations = context.scene.rigidbody_world.solver_iterations
		frame_start = context.scene.rigidbody_world.point_cache.frame_start
		frame_end = context.scene.rigidbody_world.point_cache.frame_end
		
		bpy.ops.rigidbody.world_remove()
		bpy.ops.rigidbody.world_add()
		
		context.scene.rigidbody_world.group = group
		context.scene.rigidbody_world.constraints = constraints
		context.scene.rigidbody_world.time_scale = time_scale
		context.scene.rigidbody_world.steps_per_second = steps_per_second
		context.scene.rigidbody_world.use_split_impulse = use_split_impulse
		context.scene.rigidbody_world.solver_iterations = solver_iterations
		context.scene.rigidbody_world.point_cache.frame_start = frame_start
		context.scene.rigidbody_world.point_cache.frame_end = frame_end
		return {'FINISHED'}

##########################
# サブメニュー(Modifier) #
##########################

class EntireProcessMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process"
	bl_label = "Batch Proccess)"
	bl_description = "all data is a function group to batch process a"
	
	def draw(self, context):
		self.layout.menu(EntireProcessObjectMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(EntireProcessMaterialMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(EntireProcessTextureMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(EntireProcessImageMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(EntireProcessPhysicsMenu.bl_idname, icon="PLUGIN")

class EntireProcessObjectMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_object"
	bl_label = "Object"
	bl_description = "all objects is a function group to batch processing"
	
	def draw(self, context):
		self.layout.operator(AllOnShowAllEdges.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetDrawType.bl_idname, icon="PLUGIN")
		self.layout.operator(AllRenameObjectData.bl_idname, icon="PLUGIN")

class EntireProcessMaterialMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_material"
	bl_label = "Material"
	bl_description = "all material is a function group to batch processing"
	
	def draw(self, context):
		self.layout.operator(AllSetMaterialReceiveTransparent.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetMaterialColorRamp.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetMaterialFreestyleColor.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetMaterialFreestyleColorByDiffuse.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetMaterialObjectColor.bl_idname, icon="PLUGIN")

class EntireProcessTextureMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_texture"
	bl_label = "Texture"
	bl_description = "all texture is a function group to batch process a"
	
	def draw(self, context):
		self.layout.operator(AllRenameTextureFileName.bl_idname, icon="PLUGIN")
		self.layout.operator(AllSetBumpMethod.bl_idname, icon="PLUGIN")
		self.layout.operator(FixEmptyTextureUVLayer.bl_idname, icon="PLUGIN")

class EntireProcessImageMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_image"
	bl_label = "Image"
	bl_description = "all image is a function group to batch process a"
	
	def draw(self, context):
		self.layout.operator(AllRenameImageFileName.bl_idname, icon="PLUGIN")

class EntireProcessPhysicsMenu(bpy.types.Menu):
	bl_idname = "INFO_MT_entire_process_physics"
	bl_label = "Physics"
	bl_description = "data of physics relationship is a function group of batch processing"
	
	def draw(self, context):
		self.layout.operator(AllSetPhysicsFrames.bl_idname, icon="PLUGIN")
		self.layout.operator(FreeRigidBodyBake.bl_idname, icon="PLUGIN")

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
		self.layout.operator(RestartBlender.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SaveMainfileUnmassage.bl_idname, icon="PLUGIN")
		self.layout.operator(RecoverLatestAutoSave.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.separator()
		self.layout.separator()
		self.layout.menu(EntireProcessMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
