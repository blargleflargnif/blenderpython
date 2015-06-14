# ユーザー設定 > ヘッダー

import bpy
import zipfile, urllib.request, os, sys, re
import csv, codecs
import collections
import subprocess
import webbrowser
try:
	import winreg
except:
	pass
from xml.dom import minidom
import xml.etree.ElementTree as ElementTree

################################
# オペレーター(ショートカット) #
################################

class SearchKeyBind(bpy.types.Operator):
	bl_idname = "ui.search_key_bind"
	bl_label = "キーバインド検索"
	bl_description = "設定したキーバインドに一致する割り当てを検索します"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		keymap = context.window_manager.keyconfigs.addon.keymaps['temp'].keymap_items[0]
		if (keymap.type == 'NONE'):
			self.report(type={'ERROR'}, message="検索するキーが空です、設定してください")
			return {'CANCELLED'}
		filter_str = keymap.type
		if (not keymap.any):
			if (keymap.shift):
				filter_str = filter_str + " Shift"
			if (keymap.ctrl):
				filter_str = filter_str + " Ctrl"
			if (keymap.alt):
				filter_str = filter_str + " Alt"
		else:
			filter_str = filter_str + " Any"
		context.space_data.filter_type = 'KEY'
		context.space_data.filter_text = filter_str
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class CloseKeyMapItems(bpy.types.Operator):
	bl_idname = "ui.close_key_map_items"
	bl_label = "キーコンフィグを全て閉じる"
	bl_description = "キーコンフィグのメニューを全て折りたたみます"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		for keyconfig in context.window_manager.keyconfigs:
			for keymap in keyconfig.keymaps:
				keymap.show_expanded_children = False
				keymap.show_expanded_items = False
				for keymap_item in keymap.keymap_items:
					keymap_item.show_expanded = False
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

