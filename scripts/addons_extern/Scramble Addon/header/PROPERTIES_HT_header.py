# プロパティ > ヘッダー

import bpy

################
# オペレーター #
################

class ChangeContextTab(bpy.types.Operator):
	bl_idname = "buttons.change_context_tab"
	bl_label = "Change Context"
	bl_description = "move left/right"
	bl_options = {'REGISTER'}
	
	is_left = bpy.props.BoolProperty(name="Left", default=False)
	
	def execute(self, context):
		for area in context.screen.areas:
			if (area.type == 'PROPERTIES'):
				for space in area.spaces:
					if (space.type == 'PROPERTIES'):
						space_data = space
		now_tab = space_data.context
		tabs = ['RENDER', 'RENDER_LAYER', 'SCENE', 'WORLD', 'OBJECT', 'CONSTRAINT', 'MODIFIER', 'DATA', 'BONE', 'BONE_CONSTRAINT', 'MATERIAL', 'TEXTURE', 'PARTICLES', 'PHYSICS']
		for tab in tabs[:]:
			try:
				space_data.context = tab
			except TypeError:
				tabs.remove(tab)
		if (now_tab not in tabs):
			self.report(type={'ERROR'}, message="Nothing to do")
			return {'CANCELLED'}
		if (self.is_left):
			tabs.reverse()
		flag = False
		for tab in tabs:
			if (flag):
				space_data.context = tab
				break
			if (tab == now_tab):
				flag = True
		else:
			space_data.context = tabs[0]
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
		row = self.layout.row(align=True)
		row.operator(ChangeContextTab.bl_idname, text="", icon='TRIA_LEFT').is_left = True
		row.operator(ChangeContextTab.bl_idname, text="", icon='TRIA_RIGHT').is_left = False
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
