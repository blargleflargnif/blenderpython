# 3Dビュー > オブジェクト/メッシュ編集モード > 「追加」メニュー > 「メッシュ」メニュー

import bpy
import math
from .add_mesh_icicle_snowflake import add_mesh_snowflake1
from .add_mesh_icicle_snowflake import add_mesh_icicle_gen1
################


class INFO_MT_mesh_icy_add(bpy.types.Menu):
    # Define the "Ice" menu
    bl_idname = "INFO_MT_mesh_ice_add"
    bl_label = "Ice & Snow"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.icicle_gen",
            text="Icicle Generator")
        layout.operator("mesh.snowflake",
            text="Snowflake")

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
		self.layout.menu("INFO_MT_mesh_ice_add", text="Ice & Snow")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable', text = 'Additional Items', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