class ShowShortcutHtml(bpy.types.Operator):
	bl_idname = "system.show_shortcut_html"
	bl_label = "ショートカット一覧をブラウザで閲覧"
	bl_description = "Blenderの全てのショートカットをブラウザで確認出来ます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		keyDatas = collections.OrderedDict()
		with codecs.open(os.path.join(addonDir, "ShortcutHtmlKeysData.csv"), 'r', 'utf-8') as f:
			reader = csv.reader(f)
			for row in reader:
				name = row[1]
				keyDatas[name] = {}
				keyDatas[name]["key_name"] = row[0]
				keyDatas[name]["key_code"] = row[1]
				keyDatas[name]["shape"] = row[2]
				keyDatas[name]["coords"] = row[3]
				keyDatas[name]["configs"] = collections.OrderedDict()
		keyconfigs = context.window_manager.keyconfigs
		for kc in (keyconfigs.user, keyconfigs.addon):
			for km in kc.keymaps:
				for kmi in km.keymap_items:
					if (kmi.type in keyDatas):
						if (not kmi.name):
							continue
						if (km.name in keyDatas[kmi.type]["configs"]):
							keyDatas[kmi.type]["configs"][km.name].append(kmi)
						else:
							keyDatas[kmi.type]["configs"][km.name] = [kmi]
		areaStrings = ""
		for name, data in keyDatas.items():
			title = "<b>【 " +data["key_name"]+ " 】</b><br><br>"
			for mapName, cfgs in data["configs"].items():
				title = title + "<b>[" + mapName + "]</b><br>"
				cfgsData = []
				for cfg in cfgs:
					cfgStr = ""
					color = ["0", "0", "0"]
					if (cfg.shift):
						cfgStr = cfgStr + " Shift"
						color[2] = "6"
					if (cfg.ctrl):
						cfgStr = cfgStr + " Ctrl"
						color[1] = "6"
					if (cfg.alt):
						cfgStr = cfgStr + " Alt"
						color[0] = "6"
					if (cfg.oskey):
						cfgStr = cfgStr + " OS"
					if (cfg.key_modifier != 'NONE'):
						cfgStr = cfgStr + " " + cfg.key_modifier
					if (cfgStr):
						cfgStr = "(+" + cfgStr[1:] + ")　"
					if (cfg.any):
						cfgStr = "(常に)　"
					modifierKeyStr = cfgStr
					if (cfg.name):
						if (cfg.idname == "wm.call_menu"):
							cfgStr = cfgStr + "「" + cfg.properties.name + "」メニューの呼び出し"
						elif (cfg.idname == "wm.context_set_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」を「" + cfg.properties.value + "」に変更"
						elif (cfg.idname == "wm.context_toggle"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」の切り替え"
						elif (cfg.idname == "wm.context_toggle_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」を「" + cfg.properties.value_1 + "」と「" + cfg.properties.value_2 + "」に切り替え"
						elif (cfg.idname == "wm.context_menu_enum"):
							cfgStr = cfgStr + "「" + cfg.properties.data_path + "」メニューの呼び出し"
						else:
							cfgStr = cfgStr + cfg.name
					else:
						cfgStr = cfgStr + cfg.propvalue
					if (not cfg.active):
						cfgStr = "<s>" + cfgStr + "</s>"
					cfgStr = "　<font size='2' color='#" +color[0]+color[1]+color[2]+ "'>" + cfgStr + "</font><br>"
					cfgsData.append([cfgStr, modifierKeyStr])
				cfgsData = sorted(cfgsData, key=lambda i: len(i[1]))
				alreadys = []
				for i in cfgsData:
					if (i[0] not in alreadys):
						title = title + i[0]
						alreadys.append(i[0])
			areaStrings = areaStrings+ '<area href="#" title="' +title+ '" shape="' +data["shape"]+ '" coords="' +data["coords"]+ '">\n'
		file = codecs.open(os.path.join(addonDir, "ShortcutHtmlTemplate.html"), 'r', 'utf-8')
		template = file.read()
		file.close()
		template = template.replace("<!-- [AREAS] -->", areaStrings)
		file = codecs.open(os.path.join(addonDir, "ShortcutHtmlTemp.html"), "w", 'utf-8')
		file.write(template)
		file.close()
		webbrowser.open(os.path.join(addonDir, "ShortcutHtmlTemp.html"))
		return {'FINISHED'}

class RegisterLastCommandKeyconfig(bpy.types.Operator):
	bl_idname = "wm.register_last_command_keyconfig"
	bl_label = "最後のコマンドをショートカットに登録"
	bl_description = "最後に実行したコマンドをショートカットに登録します"
	bl_options = {'REGISTER'}
	
	is_clipboard = bpy.props.BoolProperty(name="(変更しないで)")
	command = bpy.props.StringProperty(name="(変更しないで)")
	sub_command = bpy.props.StringProperty(name="(変更しないで)")
	items = [
		('Window', "ウィンドウ", "", 1),
		('Screen', "スクリーン", "", 2),
		('Screen Editing', "スクリーン編集", "", 3),
		('View2D', "2Dビュー", "", 4),
		('Frames', "フレーム", "", 5),
		('Header', "ヘッダー", "", 6),
		('View2D Buttons List', "2Dビューボタンリスト", "", 7),
		('Property Editor', "プロパティエディター", "", 8),
		('3D View Generic', "3Dビュー全般", "", 9),
		('Grease Pencil', "グリースペンシル", "", 10),
		('Grease Pencil Stroke Edit Mode', "グリースペンシルストローク編集モード", "", 11),
		('Face Mask', "面のマスク", "", 12),
		('Weight Paint Vertex Selection', "ウェイトペイント頂点選択", "", 13),
		('Pose', "ポーズ", "", 14),
		('Object Mode', "オブジェクトモード", "", 15),
		('Paint Curve', "ペイントカーブ", "", 16),
		('Curve', "カーブ", "", 17),
		('Image Paint', "画像ペイント", "", 18),
		('Vertex Paint', "頂点ペイント", "", 19),
		('Weight Paint', "ウェイトペイント", "", 20),
		('Sculpt', "スカルプト", "", 21),
		('Mesh', "メッシュ", "", 22),
		('Armature', "アーマチュア", "", 23),
		('Metaball', "メタボール", "", 24),
		('Lattice', "ラティス", "", 25),
		('Particle', "パーティクル", "", 26),
		('Font', "フォント", "", 27),
		('Object Non-modal', "オブジェクト非モーダル", "", 28),
		('3D View', "3Dビュー", "", 29),
		('Outliner', "アウトライナー", "", 30),
		('Info', "情報", "", 31),
		('View3D Gesture Circle', "3Dビュージェスチャサークル", "", 32),
		('Gesture Border', "ジェスチャ境界", "", 33),
		('Gesture Zoom Border', "ジェスチャ境界ズーム", "", 34),
		('Gesture Straight Line', "ジェスチャ直線", "", 35),
		('Standard Modal Map', "標準モーダルマップ", "", 36),
		('Animation', "アニメーション", "", 37),
		('Animation Channels', "アニメーションチャンネル", "", 38),
		('Knife Tool Modal Map', "ナイフツールモーダルマップ", "", 39),
		('UV Editor', "UVエディター", "", 40),
		('Transform Modal Map', "トランスフォームモーダルマップ", "", 41),
		('UV Sculpt', "UVスカルプト", "", 42),
		('Paint Stroke Modal', "ペイントストロークモーダル", "", 43),
		('Mask Editing', "マスク編集", "", 44),
		('Markers', "マーカー", "", 45),
		('Timeline', "タイムライン", "", 46),
		('View3D Fly Modal', "3Dビューフライモーダル", "", 47),
		('View3D Walk Modal', "3Dビューウォークモーダル", "", 48),
		('View3D Rotate Modal', "3Dビュー回転モーダル", "", 49),
		('View3D Move Modal', "3Dビュー移動モーダル", "", 50),
		('View3D Zoom Modal', "3Dビューズームモーダル", "", 51),
		('View3D Dolly Modal', "3Dビュードリーモーダル", "", 52),
		('Graph Editor Generic', "グラフエディター全般", "", 53),
		('Graph Editor', "グラフエディター", "", 54),
		('Image Generic', "画像全般", "", 55),
		('Image', "画像", "", 56),
		('Node Generic', "ノード全般", "", 57),
		('Node Editor', "ノードエディター", "", 58),
		('File Browser', "ファイルブラウザー", "", 59),
		('File Browser Main', "ファイルブラウザーメイン", "", 60),
		('File Browser Buttons', "ファイルブラウザーボタン", "", 61),
		('Dopesheet', "ドープシート", "", 62),
		('NLA Generic', "NLA全般", "", 63),
		('NLA Channels', "NLAチャンネル", "", 64),
		('NLA Editor', "NLAエディター", "", 65),
		('Text Generic', "テキスト全般", "", 66),
		('Text', "テキスト", "", 67),
		('SequencerCommon', "シーケンサー共通", "", 68),
		('Sequencer', "シーケンサー", "", 69),
		('SequencerPreview', "シーケンサープレビュー", "", 70),
		('Logic Editor', "ロジックエディター", "", 71),
		('Console', "コンソール", "", 72),
		('Clip', "クリップ", "", 73),
		('Clip Editor', "クリップエディター", "", 74),
		('Clip Graph Editor', "クリップグラフエディター", "", 75),
		('Clip Dopesheet Editor', "クリップドープシートエディター", "", 76),
		]
	key_map = bpy.props.EnumProperty(items=items, name="有効エリア")
	items = [
		('LEFTMOUSE', "左クリック", "", 1),
		('MIDDLEMOUSE', "ホイールクリック", "", 2),
		('RIGHTMOUSE', "右クリック", "", 3),
		('BUTTON4MOUSE', "マウス4ボタン", "", 4),
		('BUTTON5MOUSE', "マウス5ボタン", "", 5),
		('BUTTON6MOUSE', "マウス6ボタン", "", 6),
		('BUTTON7MOUSE', "マウス7ボタン", "", 7),
		('MOUSEMOVE', "マウス移動", "", 8),
		('INBETWEEN_MOUSEMOVE', "境界のマウス移動", "", 9),
		('WHEELUPMOUSE', "ホイールアップ", "", 10),
		('WHEELDOWNMOUSE', "ホイールダウン", "", 11),
		('A', "Aキー", "", 12),
		('B', "Bキー", "", 13),
		('C', "Cキー", "", 14),
		('D', "Dキー", "", 15),
		('E', "Eキー", "", 16),
		('F', "Fキー", "", 17),
		('G', "Gキー", "", 18),
		('H', "Hキー", "", 19),
		('I', "Iキー", "", 20),
		('J', "Jキー", "", 21),
		('K', "Kキー", "", 22),
		('L', "Lキー", "", 23),
		('M', "Mキー", "", 24),
		('N', "Nキー", "", 25),
		('O', "Oキー", "", 26),
		('P', "Pキー", "", 27),
		('Q', "Qキー", "", 28),
		('R', "Rキー", "", 29),
		('S', "Sキー", "", 30),
		('T', "Tキー", "", 31),
		('U', "Uキー", "", 32),
		('V', "Vキー", "", 33),
		('W', "Wキー", "", 34),
		('X', "Xキー", "", 35),
		('Y', "Yキー", "", 36),
		('Z', "Zキー", "", 37),
		('ZERO', "0", "", 38),
		('ONE', "1", "", 39),
		('TWO', "2", "", 40),
		('THREE', "3", "", 41),
		('FOUR', "4", "", 42),
		('FIVE', "5", "", 43),
		('SIX', "6", "", 44),
		('SEVEN', "7", "", 45),
		('EIGHT', "8", "", 46),
		('NINE', "9", "", 47),
		('LEFT_CTRL', "左CTRL", "", 48),
		('LEFT_ALT', "左ALT", "", 49),
		('LEFT_SHIFT', "左SHIFT", "", 50),
		('RIGHT_ALT', "右ALT", "", 51),
		('RIGHT_CTRL', "右CTRL", "", 52),
		('RIGHT_SHIFT', "右SHIFT", "", 53),
		('OSKEY', "OSキー", "", 54),
		('GRLESS', "\\", "", 55),
		('ESC', "Escキー", "", 56),
		('TAB', "Tabキー", "", 57),
		('RET', "エンターキー", "", 58),
		('SPACE', "Spaceキー", "", 59),
		('BACK_SPACE', "BackSpaceキー", "", 60),
		('DEL', "Deleteキー", "", 61),
		('SEMI_COLON', ":", "", 62),
		('PERIOD', ".(ピリオド)", "", 63),
		('COMMA', ",(コンマ)", "", 64),
		('QUOTE', "^", "", 65),
		('ACCENT_GRAVE', "@", "", 66),
		('MINUS', "-", "", 67),
		('SLASH', "/", "", 68),
		('BACK_SLASH', "\\(バックスラッシュ)", "", 69),
		('EQUAL', ";", "", 70),
		('LEFT_BRACKET', "[", "", 71),
		('RIGHT_BRACKET', "]", "", 72),
		('LEFT_ARROW', "←", "", 73),
		('DOWN_ARROW', "↓", "", 74),
		('RIGHT_ARROW', "→", "", 75),
		('UP_ARROW', "↑", "", 76),
		('NUMPAD_2', "テンキー2", "", 77),
		('NUMPAD_4', "テンキー4", "", 78),
		('NUMPAD_6', "テンキー6", "", 79),
		('NUMPAD_8', "テンキー8", "", 80),
		('NUMPAD_1', "テンキー1", "", 81),
		('NUMPAD_3', "テンキー3", "", 82),
		('NUMPAD_5', "テンキー5", "", 83),
		('NUMPAD_7', "テンキー7", "", 84),
		('NUMPAD_9', "テンキー9", "", 85),
		('NUMPAD_PERIOD', "テンキーピリオド", "", 86),
		('NUMPAD_SLASH', "テンキースラッシュ", "", 87),
		('NUMPAD_ASTERIX', "テンキー＊", "", 88),
		('NUMPAD_0', "テンキー0", "", 89),
		('NUMPAD_MINUS', "テンキーマイナス", "", 90),
		('NUMPAD_ENTER', "テンキーエンター", "", 91),
		('NUMPAD_PLUS', "テンキー＋", "", 92),
		('F1', "F1", "", 93),
		('F2', "F2", "", 94),
		('F3', "F3", "", 95),
		('F4', "F4", "", 96),
		('F5', "F5", "", 97),
		('F6', "F6", "", 98),
		('F7', "F7", "", 99),
		('F8', "F8", "", 100),
		('F9', "F9", "", 101),
		('F10', "F10", "", 102),
		('F11', "F11", "", 103),
		('F12', "F12", "", 104),
		('F13', "F13", "", 105),
		('F14', "F14", "", 106),
		('F15', "F15", "", 107),
		('F16', "F16", "", 108),
		('F17', "F17", "", 109),
		('F18', "F18", "", 110),
		('F19', "F19", "", 111),
		('PAUSE', "Pauseキー", "", 112),
		('INSERT', "Insertキー", "", 113),
		('HOME', "Homeキー", "", 114),
		('PAGE_UP', "PageUpキー", "", 115),
		('PAGE_DOWN', "PageDownキー", "", 116),
		('END', "Endキー", "", 117),
		]
	type = bpy.props.EnumProperty(items=items, name="入力キー")
	shift = bpy.props.BoolProperty(name="Shiftを修飾キーに", default=False)
	ctrl = bpy.props.BoolProperty(name="Ctrlを修飾キーに", default=False)
	alt = bpy.props.BoolProperty(name="Altを修飾キーに", default=False)
	
	def execute(self, context):
		keymap_item = context.window_manager.keyconfigs.user.keymaps[self.key_map].keymap_items.new(self.command, self.type, 'PRESS', False, self.shift, self.ctrl, self.alt)
		for command in self.sub_command.split(","):
			if (not command):
				continue
			name, value = command.split(":")
			if (re.search(r"^\d+$", value)):
				keymap_item.properties[name] = int(value)
			elif (re.search(r"^[+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$", value)):
				keymap_item.properties[name] = float(value)
			else:
				keymap_item.properties[name] = value
		self.report(type={"INFO"}, message="ショートカットを登録しました、必要であれば「ユーザー設定の保存」をしてください")
		return {'FINISHED'}
	def invoke(self, context, event):
		pre_clipboard = context.window_manager.clipboard
		pre_area_type = context.area.type
		context.area.type = 'INFO'
		if (not self.is_clipboard):
			for area in context.screen.areas:
				area.tag_redraw()
			bpy.ops.info.reports_display_update()
			for i in range(50):
				bpy.ops.info.select_all_toggle()
				bpy.ops.info.report_copy()
				if (context.window_manager.clipboard != ""):
					break
			bpy.ops.info.select_all_toggle()
		context.area.type = pre_area_type
		commands = context.window_manager.clipboard.split("\n")
		context.window_manager.clipboard = pre_clipboard
		if (commands[-1] == ''):
			commands = commands[:-1]
		if (len(commands) <= 0):
			self.report(type={'ERROR'}, message="最後に実行したコマンドが見つかりません")
			return {'CANCELLED'}
		commands.reverse()
		for command in commands:
			if (re.search(r"^bpy\.ops\.wm\.call_menu", command)):
				self.command = 'wm.call_menu'
				self.sub_command = 'name:'+re.search(r'^bpy\.ops\.wm\.call_menu\(name\="([^"]+)"\)$', command).groups()[0]
				break
			elif (re.search(r"^bpy\.ops\.", command)):
				self.command = re.search(r"^bpy\.ops\.([^\(]+)", command).groups()[0]
				#options = re.search(r"\((.*)\)$", command).groups()[0]
				#properties = options.split(",")
				break
			elif (re.search(r"^bpy\.context\.", command)):
				if (re.search(r"True$", command) or re.search(r"False$", command)):
					self.command = 'wm.context_toggle'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
				elif (re.search(r" = '[^']+'$", command)):
					self.command = 'wm.context_set_enum'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r" = '([^']+)'$", command).groups()[0]
				elif (re.search(r" = \d+$", command)):
					self.command = 'wm.context_set_int'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r" = (\d+)$", command).groups()[0]
				elif (re.search(r' = [+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$', command)):
					self.command = 'wm.context_set_float'
					self.sub_command = 'data_path:'+re.search(r"^bpy\.context\.([^ ]+)", command).groups()[0]
					self.sub_command = self.sub_command+","+'value:'+re.search(r' = [+-]?(\d*\.\d+|\d+\.?\d*)([eE][+-]?\d+|)\Z$', command).groups()[0]
				else:
					self.report(type={'ERROR'}, message="対応していないタイプのコマンドです")
					return {'CANCELLED'}
				break
		else:
			self.report(type={'ERROR'}, message="登録出来るコマンドが見つかりませんでした")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)

