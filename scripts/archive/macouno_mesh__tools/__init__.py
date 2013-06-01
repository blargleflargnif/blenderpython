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

bl_info = {
    "name": "Mesh_Select_Tools",
    "author": "Macouno",
    "version": (0, 1),
    "blender": (2, 5, 8),
    "api": 35853,
    "location": "Editmode select menu",
    "description": "Adds More vert/face select modes.",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=22457",
    "category": "Mesh"}


if "bpy" in locals():
    import imp
    imp.reload(mesh_select_by_direction)
    imp.reload(mesh_select_by_edge_length)
    imp.reload(mesh_select_by_pi)
    imp.reload(mesh_select_checkered)
    imp.reload(mesh_select_connected_faces)
    imp.reload(mesh_select_innermost)
    imp.reload(mesh_select_nonmanifold_edges)
else:
    from . import mesh_select_by_direction
    from . import mesh_select_by_edge_length
    from . import mesh_select_by_pi
    from . import mesh_select_checkered
    from . import mesh_select_connected_faces
    from . import mesh_select_innermost
    from . import mesh_select_nonmanifold_edges

import bpy


class VIEW3D_MT_select_edit_mesh_add(bpy.types.Menu):
    # Define the "Mesh_Select_Tools" menu
    bl_idname = "mesh.mesh_select_tools"
    bl_label = "Mesh Select Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("mesh.select_by_direction",
            text="by_direction")
        layout.operator("mesh.select_by_edge_length",
            text="by_edge_length")
        layout.operator("mesh.select_by_pi",
            text="by_pi")
        layout.operator("mesh.select_checkered",
            text="checkered")
        layout.operator("mesh.select_connected_faces",
            text="connected_faces")
        layout.operator("mesh.select_innermost",
            text="innermost")

# Register all operators and panels

# Define "Extras" menu
def menu_func(self, context):
    self.layout.menu("mesh.mesh_select_tools", icon="PLUGIN")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_select_edit_mesh.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_select_edit_mesh.remove(menu_func)

if __name__ == "__main__":
	register()
