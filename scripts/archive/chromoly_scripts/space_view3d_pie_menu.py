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

bl_info = {
    'name': 'Pie Menu',
    'author': 'chromoly',
    'version': (0, 4, 3),
    'blender': (2, 5, 6),
    'api': 34890,
    'location': 'View3D > Mouse',
    'category': '3D View'}


'''
PieMenuを呼び出すショートカットが既存のショートカットと重複した場合、上書きします。たぶん

available:
    3D View:
        shift + S: Snap
        ctrl + shift + Tab: Snap Element
        ctrl + Space: Manipulator
        alt + Space: Orientation
    Mesh Edit:
        ctrl + Tab: select mode
        X: delete

shortcut when running pie menu:
    wheel up: prev menu
    wheel down: next menu  (e.g. 3DView shift + Tab, or editmode X)
    shift + middle mouse: move menu
    left mouse: call function.
    rigth mouse: [next, prev, parent, exit] menu. hold and release.
    middle mouse: cancel
    right mouse + left mouse: cancel
    left mouse + rigth mouse: cancel
    ctrl: cancel
    shift: toggle menu item (e.g. editmode ctrl + Tab, or editmode X)

If you want more pie menu, edit generate_menus()
'''

'''
Change log:
0.4.2:
    add Menu.op(self, context). this method for initialize menu.

    MenuItem.op(context, event) -> MenuItem.op(self, context)
    (function -> method)

    add Manipulator and Orientation menus.
    3D View:
        ctrl + Space: Manipulator
        alt + Space: Orientation

    If your blender's python api can access Region.xmin and Region.ymin,
    draw pie menu over region border.
0.4.3:
    Change mouse shortcuts.
'''


import string
import re
import math
from types import MethodType

import bpy
from bpy.props import *
import mathutils as Math
from mathutils import Euler, Matrix, Vector, Quaternion
import bgl
import blf


from va.gl import draw_circle, draw_triangle, draw_trapezoid, draw_quad_fan, \
                  draw_arrow, draw_sun, draw_rounded_box, draw_arc
from va.mesh import PyMesh
from va.view import Shortcut


