# 3Dビュー > Shift+S

import bpy

################
# オペレーター #
################

class SnapMesh3DCursor(bpy.types.Operator):
	bl_idname = "view3d.snap_mesh_3d_cursor"
	bl_label = "3D cursor snap to mesh"
	bl_description = "(Please use the shortcuts) mesh surface under the mouse move the 3D cursor"
	bl_options = {'REGISTER'}
	
	mouse_co = bpy.props.IntVectorProperty(name="Mouse position", size=2)
	
	def execute(self, context):
		preGp = context.scene.grease_pencil
		preGpSource = context.scene.tool_settings.grease_pencil_source
		context.scene.tool_settings.grease_pencil_source = 'SCENE'
		if (preGp):
			tempGp = preGp
		else:
			try:
				tempGp = bpy.data.grease_pencil["temp"]
			except KeyError:
				tempGp = bpy.data.grease_pencil.new("temp")
		context.scene.grease_pencil = tempGp
		tempLayer = tempGp.layers.new("temp", set_active=True)
		tempGp.draw_mode = 'SURFACE'
		bpy.ops.gpencil.draw(mode='DRAW_POLY', stroke=[{"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0),"mouse":self.mouse_co, "pressure":1, "time":0, "size":0}, {"name":"", "pen_flip":False, "is_start":True, "location":(0, 0, 0),"mouse":(0, 0), "pressure":1, "time":0, "size":0}])
		bpy.context.space_data.cursor_location = tempLayer.frames[-1].strokes[-1].points[0].co
		tempGp.layers.remove(tempLayer)
		context.scene.grease_pencil = preGp
		context.scene.tool_settings.grease_pencil_source = preGpSource
		return {'FINISHED'}
	def invoke(self, context, event):
		self.mouse_co[0] = event.mouse_region_x
		self.mouse_co[1] = event.mouse_region_y
		return self.execute(context)

class Move3DCursorToViewLocation(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_to_view_location"
	bl_label = "3D Navigation view"
	bl_description = "Move the 3D cursor center position of"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		bpy.context.space_data.cursor_location = context.region_data.view_location[:]
		return {'FINISHED'}

class Move3DCursorFar(bpy.types.Operator):
	bl_idname = "view3d.move_3d_cursor_far"
	bl_label = "3D cursor invisible in the (distant)"
	bl_description = "Pretend to hide the 3D cursor to move far far away"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		bpy.context.space_data.cursor_location = (24210, 102260, 38750)
		return {'FINISHED'}


# menu
def menu(self, context):

	self.layout.separator()
	self.layout.operator(Move3DCursorToViewLocation.bl_idname, text="Cursor-position", icon="PLUGIN")
	self.layout.operator(Move3DCursorFar.bl_idname, text="Cursor to hide (to)", icon="PLUGIN")
	self.layout.operator(SnapMesh3DCursor.bl_idname, text="Cursor → mesh surface", icon="PLUGIN")

