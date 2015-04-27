# 3Dビュー > オブジェクトモード > 「W」キー

import bpy, bmesh, mathutils
import re, random

################
# オペレーター #
################

class CopyObjectName(bpy.types.Operator):
	bl_idname = "object.copy_object_name"
	bl_label = "Copy the name of the object to the clipboard"
	bl_description = "I will copy the name of the active object to the clipboard"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.window_manager.clipboard = context.active_object.name
		return {'FINISHED'}

class RenameObjectRegularExpression(bpy.types.Operator):
	bl_idname = "object.rename_object_regular_expression"
	bl_label = "Replace object name in the regular expression"
	bl_description = "I will replace the name of the object being selected in the regular expression"
	bl_options = {'REGISTER', 'UNDO'}
	
	pattern = bpy.props.StringProperty(name="Before replacement (regular expression)", default="")
	repl = bpy.props.StringProperty(name="After substitution", default="")
	
	def execute(self, context):
		for obj in context.selected_objects:
			obj.name = re.sub(self.pattern, self.repl, obj.name)
		return {'FINISHED'}

class EqualizeObjectNameAndDataName(bpy.types.Operator):
	bl_idname = "object.equalize_objectname_and_dataname"
	bl_label = "I to have the same object name and the data name"
	bl_description = "I should be the same object name and the data name of the currently selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj and obj.data):
				obj.data.name = obj.name
		return {'FINISHED'}

class AddVertexColorSelectedObject(bpy.types.Operator):
	bl_idname = "object.add_vertex_color_selected_object"
	bl_label = "Collectively add vertices color"
	bl_description = "Add the vertex color to all mesh objects in the selection by specifying the color and name"
	bl_options = {'REGISTER', 'UNDO'}
	
	name = bpy.props.StringProperty(name="Vertex color name", default="Col")
	color = bpy.props.FloatVectorProperty(name="Vertex color", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				me = obj.data
				try:
					col = me.vertex_colors[self.name]
				except KeyError:
					col = me.vertex_colors.new(self.name)
				for data in col.data:
					data.color = self.color
		return {'FINISHED'}

class CreateRopeMesh(bpy.types.Operator):
	bl_idname = "object.create_rope_mesh"
	bl_label = "Create a rope-like mesh from the curve"
	bl_description = "The mesh such as rope and snake along the active curve object to create a new"
	bl_options = {'REGISTER', 'UNDO'}
	
	vertices = bpy.props.IntProperty(name="Vertices", default=32, min=3, soft_min=3, max=999, soft_max=999, step=1)
	radius = bpy.props.FloatProperty(name="Radius", default=0.1, step=1, precision=3, min=0, soft_min=0, max=99, soft_max=99)
	number_cuts = bpy.props.IntProperty(name="Division", default=32, min=2, soft_min=2, max=999, soft_max=999, step=1)
	resolution_u = bpy.props.IntProperty(name="Resolution", default=64, min=1, soft_min=1, max=999, soft_max=999, step=1)
	
	def execute(self, context):
		for obj in context.selected_objects:
			activeObj = obj
			context.scene.objects.active = obj
			pre_use_stretch = activeObj.data.use_stretch
			pre_use_deform_bounds = activeObj.data.use_deform_bounds
			bpy.ops.object.transform_apply_all()
			
			bpy.ops.mesh.primitive_cylinder_add(vertices=self.vertices, radius=self.radius, depth=1, end_fill_type='NOTHING', view_align=False, enter_editmode=True, location=(0, 0, 0), rotation=(0, 1.5708, 0))
			bpy.ops.mesh.select_all(action='DESELECT')
			context.tool_settings.mesh_select_mode = [False, True, False]
			bpy.ops.mesh.select_non_manifold()
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.mesh.subdivide(number_cuts=self.number_cuts, smoothness=0)
			bpy.ops.object.mode_set(mode='OBJECT')
			
			meshObj = context.active_object
			modi = meshObj.modifiers.new("temp", 'CURVE')
			modi.object = activeObj
			activeObj.data.use_stretch = True
			activeObj.data.use_deform_bounds = True
			activeObj.data.resolution_u = self.resolution_u
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modi.name)
			
			activeObj.data.use_stretch = pre_use_stretch
			activeObj.data.use_deform_bounds = pre_use_deform_bounds
		return {'FINISHED'}

class VertexGroupTransferWeightObjmode(bpy.types.Operator):
	bl_idname = "object.vertex_group_transfer_weight_objmode"
	bl_label = "Weight transfer"
	bl_description = "I will transfer the weight painting to active from the mesh in other selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	isDeleteWeights = bpy.props.BoolProperty(name="Since the weight all Delete", default=True)
	items = [
		('WT_BY_INDEX', "Index number of vertices", "", 1),
		('WT_BY_NEAREST_VERTEX', "Nearest vertex", "", 2),
		('WT_BY_NEAREST_FACE', "Nearest face", "", 3),
		('WT_BY_NEAREST_VERTEX_IN_FACE', "The nearest vertex in the plane", "", 4),
		]
	method = bpy.props.EnumProperty(items=items, name="Method", default="WT_BY_NEAREST_VERTEX")
	
	def execute(self, context):
		if (self.isDeleteWeights):
			try:
				bpy.ops.object.vertex_group_remove(all=True)
			except RuntimeError:
				pass
		bpy.ops.object.vertex_group_transfer_weight(group_select_mode='WT_REPLACE_ALL_VERTEX_GROUPS', method=self.method, replace_mode='WT_REPLACE_ALL_WEIGHTS')
		return {'FINISHED'}