'''
### Copy from va ##############################################################
def draw_circle(x, y, radius, subdivide, poly=False):
    r = 0.0
    dr = math.pi * 2 / subdivide
    if poly:
        subdivide += 1
        bgl.glBegin(bgl.GL_TRIANGLE_FAN)
        bgl.glVertex2f(x, y)
    else:
        bgl.glBegin(bgl.GL_LINE_LOOP)
    for i in range(subdivide):
        bgl.glVertex2f(x + radius * math.cos(r), y + radius * math.sin(r))
        r += dr
    bgl.glEnd()


def draw_triangle_get_vectors(base, base_length, top_relative):
    # triangle_relative_to_vertsの書き直し
    # base左, base右, top
    v0 = Vector(base)
    v = (Vector([-top_relative[1], top_relative[0]])).normalized()
    v *= base_length / 2
    v1 = v0 + v
    v2 = v0 - v
    v3 = v0 + Vector(top_relative)
    return v1, v2, v3


def draw_triangle(base, base_length, top_relative, poly=False):
    # draw_triangle_relativeの書き直し
    # base左, base右, top
    v1, v2, v3 = draw_triangle_get_vectors(base, base_length, top_relative)
    bgl.glBegin(bgl.GL_TRIANGLES if poly else bgl.GL_LINE_LOOP)
    bgl.glVertex2f(*v1)
    bgl.glVertex2f(*v2)
    bgl.glVertex2f(*v3)
    bgl.glEnd()


def draw_trapezoid_get_vectors(base, top_relative, base_length, top_length):
    # base左, base右, top右, top左
    v0 = Vector(base)
    v = (Vector([-top_relative[1], top_relative[0]])).normalized()
    vb = v * base_length / 2
    v1 = v0 + vb
    v2 = v0 - vb
    vt = v * top_length / 2
    v3 = v0 + Vector(top_relative) - vt
    v4 = v0 + Vector(top_relative) + vt
    return v1, v2, v3, v4


def draw_trapezoid(base, top_relative, base_length, top_length, poly=False):
    # base左, base右, top右, top左
    v1, v2, v3, v4 = draw_trapezoid_get_vectors(base, top_relative,
                                                base_length, top_length)
    bgl.glBegin(bgl.GL_QUADS if poly else bgl.GL_LINE_LOOP)
    bgl.glVertex2f(*v1)
    bgl.glVertex2f(*v2)
    bgl.glVertex2f(*v3)
    bgl.glVertex2f(*v4)
    bgl.glEnd()


def normalize_angle(angle):
    while angle < 0.0:
        angle += math.pi * 2
    while angle > math.pi * 2:
        angle -= math.pi * 2
    return angle


def draw_quad_fan(x, y, inner_radius, outer_radius,
                  start_angle, end_angle, edgenum=16):
    # 三時から反時計回りに描画
    start = normalize_angle(start_angle)
    end = normalize_angle(end_angle)
    if end < start:
        end += math.pi * 2
    d = (end - start) / edgenum
    a = start
    bgl.glBegin(bgl.GL_QUAD_STRIP)
    for i in range(edgenum + 1):
        bgl.glVertex2f(x + inner_radius * math.cos(a),
                       y + inner_radius * math.sin(a))
        bgl.glVertex2f(x + outer_radius * math.cos(a),
                       y + outer_radius * math.sin(a))
        a += d
    bgl.glEnd()


def draw_arc_get_vectors(x, y, radius, start_angle, end_angle, edgenum=16):
    # 三時から反時計回りに描画 angle:radians
    start = normalize_angle(start_angle)
    end = normalize_angle(end_angle)
    if end < start:
        end += math.pi * 2
    d = (end - start) / edgenum
    a = start
    l = []
    for i in range(edgenum + 1):
        l.append(Vector([x + radius * math.cos(a), y + radius * math.sin(a)]))
        a += d
    return l


def draw_arc(x, y, radius, start_angle, end_angle, edgenum=16):
    # 三時から反時計回りに描画 angle:radians
    l = draw_arc_get_vectors(x, y, radius, start_angle, end_angle, edgenum)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for v in l:
        bgl.glVertex2f(*v)
    bgl.glEnd()


def draw_rounded_box(xmin, ymin, xmax, ymax, round_radius, poly=False):
    r = min(round_radius, (xmax - xmin) / 2, (ymax - ymin) / 2)
    bgl.glBegin(bgl.GL_POLYGON if poly else bgl.GL_LINE_LOOP)
    if round_radius > 0.0:
        pi = math.pi
        l = []
        # 左下
        l += draw_arc_get_vectors(xmin + r, ymin + r, r, pi, pi * 3 / 2, 4)
        # 右下
        l += draw_arc_get_vectors(xmax - r, ymin + r, r, pi * 3 / 2, 0.0, 4)
        # 右上
        l += draw_arc_get_vectors(xmax - r, ymax - r, r, 0.0, pi / 2, 4)
        # 左上
        l += draw_arc_get_vectors(xmin + r, ymax - r, r, pi / 2, pi, 4)
        for v in l:
            bgl.glVertex2f(*v)
    else:
        bgl.glVertex2f(xmin, ymin)
        bgl.glVertex2f(xmax, ymin)
        bgl.glVertex2f(xmax, ymax)
        bgl.glVertex2f(xmin, ymax)
    bgl.glEnd()


def key_edge_dict(me, select=None, hide=None):
    check = lambda item: (select is None or item.select is select) and \
                         (hide is None or item.hide is hide)
    key_edge = {e.key: e.index for e in me.edges if check(e)}
    return key_edge


class Vert():
    def __init__(self, vertex=None):
        if vertex:
            self.index = vertex.index
            self.select = vertex.select
            self.hide = vertex.hide
            self.normal = vertex.normal.copy()
            self.co = vertex.co.copy()
        else:
            self.index = 0
            self.select = False
            self.hide = False
            self.normal = Vector()
            self.co = Vector()
        self.vertices = []
        self.edges = []
        self.faces = []
        self.f1 = 0
        self.f2 = 0
        self.wldco = None  # type:Vector. self.co * ob.matrix_world
        self.winco = None  # type:Vector. convert_world_to_window()
        self.viewco = None  # type:Vector self.wldco * viewmat

    def _get_selected(self):
        return self.select and not self.hide

    def _set_selected(self, val):
        if not self.hide:
            self.select = val

    is_selected = property(_get_selected, _set_selected)

    def copy(self, set_original=False):
        vert = Vert(self)
        if set_original:
            vert.original = self
        return vert


class Edge():
    def __init__(self, edge=None, vertices=None):
        if edge:
            self.index = edge.index
            self.select = edge.select
            self.hide = edge.hide
            self.is_loose = edge.is_loose
            self.use_edge_sharp = edge.use_edge_sharp
            self.use_seam = edge.use_seam
            self.key = edge.key
            if vertices:
                #self.vertices = [vertices[i] for i in edge.vertices]
                self.vertices = [vertices[edge.vertices[0]],
                                 vertices[edge.vertices[1]]]
        else:
            self.index = 0
            self.select = False
            self.hide = False
            self.is_loose = False
            self.use_edge_sharp = False
            self.use_seam = False
            self.key = ()  # (int, int)
            self.vertices = []
        self.faces = []
        self.f1 = 0
        self.f2 = 0

    def _get_selected(self):
        return self.select and not self.hide

    def _set_selected(self, val):
        if not self.hide:
            self.select = val

    is_selected = property(_get_selected, _set_selected)

    def copy(self, set_original=False):
        edge = Edge(self)
        edge.vertices = list(self.vertices)
        if set_original:
            edge.original = self
        return edge

    def vert_another(self, v):
        if v in self.vertices:
            return self.vertices[self.vertices.index(v) - 1]
        else:
            return None


class Face():
    def __init__(self, face=None, vertices=None, key_edge=None):
        if face:
            self.index = face.index
            self.select = face.select
            self.hide = face.hide
            self.material_index = face.material_index
            self.area = face.area
            self.normal = face.normal.copy()
            self.center = face.center.copy()
            self.edge_keys = tuple(face.edge_keys)
            if vertices:
                self.vertices = [vertices[i] for i in face.vertices]
            if key_edge:
                self.edges = [key_edge[key] for key in face.edge_keys]
        else:
            self.index = 0
            self.select = False
            self.hide = False
            self.material_index = 0
            self.area = 0.0
            self.normal = Vector()
            self.center = Vector()
            self.edge_keys = []
            self.vertices = []
            self.edges = []
        self.f1 = 0
        self.f2 = 0

    def _get_selected(self):
        return self.select and not self.hide

    def _set_selected(self, val):
        if not self.hide:
            self.select = val

    is_selected = property(_get_selected, _set_selected)

    def copy(self, set_original=False):
        face = Face(self)
        face.vertices = list(self.vertices)
        face.edges = list(self.edges)
        if set_original:
            face.original = self
        return face


class PyMesh():
    def __init__(self, me, select=(None, None, None), hide=(None, None, None)):
        key_edge = key_edge_dict(me, select=None, hide=None)

        def select_hide_check(item, select, hide):
            if (select is None or item.select == select) and \
               (hide is None or item.hide == hide):
                return True
            return False
        vertices = [Vert(v) for v in me.vertices]
        #vertices = [Vert(v) for v in me.vertices if select_hide_check(v)]()
        edges = [Edge(e, vertices) for e in me.edges]
        key_edge = {k: edges[ei] for k, ei in key_edge.items()}
        faces = [Face(f, vertices, key_edge) for f in me.faces]

        for f in faces:
            for v in f.vertices:
                v.faces.append(f)
            for key in f.edge_keys:
                key_edge[key].faces.append(f)
        for e in edges:
            for v in e.vertices:
                v.edges.append(e)
        for v in vertices:
            for e in v.edges:
                v.vertices.append(e.vert_another(v))

        self.vertices = vertices
        self.edges = edges
        self.faces = faces
        self.key_edge = key_edge

    def calc_world_coordinate(self, matrix_world):
        for vert in self.vertices:
            vert.wldco = vert.co * matrix_world

    def calc_window_coordinate(self, persmat, sx, sy):
        for vert in self.vertices:
            if vert.wldco:
                vert.winco = convert_world_to_window(vert.wldco, \
                                                     persmat, sx, sy)

    def calc_view_coordinate(self, view_matrix):
        for vert in self.vertices:
            if vert.wldco:
                vert.viewco = vert.wldco * view_matrix

    def calc_same_coordinate(self):
        for vert in self.vertices:
            vert.on_vertices = [v for v in vert.vertices if v.co == vert.co]

    def removed_same_coordinate(verts):
        d = OrderedDict(zip((tuple(v.co) for v in verts), range(len(verts))))
        return [verts[i] for i in d.values()]

    def find_edge(self, v1, v2):
        return self.key_edge.get(tuple(sorted(v1.index, v2.index)), None)


class Shortcut:
    def __init__(self, name='', type='', press=True,
                 shift=False, ctrl=False, alt=False, oskey=False, **kw):
        self.name = name
        self.type = type
        self.press = press
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt
        self.oskey = oskey
        for k, v in kw.items():
            setattr(self, k, v)

    def check(self, event):
        if (self.type is None or event.type == self.type):
            if ((event.value == 'PRESS' and self.press is True) or \
                (event.value == 'RELEASE' and self.press is False) or \
                (event.value == 'NOTHING' and self.press is None)):
                if (self.shift is None or event.shift == self.shift) and \
                    (self.ctrl is None or event.ctrl == self.ctrl) and \
                    (self.alt is None or event.alt == self.alt) and \
                    (self.oskey is None or event.oskey == self.oskey):
                    return True
        return False

    def label(self):
        l = []
        if self.shift:
            l.append('Shift + ')
        if self.ctrl:
            l.append('Ctrl + ')
        if self.alt:
            l.append('Alt + ')
        if self.oskey:
            l.append('Oskey + ')
        l.append(self.type)
        return ''.join(l)
### Copy end ##################################################################
'''


class Settings:
    def __init__(self):
        self.tricky = False
        self.redraw_all = False  # draw all area. Slower.
        # メニュー中央の無反応領域
        self.center_radius = 8
        # 文字列の端からテキストボックス縁までの距離
        self.text_ofs = 5
        # 文字描画時の上下へのオフセット。何故か下へずれる為。
        self.text_ofsy = 2
        # テキストボックスの角の丸み
        self.round_radius = 5
        # fontsize
        self.fontsize = (0, 12, bpy.context.user_preferences.system.dpi)
        # drag_cancel_length  中央に赤ランプが点灯
        self.valid_drag = 40
        # handsize: menu.radiusからはみ出る長さ, 根本幅, 先端幅
        self.handsize = [0, 6, 4]

