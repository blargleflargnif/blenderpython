# 情報 > 「ファイル」メニュー > 「外部データ」メニュー

import bpy
import os

################
# オペレーター #
################

class ReloadAllImage(bpy.types.Operator):
	bl_idname = "image.reload_all_image"
	bl_label = "Reload all Images"
	bl_description = "all the image data that refer to the external file I will re-read"
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

class ResaveAllImage(bpy.types.Operator):
	bl_idname = "image.resave_all_image"
	bl_label = "I re-save all the images in the textures folder"
	bl_description = "all the image data that refer to the external file I re-saved in the textures folder"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		if (context.blend_data.filepath == ""):
			self.report(type={"ERROR"}, message="Run to Save the blend file")
			return {'CANCELLED'}
		for img in context.blend_data.images:
			if (img.filepath != ""):
				try:
					img.pack()
					img.unpack()
				except RuntimeError:
					pass
		self.report(type={"INFO"}, message="I was re-saved in the textures folder")
		return {'FINISHED'}

class OpenRecentFiles(bpy.types.Operator):
	bl_idname = "wm.open_recent_files"
	bl_label = "Open Recent Files Text"
	bl_description = " Recent Files and I will open in a Blender text editor"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		path = os.path.join(bpy.utils.user_resource('CONFIG'), "recent-files.txt")
		pre_texts = context.blend_data.texts[:]
		bpy.ops.text.open(filepath=path)
		for text in context.blend_data.texts[:]:
			for pre in pre_texts:
				if (text.name == pre.name):
					break
			else:
				new_text = text
				break
		max_area = 0
		target_area = None
		for area in context.screen.areas:
			if (area.type == 'TEXT_EDITOR'):
				target_area = area
				break
			if (max_area < area.height * area.width):
				max_area = area.height * area.width
				target_area = area
		target_area.type = 'TEXT_EDITOR'
		for space in target_area.spaces:
			if (space.type == 'TEXT_EDITOR'):
				space.text = new_text
		return {'FINISHED'}

class OpenBookmarkText(bpy.types.Operator):
	bl_idname = "wm.open_bookmark_text"
	bl_label = "Open Bookmarks Text"
	bl_description = "file I open the browser bookmarks in Blender's text editor"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		path = os.path.join(bpy.utils.user_resource('CONFIG'), "bookmarks.txt")
		pre_texts = context.blend_data.texts[:]
		bpy.ops.text.open(filepath=path)
		for text in context.blend_data.texts[:]:
			for pre in pre_texts:
				if (text.name == pre.name):
					break
			else:
				new_text = text
				break
		max_area = 0
		target_area = None
		for area in context.screen.areas:
			if (area.type == 'TEXT_EDITOR'):
				target_area = area
				break
			if (max_area < area.height * area.width):
				max_area = area.height * area.width
				target_area = area
		target_area.type = 'TEXT_EDITOR'
		for space in target_area.spaces:
			if (space.type == 'TEXT_EDITOR'):
				space.text = new_text
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
		self.layout.operator(ReloadAllImage.bl_idname, icon="PLUGIN")
		self.layout.operator(ResaveAllImage.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(OpenRecentFiles.bl_idname, icon="PLUGIN")
		self.layout.operator(OpenBookmarkText.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
