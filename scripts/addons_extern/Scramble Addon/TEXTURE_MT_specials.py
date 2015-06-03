# プロパティ > 「テクスチャ」タブ > リスト右の▼

import bpy

################
# オペレーター #
################

class RenameTextureFileName(bpy.types.Operator):
	bl_idname = "texture.rename_texture_file_name"
	bl_label = "テクスチャ名を使用する画像ファイル名に"
	bl_description = "アクティブなテクスチャの名前を使用している外部画像のファイル名にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isExt = bpy.props.BoolProperty(name="拡張子も含む", default=True)
	
	def execute(self, context):
		tex = context.texture
		if (not tex):
			self.report(type={"ERROR"}, message="画像/動画テクスチャで実行してください")
			return {"CANCELLED"}
		if (tex.type == "IMAGE"):
			if (not tex.image):
				self.report(type={"ERROR"}, message="画像が指定されていません")
				return {"CANCELLED"}
			if (tex.image.filepath_raw != ""):
				name = bpy.path.basename(tex.image.filepath_raw)
				if (not self.isExt):
					name, ext = os.path.splitext(name)
				try:
					tex.name = name
				except: pass
		else:
			self.report(type={"ERROR"}, message="画像/動画テクスチャで実行してください")
			return {"CANCELLED"}
		return {'FINISHED'}

class RemoveAllTextureSlots(bpy.types.Operator):
	bl_idname = "texture.remove_all_texture_slots"
	bl_label = "テクスチャスロットを全て空に"
	bl_description = "アクティブなマテリアルの全てのテクスチャスロットを空にします"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		slots = context.active_object.active_material.texture_slots[:]
		for i in range(len(slots)):
			context.active_object.active_material.texture_slots.clear(i)
		return {'FINISHED'}

class SlotMoveTop(bpy.types.Operator):
	bl_idname = "texture.slot_move_top"
	bl_label = "最上段へ"
	bl_description = "アクティブなテクスチャスロットを一番上に移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		preTop = context.active_object.active_material.texture_slots[0]
		i = 0
		while True:
			if (preTop != context.active_object.active_material.texture_slots[0]):
				break
			preTop = context.active_object.active_material.texture_slots[0]
			bpy.ops.texture.slot_move(type='UP')
			if (100 <= i): break
			i += 1
		return {'FINISHED'}
class SlotMoveBottom(bpy.types.Operator):
	bl_idname = "texture.slot_move_bottom"
	bl_label = "最下段へ"
	bl_description = "アクティブなテクスチャスロットを一番下に移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for i in range(len(context.active_object.active_material.texture_slots)):
			if (context.active_object.active_material.texture_slots[i]):
				slotIndex = i
		preBottom = context.active_object.active_material.texture_slots[slotIndex]
		i = 0
		while True:
			if (preBottom != context.active_object.active_material.texture_slots[slotIndex]):
				break
			preBottom = context.active_object.active_material.texture_slots[slotIndex]
			bpy.ops.texture.slot_move(type='DOWN')
			if (100 <= i): break
			i += 1
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
		self.layout.operator(SlotMoveTop.bl_idname, icon="PLUGIN")
		self.layout.operator(SlotMoveBottom.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RemoveAllTextureSlots.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RenameTextureFileName.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
