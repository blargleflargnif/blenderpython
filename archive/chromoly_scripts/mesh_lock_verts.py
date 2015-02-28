# coding: utf-8

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
    'name': 'Lock Verts Menu',
    'author': 'chromoly',
    'version': (0, 3),
    'blender': (2, 5, 6),
    'api': 34765,
    'location': 'View3D > Shift + V',
    'url': '',
    'category': 'Mesh'}


import bpy
#from bpy.props import *


class VIEW3D_MT_lock_verts_menu(bpy.types.Menu):
    #bl_idname = 'mesh.lock_verts_menu'
    bl_label = "Lock Verts"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.lock', text='Lock Selected')
        layout.operator('mesh.lock', text='Lock Unselected').unselected=True
        layout.operator('mesh.unlock', text='Unlock')


# Register
def register():
    bpy.utils.register_module(__name__)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.items:
        if kmi.idname == 'mesh.rip_move':
            if kmi.type == 'V':
                kmi.shift = kmi.ctrl = True
                kmi.alt = kmi.oskey = False
    kmi = km.items.new('wm.call_menu', 'V', 'PRESS')
    #kmi.properties.name = 'mesh.lock_verts_menu'
    kmi.properties.name = 'VIEW3D_MT_lock_verts_menu'
    kmi.shift = True


def unregister():
    bpy.utils.unregister_module(__name__)

    km = bpy.context.window_manager.keyconfigs.active.keymaps['Mesh']
    for kmi in km.items:
        if kmi.idname == 'wm.call_menu':
            #if kmi.properties.name == 'mesh.lock_verts_menu':
            if kmi.properties.name == 'VIEW3D_MT_lock_verts_menu':
                km.items.remove(kmi)
        if kmi.idname == 'mesh.rip_move':
            if kmi.type == 'V':
                kmi.shift = kmi.ctrl = kmi.alt = kmi.oskey = False


if __name__ == '__main__':
    register()
