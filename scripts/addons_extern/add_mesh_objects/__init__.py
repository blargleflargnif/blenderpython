# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Contributed to by
# Pontiac, Fourmadmen, varkenvarken, tuga3d, meta-androcto, metalliandy, dreampainter, cotejrp1 #
# liero, Kayo Phoenix, sugiany, dommetysk, Phymec, Anthony D'Agostino, Pablo Vazquez, Richard Wilks #
# xyz presets by elfnor

from .add_mesh_icicle_snowflake import add_mesh_icicle_gen
from .add_mesh_icicle_snowflake import add_mesh_snowflake
from .add_mesh_siding_wall import add_mesh_drystone
from .add_mesh_siding_wall import add_mesh_floor_planks
from .add_mesh_siding_wall import add_mesh_plancher
from .add_mesh_siding_wall import add_mesh_siding
from .add_ant_erosion import erode
from .add_ant_erosion import erosion

bl_info = {
    "name": "Object Factory",
    "author": "Multiple Authors",
    "version": (0, 3, 0),
    "blender": (2, 74, 5),
    "location": "View3D > Add > Mesh",
    "description": "Add extra mesh object types",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Add_Mesh/Add_Extra",
    "category": "Add Mesh",
}

if "bpy" in locals():
    import importlib
    importlib.reload(add_mesh_star)
    importlib.reload(add_mesh_twisted_torus)
    importlib.reload(add_mesh_gemstones)
    importlib.reload(add_mesh_gears)
    importlib.reload(add_mesh_3d_function_surface)
    importlib.reload(add_mesh_round_cube)
    importlib.reload(add_mesh_supertoroid)
    importlib.reload(add_mesh_pyramid)
    importlib.reload(add_mesh_torusknot)
    importlib.reload(add_mesh_honeycomb)
    importlib.reload(add_mesh_teapot)
    importlib.reload(add_mesh_pipe_joint)
    importlib.reload(add_mesh_solid)
    importlib.reload(add_mesh_round_brilliant)
    importlib.reload(add_mesh_menger_sponge)
    importlib.reload(add_mesh_vertex)
    importlib.reload(add_empty_as_parent)
    importlib.reload(add_mesh_ant_landscape_modified)
    importlib.reload(add_mesh_cave_gen)
    importlib.reload(add_mesh_lowpoly_rock)
    importlib.reload(fractalDome)
    importlib.reload(Boltactory)
    importlib.reload(add_mesh_beam_builder)

else:
    from . import add_mesh_star
    from . import add_mesh_twisted_torus
    from . import add_mesh_gemstones
    from . import add_mesh_gears
    from . import add_mesh_3d_function_surface
    from . import add_mesh_round_cube
    from . import add_mesh_supertoroid
    from . import add_mesh_pyramid
    from . import add_mesh_torusknot
    from . import add_mesh_honeycomb
    from . import add_mesh_teapot
    from . import add_mesh_pipe_joint
    from . import add_mesh_solid
    from . import add_mesh_round_brilliant
    from . import add_mesh_menger_sponge
    from . import add_mesh_vertex
    from . import add_empty_as_parent
    from . import add_mesh_ant_landscape_modified
    from . import add_mesh_cave_gen
    from . import add_mesh_lowpoly_rock
    from . import fractalDome
    from . import Boltfactory
    from . import add_mesh_beam_builder


import bpy

class INFO_MT_mesh_ant_add(bpy.types.Menu):
    # Define the "Ice" menu
    bl_idname = "INFO_MT_mesh_ant_add"
    bl_label = "ANT Mod"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.landscape_modified_add",
            text="ANT Landscape")
        layout.label(text="Use Erode After ANT")
        layout.operator("mesh.erode",
            text="Erosion")

class INFO_MT_mesh_vert_add(bpy.types.Menu):
    # Define the "Pipe Joints" menu
    bl_idname = "INFO_MT_mesh_vert_add"
    bl_label = "Single Vert"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_vert_add",
            text="Add Single Vert ")
        layout.operator("mesh.primitive_emptyvert_add",
            text="Object Origin Only")
        layout.operator("mesh.primitive_symmetrical_vert_add",
            text="Origin & Vert Mirrored")
        layout.operator("mesh.primitive_symmetrical_empty_add",
            text="Object Origin Mirrored")


class INFO_MT_mesh_gears_add(bpy.types.Menu):
    # Define the "Gears" menu
    bl_idname = "INFO_MT_mesh_gears_add"
    bl_label = "Gears"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_gear",
            text="Gear")
        layout.operator("mesh.primitive_worm_gear",
            text="Worm")


class INFO_MT_mesh_diamonds_add(bpy.types.Menu):
    # Define the "Gears" menu
    bl_idname = "INFO_MT_mesh_diamonds_add"
    bl_label = "Diamonds"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_brilliant_add",
            text="Brilliant Diamond")
        layout.operator("mesh.primitive_diamond_add",
            text="Diamond")
        layout.operator("mesh.primitive_gem_add",
            text="Gem")


class INFO_MT_mesh_math_add(bpy.types.Menu):
    # Define the "Math Function" menu
    bl_idname = "INFO_MT_mesh_math_add"
    bl_label = "Math Functions"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_z_function_surface",
            text="Z Math Surface")
        layout.operator("mesh.primitive_xyz_function_surface",
            text="XYZ Math Surface")
        self.layout.operator("mesh.primitive_solid_add", text="Regular Solid")


