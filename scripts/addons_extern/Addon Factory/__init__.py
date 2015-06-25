# Initially this file is loaded when you load the add-on.

import os, csv, codecs

from .add_menu import INFO_MT_add
from .add_curve_objects import INFO_MT_curve_add
from .add_mesh_objects import INFO_MT_mesh_add
from .add_surface_objects import INFO_MT_surface_add
from .armature import VIEW3D_MT_armature_specials
from .armature import VIEW3D_MT_bone_options_toggle
from .armature import VIEW3D_MT_edit_armature
from .edit_mesh import VIEW3D_MT_edit_mesh
from .edit_mesh import VIEW3D_MT_edit_mesh_delete
from .edit_mesh import VIEW3D_MT_edit_mesh_showhide
from .edit_mesh import VIEW3D_MT_edit_mesh_specials
from .edit_mesh import VIEW3D_MT_edit_mesh_vertices
from .file import INFO_MT_file
from .file import INFO_MT_file_external_data
from .header import PROPERTIES_HT_header
from .header import USERPREF_HT_header
from .help import INFO_MT_help
from .image import IMAGE_MT_image
from .image import IMAGE_MT_select
from .image import IMAGE_MT_view
from .materials import MATERIAL_MT_specials
from .tools_panels import VIEW3D_MT_tools_panels
from .modifiers import DATA_PT_modifiers
from .node import NODE_MT_node
from .object import VIEW3D_MT_make_links
from .object import VIEW3D_MT_object
from .object import VIEW3D_MT_object_showhide
from .object import VIEW3D_MT_object_specials
from .object import VIEW3D_MT_object_apply
from .pie_menu import INFO_MT_window
from .pose import VIEW3D_MT_pose_constraints
from .pose import VIEW3D_MT_pose_showhide
from .pose import VIEW3D_MT_pose_specials
from .render import INFO_MT_render
from .select import VIEW3D_MT_select_edit_mesh
from .select import VIEW3D_MT_select_pose
from .select import VIEW3D_MT_select_edit_armature
from .select import VIEW3D_MT_select_object
from .shape_keys import MESH_MT_shape_key_specials
from .texture import TEXTURE_MT_specials
from .uv_texture import DATA_PT_uv_texture
from .uv_texture import VIEW3D_MT_uv_map
from .vertex_colors import DATA_PT_vertex_colors
from .vertex_group import MESH_MT_vertex_group_specials
from .vertex_paint import VIEW3D_MT_paint_weight
from .view_3d import VIEW3D_MT_view
from .view_3d import VIEW3D_MT_view_align
from .view_3d import VIEW3D_MT_view_align_selected
from .view_3d import VIEW3D_MT_snap
from .shading import VIEW3D_PT_view3d_shading


# Blender Addon Information
bl_info = {
	"name" : "Addon Factory",
	"author" : "さいでんか(saidenka), meta-androcto, various",
	"version" : (0,1),
	"blender" : (2, 7),
	"location" : "Everywhere",
	"description" : "Extended Menu's",
	"warning" : "",
	"wiki_url" : "http://github.com/saidenka/Blender-Scramble-Addon",
	"tracker_url" : "http://github.com/saidenka/Blender-Scramble-Addon/issues",
	"category" : "Addon Factory"
}

# get the py modules

if "bpy" in locals():
	import importlib
	importlib.reload(DOPESHEET_MT_key)


else:
	from . import DOPESHEET_MT_key

import bpy

bpy.context.user_preferences.system.use_international_fonts = True
bpy.context.user_preferences.system.language = 'en_US'
bpy.context.user_preferences.system.use_translate_interface = True
bpy.context.user_preferences.system.use_translate_tooltips = True

