### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

# Contact for more information about the Addon:
# Email:    germano.costa@ig.com.br
# Twitter:  wii_mano @mano_wii

bl_info = {
    "name": "Snap_Utilities_Lite",
    "author": "Germano Cavalcante",
    "version": (1, 0),
    "blender": (2, 73, 8),
    "location": "View3D > TOOLS > Mano-Addons > snap utilities",
    "description": "Extends Blender Snap controls",
    "wiki_url" : "http://cgcookiemarkets.com/blender/all-products/snap-utilities/",
    "category": "Mesh"}
    
import bpy, bgl, bmesh, mathutils, math
from mathutils import Vector, Matrix
from bpy_extras import view3d_utils
        
def get_depth(x, y):    
    depth = bgl.Buffer(bgl.GL_FLOAT, [0.0])
    bgl.glReadPixels(x, y, 1, 1, bgl.GL_DEPTH_COMPONENT, bgl.GL_FLOAT, depth)
    return depth[0]

def unProject(region, rv3d, x, y, z):
    bpy_view_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4,4],  rv3d.view_matrix.transposed())
    if 'window_matrix' in dir(rv3d): # Blender version >= 2.74
        bpy_projection_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4,4],  rv3d.window_matrix.transposed())
    else: # Blender version <= 2.73
        bpy_projection_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4, 4])
        bgl.glGetDoublev(bgl.GL_PROJECTION_MATRIX, bpy_projection_matrix)
    bpy_viewport = bgl.Buffer(bgl.GL_INT, 4, [region.x, region.y, region.width, region.height])
    world_x = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_y = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_z = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    bgl.gluUnProject(x, y, z, bpy_view_matrix, bpy_projection_matrix, bpy_viewport, world_x, world_y, world_z)        
    return Vector((world_x[0], world_y[0], world_z[0]))

def project(region, rv3d, x, y, z):
    bpy_view_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4,4],  rv3d.view_matrix.transposed())
    if 'window_matrix' in dir(rv3d): # Blender version >= 2.74
        bpy_projection_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4,4],  rv3d.window_matrix.transposed())
    else: # Blender version <= 2.73
        bpy_projection_matrix = bgl.Buffer(bgl.GL_DOUBLE, [4, 4])
        bgl.glGetDoublev(bgl.GL_PROJECTION_MATRIX, bpy_projection_matrix)
    bpy_viewport = bgl.Buffer(bgl.GL_INT, 4, [region.x, region.y, region.width, region.height])
    world_x = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_y = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    world_z = bgl.Buffer(bgl.GL_DOUBLE, 1, [0.0])
    bgl.gluProject(x, y, z, bpy_view_matrix, bpy_projection_matrix, bpy_viewport, world_x, world_y, world_z)
    return (int(world_x[0]), int(world_y[0]))

def out_Location(rv3d, region, mcursor):
    view_matrix = rv3d.view_matrix.transposed()
    orig = view3d_utils.region_2d_to_origin_3d(region, rv3d, ((mcursor[0]-region.x),(mcursor[1]-region.y)))
    vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, ((mcursor[0]-region.x),(mcursor[1]-region.y)))*-1
    v1 = Vector((int(view_matrix[0][0]*1.5),int(view_matrix[1][0]*1.5),int(view_matrix[2][0]*1.5)))
    v2 = Vector((int(view_matrix[0][1]*1.5),int(view_matrix[1][1]*1.5),int(view_matrix[2][1]*1.5)))
    
    hit = mathutils.geometry.intersect_ray_tri(Vector((1,0,0)), Vector((0,1,0)), Vector((0,0,0)), (-vector), (orig), False)
    if hit == None:
        hit = mathutils.geometry.intersect_ray_tri(v1, v2, Vector((0,0,0)), (-vector), (orig), False)        
    if hit == None:
        hit = mathutils.geometry.intersect_ray_tri(v1, v2, Vector((0,0,0)), (vector), (orig), False)
    if hit == None:
        hit = Vector((0,0,0))
    return hit

