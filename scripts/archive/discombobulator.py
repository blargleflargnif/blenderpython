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
    "name": "Discombobulator",
    "description": "Its job is to easily add scifi details to a surface to create nice-looking space-ships or futuristic cities.",
    "author": "Chichiri",
    "version": (0,1),
    "blender": (2, 5, 9),
    "api": 39631,
    "location": "Spacebar > Discombobulate",
    "warning": 'Beta',
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=<number>",
    "category": "Mesh"}
 
import bpy, bmesh
import random
import mathutils
import math
 
doprots = True
 
# Datas in which we will build the new discombobulated mesh
nFaces = []
nVerts = []
Verts = []
Faces = []
dVerts = []
dFaces = []
i_prots = [] # index of the top faces on whow we will generate the doodads
i_dood_type = [] # type of doodad (given by index of the doodad obj)
 
bpy.types.Scene.DISC_doodads = []
 
def randnum(a, b):
    return random.random()*(b-a)+a
 
def randVertexOnQuad(a, b, c, d, Verts):
    ''' return a vector of a random vertex on a quad-face'''
    i = random.randint(1,2)
    A, B, C, D = 0, 0, 0, 0
    if(a==1):
        A, B, C, D = a, b, c, d
    else:
        A, B, C, D = a, d, c, b
   
    i = randnum(0.1, 0.9)
   
    vecAB = [Verts[B][0]-Verts[A][0], Verts[B][1]-Verts[A][1], Verts[B][2]-Verts[A][2]]
    E = [Verts[A][0]+vecAB[0]*i, Verts[A][1]+vecAB[1]*i, Verts[A][2]+vecAB[2]*i]
   
    vecDC = [Verts[C][0]-Verts[D][0], Verts[C][1]-Verts[D][1], Verts[C][2]-Verts[D][2]]
    F = [Verts[D][0]+vecDC[0]*i, Verts[D][1]+vecDC[1]*i, Verts[D][2]+vecDC[2]*i]
   
    i = randnum(0.1, 0.9)
    vecEF = [F[0]-E[0], F[1]-E[1], F[2]-E[2]]
    O = [E[0]+vecEF[0]*i, E[1]+vecEF[1]*i, E[2]+vecEF[2]*i]
    return O

def randVertexOnTri(a, b, c, Verts):
    ''' return a vector of a random vertex on a triangle'''
    A,  B = randnum(0,  1),  randnum(0,  1)
    if(A+B > 1):
        A = 1-A
        B = 1-B
    C = 1-A-B
    print(mathutils.Vector(Verts[a])*A)
    return mathutils.Vector(Verts[a])*A+mathutils.Vector(Verts[b])*B+mathutils.Vector(Verts[c])*C

################################ Protusions ###################################

def fill_older_datas(verts, face):
    ''' Specifically coded to be called by the function addProtusionToFace, its sets up a tuple which contains the vertices from the base and the top of the protusions. '''
    temp_vertices = [] 
    for i in face:
        temp_vertices.append(list(verts[i]))
    return temp_vertices

def add_base(temp_vertices, face, verts):
    for i in face:
        temp_vertices.append(list(verts[i]))
   
def extrude_top(temp_vertices, normal, height):
    ''' This function extrude the face composed of the four first members of the tuple temp_vertices along the normal multiplied by the height of the extrusion.'''
    j = 0
    while j < 3:
        for vert in temp_vertices:
            vert[j]+=list(normal)[j]*height
        j+=1
 
def scale_top(temp_vertices, center, normal, height, scale_ratio):
    ''' This function scale the face composed of the four first members of the tuple temp_vertices. '''
    vec = [0, 0, 0]
    j = 0
    while j < 3:
        for vert in temp_vertices:
            center[j]+=list(normal)[j]*height
            vec[j] = vert[j] - center[j]
            vert[j] = center[j] + vec[j]*(1-scale_ratio)
        j+=1
 
def add_prot_faces(temp_vertices):
    ''' Specifically coded to be called by addProtusionToFace, this function put the data from the generated protusion at the end the tuples Verts and Faces, which will later used to generate the final mesh. '''
    global Verts
    global Faces
    global i_prots
   
    findex = len(Verts)
    Verts+=temp_vertices
    
    if(len(temp_vertices) == 8):
        facetop = [findex+0, findex+1, findex+2, findex+3]
        face1 = [findex+0, findex+1, findex+5, findex+4]
        face2 = [findex+1, findex+2, findex+6, findex+5]
        face3 = [findex+2, findex+3, findex+7, findex+6]
        face4 = [findex+3, findex+0, findex+4, findex+7]
        Faces.append(facetop)
        i_prots.append(len(Faces)-1)
        Faces.append(face1)
        Faces.append(face2)
        Faces.append(face3)
        Faces.append(face4)
    if(len(temp_vertices) == 6):
        facetop = [findex+0, findex+1, findex+2]
        face1 = [findex+0, findex+1, findex+4, findex+3]
        face2 = [findex+1, findex+2, findex+5, findex+4]
        face3 = [findex+2, findex+5, findex+3, findex+0]
        Faces.append(facetop)
        i_prots.append(len(Faces)-1)
        Faces.append(face1)
        Faces.append(face2)
        Faces.append(face3)

def addProtusionToFace(obface, verts, minHeight, maxHeight, minTaper, maxTaper):
    '''Create a protusion from the face "obface" of the original object and use several values sent by the user. It calls in this order the following functions:
       - fill_older_data;
       - extrude_top;
       - scale_top;
       - add_prot_faces;
   '''
    # some useful variables
    face = tuple(obface.vertices)
    facetop = face
    face1 = []
    face2 = []
    face3 = []
    face4 = []
    vertices = []
    tVerts = list(fill_older_datas(verts, face)) # list of temp vertices
    height = randnum(minHeight, maxHeight) # height of generated protusion
    scale_ratio = randnum(minTaper, maxTaper)
   
    # extrude the top face
    extrude_top(tVerts, obface.normal, height)
    # Now, we scale, the top face along its normal
    scale_top(tVerts, obface.center, obface.normal, height, scale_ratio)
    # add the base
    add_base(tVerts, face, verts)
    # Finally, we add the protusions to the list of faces
    add_prot_faces(tVerts)
 
