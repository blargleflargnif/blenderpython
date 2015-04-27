# UV/画像エディター > 「画像」メニュー

import bpy
import os

################
# オペレーター #
################

class RenameImageFileName(bpy.types.Operator):
	bl_idname = "image.rename_image_file_name"
	bl_label = "Using the name of the image file name"
	bl_description = "External images are using the name of the active image file name"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Including the extension", default=True)
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		name = bpy.path.basename(img.filepath_raw)
		if (not self.isExt):
			name, ext = os.path.splitext(name)
		try:
			img.name = name
		except: pass
		return {'FINISHED'}

class AllRenameImageFileName(bpy.types.Operator):
	bl_idname = "image.all_rename_image_file_name"
	bl_label = "In the file name to use for all image names"
	bl_description = "The names of all images using external image file name"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Including the extension", default=True)
	
	def execute(self, context):
		for img in  bpy.data.images:
			name = bpy.path.basename(img.filepath_raw)
			if (not self.isExt):
				name, ext = os.path.splitext(name)
			try:
				img.name = name
			except: pass
		return {'FINISHED'}

class ReloadAllImage(bpy.types.Operator):
	bl_idname = "image.reload_all_image"
	bl_label = "Load all images"
	bl_description = "Reloads all the image data referring to external file"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for img in bpy.data.images:
			if (img.filepath != ""):
				img.reload()
				try:
					img.update()
				except RuntimeError:
					pass
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class FillColor(bpy.types.Operator):
	bl_idname = "image.fill_color"
	bl_label = "Fill with color"
	bl_description = "All fill in the color you specify the active image"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="colors", description="Color fill", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	alpha = bpy.props.FloatProperty(name="Transparency (optical)", description="Transparency (optical)", default=1, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		pixel = list(self.color[:])
		if (4 <= img.channels):
			pixel.append(self.alpha)
		pixels = []
		for i in range(img.size[0] * img.size[1]):
			pixels.extend(pixel)
		img.pixels=pixels
		img.update()
		context.area.tag_redraw()
		return {'FINISHED'}

class RenameImageFile(bpy.types.Operator):
	bl_idname = "image.rename_image_file"
	bl_label = "Change the name of the image file"
	bl_description = "Change the file name of the active image"
	bl_options = {'REGISTER'}
	
	new_name = bpy.props.StringProperty(name="New file name")
	
	def invoke(self, context, event):
		self.new_name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == ""):
			self.report(type={"ERROR"}, message="External file does not exist on this image")
			return {"CANCELLED"}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		pre_filepath = context.edit_image.filepath_raw
		dir = os.path.dirname(bpy.path.abspath(context.edit_image.filepath_raw))
		name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == name):
			self.report(type={"ERROR"}, message="The image file name is the same as the original")
			return {"CANCELLED"}
		bpy.ops.image.save_as(filepath=os.path.join(dir, self.new_name))
		context.edit_image.name = self.new_name
		os.remove(bpy.path.abspath(pre_filepath))
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
		self.layout.operator(FillColor.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RenameImageFile.bl_idname, icon="PLUGIN")
		self.layout.operator(RenameImageFileName.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(AllRenameImageFileName.bl_idname, icon="PLUGIN")
		self.layout.operator(ReloadAllImage.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
