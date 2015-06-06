#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import bpy, string, random
from bpy.app.handlers import persistent


bl_info = {
    'name': 'Text scrambler',
    'author': 'Martin Wacker',
    'version': '0.1',
    'blender': (2, 6, 5),
    'location': 'Properties Editor, Text Context',
    'description': 'Text scrambler effect. Based on Bassam Kurdali\'s Typewriter Text effect',
    'url': 'mailto:martas@imm.cz',
    'category': 'Animation'}

__bpydoc__ = """
Text scrambler For Font Objects
"""


def uptext(text):
 source = text.source_text
 if source in bpy.data.texts: r = bpy.data.texts[source].as_string()
 else: r = source
 
 base = len(r)
 prog = text.scrambler_progress / 100.0
 
 c = int(base * prog)
 
 clean     = r[:base-c]
 scrambled = ""
 for i in range(c): scrambled += random.choice(text.characters)
 text.body = clean+scrambled
 

@persistent   
def textscrambler_update_frame(scene):
 for text in scene.objects:
  if text.type == 'FONT' and text.data.use_text_scrambler:
   uptext(text.data)

def update_func(self, context):
 uptext(self)
   
   
class TEXT_PT_Textscrambler(bpy.types.Panel):
 bl_label       = "Text scrambler"
 bl_idname      = "TEXT_PT_Textscrambler"
 bl_space_type  = 'PROPERTIES'
 bl_region_type = 'WINDOW'
 bl_context     = 'data'

 @classmethod
 def poll(cls, context):
  return context.active_object and context.active_object.type == 'FONT'

 def draw_header(self, context):
  text = context.active_object.data
  layout = self.layout
  layout.prop(text, 'use_text_scrambler', text="")

 def draw(self, context):
  text   = context.active_object.data
  layout = self.layout
  layout.prop(text,'scrambler_progress', text="Progress")
  layout.prop(text,'source_text', text="Source text")
  layout.prop(text,'characters', text="Characters")


def register():
 bpy.types.TextCurve.scrambler_progress = bpy.props.IntProperty    (name="scrambler_progress",update=update_func, min=0, max=100, options={'ANIMATABLE'})
 bpy.types.TextCurve.use_text_scrambler = bpy.props.BoolProperty   (name="use_text_scrambler", default=False)
 bpy.types.TextCurve.source_text        = bpy.props.StringProperty (name="source_text")
 bpy.types.TextCurve.characters         = bpy.props.StringProperty (name="characters",default="ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz")
 
 bpy.utils.register_module(__name__)
 bpy.app.handlers.frame_change_pre.append(textscrambler_update_frame)


def unregister():
 bpy.app.handlers.frame_change_pre.remove(textscrambler_update_frame)
 bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
 register()