class AddGreasePencilPathMetaballs(bpy.types.Operator):
	bl_idname = "object.add_grease_pencil_path_metaballs"
	bl_label = "The Blobby placed in grease pencil"
	bl_description = "Place the metaballs along the active grease pencil"
	bl_options = {'REGISTER', 'UNDO'}
	
	dissolve_verts_count = bpy.props.IntProperty(name="Density", default=3, min=1, max=100, soft_min=1, soft_max=100, step=1)
	radius = bpy.props.FloatProperty(name="Meta ball size", default=0.05, min=0, max=1, soft_min=0, soft_max=1, step=0.2, precision=3)
	resolution = bpy.props.FloatProperty(name="Blobby resolution", default=0.05, min=0.001, max=1, soft_min=0.001, soft_max=1, step=0.2, precision=3)
	
	def execute(self, context):
		if (not context.scene.grease_pencil.layers.active):
			self.report(type={"ERROR"}, message="Grease pencil layer does not exist")
			return {"CANCELLED"}
		pre_selectable_objects = context.selectable_objects
		bpy.ops.gpencil.convert(type='CURVE', use_normalize_weights=False, use_link_strokes=False, use_timing_data=True)
		for obj in context.selectable_objects:
			if (not obj in pre_selectable_objects):
				curveObj = obj
				break
		bpy.ops.object.select_all(action='DESELECT')
		curveObj.select = True
		context.scene.objects.active = curveObj
		curveObj.data.resolution_u = 1
		bpy.ops.object.convert(target='MESH', keep_original=False)
		pathObj = context.scene.objects.active
		for vert in pathObj.data.vertices:
			if (vert.index % self.dissolve_verts_count == 0):
				vert.select = False
			else:
				vert.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.dissolve_verts()
		bpy.ops.object.mode_set(mode='OBJECT')
		metas = []
		for vert in pathObj.data.vertices:
			bpy.ops.object.metaball_add(type='BALL', radius=self.radius, view_align=False, enter_editmode=False, location=vert.co)
			metas.append(context.scene.objects.active)
			metas[-1].data.resolution = self.resolution
		for obj in metas:
			obj.select = True
		context.scene.objects.unlink(pathObj)
		return {'FINISHED'}

class CreateVertexToMetaball(bpy.types.Operator):
	bl_idname = "object.create_vertex_to_metaball"
	bl_label = "And hook the metaballs to vertex"
	bl_description = "The top portion of the mesh objects in the selection I will not stick a new metaballs"
	bl_options = {'REGISTER', 'UNDO'}
	
	name = bpy.props.StringProperty(name="Blobby name", default="Mball")
	size = bpy.props.FloatProperty(name="Size", default=0.1, min=0.001, max=10, soft_min=0.001, soft_max=10, step=1, precision=3)
	resolution = bpy.props.FloatProperty(name="Resolution", default=0.1, min=0.001, max=10, soft_min=0.001, soft_max=10, step=0.5, precision=3)
	isUseVg = bpy.props.BoolProperty(name="To the vertex group size", default=False)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				me = obj.data
				metas = []
				active_vg_index = obj.vertex_groups.active_index
				for i in range(len(me.vertices)):
					multi = 1.0
					if (self.isUseVg):
						for element in me.vertices[i].groups:
							if (element.group == active_vg_index):
								multi = element.weight
								break
					meta = bpy.data.metaballs.new(self.name)
					metas.append( bpy.data.objects.new(self.name, meta) )
					meta.elements.new()
					meta.update_method = 'NEVER'
					meta.resolution = self.resolution
					metas[-1].name = self.name
					size = self.size * multi
					metas[-1].scale = (size, size, size)
					metas[-1].parent = obj
					metas[-1].parent_type = 'VERTEX'
					metas[-1].parent_vertices = (i, 0, 0)
				bpy.ops.object.select_all(action='DESELECT')
				for meta in metas:
					context.scene.objects.link(meta)
					meta.select = True
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
				metas[-1].parent_type = metas[-1].parent_type
				base_obj = metas[0] #context.scene.objects[re.sub(r'\.\d+$', '', metas[0].name)]
				context.scene.objects.active = base_obj
				base_obj.data.update_method = 'UPDATE_ALWAYS'
				#context.scene.update()
		return {'FINISHED'}

class ToggleSmooth(bpy.types.Operator):
	bl_idname = "object.toggle_smooth"
	bl_label = "Switch the smooth / flat"
	bl_description = "I will switch the smooth / flat state of mesh objects in the selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		activeObj = context.active_object
		if (activeObj.type == 'MESH'):
			me = activeObj.data
			is_smoothed = False
			if (1 <= len(me.polygons)):
				if (me.polygons[0].use_smooth):
					is_smoothed = True
			for obj in context.selected_objects:
				if (is_smoothed):
					bpy.ops.object.shade_flat()
				else:
					bpy.ops.object.shade_smooth()
		else:
			self.report(type={"ERROR"}, message="Run it from the mesh object to the active")
			return {'CANCELLED'}
		if (is_smoothed):
			self.report(type={"INFO"}, message="I have a mesh object to flat")
		else:
			self.report(type={"INFO"}, message="I have a mesh object smoothly")
		return {'FINISHED'}

class SetRenderHide(bpy.types.Operator):
	bl_idname = "object.set_render_hide"
	bl_label = "Limit rendering of selections"
	bl_description = "You set not to render the objects in the selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Not rendering", default=True)
	
	def execute(self, context):
		for obj in context.selected_objects:
			obj.hide_render = self.reverse
		return {'FINISHED'}

class SyncRenderHide(bpy.types.Operator):
	bl_idname = "object.sync_render_hide"
	bl_label = "Sync whether to render the Show / Hide"
	bl_description = "Synchronize with the show / hide state whether to render the objects in the current layer"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAll = bpy.props.BoolProperty(name="All objects", default=False)
	
	def execute(self, context):
		objs = []
		for obj in bpy.data.objects:
			if (self.isAll):
				objs.append(obj)
			else:
				for i in range(len(context.scene.layers)):
					if (context.scene.layers[i] and obj.layers[i]):
						objs.append(obj)
						break
		for obj in objs:
			obj.hide_render = obj.hide
		return {'FINISHED'}

class SetHideSelect(bpy.types.Operator):
	bl_idname = "object.set_hide_select"
	bl_label = "And limit the choice of selections"
	bl_description = "I will not be able to select the object in the selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Dimmed", default=True)
	
	def execute(self, context):
		for obj in context.selected_objects:
			obj.hide_select = self.reverse
			if (self.reverse):
				obj.select = not self.reverse
		return {'FINISHED'}

class SetUnselectHideSelect(bpy.types.Operator):
	bl_idname = "object.set_unselect_hide_select"
	bl_label = "And limit the choice of the non-selected products"
	bl_description = "I will not be able to select an object other than the selected products"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Dimmed", default=True)
	
	def execute(self, context):
		for obj in bpy.data.objects:
			for i in range(len(context.scene.layers)):
				if (obj.layers[i] and context.scene.layers[i]):
					if (not obj.select):
						obj.hide_select = self.reverse
		return {'FINISHED'}

