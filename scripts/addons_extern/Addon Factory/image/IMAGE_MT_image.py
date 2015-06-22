# UV/画像エディター > 「画像」メニュー

import bpy
import os, numpy

################
# オペレーター #
################

class RenameImageFileName(bpy.types.Operator):
	bl_idname = "image.rename_image_file_name"
	bl_label = "Rename Image File Name"
	bl_description = "External images are using the name of the active image file name"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Include Extension", default=True)
	
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
	bl_label = "Rename Image"
	bl_description = "The names of all images using external image file name"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="Include Extension", default=True)
	
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
	bl_label = "Reload all Images"
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
	bl_description = "fill the active image with color"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="Colors", description="Color fill", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
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
	bl_label = "Rename Image"
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

# ながとさんに協力して頂きました、感謝！
class BlurImage(bpy.types.Operator):
	bl_idname = "image.blur_image"
	bl_label = "Blur image"
	bl_description = "Blur The Image"
	bl_options = {'REGISTER', 'UNDO'}
	
	strength = bpy.props.IntProperty(name="Strength", default=10, min=1, max=100, soft_min=1, soft_max=100)
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="Nothing to Blur")
			return {'CANCELLED'}
		w, h, c = img.size[0], img.size[1], img.channels
		ps = numpy.array(img.pixels)
		lengthes = []
		for i in range(999):
			length = 2 ** i
			lengthes.append(length)
			if (self.strength < sum(lengthes)):
				lengthes[-1] -= sum(lengthes) - self.strength
				if (2 <= len(lengthes)):
					if (lengthes[-1] == 0):
						lengthes = lengthes[:-1]
					elif (lengthes[-1] <= lengthes[-2] / 2):
						lengthes[-2] += lengthes[-1]
						lengthes = lengthes[:-1]
				break
		divisor = 16 ** len(lengthes)
		for length in lengthes:
			for (dx, dy, endX, endY) in [(w*c, c, h, w), (c, w*c, w, h)]:
				for (start, end, sign) in [(0, endX, 1), (endX-1, -1, -1)]:
					dir  = sign * dx
					diff = dir * length
					for y in range(0, dy*endY, dy):
						for x in range(start*dx, end*dx - diff, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] + ps[i + diff]
						for x in range(end*dx - diff, end*dx, dir):
							for i in range(y + x, y + x + c):
								ps[i] = ps[i] * 2
		for y in range(0, h*w*c, w*c):
			for x in range(0, w*c, c):
				for i in range(y + x, y + x + c):
					ps[i] = ps[i] / divisor
		img.pixels = ps.tolist()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseWidthImage(bpy.types.Operator):
	bl_idname = "image.reverse_width_image"
	bl_label = "Reverse Width"
	bl_description = "Reverse the Image width"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="Nothing to do")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for i in range(img_height):
			pixels[i] = pixels[i][::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ReverseHeightImage(bpy.types.Operator):
	bl_idname = "image.reverse_height_image"
	bl_label = "Reverse Height"
	bl_description = "Reverse Image Height"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="nothing to do")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class Rotate180Image(bpy.types.Operator):
	bl_idname = "image.rotate_180_image"
	bl_label = "Rotate 180°"
	bl_description = "Rotate image 180°"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		img = context.edit_image
		if (not img):
			self.report(type={'ERROR'}, message="nothing to do")
			return {'CANCELLED'}
		img_width, img_height, img_channel = img.size[0], img.size[1], img.channels
		pixels = numpy.array(img.pixels).reshape(img_height, img_width, img_channel)
		for i in range(img_height):
			pixels[i] = pixels[i][::-1]
		pixels = pixels[::-1]
		img.pixels = pixels.flatten()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class TransformMenu(bpy.types.Menu):
	bl_idname = "IMAGE_MT_image_transform"
	bl_label = "Image Transform"
	bl_description = "Transform Image"
	
	def draw(self, context):
		self.layout.operator(ReverseWidthImage.bl_idname, icon="PLUGIN")
		self.layout.operator(ReverseHeightImage.bl_idname, icon="PLUGIN")
		self.layout.operator(Rotate180Image.bl_idname, icon="PLUGIN")

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
		self.layout.operator(FillColor.bl_idname, icon="PLUGIN")
		self.layout.operator(BlurImage.bl_idname, icon="PLUGIN")
		self.layout.menu(TransformMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RenameImageFile.bl_idname, icon="PLUGIN")
		self.layout.operator(RenameImageFileName.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(AllRenameImageFileName.bl_idname, icon="PLUGIN")
		self.layout.operator(ReloadAllImage.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
