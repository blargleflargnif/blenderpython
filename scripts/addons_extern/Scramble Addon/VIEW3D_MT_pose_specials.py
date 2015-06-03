# 3Dビュー > ポーズモード > 「W」キー

import bpy
import re, math

################
# オペレーター #
################

class CreateCustomShape(bpy.types.Operator):
	bl_idname = "pose.create_custom_shape"
	bl_label = "カスタムシェイプを作成"
	bl_description = "選択中のボーンのカスタムシェイプオブジェクトを作成します"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="オブジェクト名", default="カスタムシェイプ用オブジェクト")
	items = [
		("1", "線", "", 1),
		("2", "ひし形", "", 2),
		]
	shape = bpy.props.EnumProperty(items=items, name="形")
	isObjectMode =  bpy.props.BoolProperty(name="完了後オブジェクトモードに", default=True)
	isHide = bpy.props.BoolProperty(name="完了後アーマチュアを隠す", default=True)
	
	def execute(self, context):
		obj = bpy.context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "POSE"):
				bpy.ops.object.mode_set(mode="OBJECT")
				for bone in obj.data.bones:
					if(bone.select == True):
						bpy.ops.object.select_all(action="DESELECT")
						
						#context.scene.cursor_location = bone.head_local
						bone.show_wire = True
						
						me = bpy.data.meshes.new(self.name)
						if (self.shape == "1"):
							me.from_pydata([(0,0,0), (0,1,0)], [(0,1)], [])
						elif (self.shape == "2"):
							me.from_pydata([(0,0,0), (0,1,0), (0.1,0.5,0), (0,0.5,0.1), (-0.1,0.5,0), (0,0.5,-0.1)], [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (3,4), (4,5), (5,2)], [])
						me.update()
						meObj = bpy.data.objects.new(me.name, me)
						meObj.data = me
						context.scene.objects.link(meObj)
						meObj.select = True
						context.scene.objects.active = meObj
						
						meObj.draw_type = "WIRE"
						meObj.show_x_ray = True
						bpy.ops.object.constraint_add(type="COPY_TRANSFORMS")
						meObj.constraints[-1].target = obj
						meObj.constraints[-1].subtarget = bone.name
						bpy.ops.object.visual_transform_apply()
						meObj.constraints.remove(meObj.constraints[-1])
						obj.pose.bones[bone.name].custom_shape = meObj
						len = bone.length
						bpy.ops.transform.resize(value=(len, len, len))
				bpy.ops.object.select_all(action="DESELECT")
				obj.select = True
				context.scene.objects.active = obj
				bpy.ops.object.mode_set(mode="POSE")
				if (self.isObjectMode or self.isHide):
					bpy.ops.object.mode_set(mode="OBJECT")
				if (self.isHide):
					obj.hide = True
			else:
				self.report(type={"ERROR"}, message="ポーズモードで実行してください")
				return {'CANCELLED'}
		else:
			self.report(type={"ERROR"}, message="アクティブオブジェクトがアーマチュアではありません")
			return {'CANCELLED'}
		return {'FINISHED'}