class AllResetHideSelect(bpy.types.Operator):
	bl_idname = "object.all_reset_hide_select"
	bl_label = "Clear all selected limit"
	bl_description = "Deselect Disable setting of all objects (vice versa)"
	bl_options = {'REGISTER', 'UNDO'}
	
	reverse = bpy.props.BoolProperty(name="Dimmed", default=False)
	
	def execute(self, context):
		for obj in bpy.data.objects:
			obj.hide_select = self.reverse
			if (self.reverse):
				obj.select = not self.reverse
		return {'FINISHED'}

class VertexGroupTransfer(bpy.types.Operator):
	bl_idname = "object.vertex_group_transfer"
	bl_label = "Transfer of vertex group"
	bl_description = "I will transfer the vertex group of other selected mesh to the active mesh"
	bl_options = {'REGISTER', 'UNDO'}
	
	vertex_group_remove_all = bpy.props.BoolProperty(name="First vertex group Delete all", default=False)
	vertex_group_clean = bpy.props.BoolProperty(name="Clean vertex group", default=True)
	vertex_group_delete = bpy.props.BoolProperty(name="No vertex group Delete the allocation", default=True)
	
	def execute(self, context):
		if (context.active_object.type != 'MESH'):
			self.report(type={'ERROR'}, message="Run in the active state mesh object")
			return {'CANCELLED'}
		source_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH' and context.active_object.name != obj.name):
				source_objs.append(obj)
		if (len(source_objs) <= 0):
			self.report(type={'ERROR'}, message="Please run in the selected state the mesh object two or more")
			return {'CANCELLED'}
		if (0 < len(context.active_object.vertex_groups) and self.vertex_group_remove_all):
			bpy.ops.object.vertex_group_remove(all=True)
		me = context.active_object.data
		vert_mapping = 'NEAREST'
		for obj in source_objs:
			if (len(obj.data.polygons) <= 0):
				for obj2 in source_objs:
					if (len(obj.data.edges) <= 0):
						break
				else:
					vert_mapping = 'EDGEINTERP_NEAREST'
				break
		else:
			vert_mapping = 'POLYINTERP_NEAREST'
		bpy.ops.object.data_transfer(use_reverse_transfer=True, data_type='VGROUP_WEIGHTS', use_create=True, vert_mapping=vert_mapping, layers_select_src = 'ALL', layers_select_dst = 'NAME')
		if (self.vertex_group_clean):
			bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0, keep_single=False)
		if (self.vertex_group_delete):
			bpy.ops.mesh.remove_empty_vertex_groups()
		return {'FINISHED'}