class Colors:
    def __init__(self):
        #theme_ui = context.user_preferences.themes['Default'].user_interface
        #theme_menu_back = theme_ui.wcol_menu_back
        #theme_menu_item = theme_ui.wcol_menu_item

        #self.outline = theme_menu_back.outline[:] + [1.0]
        #self.inner_back = theme_menu_back.inner
        #self.inner = theme_menu_item.inner
        #self.inner_sel = theme_menu_item.inner_sel
        self.outline = [0.0, 0.0, 0.0, 1.0]  # rounded box
        self.inner_back = [0.13, 0.13, 0.13, 0.9]  # rounded box
        self.inner = [0.0, 0.0, 0.0, 0.0]  # rounded box
        self.inner_right_menu = [0.2, 0.4, 0.0, 0.8]  # rounded box
        self.inner_sel = [1.0, 1.0, 1.0, 1.0]  # rounded box
        #self.text = theme_menu_item.text[:] + [1.0]
        #self.text_sel = theme_menu_item.text_sel[:] + [1.0]
        self.text = [1.0, 1.0, 1.0, 1.0]  # item text
        self.text_sel = [0.0, 0.0, 0.5, 1.0]
        self.line = [0.8, 0.8, 0.8, 1.0]  # center to rounded box
        self.line_active = [1.0, 1.0, 1.0, 1.0]
        self.marker = [1.0, 1.0, 1.0, 1.0]  # triangle marker
        self.marker_outline = [0.0, 0.0, 0.0, 1.0]
        self.title = [1.0, 1.0, 1.0, 1.0]
        self.active_back = [0.8, 0.8, 1.0, 0.5]  # active item
        self.hand = [0.3, 0.3, 1.0, 1.0]
        self.handoutline = [1.0, 1.0, 1.0, 1.0]
        self.press = [1.0, 1.0, 1.0, 0.7]  # center lamp
        self.next = [0.0, 1.0, 0.0, 0.7]  # center lamp (press center)
        self.cancel = [1.0, 0.3, 0.0, 1.0]  # center lamp

settings = Settings()
settings.colors = Colors()


class Menu:
    def __init__(self, name='', shortcut=None, op=lambda self, context: None):
        self.shortcut = shortcut  # keymap
        self.name = name
        self.op = op  # type: method. to initialize Menu
        self.op_called = False
        self.items = []  # type: MenuItem or None(as spacer)
        self.next = None  # type: Menu
        self.prev = None  # type: Menu
        self.parent = None  # type: MenuItem
        self.active = -1  # type: int (active item index (-1=disable))
        self.radius = 50
        self.align = True  # Don't change! MenuItem端を中央の円に揃えて表示。
        self.ellispe = True  # アイテムが重なる場合の、radiusの拡大方法。未完

    def _op_get(self):
        return self._op

    def _op_set(self, op):
        #self._op = MethodType(op, self)
        def _op(self, context):
            if not self.op_called:
                op(self, context)
                self.op_called = True
        self._op = MethodType(_op, self)

    op = property(_op_get, _op_set)

    def check_shortcut(self, event, shift=False):
        for item in (item for item in self.items if item):
            if shift:
                shiftitem = item.shiftitem
                if shiftitem.shortcut:
                    if shiftitem.shortcut.check(event):
                        return shiftitem
            else:
                if item.shortcut:
                    if item.shortcut.check(event):
                        return item
        return None


class MenuItem:
    def __init__(self, menu=None, name='', description='',
                 op=lambda self, context: None,
                 poll=lambda self, context: True,
                 shortcut=None, child=None, color=None, **kw):
        self.name = name
        self.description = description  # 未実装。タイマー的な物が使えないと無理。
        self.op = op  # type: method
        self.shortcut = shortcut  # op()
        self.child = child  # type: Menu
        self.color = color  # Outline Color
        self.shiftitem = self  # type: MenuItem SHIFTキーを押した時
        self.poll = poll  # executable self.op ?
        if menu:  # menuは受け取っておく事。
            menu.items.append(self)
            self.menu = menu
        for k, v in kw.items():
            setattr(self, k, v)

    def _op_get(self):
        return self._op

    def _op_set(self, op):
        self._op = MethodType(op, self)

    op = property(_op_get, _op_set)

    def _poll_get(self):
        return self._poll

    def _poll_set(self, poll):
        self._poll = MethodType(poll, self)

    poll = property(_poll_get, _poll_set)