class CreateWeightCopyMesh(bpy.types.Operator):
	bl_idname = "pose.create_weight_copy_mesh"
	bl_label = "ウェイトコピー用メッシュを作成"
	bl_description = "選択中のボーンのウェイトコピーで使用するメッシュを作成します"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="作成するオブジェクト名", default="ウェイトコピー用オブジェクト")
	items = [
		("TAIL", "末尾", "", 1),
		("HEAD", "根本", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="ウェイトの位置")
	
	def execute(self, context):
		obj = bpy.context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "POSE"):
				bpy.ops.object.mode_set(mode="OBJECT")
				bones = []
				for bone in obj.data.bones:
					if(bone.select and not bone.hide):
						bones.append(bone)
				me = bpy.data.meshes.new(self.name)
				verts = []
				edges = []
				for bone in bones:
					co = bone.tail_local
					if (self.mode == "HEAD"):
						co = bone.head_local
					verts.append(co)
					i = 0
					for b in bones:
						if (bone.parent):
							if (bone.parent.name == b.name):
								edges.append((len(verts)-1, i))
								break
						i += 1
				me.from_pydata(verts, edges, [])
				me.update()
				meObj = bpy.data.objects.new(self.name, me)
				meObj.data = me
				context.scene.objects.link(meObj)
				bpy.ops.object.select_all(action="DESELECT")
				meObj.select = True
				context.scene.objects.active = meObj
				
				i = 0
				for bone in bones:
					meObj.vertex_groups.new(bone.name)
					meObj.vertex_groups[bone.name].add([i], 1.0, "REPLACE")
					i += 1
				
				#bpy.ops.object.mode_set(mode="EDIT")
				#bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, 0.01)})
				#bpy.ops.object.mode_set(mode="OBJECT")
			else:
				self.report(type={"ERROR"}, message="ポーズモードで実行してください")
				return {'CANCELLED'}
		else:
			self.report(type={"ERROR"}, message="アクティブオブジェクトがアーマチュアではありません")
			return {'CANCELLED'}
		return {'FINISHED'}

class CopyBoneName(bpy.types.Operator):
	bl_idname = "pose.copy_bone_name"
	bl_label = "ボーン名をクリップボードにコピー"
	bl_description = "アクティブボーンの名前をクリップボードにコピーします"
	bl_options = {'REGISTER', 'UNDO'}
	
	isObject = bpy.props.BoolProperty(name="オブジェクト名も", default=False)
	
	def execute(self, context):
		if (self.isObject):
			context.window_manager.clipboard = context.active_object.name + ":" + context.active_pose_bone.name
		else:
			context.window_manager.clipboard = context.active_pose_bone.name
		return {'FINISHED'}

class SplineGreasePencil(bpy.types.Operator):
	bl_idname = "pose.spline_grease_pencil"
	bl_label = "チェーン状ボーンをグリースペンシルに沿わせる"
	bl_description = "チェーンの様に繋がった選択ボーンをグリースペンシルに沿わせてポーズを付けます"
	bl_options = {'REGISTER', 'UNDO'}
	
	isRootReset = bpy.props.BoolProperty(name="根本を元の位置に", default=False)
	
	def execute(self, context):
		activeObj = context.active_object
		i = 0
		for bone in context.selected_pose_bones:
			for bone2 in context.selected_pose_bones:
				if (bone.parent):
					if (bone.parent.name == bone2.name):
						i += 1
						break
		if (i+1 < len(context.selected_pose_bones)):
			self.report(type={"ERROR"}, message="チェーン状に繋がったボーン群を選択して実行して下さい")
			return {'CANCELLED'}
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.gpencil.convert(type='CURVE', use_timing_data=True)
		for obj in context.selectable_objects:
			if ("GP_Layer" in obj.name):
				curveObj = obj
		bpy.ops.object.mode_set(mode='POSE')
		tails = []
		for bone in context.selected_pose_bones:
			if (len(bone.children) == 0):
				const = bone.constraints.new("SPLINE_IK")
				const.target = curveObj
				const.use_curve_radius = False
				const.use_y_stretch = False
				const.chain_count = len(context.selected_pose_bones)
				tails.append((bone, const))
			for child in bone.children:
				for bone2 in context.selected_pose_bones:
					if (child.name == bone2.name):
						break
				else:
					const = bone.constraints.new("SPLINE_IK")
					const.target = curveObj
					const.use_curve_radius = False
					const.use_y_stretch = False
					const.chain_count = len(context.selected_pose_bones)
					tails.append((bone, const))
					break
		bpy.ops.pose.visual_transform_apply()
		for bone, const in tails:
			bone.constraints.remove(const)
		bpy.ops.pose.scale_clear()
		context.scene.objects.unlink(curveObj)
		if (self.isRootReset):
			bpy.ops.pose.loc_clear()
		return {'FINISHED'}

