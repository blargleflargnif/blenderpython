# 「3Dビュー」エリア > プロパティ > 「3Dカーソル」パネル

import bpy

################
# オペレーター #
################

################
# メニュー追加 #
################
# Classes for VIEW3D_MT_CursorMenu()
class VIEW3D_OT_pivot_cursor(bpy.types.Operator):
    "Cursor as Pivot Point"
    bl_idname = "view3d.pivot_cursor"
    bl_label = "Cursor as Pivot Point"

    @classmethod
    def poll(cls, context):
        return bpy.context.space_data.pivot_point != 'CURSOR'

    def execute(self, context):
        bpy.context.space_data.pivot_point = 'CURSOR'
        return {'FINISHED'}

class VIEW3D_OT_revert_pivot(bpy.types.Operator):
    "Revert Pivot Point"
    bl_idname = "view3d.revert_pivot"
    bl_label = "Reverts Pivot Point to median"

    @classmethod
    def poll(cls, context):
        return bpy.context.space_data.pivot_point != 'MEDIAN_POINT'

    def execute(self, context):
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        # @todo Change this to 'BOUDNING_BOX_CENTER' if needed...
        return{'FINISHED'}

# menu
def menu(self, context):

	layout = self.layout
	layout.operator_context = 'INVOKE_REGION_WIN'
	layout.label(text= "Snap Cursor Menu")

	row = layout.row(align=True)
	row.operator("view3d.snap_cursor_to_selected",
		text="Selected")
	row.operator("view3d.snap_cursor_to_center",
		text="Center")
	row = layout.row(align=True)
	row.operator("view3d.snap_cursor_to_grid",
		text="Grid")
	row.operator("view3d.snap_cursor_to_active",
		text="Active")
	row = layout.row(align=True)
	row.operator("view3d.snap_selected_to_cursor",
		text="Select > Cursor")
	row.operator("view3d.snap_selected_to_grid",
		text="Select > Grid")
	row = layout.row(align=True)
	row.operator("view3d.pivot_cursor",
		text="Cursor Is Pivot")
	row.operator("view3d.revert_pivot",
		text="Revert Pivot")