def draw_menu(self, context):
    if context.region.id != self.region_id:
        if not hasattr(context.region, 'xmin') or \
           not hasattr(context.region, 'ymin'):
            return
    menu = self.menu
    shift = self.shift
    center_radius = settings.center_radius
    round_radius = settings.round_radius
    text_ofs = settings.text_ofs
    text_ofsy = settings.text_ofsy
    colors = settings.colors

    if hasattr(context.region, 'xmin') and hasattr(context.region, 'ymin'):
        region = context.region
        v = Vector([region.xmin, region.ymin, 0])
        mouseco_menu = self.mouseco_menu_abs - v
        mouseco = self.mouseco_abs - v
    else:
        mouseco_menu = self.mouseco_menu
        mouseco = self.mouseco
    xo, yo, zo = mouseco_menu
    relative = mouseco - mouseco_menu
    itemangle = math.pi * 2 / len(menu.items)
    menuradius = menu.radius

    ## Get all charactor text_height
    blf.size(*settings.fontsize)
    _text_width, text_height = blf.dimensions(0, string.printable)

    ## Check menu radius
    box_height = (text_height + text_ofs * 2)
    if len(menu.items) <= 1:
        menuradius_top = menuradius
    elif menu.ellispe:
        if (menuradius * math.sin(itemangle / 2)) * 2 < (box_height + 4):
            menuradius = (box_height + 4) / math.sin(itemangle)
        if menuradius - menuradius * math.cos(itemangle) < \
                                                          (box_height + 4) / 2:
            menuradius_top = (math.ceil(len(menu.items) / 4) - 0.5) * \
                                (box_height + 4) * 1.15
        else:
            menuradius_top = menuradius
    else:
        if menuradius - menuradius * math.cos(itemangle) < \
                                                          (box_height + 4) / 2:
            menuradius = (box_height + 4) / 2 / (1 - math.cos(itemangle))

    ## Title
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(*colors.title)
    # Active Menu Name
    text_width, _text_height = blf.dimensions(0, menu.name)
    xmin = xo - text_width / 2 - text_ofs
    xmax = xo + text_width / 2 + text_ofs
    ymin = yo + menuradius + 40
    ymax = ymin + text_height + text_ofs * 2
    draw_rounded_box(xmin, ymin, xmax, ymax, round_radius)
    blf.position(0, xmin + text_ofs, ymin + text_ofs + text_ofsy, 0)
    blf.draw(0, menu.name)
    # Next Menus
    next = menu.next
    pos = xmax + 20
    for i in range(3):
        if not next:
            break
        text_w, text_h = blf.dimensions(0, next.name)
        pos += text_ofs
        blf.position(0, pos, ymin + text_ofs + text_ofsy, 0)
        blf.draw(0, next.name)
        pos += text_w + text_ofs
        next = next.next
    # Prev Menus
    prev = menu.prev
    pos = xmin - 20
    for i in range(3):
        if not prev:
            break
        text_w, text_h = blf.dimensions(0, prev.name)
        pos -= text_w + text_ofs * 2
        blf.position(0, pos, ymin + text_ofs + text_ofsy, 0)
        blf.draw(0, prev.name)
        prev = prev.prev
    # Parent Menus
    for i, text in enumerate(self.history):
        ymin = ymax + 2
        bgl.glEnable(bgl.GL_BLEND)  # text描画後にOFFになる為
        text_width, _text_height = blf.dimensions(0, text)
        xmin = xo - text_width / 2 - text_ofs
        xmax = xo + text_width / 2 + text_ofs
        ymax = ymin + text_height + text_ofs * 2
        #draw_rounded_box(xmin, ymin, xmax, ymax, round_radius)
        blf.position(0, xmin + text_ofs, ymin + text_ofs + text_ofsy, 0)
        blf.draw(0, text)
    bgl.glEnable(bgl.GL_BLEND)  # text描画後にOFFになる為

    ## Active Background
    if menu.active != -1:
        angle = math.pi * 3 / 2 - itemangle * menu.active
        col = colors.active_back[:]
        bgl.glColor4f(*col)
        draw_quad_fan(xo, yo, center_radius, menuradius,
                      angle - itemangle / 2, angle + itemangle / 2, 16)
        for j in range(15):  # gradation
            col[3] = colors.active_back[3] * (15 - j) / 15
            bgl.glColor4f(*col)
            draw_quad_fan(xo, yo, menuradius + j * 5,
                          menuradius + (j + 1) * 5,
                          angle - itemangle / 2, angle + itemangle / 2, 16)

    ## Center Lamp
    if self.mouseco_left or self.mouseco_middle or self.mouseco_right:
        if self.mouseco_left:
            v = self.mouseco_left
        elif self.mouseco_middle:
            v = self.mouseco_middle
        else:
            v = self.mouseco_right
        if (mouseco - v).length <= settings.valid_drag:
            bgl.glColor4f(*colors.press)
        else:
            bgl.glColor4f(*colors.cancel)
        draw_circle(xo, yo, center_radius, 16, poly=True)

    ## Items
    angle = math.pi * 3 / 2
    for i, item in enumerate(menu.items):
        if item and shift:
            item = item.shiftitem
        if item is None:
            angle -= itemangle
            continue


        if len(menu.items) % 2 == 0 and i == int(len(menu.items) / 2):
            position = 'top'
        elif i == 0:
            position = 'bottom'
        elif i < len(menu.items) / 2:
            position = 'left'
        else:
            position = 'right'
        if len(menu.items) % 4 == 0 and (i == len(menu.items) / 4 or
                                         i == len(menu.items) / 4 * 3):
            horizon = True
        else:
            horizon = False

        text = item.name
        text_width, _text_height = blf.dimensions(0, text)
        if menu.ellispe:
            x = y = 0
            if position == 'top':
                y = menuradius_top
            elif position == 'bottom':
                y = -menuradius_top
            elif position == 'left' and horizon:
                x = -menuradius
            elif position == 'right' and horizon:
                x = menuradius
            else:
                a = math.sin(angle) / math.cos(angle)
                x = math.sqrt((menuradius ** 2 * menuradius_top ** 2) /
                              (menuradius_top ** 2 + menuradius ** 2 * a ** 2))
                if i < len(menu.items) / 2:
                    x = -x
                y = a * x
        else:
            x = menuradius * math.cos(angle)
            y = menuradius * math.sin(angle)

        xmin = xo + x - text_width / 2 - text_ofs
        ymin = yo + y - text_height / 2 - text_ofs
        if menu.align:
            dx = text_width / 2 + text_ofs
            dy = text_height / 2 + text_ofs
            if position == 'top':
                ymin += dy
            elif position == 'bottom':
                ymin -= dy
            elif position == 'left':
                xmin -= dx
            else:
                xmin += dx
        xmax = xmin + text_width + text_ofs * 2
        ymax = ymin + text_height + text_ofs * 2

        bgl.glEnable(bgl.GL_BLEND)  # text描画後にOFFになる為

        ## Center to RoundedBox Line
        if menu.active == i:
            bgl.glColor4f(*colors.line_active)
            #bgl.glLineWidth(3)
        else:
            bgl.glColor4f(*colors.line)
            #bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(xo + center_radius * math.cos(angle),
                       yo + center_radius * math.sin(angle))
        if position == 'top':
            bgl.glVertex2f((xmin + xmax) / 2, ymin)
        elif position == 'bottom':
            bgl.glVertex2f((xmin + xmax) / 2, ymax)
        elif position == 'left':
            bgl.glVertex2f(xmax, (ymin + ymax) / 2)
        else:
            bgl.glVertex2f(xmin, (ymin + ymax) / 2)
        bgl.glEnd()
        #bgl.glLineWidth(1)

        ## Line-Box Connection
        if position == 'top':
            draw_quad_fan((xmin + xmax) / 2, ymin, 0, 3,
                          math.pi, math.pi * 2, edgenum=8)
        elif position == 'bottom':
            draw_quad_fan((xmin + xmax) / 2, ymax, 0, 3,
                          0, math.pi, edgenum=8)
        elif position == 'left':
            draw_quad_fan(xmax, (ymin + ymax) / 2, 0, 3,
                          math.pi * 3 / 2, math.pi / 2, edgenum=8)
        else:
            draw_quad_fan(xmin, (ymin + ymax) / 2, 0, 3,
                          math.pi / 2, math.pi * 3 / 2, edgenum=8)

        ## RoundedBox
        bgl.glColor4f(*colors.inner_back)
        draw_rounded_box(xmin, ymin, xmax, ymax, round_radius, poly=True)
        if menu.active == i:
            bgl.glColor4f(*colors.inner_sel)
        else:
            if settings.tricky and self.mouseco_right:
                bgl.glColor4f(*colors.inner_right_menu)
            else:
                bgl.glColor4f(*colors.inner)
        draw_rounded_box(xmin, ymin, xmax, ymax, round_radius, poly=True)
        bgl.glColor4f(*(item.color if item.color else colors.outline))
        draw_rounded_box(xmin, ymin, xmax, ymax, round_radius)
        ## Child Marker
        if item.child:
            b = math.sqrt(2)
            f = b * math.sin(math.pi / 4) / 2
            if menu.active == i:
                size = ((xmax - 2, ymin + 2), 12 * b, (12 * f, -12 * f))
            else:
                size = ((xmax - 2, ymin + 2), 8 * b, (8 * f, -8 * f))
            bgl.glColor4f(*colors.marker)
            draw_triangle(*size, poly=True)
            bgl.glColor4f(*colors.marker_outline)
            draw_triangle(*size)
        ## Text
        bgl.glColor4f(*(colors.text_sel if menu.active == i else colors.text))
        blf.position(0, xmin + text_ofs, ymin + text_ofs + text_ofsy, 0)
        blf.draw(0, text)
        ## Shortcut
        if item.shortcut:
            if item.shortcut.draw_shortcut:
                text = item.shortcut.label()
                text_width, _text_height = blf.dimensions(0, text)
                if position == 'left':
                    x = xmin - text_width - text_ofs
                    blf.position(0, x, ymin + text_ofs + text_ofsy, 0)
                else:
                    blf.position(0, xmax + text_ofs,
                                 ymin + text_ofs + text_ofsy, 0)
                blf.draw(0, text)

        angle -= itemangle

    ## Center Circle
    bgl.glColor4f(*colors.line)
    draw_circle(xo, yo, center_radius, 32)

    ## Center Hand
    if menu.active != -1:
        handlength, base_w, top_w = settings.handsize
        handlength = menuradius - center_radius + handlength
        v = relative.normalized()
        bgl.glColor4f(*colors.hand)
        draw_trapezoid((mouseco_menu + v * center_radius).to_2d(),
                       (v * handlength).to_2d(), base_w, top_w, poly=True)
        bgl.glColor4f(*colors.handoutline)
        draw_trapezoid((mouseco_menu + v * center_radius).to_2d(),
                       (v * handlength).to_2d(), base_w, top_w)

    ## Center Marker
    if menu.parent:
        bgl.glColor4f(*colors.marker)
        draw_triangle((xo, yo + center_radius - 4), 9, (0, 9), poly=True)
        bgl.glColor4f(*colors.marker_outline)
        draw_triangle((xo, yo + center_radius - 4), 9, (0, 9))
    if menu.next:
        bgl.glColor4f(*colors.marker)
        draw_triangle((xo + center_radius - 4, yo), 9, (9, 0), poly=True)
        bgl.glColor4f(*colors.marker_outline)
        draw_triangle((xo + center_radius - 4, yo), 9, (9, 0))
    if menu.prev:
        bgl.glColor4f(*colors.marker)
        draw_triangle((xo - center_radius + 4, yo), 9, (-9, 0), poly=True)
        bgl.glColor4f(*colors.marker_outline)
        draw_triangle((xo - center_radius + 4, yo), 9, (-9, 0))

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    blf.size(0, 11, context.user_preferences.system.dpi)