class INFO_MT_mesh_extras_add(bpy.types.Menu):
    # Define the "Simple Objects" menu
    bl_idname = "INFO_MT_mesh_extras_add"
    bl_label = "Extras"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.menu("INFO_MT_mesh_diamonds_add", text="Diamonds", icon="PMARKER_SEL")
        layout.operator("mesh.primitive_star_add",
            text="Simple Star")
        layout.operator("mesh.primitive_steppyramid_add",
            text="Step Pyramid")
        layout.operator("mesh.honeycomb_add",
            text="Honeycomb")
        layout.operator("mesh.primitive_teapot_add",
            text="Teapot+")
        layout.operator("mesh.menger_sponge_add",
            text="Menger Sponge")
        layout.operator("mesh.primitive_cave_gen",
            text="Cave Gen")
        layout.operator("mesh.lowpoly_rock_add",
            text="Low Poly Rock")
        layout.operator("mesh.fractal_dome",
            text="Fractal Dome")


class INFO_MT_mesh_torus_add(bpy.types.Menu):
    # Define the "Simple Objects" menu
    bl_idname = "INFO_MT_mesh_torus_add"
    bl_label = "Torus Objects"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_twisted_torus_add",
            text="Twisted Torus")
        layout.operator("mesh.primitive_supertoroid_add",
            text="Supertoroid")
        layout.operator("mesh.primitive_torusknot_add",
            text="Torus Knot")


class INFO_MT_mesh_pipe_joints_add(bpy.types.Menu):
    # Define the "Pipe Joints" menu
    bl_idname = "INFO_MT_mesh_pipe_joints_add"
    bl_label = "Pipe Joints"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_elbow_joint_add",
            text="Pipe Elbow")
        layout.operator("mesh.primitive_tee_joint_add",
            text="Pipe T-Joint")
        layout.operator("mesh.primitive_wye_joint_add",
            text="Pipe Y-Joint")
        layout.operator("mesh.primitive_cross_joint_add",
            text="Pipe Cross-Joint")
        layout.operator("mesh.primitive_n_joint_add",
            text="Pipe N-Joint")

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

class INFO_MT_mesh_floorwall_add(bpy.types.Menu):
    # Define the "Ice" menu
    bl_idname = "INFO_MT_mesh_floorwall_add"
    bl_label = "Floors & Walls"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.primitive_add_siding",
            text = "Siding")
        layout.operator("mesh.drystone",
            text="Drystone")
        layout.operator("mesh.floor_boards_add",
            text="Floor Boards")
        layout.operator("mesh.ajout_primitive",
            text="Plancher")

# Register all operators and panels
class AddonPreferences1(bpy.types.AddonPreferences):
	bl_idname = __name__
	
	disabled_menu = bpy.props.StringProperty(name="Object Factory", default="")
	use_disabled_menu = bpy.props.BoolProperty(name="Turn On/Off Toggle Option", default=True)
	
	def draw(self, context):
		layout = self.layout
		layout.label(text="Use with or without Toggle option.")
		layout.prop(self, 'disabled_menu')
		layout.prop(self, 'use_disabled_menu')

# ?????????/??
class ToggleMenuEnable1(bpy.types.Operator):
	bl_idname = "wm.toggle_menu_enable1"
	bl_label = "Toggle Menu"
	bl_description = "Turn off on Additional Items"
	bl_options = {'REGISTER', 'UNDO'}
	
	id = bpy.props.StringProperty()
	
	def execute(self, context):
		recovery = ""
		is_on = False
		for id in context.user_preferences.addons["add_mesh_objects"].preferences.disabled_menu.split(','):
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
		context.user_preferences.addons["add_mesh_objects"].preferences.disabled_menu = recovery
		return {'FINISHED'}

def IsMenuEnable(self_id):
	for id in bpy.context.user_preferences.addons["add_mesh_objects"].preferences.disabled_menu.split(','):
		if (id == self_id):
			return False
	else:
		return True
# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
	if (IsMenuEnable(__name__.split('.')[-1])):
		layout = self.layout
		col = layout.column()
		self.layout.separator()
		layout.label(text="Object Factory")
		self.layout.menu("INFO_MT_mesh_ant_add", text="Landscape", icon="RNDCURVE")
		self.layout.menu("INFO_MT_mesh_vert_add", text="Single Vert", icon="LAYER_ACTIVE")
		self.layout.menu("INFO_MT_mesh_round_cube_add", text="Round Cube", icon="WIRE")
		self.layout.menu("INFO_MT_mesh_math_add", text="Math Function", icon="PACKAGE")
		self.layout.operator("mesh.bolt_add", text="Add Bolt", icon="CURSOR")
		self.layout.menu("INFO_MT_mesh_pipe_joints_add", text="Pipe Joints", icon="SNAP_PEEL_OBJECT")
		self.layout.menu("INFO_MT_mesh_gears_add", text="Gears", icon="SCRIPTWIN")
		self.layout.menu("INFO_MT_mesh_beambuilder_add", text="Beam Builder", icon="NOCURVE")
		self.layout.menu("INFO_MT_mesh_torus_add", text="Torus Objects", icon="MESH_TORUS")
		self.layout.menu("INFO_MT_mesh_extras_add", text="Extras", icon="MESH_DATA")
		self.layout.separator()
		self.layout.operator("object.parent_to_empty", text="Parent To Empty", icon="LINK_AREA")
		self.layout.separator()
		self.layout.menu("INFO_MT_mesh_floorwall_add", text="Floors & Walls", icon = "UV_ISLANDSEL")
		self.layout.menu("INFO_MT_mesh_ice_add", text="Ice & Snow", icon="FREEZE")

	if (context.user_preferences.addons["add_mesh_objects"].preferences.use_disabled_menu):
		layout = self.layout
		col = layout.column()
		self.layout.separator()
		self.layout.operator('wm.toggle_menu_enable1', text="Object Factory Toggle", icon='VISIBLE_IPO_ON').id = __name__.split('.')[-1]
		self.layout.separator()

def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Mesh" menu
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    # Remove "Extras" menu from the "Add Mesh" menu.
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
