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
    'name': 'Mouse Gesture',
    'author': 'chromoly',
    'version': (0, 2, 6),
    'blender': (2, 5, 6),
    'api': 34890,
    'location': 'View3D > Mouse',
    'description': '',
    'warning': '',
    'category': '3D View'}

'''
U: Up, D: Down, L: Left, R: Right.

If you need a list of mouse gestures,
drag action mouse (default: left mouse) "DURD" in 3D View.
Appears in the terminal.
'''

'''
マウスジェスチャーの追加・変更はCustomize区間で行います。
blender起動時に実行されるregister()では既存のショートカットに対する変更が行えない為、
ジェスチャー初回呼び出し時に'Set 3D Cursor'に対する変更を行います。

change log
0.2.6:
    バグ潰し、微調整。
0.2.4:
    3DView -> Properiesパネルへ追加。
    細かい修正。
0.2.3:
    ショートカット変更に関する部分を修正。 (action_mouse_checked 参照)
0.2.2:
    細かい修正。
0.2.1:
    Continuous Grab(3DViewからはみ出したカーソルが反対側に現れる機能)を
    呼び出したオペレータで利用出来るように修正。
    副作用として、translate()等を呼び出した直後ではヘッダに数値が表示されなくなる。
0.2.0:
    色々書き直し。
    ドラッグの最中にTABキーを押すことで、マウスジェスチャーの種類を変更。
    ドラッグ下 -> TAB: Transform。
    ドラッグ上 -> TAB: 視点変更。
'''

import math
from types import MethodType

import bpy
from bpy.props import *
from mathutils import Vector
import bgl
import blf


class MGItem:
    def __init__(self, name='',
                 check=lambda self, context, event, action: True,
                 op=lambda self, context: None,
                 **kw):
        '''
        check: 返り値が真となったとき、opを実行します。
               actionはジェスチャーを表す文字列です。 (例: 'UDR')
        op: ジェスチャーで実行する関数です。
            modalの場合は、{'RUNNING_MODAL'}を返すようにします。
        '''
        self.name = name  # type: str
        self.check = check  # type: function
        self.op = op  # type: function
        for k, v in kw.items():
            setattr(self, k, v)

    def _ch_get(self):
        return self._ch
    def _ch_set(self, ch):
        self._ch= MethodType(ch, self)
    check = property(_ch_get, _ch_set)

    def _op_get(self):
        return self._op
    def _op_set(self, op):
        self._op = MethodType(op, self)
    op = property(_op_get, _op_set)


### Customize if you need #####################################################
path_threthold = 5.0  # update interval
path_max_length = 2000

help_str = \
'''### Mouse Gesture ###
Drag Action Mouse.
U: Up, D: Down, L: Left, R: Right.

Help:
  UDLU, DURD: Print list of gestures.

Change Mouse Gesture Type (relative: False):
  D -> (Space or Tab): Transform
  U -> (Space or Tab): View

Transform (relative: True):
  U:        Grab/Move
  UR*, UL*: Rotate
  UD*:      Scale

View (relative: False):
  D:   View Front        (Numpad 1)
  DU:  View Back         (Ctrl Numpad 1)
  R:   View Right        (Numpad 3)
  RL:  View Left         (Ctrl Numpad 3)
  U:   View Top          (Numpad 7)
  UD:  View Bottom       (Ctrl Numpad 7)
  L:   View Camera       (Numpad 0)
  LR:  View Persp/Ortho  (Numpad 5)
  LU:          View All                    (Home)
  DR:          View Global/Local           (Numpad /)
  LD:          View Selected               (Numpad .)
  LDL, RD:     View Selected and keep zoom
  LDR*, ULDR*: Center View to Cursor       (Ctrl Numpad .)
'''


