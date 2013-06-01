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
    'name': 'Export Inkscape SVG',
    'author': 'chromoly',
    'version': (0, 0, 1),
    'blender': (2, 5, 6),
    'api': 34765,
    'location': 'File > Export',
    'description': '',
    'warning': '',
    'category': 'Import-Export'}

'''
BezierCurve, PolyCurveのみ出力。
'''


import os

import bpy
from bpy.props import *
from mathutils import Matrix, Vector, geometry
from mathutils.geometry import interpolate_bezier
from va.view import convert_world_to_window


DOC_MIN_SIZE = 10  # SVG文書の一辺の長さがこれ以上であることを保証する
BEZIER_SUBDIVIDE = 20  # SVG文書の大きさを計算する際のBezierポイント間の分割数


class Data:
    def __init__(self, op):
        self.actob = bpy.context.active_object

        self.filepath = op.filepath
        self.coordinate = op.coordinate
        self.scale = op.scale
        self.fix = op.fix
        self.line_width = op.line_width
        self.ofs = op.ofs

        self.l = []  # list of strings
        #self.pysplines = []  # list of PySpline
        self.pysplines_dict = {}  # ob.name: [PySpline, PySpline, ...]
        self.doc_sx = 0
        self.doc_sy = 0
        self.matrix = None


class PySpline:
    def __init__(self, type='', cyclic=False):
        self.type = type
        self.cyclic = cyclic
        self.points = []
        self.bpoints = []  # bezier
        self.handletypes = []  # BEZIER only.'FREE', 'AUTO', 'VECTOR', 'ALIGNED


# format(width=str(1024), height=str(1024))
svg_header = \
'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="{width}"
   height="{heigth}"
   version="1.1">
'''

svg_metadata = \
'''  <metadata
     id="metadata0">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
      </cc:Work>
    </rdf:RDF>
  </metadata>