class CreateSolidifyEdge(bpy.types.Operator):
	bl_idname = "object.create_solidify_edge"
	bl_label = "Contour lines generated by the thickness with modifier"
	bl_description = "I'll add a contour drawing by the thickness with modifier to the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_render = bpy.props.BoolProperty(name="Also be applied to the rendering", default=False)
	thickness = bpy.props.FloatProperty(name="Thickness of the outline", default=0.01, min=0, max=1, soft_min=0, soft_max=1, step=0.1, precision=3)
	color = bpy.props.FloatVectorProperty(name="Color of the line", default=(0.0, 0.0, 0.0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	use_rim = bpy.props.BoolProperty(name="I put a face to the edge", default=False)
	show_backface_culling = bpy.props.BoolProperty(name="And on the hide the back", default=True)
	
	def execute(self, context):
		pre_active_obj = context.active_object
		selected_objs = []
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				selected_objs.append(obj)
			else:
				self.report(type={'INFO'}, message=obj.name+"I will ignore because it is not a mesh object")
		if (len(selected_objs) <= 0):
			self.report(type={'ERROR'}, message="Run in a state of selecting the one or more mesh object")
			return {'CANCELLED'}
		for obj in selected_objs:
			pre_mtls = []
			for i in obj.material_slots:
				if (i.material):
					pre_mtls.append(i)
			if (len(pre_mtls) <= 0):
				self.report(type={'WARNING'}, message=obj.name+"I ignored because material is not assigned to")
				continue
			context.scene.objects.active = obj
			
			mtl = bpy.data.materials.new(obj.name+"Of contour lines")
			mtl.use_shadeless = True
			mtl.diffuse_color = self.color
			mtl.use_nodes = True
			mtl.use_transparency = True
			
			for n in mtl.node_tree.nodes:
				if (n.bl_idname == 'ShaderNodeMaterial'):
					n.material = mtl
			node = mtl.node_tree.nodes.new('ShaderNodeGeometry')
			link_input = node.outputs[8]
			for n in mtl.node_tree.nodes:
				if (n.bl_idname == 'ShaderNodeOutput'):
					link_output = n.inputs[1]
			mtl.node_tree.links.new(link_input, link_output)
			
			slot_index = len(obj.material_slots)
			bpy.ops.object.material_slot_add()
			slot = obj.material_slots[-1]
			slot.material = mtl
			
			mod = obj.modifiers.new("Outline", 'SOLIDIFY')
			mod.use_flip_normals = True
			if (not self.use_rim):
				mod.use_rim = False
			mod.material_offset = slot_index
			mod.material_offset_rim = slot_index
			mod.offset = 1
			mod.thickness = self.thickness
			if (not self.use_render):
				mod.show_render = False
		context.scene.objects.active = pre_active_obj
		context.space_data.show_backface_culling = self.show_backface_culling
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class ApplyObjectColor(bpy.types.Operator):
	bl_idname = "object.apply_object_color"
	bl_label = "Object color Enable + color settings"
	bl_description = "Enable the object color of the selected object, you can set the color"
	bl_options = {'REGISTER', 'UNDO'}
	
	color = bpy.props.FloatVectorProperty(name="Color", default=(0, 0, 0), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	use_random = bpy.props.BoolProperty(name="I use a random color", default=True)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (self.use_random):
				col = mathutils.Color((0.0, 0.0, 1.0))
				col.s = 1.0
				col.v = 1.0
				col.h = random.random()
				obj.color = (col.r, col.g, col.b, 1)
			else:
				obj.color = (self.color[0], self.color[1], self.color[2], 1)
			for slot in obj.material_slots:
				if (slot.material):
					slot.material.use_object_color = True
		return {'FINISHED'}

class ClearObjectColor(bpy.types.Operator):
	bl_idname = "object.clear_object_color"
	bl_label = "Object color invalid + color settings"
	bl_description = "Disable the object color of the selected object, you can set the color"
	bl_options = {'REGISTER', 'UNDO'}
	
	set_color = bpy.props.BoolProperty(name="I set the color", default=False)
	color = bpy.props.FloatVectorProperty(name="Color", default=(1, 1, 1), min=0, max=1, soft_min=0, soft_max=1, step=10, precision=3, subtype='COLOR')
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (self.set_color):
				obj.color = (self.color[0], self.color[1], self.color[2], 1)
			for slot in obj.material_slots:
				if (slot.material):
					slot.material.use_object_color = False
		return {'FINISHED'}

class CreateMeshImitateArmature(bpy.types.Operator):
	bl_idname = "object.create_mesh_imitate_armature"
	bl_label = "Create an armature to imitate the deformation of the mesh"
	bl_description = "The armature to follow the deformation of the active mesh object I create a new"
	bl_options = {'REGISTER', 'UNDO'}
	
	bone_length = bpy.props.FloatProperty(name="Bone Length", default=0.1, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	use_normal = bpy.props.BoolProperty(name="Rotation to match the normal", default=False)
	add_edge = bpy.props.BoolProperty(name="Add bones to side", default=False)
	vert_bone_name = bpy.props.StringProperty(name="Bone names of vertex part", default="Vertex")
	edge_bone_name = bpy.props.StringProperty(name="Bone names of side portions", default="Side")
	
	def execute(self, context):
		pre_active_obj = context.active_object
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'INFO'}, message=obj.name+"I will ignore because it is not a mesh object")
				continue
			arm = bpy.data.armatures.new(obj.name+"Armature to the imitation")
			arm_obj = bpy.data.objects.new(obj.name+"Armature to the imitation", arm)
			context.scene.objects.link(arm_obj)
			context.scene.objects.active = arm_obj
			bpy.ops.object.mode_set(mode='EDIT')
			bone_names = []
			for vert in obj.data.vertices:
				bone = arm.edit_bones.new(self.vert_bone_name+str(vert.index))
				bone.head = obj.matrix_world * vert.co
				bone.tail = bone.head + (obj.matrix_world * vert.normal * self.bone_length)
				bone_names.append(bone.name)
			bpy.ops.object.mode_set(mode='OBJECT')
			for vert, name in zip(obj.data.vertices, bone_names):
				vg = obj.vertex_groups.new(name)
				vg.add([vert.index], 1.0, 'REPLACE')
				const = arm_obj.pose.bones[name].constraints.new('COPY_LOCATION')
				const.target = obj
				const.subtarget = vg.name
				if (self.use_normal):
					const_rot = arm_obj.pose.bones[name].constraints.new('COPY_ROTATION')
					const_rot.target = obj
					const_rot.subtarget = vg.name
			context.scene.objects.active = obj
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.object.mode_set(mode='OBJECT')
			context.scene.objects.active = arm_obj
			if (self.use_normal):
				bpy.ops.object.mode_set(mode='POSE')
				bpy.ops.pose.armature_apply()
				bpy.ops.object.mode_set(mode='OBJECT')
			if (self.add_edge):
				edge_bone_names = []
				bpy.ops.object.mode_set(mode='EDIT')
				for edge in obj.data.edges:
					vert0 = obj.data.vertices[edge.vertices[0]]
					vert1 = obj.data.vertices[edge.vertices[1]]
					bone = arm.edit_bones.new(self.edge_bone_name+str(edge.index))
					bone.head = obj.matrix_world * vert0.co
					bone.tail = obj.matrix_world * vert1.co
					bone.layers = (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
					bone.parent = arm.edit_bones[self.vert_bone_name + str(vert0.index)]
					edge_bone_names.append(bone.name)
				bpy.ops.object.mode_set(mode='OBJECT')
				arm.layers[1] = True
				for edge, name in zip(obj.data.edges, edge_bone_names):
					const = arm_obj.pose.bones[name].constraints.new('STRETCH_TO')
					const.target = arm_obj
					const.subtarget = self.vert_bone_name + str(edge.vertices[1])
		context.scene.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}

class CreateVertexGroupsArmature(bpy.types.Operator):
	bl_idname = "object.create_vertex_groups_armature"
	bl_label = "The bone created vertex position where there is a vertex group"
	bl_description = "The vertex position the vertex group of selected objects have been assigned, I will create a bone of the vertex group name"
	bl_options = {'REGISTER', 'UNDO'}
	
	armature_name = bpy.props.StringProperty(name="The name of the armature", default="Armature")
	use_vertex_group_name = bpy.props.BoolProperty(name="Bone name to vertex group name", default=True)
	bone_length = bpy.props.FloatProperty(name="The length of the bone", default=0.5, min=0, max=10, soft_min=0, soft_max=10, step=1, precision=3)
	
	def execute(self, context):
		pre_active_obj = context.active_object
		if (not pre_active_obj):
			self.report(type={'ERROR'}, message="There is no active object")
			return {'CANCELLED'}
		pre_mode = pre_active_obj.mode
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'INFO'}, message=obj.name+"Is not a mesh object, I will ignore")
				continue
			if (len(obj.vertex_groups) <= 0):
				self.report(type={'INFO'}, message=obj.name+"There is no vertex group is in, I will ignore")
				continue
			arm = bpy.data.armatures.new(self.armature_name)
			arm_obj = bpy.data.objects.new(self.armature_name, arm)
			bpy.context.scene.objects.link(arm_obj)
			arm_obj.select = True
			bpy.context.scene.objects.active = arm_obj
			me = obj.data
			bpy.ops.object.mode_set(mode='EDIT')
			for vert in me.vertices:
				for vg in vert.groups:
					if (0.0 < vg.weight):
						if (self.use_vertex_group_name):
							bone_name = obj.vertex_groups[vg.group].name
						else:
							bone_name = "Bone"
						bone = arm.edit_bones.new(bone_name)
						vert_co = obj.matrix_world * vert.co
						vert_no = obj.matrix_world.to_quaternion() * vert.normal * self.bone_length
						bone.head = vert_co
						bone.tail = vert_co + vert_no
			bpy.ops.object.mode_set(mode='OBJECT')
		bpy.context.scene.objects.active = pre_active_obj
		bpy.ops.object.mode_set(mode=pre_mode)
		return {'FINISHED'}

################################
# オペレーター(モディファイア) #
################################

class ApplyAllModifiers(bpy.types.Operator):
	bl_idname = "object.apply_all_modifiers"
	bl_label = "All modifier applied"
	bl_description = "I will apply all of the modifier of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers[:]:
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		return {'FINISHED'}