###################################################################################
################################## Divide a face ##################################
###################################################################################
# The algorithm to divide a polygon is particular, as long as bmesh is not implemented, a face can have to different number of vertices:
# - 3 for a triangle
# - 4 for a quad
# That's why when it comes to divide a face, it first checks how many vertices there is in the face and it divide the face in function of the number of
# vertices. When bmesh will be implemented, for faces with more than 4 vertices I will use the algorithm I found on this web page:
# http://blog.soulwire.co.uk/laboratory/flash/recursive-polygon-subdivision
# If anyone has a better idea, it will be welcome.
 
def divide_one(list_faces, list_vertices, verts, face, findex):
    ''' called by divide_face, to generate a face from one face, maybe I could simplify this process '''
    if(len(face) == 4):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append(list(verts[face[3]]))
        list_faces.append([findex+0, findex+1, findex+2, findex+3])
        
    elif(len(face) == 3):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_faces.append([findex+0, findex+1, findex+2])
   
def divide_two(list_faces, list_vertices, verts, face, findex):
    ''' called by divide_face, to generate two faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    if(len(face) == 4):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append(list(verts[face[3]]))
        list_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
        list_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
        list_faces.append([findex+0, findex+4, findex+5, findex+3])
        list_faces.append([findex+1, findex+2, findex+5, findex+4])
    if(len(face) == 3):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
        list_faces.append([findex+0, findex+3, findex+2])
        list_faces.append([findex+1, findex+2, findex+3])

def divide_three(list_faces, list_vertices, verts, face, findex, center):
    ''' called by divide_face, to generate three faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    if(len(face) == 4):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append(list(verts[face[3]]))
        list_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
        list_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
        list_vertices.append([(verts[face[1]][0]+verts[face[2]][0])/2, (verts[face[1]][1]+verts[face[2]][1])/2, (verts[face[1]][2]+verts[face[2]][2])/2])
        list_vertices.append(list(center))
        list_faces.append([findex+0, findex+4, findex+5, findex+3])
        list_faces.append([findex+1, findex+6, findex+7, findex+4])
        list_faces.append([findex+6, findex+2, findex+5, findex+7])
    if(len(face) == 3):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append(list(center))
        list_faces.append([findex+0, findex+1, findex+3])
        list_faces.append([findex+1, findex+2, findex+3])
        list_faces.append([findex+0, findex+2, findex+3])

def divide_four(list_faces, list_vertices, verts, face, findex, center):
    ''' called by divide_face, to generate four faces from one face and add them to the list of faces and vertices which form the discombobulated mesh'''
    if(len(face) == 4):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append(list(verts[face[3]]))
        list_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
        list_vertices.append([(verts[face[2]][0]+verts[face[3]][0])/2, (verts[face[2]][1]+verts[face[3]][1])/2, (verts[face[2]][2]+verts[face[3]][2])/2])
        list_vertices.append([(verts[face[1]][0]+verts[face[2]][0])/2, (verts[face[1]][1]+verts[face[2]][1])/2, (verts[face[1]][2]+verts[face[2]][2])/2])
        list_vertices.append(list(center))
        list_vertices.append([(verts[face[0]][0]+verts[face[3]][0])/2, (verts[face[0]][1]+verts[face[3]][1])/2, (verts[face[0]][2]+verts[face[3]][2])/2])
        list_vertices.append(list(center))
        list_faces.append([findex+0, findex+4, findex+7, findex+8])
        list_faces.append([findex+1, findex+6, findex+7, findex+4])
        list_faces.append([findex+6, findex+2, findex+5, findex+7])
        list_faces.append([findex+8, findex+7, findex+5, findex+3])
    if(len(face) == 3):
        list_vertices.append(list(verts[face[0]]))
        list_vertices.append(list(verts[face[1]]))
        list_vertices.append(list(verts[face[2]]))
        list_vertices.append([(verts[face[0]][0]+verts[face[1]][0])/2, (verts[face[0]][1]+verts[face[1]][1])/2, (verts[face[0]][2]+verts[face[1]][2])/2])
        list_vertices.append([(verts[face[2]][0]+verts[face[0]][0])/2, (verts[face[2]][1]+verts[face[0]][1])/2, (verts[face[2]][2]+verts[face[0]][2])/2])
        list_vertices.append([(verts[face[1]][0]+verts[face[2]][0])/2, (verts[face[1]][1]+verts[face[2]][1])/2, (verts[face[1]][2]+verts[face[2]][2])/2])
        list_faces.append([findex+0, findex+3, findex+4])
        list_faces.append([findex+1, findex+3, findex+5])
        list_faces.append([findex+5, findex+4, findex+2])
        list_faces.append([findex+3, findex+5, findex+4])
   
def divideface(obface, verts, number):
    '''Divide the face into the wanted number of faces'''
    global nFaces
    global nVerts
   
    face = tuple(obface.vertices)
    tVerts = []
   
    if(number==1):
        divide_one(nFaces, nVerts, verts, face, len(nVerts))
    elif(number==2):
        divide_two(nFaces, nVerts, verts, face, len(nVerts))
    elif(number==3):
        divide_three(nFaces, nVerts, verts, face, len(nVerts), obface.center)      
    elif(number==4):
        divide_four(nFaces, nVerts, verts, face, len(nVerts), obface.center)
   
############################### Discombobulate ################################
 
