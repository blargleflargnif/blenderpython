# UV/画像エディター > 「画像」メニュー

import bpy
import os

################
# オペレーター #
################

class RenameImageFileName(bpy.types.Operator):
	bl_idname = "image.rename_image_file_name"
	bl_label = "画像名を使用するファイル名に"
	bl_description = "アクティブな画像の名前を、使用している外部画像のファイル名にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="拡張子も含む", default=True)
	
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
	bl_label = "全ての画像名を使用するファイル名に"
	bl_description = "全ての画像の名前を、使用している外部画像のファイル名にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="拡張子も含む", default=True)
	
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
	bl_label = "全ての画像を再読み込み"
	bl_description = "外部ファイルを参照している画像データを全て読み込み直します"
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
	bl_label = "指定色で塗り潰し"
	bl_description = "アクティブな画像を指定した色で全て塗り潰します"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="色", description="塗り潰す色", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	alpha = bpy.props.FloatProperty(name="透明度", description="透明度", default=1, min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3)
	
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
	bl_label = "画像ファイル名を変更"
	bl_description = "アクティブな画像のファイル名を変更します"
	bl_options = {'REGISTER'}
	
	new_name = bpy.props.StringProperty(name="新しいファイル名")
	
	def invoke(self, context, event):
		self.new_name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == ""):
			self.report(type={"ERROR"}, message="この画像には外部ファイルが存在しません")
			return {"CANCELLED"}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		pre_filepath = context.edit_image.filepath_raw
		dir = os.path.dirname(bpy.path.abspath(context.edit_image.filepath_raw))
		name = bpy.path.basename(context.edit_image.filepath_raw)
		if (self.new_name == name):
			self.report(type={"ERROR"}, message="画像ファイル名が元と同じです")
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