class DeleteAllModifiers(bpy.types.Operator):
	bl_idname = "object.delete_all_modifiers"
	bl_label = "All modifier Delete"
	bl_description = "I will delete all of the modifier of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			modifiers = obj.modifiers[:]
			for modi in modifiers:
				obj.modifiers.remove(modi)
		return {'FINISHED'}

class ToggleApplyModifiersView(bpy.types.Operator):
	bl_idname = "object.toggle_apply_modifiers_view"
	bl_label = "Switch the modifier application to view"
	bl_description = "I will switch the application to all of the modifier of view of the selected object"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		is_apply = True
		for mod in context.active_object.modifiers:
			if (mod.show_viewport):
				is_apply = False
				break
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				mod.show_viewport = is_apply
		if is_apply:
			self.report(type={"INFO"}, message="I have applied the modifier to view")
		else:
			self.report(type={"INFO"}, message="I have to release the modifier application to view")
		return {'FINISHED'}

class SyncShowModifiers(bpy.types.Operator):
	bl_idname = "object.sync_show_modifiers"
	bl_label = "Sync modifier use"
	bl_description = "I will synchronize the modifier use of the time during rendering / view of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("1", "Rendering to view", "", 1),
		("0", "View to rendering", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Calculation", default="0")
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				if (int(self.mode)):
					mod.show_viewport = mod.show_render
				else:
					mod.show_render = mod.show_viewport
		return {'FINISHED'}

class ToggleAllShowExpanded(bpy.types.Operator):
	bl_idname = "wm.toggle_all_show_expanded"
	bl_label = "Switch to the all modifier Expand / Close"
	bl_description = "All modifier of active objects to switch the Expand / Close to (toggle)"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		obj = context.active_object
		if (len(obj.modifiers)):
			vs = 0
			for mod in obj.modifiers:
				if (mod.show_expanded):
					vs += 1
				else:
					vs -= 1
			is_close = False
			if (0 < vs):
				is_close = True
			for mod in obj.modifiers:
				mod.show_expanded = not is_close
		else:
			self.report(type={'WARNING'}, message="Modifier does not have one")
			return {'CANCELLED'}
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ApplyModifiersAndJoin(bpy.types.Operator):
	bl_idname = "object.apply_modifiers_and_join"
	bl_label = "Modifier applied + integration"
	bl_description = "Integrate the modifier of object after all applicable"
	bl_options = {'REGISTER', 'UNDO'}
	
	unapply_subsurf = bpy.props.BoolProperty(name="I except Sabusafu", default=True)
	unapply_armature = bpy.props.BoolProperty(name="I except the armature", default=True)
	unapply_mirror = bpy.props.BoolProperty(name="I except mirror", default=False)
	
	def execute(self, context):
		pre_active_object = context.active_object
		for obj in context.selected_objects:
			context.scene.objects.active = obj
			for mod in obj.modifiers[:]:
				if (self.unapply_subsurf and mod.type == 'SUBSURF'):
					continue
				if (self.unapply_armature and mod.type == 'ARMATURE'):
					continue
				if (self.unapply_mirror and mod.type == 'MIRROR'):
					continue
				bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
		context.scene.objects.active = pre_active_object
		bpy.ops.object.join()
		return {'FINISHED'}

class AutoRenameModifiers(bpy.types.Operator):
	bl_idname = "object.auto_rename_modifiers"
	bl_label = "And rename automatically modifier name"
	bl_description = "I will rename the modifier name of the selected object in the name of such Reference"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			for mod in obj.modifiers:
				try:
					if (mod.subtarget):
						mod.name = mod.subtarget
					continue
				except AttributeError: pass
				try:
					if (mod.target):
						mod.name = mod.target.name
					continue
				except AttributeError: pass
				try:
					if (mod.object):
						mod.name = mod.object.name
					continue
				except AttributeError: pass
				try:
					if (mod.vertex_group):
						mod.name = mod.vertex_group
					continue
				except AttributeError: pass
		return {'FINISHED'}

############################
# オペレーター(ブーリアン) #
############################

class AddBoolean(bpy.types.Operator):
	bl_idname = "object.add_boolean"
	bl_label = "Add a boolean"
	bl_description = "Add a boolean of other selected objects in the Active Object"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("INTERSECT", "Intersect", "", 1),
		("UNION", "Union", "", 2),
		("DIFFERENCE", "Difference", "", 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="Calculation")
	
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH" and activeObj.name != obj.name):
				modi = activeObj.modifiers.new("Boolean", "BOOLEAN")
				modi.object = obj
				modi.operation = self.mode
				obj.draw_type = "BOUNDS"
		return {'FINISHED'}

class ApplyBoolean(bpy.types.Operator):
	bl_idname = "object.apply_boolean"
	bl_label = "Apply Boolean"
	bl_description = "Apply Boolean of other selected objects in the Active Object"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("INTERSECT", "Intersect", "", 1),
		("UNION", "Union", "", 2),
		("DIFFERENCE", "Difference", "", 3),
		]
	mode = bpy.props.EnumProperty(items=items, name="Calculation")
	
	def execute(self, context):
		activeObj = context.active_object
		for obj in context.selected_objects:
			if (obj.type == "MESH" and activeObj.name != obj.name):
				modi = activeObj.modifiers.new("Boolean", "BOOLEAN")
				modi.object = obj
				modi.operation = self.mode
				bpy.ops.object.modifier_apply (modifier=modi.name)
				bpy.ops.object.select_all(action='DESELECT')
				obj.select = True
				bpy.ops.object.delete()
				activeObj.select = True
		return {'FINISHED'}

####################
# オペレーター(UV) #
####################

class RenameSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.rename_specific_name_uv"
	bl_label = "Rename summarizes the UV"
	bl_description = "Rename summarizes the specified UV in the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	source_name =  bpy.props.StringProperty(name="UV name to rename", default="Past of UV")
	replace_name =  bpy.props.StringProperty(name="New UV name", default="New UV")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'WARNING'}, message=obj.name+" Is not a mesh object, I will ignore")
				continue
			me = obj.data
			for uv in me.uv_textures[:]:
				if (uv.name == self.source_name):
					uv.name = self.replace_name
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class DeleteSpecificNameUV(bpy.types.Operator):
	bl_idname = "object.delete_specific_name_uv"
	bl_label = "Remove UV with the specified name"
	bl_description = "The UV of the same name with the specified name, and then removed from the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="UV name to be deleted", default="UV")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type != 'MESH'):
				self.report(type={'WARNING'}, message=obj.name+" Is not a mesh object, I will ignore")
				continue
			me = obj.data
			for uv in me.uv_textures:
				if (uv.name == self.name):
					me.uv_textures.remove(uv)
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class RenameUV(bpy.types.Operator):
	bl_idname = "object.rename_uv"
	bl_label = "Change UV name"
	bl_description = "Change the name of the active UV (UV-specified texture will also change along with it)"
	bl_options = {'REGISTER', 'UNDO'}
	
	name =  bpy.props.StringProperty(name="New UV name", default="UV")
	
	def execute(self, context):
		obj = context.active_object
		if (obj.type == "MESH"):
			me = obj.data
			uv = me.uv_layers.active
			if (uv == None):
				self.report(type={"ERROR"}, message="UV does not exist")
				return {"CANCELLED"}
			preName = uv.name
			uv.name = self.name
			for mat in me.materials:
				if (mat):
					for slot in mat.texture_slots:
						if (slot != None):
							if (slot.uv_layer == preName):
									slot.uv_layer = uv.name
									self.report(type={"INFO"}, message="Materials"+mat.name+"I was fixed UV designation of")
					for me2 in bpy.data.meshes:
						for mat2 in me2.materials:
							if (mat2):
								if (mat.name == mat2.name):
									try:
										me2.uv_layers[preName].name = uv.name
										self.report(type={"INFO"}, message="Mesh"+me2.name+"I was fixed UV designation of")
									except KeyError: pass
		else:
			self.report(type={'ERROR'}, message="Not a mesh object")
			return {'CANCELLED'}
		return {'FINISHED'}
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class DeleteEmptyUV(bpy.types.Operator):
	bl_idname = "object.delete_empty_uv"
	bl_label = "Remove UV unused"
	bl_description = "You Delete all the unused UV in the material of the active object (UV that are used in other parts will erase)"
	bl_options = {'REGISTER', 'UNDO'}
	
	isAllSelected =  bpy.props.BoolProperty(name="All of the selected mesh", default=False)
	
	def execute(self, context):
		objs = [context.active_object]
		if (self.isAllSelected):
			objs = context.selected_objects
		for obj in objs:
			if (obj.type == "MESH"):
				uvs = []
				for mat in obj.material_slots:
					if (mat):
						for slot in mat.material.texture_slots:
							if (slot):
								if (not slot.uv_layer in uvs):
									uvs.append(slot.uv_layer)
				me = obj.data
				preUV = me.uv_layers.active
				u = me.uv_layers[:]
				for uv in u:
					if (not uv.name in uvs):
						self.report(type={"INFO"}, message=uv.name+" I have removed the")
						me.uv_layers.active = uv
						bpy.ops.mesh.uv_texture_remove()
				me.uv_layers.active = preUV
			else:
				self.report(type={"WARNING"}, message=obj.name+"Is not a mesh object")
		return {'FINISHED'}

############################
# オペレーター(サブサーフ) #
############################

class SetRenderSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.set_render_subsurf_level"
	bl_label = "Set the subdivision number at the time of rendering"
	bl_description = "I set the subdivision number at the time of rendering of sub-surf modifier of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	level = bpy.props.IntProperty(name="Division number", default=2, min=0, max=6)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						modi.render_levels = self.level
		return {'FINISHED'}

class EqualizeSubsurfLevel(bpy.types.Operator):
	bl_idname = "object.equalize_subsurf_level"
	bl_label = "Subdivided number is the same as that of the preview rendering"
	bl_description = "I set the subdivision number at the time of sub-surf modifier of preview during the rendering of the selected object in the same"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		("ToRender", "Preview to rendering", "", 1),
		("ToPreview", "Rendering → preview", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="Setting method")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						if (self.mode == "ToRender"):
							modi.render_levels = modi.levels
						else:
							modi.levels = modi.render_levels
		return {'FINISHED'}

class SetSubsurfOptimalDisplay(bpy.types.Operator):
	bl_idname = "object.set_subsurf_optimal_display"
	bl_label = "Set the optimization display"
	bl_description = "I set the optimization display of sub-surf modifier of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	mode =  bpy.props.BoolProperty(name="Optimization display")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						modi.show_only_control_edges = self.mode
		return {'FINISHED'}

class DeleteSubsurf(bpy.types.Operator):
	bl_idname = "object.delete_subsurf"
	bl_label = "Remove Sabusafu of selected objects"
	bl_description = "I will delete the sub-surf modifier of the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				for modi in obj.modifiers:
					if (modi.type == "SUBSURF"):
						obj.modifiers.remove(modi)
		return {'FINISHED'}

class AddSubsurf(bpy.types.Operator):
	bl_idname = "object.add_subsurf"
	bl_label = "Add Sabusafu to selected objects"
	bl_description = "Add a sub-surf modifier to the selected object"
	bl_options = {'REGISTER', 'UNDO'}
	
	
	subdivision_type = bpy.props.EnumProperty(items=[("CATMULL_CLARK", "Catmull Clark", "", 1), ("SIMPLE", "Simple", "", 2)], name="Subdivision method")
	levels = bpy.props.IntProperty(name="Levels", default=2, min=0, max=6)
	render_levels = bpy.props.IntProperty(name="Render Levels", default=2, min=0, max=6)
	use_subsurf_uv =  bpy.props.BoolProperty(name="And subdividing the UV", default=True)
	show_only_control_edges =  bpy.props.BoolProperty(name="Optimization display")
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type=="MESH" or obj.type=="CURVE" or obj.type=="SURFACE" or obj.type=="FONT" or obj.type=="LATTICE"):
				modi = obj.modifiers.new("Subsurf", "SUBSURF")
				modi.subdivision_type = self.subdivision_type
				modi.levels = self.levels
				modi.render_levels = self.render_levels
				modi.use_subsurf_uv = self.use_subsurf_uv
				modi.show_only_control_edges = self.show_only_control_edges
		return {'FINISHED'}

##############################
# オペレーター(アーマチュア) #
##############################