def tag_redraw_all(context):
    if hasattr(context.region, 'xmin') and \
       hasattr(context.region, 'ymin') and settings.redraw_all:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    else:
        context.area.tag_redraw()


# *** Main Operator *** #
class VIEW3D_OT_pie_menu(bpy.types.Operator):
    bl_label = 'Pie Menu'
    bl_idname = 'view3d.pie_menu'
    bl_options = {'REGISTER'}
    # 'REGISTER', 'UNDO', 'BLOCKING', 'MACRO', 'GRAB_POINTER'

    menu_name = StringProperty(name='Menu', description='',
                          default='mesh_select_mode',
                          options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if bpy.context.space_data:
            return bpy.context.space_data.region_3d != None
        else:
            return False

    def check_pie_active(self, relative, pie_number):
        if relative.length <= settings.center_radius:
            active = -1
        else:
            itemangle = math.pi * 2 / pie_number
            v = Vector([0, -1, 0])
            angle = v.angle(relative)
            if v.cross(relative)[2] >= 0:
                angle = math.pi * 2 - angle
            a = itemangle / 2
            for i in range(pie_number):
                if angle < a:
                    active = i
                    break
                a += itemangle
            else:
                active = 0
        return active

    def check_pie_menu_active(self, context):
        menu = self.menu
        center = self.mouseco_menu
        mouseco = self.mouseco

        relative = mouseco - center
        active = self.check_pie_active(relative, len(menu.items))
        if active != -1:
            # item is None ?
            item = menu.items[active]
            if self.shift:
                item = item.shiftitem
            if item is None or not item.poll(context):
                active = -1
        self.menu.active = active

    def parent_menu(self, context):
        menu = self.menu
        if menu.parent:
            self.history = self.history[:-1]
            self.menu = menu.parent.menu
            self.menu.op(context)
            self.check_pie_menu_active(context)
            tag_redraw_all(context)
            return True
        else:
            tag_redraw_all(context)
            return False

    def next_menu(self, context, prev=False):
        menu = self.menu
        if (menu.next and not prev) or (menu.prev and prev):
            if menu.next and not prev:
                self.menu = menu.next
            elif menu.prev and prev:
                self.menu = menu.prev
            self.menu.op(context)
            self.check_pie_menu_active(context)
            tag_redraw_all(context)
            return True
        else:
            tag_redraw_all(context)
            return False

    def exit(self, context):
        context.region.callback_remove(self._handle)
        tag_redraw_all(context)

    def modal(self, context, event):
        mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0))
        mouseco_abs = Vector((event.mouse_x, event.mouse_y, 0))
        menu = self.menu
        valid_drag = settings.valid_drag
        tricky = settings.tricky

        do_redraw = False
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE'):
            if event.value == 'PRESS':
                if event.type == 'LEFTMOUSE':
                    if self.mouseco_middle or self.mouseco_right:
                        if tricky and self.mouseco_right:
                            #menu = self.menu = self.menu_bak
                            self.exit(context)
                            return {'CANCELLED'}
                        self.mouseco_left = self.mouseco_middle = \
                        self.mouseco_right = None
                    else:
                        self.mouseco_left = mouseco.copy()
                elif event.type == 'MIDDLEMOUSE':
                    if self.mouseco_left or self.mouseco_right:
                        if self.mouseco_right:
                            menu = self.menu = self.menu_bak
                        self.mouseco_left = self.mouseco_middle = \
                        self.mouseco_right = None
                    else:
                        self.mouseco_middle = mouseco.copy()
                        if self.shift:
                            self.mouseco_menu = mouseco.copy()
                            self.mouseco_menu_abs = mouseco_abs.copy()
                else:
                    if self.mouseco_left or self.mouseco_middle:
                        if tricky and self.mouseco_left:
                            self.exit(context)
                            return {'CANCELLED'}
                        self.mouseco_left = self.mouseco_middle = \
                        self.mouseco_right = None
                    else:
                        self.mouseco_right = mouseco.copy()
                        if tricky:
                            self.menu_bak = menu
                            menu = self.menu = menus['right_mouse_menu']
                            self.check_pie_menu_active(context)
                do_redraw = True
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self.mouseco_left:
                if (mouseco - self.mouseco_left).length <= valid_drag:
                    self.mouseco_left = None
                    active = self.menu.active
                    if active != -1:
                        item = menu.items[active]
                        if self.shift:
                            item = item.shiftitem
                        if item.child:
                            self.history.append(menu.name)
                            self.menu = item.child
                            self.check_pie_menu_active(context)
                            do_redraw = True
                        else:
                            self.exit(context)
                            item.op(context)  # Call Operator
                            return {'FINISHED'}
                    else:
                        do_redraw = True
                else:
                    self.mouseco_left = None
                    do_redraw = True
        elif event.type == 'MIDDLEMOUSE' and event.value == 'RELEASE':
            if self.mouseco_middle:
                if (mouseco - self.mouseco_middle).length <= valid_drag:
                    if tricky:
                        self.exit(context)
                        return {'CANCELLED'}
                    else:
                        self.parent_menu(context)
                        self.mouseco_middle = None
                else:
                    self.mouseco_middle = None
                    do_redraw = True
        elif event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            if self.mouseco_right:
                if tricky:
                    active = self.menu.active
                    menu = self.menu = self.menu_bak
                    if (mouseco - self.mouseco_right).length <= valid_drag:
                        self.mouseco_right = None
                        if active == 0:
                            self.exit(context)
                            return {'CANCELLED'}
                        elif active == 1:
                            self.next_menu(context, prev=True)
                        elif active == 2:
                            self.parent_menu(context)
                        elif active == 3:
                            self.next_menu(context)
                        else:
                            do_redraw = True
                    else:
                        menu = self.menu = self.menu_bak
                        self.mouseco_right = None
                        do_redraw = True
                else:
                    if (mouseco - self.mouseco_right).length <= valid_drag:
                        self.exit(context)
                        return {'CANCELLED'}
                    else:
                        self.mouseco_right = None
                        do_redraw = True
        elif event.type == 'WHEELUPMOUSE':
            self.next_menu(context, prev=True)
        elif event.type == 'WHEELDOWNMOUSE':
            self.next_menu(context)
        elif event.type == 'BUTTON6MOUSE':
            self.next_menu(context, prev=True)
        elif event.type == 'BUTTON7MOUSE':
            self.next_menu(context)
        elif event.type == 'MOUSEMOVE':
            # move menu (middle mouse)
            if event.shift and self.mouseco_middle:
                self.mouseco_menu = mouseco.copy()
                self.mouseco_menu_abs = mouseco_abs.copy()
            # active item (left mouse)
            self.mouseco = mouseco
            self.mouseco_abs = mouseco_abs
            self.check_pie_menu_active(context)
            do_redraw = True
        elif event.type in ('LEFT_SHIFT', 'RIGHT_SHIFT'):
            if event.value == 'PRESS':
                self.shift = True
            elif event.value == 'RELEASE':
                self.shift = False
            self.check_pie_menu_active(context)  # call shiftitem.poll()
            do_redraw = True
        elif event.type in ('ESC', ):
            if event.value == 'PRESS':
                self.exit(context)
                return {'CANCELLED'}
        elif event.type in ('LEFT_CTRL', 'RIGHT_CTRL') and tricky:
            if event.value == 'PRESS':
                self.exit(context)
                return {'CANCELLED'}
        else:
            item = menu.check_shortcut(event, self.shift)  # item or shiftitem
            if item:
                if item.child:
                    self.menu = item.child
                else:
                    self.exit(context)
                    item.op(context)  # Call Operator
                    return {'FINISHED'}
        if do_redraw:
            tag_redraw_all(context)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        active_space = context.space_data
        if active_space.type == 'VIEW_3D':
            if self.menu_name in menus:
                self.menu = menus[self.menu_name]
            else:
                self.report({'ERROR'}, 'Not Menu')
                return {'CANCELLED'}

            context.window_manager.modal_handler_add(self)
            # POST_PIXEL, POST_VIEW, PRE_VIEW
            self._handle = context.region.callback_add(draw_menu,
                                                 (self, context), 'POST_PIXEL')
            self.region_id = context.region.id

            # Set Mouse
            mouseco = Vector((event.mouse_region_x, event.mouse_region_y, 0))
            mouseco_abs = Vector((event.mouse_x, event.mouse_y, 0))
            self.mouseco = mouseco
            self.mouseco_menu = mouseco.copy()
            self.mouseco_abs = mouseco_abs
            self.mouseco_menu_abs = mouseco_abs.copy()
            self.mouseco_left = None  # mouseco.copy()
            self.mouseco_right = False  # next, prev, parent menu. or close.
            self.mouseco_middle = False  # move menu

            # Reset Menu
            self.menu_bak = None
            self.history = []
            for menu in menus.values():
                menu.op_called = False
            self.menu.op(context)
            self.check_pie_menu_active(context)
            self.shift = False
            tag_redraw_all(context)

            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, 'Active space must be a View3d')
            return {'CANCELLED'}