def snapUtilities(self, obj_matrix_world, bm_geom, bool_update, bm_vert_to_perpendicular, mcursor, bool_constrain, vector_constrain):
    depth = get_depth(*mcursor)
    if 'const' not in dir(self):
        self.const = None
        
    if bool_constrain == False and self.const != None:
        self.const = None

    if isinstance(bm_geom, bmesh.types.BMVert):                
        if 'bvert' not in dir(self) or self.bvert != bm_geom or bool_update == True: #globals(), vars(__builtins__):
            self.bvert = bm_geom
            self.vert = obj_matrix_world * self.bvert.co
            self.Pvert = project(self.region, self.rv3d, self.vert[0], self.vert[1], self.vert[2])            
            return self.vert, 'VERT'

        else: # when self.bvert == bm_geom:
            if abs(self.Pvert[0]-mcursor[0]) < 30 and abs(self.Pvert[1]-mcursor[1]) < 30 and depth == 1.0 or depth != 1.0:
                if bool_constrain == True:
                    if self.const == None:
                        self.const = self.vert
                        self.list_vertices = [bm_geom]
                    #point = Vector([(self.vert[index] if vector_constrain==1 else self.const[index]) for index, vector_constrain in enumerate(vector_constrain)])
                    point = mathutils.geometry.intersect_point_line(self.vert, self.const, (self.const+vector_constrain))[0]
                    #point = vector_constrain.project(self.vert)
                    return point, 'VERT' #50% is 'OUT'
                #else:
                return self.vert, 'VERT'
            
            else:
                if bool_constrain == True:
                    if self.const == None:
                        self.const = self.vert
                    orig = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 0.0)
                    end = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 1.0)
                    point = mathutils.geometry.intersect_line_line(self.const, (self.const+vector_constrain), orig, end)
                    return point[0], 'OUT'
                #else:
                return out_Location(self.rv3d, self.region, mcursor), 'OUT'
                
    if isinstance(bm_geom, bmesh.types.BMEdge):
        #print('pegou as edges',bm_geom[-1].index, 'e', bm_geom[0].index, 'agora analise')
        if 'bedge' not in dir(self) or self.bedge != bm_geom or bool_update == True:
            #print(bm_geom[0].index, bm_geom[-1].index)
            self.bedge = bm_geom
            self.vert0 = obj_matrix_world*self.bedge.verts[0].co
            self.vert1 = obj_matrix_world*self.bedge.verts[1].co
            self.po_cent = (self.vert0+self.vert1)/2
            self.Pcent = project(self.region, self.rv3d, self.po_cent[0], self.po_cent[1], self.po_cent[2])
            self.Pvert0 = project(self.region, self.rv3d, self.vert0[0], self.vert0[1], self.vert0[2])
            self.Pvert1 = project(self.region, self.rv3d, self.vert1[0], self.vert1[1], self.vert1[2])
            
            try:
                self.tan = (self.Pvert1[1]-self.Pvert0[1])/(self.Pvert1[0]-self.Pvert0[0])
                self.arctan = 1/self.tan
            except:
                self.tan = 0
                self.arctan = 0
                
            if bm_vert_to_perpendicular != None and bm_vert_to_perpendicular not in self.bedge.verts:
                vert_perp = obj_matrix_world*bm_vert_to_perpendicular.co
                point_perpendicular = mathutils.geometry.intersect_point_line(vert_perp, self.vert0, self.vert1)
                self.po_perp = point_perpendicular[0]
                self.Pperp = project(self.region, self.rv3d, self.po_perp[0], self.po_perp[1], self.po_perp[2])
            if depth == 1:
                return out_Location(self.rv3d, self.region, mcursor), 'OUT'
            else:
                return unProject(self.region, self.rv3d, mcursor[0], mcursor[1], depth), 'FACE'
            
        if 'Pperp' in dir(self) and bool_constrain == False and abs(self.Pperp[0]-mcursor[0]) < 10 and abs(self.Pperp[1]-mcursor[1]) < 10:
            return self.po_perp, 'PERPENDICULAR'
        
        elif bool_constrain == False and abs(self.Pcent[0]-mcursor[0]) < 10 and abs(self.Pcent[1]-mcursor[1]) < 10:
            return self.po_cent, 'CENTER'
        
        else:
            near_y = self.tan*(self.Pvert1[0]-mcursor[0])-(self.Pvert1[1]-mcursor[1])
            near_x = self.arctan*(self.Pvert1[1]-mcursor[1])-(self.Pvert1[0]-mcursor[0])
            if depth != 1.0 or depth == 1.0 and (abs(near_x) < 25 or abs(near_y) < 25) and (self.Pvert0[0]<mcursor[0]<self.Pvert1[0] or self.Pvert1[0]<mcursor[0]<self.Pvert0[0] or self.Pvert0[1]<mcursor[1]<self.Pvert1[1] or self.Pvert1[1]<mcursor[1]<self.Pvert0[1]):
                orig = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 0.0)
                end = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 1.0)
                if bool_constrain == True:
                    if self.const == None:
                        self.const = self.po_cent
                    point = mathutils.geometry.intersect_line_line(self.const, (self.const+vector_constrain), self.vert0, self.vert1)
                    if point == None:
                        point = mathutils.geometry.intersect_line_line(self.const, (self.const+vector_constrain), orig, end)
                    return point[0], 'EDGE'
                #else:
                point = mathutils.geometry.intersect_line_line(self.vert0, self.vert1, orig, end)
                return point[0], 'EDGE'
            else:
                if bool_constrain == True:
                    orig = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 0.0)
                    end = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 1.0)
                    if self.const == None:
                        self.const = self.po_cent
                    point = mathutils.geometry.intersect_line_line(self.const, (self.const+vector_constrain), orig, end)
                    return point[0], 'OUT'
                #else:
                return out_Location(self.rv3d, self.region, mcursor), 'OUT'
                    
    if isinstance(bm_geom, bmesh.types.BMFace):
        if 'normal_face' in dir(self):
            self.normal_face = (bm_geom.normal*obj_matrix_world.inverted()).normalized()
            
        if bool_constrain == True:
            if self.const == None:
                if depth != 1.0:
                    self.const = Vector(unProject(self.region, self.rv3d, mcursor[0], mcursor[1], depth))
                else:
                    self.const = Vector(out_Location(self.rv3d, self.region, mcursor))
            point = mathutils.geometry.intersect_point_line(unProject(self.region, self.rv3d, mcursor[0], mcursor[1], depth), self.const, (self.const+vector_constrain))
            return point[0], 'FACE'
    
        elif depth != 1.0:
            return unProject(self.region, self.rv3d, mcursor[0], mcursor[1], depth), 'FACE'
        else:
            return out_Location(self.rv3d, self.region, mcursor), 'OUT'
    
    else:
        if bool_constrain == True:
            if self.const == None:
                if (depth != 1.0):
                    self.const = Vector(unProject(self.region, self.rv3d, mcursor[0], mcursor[1], depth))
                else:
                    self.const = Vector(out_Location(self.rv3d, self.region, mcursor))
            orig = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 0.0)
            end = unProject(self.region, self.rv3d, mcursor[0], mcursor[1], 1.0)
            point = mathutils.geometry.intersect_line_line(self.const, (self.const+vector_constrain), orig, end)
            return point[0], 'CONSTRAIN'
        else:
            return out_Location(self.rv3d, self.region, mcursor), 'OUT'