class RenameBoneRegularExpression(bpy.types.Operator):
	bl_idname = "pose.rename_bone_regular_expression"
	bl_label = "ボーン名を正規表現で置換"
	bl_description = "(選択中の)ボーン名を正規表現に一致する部分で置換します"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAll = bpy.props.BoolProperty(name="非選択も含め全て", default=False)
	pattern = bpy.props.StringProperty(name="置換前(正規表現)", default="^")
	repl = bpy.props.StringProperty(name="置換後", default="@")
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "ARMATURE"):
			if (obj.mode == "POSE"):
				bones = context.selected_pose_bones
				if (self.isAll):
					bones = obj.pose.bones
				for bone in bones:
					bone.name = re.sub(self.pattern, self.repl, bone.name)
			else:
				self.report(type={"ERROR"}, message="ポーズモードで実行してください")
				return {'CANCELLED'}
		else:
			self.report(type={"ERROR"}, message="アーマチュアオブジェクトではありません")
			return {'CANCELLED'}
		return {'FINISHED'}

class SetSlowParentBone(bpy.types.Operator):
	bl_idname = "pose.set_slow_parent_bone"
	bl_label = "スローペアレントを設定"
	bl_description = "選択中のボーンにスローペアレントを設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('DAMPED_TRACK', "減衰トラック", "", 1),
		('IK', "IK", "", 2),
		('STRETCH_TO', "ストレッチ", "", 3),
		('COPY_LOCATION', "位置コピー", "", 4),
		]
	constraint = bpy.props.EnumProperty(items=items, name="コンストレイント")
	radius = bpy.props.FloatProperty(name="エンプティの大きさ", default=0.5, min=0.01, max=10, soft_min=0.01, soft_max=10, step=10, precision=3)
	slow_parent_offset = bpy.props.FloatProperty(name="スローペアレントの強度", default=5, min=0, max=100, soft_min=0, soft_max=100, step=50, precision=3)
	is_use_driver = bpy.props.BoolProperty(name="ボーンにドライバを追加", default=True)
	
	def execute(self, context):
		pre_cursor_location = context.space_data.cursor_location[:]
		pre_active_pose_bone = context.active_pose_bone
		obj = context.active_object
		arm = obj.data
		bones = context.selected_pose_bones[:]
		for bone in bones:
			if (not bone.parent):
				self.report(type={'WARNING'}, message="ボーン「"+bone.name+"」には親がありません、スルーします")
				continue
			if (self.constraint == 'COPY_LOCATION'):
				context.space_data.cursor_location = obj.matrix_world * arm.bones[bone.name].head_local
			else:
				context.space_data.cursor_location = obj.matrix_world * arm.bones[bone.name].tail_local
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.empty_add(type='PLAIN_AXES', radius=self.radius)
			empty_obj = context.active_object
			empty_obj.name = bone.name+" slow parent"
			obj.select = True
			context.scene.objects.active = obj
			bpy.ops.object.mode_set(mode='POSE')
			pre_parent_select = arm.bones[bone.parent.name].select
			arm.bones.active = arm.bones[bone.parent.name]
			bpy.ops.object.parent_set(type='BONE')
			arm.bones[bone.parent.name].select = pre_parent_select
			arm.bones.active = arm.bones[bone.name]
			empty_obj.use_slow_parent = True
			empty_obj.slow_parent_offset = self.slow_parent_offset
			const = bone.constraints.new(self.constraint)
			const.target = empty_obj
			if (self.constraint == 'IK'):
				const.chain_count = 1
			empty_obj.select = False
			if (self.is_use_driver):
				bone["SlowParentOffset"] = self.slow_parent_offset
				fcurve = empty_obj.driver_add('slow_parent_offset')
				fcurve.driver.type = 'AVERAGE'
				variable = fcurve.driver.variables.new()
				variable.targets[0].id = obj
				variable.targets[0].data_path = 'pose.bones["'+bone.name+'"]["SlowParentOffset"]'
		arm.bones.active = arm.bones[pre_active_pose_bone.name]
		context.space_data.cursor_location = pre_cursor_location[:]
		return {'FINISHED'}

