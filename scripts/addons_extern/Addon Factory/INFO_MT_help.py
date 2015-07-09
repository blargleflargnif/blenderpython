# 情報 > 「ヘルプ」メニュー

import bpy

################
# オペレーター #
################

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
		self.layout.operator('wm.toggle_disabled_menu', icon='PLUGIN')
		self.layout.operator('script.update_scramble_addon', icon='PLUGIN')
	if (context.user_preferences.addons["Addon Factory"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