class SetArmatureDeformPreserveVolume(bpy.types.Operator):
	bl_idname = "object.set_armature_deform_preserve_volume"
	bl_label = "Configured together to maintain the volume of the armature"
	bl_description = "maintain the volume of the armature modifier of the selected object is used to turn on / off the armature"
	bl_options = {'REGISTER', 'UNDO'}
	
	use_deform_preserve_volume =  bpy.props.BoolProperty(name="Maintain the Volume", default=True)
	
	def execute(self, context):
		for obj in context.selected_objects:
			if (obj.type == "MESH"):
				for mod in obj.modifiers:
					if (mod.type == 'ARMATURE'):
						mod.use_deform_preserve_volume = self.use_deform_preserve_volume
		return {'FINISHED'}

########################
# オペレーター(カーブ) #
########################

class QuickCurveDeform(bpy.types.Operator):
	bl_idname = "object.quick_curve_deform"
	bl_label = "Quick curve deformation"
	bl_description = "I will apply the quick curve modifier"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('POS_X', "+X", "", 1),
		('POS_Y', "+Y", "", 2),
		('POS_Z', "+Z", "", 3),
		('NEG_X', "-X", "", 4),
		('NEG_Y', "-Y", "", 5),
		('NEG_Z', "-Z", "", 6),
		]
	deform_axis = bpy.props.EnumProperty(items=items, name="Axis deformation")
	is_apply = bpy.props.BoolProperty(name="Modifier applied", default=True)
	
	def execute(self, context):
		mesh_obj = context.active_object
		if (mesh_obj.type != 'MESH'):
			self.report(type={"ERROR"}, message="un in the active state mesh object")
			return {"CANCELLED"}
		if (len(context.selected_objects) != 2):
			self.report(type={"ERROR"}, message="Run by only two selection of mesh curve")
			return {"CANCELLED"}
		for obj in context.selected_objects:
			if (mesh_obj.name != obj.name):
				if (obj.type == 'CURVE'):
					curve_obj = obj
					break
		else:
			self.report(type={"ERROR"}, message="Curve object is also run on the selected state")
			return {"CANCELLED"}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply_all()
		mod = mesh_obj.modifiers.new("temp", 'CURVE')
		mod.object = curve_obj
		mod.deform_axis = self.deform_axis
		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod.name)
		if (self.is_apply):
			bpy.ops.object.modifier_apply(modifier=mod.name)
			curve.use_stretch = pre_use_stretch
			curve.use_deform_bounds = pre_use_deform_bounds
		return {'FINISHED'}

class QuickArrayAndCurveDeform(bpy.types.Operator):
	bl_idname = "object.quick_array_and_curve_deform"
	bl_label = "Quick sequence replication + curve deformation"
	bl_description = "I will apply the quick sequence replication modifier and curve modifier"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('POS_X', "+X", "", 1),
		('POS_Y', "+Y", "", 2),
		('POS_Z', "+Z", "", 3),
		('NEG_X', "-X", "", 4),
		('NEG_Y', "-Y", "", 5),
		('NEG_Z', "-Z", "", 6),
		]
	deform_axis = bpy.props.EnumProperty(items=items, name="Axis deformation")
	use_merge_vertices = bpy.props.BoolProperty(name="Vertex coupling", default=True)
	is_apply = bpy.props.BoolProperty(name="Modifier applied", default=True)
	
	def execute(self, context):
		mesh_obj = context.active_object
		if (mesh_obj.type != 'MESH'):
			self.report(type={'ERROR'}, message="Run in the active state mesh object")
			return {'CANCELLED'}
		if (len(context.selected_objects) != 2):
			self.report(type={'ERROR'}, message="Run by only two selection of mesh curve")
			return {'CANCELLED'}
		for obj in context.selected_objects:
			if (mesh_obj.name != obj.name):
				if (obj.type == 'CURVE'):
					curve_obj = obj
					break
		else:
			self.report(type={'ERROR'}, message="Curve object is also run on the selected state")
			return {'CANCELLED'}
		curve = curve_obj.data
		pre_use_stretch = curve.use_stretch
		pre_use_deform_bounds = curve.use_deform_bounds
		curve.use_stretch = True
		curve.use_deform_bounds = True
		bpy.ops.object.transform_apply_all()
		
		mod_array = mesh_obj.modifiers.new("Array", 'ARRAY')
		mod_array.fit_type = 'FIT_CURVE'
		mod_array.curve = curve_obj
		mod_array.use_merge_vertices = self.use_merge_vertices
		mod_array.use_merge_vertices_cap = self.use_merge_vertices
		if (self.deform_axis == 'POS_Y'):
			mod_array.relative_offset_displace = (0, 1, 0)
		elif (self.deform_axis == 'POS_Z'):
			mod_array.relative_offset_displace = (0, 0, 1)
		elif (self.deform_axis == 'NEG_X'):
			mod_array.relative_offset_displace = (-1, 0, 0)
		elif (self.deform_axis == 'NEG_Y'):
			mod_array.relative_offset_displace = (0, -1, 0)
		elif (self.deform_axis == 'NEG_Z'):
			mod_array.relative_offset_displace = (0, 0, -1)
		
		mod_curve = mesh_obj.modifiers.new("Curve", 'CURVE')
		mod_curve.object = curve_obj
		mod_curve.deform_axis = self.deform_axis
		
		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod_curve.name)
		for i in range(len(mesh_obj.modifiers)):
			bpy.ops.object.modifier_move_up(modifier=mod_array.name)
		
		if (self.is_apply):
			bpy.ops.object.modifier_apply(modifier=mod_array.name)
			bpy.ops.object.modifier_apply(modifier=mod_curve.name)
			curve.use_stretch = pre_use_stretch
			curve.use_deform_bounds = pre_use_deform_bounds
		return {'FINISHED'}

################
# サブメニュー #
################

class RenderHideMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_render_hide"
	bl_label = "Rendering limit"
	bl_description = "This is a menu of rendering limit relationship of objects"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator(SetRenderHide.bl_idname, text="Limit rendering of selections", icon="PLUGIN").reverse = True
		column.operator('object.isolate_type_render')
		column.separator()
		column.operator(SetRenderHide.bl_idname, text="Allow rendering of selections", icon="PLUGIN").reverse = False
		column.operator('object.hide_render_clear_all')
		column.separator()
		column.operator(SyncRenderHide.bl_idname, icon="PLUGIN")

class HideSelectMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_hide_select"
	bl_label = "Selection restriction"
	bl_description = "This is the menu for the selected limit relationship of objects"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator(SetHideSelect.bl_idname, text="And limit the choice of selections", icon="PLUGIN").reverse = True
		column.operator(SetUnselectHideSelect.bl_idname, icon="PLUGIN").reverse = True
		column.separator()
		column.operator(AllResetHideSelect.bl_idname, icon="PLUGIN").reverse = False

class ObjectNameMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_object_name"
	bl_label = "Object name"
	bl_description = "This is the menu of the object name relationship"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator(CopyObjectName.bl_idname, icon="PLUGIN")
		column.operator(RenameObjectRegularExpression.bl_idname, icon="PLUGIN")
		column.operator(EqualizeObjectNameAndDataName.bl_idname, icon="PLUGIN")
		if (len(context.selected_objects) <= 0):
			column.enabled = False

class ObjectColorMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_object_color"
	bl_label = "Object color"
	bl_description = "Object is a menu of color relationship"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator(ApplyObjectColor.bl_idname, icon="PLUGIN")
		column.operator(ClearObjectColor.bl_idname, icon="PLUGIN")

class ModifierMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_modifier"
	bl_label = "Modifier relationship"
	bl_description = "Modifier relationship"
	
	def draw(self, context):
		self.layout.menu(SubsurfMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(ArmatureMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(BooleanMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(CurveMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.separator()
		self.layout.operator(ApplyAllModifiers.bl_idname, icon="PLUGIN")
		self.layout.operator(ApplyModifiersAndJoin.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(DeleteAllModifiers.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(AutoRenameModifiers.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ToggleApplyModifiersView.bl_idname, icon="PLUGIN")
		self.layout.operator(ToggleAllShowExpanded.bl_idname, icon="PLUGIN")
		self.layout.operator(SyncShowModifiers.bl_idname, icon="PLUGIN")

class ArmatureMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_armature"
	bl_label = "Armature relationship"
	bl_description = "This is the operation of the armature relationship"
	
	def draw(self, context):
		self.layout.operator(SetArmatureDeformPreserveVolume.bl_idname, icon="PLUGIN")

class BooleanMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_boolean"
	bl_label = "Boolean relations"
	bl_description = "This is the operation of Boolean relations"
	
	def draw(self, context):
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Intersect").mode = "INTERSECT"
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Union").mode = "UNION"
		self.layout.operator(AddBoolean.bl_idname, icon="PLUGIN", text="Difference)").mode = "DIFFERENCE"
		self.layout.separator()
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Intersect").mode = "INTERSECT"
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Union").mode = "UNION"
		self.layout.operator(ApplyBoolean.bl_idname, icon="PLUGIN", text="Difference").mode = "DIFFERENCE"

class SubsurfMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_subsurf"
	bl_label = "Sabusafu relationship"
	bl_description = "This is the operation of sub-surface relationship"
	
	def draw(self, context):
		self.layout.operator(AddSubsurf.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteSubsurf.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(SetRenderSubsurfLevel.bl_idname, icon="PLUGIN")
		self.layout.operator(EqualizeSubsurfLevel.bl_idname, icon="PLUGIN")
		self.layout.operator(SetSubsurfOptimalDisplay.bl_idname, icon="PLUGIN")

class CurveMenu(bpy.types.Menu):
	bl_idname = "view3d_mt_object_specials_curve"
	bl_label = "Curve relationship"
	bl_description = "This is the operation of the curve relationship"
	
	def draw(self, context):
		self.layout.operator(QuickCurveDeform.bl_idname, icon="PLUGIN")
		self.layout.operator(QuickArrayAndCurveDeform.bl_idname, icon="PLUGIN")

class UVMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_uv"
	bl_label = "UV relationship"
	bl_description = "This is the operation of the UV relationship"
	
	def draw(self, context):
		self.layout.operator(RenameUV.bl_idname, icon="PLUGIN")
		self.layout.operator(RenameSpecificNameUV.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(DeleteSpecificNameUV.bl_idname, icon="PLUGIN")
		self.layout.operator(DeleteEmptyUV.bl_idname, icon="PLUGIN")

class SpecialsMenu(bpy.types.Menu):
	bl_idname = "VIEW3D_MT_object_specials_specials"
	bl_label = "Special processing"
	bl_description = "This is a menu of operations that a special treatment"
	
	def draw(self, context):
		column = self.layout.column()
		column.operator(CreateRopeMesh.bl_idname, icon="PLUGIN")
		column.enabled = False
		if (context.active_object):
			if (context.active_object.type == "CURVE"):
				column.enabled = True
		column = self.layout.column()
		self.layout.separator()
		column = self.layout.column()
		column.operator(CreateVertexToMetaball.bl_idname, icon="PLUGIN")
		column.enabled = False
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				column.enabled = True
		column = self.layout.column()
		column.operator(AddGreasePencilPathMetaballs.bl_idname, icon="PLUGIN")
		if (not context.gpencil_data):
			column.enabled = False
		self.layout.separator()
		column = self.layout.column()
		column.operator(CreateMeshImitateArmature.bl_idname, icon="PLUGIN")
		column.operator(CreateVertexGroupsArmature.bl_idname, icon="PLUGIN")
		self.layout.separator()
		column = self.layout.column()
		column.operator(CreateSolidifyEdge.bl_idname, icon="PLUGIN")
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				column.enabled = True

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
		self.layout.menu(RenderHideMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(HideSelectMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(ObjectNameMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(ObjectColorMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(UVMenu.bl_idname, icon="PLUGIN")
		self.layout.menu(ModifierMenu.bl_idname, icon="PLUGIN")
		self.layout.separator()
		column = self.layout.column()
		column.operator(ToggleSmooth.bl_idname, icon="PLUGIN")
		column.operator(AddVertexColorSelectedObject.bl_idname, icon="PLUGIN")
		column.enabled = False
		for obj in context.selected_objects:
			if (obj.type == 'MESH'):
				column.enabled = True
		self.layout.separator()
		column = self.layout.column()
		operator = column.operator(VertexGroupTransfer.bl_idname, icon="PLUGIN")
		column.enabled = False
		if (context.active_object.type == 'MESH'):
			i = 0
			for obj in context.selected_objects:
				if (obj.type == 'MESH'):
					i += 1
			if (2 <= i):
				column.enabled = True
		column = self.layout.column()
		column.operator('mesh.vertex_group_average_all', icon="PLUGIN")
		self.layout.separator()
		self.layout.menu(SpecialsMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='CANCEL').id = __name__.split('.')[-1]