def division(obfaces, verts, sf1, sf2, sf3, sf4):
    '''Function to divide each of the selected faces'''
    divide = []
    if(sf1): divide.append(1)
    if(sf2): divide.append(2)
    if(sf3): divide.append(3)
    if(sf4): divide.append(4)
    for face in obfaces:
        if(face.select == True):
            print(1)
            a = random.randint(0, len(divide)-1)
            divideface(face, verts, divide[a])

def protusion(obverts, obfaces, minHeight, maxHeight, minTaper, maxTaper):
    '''function to generate the protusions'''
    verts = []
    for vertex in obverts:
        verts.append(tuple(vertex.co))
           
    for face in obfaces:
        if(face.select == True):
            addProtusionToFace(face, verts, minHeight, maxHeight, minTaper, maxTaper)
 
def test_v2_near_v1(v1, v2):
    if(v1.x - 0.1 <= v2.x <= v1.x + 0.1
        and v1.y - 0.1 <= v2.y <= v1.y + 0.1
        and v1.z - 0.1 <= v2.z <= v1.z + 0.1):
        return True
   
    return False
 
def angle_between_nor(nor_orig, nor_result):
    angle = math.acos(nor_orig.dot(nor_result))
    axis = nor_orig.cross(nor_result).normalized()
   
    q = mathutils.Quaternion()
    q.x = axis.x*math.sin(angle/2)
    q.y = axis.y*math.sin(angle/2)
    q.z = axis.z*math.sin(angle/2)
    q.w = math.cos(angle/2)
   
    return q

############################ Doodad classes #################################

class Doodad():
    """ Parent class of all the other doodad classes, she's never used in the source code,
        just here to indicate relations between different doodads, even if I'm still thinking
        about a possible uniformisation """
    def draw(self, dFaces, dVerts, face, mmSi, mmHei):
        Xsi = randnum(mmSi[0], mmSi[1])
        Ysi = randnum(mmSi[0], mmSi[1])
        hei = randnum(mmHei[0], mmHei[1])
        
        # determine orientation
        orient = int(round(randnum(0.0, 3.0)))
        
        self.singleBox(face.normal, face, Xsi, Ysi, hei, dFaces, dVerts)

class B1Doodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""

    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        vecX*=Xsi
        vecY*=Ysi
        n = normal*hei
        Xsi/=2
        Ysi/=2
        vert0 = tuple(origin_dood+vecX+vecY)
        vert1 = tuple(origin_dood+vecX-vecY)
        vert2 = tuple(origin_dood-vecX-vecY)
        vert3 = tuple(origin_dood-vecX+vecY)
        vert4 = tuple(origin_dood+vecX+vecY+n)
        vert5 = tuple(origin_dood+vecX-vecY+n)
        vert6 = tuple(origin_dood-vecX-vecY+n)
        vert7 = tuple(origin_dood-vecX+vecY+n)
        self.verts = (vert0, vert1, vert2, vert3, vert4, vert5, vert6, vert7)
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))

    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        
class B2Doodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""
        
    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        spacing = randnum(0.0, 0.2)
        vecX*=Xsi
        vecY*=Ysi
        n = normal*hei
        Xsi/=2
        Ysi/=2
        vert0 = tuple(origin_dood+vecX+vecY)
        vert1 = tuple(origin_dood+vecX+vecY*spacing)
        vert2 = tuple(origin_dood-vecX+vecY*spacing)
        vert3 = tuple(origin_dood-vecX+vecY)
        vert4 = tuple(origin_dood+vecX+vecY+n)
        vert5 = tuple(origin_dood+vecX+vecY*spacing+n)
        vert6 = tuple(origin_dood-vecX+vecY*spacing+n)
        vert7 = tuple(origin_dood-vecX+vecY+n)
        
        vert8 = tuple(origin_dood+vecX-vecY*spacing)
        vert9 = tuple(origin_dood+vecX-vecY)
        vert10 = tuple(origin_dood-vecX-vecY)
        vert11 = tuple(origin_dood-vecX-vecY*spacing)
        vert12 = tuple(origin_dood+vecX-vecY*spacing+n)
        vert13 = tuple(origin_dood+vecX-vecY+n)
        vert14 = tuple(origin_dood-vecX-vecY+n)
        vert15 = tuple(origin_dood-vecX-vecY*spacing+n)
        self.verts = (vert0, vert1, vert2, vert3, vert4, vert5, vert6, vert7, vert8, vert9,
            vert10, vert11, vert12, vert13, vert14, vert15)
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7),
                    (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))

    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        
class B3Doodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""
        
    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        vecX*=Xsi
        vecY*=Ysi
        spacing = randnum(0.0, 0.2)
        n = normal*hei
        Xsi/=2
        Ysi/=2
        self.verts = []
        self.verts.append(tuple(origin_dood+vecX+vecY))
        self.verts.append(tuple(origin_dood+vecX+vecY*(1/3+spacing)))
        self.verts.append(tuple(origin_dood-vecX+vecY*(1/3+spacing)))
        self.verts.append(tuple(origin_dood-vecX+vecY))
        self.verts.append(tuple(origin_dood+vecX+vecY+n))
        self.verts.append(tuple(origin_dood+vecX+vecY*(1/3+spacing)+n))
        self.verts.append(tuple(origin_dood-vecX+vecY*(1/3+spacing)+n))
        self.verts.append(tuple(origin_dood-vecX+vecY+n))
        
        self.verts.append(tuple(origin_dood+vecX+vecY*(1/3-spacing)))
        self.verts.append(tuple(origin_dood+vecX-vecY*(1/3-spacing)))
        self.verts.append(tuple(origin_dood-vecX-vecY*(1/3-spacing)))
        self.verts.append(tuple(origin_dood-vecX+vecY*(1/3-spacing)))
        self.verts.append(tuple(origin_dood+vecX+vecY*(1/3-spacing)+n))
        self.verts.append(tuple(origin_dood+vecX-vecY*(1/3-spacing)+n))
        self.verts.append(tuple(origin_dood-vecX-vecY*(1/3-spacing)+n))
        self.verts.append(tuple(origin_dood-vecX+vecY*(1/3-spacing)+n))
        
        self.verts.append(tuple(origin_dood+vecX-vecY*(1/3+spacing)))
        self.verts.append(tuple(origin_dood+vecX-vecY))
        self.verts.append(tuple(origin_dood-vecX-vecY))
        self.verts.append(tuple(origin_dood-vecX-vecY*(1/3+spacing)))
        self.verts.append(tuple(origin_dood+vecX-vecY*(1/3+spacing)+n))
        self.verts.append(tuple(origin_dood+vecX-vecY+n))
        self.verts.append(tuple(origin_dood-vecX-vecY+n))
        self.verts.append(tuple(origin_dood-vecX-vecY*(1/3+spacing)+n))
        
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), 
            (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15),
            (16, 17, 21, 20), (17, 18, 22, 21), (18, 19, 23, 22), (19, 16, 20, 23), (20, 21, 22, 23))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))

    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        
class TDoodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""
        
    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        vecX*=Xsi
        vecY*=Ysi
        n = normal*hei
        Xsi/=2
        Ysi/=2
        horiBar = randnum(0.01, 0.99)
        verBar = randnum(0.01, 0.99)
        vert0 = tuple(origin_dood+vecX+vecY)
        vert1 = tuple(origin_dood+vecX+vecY*(1-verBar))
        vert2 = tuple(origin_dood-vecX+vecY*(1-verBar))
        vert3 = tuple(origin_dood-vecX+vecY)
        vert4 = tuple(origin_dood+vecX+vecY+n)
        vert5 = tuple(origin_dood+vecX+vecY*(1-verBar)+n)
        vert6 = tuple(origin_dood-vecX+vecY*(1-verBar)+n)
        vert7 = tuple(origin_dood-vecX+vecY+n)
        
        vert8 = tuple(origin_dood+vecX*horiBar+vecY*(1-verBar))
        vert9 = tuple(origin_dood+vecX*horiBar-vecY)
        vert10 = tuple(origin_dood-vecX*horiBar-vecY)
        vert11 = tuple(origin_dood-vecX*horiBar+vecY*(1-verBar))
        vert12 = tuple(origin_dood+vecX*horiBar+vecY*(1-verBar)+n)
        vert13 = tuple(origin_dood+vecX*horiBar-vecY+n)
        vert14 = tuple(origin_dood-vecX*horiBar-vecY+n)
        vert15 = tuple(origin_dood-vecX*horiBar+vecY*(1-verBar)+n)
        self.verts = (vert0, vert1, vert2, vert3, vert4, vert5, vert6, vert7, vert8, vert9,
            vert10, vert11, vert12, vert13, vert14, vert15)
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7),
                    (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))

    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        
class LDoodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""
        
    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        vecX*=Xsi
        vecY*=Ysi
        n = normal*hei
        Xsi/=2
        Ysi/=2
        print("a")
        horiBar = randnum(0.01, 0.99)
        verBar = randnum(0.01, 0.99)
        vert0 = tuple(origin_dood+vecX*verBar+vecY)
        vert1 = tuple(origin_dood+vecX*verBar+vecY*horiBar)
        vert2 = tuple(origin_dood-vecX*verBar+vecY*horiBar)
        vert3 = tuple(origin_dood-vecX*verBar+vecY)
        vert4 = tuple(origin_dood+vecX*verBar+vecY+n)
        vert5 = tuple(origin_dood+vecX*verBar+vecY*horiBar+n)
        vert6 = tuple(origin_dood-vecX*verBar+vecY*horiBar+n)
        vert7 = tuple(origin_dood-vecX*verBar+vecY+n)
        
        vert8 = tuple(origin_dood+vecX+vecY)
        vert9 = tuple(origin_dood+vecX-vecY)
        vert10 = tuple(origin_dood+vecX*verBar-vecY)
        vert11 = tuple(origin_dood+vecX*verBar+vecY)
        vert12 = tuple(origin_dood+vecX+vecY+n)
        vert13 = tuple(origin_dood+vecX-vecY+n)
        vert14 = tuple(origin_dood+vecX*verBar-vecY+n)
        vert15 = tuple(origin_dood+vecX*verBar+vecY+n)
        self.verts = (vert0, vert1, vert2, vert3, vert4, vert5, vert6, vert7, vert8, vert9,
            vert10, vert11, vert12, vert13, vert14, vert15)
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7),
                    (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))

    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        
class SDoodad(Doodad):
    """ class to define a doodad composed of a single box.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed"""
        
    def singleBox(self, normal, face_base, Xsi, Ysi, hei, dFaces, dVerts):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        vecX        = (mathutils.Vector(Verts[face_base.vertices[0]]) - mathutils.Vector(Verts[face_base.vertices[1]])).normalized()
        vecY        = (mathutils.Vector(Verts[face_base.vertices[1]]) - mathutils.Vector(Verts[face_base.vertices[2]])).normalized()
        vecX*=Xsi
        vecY*=Ysi
        n = normal*hei
        Xsi/=2
        Ysi/=2
        
        centerW = randnum(0.01, 0.99)
             
        vert0 = tuple(origin_dood+vecX+vecY)
        vert1 = tuple(origin_dood+vecX-vecY*(centerW/2))
        vert2 = tuple(origin_dood-vecY*(centerW/2))
        vert3 = tuple(origin_dood+vecY)
        vert4 = tuple(origin_dood+vecX+vecY+n)
        vert5 = tuple(origin_dood+vecX-vecY*(centerW/2)+n)
        vert6 = tuple(origin_dood-vecY*(centerW/2)+n)
        vert7 = tuple(origin_dood+vecY+n)
        
        vert8 = tuple(origin_dood+vecY*(centerW/2))
        vert9 = tuple(origin_dood-vecY)
        vert10 = tuple(origin_dood-vecX-vecY)
        vert11 = tuple(origin_dood-vecX+vecY*(centerW/2))
        vert12 = tuple(origin_dood+vecY*(centerW/2)+n)
        vert13 = tuple(origin_dood-vecY+n)
        vert14 = tuple(origin_dood-vecX-vecY+n)
        vert15 = tuple(origin_dood-vecX+vecY*(centerW/2)+n)
        self.verts = (vert0, vert1, vert2, vert3, vert4, vert5, vert6, vert7, vert8, vert9,
            vert10, vert11, vert12, vert13, vert14, vert15)
        self.faces = ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7),
                    (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15), (12, 13, 14, 15))
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))
        
    def __init__(self):
        # initialize attribute of the mesh
        self.name       = "B1"
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))