class MESH_OT_delete_loose(bpy.types.Operator):
    bl_idname = 'mesh.delete_loose'
    bl_label = 'Delete Loose Vertices and Edges'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        tool_settings = context.tool_settings
        mesh_select_mode_bak = tool_settings.mesh_select_mode[:]

        bpy.ops.object.mode_set(mode='OBJECT')
        me = context.active_object.data
        pymesh = PyMesh(me)
        rem_nan = rem_vertices = rem_edges = 0

        ## delete vertices
        tool_settings.mesh_select_mode[0] = True
        for vert, pyvert in zip(me.vertices, pymesh.vertices):
            if pyvert.is_selected:
                nan = False
                for val in pyvert.co:
                    if bool(val) and not (val >= 0.0 or val <= 0.0):
                        nan = True
                        rem_nan += 1
                if nan is False and (pyvert.faces or pyvert.edges):
                    vert.select = False
                else:
                    vert.select = True
                    rem_vertices += 1
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')

        ## delete edges
        bpy.ops.object.mode_set(mode='OBJECT')
        tool_settings.mesh_select_mode = [False, True, False]
        for edge, pyedge in zip(me.edges, pymesh.edges):
            if pyedge.is_selected:
                if pyedge.faces:
                    edge.select = False
                else:
                    edge.select = True
                    rem_edges += 1
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='EDGE')

        ## re select faces
        bpy.ops.object.mode_set(mode='OBJECT')
        tool_settings.mesh_select_mode = [False, False, True]
        if rem_nan:
            txt = 'Ve {}, Ed {}, Nan {}'
            self.report({'INFO'}, txt.format(rem_vertices, rem_edges, rem_nan))
        if not rem_nan:
            for face, pyface in zip(me.faces, pymesh.faces):
                if pyface.is_selected:
                    face.select = True
        bpy.ops.object.mode_set(mode='EDIT')  # 切替時のmesh_select_modeに注意
        tool_settings.mesh_select_mode = mesh_select_mode_bak
        return {'FINISHED'}