class RenameBoneNameEnd(bpy.types.Operator):
	bl_idname = "pose.rename_bone_name_end"
	bl_label = "ボーン名の XXX.R => XXX_R を相互変換"
	bl_description = "ボーン名の XXX.R => XXX_R を相互変換します"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="XXX.R => XXX_R", default=False)
	
	def execute(self, context):
		if (not context.selected_pose_bones):
			self.report(type={"ERROR"}, message="ポーズモードでボーンを選択して実行して下さい")
			return {"CANCELLED"}
		rename_count = 0
		for bone in context.selected_pose_bones:
			pre_name = bone.name
			if (not self.reverse):
				bone.name = re.sub(r'_L$', '.L', bone.name)
				bone.name = re.sub(r'_l$', '.l', bone.name)
				if (pre_name != bone.name):
					continue
				bone.name = re.sub(r'_R$', '.R', bone.name)
				bone.name = re.sub(r'_r$', '.r', bone.name)
			else:
				bone.name = re.sub(r'\.L$', '_L', bone.name)
				bone.name = re.sub(r'\.l$', '_l', bone.name)
				if (pre_name != bone.name):
					continue
				bone.name = re.sub(r'\.R$', '_R', bone.name)
				bone.name = re.sub(r'\.r$', '_r', bone.name)
			if (pre_name != bone.name):
				rename_count += 1
		for area in context.screen.areas:
			area.tag_redraw()
		self.report(type={"INFO"}, message="ボーン名の変換が終了しました、"+str(rename_count)+"個変換しました")
		return {'FINISHED'}

class RenameBoneNameEndJapanese(bpy.types.Operator):
	bl_idname = "pose.rename_bone_name_end_japanese"
	bl_label = "ボーン名の XXX.R => 右XXX を相互変換"
	bl_description = "ボーン名の XXX.R => 右XXX を相互変換します"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="XXX.R => 右XXX", default=False)
	
	def execute(self, context):
		if (not context.selected_pose_bones):
			self.report(type={"ERROR"}, message="ポーズモードでボーンを選択して実行して下さい")
			return {"CANCELLED"}
		rename_count = 0
		for bone in context.selected_pose_bones:
			pre_name = bone.name
			if (not self.reverse):
				if (re.search(r"[\._][rR]$", bone.name)):
					bone.name = "右" + bone.name[:-2]
				if (re.search(r"[\._][lL]$", bone.name)):
					bone.name = "左" + bone.name[:-2]
			else:
				if (re.search(r"^右", bone.name)):
					bone.name = bone.name[1:] + "_R"
				if (re.search(r"^左", bone.name)):
					bone.name = bone.name[1:] + "_L"
			if (pre_name != bone.name):
				rename_count += 1
		for area in context.screen.areas:
			area.tag_redraw()
		self.report(type={"INFO"}, message="ボーン名の変換が終了しました、"+str(rename_count)+"個変換しました")
		return {'FINISHED'}

class TogglePosePosition(bpy.types.Operator):
	bl_idname = "pose.toggle_pose_position"
	bl_label = "ポーズ位置を切り替え"
	bl_description = "アーマチュアのポーズ位置/レスト位置を切り替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		if (context.object.type != 'ARMATURE'):
			self.report(type={"ERROR"}, message="アーマチュアで実行して下さい")
			return {"CANCELLED"}
		if (context.object.data.pose_position == 'POSE'):
			context.object.data.pose_position = 'REST'
		else:
			context.object.data.pose_position = 'POSE'
		return {'FINISHED'}

