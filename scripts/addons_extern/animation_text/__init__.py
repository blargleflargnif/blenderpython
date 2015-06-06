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
    "name": "Text Animate",
    "author": "Multiple Authors",
    "version": (0, 3, 0),
    "blender": (2, 74, 5),
    "location": "View3D > Toolshelf",
    "description": "Animate Text",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}

if "bpy" in locals():
    import importlib
    importlib.reload(text_counter)
    importlib.reload(text_scrambler)
    importlib.reload(typewritter)
    importlib.reload(typing_text)



else:
    from . import text_counter
    from . import text_scrambler
    from . import typewritter
    from . import typing_text


import bpy


# Register all operators and panels


def register():
    bpy.utils.register_module(__name__)




def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()