# 3Dビュー > アーマチュア編集モード > 「Shift+W」キー

import bpy

##############
# その他関数 #
##############

################
# オペレーター #
################

class SetBoneNames(bpy.types.Operator):
	bl_idname = "pose.set_bone_names"
	bl_label = "ボーン名をまとめて設定"
	bl_description = "選択中のボーンの名前をまとめて設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="ボーン名", default="Bone")
	
	def execute(self, context):
		context.active_bone.name = "temp"
		context.active_bone.name = self.name
		if (context.selected_bones):
			for bone in context.selected_bones:
				bone.name = self.name
		if (context.selected_pose_bones):
			for bone in context.selected_pose_bones:
				bone.name = self.name
		return {'FINISHED'}

class SetCurvedBones(bpy.types.Operator):
	bl_idname = "pose.set_curved_bones"
	bl_label = "カーブボーンをまとめて設定"
	bl_description = "選択中のボーンのカーブボーン設定をします"
	bl_options = {'REGISTER', 'UNDO'}
	
	bbone_segments = bpy.props.IntProperty(name="セグメント", default=1, min=1, soft_min=1)
	bbone_in = bpy.props.FloatProperty(name="イーズイン", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)
	bbone_out = bpy.props.FloatProperty(name="イーズアウト", default=1.0, min=0, max=2, soft_min=0, soft_max=2, step=10, precision=3)
	
	def execute(self, context):
		obj = bpy.context.active_object
		if (obj.type == "ARMATURE"):
			for bone in context.selected_pose_bones:
				obj.data.bones[bone.name].bbone_segments = self.bbone_segments
				obj.data.bones[bone.name].bbone_in = self.bbone_in
				obj.data.bones[bone.name].bbone_out = self.bbone_out
		return {'FINISHED'}

class SetBoneRoll(bpy.types.Operator):
	bl_idname = "pose.set_bone_roll"
	bl_label = "ロールをまとめて設定"
	bl_description = "選択中のボーンのロールを設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	roll = bpy.props.FloatProperty(name="ロール", default=0, step=10, precision=3)
	
	def execute(self, context):
		for bone in context.selected_bones:
			bone.roll = self.roll
		return {'FINISHED'}

class LinkIKSetting(bpy.types.Operator):
	bl_idname = "pose.link_ik_setting"
	bl_label = "アクティブのIK設定(回転制限等)をコピー"
	bl_description = "アクティブなボーンのIK設定(回転制限など)を他の選択ボーンにコピーします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isX = bpy.props.BoolProperty(name="X軸の設定", default=True)
	isY = bpy.props.BoolProperty(name="Y軸の設定", default=True)
	isZ = bpy.props.BoolProperty(name="Z軸の設定", default=True)
	isStretch = bpy.props.BoolProperty(name="ストレッチの設定", default=True)
	
	def execute(self, context):
		activeBone = context.active_pose_bone
		for bone in context.selected_pose_bones:
			if (activeBone.name != bone.name):
				if (self.isX):
					bone.lock_ik_x = activeBone.lock_ik_x
					bone.use_ik_limit_x = activeBone.use_ik_limit_x
					bone.ik_stiffness_x = activeBone.ik_stiffness_x
					bone.ik_min_x = activeBone.ik_min_x
					bone.ik_max_x = activeBone.ik_max_x
				if (self.isY):
					bone.lock_ik_y = activeBone.lock_ik_y
					bone.use_ik_limit_y = activeBone.use_ik_limit_y
					bone.ik_stiffness_y = activeBone.ik_stiffness_y
					bone.ik_min_y = activeBone.ik_min_y
					bone.ik_max_y = activeBone.ik_max_y
				if (self.isZ):
					bone.lock_ik_z = activeBone.lock_ik_z
					bone.use_ik_limit_z = activeBone.use_ik_limit_z
					bone.ik_stiffness_z = activeBone.ik_stiffness_z
					bone.ik_min_z = activeBone.ik_min_z
					bone.ik_max_z = activeBone.ik_max_z
				if (self.isStretch):
					bone.ik_stretch = activeBone.ik_stretch
		return {'FINISHED'}

class SetIKPoleTarget(bpy.types.Operator):
	bl_idname = "pose.set_ik_pole_target"
	bl_label = "IKのポールターゲットを設定"
	bl_description = "アクティブなボーンのIKのポールターゲットを第二選択ボーンに設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		activeBone = context.active_pose_bone
		if (len(context.selected_pose_bones) != 2):
			self.report(type={"ERROR"}, message="ボーンを二つ選択して実行してください")
			return {"CANCELLED"}
		for bone in context.selected_pose_bones:
			if (activeBone.name != bone.name):
				ik = None
				for const in activeBone.constraints:
					if (const.type == "IK"):
						ik = const
				if (ik == None):
					self.report(type={"ERROR"}, message="アクティブボーンにIKコンストレイントがありません")
					return {"CANCELLED"}
				ik.pole_target = activeObj
				ik.pole_subtarget = bone.name
		return {'FINISHED'}

class SetIKChainLength(bpy.types.Operator):
	bl_idname = "pose.set_ik_chain_length"
	bl_label = "IKのチェーンの長さを設定"
	bl_description = "アクティブなボーンのIKのチェーンの長さを第二選択ボーンへの長さへと設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeBone = context.active_pose_bone
		if (len(context.selected_pose_bones) != 2):
			self.report(type={"ERROR"}, message="ボーンを二つ選択して実行してください")
			return {"CANCELLED"}
		targetBone = None
		for bone in context.selected_pose_bones:
			if (activeBone.name != bone.name):
				targetBone = bone
		tempBone = activeBone
		i = 0
		while True:
			if (tempBone.parent):
				if (tempBone.name == targetBone.name):
					i += 1
					break
				tempBone = tempBone.parent
				i += 1
			else:
				i = 0
				break
		if (i == 0):
			self.report(type={"ERROR"}, message="上手くチェーン数を取得出来ませんでした")
			return {"CANCELLED"}
		ik = None
		for const in activeBone.constraints:
			if (const.type == "IK"):
				ik = const
		ik.chain_count = i
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
		self.layout.operator(SetBoneNames.bl_idname, icon="PLUGIN")
		self.layout.operator(SetBoneRoll.bl_idname, icon="PLUGIN")
		self.layout.operator(SetCurvedBones.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SetIKPoleTarget.bl_idname, icon="PLUGIN")
		self.layout.operator(SetIKChainLength.bl_idname, icon="PLUGIN")
		self.layout.operator(LinkIKSetting.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