def generate_mgdict():
    '''
    relativeを真とした場合、ジェスチャーの最初の軌跡を基準とします。
    (この場合actionは常に'U'から始まる事になります)
    '''
    mgdict = {}

    ### Transform ###
    transitems = []
    # Translate
    def check(self, context, event, action):
        return len(action) <= 1
    def op(self, context):
        return bpy.ops.transform.translate('INVOKE_REGION_WIN')
    transitems.append(MGItem('Grab/Move', check, op))

    # Rotate
    def check(self, context, event, action):
        if action.startswith(('UR', 'UL')):
            return True
        else:
            return False
    def op(self, context):
        return bpy.ops.transform.rotate('INVOKE_REGION_WIN')
    transitems.append(MGItem('Rotate', check, op))

    # Resize
    def check(self, context, event, action):
        if action.startswith('UD'):
            return True
        else:
            return False
    def op(self, context):
        return bpy.ops.transform.resize('INVOKE_REGION_WIN')
    transitems.append(MGItem('Scale', check, op))

    mgdict['transform'] = {'items': transitems, 'relative': True}

    ### View ###
    viewitems = []
    # View
    for name, vtype, ac in (('View Front', 'FRONT', 'D'),
                            ('View Back', 'BACK', 'DU'),
                            ('View Left', 'LEFT', 'RL'),
                            ('View Right', 'RIGHT', 'R'),
                            ('View Top', 'TOP', 'U'),
                            ('View Bottom', 'BOTTOM', 'UD'),
                            ('View Camera', 'CAMERA', 'L')):
        def check(self, context, event, action):
            return action == self.ac
        def op(self, context):
            rv3d = context.region_data
            if rv3d and not rv3d.lock_rotation:
                bpy.ops.view3d.viewnumpad(type=self.vtype)
        item = MGItem(name, check, op, vtype=vtype, ac=ac)
        viewitems.append(item)

    def check(self, context, event, action):
        return action == 'LR'
    def op(self, context):
        bpy.ops.view3d.view_persportho('INVOKE_REGION_WIN')
    viewitems.append(MGItem('View Persp/Ortho', check, op))

    def check(self, context, event, action):
        return action == 'DR'
    def op(self, context):
        bpy.ops.view3d.localview()
    viewitems.append(MGItem('View Global/Local', check, op))

    def check(self, context, event, action):
        return action == 'LU'
    def op(self, context):
        if hasattr(context.space_data, 'use_local_grid'):
            bpy.ops.view3d.view_all(localgrid=True)
        else:
            bpy.ops.view3d.view_all()  # center=True == Ctrl + C
    viewitems.append(MGItem('View All', check, op))

    def check(self, context, event, action):
        return action == 'LD'
    def op(self, context):
        bpy.ops.view3d.view_selected()
    viewitems.append(MGItem('View Selected', check, op))

    def check(self, context, event, action):
        return action.startswith(('LDR', 'ULDR'))
    def op(self, context):
        bpy.ops.view3d.view_center_cursor()
    viewitems.append(MGItem('Center View to Cursor', check, op))

    def check(self, context, event, action):
        return action in ('LDL', 'RD')
    def op(self, context):
        scn = context.scene
        cursor_bak = scn.cursor_location[:]
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.view3d.view_center_cursor()
        scn.cursor_location = cursor_bak
    viewitems.append(MGItem('View Selected (Keep zoom)', check, op))

    mgdict['view'] = {'items': viewitems, 'relative': False}

    '''### Generic ###
    genitems = []
    # Space Menu (call menu test)
    def check(self, context, event, action):
        return action == 'D'
    def op(self, context):
        bpy.ops.wm.call_menu('INVOKE_REGION_WIN',
                             name='VIEW3D_MT_Space_Dynamic_Menu')
    genitems.append(MGItem('Space Dynamic Menu', check, op))
    mgdict['generic'] = {'items': genitems, 'relative': False}
    '''

    ### Common ###
    commonitems = []
    # help
    def check(self, context, event, action):
        return action in ('UDLU', 'DURD')
    def op(self, context):
        print(help_str)
    commonitems.append(MGItem('Help', check, op))

    # Mesh Select Overlap
    def check(self, context, event, action):
        if action == 'UDU':
            if hasattr(context.tool_settings, 'use_select_overlap'):
                return True
        return False
    def op(self, context):
        ts = context.tool_settings
        ts.use_select_overlap = not ts.use_select_overlap
    commonitems.append(MGItem('Toggle Mesh Select Overlap', check, op))

    mgdict['common'] = {'items': commonitems}

    ############################
    ### Change Mouse Gesture ###
    ############################
    chitems = []
    def check(self, context, event, action):
        return action == 'D'
    def op(self, context):
        mg = context.scene.mouse_gesture
        mg.type = self.mgtype
        mg.relative = mgdict[self.mgtype]['relative']
    chitems.append(MGItem('Transform', check, op, mgtype='transform'))

    def check(self, context, event, action):
        return action == 'U'
    def op(self, context):
        mg = context.scene.mouse_gesture
        mg.type = self.mgtype
        mg.relative = mgdict[self.mgtype]['relative']
    chitems.append(MGItem('View', check, op, mgtype='view'))

    '''def check(self, context, event, action):
        return action == 'R'
    def op(self, context):
        mg = context.scene.mouse_gesture
        mg.type = self.mgtype
        mg.relative = mgdict[self.mgtype]['relative']
    chitems.append(MGItem('Generic', check, op, mgtype='generic'))
    '''

    mgdict['change_mgtype'] = {'items': chitems, 'relative': False}

    return mgdict