def get_isolated_edges(bmvert):
    linked = [c for c in bmvert.link_edges[:] if c.link_faces[:] == []]
    for a in linked:
        edges = [b for c in a.verts[:] if c.link_faces[:] == [] for b in c.link_edges[:] if b not in linked]
        for e in edges:
            linked.append(e)
    return linked

def split_face(mesh, Bmesh, listverts, listedges, listfaces):
    if len(listverts) >=2 and listverts[-1] not in [x for y in [a.verts[:] for a in listverts[-2].link_edges] for x in y if x != listverts[-2]]:
        if listverts[-2].link_faces[:] == []:
            if listfaces == []:
                for face in listverts[-1].link_faces:
                    testface = bmesh.geometry.intersect_face_point(face, listverts[-2].co)
                    if testface:
                        listfaces.append(face)
        else:
            face = [x for x in listverts[-1].link_faces[:] if x in listverts[-2].link_faces[:]]
            if face != []:
                listfaces.append(face[0])
        if listverts[-1] != listverts[-2]:
            edge = Bmesh.edges.new([listverts[-1], listverts[-2]])        
            listedges.append(edge)
            if listfaces == []:
                for face in listverts[-2].link_faces:
                    testface = bmesh.geometry.intersect_face_point(face, listverts[-1].co)
                    if testface:
                        listfaces.append(face)
            if listfaces != []:
                for face in list(set(listfaces)):
                    facesp = bmesh.utils.face_split_edgenet(face, list(set(listedges)))
                    bmesh.update_edit_mesh(mesh, tessface=True, destructive=True)
                listedges = []