class CustomDoodad(Doodad):
    """ class to define a doodad from a specified object.
    Its attributes are:
        - name(String)      : the name of the doodad
        - nor_def(Vector)   : the normal from which rotational difference will be computed
        - faces(tuple)      : the faces of the doodad
        - verts(tuple)      : the vertices of the doodad
        - object(Object)    : the object in case it is edited after having been selected"""

    def update():
        # First we have to apply scaling and rotation to the mesh
        bpy.ops.object.select_name(name=object.name)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        # Than we reinitialize faces and vertices tuples
        self.faces = []
        for facei in object.data.faces:
            self.faces.append(tuple(face.vertices))
        self.verts = []
        for verti in object.data.vertices:
            self.verts.append(vertex.co.copy())
    
    def draw(self, dFaces, dVerts, nor_face, face_i):
        if(len(face_base.vertices) == 4):
            origin_dood = mathutils.Vector(randVertexOnQuad(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], face_base.vertices[3], Verts))
        elif(len(face_base.vertices) == 3):
            origin_dood = mathutils.Vector(randVertexOnTri(face_base.vertices[0], face_base.vertices[1], face_base.vertices[2], Verts))
    
        qr = self.nor_def.rotation_difference(nor_face.normalized())

        case_z = False
        if(test_v2_near_v1(self.nor_def, -nor_face)):
            case_z = True
            qr = mathutils.Quaternion((0.0, 0.0, 0.0, 0.0))
        #qr = angle_between_nor(nor_def, normal_original_face)
        for vertex in self.verts:
            vertex.rotate(qr)
            vertex+=origin_dood
        findex = len(dVerts)
        for face in self.faces:
            dFaces.append([face[0]+findex, face[1]+findex, face[2]+findex, face[3]+findex])
            i_dood_type.append(self.name)
        for vertex in self.verts:
            dVerts.append(tuple(vertex))
    
    def __init__(self, object, dminScale, dmaxScale, iface):
        # First we have to apply scaling and rotation to the mesh
        bpy.ops.object.select_name(name=object.name)
        to_scale = randnum(bpy.context.window_manager.discombobulator.custMinScale, bpy.context.window_manager.discombobulator.custMaxScale)
        bpy.ops.transform.resize(value=(to_scale, to_scale, to_scale))
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        # initialize attribute of the mesh
        self.name       = object.name
        self.nor_def    = mathutils.Vector((0.0, 0.0, 1.0))
        self.faces = []
        for face in object.data.faces:
            self.faces.append(tuple(face.vertices))
        self.verts = []
        for vertex in object.data.vertices:
            self.verts.append(vertex.co.copy())
        bpy.ops.transform.resize(value=(1/to_scale, 1/to_scale, 1/to_scale))



def doodads(object1, mesh1, dmin, dmax, dminScale, dmaxScale, dminHei, dmaxHei):
    '''function to generate the doodads'''
    global dVerts
    global dFaces
    i = 0
    # on parcoure cette boucle pour ajouter des doodads a toutes les faces
    #while(i<len(object1.data.faces)):
    for i in i_prots:
        doods_nbr = random.randint(dmin, dmax)
        j = 0
        while(j<=doods_nbr):
            defDood = bpy.types.Scene.DISC_doodads[:]
            if(bpy.context.window_manager.discombobulator.B1dood == True):
                defDood.append("B1")
            if(bpy.context.window_manager.discombobulator.B2dood == True):
                defDood.append("B2")
            if(bpy.context.window_manager.discombobulator.B3dood == True):
                defDood.append("B3")
            if(bpy.context.window_manager.discombobulator.Ldood == True):
                defDood.append("L")
            if(bpy.context.window_manager.discombobulator.Sdood == True):
                defDood.append("S")
            if(bpy.context.window_manager.discombobulator.Tdood == True):
                defDood.append("T")
            if(len(defDood)!=0):
                type_dood = random.randint(0, len(defDood)-1)
                faces_add = []
                verts_add = []
                if(type_dood <= len(bpy.types.Scene.DISC_doodads)-1):
                    dood = CustomDoodad(bpy.data.objects[bpy.types.Scene.DISC_doodads[type_dood]], dminScale, dmaxScale, object1.data.faces[i])
                    dood.draw(dFaces, dVerts, object1.data.faces[i].normal, object1.data.faces[i])
                elif defDood[type_dood] == "B1":
                    dood = B1Doodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
                elif defDood[type_dood] == "B2":
                    dood = B2Doodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
                elif defDood[type_dood] == "B3":
                    dood = B3Doodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
                elif defDood[type_dood] == "L":
                    dood = LDoodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
                elif defDood[type_dood] == "S":
                    dood = SDoodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
                elif defDood[type_dood] == "T":
                    dood = TDoodad()
                    dood.draw(dFaces, dVerts, object1.data.faces[i], (dminScale, dmaxScale), (dminHei, dmaxHei))
            j+=1
       