class CopyConstraintsMirror(bpy.types.Operator):
	bl_idname = "pose.copy_constraints_mirror"
	bl_label = "対のボーンにコンストレイントをコピー"
	bl_description = "「X.L」なら「X.R」、「X.R」なら「X.L」の名前のボーンへとコンストレイントをコピーします"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		def GetMirrorBoneName(name):
			new_name = re.sub(r'([\._])L$', r"\1R", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])l$', r"\1r", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])R$', r"\1L", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])r$', r"\1l", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])L([\._]\d+)$', r"\1R\2", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])l([\._]\d+)$', r"\1r\2", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])R([\._]\d+)$', r"\1L\2", name)
			if (new_name != name): return new_name
			new_name = re.sub(r'([\._])r([\._]\d+)$', r"\1l\2", name)
			if (new_name != name): return new_name
			return name
		for bone in context.selected_pose_bones:
			try:
				mirror_bone = context.active_object.pose.bones[GetMirrorBoneName(bone.name)]
			except KeyError:
				self.report(type={"WARNING"}, message=bone.name+"の対になるボーンが存在しないので無視します")
				continue
			if (bone.name == mirror_bone.name):
				self.report(type={"WARNING"}, message=bone.name+"はミラーに対応した名前ではありません、無視します")
				continue
			for const in mirror_bone.constraints[:]:
				mirror_bone.constraints.remove(const)
			for const in bone.constraints[:]:
				new_const = mirror_bone.constraints.new(const.type)
				for value_name in dir(new_const):
					if (value_name[0] != '_'):
						try:
							new_const.__setattr__(value_name, const.__getattribute__(value_name))
						except AttributeError:
							continue
				try:
					new_const.subtarget
				except AttributeError:
					continue
				new_const.subtarget = GetMirrorBoneName(new_const.subtarget)
		pre_mode = context.mode
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class RemoveBoneNameSerialNumbers(bpy.types.Operator):
	bl_idname = "pose.remove_bone_name_serial_numbers"
	bl_label = "ボーン名の連番を削除"
	bl_description = "「X.001」など、連番の付いたボーン名から数字を取り除くのを試みます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for bone in context.selected_pose_bones:
			bone.name = re.sub(r'\.\d+$', "", bone.name)
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class SetRigidBodyBone(bpy.types.Operator):
	bl_idname = "pose.set_rigid_body_bone"
	bl_label = "物理演算を設定"
	bl_description = "選択中の繋がったボーン群に、RigidBodyによる物理演算を設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	shape_size = bpy.props.FloatProperty(name="シェイプサイズ", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	shape_level = bpy.props.IntProperty(name="シェイプの細分化", default=3, min=1, max=6, soft_min=1, soft_max=6)
	constraints_size = bpy.props.FloatProperty(name="剛体コンストレイントサイズ", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	items = [
		('PLAIN_AXES', "十字", "", 1),
		('ARROWS', "座標軸", "", 2),
		('SINGLE_ARROW', "矢印", "", 3),
		('CIRCLE', "円", "", 4),
		('CUBE', "立方体", "", 5),
		('SPHERE', "球", "", 6),
		('CONE', "円錐", "", 7),
		('IMAGE', "画像", "", 8),
		]
	empty_draw_type = bpy.props.EnumProperty(items=items, name="剛体コンストレイント表示", default='SPHERE')
	is_parent_shape = bpy.props.BoolProperty(name="剛体コンストレイントをシェイプに追尾", default=False)
	rot_limit = bpy.props.FloatProperty(name="回転制限", default=90, min=0, max=360, soft_min=0, soft_max=360, step=1, precision=3)
	linear_damping = bpy.props.FloatProperty(name="減衰：移動", default=0.04, min=0, max=1, soft_min=0, soft_max=1, step=1, precision=3)
	angular_damping = bpy.props.FloatProperty(name="減衰：回転", default=0.1, min=0, max=1, soft_min=0, soft_max=1, step=1, precision=3)
	
	def execute(self, context):
		pre_active_obj = context.active_object
		if (not pre_active_obj):
			self.report(type={'ERROR'}, message="アクティブオブジェクトがありません")
			return {'CANCELLED'}
		if (pre_active_obj.type != 'ARMATURE'):
			self.report(type={'ERROR'}, message="アーマチュアオブジェクトで実行して下さい")
			return {'CANCELLED'}
		pre_mode = pre_active_obj.mode
		if (pre_mode != 'POSE'):
			self.report(type={'ERROR'}, message="ポーズモードで実行して下さい")
			return {'CANCELLED'}
		pre_cursor_location = context.space_data.cursor_location[:]
		arm_obj = pre_active_obj
		arm = arm_obj.data
		bone_names = []
		for bone in context.selected_pose_bones:
			bone_names.append(bone.name)
		no_parent_count = 0
		no_parent_bone = None
		base_bone = None
		bones = []
		for bone in context.selected_pose_bones:
			if (bone.parent):
				if (not bone.parent.name in bone_names):
					no_parent_bone = bone
					base_bone = bone.parent
					no_parent_count += 1
			else:
				no_parent_bone = bone
				no_parent_count += 1
			bones.append(bone)
		if (no_parent_count != 1):
			self.report(type={'ERROR'}, message="一連の繋がったボーンを選択して実行して下さい")
			return {'CANCELLED'}
		bpy.ops.object.mode_set(mode='OBJECT')
		base_obj = None
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=self.shape_level, size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
		obj = context.active_object
		bpy.ops.rigidbody.object_add()
		obj.rigid_body.enabled = False
		obj.rigid_body.kinematic = True
		obj.rigid_body.linear_damping = self.linear_damping
		obj.rigid_body.angular_damping = self.angular_damping
		const = obj.constraints.new('COPY_TRANSFORMS')
		const.target = arm_obj
		if (base_bone):
			const.subtarget = base_bone.name
		const.head_tail = 0.5
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.ops.object.visual_transform_apply()
		obj.constraints.remove(const)
		if (base_bone):
			bone = arm.bones[base_bone.name]
			obj.scale.y = (bone.head_local - bone.tail_local).length * 0.5
			obj.scale.x, obj.scale.z = self.shape_size, self.shape_size
		else:
			obj.scale.x, obj.scale.y, obj.scale.z = self.shape_size, self.shape_size, self.shape_size
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		obj.draw_type = 'WIRE'
		arm_obj.select = True
		context.scene.objects.active = arm_obj
		if (base_bone):
			arm.bones.active = arm.bones[bone.name]
			bpy.ops.object.mode_set(mode='POSE')
			bpy.ops.object.parent_set(type='BONE')
		else:
			bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
		bpy.ops.object.mode_set(mode='OBJECT')
		base_obj = obj
		base_obj.name = "剛体基点"
		pairs = []
		for bone in bones:
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=self.shape_level, size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
			obj = context.active_object
			const = obj.constraints.new('COPY_TRANSFORMS')
			const.target = arm_obj
			const.subtarget = bone.name
			const.head_tail = 0.5
			bpy.ops.object.select_all(action='DESELECT')
			obj.select = True
			bpy.ops.object.visual_transform_apply()
			obj.constraints.remove(const)
			bone = arm.bones[bone.name]
			obj.scale.y = (bone.head_local - bone.tail_local).length * 0.5
			obj.scale.x, obj.scale.z = self.shape_size, self.shape_size
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			obj.draw_type = 'WIRE'
			const = arm_obj.pose.bones[bone.name].constraints.new('DAMPED_TRACK')
			const.target = obj
			obj.name = "剛体"
			shape = obj
			bpy.ops.rigidbody.object_add()
			
			shape.rigid_body.linear_damping = self.linear_damping
			shape.rigid_body.angular_damping = self.angular_damping
			
			bpy.ops.object.empty_add(type=self.empty_draw_type, radius=1, view_align=False, location=(0, 0, 0))
			obj = context.active_object
			const = obj.constraints.new('COPY_TRANSFORMS')
			const.target = arm_obj
			const.subtarget = bone.name
			bpy.ops.object.select_all(action='DESELECT')
			obj.select = True
			bpy.ops.object.visual_transform_apply()
			obj.constraints.remove(const)
			obj.scale = (self.constraints_size, self.constraints_size, self.constraints_size)
			bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
			obj.name = "剛体コンストレイント"
			
			bpy.ops.rigidbody.constraint_add()
			obj.rigid_body_constraint.type = 'GENERIC'
			obj.rigid_body_constraint.use_limit_lin_x = True
			obj.rigid_body_constraint.limit_lin_x_lower = 0
			obj.rigid_body_constraint.limit_lin_x_upper = 0
			obj.rigid_body_constraint.use_limit_lin_y = True
			obj.rigid_body_constraint.limit_lin_y_lower = 0
			obj.rigid_body_constraint.limit_lin_y_upper = 0
			obj.rigid_body_constraint.use_limit_lin_z = True
			obj.rigid_body_constraint.limit_lin_z_lower = 0
			obj.rigid_body_constraint.limit_lin_z_upper = 0
			
			bpy.context.object.rigid_body_constraint.use_limit_ang_x = True
			bpy.context.object.rigid_body_constraint.limit_ang_x_lower = math.radians(self.rot_limit) * -1
			bpy.context.object.rigid_body_constraint.limit_ang_x_upper = math.radians(self.rot_limit)
			bpy.context.object.rigid_body_constraint.use_limit_ang_y = True
			bpy.context.object.rigid_body_constraint.limit_ang_y_lower = 0
			bpy.context.object.rigid_body_constraint.limit_ang_y_upper = 0
			bpy.context.object.rigid_body_constraint.use_limit_ang_z = True
			bpy.context.object.rigid_body_constraint.limit_ang_z_lower = math.radians(self.rot_limit) * -1
			bpy.context.object.rigid_body_constraint.limit_ang_z_upper = math.radians(self.rot_limit)
			
			pairs.append((bone, shape, obj))
		for bone, shape, const in pairs:
			const.rigid_body_constraint.object1 = shape
			
			bpy.ops.object.select_all(action='DESELECT')
			const.select = True
			arm_obj.select = True
			context.scene.objects.active = arm_obj
			if (bone.parent):
				if (bone.parent.name in bone_names):
					for a, b, c in pairs:
						if (bone.parent.name == a.name):
							const.rigid_body_constraint.object2 = b
							arm.bones.active = arm.bones[bone.parent.name]
							break
				else:
					const.rigid_body_constraint.object2 = base_obj
			else:
				const.rigid_body_constraint.object2 = base_obj
			if (self.is_parent_shape):
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.object.parent_set(type='BONE')
				bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		pre_active_obj.select = True
		context.scene.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

class SetIKRotationLimitByPose(bpy.types.Operator):
	bl_idname = "pose.set_ik_rotation_limit_by_pose"
	bl_label = "現ポーズを回転制限に"
	bl_description = "現在のボーンの回転状態を、IKやコンストレイントの回転制限へと設定します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('IK', "IKの回転制限", "", 1),
		('CONST', "コンストレイントの回転制限", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード")
	use_reverse = bpy.props.BoolProperty(name="制限の反転", default=True)
	use_x = bpy.props.BoolProperty(name="X軸の制限", default=True)
	use_y = bpy.props.BoolProperty(name="Y軸の制限", default=True)
	use_z = bpy.props.BoolProperty(name="Z軸の制限", default=True)
	is_clear_rot = bpy.props.BoolProperty(name="ポーズの回転をリセット", default=True)
	
	def execute(self, context):
		pre_active_obj = context.active_object
		if (not pre_active_obj):
			self.report(type={'ERROR'}, message="アクティブオブジェクトがありません")
			return {'CANCELLED'}
		if (pre_active_obj.type != 'ARMATURE'):
			self.report(type={'ERROR'}, message="アーマチュアオブジェクトで実行して下さい")
			return {'CANCELLED'}
		pre_mode = pre_active_obj.mode
		if (pre_mode != 'POSE'):
			self.report(type={'ERROR'}, message="ポーズモードで実行して下さい")
			return {'CANCELLED'}
		for bone in context.selected_pose_bones:
			pre_rotation_mode = bone.rotation_mode
			bone.rotation_mode = 'ZYX'
			rot = bone.rotation_euler.copy()
			bone.rotation_mode = pre_rotation_mode
			print(rot)
			if (self.mode == 'IK'):
				if (self.use_x):
					bone.use_ik_limit_x = True
					if (0 <= rot.x):
						bone.ik_max_x = rot.x
						if (self.use_reverse): bone.ik_min_x = -rot.x
					else:
						bone.ik_min_x = rot.x
						if (self.use_reverse): bone.ik_max_x = -rot.x
				if (self.use_y):
					bone.use_ik_limit_y = True
					if (0 <= rot.y):
						bone.ik_max_y = rot.y
						if (self.use_reverse): bone.ik_min_y = -rot.y
					else:
						bone.ik_min_y = rot.y
						if (self.use_reverse): bone.ik_max_y = -rot.y
				if (self.use_z):
					bone.use_ik_limit_z = True
					if (0 <= rot.z):
						bone.ik_max_z = rot.z
						if (self.use_reverse): bone.ik_min_z = -rot.z
					else:
						bone.ik_min_z = rot.z
						if (self.use_reverse): bone.ik_max_z = -rot.z
			elif (self.mode == 'CONST'):
				rot_const = None
				for const in bone.constraints:
					if (const.type == 'LIMIT_ROTATION'):
						rot_const = const
				if (not rot_const):
					rot_const = bone.constraints.new('LIMIT_ROTATION')
				rot_const.owner_space = 'LOCAL'
				if (self.use_x):
					rot_const.use_limit_x = True
					if (0 <= rot.x):
						rot_const.max_x = rot.x
						if (self.use_reverse): rot_const.min_x = -rot.x
					else:
						rot_const.min_x = rot.x
						if (self.use_reverse): rot_const.max_x = -rot.x
				if (self.use_y):
					rot_const.use_limit_y = True
					if (0 <= rot.y):
						rot_const.max_y = rot.y
						if (self.use_reverse): rot_const.min_y = -rot.y
					else:
						rot_const.min_y = rot.y
						if (self.use_reverse): rot_const.max_y = -rot.y
				if (self.use_z):
					rot_const.use_limit_z = True
					if (0 <= rot.z):
						rot_const.max_z = rot.z
						if (self.use_reverse): rot_const.min_z = -rot.z
					else:
						rot_const.min_z = rot.z
						if (self.use_reverse): rot_const.max_z = -rot.z
		if (self.is_clear_rot):
			bpy.ops.pose.rot_clear()
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class BoneNameMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_pose_specials_bone_name"
	bl_label = "ボーン名"
	bl_description = "ボーン名に関する機能のメニューです"
	
	def draw(self, context):
		self.layout.operator(CopyBoneName.bl_idname, icon="PLUGIN")
		self.layout.operator(RenameBoneRegularExpression.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RemoveBoneNameSerialNumbers.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RenameBoneNameEnd.bl_idname, text="ボーン名置換「XXX_R => XXX.R」", icon="PLUGIN").reverse = False
		self.layout.operator(RenameBoneNameEnd.bl_idname, text="ボーン名置換「XXX.R => XXX_R」", icon="PLUGIN").reverse = True
		self.layout.separator()
		self.layout.operator(RenameBoneNameEndJapanese.bl_idname, text="ボーン名置換「XXX_R => 右XXX」", icon="PLUGIN").reverse = False
		self.layout.operator(RenameBoneNameEndJapanese.bl_idname, text="ボーン名置換「右XXX => XXX_R」", icon="PLUGIN").reverse = True

class SpecialsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_pose_specials_specials"
	bl_label = "特殊処理"
	bl_description = "特殊な処理に関する機能のメニューです"
	
	def draw(self, context):
		self.layout.operator(SplineGreasePencil.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CreateCustomShape.bl_idname, icon="PLUGIN")
		self.layout.operator(CreateWeightCopyMesh.bl_idname, icon="PLUGIN")
		self.layout.operator(SetSlowParentBone.bl_idname, icon="PLUGIN")
		self.layout.operator(SetRigidBodyBone.bl_idname, icon="PLUGIN")
		self.layout.operator(SetIKRotationLimitByPose.bl_idname, icon="PLUGIN")

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
		self.layout.menu(BoneNameMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(CopyConstraintsMirror.bl_idname, icon="PLUGIN")
		self.layout.separator()
		text = "ポーズ位置を切り替え (現在：レスト位置)"
		if (context.object.data.pose_position == 'POSE'):
			text = "ポーズ位置を切り替え (現在：ポーズ位置)"
		self.layout.operator(TogglePosePosition.bl_idname, text=text, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(SpecialsMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