# Addons Preferences
class AddonPreferences(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	disabled_menu = bpy.props.StringProperty(name="Disable Menu", default="")
	use_disabled_menu = bpy.props.BoolProperty(name="Use Disabled menu", default=True)
	view_savedata = bpy.props.StringProperty(name="View Saved Data", default="")
	key_config_xml_path = bpy.props.StringProperty(name="XML Key Path Config", default="BlenderKeyConfig.xml")
	
	def draw(self, context):
		layout = self.layout
		layout.prop(self, 'disabled_menu')
		layout.prop(self, 'use_disabled_menu')
		layout.prop(self, 'view_savedata')
		layout.prop(self, 'key_config_xml_path')

# 追加メニューの有効/無効
class ToggleMenuEnable(bpy.types.Operator):
	bl_idname = "wm.toggle_menu_enable"
	bl_label = "Menu Enable Toggle"
	bl_description = "Scramble on/off"
	bl_options = {'REGISTER', 'UNDO'}
	
	id = bpy.props.StringProperty()
	
	def execute(self, context):
		recovery = ""
		is_on = False
		for id in context.user_preferences.addons["Addon Factory"].preferences.disabled_menu.split(','):
			if (id == ""):
				continue
			if (id == self.id):
				is_on = True
			else:
				recovery = recovery + id + ","
		if (not is_on):
			recovery = recovery + self.id + ","
		if (recovery != ""):
			if (recovery[-1] == ","):
				recovery = recovery[:-1]
		context.user_preferences.addons["Addon Factory"].preferences.disabled_menu = recovery
		return {'FINISHED'}

# 翻訳辞書の取得
def GetTranslationDict():
	dict = {'en':{}}
	path = os.path.join(os.path.dirname(__file__), "TranslationDictionary.csv")
	with codecs.open(path, 'r', 'utf-8') as f:
		reader = csv.reader(f)
		for row in reader:
			#for context in bpy.app.translations.contexts:
			dict['en'][(bpy.app.translations.contexts.default, row[0])] = row[1]
			dict['en'][(bpy.app.translations.contexts.operator_default, row[0])] = row[1]
	return dict

# プラグインをインストールしたときの処理
def register():
	bpy.utils.register_module(__name__)
	
	translation_dict = GetTranslationDict()
	bpy.app.translations.register(__name__, translation_dict)

	bpy.types.INFO_MT_add.append(INFO_MT_add.menu)
	bpy.types.INFO_MT_mesh_add.append(INFO_MT_mesh_add.menu)
	bpy.types.INFO_MT_curve_add.append(INFO_MT_curve_add.menu)
	bpy.types.INFO_MT_surface_add.append(INFO_MT_surface_add.menu)
	bpy.types.IMAGE_MT_image.append(IMAGE_MT_image.menu)
	bpy.types.IMAGE_MT_select.append(IMAGE_MT_select.menu)
	bpy.types.IMAGE_MT_view.append(IMAGE_MT_view.menu)
	bpy.types.INFO_MT_file.append(INFO_MT_file.menu)
	bpy.types.INFO_MT_file_external_data.append(INFO_MT_file_external_data.menu)
	bpy.types.INFO_MT_render.append(INFO_MT_render.menu)
	bpy.types.INFO_MT_window.append(INFO_MT_window.menu)
	bpy.types.MATERIAL_MT_specials.append(MATERIAL_MT_specials.menu)
	bpy.types.MESH_MT_shape_key_specials.append(MESH_MT_shape_key_specials.menu)
	bpy.types.MESH_MT_vertex_group_specials.append(MESH_MT_vertex_group_specials.menu)
	bpy.types.NODE_MT_node.append(NODE_MT_node.menu)
	bpy.types.TEXTURE_MT_specials.append(TEXTURE_MT_specials.menu)
	bpy.types.VIEW3D_MT_armature_specials.append(VIEW3D_MT_armature_specials.menu)
	bpy.types.VIEW3D_MT_bone_options_toggle.append(VIEW3D_MT_bone_options_toggle.menu)
	bpy.types.VIEW3D_MT_edit_armature.append(VIEW3D_MT_edit_armature.menu)
	bpy.types.VIEW3D_MT_edit_mesh.append(VIEW3D_MT_edit_mesh.menu)
	bpy.types.VIEW3D_MT_edit_mesh_delete.append(VIEW3D_MT_edit_mesh_delete.menu)
	bpy.types.VIEW3D_MT_edit_mesh_showhide.append(VIEW3D_MT_edit_mesh_showhide.menu)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(VIEW3D_MT_edit_mesh_specials.menu)
	bpy.types.VIEW3D_MT_make_links.append(VIEW3D_MT_make_links.menu)
	bpy.types.VIEW3D_MT_object.append(VIEW3D_MT_object.menu)
	bpy.types.VIEW3D_MT_object_showhide.append(VIEW3D_MT_object_showhide.menu)
	bpy.types.VIEW3D_MT_object_specials.append(VIEW3D_MT_object_specials.menu)
	bpy.types.VIEW3D_MT_paint_weight.append(VIEW3D_MT_paint_weight.menu)
	bpy.types.VIEW3D_MT_pose_constraints.append(VIEW3D_MT_pose_constraints.menu)
	bpy.types.VIEW3D_MT_pose_showhide.append(VIEW3D_MT_pose_showhide.menu)
	bpy.types.VIEW3D_MT_pose_specials.append(VIEW3D_MT_pose_specials.menu)
	bpy.types.VIEW3D_MT_select_edit_mesh.append(VIEW3D_MT_select_edit_mesh.menu)
	bpy.types.VIEW3D_MT_select_pose.append(VIEW3D_MT_select_pose.menu)
	bpy.types.VIEW3D_MT_view.prepend(VIEW3D_MT_view.menu)
	bpy.types.VIEW3D_MT_view_align.append(VIEW3D_MT_view_align.menu)
	bpy.types.VIEW3D_MT_select_edit_armature.append(VIEW3D_MT_select_edit_armature.menu)
	bpy.types.VIEW3D_MT_edit_mesh_vertices.append(VIEW3D_MT_edit_mesh_vertices.menu)
	bpy.types.INFO_MT_help.append(INFO_MT_help.menu)
	bpy.types.DOPESHEET_MT_key.append(DOPESHEET_MT_key.menu)
	bpy.types.VIEW3D_MT_select_object.append(VIEW3D_MT_select_object.menu)
	bpy.types.VIEW3D_MT_object_apply.append(VIEW3D_MT_object_apply.menu)
	bpy.types.VIEW3D_MT_view_align_selected.append(VIEW3D_MT_view_align_selected.menu)
	bpy.types.VIEW3D_MT_snap.append(VIEW3D_MT_snap.menu)
	bpy.types.VIEW3D_MT_uv_map.append(VIEW3D_MT_uv_map.menu)
	bpy.types.USERPREF_HT_header.append(USERPREF_HT_header.menu)
	bpy.types.PROPERTIES_HT_header.append(PROPERTIES_HT_header.menu)
	bpy.types.DATA_PT_modifiers.append(DATA_PT_modifiers.menu)
	bpy.types.DATA_PT_uv_texture.append(DATA_PT_uv_texture.menu)
	bpy.types.DATA_PT_vertex_colors.append(DATA_PT_vertex_colors.menu)
	bpy.types.VIEW3D_PT_view3d_shading.append(VIEW3D_PT_view3d_shading.menu)
	
# プラグインをアンインストールしたときの処理
def unregister():

	
	bpy.app.translations.unregister(__name__)

	bpy.types.INFO_MT_add.remove(INFO_MT_add.menu)
	bpy.types.INFO_MT_mesh_add.remove(INFO_MT_mesh_add.menu)
	bpy.types.INFO_MT_curve_add.remove(INFO_MT_curve_add.menu)
	bpy.types.INFO_MT_surface_add.remove(INFO_MT_surface_add.menu)		
	bpy.types.IMAGE_MT_image.remove(IMAGE_MT_image.menu)
	bpy.types.IMAGE_MT_select.remove(IMAGE_MT_select.menu)
	bpy.types.IMAGE_MT_view.remove(IMAGE_MT_view.menu)
	bpy.types.INFO_MT_file.remove(INFO_MT_file.menu)
	bpy.types.INFO_MT_file_external_data.remove(INFO_MT_file_external_data.menu)
	bpy.types.INFO_MT_render.remove(INFO_MT_render.menu)
	bpy.types.INFO_MT_window.remove(INFO_MT_window.menu)
	bpy.types.MATERIAL_MT_specials.remove(MATERIAL_MT_specials.menu)
	bpy.types.MESH_MT_shape_key_specials.remove(MESH_MT_shape_key_specials.menu)
	bpy.types.MESH_MT_vertex_group_specials.remove(MESH_MT_vertex_group_specials.menu)
	bpy.types.NODE_MT_node.remove(NODE_MT_node.menu)
	bpy.types.TEXTURE_MT_specials.remove(TEXTURE_MT_specials.menu)
	bpy.types.VIEW3D_MT_armature_specials.remove(VIEW3D_MT_armature_specials.menu)
	bpy.types.VIEW3D_MT_bone_options_toggle.remove(VIEW3D_MT_bone_options_toggle.menu)
	bpy.types.VIEW3D_MT_edit_armature.remove(VIEW3D_MT_edit_armature.menu)
	bpy.types.VIEW3D_MT_edit_mesh.remove(VIEW3D_MT_edit_mesh.menu)
	bpy.types.VIEW3D_MT_edit_mesh_delete.remove(VIEW3D_MT_edit_mesh_delete.menu)
	bpy.types.VIEW3D_MT_edit_mesh_showhide.remove(VIEW3D_MT_edit_mesh_showhide.menu)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(VIEW3D_MT_edit_mesh_specials.menu)
	bpy.types.VIEW3D_MT_make_links.remove(VIEW3D_MT_make_links.menu)
	bpy.types.VIEW3D_MT_object.remove(VIEW3D_MT_object.menu)
	bpy.types.VIEW3D_MT_object_showhide.remove(VIEW3D_MT_object_showhide.menu)
	bpy.types.VIEW3D_MT_object_specials.remove(VIEW3D_MT_object_specials.menu)
	bpy.types.VIEW3D_MT_paint_weight.remove(VIEW3D_MT_paint_weight.menu)
	bpy.types.VIEW3D_MT_pose_constraints.remove(VIEW3D_MT_pose_constraints.menu)
	bpy.types.VIEW3D_MT_pose_showhide.remove(VIEW3D_MT_pose_showhide.menu)
	bpy.types.VIEW3D_MT_pose_specials.remove(VIEW3D_MT_pose_specials.menu)
	bpy.types.VIEW3D_MT_select_edit_mesh.remove(VIEW3D_MT_select_edit_mesh.menu)
	bpy.types.VIEW3D_MT_select_pose.remove(VIEW3D_MT_select_pose.menu)
	bpy.types.VIEW3D_MT_view.remove(VIEW3D_MT_view.menu)
	bpy.types.VIEW3D_MT_view_align.remove(VIEW3D_MT_view_align.menu)
	bpy.types.VIEW3D_MT_select_edit_armature.remove(VIEW3D_MT_select_edit_armature.menu)
	bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(VIEW3D_MT_edit_mesh_vertices.menu)
	bpy.types.INFO_MT_help.remove(INFO_MT_help.menu)
	bpy.types.DOPESHEET_MT_key.remove(DOPESHEET_MT_key.menu)
	bpy.types.VIEW3D_MT_select_object.remove(VIEW3D_MT_select_object.menu)
	bpy.types.VIEW3D_MT_object_apply.remove(VIEW3D_MT_object_apply.menu)
	bpy.types.VIEW3D_MT_view_align_selected.remove(VIEW3D_MT_view_align_selected.menu)
	bpy.types.VIEW3D_MT_snap.remove(VIEW3D_MT_snap.menu)
	bpy.types.VIEW3D_MT_uv_map.remove(VIEW3D_MT_uv_map.menu)
	bpy.types.USERPREF_HT_header.remove(USERPREF_HT_header.menu)
	bpy.types.PROPERTIES_HT_header.remove(PROPERTIES_HT_header.menu)
	bpy.types.DATA_PT_modifiers.remove(DATA_PT_modifiers.menu)
	bpy.types.DATA_PT_uv_texture.remove(DATA_PT_uv_texture.menu)
	bpy.types.DATA_PT_vertex_colors.remove(DATA_PT_vertex_colors.menu)
	bpy.types.VIEW3D_PT_view3d_shading.remove(VIEW3D_PT_view3d_shading.menu)

	bpy.utils.unregister_module(__name__)
# メイン関数
if __name__ == "__main__":
	register()