def generate_menus():
    red = [1.0, 0.0, 0.0, 1.0]
    green = [0.0, 1.0, 0.0, 1.0]
    brue = [0.0, 0.0, 1.0, 1.0]
    yellow = [1.0, 1.0, 0.0, 1.0]
    gray = [0.8, 0.8, 0.8, 1.0]

    menus = {}

    ### Right Mouse Menu ######################################################
    menus['right_mouse_menu'] = menu = Menu('Pie Menu')
    MenuItem(menu, 'Exit', '', shortcut=Shortcut(type='LEFTMOUSE'))
    MenuItem(menu, 'Prev', '')
    MenuItem(menu, 'Parent', '')
    MenuItem(menu, 'Next', '')

    ### 3D View ###############################################################
    km = '3D View'

    ### Manipulator ###
    menus['manipulator'] = menu = \
        Menu('Manipulator', Shortcut(type='SPACE', ctrl=True, km=km))
    def op(self, context):
        context.space_data.show_manipulator ^= True
    item = MenuItem(menu, 'Toggle', '', op,
                    shortcut=Shortcut(type='SPACE', shift=None, ctrl=None))
    # func to set manipulator
    def set_manipulator_handles(context, translate, rotate, scale):
        '''bpy.ops.view3d.enable_manipulator('INVOKE_REGION_WIN',
           translate=False, rotate=False, scale=False) と同様
        '''
        v3d = context.space_data
        v3d.use_manipulator_translate = translate
        v3d.use_manipulator_rotate = rotate
        v3d.use_manipulator_scale = scale
    def get_manipulator_handles(context):
        v3d = context.space_data
        return (v3d.use_manipulator_translate,
                v3d.use_manipulator_rotate,
                v3d.use_manipulator_scale)
    # translate
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        set_manipulator_handles(context, True, False, False)
    item = MenuItem(menu, 'Translate', '', op, shortcut=Shortcut(type='G'))
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        if get_manipulator_handles(context) != (True, False, False):
            v3d.use_manipulator_translate ^= True
    item.shiftitem = MenuItem(None, '+Translate', '', op,
                              shortcut=Shortcut(type='G', shift=True))
    # rotate
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        set_manipulator_handles(context, False, True, False)
    item = MenuItem(menu, 'Rotate', '', op, shortcut=Shortcut(type='R'))
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        if get_manipulator_handles(context) != (False, True, False):
            v3d.use_manipulator_rotate ^= True
    item.shiftitem = MenuItem(None, '+Rotate', '', op,
                              shortcut=Shortcut(type='R', shift=True))
    # scale
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        set_manipulator_handles(context, False, False, True)
    item = MenuItem(menu, 'Scale', '', op, shortcut=Shortcut(type='S'))
    def op(self, context):
        v3d = context.space_data
        v3d.show_manipulator = True
        if get_manipulator_handles(context) != (False, False, True):
            v3d.use_manipulator_scale ^= True
    item.shiftitem = MenuItem(None, '+Scale', '', op,
                              shortcut=Shortcut(type='S', shift=True))

    ### Orientation ###
    # Orientation func. add main orientation items
    def add_main_orientation_menu_items(self, context):
        self.items[:] = []  # clear
        current = context.space_data.transform_orientation
        if hasattr(context.space_data, 'use_local_grid'):
            orientations = ['GLOBAL', 'LOCAL', 'GRID',
                            'GIMBAL', 'NORMAL', 'VIEW']
        else:
            orientations = ['GLOBAL', 'LOCAL', 'GIMBAL', 'NORMAL', 'VIEW']
        for orientation in orientations:
            name = orientation.title()
            color = yellow if orientation == current else None
            def op(self, context):
                select_orientation(orientation=self.orientation)
            item = MenuItem(self, name, '', op, color=color)
            item.orientation = orientation
    # <<Orientation (next Manipulator)>>
    menus['orientation_next_manipulator'] = menu = Menu('Orientation',
                                op=add_main_orientation_menu_items)
    menu.prev = menus['manipulator']
    # <<Orientation>>
    select_orientation = bpy.ops.transform.select_orientation
    def add_orientation_menu_items(self, context):
        add_main_orientation_menu_items(self, context)
        current = context.space_data.transform_orientation
        custommenu_radius = 50
        max_item_num = 8
        page = 0
        cnt = 0
        for orientation in [o.name for o in context.scene.orientations]:
            name = orientation.title()
            color = yellow if orientation == current else None
            if page == 0:
                page = 1
                menu = Menu('Custom' + str(page))
                menu.radius = custommenu_radius
                menu.prev = self
                self.next = menu
            elif cnt >= max_item_num:
                page += 1
                menu_next = Menu('Custom' + str(page))
                menu_next.radius = custommenu_radius
                menu_next.prev = menu
                menu.next = menu_next
                menu = menu_next
                cnt = 0
            def op(self, context):
                select_orientation(orientation=self.orientation)
            item = MenuItem(menu, name, '', op, color=color)
            item.orientation = name
            def op(self, context):
                bak = context.space_data.transform_orientation
                select_orientation(orientation=self.orientation)
                rem = context.space_data.transform_orientation
                bpy.ops.transform.delete_orientation()
                if bak != rem:
                    select_orientation(orientation=bak)
            item.shiftitem = MenuItem(None, '- ' + name, '', op, color=color)
            item.shiftitem.orientation = name
            cnt += 1
        if page and cnt >= 1:  # add separator
            while cnt < max_item_num:
                menu.items.append(None)
                cnt += 1
        menu = Menu('Create')
        def op(self, context):
            bpy.ops.transform.create_orientation()
        MenuItem(menu, 'Create', '', op)
        def op(self, context):
            bpy.ops.transform.create_orientation(use=True)
        MenuItem(menu, 'Create and Use', '', op)
        self.prev = menu
        menu.next = self
    menus['orientation'] = Menu('Orientation',
                                Shortcut(type='SPACE', alt=True, km=km),
                                op=add_orientation_menu_items)

    ## Snap & Scale Zero ###
    # <<Snap>>
    menus['snap'] = menu = Menu('Snap', Shortcut(type='S', shift=True, km=km))
    def op(self, context):
        bpy.ops.view3d.snap_selected_to_grid()
    MenuItem(menu, 'Selection to Grid', '', op, color=red)
    def op(self, context):
        bpy.ops.view3d.snap_selected_to_cursor()
    MenuItem(menu, 'Selection to Cursor', '', op, color=red)
    def op(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
    MenuItem(menu, 'Cursor to Selected', '', op, color=gray)
    def op(self, context):
        bpy.ops.view3d.snap_cursor_to_center()
    MenuItem(menu, 'Cursor to Center', '', op, color=gray)
    def op(self, context):
        bpy.ops.view3d.snap_cursor_to_grid()
    MenuItem(menu, 'Cursor to Grid', '', op, color=gray)
    def op(self, context):
        bpy.ops.view3d.snap_cursor_to_active()
    MenuItem(menu, 'Cursor to Active', '', op, color=gray)

    # <<Scale zero>>
    menus['scale_zero'] = menu = Menu('Scale Zero to Cursor')
    resize = bpy.ops.transform.resize
    def do_scale_zero(self, context):
        v3d = context.space_data
        pivot = v3d.pivot_point
        v3d.pivot_point = 'CURSOR'
        resize(value=self.value, constraint_axis=self.local,
               constraint_orientation=self.orientation)
        v3d.pivot_point = pivot
    # X
    def op(self, context):
        self.value = (0.0, 1.0, 1.0)
        self.local = (True, False, False)
        self.orientation = 'GLOBAL'
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Global X', '', op)
    # Y
    def op(self, context):
        self.value = (1.0, 0.0, 1.0)
        self.local = (False, True, False)
        self.orientation = 'GLOBAL'
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Global Y', '', op)
    # Z
    def op(self, context):
        self.value = (1.0, 1.0, 0.0)
        self.local = (False, False, True)
        self.orientation = 'GLOBAL'
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Global Z', '', op)
    def op(self, context):
        self.value = (0.0, 1.0, 1.0)
        self.local = (True, False, False)
        self.orientation = context.space_data.transform_orientation
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Manipul X', '', op)
    def op(self, context):
        self.value = (1.0, 0.0, 1.0)
        self.local = (False, True, False)
        self.orientation = context.space_data.transform_orientation
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Manipul Y', '', op)
    def op(self, context):
        self.value = (1.0, 1.0, 0.0)
        self.local = (False, False, True)
        self.orientation = context.space_data.transform_orientation
        do_scale_zero(self, context)
    item = MenuItem(menu, 'Manipul Z', '', op)
    menu.prev = menus['snap']

    ### Snap element ###
    menus['snap_element'] = menu = \
        Menu('Snap Element', Shortcut(type='TAB', ctrl=True, shift=True, km=km))
    '''def op(self, context):
        snap = context.tool_settings.use_snap
        context.tool_settings.use_snap = False if snap else True
    MenuItem(menu, 'Toggle', '', op=op)
    '''
    def op(self, context):
        context.tool_settings.snap_element = 'INCREMENT'
    MenuItem(menu, 'Increment', '', op=op)
    def op(self, context):
        context.tool_settings.snap_element = 'VERTEX'
    MenuItem(menu, 'Vertex', '', op=op)
    def op(self, context):
        context.tool_settings.snap_element = 'EDGE'
    MenuItem(menu, 'Edge', '', op=op)
    def op(self, context):
        context.tool_settings.snap_element = 'FACE'
    MenuItem(menu, 'Face', '', op=op)
    def op(self, context):
        context.tool_settings.snap_element = 'VOLUME'
    MenuItem(menu, 'Volume', '', op=op)

    # Snap target
    menus['snap_target'] = menu = Menu('Snap Target')
    def op(self, context):
        context.tool_settings.snap_target = 'CLOSEST'
    MenuItem(menu, 'Closest', '', op=op)
    def op(self, context):
        context.tool_settings.snap_target = 'CENTER'
    MenuItem(menu, 'Center', '', op=op)
    def op(self, context):
        context.tool_settings.snap_target = 'MEDIAN'
    MenuItem(menu, 'Median', '', op=op)
    def op(self, context):
        context.tool_settings.snap_target = 'ACTIVE'
    MenuItem(menu, 'Active', '', op=op)

    menus['snap_target'].prev = menus['snap_element']

    ### Mesh ##################################################################
    km = 'Mesh'

    ### Mesh select mode ###
    # vert
    menus['mesh_select_mode'] = menu = \
        Menu('Mesh Select Mode', Shortcut(type='TAB', ctrl=True, km=km))
    #menu.radius = 30
    def op(self, context):
        context.tool_settings.mesh_select_mode = [True, False, False]
    item = MenuItem(menu, 'Vetrex', '', op=op)
    def op(self, context):
        mode = context.tool_settings.mesh_select_mode[:]
        if mode != [True, False, False]:
            mode[0] ^= True
            context.tool_settings.mesh_select_mode = mode
    item.shiftitem = MenuItem(name='+Vetrex', op=op)
    # edge
    def op(self, context):
        context.tool_settings.mesh_select_mode = [False, True, False]
    item = MenuItem(menu, 'Edge', '', op=op)
    def op(self, context):
        mode = context.tool_settings.mesh_select_mode[:]
        if mode != [False, True, False]:
            mode[1] ^= True
            context.tool_settings.mesh_select_mode = mode
    item.shiftitem = MenuItem(name='+Edge', op=op)
    # face
    def op(self, context):
        context.tool_settings.mesh_select_mode = [False, False, True]
    item = MenuItem(menu, 'Face', '', op=op)
    def op(self, context):
        mode = context.tool_settings.mesh_select_mode[:]
        if mode != [False, False, True]:
            mode[2] ^= True
            context.tool_settings.mesh_select_mode = mode
    item.shiftitem = MenuItem(name='+Falce', op=op)

    ### Mesh delete ###
    menus['mesh_delete'] = menu = Menu('Mesh Delete',
                                       Shortcut(type='X', km=km))
    def op(self, context):
        bpy.ops.mesh.delete()
    item = MenuItem(menu, 'Vertices', op=op)
    def op(self, context):  # shift
        bpy.ops.mesh.delete(type='EDGE_FACE')
    item.shiftitem = MenuItem(name='Edges & Faces', op=op)
    def op(self, context):
        bpy.ops.mesh.delete(type='EDGE')
    item = MenuItem(menu, 'Edges', op=op)
    def op(self, context):  # shift
        bpy.ops.mesh.delete(type='EDGE_LOOP')
    item.shiftitem = MenuItem(name='Edge Loop', op=op)
    def op(self, context):
        bpy.ops.mesh.delete(type='FACE')
    item = MenuItem(menu, 'Faces', op=op)
    def op(self, context):  # shift
        bpy.ops.mesh.delete(type='ONLY_FACE')
    item.shiftitem = MenuItem(name='Only Faces', op=op)
    def op(self, context):
        bpy.ops.mesh.delete(type='ALL')
    item = MenuItem(menu, 'All', op=op)
    def op(self, context):  # shift
        bpy.ops.mesh.delete_loose()
    item.shiftitem = MenuItem(name='Loose', op=op)

    menus['mesh_delete_sub'] = menu = Menu('Mesh Delete 2')
    def op(self, context):
        bpy.ops.mesh.delete(type='EDGE_FACE')
    MenuItem(menu, 'Edges & Faces', op=op)
    def op(self, context):
        bpy.ops.mesh.delete(type='EDGE_LOOP')
    MenuItem(menu, 'Edge Loop', op=op)
    def op(self, context):
        bpy.ops.mesh.delete(type='ONLY_FACE')
    MenuItem(menu, 'Only Faces', op=op)
    def op(self, context):
        bpy.ops.mesh.delete_loose()
    MenuItem(menu, 'Loose', op=op)

    menus['mesh_delete_sub'].prev = menus['mesh_delete']

    ### Lock Vertices ##
    menus['mesh_lock'] = menu = Menu('Lock Vertices',
                                     Shortcut(type='V', shift=True, km=km))
    def op(self, context):
        bpy.ops.mesh.lock()
    MenuItem(menu, 'Lock Selected', op=op)
    def op(self, context):
        bpy.ops.mesh.lock(unselected=True)
    MenuItem(menu, 'Lock Unselected', op=op)
    def op(self, context):
        bpy.ops.mesh.unlock()
    MenuItem(menu, 'Unock', op=op)

    ### Vertex Align ###
    # <<Vertex align (vertex)>>
    # X
    menus['vertex_align_verts'] = menu = Menu('Align Vertices')
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='x')
    item = MenuItem(menu, 'X', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='lx')
    item.shiftitem = MenuItem(name='Local X', op=op)
    # Y
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='y')
    item = MenuItem(menu, 'Y', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='ly')
    item.shiftitem = MenuItem(name='Local Y', op=op)
    # Z
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='z')
    item = MenuItem(menu, 'Z', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='lz')
    item.shiftitem = MenuItem(name='Local Z', op=op)
    # etc
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='vx')
    MenuItem(menu, 'View X', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='vy')
    MenuItem(menu, 'View Y', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='ax')
    MenuItem(menu, 'Custom', op=op)
    def op(self, context):
        bpy.ops.mesh.align_verts_to_plane('INVOKE_REGION_WIN', mode='nor')
    MenuItem(menu, 'Normal', op=op)

    # <<Vertex align (edge)>>
    menus['vertex_align_edges'] = menu = Menu('Align Edges')
    def op(self, context):
        bpy.ops.mesh.align_edges_to_plane('INVOKE_REGION_WIN', mode='single')
    MenuItem(menu, 'Move 1', op=op)
    def op(self, context):
        bpy.ops.mesh.align_edges_to_plane('INVOKE_REGION_WIN', mode='double')
    MenuItem(menu, 'Move 2', op=op)
    def op(self, context):
        bpy.ops.mesh.align_edges_to_plane('INVOKE_REGION_WIN', mode='add')
    MenuItem(menu, 'Add', op=op)

    # <<Vertex align (sub)>>
    menus['vertex_align_sub'] = menu = Menu('Vertex Align Sub')
    def op(self, context):
        bpy.ops.mesh.va_edge_unbend('INVOKE_REGION_WIN')
    MenuItem(menu, 'Edge Unbend', op=op)
    def op(self, context):
        bpy.ops.mesh.edge_intersect('INVOKE_REGION_WIN')
    MenuItem(menu, 'Edge Intersect', op=op)
    def op(self, context):
        bpy.ops.mesh.edge_slide2('INVOKE_REGION_WIN')
    MenuItem(menu, 'Edge Slide', op=op)
    def op(self, context):
        bpy.ops.mesh.va_solidify('INVOKE_REGION_WIN')
    MenuItem(menu, 'Solidify', op=op)
    def op(self, context):
        bpy.ops.mesh.shift_outline('INVOKE_REGION_WIN')
    MenuItem(menu, 'Shift Outline', op=op)
    def op(self, context):
        bpy.ops.mesh.select_verts()
    MenuItem(menu, 'Select Verts', op=op)

    # <<Vertex align>>
    menus['vertex_align'] = menu = \
        Menu('Vertex Align', Shortcut(type='A', ctrl=True, km=km))
    MenuItem(menu, 'Align Vertices', '', child=menus['vertex_align_verts'])
    MenuItem(menu, 'Align Edges', '', child=menus['vertex_align_edges'])
    def op(self, context):
        bpy.ops.mesh.mark_plane('INVOKE_REGION_WIN')
    MenuItem(menu, 'Mark Plane', op=op)
    def op(self, context):
        bpy.ops.mesh.mark_axis('INVOKE_REGION_WIN')
    MenuItem(menu, 'Mark Axis', op=op)

    menus['vertex_align_sub'].prev= menus['vertex_align']

    ## auto set Menu.next or Menu.prev. type:Menu
    for menu in menus.values():
        if menu.next:
            menu.next.prev = menu
        if menu.prev:
            menu.prev.next = menu

    ## auto set Menu.parent. type:MenuItem
    for menu in menus.values():
        for item in menu.items:
            if item and item.child:  # item.child = type: Menu
                item.child.parent = item

    return menus

menus = generate_menus()


# Register
def register():
    bpy.utils.register_module(__name__)

    keymaps = bpy.context.window_manager.keyconfigs.active.keymaps
    for name, menu in menus.items():
        if menu.shortcut and hasattr(menu.shortcut, 'km'):
            sc = menu.shortcut
            km = keymaps[menu.shortcut.km]
            for kmi in km.items:
                if kmi.type == sc.type:
                    if kmi.value == 'PRESS' and sc.press is True or \
                       kmi.value == 'RELEASE' and sc.press is False:
                        if kmi.shift == sc.shift and \
                           kmi.ctrl == sc.ctrl and \
                           kmi.alt == sc.alt and \
                           kmi.oskey == sc.oskey:
                            km.items.remove(kmi)
            value = 'PRESS' if sc.press else 'RELEASE'
            kmi = km.items.new('view3d.pie_menu', sc.type, value,
                               shift=sc.shift, ctrl=sc.ctrl, alt=sc.alt,
                               oskey=sc.oskey)
            kmi.properties.menu_name = name


def unregister():
    bpy.utils.unregister_module(__name__)



if __name__ == '__main__':
    register()