def draw(self, obj, Bmesh, bm_geom, location, bool_merge):
    if 'list_vertices' not in dir(self):
        self.list_vertices = []

    if 'list_edges' not in dir(self):
        self.list_edges = []

    if 'list_faces' not in dir(self):
        self.list_faces = []

    if bool_merge == False:
        vertices = (bmesh.ops.create_vert(Bmesh, co=(location)))
        self.list_vertices.append(vertices['vert'][0])
        split_face(obj.data, Bmesh, self.list_vertices, self.list_edges, self.list_faces)

    elif isinstance(bm_geom, bmesh.types.BMVert):
        if (bm_geom.co - location).length < .01:
            self.list_vertices.append(bm_geom)
            for edge in get_isolated_edges(bm_geom):
                if edge not in self.list_edges:
                    self.list_edges.append(edge)
        else:
            vertices = bmesh.ops.create_vert(Bmesh, co=(location))
            self.list_vertices.append(vertices['vert'][0])
            
        split_face(obj.data, Bmesh, self.list_vertices, self.list_edges, self.list_faces)
        
    elif isinstance(bm_geom, bmesh.types.BMEdge):
        self.list_edges.append(bm_geom)
        vector_p0_l = (bm_geom.verts[0].co-location)
        vector_p1_l = (bm_geom.verts[1].co-location)
        vector_p0_p1 = (bm_geom.verts[0].co-bm_geom.verts[1].co)
        factor = vector_p0_l.length/bm_geom.calc_length()
        if 0 < factor < 1 and vector_p1_l <  vector_p0_p1 and round(vector_p0_l.angle(vector_p1_l), 2) == 3.14:                  
            vertex0 = bmesh.utils.edge_split(bm_geom, bm_geom.verts[0], factor)
            self.list_vertices.append(vertex0[1])
            self.list_edges.append(vertex0[0])
                                
            split_face(obj.data, Bmesh ,self.list_vertices, self.list_edges, self.list_faces)
            self.list_edges = []
        else:
            vertices = bmesh.ops.create_vert(Bmesh, co=(location))
            self.list_vertices.append(vertices['vert'][0])
            split_face(obj.data, Bmesh, self.list_vertices, self.list_edges, self.list_faces)

    elif isinstance(bm_geom, bmesh.types.BMFace):
        vertices = (bmesh.ops.create_vert(Bmesh, co=(location)))
        self.list_vertices.append(vertices['vert'][0])
        self.list_faces.append(bm_geom)
        split_face(obj.data, Bmesh, self.list_vertices, self.list_edges, self.list_faces)
        
    return self.list_vertices