def protusions_repeat(object1, mesh1, r_prot):
    i = 2
    while(i<=r_prot):
        # Here we select the top faces stored in i_prots
        bpy.ops.object.select_name(name = object1.name)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.wm.context_set_value(data_path="tool_settings.mesh_select_mode", value="(False, False, True)")
        for j in i_prots:
            object1.data.faces[j].select = True
        bpy.ops.object.mode_set(mode='OBJECT')
        i+=1
 
def setMatProt(discObj, origObj, sideProtMat, topProtMat):
    ''' Functions which sets the materials of the protusions 
        Its attributes are:
            - discObj(Object)       : discombobulated object
            - origObj(Object)       : original object
            - sideProtMat(string)   : material of the sides of the protusions
            - topProtMat(string)    : material of the tops of the protusions
    '''
    # First we put the materials in their slots
    myobject = bpy.data.objects[discObj.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True
    try:
        origObj.material_slots[topProtMat]
        origObj.material_slots[sideProtMat]
    except:
        return
    bpy.ops.object.material_slot_add()
    bpy.ops.object.material_slot_add()
    discObj.material_slots[0].material = origObj.material_slots[topProtMat].material
    discObj.material_slots[1].material = origObj.material_slots[sideProtMat].material
   
    # Then we assign materials to protusions
    for face in discObj.data.faces:
        if face.index in i_prots:
            face.material_index = 0
        else:
            face.material_index = 1
 
def setMatDood(doodObj):
    ''' Function which sets the materials of the doodads
        Its attributes are:
            - doodObj(Object): object with the doodads
    '''
    # First we add the materials slots
    myobject = bpy.data.objects[doodObj.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True
    for name in bpy.types.Scene.DISC_doodads:
        try:
            bpy.ops.object.material_slot_add()
            doodObj.material_slots[-1].material = bpy.data.objects[name].material_slots[0].material
            for face in doodObj.data.faces:
                if i_dood_type[face.index] == name:
                    face.material_index = len(doodObj.material_slots)-1
        except:
            print()

def discombobulate(minHeight, maxHeight, minTaper, maxTaper, sf1, sf2, sf3, sf4, dmin, dmax, 
    r_prot, sideProtMat, topProtMat, dminScale, dmaxScale, dminHei, dmaxHei):
    global doprots
    global nVerts
    global nFaces
    global Verts
    global Faces
    global dVerts
    global dFaces
    global i_prots
        
    bpy.ops.object.mode_set(mode = 'OBJECT')
    # Create the discombobulated mesh
    mesh = bpy.data.meshes.new("tmp")
    object = bpy.data.objects.new("tmp", mesh)
    bpy.context.scene.objects.link(object)
   
    # init final verts and faces tuple
    nFaces = []
    nVerts = []
    Faces = []
    Verts = []
    dFaces = []
    dVerts = []
    i_prots = []
   
    origObj = bpy.context.active_object
   
    # There we collect the rotation, translation and scaling datas from the original mesh
    to_translate = bpy.context.active_object.location
    to_scale     = bpy.context.active_object.scale
    to_rotate    = bpy.context.active_object.rotation_euler

    #####################################################################################
    ############################     Division of the mesh    ############################
    #####################################################################################
       
    # First, we collect all the informations we will need from the previous mesh        
    obverts = bpy.context.active_object.data.vertices
    obfaces = bpy.context.active_object.data.faces
    verts = []
    for vertex in obverts:
        verts.append(tuple(vertex.co))

    # Then, we divide the mesh
    division(obfaces, verts, sf1, sf2, sf3, sf4)
       
    # Fill in the discombobulated mesh with the new faces
    mesh.from_pydata(nVerts, [], nFaces)
    mesh.update(calc_edges = True)
    
    myobject = bpy.data.objects[object.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    #####################################################################################
    ##########################  Generation of the protusions  ###########################
    #####################################################################################
      
    # Reload the datas
    bpy.ops.object.select_all(action="DESELECT")
    myobject = bpy.data.objects[object.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True
    obverts = bpy.context.active_object.data.vertices
    obfaces = bpy.context.active_object.data.faces

    protusion(obverts, obfaces, minHeight, maxHeight, minTaper, maxTaper) # We generate the protusions
   
    # Fill in the discombobulated mesh with the new faces
    mesh1 = bpy.data.meshes.new("discombobulated_object")
    object1 = bpy.data.objects.new("discombobulated_mesh", mesh1)
    bpy.context.scene.objects.link(object1)
    mesh1.from_pydata(Verts, [], Faces)
    mesh1.update(calc_edges = True)
    
    # Set the material's of discombobulated object
    setMatProt(object1, origObj, sideProtMat, topProtMat)
    myobject = bpy.data.objects[object1.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True   
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
   
    if(bpy.context.window_manager.discombobulator.repeatprot):
        protusions_repeat(object1, mesh1, r_prot>1)
    
    #####################################################################################
    ########################      Generation of the doodads      ########################
    #####################################################################################
    
    doodads(object1, mesh1, dmin, dmax, dminScale, dmaxScale, dminHei, dmaxHei)
    mesh2 = bpy.data.meshes.new("dood_mesh")
    object2 = bpy.data.objects.new("dood_obj", mesh2)
    bpy.context.scene.objects.link(object2)
    mesh2.from_pydata(dVerts, [], dFaces)
    mesh2.update(calc_edges = True)
    setMatDood(object2)
    object2.location        = to_translate
    object2.rotation_euler  = to_rotate
    object2.scale           = to_scale
    myobject = bpy.data.objects[object.name]
    bpy.context.scene.objects.active = myobject
    myobject.select = True
    bpy.ops.object.delete()
   
    # translate, scale and rotate discombobulated results
    object1.location        = to_translate
    object1.rotation_euler  = to_rotate
    object1.scale           = to_scale
    
    if(not bpy.context.window_manager.discombobulator.makeDoodSingleMesh):
        if(not bpy.context.window_manager.discombobulator.makeProtSingleMesh):
            bpy.ops.object.select_all(action='DESELECT')
            myobject = bpy.data.objects[object2.name]
            bpy.context.scene.objects.active = myobject
            myobject.select = True
            myobject = bpy.data.objects(object1.name, extend=True)
            bpy.context.scene.objects.active = myobject
            myobject.select = True
            bpy.ops.object.select_name(name = object1.name, extend=True)
            bpy.ops.object.join()
        else:
            bpy.ops.object.select_all(action='DESELECT')
            myobject = bpy.data.objects[object2.name]
            bpy.context.scene.objects.active = myobject
            myobject.select = True
            myobject = bpy.data.objects(origObj.name, extend=True)
            bpy.context.scene.objects.active = myobject
            myobject.select = True
#            bpy.ops.object.select_name(name = object1.name, extend=True)
            bpy.ops.object.join()
			
 #           bpy.ops.object.select_all(action='DESELECT')
 #           bpy.ops.object.select_name(name = object2.name)
  #          bpy.ops.object.select_name(name = origObj.name, extend=True)
  #          bpy.ops.object.join()
    
    if(not bpy.context.window_manager.discombobulator.makeProtSingleMesh):
        bpy.ops.object.select_all(action='DESELECT')
        myobject = bpy.data.objects[object1.name]
        bpy.context.scene.objects.active = myobject
        myobject.select = True
        myobject = bpy.data.objects(origObj.name, extend=True)
        bpy.context.scene.objects.active = myobject
        myobject.select = True
		
 #       bpy.ops.object.select_all(action='DESELECT')
 #       bpy.ops.object.select_name(name = object1.name)
 #       bpy.ops.object.select_name(name = origObj.name, extend=True)
 #       bpy.ops.object.join()

############ Operator to select and deslect an object as a doodad ###############
 
class chooseDoodad(bpy.types.Operator):
    bl_idname = "object.discombobulate_set_doodad"
    bl_label = "Discombobulate set doodad object"

    def execute(self, context):
        bpy.context.scene.DISC_doodads.append(bpy.context.active_object.name)

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}
 
class unchooseDoodad(bpy.types.Operator):
    bl_idname = "object.discombobulate_unset_doodad"
    bl_label = "Discombobulate unset doodad object"
   
    def execute(self, context):
        for name in bpy.context.scene.DISC_doodads:
            if name == bpy.context.active_object.name:
                bpy.context.scene.DISC_doodads.remove(name)
               
    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}
 
################################## Interface ####################################
 
class discombobulator(bpy.types.Operator):
    bl_idname = "object.discombobulate"
    bl_label = "Discombobulate"
    bl_options = {'REGISTER', 'UNDO'}    
  
    def execute(self, context):
        dp = context.window_manager.discombobulator
        discombobulate(dp.minHeight, dp.maxHeight, dp.minTaper, dp.maxTaper, dp.subface1, 
        dp.subface2, dp.subface3, dp.subface4, dp.mindoodads, dp.maxdoodads, dp.repeatprot, 
        dp.sideProtMat, dp.topProtMat, dp.doodMinScale, dp.doodMaxScale, dp.doodMinHei, dp.doodMaxHei)
        return {'FINISHED'}

class VIEW3D_PT_tools_discombobulate(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
 
    bl_label = "Discombobulator"
    bl_context = "objectmode"
    @classmethod
    def poll(cls, context):
        return context.active_object 
    def draw(self, context):
        layout = self.layout
        discP = context.window_manager.discombobulator
        
        row = layout.row()
        row.operator("object.discombobulate", text = "Discombobulate")
        row = layout.row()
        row.prop(discP, "makeDoodSingleMesh")
        row = layout.row()
        row.prop(discP, "makeProtSingleMesh")
        box = layout.box()
        box.label("Protusions settings")
        col = box.column()
        col.prop(discP, 'doprots')
        col.prop(discP, 'minHeight')
        col.prop(discP, 'maxHeight')
        col.prop(discP, 'minTaper')
        col.prop(discP, 'maxTaper')
        row = box.row()
        col1 = row.column(align = True)
        col1.prop(discP, "subface1")
        col2 = row.column(align = True)
        col2.prop(discP, "subface2")
        col3 = row.column(align = True)
        col3.prop(discP, "subface3")
        col4 = row.column(align = True)
        col4.prop(discP, "subface4")
        row = box.row()
        row.prop(discP, "repeatprot")
        box = layout.box()
        box.label("Doodads settings")
        row = box.row()
        row.prop(discP, 'dodoodads')
        row = box.row()
        row.prop(discP, "mindoodads")
        row = box.row()
        row.prop(discP, "maxdoodads")
        col = box.column(align = True)
        split = col.split(percentage=0.15)
        if(discP.displayCustomDood):
            split.prop(discP, "displayCustomDood", text="", icon="DOWNARROW_HLT")
            split.label("Custom doodads")
            col.operator("object.discombobulate_set_doodad", text = "Pick doodad")
            col.operator("object.discombobulate_unset_doodad", text = "Remove doodad")
            col.prop(discP, "custMinScale")
            col.prop(discP, "custMaxScale")
            for name in bpy.context.scene.DISC_doodads:
                col.label(text = name)
        else:
            split.prop(discP, "displayCustomDood", text="", icon="RIGHTARROW")
            split.label("Custom doodads")
        col = box.column(align = True)
        split = col.split(percentage=0.15)
        if(discP.displayDefDood):
            split.prop(discP, "displayDefDood", text="", icon="DOWNARROW_HLT")
            split.label("Custom doodads")
            """col.prop(discP, "Tdood")"""
            col.prop(discP, "Ldood")
            col.prop(discP, "Sdood")
            col.prop(discP, "Tdood")
            col.prop(discP, "B1dood")
            col.prop(discP, "B2dood")
            col.prop(discP, "B3dood")
            col.prop(discP, "doodMinScale")
            col.prop(discP, "doodMaxScale")
            col.prop(discP, "doodMinHei")
            col.prop(discP, "doodMaxHei")
        else:
            split.prop(discP, "displayDefDood", text="", icon="RIGHTARROW")
            split.label("Default doodads")
        box = layout.box()
        box.label("Materials settings")
        row = box.row()
        row.prop(discP, 'topProtMat')
        row = box.row()
        row.prop(discP, "sideProtMat")
        row = box.row()

class DiscombobulatorProps(bpy.types.PropertyGroup):
    """ Fake module like class
    bpy.context.window_manager.discombobulator
    """

    # General properties:
    makeDoodSingleMesh = bpy.props.BoolProperty(name="Doodads single mesh", description="Make doodads as a single mesh", default=False)
    makeProtSingleMesh = bpy.props.BoolProperty(name="Protusions single mesh", description="Make protusions as a single mesh", default=False)
    
    # Protusions properties:
    repeatprot = bpy.props.IntProperty(name="Repeat protusions",
        description="make several layers of protusion", default = 1, min = 1, max = 10)
    doprots = bpy.props.BoolProperty(name="Make protusions",
        description = "Check if we want to add protusions to the mesh", default = True)
    faceschangedpercent = bpy.props.FloatProperty(name="Face %", 
        description = "Percentage of changed faces", default = 1.0)
    minHeight = bpy.props.FloatProperty(name="Min height", 
        description="Minimal height of the protusions", default=0.2)
    maxHeight = bpy.props.FloatProperty(name="Max height",
        description="Maximal height of the protusions", default = 0.4)
    minTaper = bpy.props.FloatProperty(name="Min taper",
        description="Minimal height of the protusions", default=0.15, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    maxTaper = bpy.props.FloatProperty(name="Max taper", 
        description="Maximal height of the protusions", default = 0.35, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    subface1 = bpy.props.BoolProperty(name="1", default = True)
    subface2 = bpy.props.BoolProperty(name="2", default = True)
    subface3 = bpy.props.BoolProperty(name="3", default = True)
    subface4 = bpy.props.BoolProperty(name="4", default = True)
   
    # Doodads properties:
    dodoodads = bpy.props.BoolProperty(name="Make doodads", 
        description = "Check if we want to generate doodads", default = True)
    mindoodads = bpy.props.IntProperty(name="Minimum doodads number", 
        description = "Ask for the minimum number of doodads to generate per face", default = 1, min = 0, max = 50)
    maxdoodads = bpy.props.IntProperty(name="Maximum doodads number", 
        description = "Ask for the maximum number of doodads to generate per face", default = 6, min = 1, max = 50)
    displayCustomDood = bpy.props.BoolProperty(name = "Custom doodads",
        description = "Display settings of the custom doodads",
        default = False)
    custMinScale = bpy.props.FloatProperty(name="Scale min", 
        description="Minimum scaling of doodad", default = 0.5, min = 0.0, max = 1.0)
    custMaxScale = bpy.props.FloatProperty(name="Scale max", 
        description="Maximum scaling of doodad", default = 1.0, min = 0.0, max = 1.0)
    # Default doodads
    displayDefDood = bpy.props.BoolProperty(name = "Default doodads",
        description = "Display settings of the default doodads",
        default = True)
    B1dood = bpy.props.BoolProperty(name = "1 Box doodad",
        description = "Enable the use of the 1box-shaped doodads",
        default = True)
    B2dood = bpy.props.BoolProperty(name = "2 Boxes doodad",
        description = "Enable the use of the 2box-shaped doodads",
        default = True)
    B3dood = bpy.props.BoolProperty(name = "3 Boxes doodad",
        description = "Enable the use of the 3box-shaped doodads",
        default = True)
    Tdood = bpy.props.BoolProperty(name = "T doodad",
        description = "Enable the use of the T-shaped doodads",
        default = True)
    Ldood = bpy.props.BoolProperty(name = "L doodad",
        description = "Enable the use of the L-shaped doodads",
        default = True)
    Sdood = bpy.props.BoolProperty(name = "S doodad",
        description = "Enable the use of the S-shaped doodads",
        default = True)
    doodMinScale = bpy.props.FloatProperty(name="Scale min", 
        description="Minimum scaling of doodad", default = 0.1, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    doodMaxScale = bpy.props.FloatProperty(name="Scale max", 
        description="Maximum scaling of doodad", default = 0.2, min = 0.0, max = 1.0, subtype = 'PERCENTAGE')
    doodMinHei = bpy.props.FloatProperty(name="Height min",
        description="Minimum height of the doodad", default = 0.1, min = 0.0)
    doodMaxHei = bpy.props.FloatProperty(name="Height max",
        description="Maximum height of the doodad", default = 0.2, min = 0.0)
   
    # Materials properties:
    sideProtMat = bpy.props.IntProperty(name="Side's prot mat", 
        description = "Material of protusion's sides", default = 0, min = 0)
    topProtMat = bpy.props.IntProperty(name = "Prot's top mat", 
        description = "Material of protusion's top", default = 0, min = 0)

# define classes for registration
classes = [discombobulator,
            chooseDoodad,
            unchooseDoodad,
            VIEW3D_PT_tools_discombobulate,
            DiscombobulatorProps]

# registering and menu integration
def register():   
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.discombobulator = bpy.props.PointerProperty(\
        type = DiscombobulatorProps)
 
# unregistering and removing menus
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    try:
        del bpy.types.WindowManager.discombobulator
    except:
        pass
 
if __name__ == "__main__":
    register()