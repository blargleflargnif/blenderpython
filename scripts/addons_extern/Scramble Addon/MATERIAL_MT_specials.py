# プロパティ > 「マテリアル」タブ > リスト右の▼

import bpy

################
# オペレーター #
################

class RemoveNoAssignMaterial(bpy.types.Operator):
	bl_idname = "material.remove_no_assign_material"
	bl_label = "割り当てのないマテリアルを削除"
	bl_description = "面に一つも割り当てられてないマテリアルを全て削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		preActiveObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				context.scene.objects.active = obj
				preActiveMaterial = obj.active_material
				slots = []
				for slot in obj.material_slots:
					slots.append((slot.name, 0))
				me = obj.data
				for face in me.polygons:
					slots[face.material_index] = (slots[face.material_index][0], slots[face.material_index][1] + 1)
				for name, count in slots:
					if (name != "" and count == 0):
						i = 0
						for slot in obj.material_slots:
							if (slot.name == name):
								break
							i += 1
						obj.active_material_index = i
						bpy.ops.object.material_slot_remove()
		context.scene.objects.active = preActiveObj
		return {'FINISHED'}

class RemoveAllMaterialSlot(bpy.types.Operator):
	bl_idname = "material.remove_all_material_slot"
	bl_label = "マテリアルスロット全削除"
	bl_description = "このオブジェクトのマテリアルスロットを全て削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		if (activeObj.type == "MESH"):
			while True:
				if (0 < len(activeObj.material_slots)):
					bpy.ops.object.material_slot_remove()
				else:
					break
		return {'FINISHED'}

class RemoveEmptyMaterialSlot(bpy.types.Operator):
	bl_idname = "material.remove_empty_material_slot"
	bl_label = "空のマテリアルスロット削除"
	bl_description = "このオブジェクトのマテリアルが割り当てられていないマテリアルスロットを全て削除します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		if (activeObj.type == "MESH"):
			slots = activeObj.material_slots[:]
			slots.reverse()
			i = 0
			for slot in slots:
				active_material_index = i
				if (not slot.material):
					bpy.ops.object.material_slot_remove()
				i += 1
		return {'FINISHED'}

class MoveMaterialSlot(bpy.types.Operator):
	bl_idname = "material.move_material_slot"
	bl_label = "マテリアルスロットを移動"
	bl_description = "アクティブなマテリアルスロットを移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("UP", "上へ", "", 1),
		("DOWN", "下へ", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード")
	
	def execute(self, context):
		activeObj = context.active_object
		if (self.mode == "UP"):
			sourceIndex = activeObj.active_material_index
			if (sourceIndex <= 0):
				self.report(type={"WARNING"}, message="既に一番上です")
				return {"CANCELLED"}
			targetIndex = sourceIndex - 1
		elif (self.mode == "DOWN"):
			sourceIndex = activeObj.active_material_index
			if (len(activeObj.material_slots)-1 <= sourceIndex):
				self.report(type={"WARNING"}, message="既に一番下です")
				return {"CANCELLED"}
			targetIndex = sourceIndex + 1
		sourceLink = activeObj.material_slots[sourceIndex].link
		sourceMaterial = activeObj.material_slots[sourceIndex].material
		activeObj.material_slots[sourceIndex].link = activeObj.material_slots[targetIndex].link
		activeObj.material_slots[sourceIndex].material = activeObj.material_slots[targetIndex].material
		activeObj.material_slots[targetIndex].link = sourceLink
		activeObj.material_slots[targetIndex].material = sourceMaterial
		activeObj.active_material_index = targetIndex
		
		me = activeObj.data
		for poly in me.polygons:
			if (poly.material_index == sourceIndex):
				poly.material_index = targetIndex
			elif (poly.material_index == targetIndex):
				poly.material_index = sourceIndex
		return {'FINISHED'}

class MoveMaterialSlotTop(bpy.types.Operator):
	bl_idname = "material.move_material_slot_top"
	bl_label = "スロットを一番上へ"
	bl_description = "アクティブなマテリアルスロットを一番上に移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		for i in range(activeObj.active_material_index):
			bpy.ops.material.move_material_slot(mode='UP')
		return {'FINISHED'}
class MoveMaterialSlotBottom(bpy.types.Operator):
	bl_idname = "material.move_material_slot_bottom"
	bl_label = "スロットを一番下へ"
	bl_description = "アクティブなマテリアルスロットを一番下に移動させます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		i = 0
		for slot in activeObj.material_slots:
			if (slot.material):
				lastSlotIndex = i
			i += 1
		for i in range(lastSlotIndex - activeObj.active_material_index):
			bpy.ops.material.move_material_slot(mode='DOWN')
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
		self.layout.operator(MoveMaterialSlot.bl_idname, icon="PLUGIN", text="上へ").mode = 'UP'
		self.layout.operator(MoveMaterialSlot.bl_idname, icon="PLUGIN", text="下へ").mode = 'DOWN'
		self.layout.separator()
		self.layout.operator(MoveMaterialSlotTop.bl_idname, icon="PLUGIN")
		self.layout.operator(MoveMaterialSlotBottom.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RemoveAllMaterialSlot.bl_idname, icon="PLUGIN")
		self.layout.operator(RemoveEmptyMaterialSlot.bl_idname, icon="PLUGIN")
		self.layout.operator(RemoveNoAssignMaterial.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
