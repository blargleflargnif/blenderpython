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

bl_addon_info = {
    'name': 'Import/Export: Fluent mesh',
    'author': 'MattCragun',
    'version': '0.1',
    'blender': (2, 5, 3),
    'location': 'File > Import/Export > .msh ',
    'description': 'Import Fluent Mesh (.msh format)',
    'warning': '', # used for warning icon and text in addons panel
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Import/Export'}

import bpy


def menu_import(self, context):
    from io_mesh_msh import mshImport2
    self.layout.operator(mshImport2.MSHImporter.bl_idname, text="Fluent mesh files (.msh)").filepath = "*.msh"

def register():
    from io_mesh_msh import mshImport2
    bpy.types.register(mshImport2.MSHImporter)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    from io_mesh_msh import mshImport2
    bpy.types.unregister(mshImport2.MSHImporter)
    bpy.types.INFO_MT_file_import.remove(menu_import)

if __name__ == "__main__":
    register()
