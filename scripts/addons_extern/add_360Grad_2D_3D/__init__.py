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
    'name': 'Fulldome Tools',
    'author': 'Jesse Cole Wilmot',
    'description': 'Tool to create a 360 degrees camera rig and projection planes for 2D/3D animations',
    'version': (0, 0, 2),
    'blender': (2, 6, 5),
    'location': 'View3D > Tool Shelf > Fulldome Tools',
    'url': '',
    "wiki_url": "http://fh-flensburg.de",
    "tracker_url": "fh-flensburg.de",
    'category': 'Render'
}


if "bpy" in locals():
    import imp
    imp.reload(add_360Grad_2D3D)
else:
    from . import add_360Grad_2D3D


import bpy
from bpy.props import *


# global properties for the script, mainly for UI
class fulldomePropertyGroup(bpy.types.PropertyGroup):
    set_TextObject = BoolProperty(
            name ="3D Text",
            default= True,
            description="Set Text to 3D")
    set_sampleSetting = BoolProperty(
            name ="Sample Setting",
            default= False,
            description="add Sample Texture and Lightsetting")
    set_TextObject_path = StringProperty(
            name="Text Path",
            description="From this path text is loaded",
            subtype='FILE_PATH')
    set_SkyShine = BoolProperty(
            name ="Illuminated Sky",
            default= True,
            description="Sets selfillumination of the Skysphere")
    use_skytexture = BoolProperty(
            name="Use Skytexture",
            default=False,
            description="Skytexture enabled")
    texture_path_skysphere = StringProperty(
            name="Skytexture Path",
            description="From this path textures for the Skysphere will be loaded",
            subtype='FILE_PATH')
    set_MovieShine = BoolProperty(
            name = "Illuminated Movieplane",
            default= True,
            description="Sets selfillumination of the Movieplane")
    set_MovieSize = BoolProperty(
            name = "Moviesize",
            default= True,
            description="Sets Planesize to Moviesize")
    use_alphatexture = BoolProperty(
            name="Use Alphatexture",
            default=False,
            description="Alphatexture enabled")
    alphamovie_texture_path = StringProperty(
            name="Alphamovie Path",
            description="From this path textures for the AlpaMovieTexture will be loaded",
            subtype='FILE_PATH')
    movie_texture_path = StringProperty(
            name="Movie Path",
            description="From this path textures for the Movietexture will be loaded",
            subtype='FILE_PATH')
    render_size = EnumProperty(
            name="Rendersize",
            description="Choose rendering size",
            items=(('OPT_A', "1 K ", "Size 1K"),
                   ('OPT_B', "2 K ", "Size 2K"),
                   ('OPT_C', "3 K ", "Size 3K"),
                   ('OPT_D', "4 K ", "Size 4K"),
                   ('OPT_E', "8 k ", "Size 8K")),
                   default='OPT_A')
    use_orthographic = BoolProperty(
            name="Use Orthographic Camerasetting",
            default=True,
            description="orthographic Camerasetting enabled")
    activate_Clear = BoolProperty(
            name="Activate Clear",
            default=False,
            description="activate Clear Button")
    clear_complete_Rig = BoolProperty(
            name="Clear Complete Rig",
            default=False,
            description="activate clear of Complete Rig")




def register():
    # register properties
    bpy.utils.register_class(fulldomePropertyGroup)
    bpy.types.Scene.fulldome = bpy.props.PointerProperty(type=fulldomePropertyGroup)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