def region_3d_view(self, context):
    # draw 3d point OpenGL in the 3D View
    bgl.glEnable(bgl.GL_BLEND)
    if self.bool_constrain:
        if self.vector_constrain == Vector((1,0,0)):
            Color4f = (1.0, 0.0, 0.0, 1.0)
        elif self.vector_constrain == Vector((0,1,0)):
            Color4f = (0.0, 1.0, 0.0, 1.0)
        elif self.vector_constrain == Vector((0,0,1)):
            Color4f = (0.0, 0.0, 1.0, 1.0)
        else:
            Color4f = (0.8, 0.5, 0.4, 1.0)
    else:
        if self.type == 'OUT':
            Color4f = (0.0, 0.0, 0.0, 0.5)
        elif self.type == 'FACE':
            Color4f = (1.0, 0.8, 0.0, 1.0)
        elif self.type == 'EDGE':
            Color4f = (0.0, 0.8, 1.0, 1.0)
        elif self.type == 'VERT':
            Color4f = (1.0, 0.5, 0.0, 1.0)
        elif self.type == 'CENTER':
            Color4f = (1.0, 0.0, 1.0, 1.0)
        elif self.type == 'PERPENDICULAR':
            Color4f = (0.1, 0.5, 0.5, 1.0)
    bgl.glColor4f(*Color4f)
    bgl.glDepthRange(0,0)    
    bgl.glPointSize(10)    
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex3f(*self.location)
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)

    # draw 3d line OpenGL in the 3D View
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glDepthRange(0,0.9999)
    bgl.glColor4f(1.0, 0.8, 0.0, 1.0)    
    bgl.glLineWidth(2)    
    bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glBegin(bgl.GL_LINE_STRIP)
    for vert_co in [vert.co for vert in self.list_vertices]:
        Gvert_co =  self.obj_matrix*vert_co
        bgl.glVertex3f(*Gvert_co)        
    bgl.glVertex3f(*self.location)        
    bgl.glEnd()
        
    # restore opengl defaults
    bgl.glDepthRange(0,1)
    bgl.glPointSize(1)
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glDisable(bgl.GL_LINE_STIPPLE)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    
    a = ""
    if self.list_vertices != [] and self.length_entered == "":
        a = 'length: '+str(round((self.list_vertices[-1].co-self.location).length, 3))
    elif self.list_vertices != [] and self.length_entered != "":
        a = 'length: '+self.length_entered

    context.area.header_text_set("hit: %.3f %.3f %.3f %s" % (self.location[0], self.location[1], self.location[2], a))
    
class PanelSnapUtilities(bpy.types.Panel) :
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Mano-Addons"
    bl_label = "snap utilities"
    
    @classmethod
    def poll(cls, context):
        return (context.object is not None and
                context.object.type == 'MESH')

    def draw(self, context):
        layout = self.layout
        view = context.space_data
        row = layout.row()
        TheCol = layout.column(align = True)
        TheCol.operator("mesh.snap_utilities_line_lite", icon="GREASEPENCIL")
        
class Constrain:
    keys = {
        'X': Vector((1,0,0)),
        'Y': Vector((0,1,0)),
        'Z': Vector((0,0,1)),
        'RIGHT_SHIFT': 'shift',
        'LEFT_SHIFT': 'shift',
        }

    def __init__(self, bool_constrain = False, vector_constrain = None):
        self.bool_constrain = bool_constrain
        self.vector_constrain = vector_constrain

    def modal(self, context, event):
        if event.value == 'PRESS':
            if self.vector_constrain == self.keys[event.type] or self.bool_constrain == False:
                self.bool_constrain = self.bool_constrain == False
                self.vector_constrain = self.keys[event.type]
                
            elif event.shift:
                if self.vector_constrain not in self.keys.values():
                    self.bool_constrain = self.bool_constrain == False
                    self.vector_constrain = self.keys[event.type]
                    
            else:
                self.vector_constrain = self.keys[event.type]
                    
        return self.bool_constrain, self.vector_constrain
    
class CharMap:
    keys = {
        'PERIOD':".", 'NUMPAD_PERIOD':".",
        'MINUS':"-", 'NUMPAD_MINUS':"-",
        'EQUAL':"+", 'NUMPAD_PLUS':"+",
        'ONE':"1", 'NUMPAD_1':"1",
        'TWO':"2", 'NUMPAD_2':"2",
        'THREE':"3", 'NUMPAD_3':"3",
        'FOUR':"4", 'NUMPAD_4':"4",
        'FIVE':"5", 'NUMPAD_5':"5",
        'SIX':"6", 'NUMPAD_6':"6",
        'SEVEN':"7", 'NUMPAD_7':"7",
        'EIGHT':"8", 'NUMPAD_8':"8",
        'NINE':"9", 'NUMPAD_9':"9",
        'ZERO':"0", 'NUMPAD_0':"0",
        'SPACE':" ",
        'SLASH':"/", 'NUMPAD_SLASH':"/",
        'NUMPAD_ASTERIX':"*",
        'BACK_SPACE':"", 'DEL':""
        }

    def __init__(self, length_entered = ""):
        self.length_entered = length_entered

    def modal(self, context, event):
        # Currently accessing event.ascii seems to crash Blender
        c = self.keys[event.type]
        if event.shift:
            if c == "8":
                c = "*"
            elif c == "5":
                c = "%"
            elif c == "9":
                c = "("
            elif c == "0":
                c = ")"

        if event.value == 'PRESS':
            self.length_entered += c
            if event.type in {'BACK_SPACE', 'DEL'} and len(self.length_entered) >= 1:
                self.length_entered = self.length_entered[:-1]

        return self.length_entered