'''

# format(fill=none, width=str(1.0))
path_style = ';'.join(['       style="color:#000000',
                       'fill:{fill}',
                       'stroke:#000000',
                       'stroke-width:{width}',
                       'stroke-linecap:butt',
                       'stroke-linejoin:miter',
                       'stroke-miterlimit:4',
                       'stroke-opacity:1'
                       'stroke-dasharray:none',
                       'stroke-dashoffset:0',
                       'marker:none',
                       'visibility:visible',
                       'display:inline',
                       'overflow:visible',
                       'enable-background:accumulate',
                       'fill-opacity:0.2"\n'])

# format(type=sscs)
path_nodetypes = \
'''       inkscape:connector-curvature="0"
       sodipodi:nodetypes="{type}"'''


def add_style_nodetypes_closepath(data, cyclic, nodetypes=None):
    l = data.l
    # style
    fill = '#000000' if cyclic else 'none'
    width = data.line_width if data.line_width > 0.0 else 'none'
    l.append(path_style.format(fill=fill, width=width))

    # node type
    if nodetypes is not None:
        l.append(path_nodetypes.format(type=nodetypes) + ' />\n')
    else:
        l.append('/>\n')


def make_curve_splines(data, ob):
    context = bpy.context
    mat = ob.matrix_world
    if data.coordinate == 'active':
        '''
        v * mat * actob.matrix_world.inverted() == \
        v * (actob.matrix_world.inverted() * mat)
        '''
        actob = data.actob
        if actob:
            quat = actob.matrix_world.to_3x3().to_quaternion()
            m4 = quat.to_matrix().to_4x4()
            mat = m4.inverted() * mat
    pysplines = data.pysplines_dict[ob.name] = []
    curve = ob.data
    for spline in curve.splines:
        if spline.hide or spline.type not in ('POLY', 'BEZIER'):
            # hide:objectModeでも隠れたまま
            continue
        if not spline.points and not spline.bezier_points:
            continue

        cyclic = spline.use_cyclic_u
        if spline.type == 'POLY':
            pysp = PySpline('POLY', cyclic)
            for p in spline.points:
                pysp.points.append(p.co * mat)
            pysplines.append(pysp)
        elif spline.type == 'BEZIER':
            pysp = PySpline('BEZIER', cyclic)
            bezier_points = spline.bezier_points
            for bp in bezier_points:
                pysp.bpoints.append([bp.handle_left * mat, bp.co * mat,
                                     bp.handle_right * mat])
                pysp.handletypes.append([bp.handle_left_type,
                                         bp.handle_right_type])
            # cacl point (for calc_document_size())
            if len(bezier_points) == 1:
                pysp.points.append(bezier_points[0].co * mat)
            elif len(bezier_points) >= 2:
                bps = bezier_points[:]
                if cyclic:
                    bps.append(bps[0])
                for bp1, bp2 in zip(bps, bps[1:]):
                    ps = interpolate_bezier(bp1.co * mat, bp1.handle_right * mat,
                                      bp2.co * mat, bp2.handle_left * mat,
                                      BEZIER_SUBDIVIDE)
                    pysp.points.extend(ps)
            pysplines.append(pysp)


def make_mesh_splines(data, ob):
    return


def calc_document_size(data):
    xcoords = []
    ycoords = []
    xcoords_append = xcoords.append  # appendをその都度呼び出すより速いらしい
    ycoords_append = ycoords.append
    for pysplines in data.pysplines_dict.values():
        for pysp in pysplines:
            for p in pysp.points:
                xcoords_append(p[0])
                ycoords_append(p[1])
    if xcoords and ycoords:
        # Calc Document size
        xmin = min(xcoords)
        xmax = max(xcoords)
        ymin = min(ycoords)
        ymax = max(ycoords)
        sx = abs(xmax - xmin)
        sy = abs(ymax - ymin)
        ofs2 = data.ofs * 2
        if data.fix:
            if sx >= sy:
                doc_sx = max(data.scale, DOC_MIN_SIZE)
                if sx == 0.0:
                    doc_sy = max(ofs2, DOC_MIN_SIZE)
                else:
                    doc_sy = max((data.scale - ofs2) * (sy / sx) + ofs2,
                                 DOC_MIN_SIZE)
            else:
                doc_sy = max(data.scale, DOC_MIN_SIZE)
                if sy == 0.0:
                    doc_sx = max(ofs2, DOC_MIN_SIZE)
                else:
                    doc_sx = max((data.scale - ofs2) * (sx / sy) + ofs2,
                                 DOC_MIN_SIZE)
            # Transform Matix
            if sx >= sy:
                scale = (doc_sx - ofs2) / sx
            else:
                scale = (doc_sy - ofs2) / sy
        else:
            sx = max(sx, DOC_MIN_SIZE / data.scale, ofs2 / data.scale)
            sy = max(sy, DOC_MIN_SIZE / data.scale, ofs2 / data.scale)
            size = sorted([sx * data.scale + ofs2,
                           sy * data.scale + ofs2])
            if sx >= sy:
                doc_sy, doc_sx = size
            else:
                doc_sx, doc_sy = size
            # Transform Matix
            if sx >= sy:
                scale = (doc_sx - ofs2) / sx
            else:
                scale = (doc_sy - ofs2) / sy
        xcent = (xmin + xmax) / 2
        ycent = (ymin + ymax) / 2
        mat_trans = Matrix.Translation(Vector([-xcent, -ycent, 0]))
        mat_scale = Matrix.Scale(scale, 4)
        mat_scale[1][1] = -scale
        mat_trans2 = Matrix.Translation(Vector([doc_sx / 2, doc_sy / 2, 0]))
        matrix = mat_trans2 * mat_scale * mat_trans

        data.doc_sx = doc_sx
        data.doc_sy = doc_sy
        data.matrix = matrix


def handle_type_to_node_type(l, r):
    if l == r == 'AUTO':
        return 'a'
    elif l == 'ALIGNED' or r == 'ALIGNED':
        return 's'
    else:
        return 'c'


def convert_splines_to_strings(data):
    l = data.l
    mat = data.matrix
    for name, splines in data.pysplines_dict.items():
        l.append('  <g id="{name}">\n'.format(name=name))
        for i in range(len(splines)):
            # each spline
            spline = splines[i]
            if spline.type not in ('POLY', 'BEZIER'):
                continue
            cyclic = spline.cyclic
            l.append('    <path\n')

            text = '       d="'
            if spline.type == 'POLY':
                points = spline.points
                p = points[0]
                co = p * mat
                if len(points) == 1:
                    text += 'M {0},{1}"\n'.format(co[0], co[1])  # close
                else:
                    text += 'M {0},{1} L'.format(co[0], co[1])
                    for p in points:
                        co = p * mat
                        text += '{0},{1} '.format(co[0], co[1])
                if cyclic:
                    text += 'z"\n'
                else:
                    text += '"\n'
                nodetypes = None
            elif spline.type == 'BEZIER':
                bpoints = spline.bpoints
                handletypes = spline.handletypes
                bp = bpoints[0]
                co = bp[1] * mat
                nodetypes = handle_type_to_node_type(*handletypes[0])
                if len(bpoints) == 1:
                    text += 'M {0},{1}"\n'.format(co[0], co[1])  # close
                else:
                    text += 'M {0},{1} C'.format(co[0], co[1])
                    h1 = bp[2] * mat
                    for bp, handle in zip(bpoints[1:], handletypes[1:]):
                        co = bp[1] * mat
                        h2 = bp[0] * mat
                        text += '{0},{1} {2},{3} {4},{5} '.format(
                                h1[0], h1[1], h2[0], h2[1], co[0], co[1])
                        nodetypes += handle_type_to_node_type(*handle)
                        h1 = bp[2] * mat
                    if cyclic:
                        bp = bpoints[0]
                        co = bp[1] * mat
                        h2 = bp[0] * mat
                        text += '{0},{1} {2},{3} {4},{5} '.format(
                                h1[0], h1[1], h2[0], h2[1], co[0], co[1])
                        text += 'z"\n'
                    else:
                        text += '"\n'
            l.append(text)
            # style & node type
            add_style_nodetypes_closepath(data, cyclic, nodetypes)
        l.append('  </g>\n')
    if not data.pysplines_dict:
        l.append('   <g />\n')


def export_svg(data):
    '''
    make groups each object
    '''
    context = bpy.context
    l = data.l

    # convert curve and append strings
    if context.active_object and context.active_object.mode == 'EDIT':
        editmode = True
        selobs = [context.active_object]
    else:
        editmode = False
        selobs = context.selected_objects
    if editmode:
        bpy.ops.object.mode_set(mode='OBJECT')

    scn = context.scene
    actob = context.active_object
    selected_objects = context.selected_objects[:]
    for ob in context.selected_objects:
        ob.select = False
    for ob in (ob for ob in selobs if ob.type in ('CURVE', 'MESH')):
        if ob.type == 'MESH':
            continue  # 作業中につき
        if ob.type == 'MESH' and ob.modifiers:
            # duplicate
            ob.select = True
            scn.objects.active = ob
            bpy.ops.object.duplicate()
            ob_cp = context.active_object
            for name in [mod.name for mod in ob_cp.modifiers]:
                try:
                    bpy.ops.object.modifier_apply(modifier=name)
                except:
                    pass

            # make splines
            if ob_cp.type == 'CURVE':
                make_curve_splines(data, ob_cp)
            else:
                make_mesh_splines(data, ob_cp)

            # remove
            scn.objects.unlink(ob_cp)
            ob_cp_data = ob_cp.data
            bpy.data.objects.remove(ob_cp)
            if ob_cp.type == 'CURVE':
                bpy.data.curves.remove(ob_cp_data)
            else:
                bpy.data.meshes.remove(ob_cp_data)

        else:
            if ob.type == 'CURVE':
                make_curve_splines(data, ob)
            else:
                make_mesh_splines(data, ob)
    for ob in selected_objects:
        ob.select = True
    scn.objects.active = actob

    calc_document_size(data)
    convert_splines_to_strings(data)

    if editmode:
        bpy.ops.object.mode_set(mode='EDIT')

    # head, end
    width = max(data.doc_sx, DOC_MIN_SIZE)
    height = max(data.doc_sy, DOC_MIN_SIZE)
    l[:0] = [svg_header.format(width=width, heigth=height)]
    l[1:1] = [svg_metadata]
    l.append('</svg>\n')

    # open, write, close
    buf = open(data.filepath, 'w', encoding='utf-8')
    txt = ''.join(l)
    #print(txt)
    buf.write(txt)
    buf.close()


class EXPORT_OT_inkscape_svg(bpy.types.Operator):
    ''' Convert Curve to SVG '''
    bl_description = 'Export BezierCurves and PolyCurves'
    bl_idname = 'export.inkscape_svg'
    bl_label = 'Export Inkscape SVG'
    bl_options = {'REGISTER', 'UNDO', 'BLOCKING'}

    filepath = StringProperty(subtype='FILE_PATH')
    coordinate = EnumProperty(items=(('global', 'Global', ''),
                                     ('active', 'ActiveObject', '')),
                              name='Coordinate',
                              description='Ues X-Y coordinate',
                              default='global')
    scale = FloatProperty(name='Pixel / BlenderUnit',
                          description='SVG document size',
                          default=1024.0, min=0.0001, soft_min=0.0001)
    fix = BoolProperty(name='Fix Document Size',
                       description='SVG document width or height is ' + \
                                   "'Pixel/BlenderUnit' value",
                       default=True)
    line_width = FloatProperty(name='Line Width', description='Line width',
                               default=1.0, min=0.0, soft_min=0.0)
    ofs = FloatProperty(name='Offset', description='Offset',
                        default=10.0, min=0.0, soft_min=0.0)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        data = Data(self)
        filepath = data.filepath
        if not filepath.endswith('.svg'):
            filepath += '.svg'
        export_svg(data)
        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def menu_func(self, context):
    filepath = os.path.splitext(bpy.data.filepath)[0] + '.svg'
    op = self.layout.operator(EXPORT_OT_inkscape_svg.bl_idname,
                              text="Inkscape SVG (.svg)")
    op.filepath = filepath


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == '__main__':
    register()