mgitems = (('transform', 'Transform', ''),
           ('view', 'View', ''))
default_mgtype = 'transform'  # type: str
### End #######################################################################

mgdict = generate_mgdict()  # type: dict
action_mouse_checked = False


class MouseGesture(bpy.types.PropertyGroup):
    EP = EnumProperty
    txt = 'Gesture "UDLU" or "DURD", ' + \
          'list of mouse gestures appear in the terminal.'
    type = EnumProperty(items=mgitems,
                        name='Mouse Gesture Type',
                        description=txt,
                        default=default_mgtype)
    txt = 'Allow moving the mouse outside the view on some manipulator' + \
          '(transform, ui control drag)'
    do_continuous_grab = BoolProperty(name='Continuous Grab',
                                      description=txt,
                                      default=False)
    relative = BoolProperty(name='Relative',
                            default=False,
                            options={'HIDDEN'})


class VIEW3D_PT_mouse_gesture(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'  # 'TOOLS'
    bl_label = 'Mouse Gesture'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.area is not None

    def draw(self, context):
        mg = context.scene.mouse_gesture
        layout = self.layout
        col = layout.column()
        col.prop(mg, 'type', text='Type')
        if mg.type == 'transform':
            col.prop(mg, 'do_continuous_grab')


class VIEW3D_OT_mouse_gesture(bpy.types.Operator):
    '''Mouse Gesture.'''
    bl_description = 'Mouse gesture.'
    bl_idname = 'view3d.mouse_gesture'
    bl_label = 'Mouse Gesture'
    bl_options = {'REGISTER'}
    # {'REGISTER', 'UNDO', 'BLOCKING', 'MACRO', 'GRAB_POINTER'}

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def draw_callback_px(self, context):
        if context.region.id != self.region_id:
            return
        posx = 70
        posy1 = 30
        posy2 = 50
        text_interval = 5
        font_id = 0
        blf.size(font_id, 11, context.user_preferences.system.dpi)
        bgl.glEnable(bgl.GL_BLEND)
        if self.changing_mgtype:
            bgl.glColor4f(1.0, 1.0, 0.0, 1.0)
        else:
            bgl.glColor4f(1.0, 1.0, 1.0, 1.0)

        # draw origin
        bgl.glLineWidth(2)
        radius = path_threthold
        radius2 = radius + 5
        x, y, z = self.path[0]
        bgl.glBegin(bgl.GL_LINES)
        for i in range(4):
            r = math.pi / 2 * i + math.pi / 4
            bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
            bgl.glVertex2f(x + radius2 * math.cos(r),
                           y + radius2 * math.sin(r))
        bgl.glEnd()
        bgl.glLineWidth(1)

        # draw lines
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
        bgl.glLineStipple(1, int(0b101010101010101))  # (factor, pattern)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for v in self.path:
            bgl.glVertex2f(v[0], v[1])
        bgl.glEnd()
        bgl.glLineStipple(1, 1)
        bgl.glDisable(bgl.GL_LINE_STIPPLE)

        # draw txt
        if self.action or self.mgitem:
            x = posx
            for txt in self.action:
                blf.position(font_id, x, posy1, 0)
                blf.draw(font_id, txt)
                text_width, text_height = blf.dimensions(font_id, txt)
                x += text_width + text_interval
            if self.mgitem:
                blf.position(font_id, posx, posy2, 0)
                blf.draw(font_id, self.mgitem.name)
        else:
            #blf.position(font_id, posx, posy2, 0)
            #blf.draw(font_id, '[Mouse Gesture]')
            pass

        # restore opengl defaults
        bgl.glLineWidth(1)
        bgl.glDisable(bgl.GL_BLEND)
        bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
        blf.size(0, 11, context.user_preferences.system.dpi)

    def append_action(self, rvec, vecs):
        angles = [rvec.angle(vec) for vec in vecs]
        a = ('U', 'D', 'R', 'L')[angles.index(min(angles))]
        if not self.action or (self.action and a != self.action[-1]):
            self.action.append(a)

    def get_mgitem(self, context, event, name):
        for mgitem in mgdict[name]['items']:
            if mgitem.check(context, event, ''.join(self.action)):
                break
        else:
            mgitem = None
        return mgitem

    def modal(self, context, event):
        mg = context.scene.mouse_gesture

        if self.op_running_modal:
            # for 'Continuous Grab'
            return {'FINISHED'}

        if context.user_preferences.inputs.select_mouse == 'RIGHT':
            action_mouse = 'LEFTMOUSE'
            select_mouse = 'RIGHTMOUSE'
        else:
            action_mouse = 'RIGHTMOUSE'
            select_mouse = 'LEFTMOUSE'

        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
        mouseco_rel = mouseco - self.path[-1]
        path_length = 0.0
        for i in range(len(self.path) - 1):
            path_length += (self.path[i] - self.path[i + 1]).length

        if event.type == 'MOUSEMOVE' and mouseco_rel.length > path_threthold:
            self.path.append(mouseco)
            if mg.relative:
                if len(self.path) == 1:
                    vec = mouseco - self.path[0]
                    vec.normalize()
                else:
                    vec = self.path[1] - self.path[0]
                    vec.normalize()
                vals = (vec, -vec, (vec[1], -vec[0], 0), (-vec[1], vec[0], 0))
            else:
                vals = ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
            vecs = [Vector(v) for v in vals]  # [U, D, R, L]
            self.append_action(mouseco_rel, vecs)

            if mg.type not in mgdict and not self.changing_mgtype:
                mgitem = None
            else:
                if self.changing_mgtype:
                    mgitem = self.get_mgitem(context, event, 'change_mgtype')
                else:
                    mgitem = self.get_mgitem(context, event, 'common')
                    if mgitem is None:
                        mgitem = self.get_mgitem(context, event, mg.type)
            self.mgitem = mgitem
            context.area.tag_redraw()

        elif (event.type in ('ESC', ) or
              (event.type in (select_mouse, 'MIDDLEMOUSE') and
               event.value == 'PRESS')):
            # cancel
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            return {'CANCELLED'}

        elif ((event.type == action_mouse and event.value == 'RELEASE') or
              event.type in ('RET', 'NUMPAD_ENTER') or
              path_length > path_max_length):
            # execute
            context.region.callback_remove(self._handle)
            context.area.tag_redraw()
            if self.mgitem:
                retval = self.mgitem.op(context)
                if retval == {'RUNNING_MODAL'} and mg.do_continuous_grab:
                    self.op_running_modal = 1
                    return {'RUNNING_MODAL'}
            return {'FINISHED'}

        elif event.type in ('SPACE', 'TAB') and event.value == 'PRESS':
            # change mg.type
            mg.relative = mgdict['change_mgtype']['relative']
            self.changing_mgtype = True
            # update action
            self.action = []
            vals = ((0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0))
            vecs = [Vector(v) for v in vals]
            for i in range(len(self.path) - 1):
                rvec = self.path[i + 1] - self.path[i]
                self.append_action(rvec, vecs)

            self.mgitem = self.get_mgitem(context, event, 'change_mgtype')
            context.area.tag_redraw()

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        global action_mouse_checked
        if not action_mouse_checked:
            km = context.window_manager.keyconfigs.active.keymaps['3D View']
            for kmi in km.items:
                if kmi.idname == 'view3d.cursor3d':
                    if kmi.type == 'ACTIONMOUSE':
                        kmi.value = 'CLICK'
            action_mouse_checked = True

        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)
        self._handle = context.region.callback_add(
                                      self.__class__.draw_callback_px,
                                      (self, context), 'POST_PIXEL')
        self.region_id = context.region.id
        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0.0))
        self.path = [mouseco]
        self.action = []
        self.changing_mgtype = False
        for mgitem in mgdict['change_mgtype']['items']:
            if mgitem.mgtype == context.scene.mouse_gesture.type:
                mgitem.op(context)
                break
        mgitem = self.get_mgitem(context, event, 'common')
        if mgitem is None:
            mgitem = self.get_mgitem(context, event,
                                     context.scene.mouse_gesture.type)
        self.mgitem = mgitem

        self.op_running_modal = 0
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}


# Register
def register():
    bpy.utils.register_module(__name__)
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    kmi = km.items.new('view3d.mouse_gesture', 'EVT_TWEAK_A', 'ANY')
    for kmi in km.items:
        if kmi.idname == 'view3d.cursor3d':
            if kmi.type == 'ACTIONMOUSE':
                kmi.value = 'CLICK'

    bpy.types.Scene.mouse_gesture = \
        PointerProperty(name='Mouse Gesture', type=MouseGesture)


def unregister():
    bpy.utils.unregister_module(__name__)
    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    for kmi in km.items:
        if kmi.idname == 'view3d.mouse_gesture':
            km.items.remove(kmi)
        elif kmi.idname == 'view3d.cursor3d':
            if kmi.type == 'ACTIONMOUSE':
                kmi.value = 'PRESS'

    if bpy.context.scene.get('mouse_gesture') != None:
        del bpy.context.scene['mouse_gesture']
    del bpy.types.Scene.mouse_gesture


if __name__ == '__main__':
    register()