class Navigation:
    keys = {
        'MIDDLEMOUSE',
        'WHEELDOWNMOUSE',
        'WHEELUPMOUSE',
        }

    def __init__(self, rv3d, location):
        self.rv3d = rv3d
        self.location = location

    def modal(self, context, event):
        if event.type == 'MIDDLEMOUSE':
            self.rotMat = self.rv3d.view_matrix.copy()
            if event.value == 'PRESS':
                if event.shift:
                    bpy.ops.view3d.move('INVOKE_DEFAULT')
                        
                else:
                    bpy.ops.view3d.rotate('INVOKE_DEFAULT')

        if event.type in {'WHEELDOWNMOUSE', 'WHEELUPMOUSE'}:
            delta = (event.type == 'WHEELUPMOUSE') - (event.type == 'WHEELDOWNMOUSE')
            if self.rv3d.is_perspective:
                rotMat = self.rv3d.view_matrix
                d = rotMat.translation
                retVec = -d * rotMat
                mat_loc = mathutils.Matrix.Translation((retVec-self.location)/6*delta)
                self.rv3d.view_matrix = self.rv3d.view_matrix*mat_loc
            elif not self.rv3d.is_perspective:
                view_distance = self.rv3d.view_distance
                self.rv3d.view_distance -= delta*self.rv3d.view_distance/6

class InvokeClass():
    def invoke(self, context, event):
        self.is_editmode = bpy.context.object.data.is_editmode
        bpy.ops.object.mode_set(mode='EDIT')
        context.space_data.use_occlude_geometry = True
        
        self.use_rotate_around_active = context.user_preferences.view.use_rotate_around_active
        context.user_preferences.view.use_rotate_around_active = True
        
        self.select_mode = context.tool_settings.mesh_select_mode[:]
        context.tool_settings.mesh_select_mode = (True, True, True)
        
        self.region = context.region
        self.rv3d = context.region_data
        self.rotMat = self.rv3d.view_matrix
        self.obj = bpy.context.active_object
        self.obj_matrix = self.obj.matrix_world.copy()
        self.bm = bmesh.from_edit_mesh(self.obj.data)
        
        self.list_vertices = []
        self.bool_constrain = False
        self.bool_update = False
        self.vector_constrain = None
        self.keytab = False
        self.length_entered = ""
        self._handle = bpy.types.SpaceView3D.draw_handler_add(region_3d_view, (self, context), 'WINDOW', 'POST_VIEW')
        context.window_manager.modal_handler_add(self)
    
        return {'RUNNING_MODAL'}