class ShowEmptyShortcuts(bpy.types.Operator):
	bl_idname = "view3d.show_empty_shortcuts"
	bl_label = "割り当ての無いショートカット一覧"
	bl_description = "現在の編集モードでの割り当ての無いキーを「情報」エリアに表示します"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		addonDir = os.path.dirname(__file__)
		key_names = collections.OrderedDict()
		key_strings = []
		key_binds = collections.OrderedDict()
		with open(os.path.join(addonDir, "KeysList.csv"), 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				key_names[row[1]] = row[0]
				key_strings.append(row[1])
				key_binds[row[1]] = None
		keyconfigs = context.window_manager.keyconfigs
		permits = ['Window', 'Screen', '3D View Generic', '3D View', 'Frames', 'Object Non-modal']
		if (context.mode == 'EDIT_MESH'):
			permits.append('Mesh')
		elif (context.mode == 'EDIT_CURVE'):
			permits.append('Curve')
		elif (context.mode == 'EDIT_SURFACE'):
			permits.append('Curve')
		elif (context.mode == 'EDIT_TEXT'):
			permits.append('Font')
		elif (context.mode == 'EDIT_ARMATURE'):
			permits.append('Armature')
		elif (context.mode == 'EDIT_METABALL'):
			permits.append('Metaball')
		elif (context.mode == 'EDIT_LATTICE'):
			permits.append('Lattice')
		elif (context.mode == 'POSE'):
			permits.append('Pose')
		elif (context.mode == 'SCULPT'):
			permits.append('Sculpt')
		elif (context.mode == 'PAINT_WEIGHT'):
			permits.append('Weight Paint')
		elif (context.mode == 'PAINT_VERTEX'):
			permits.append('Vertex Paint')
		elif (context.mode == 'PAINT_TEXTURE'):
			permits.append('Image Paint')
		elif (context.mode == 'PARTICLE'):
			permits.append('Particle')
		elif (context.mode == 'OBJECT'):
			permits.append('Object Mode')
		for keyconfig in (keyconfigs.user, keyconfigs.addon):
			for keymap in keyconfig.keymaps:
				if (not keymap.name in permits):
					continue
				for item in keymap.keymap_items:
					if (item.type in key_strings):
						if (item.active):
							if (not item.shift and not item.ctrl and not item.alt and not item.oskey and item.key_modifier == 'NONE'):
								key_binds[item.type] = item.idname
							elif (item.any):
								key_binds[item.type] = item.idname
		self.report(type={'INFO'}, message = permits[-1]+"モードでは、以下の割り当てが空いています")
		for key, value in key_binds.items():
			if (not value):
				self.report(type={'INFO'}, message = key_names[key]+" ")
		return {'FINISHED'}

class ImportKeyConfigXml(bpy.types.Operator):
	bl_idname = "file.import_key_config_xml"
	bl_label = "キーコンフィグをXMLでインポート"
	bl_description = "キーコンフィグをXML形式で読み込みます"
	bl_options = {'REGISTER'}
	
	filepath = bpy.props.StringProperty(subtype='FILE_PATH')
	items = [
		('RESET', "リセット", "", 1),
		('ADD', "追加", "", 2),
		]
	mode = bpy.props.EnumProperty(items=items, name="モード", default='ADD')
	
	def execute(self, context):
		context.user_preferences.addons["Scramble Addon"].preferences.key_config_xml_path = self.filepath
		try:
			tree = ElementTree.parse(self.filepath)
		except:
			self.report(type={'ERROR'}, message="XMLファイルの読み込みに失敗しました")
			return {'CANCELLED'}
		root = tree.getroot()
		if (root.tag != 'BlenderKeyConfig'):
			self.report(type={'ERROR'}, message="このファイルはBlenderキーコンフィグXMLファイルではありません")
			return {'CANCELLED'}
		try:
			if (root.attrib['Version'] != '1.2'):
				self.report(type={'ERROR'}, message="このBlenderキーコンフィグXMLファイルのバージョンには対応していません")
				return {'CANCELLED'}
		except KeyError:
			self.report(type={'ERROR'}, message="BlenderキーコンフィグXMLファイルのバージョンを確認できませんでした")
			return {'CANCELLED'}
		for key_config_elem in root.findall('KeyConfig'):
			key_config_name = key_config_elem.attrib['name']
			key_config = context.window_manager.keyconfigs[key_config_name]
			for key_map_elem in key_config_elem.findall('KeyMap'):
				key_map_name = key_map_elem.attrib['name']
				key_map = key_config.keymaps[key_map_name]
				if (key_map.is_modal):
					continue
				if (self.mode == 'RESET'):
					for key_map_item in key_map.keymap_items:
						key_map.keymap_items.remove(key_map_item)
				for key_map_item_elem in key_map_elem.findall('KeyMapItem'):
					active = True
					if ('Active' in key_map_item_elem.attrib):
						active = bool(int(key_map_item_elem.attrib['Active']))
					id_name = key_map_item_elem.find('Command').text
					if (not id_name):
						continue
					key_elem = key_map_item_elem.find('Key')
					type = key_elem.text
					if (not type):
						continue
					map_type = 'KEYBOARD'
					if ('Type' in key_elem.attrib):
						map_type = key_elem.attrib['Type']
					value = 'PRESS'
					if ('Value' in key_elem.attrib):
						value = key_elem.attrib['Value']
					if (not type):
						continue
					any = False
					if ('Any' in key_elem.attrib):
						shift, ctrl, alt, any = True, True, True, True
					else:
						shift = False
						if ('Shift' in key_elem.attrib):
							shift = bool(int(key_elem.attrib['Shift']))
						ctrl = False
						if ('Ctrl' in key_elem.attrib):
							ctrl = bool(int(key_elem.attrib['Ctrl']))
						alt = False
						if ('Alt' in key_elem.attrib):
							alt = bool(int(key_elem.attrib['Alt']))
					os = False
					if ('OS' in key_elem.attrib):
						os = bool(int(key_elem.attrib['OS']))
					key_modifier = 'NONE'
					if ('KeyModifier' in key_elem.attrib):
						key_modifier = key_elem.attrib['KeyModifier']
					key_map_item = key_map.keymap_items.new(id_name, type, value, any, shift, ctrl, alt, os, key_modifier)
					key_map_item.active = active
					for property_elem in key_map_item_elem.findall('Property'):
						try:
							property_name = property_elem.attrib['Name']
							property_type = property_elem.attrib['Type']
							property_value = property_elem.text
							if (property_type == 'int'):
								key_map_item.properties[property_name] = int(property_value)
							elif (property_type == 'float'):
								key_map_item.properties[property_name] = float(property_value)
							elif (property_type == 'str'):
								key_map_item.properties[property_name] = str(property_value)
							else:
								print("Unknown Type: " + property_type)
						except AttributeError:
							continue
		return {'FINISHED'}
	def invoke(self, context, event):
		self.filepath = context.user_preferences.addons["Scramble Addon"].preferences.key_config_xml_path
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

class ExportKeyConfigXml(bpy.types.Operator):
	bl_idname = "file.export_key_config_xml"
	bl_label = "キーコンフィグをXMLでエクスポート"
	bl_description = "キーコンフィグをXML形式で保存します"
	bl_options = {'REGISTER'}
	
	filepath = bpy.props.StringProperty(subtype='FILE_PATH')
	
	def execute(self, context):
		context.user_preferences.addons["Scramble Addon"].preferences.key_config_xml_path = self.filepath
		data = ElementTree.Element('BlenderKeyConfig', {'Version':'1.2'})
		for keyconfig in [context.window_manager.keyconfigs.user]:
			keyconfig_elem = ElementTree.SubElement(data, 'KeyConfig', {'name':keyconfig.name})
			for keymap in keyconfig.keymaps:
				if (keymap.is_modal):
					continue
				keymap_elem = ElementTree.SubElement(keyconfig_elem, 'KeyMap', {'name':keymap.name})
				for keymap_item in keymap.keymap_items:
					if (keymap_item.idname == ''):
						continue
					attrib = {'name':keymap_item.name}
					if (not keymap_item.active):
						attrib['Active'] = '0'
					keymap_item_elem = ElementTree.SubElement(keymap_elem, 'KeyMapItem', attrib)
					attrib = {}
					if (keymap_item.map_type != 'KEYBOARD'):
						attrib['Type'] = keymap_item.map_type
					if (keymap_item.value != 'PRESS'):
						attrib['Value'] = keymap_item.value
					if (keymap_item.any):
						attrib['Any'] = '1'
					else:
						if (keymap_item.shift):
							attrib['Shift'] = '1'
						if (keymap_item.ctrl):
							attrib['Ctrl'] = '1'
						if (keymap_item.alt):
							attrib['Alt'] = '1'
						if (keymap_item.oskey):
							attrib['OS'] = '1'
						if (keymap_item.key_modifier != 'NONE'):
							attrib['KeyModifier'] = keymap_item.key_modifier
					ElementTree.SubElement(keymap_item_elem, 'Key', attrib).text = keymap_item.type
					ElementTree.SubElement(keymap_item_elem, 'Command').text = keymap_item.idname
					if (keymap_item.properties):
						if (0 < len(keymap_item.properties.keys())):
							for property_name in keymap_item.properties.keys():
								property = keymap_item.properties[property_name]
								property_type = type(property).__name__
								if (property_type == 'IDPropertyGroup'):
									pass
								else:
									if (property != ''):
										property_elem = ElementTree.SubElement(keymap_item_elem, 'Property',
											{'Type':property_type,
											'Name':property_name})
										property_elem.text = str(property)
		string = minidom.parseString(ElementTree.tostring(data, encoding="utf-8")).toprettyxml()
		string = string.replace("</KeyMapItem>", "</KeyMapItem>\n\t\t\t")
		f = codecs.open(self.filepath, 'w', 'utf-8')
		f.write(string)
		f.close()
		return {'FINISHED'}
	def invoke(self, context, event):
		self.filepath = context.user_preferences.addons["Scramble Addon"].preferences.key_config_xml_path
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

class MoveKeyBindCategory(bpy.types.Operator):
	bl_idname = "ui.move_key_bind_category"
	bl_label = "展開しているキー割り当てのカテゴリを移動"
	bl_description = "展開しているキー割り当てを、他のカテゴリに移動します"
	bl_options = {'REGISTER', 'UNDO'}
	
	items = [
		('Window', "ウィンドウ", "", 1),
		('Screen', "スクリーン", "", 2),
		('Screen Editing', "スクリーン編集", "", 3),
		('View2D', "2Dビュー", "", 4),
		('Frames', "フレーム", "", 5),
		('Header', "ヘッダー", "", 6),
		('View2D Buttons List', "2Dビューボタンリスト", "", 7),
		('Property Editor', "プロパティエディター", "", 8),
		('3D View Generic', "3Dビュー全般", "", 9),
		('Grease Pencil', "グリースペンシル", "", 10),
		('Grease Pencil Stroke Edit Mode', "グリースペンシルストローク編集モード", "", 11),
		('Face Mask', "面のマスク", "", 12),
		('Weight Paint Vertex Selection', "ウェイトペイント頂点選択", "", 13),
		('Pose', "ポーズ", "", 14),
		('Object Mode', "オブジェクトモード", "", 15),
		('Paint Curve', "ペイントカーブ", "", 16),
		('Curve', "カーブ", "", 17),
		('Image Paint', "画像ペイント", "", 18),
		('Vertex Paint', "頂点ペイント", "", 19),
		('Weight Paint', "ウェイトペイント", "", 20),
		('Sculpt', "スカルプト", "", 21),
		('Mesh', "メッシュ", "", 22),
		('Armature', "アーマチュア", "", 23),
		('Metaball', "メタボール", "", 24),
		('Lattice', "ラティス", "", 25),
		('Particle', "パーティクル", "", 26),
		('Font', "フォント", "", 27),
		('Object Non-modal', "オブジェクト非モーダル", "", 28),
		('3D View', "3Dビュー", "", 29),
		('Outliner', "アウトライナー", "", 30),
		('Info', "情報", "", 31),
		('View3D Gesture Circle', "3Dビュージェスチャサークル", "", 32),
		('Gesture Border', "ジェスチャ境界", "", 33),
		('Gesture Zoom Border', "ジェスチャ境界ズーム", "", 34),
		('Gesture Straight Line', "ジェスチャ直線", "", 35),
		('Standard Modal Map', "標準モーダルマップ", "", 36),
		('Animation', "アニメーション", "", 37),
		('Animation Channels', "アニメーションチャンネル", "", 38),
		('Knife Tool Modal Map', "ナイフツールモーダルマップ", "", 39),
		('UV Editor', "UVエディター", "", 40),
		('Transform Modal Map', "トランスフォームモーダルマップ", "", 41),
		('UV Sculpt', "UVスカルプト", "", 42),
		('Paint Stroke Modal', "ペイントストロークモーダル", "", 43),
		('Mask Editing', "マスク編集", "", 44),
		('Markers', "マーカー", "", 45),
		('Timeline', "タイムライン", "", 46),
		('View3D Fly Modal', "3Dビューフライモーダル", "", 47),
		('View3D Walk Modal', "3Dビューウォークモーダル", "", 48),
		('View3D Rotate Modal', "3Dビュー回転モーダル", "", 49),
		('View3D Move Modal', "3Dビュー移動モーダル", "", 50),
		('View3D Zoom Modal', "3Dビューズームモーダル", "", 51),
		('View3D Dolly Modal', "3Dビュードリーモーダル", "", 52),
		('Graph Editor Generic', "グラフエディター全般", "", 53),
		('Graph Editor', "グラフエディター", "", 54),
		('Image Generic', "画像全般", "", 55),
		('Image', "画像", "", 56),
		('Node Generic', "ノード全般", "", 57),
		('Node Editor', "ノードエディター", "", 58),
		('File Browser', "ファイルブラウザー", "", 59),
		('File Browser Main', "ファイルブラウザーメイン", "", 60),
		('File Browser Buttons', "ファイルブラウザーボタン", "", 61),
		('Dopesheet', "ドープシート", "", 62),
		('NLA Generic', "NLA全般", "", 63),
		('NLA Channels', "NLAチャンネル", "", 64),
		('NLA Editor', "NLAエディター", "", 65),
		('Text Generic', "テキスト全般", "", 66),
		('Text', "テキスト", "", 67),
		('SequencerCommon', "シーケンサー共通", "", 68),
		('Sequencer', "シーケンサー", "", 69),
		('SequencerPreview', "シーケンサープレビュー", "", 70),
		('Logic Editor', "ロジックエディター", "", 71),
		('Console', "コンソール", "", 72),
		('Clip', "クリップ", "", 73),
		('Clip Editor', "クリップエディター", "", 74),
		('Clip Graph Editor', "クリップグラフエディター", "", 75),
		('Clip Dopesheet Editor', "クリップドープシートエディター", "", 76),
		]
	category = bpy.props.EnumProperty(items=items, name="移動先カテゴリ")
	
	def invoke(self, context, event):
		i = 0
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						i += 1
		if (i <= 0):
			self.report(type={'ERROR'}, message="展開中の割り当てが存在しません")
			return {'CANCELLED'}
		if (2 <= i):
			self.report(type={'ERROR'}, message="1つのみ割り当てを展開した状態で実行してください")
			return {'CANCELLED'}
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		for keymap in context.window_manager.keyconfigs.user.keymaps:
			if (not keymap.is_modal):
				for keymap_item in keymap.keymap_items:
					if (keymap_item.show_expanded):
						target_keymap = context.window_manager.keyconfigs.user.keymaps[self.category]
						target_keymap_item = target_keymap.keymap_items.new(
							idname=keymap_item.idname,
							type=keymap_item.type,
							value=keymap_item.value,
							any=keymap_item.any,
							shift=keymap_item.shift,
							ctrl=keymap_item.ctrl,
							alt=keymap_item.alt,
							oskey=keymap_item.oskey,
							key_modifier=keymap_item.key_modifier)
						for property_name in keymap_item.properties.keys():
							target_keymap_item.properties[property_name] = keymap_item.properties[property_name]
						keymap.keymap_items.remove(keymap_item)
						bpy.ops.ui.close_key_map_items()
						target_keymap.show_expanded_children = True
						target_keymap.show_expanded_items = True
						target_keymap_item.show_expanded = True
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

##########################
# オペレーター(システム) #
##########################

class RegisterBlendFile(bpy.types.Operator):
	bl_idname = "system.register_blend_file"
	bl_label = ".blendファイルをこのバージョンに関連付け"
	bl_description = ".blendファイルをこのBlender実行ファイルに関連付けます (WindowsOSのみ)"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\.blend", winreg.REG_SZ, 'blend_auto_file')
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\blend_auto_file\shell\open\command", winreg.REG_SZ, '"'+sys.argv[0]+'" "%1"')
		self.report(type={"INFO"}, message=".blendファイルをこの実行ファイルに関連付けました")
		return {'FINISHED'}

class RegisterBlendBackupFiles(bpy.types.Operator):
	bl_idname = "system.register_blend_backup_files"
	bl_label = "バックアップをこのバージョンに関連付け"
	bl_description = ".blend1 .blend2 などのバックアップファイルをこのBlender実行ファイルに関連付けます (WindowsOSのみ)"
	bl_options = {'REGISTER'}
	
	max = bpy.props.IntProperty(name=".blend1～.blendN まで", default=10, min=1, max=1000, soft_min=1, soft_max=1000)
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	def execute(self, context):
		winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\blend1_auto_file\shell\open\command", winreg.REG_SZ, '"'+sys.argv[0]+'" "%1"')
		for i in range(self.max):
			i += 1
			winreg.SetValue(winreg.HKEY_CURRENT_USER, r"Software\Classes\.blend"+str(i), winreg.REG_SZ, 'blend1_auto_file')
		self.report(type={"INFO"}, message="バックアップファイルをこの実行ファイルに関連付けました")
		return {'FINISHED'}

##########################
# オペレーター(アドオン) #
##########################

class UpdateScrambleAddon(bpy.types.Operator):
	bl_idname = "script.update_scramble_addon"
	bl_label = "Blender-Scramble-Addonを更新"
	bl_description = "Blender-Scramble-Addonをダウンロード・更新を済ませます"
	bl_options = {'REGISTER'}
	
	def execute(self, context):
		response = urllib.request.urlopen("https://github.com/saidenka/Blender-Scramble-Addon/archive/master.zip")
		tempDir = bpy.app.tempdir
		zipPath = os.path.join(tempDir, "Blender-Scramble-Addon-master.zip")
		addonDir = os.path.dirname(__file__)
		f = open(zipPath, "wb")
		f.write(response.read())
		f.close()
		zf = zipfile.ZipFile(zipPath, "r")
		for f in zf.namelist():
			if not os.path.basename(f):
				pass
			else:
				if ("Scramble Addon" in f):
					uzf = open(os.path.join(addonDir, os.path.basename(f)), 'wb')
					uzf.write(zf.read(f))
					uzf.close()
		zf.close()
		#self.report(type={"INFO"}, message="アドオンを更新しました、Blenderを再起動して下さい")
		context.window_manager.popup_menu(self.popup_menu, title="更新成功", icon='INFO')
		return {'FINISHED'}
	def popup_menu(self, unknown, context):
		unknown.layout.label("アドオンを更新しました、Blenderを再起動して下さい")

class ToggleDisabledMenu(bpy.types.Operator):
	bl_idname = "wm.toggle_disabled_menu"
	bl_label = "「追加項目のオン/オフ」の表示切り替え"
	bl_description = "ScrambleAddonによるメニューの末尾の「追加項目のオン/オフ」ボタンの表示/非表示を切り替えます"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu = not context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu
		for area in context.screen.areas:
			area.tag_redraw()
		return {'FINISHED'}

################
# サブメニュー #
################

class InputMenu(bpy.types.Menu):
	bl_idname = "USERPREF_HT_header_input"
	bl_label = "　ショートカット操作"
	bl_description = "ショートカットに関係する操作のメニューです"
	
	def draw(self, context):
		self.layout.operator(CloseKeyMapItems.bl_idname, icon="PLUGIN")
		self.layout.operator(MoveKeyBindCategory.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(ShowShortcutHtml.bl_idname, icon="PLUGIN")
		self.layout.operator(ShowEmptyShortcuts.bl_idname, icon="PLUGIN")
		self.layout.separator()
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, text="最後のコマンドをショートカットに登録", icon="PLUGIN").is_clipboard = False
		self.layout.operator(RegisterLastCommandKeyconfig.bl_idname, text="クリップボードのコマンドをショートカットに登録", icon="PLUGIN").is_clipboard = True
		self.layout.separator()
		self.layout.operator(ImportKeyConfigXml.bl_idname, icon="PLUGIN")
		self.layout.operator(ExportKeyConfigXml.bl_idname, icon="PLUGIN")

class SystemAssociateMenu(bpy.types.Menu):
	bl_idname = "USERPREF_HT_header_system_associate"
	bl_label = "　関連付け関係"
	bl_description = "関連付けに関係する操作のメニューです"
	
	def draw(self, context):
		self.layout.operator(RegisterBlendFile.bl_idname, icon="PLUGIN")
		self.layout.operator(RegisterBlendBackupFiles.bl_idname, icon="PLUGIN")

class AddonsMenu(bpy.types.Menu):
	bl_idname = "USERPREF_HT_header_scramble_addon"
	bl_label = "　Scramble Addon"
	bl_description = "Scramble Addonに関係する操作のメニューです"
	
	def draw(self, context):
		self.layout.operator(ToggleDisabledMenu.bl_idname, icon="PLUGIN")
		self.layout.operator(UpdateScrambleAddon.bl_idname, icon="PLUGIN")

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
		active_section = context.user_preferences.active_section
		if (active_section == 'INPUT'):
			self.layout.menu(InputMenu.bl_idname, icon="PLUGIN")
			try:
				keymap = context.window_manager.keyconfigs.addon.keymaps['temp']
			except KeyError:
				keymap = context.window_manager.keyconfigs.addon.keymaps.new('temp')
			if (1 <= len(keymap.keymap_items)):
				keymap_item = keymap.keymap_items[0]
			else:
				keymap_item = keymap.keymap_items.new('', 'W', 'PRESS')
			self.layout.prop(keymap_item, 'type', event=True, text="")
			self.layout.prop(keymap_item, 'shift', text="Shift")
			self.layout.prop(keymap_item, 'ctrl', text="Ctrl")
			self.layout.prop(keymap_item, 'alt', text="Alt")
			self.layout.prop(keymap_item, 'any', text="Any")
			self.layout.operator(SearchKeyBind.bl_idname, icon="PLUGIN")
		elif (active_section == 'FILES'):
			self.layout.menu(SystemAssociateMenu.bl_idname, icon="PLUGIN")
		elif (active_section == 'ADDONS'):
			self.layout.menu(AddonsMenu.bl_idname, icon="PLUGIN")
	if (context.user_preferences.addons["Scramble Addon"].preferences.use_disabled_menu):
		self.layout.operator('wm.toggle_menu_enable', icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
