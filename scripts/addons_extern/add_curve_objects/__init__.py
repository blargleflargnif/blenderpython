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
# testscreenings, Alejandro Omar Chocano Vasquez, Jimmy Hazevoet, Adam Newgas, meta-androcto #


bl_info = {
    "name": "Objects",
    "author": "Multiple Authors",
    "version": (0, 1),
    "blender": (2, 74, 0),
    "location": "View3D > Add > Curve",
    "description": "Add extra curve object types",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Curve/Curve_Objects",
    "category": "Add Curve"}

if "bpy" in locals():
    import importlib
    importlib.reload(sapling)
#    importlib.reload(utils)
    importlib.reload(add_curve_aceous_galore)
    importlib.reload(add_curve_spirals)
    importlib.reload(add_curve_torus_knots)
    importlib.reload(add_curve_braid)
    importlib.reload(add_curve_curly)
    importlib.reload(add_curve_celtic_links)
    importlib.reload(add_curve_formulacurves)
    importlib.reload(add_curve_wires)


else:
    from . import sapling
#    from . import utils
    from . import add_curve_aceous_galore
    from . import add_curve_spirals
    from . import add_curve_torus_knots
    from . import add_curve_braid
    from . import add_curve_curly
    from . import add_curve_celtic_links
    from . import add_curve_formulacurves
    from . import add_curve_wires


import bpy


class INFO_MT_curve_extras_add(bpy.types.Menu):
    # Define the "Extras" menu
    bl_idname = "curve_extra_objects_add"
    bl_label = "Extra Objects"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("curve.tree_add",
            text="Sapling 3")
        layout.operator("mesh.curveaceous_galore",
            text="Curves Galore!")
        layout.operator("curve.spirals",
            text="Spirals")
        layout.operator("curve.torus_knot_plus",
            text="Torus Knot Plus")
        layout.operator("mesh.add_braid",
            text="Braid Knot")
        layout.operator("curve.curlycurve",
            text="Curly Curve")
        layout.operator("curve.celtic_links",
            text="Celtic Links")
        layout.operator("curve.formulacurves",
            text="Formula Curve")
        layout.operator("curve.wires",
            text="Curve Wires")

# Define "Extras" menu
def menu_func(self, context):
    self.layout.operator("curve.tree_add",
            text="Sapling 3!",
            icon="PLUGIN")
    self.layout.operator("mesh.curveaceous_galore",
            text="Curves Galore!",
            icon="PLUGIN")
    self.layout.operator("curve.torus_knot_plus",
            text="Torus Knot Plus",
            icon="PLUGIN")
    self.layout.operator("curve.spirals",
            text="Spirals",
            icon="PLUGIN")
    self.layout.operator("mesh.add_braid",
            text="Braid Knot",
            icon="PLUGIN")
    self.layout.operator("curve.curlycurve",
            text="Curly Curve",
            icon="PLUGIN")
    self.layout.operator("curve.celtic_links",
            text="Celtic Links",
            icon="PLUGIN")
    self.layout.operator("curve.formulacurves",
            text="Formula Curve",
            icon="PLUGIN")
    self.layout.operator("curve.wires",
            text="Curve Wires",
            icon="PLUGIN")


def register():
    bpy.utils.register_module(__name__)

    # Add "Extras" menu to the "Add Curve" menu
    bpy.types.INFO_MT_curve_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)

    # Remove "Extras" menu from the "Add Curve" menu.
    bpy.types.INFO_MT_curve_add.remove(menu_func)

if __name__ == "__main__":
    register()