class OperatorSnapUtilitiesLine(bpy.types.Operator):
    """using events"""
    bl_idname = "mesh.snap_utilities_line_lite"
    bl_label = "LINE"
    bl_options = {'REGISTER', 'UNDO'}
    
    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
            if self.rv3d.view_matrix != self.rotMat:
                self.rotMat = self.rv3d.view_matrix
                self.bool_update = True
            else:
                self.bool_update = False

        if event.type in Navigation.keys:
            Navigation.modal(self, context, event)

        if event.type in Constrain.keys:
            Constrain2 = Constrain(self.bool_constrain, self.vector_constrain)
            self.bool_constrain, self.vector_constrain = Constrain2.modal(context, event)
            if self.vector_constrain == 'shift':
                if isinstance(self.geom, bmesh.types.BMEdge):
                    self.vector_constrain = self.obj_matrix*self.geom.verts[1].co-self.obj_matrix*self.geom.verts[0].co
                else:
                    self.bool_constrain = False

        elif event.type in CharMap.keys and event.value == 'PRESS':
            CharMap2 = CharMap(self.length_entered)
            self.length_entered = CharMap2.modal(context, event)
            print(self.length_entered)
        
        elif event.type == 'MOUSEMOVE':
            x, y = (event.mouse_region_x, event.mouse_region_y)
            self.mouse_coods = (self.region.x+x), (self.region.y+y)
            bpy.ops.view3d.select(extend=False, location=(x, y))# This operator also starts the handler of the view 3d. Only Edit Mode. why?
            if self.list_vertices != []:
                bm_vert_to_perpendicular = self.list_vertices[-1]
            else:
                bm_vert_to_perpendicular = None
            
            try:
                self.geom = self.bm.select_history[0]
            except: # IndexError or AttributeError:
                self.geom = None
                
            self.location, self.type = snapUtilities(self, self.obj_matrix, self.geom, self.bool_update, bm_vert_to_perpendicular, self.mouse_coods, self.bool_constrain, self.vector_constrain)
            
        elif event.type == 'LEFTMOUSE':# and event.value == 'PRESS':
            if event.value == 'PRESS':
                # SNAP 2D
                snap_3d = self.location
                Lsnap_3d = self.obj_matrix.inverted()*snap_3d
                LSnap_2d = project(self.region, self.rv3d, snap_3d[0], snap_3d[1], snap_3d[2])
                Snap_2d = int(LSnap_2d[0]-self.region.x), int(LSnap_2d[1]-self.region.y)
                
                # SELECT AND DRAW
                bpy.ops.view3d.select(extend=False, location=(Snap_2d))
                try:
                    geom2 = self.bm.select_history[0]
                except: # IndexError or AttributeError:
                    geom2 = None
                bool_merge = self.type != 'OUT'
                self.bool_constrain = False
                self.list_vertices = draw(self, self.obj, self.bm, geom2, Lsnap_3d, bool_merge)
            
        elif event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'RELEASE':
            if self.length_entered != "" and self.list_vertices != []:
                try:
                    text_value = eval(self.length_entered, math.__dict__)
                    vector_h0_h1 = (self.obj_matrix.inverted()*self.location-self.list_vertices[-1].co).normalized()
                    location = ((vector_h0_h1*text_value)+self.list_vertices[-1].co)
                    bool_merge = self.type != 'OUT'
                    self.list_vertices = draw(self, self.obj, self.bm, self.geom, location, bool_merge)
                    self.length_entered = ""
                
                except:# ValueError:
                    self.report({'INFO'}, "Operation not supported yet")
        
        elif event.type == 'TAB' and event.value == 'PRESS':
            self.keytab = self.keytab == False
            if self.keytab:            
                context.tool_settings.mesh_select_mode = (False, False, True)
            else:
                context.tool_settings.mesh_select_mode = (True, True, True)
            
        elif event.type in {'RIGHTMOUSE', 'ESC'} and event.value == 'RELEASE':
            if self.list_vertices == [] or event.type == 'ESC':                
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                context.tool_settings.mesh_select_mode = self.select_mode
                context.area.header_text_set()
                context.user_preferences.view.use_rotate_around_active = self.use_rotate_around_active
                if not self.is_editmode:
                    bpy.ops.object.editmode_toggle()
                return {'FINISHED'}
            else:
                self.list_vertices = []
                self.list_faces = []
                
        return {'RUNNING_MODAL'} 

    def invoke(self, context, event):        
        if context.space_data.type == 'VIEW_3D':
            return InvokeClass.invoke(self, context, event)
        else:
            self.report({'WARNING'}, "Active space must be a View3d")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(PanelSnapUtilities)
    bpy.utils.register_class(OperatorSnapUtilitiesLine)

def unregister():
    bpy.utils.unregister_class(PanelSnapUtilities)
    bpy.utils.unregister_class(OperatorSnapUtilitiesLine)

if __name__ == "__main__":
    register()
