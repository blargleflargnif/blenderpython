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

__author__ = ["Matt Cragun "]
__version__ = '0.3'
__bpydoc__ = """\
This script imports .msh file format into Blender

Usage:<br>
    Execute this script from the "File->Import" menu and choose a Raw file to
open.

Notes:<br>\
  Heavily based on importRaw script by Anthony D'Agostino (Scorpius) and Aurel Wildfellner
  Only works on ASCII .msh files currently
  This is version 0.3: This time surface sets are imported as vertex groups.  So, one .msh file = 1 mesh object, but surface sets should show up as vertex groups
"""


#Python to read mesh file into blender
import re
import bpy
from import_scene_obj import unpack_face_list, unpack_list

def readMesh(meshFilePath, objName):
    #----------------------------------------
    #Declare Variables, etc.
    #----------------------------------------
    nodeHdr = re.compile('\(10 \(.*\).*\(')   #Regular expressions to find the important stuff
    faceHdr = re.compile('\(13 \(.*\).*\(')
    nameHdr = re.compile('\(45 \(.*\)\)')
    tailHdr = re.compile('\)\)')
    
    FACESETS = []
    RAW_NODES = []
    RAW_FACES = []
    FACESETS = []
    RAW_NAMES = []

    #----------------------------------------
    #Open the mesh file
    #----------------------------------------
    print("Importing %s" % meshFilePath)
    file = open(meshFilePath,'r')
    meshData = file.read()
    file.close()
    #--------------------------------------
    #read in the nodes
    #--------------------------------------
    for thisNodeSet in nodeHdr.finditer(meshData):
        RAW_NODES = []
        nodeData = meshData[thisNodeSet.end()+1:]
        nodeData = nodeData[:tailHdr.search(nodeData).start()-1]
        #print(nodeData)
        for eachNode in nodeData.splitlines():
            node = [float(x) for x in eachNode.split()]
            #print (node)
            RAW_NODES.append(node)

    #----------------------------------------
    #read in the faces
    #----------------------------------------
        #this section needs some work--need to figure out how to import surface sets
    for thisFaceSet in faceHdr.finditer(meshData):
        FACES = []
        faceData = meshData[thisFaceSet.end()+1:]
        faceData = faceData[:tailHdr.search(faceData).start()-1]
        for eachFace in faceData.splitlines():
            f = eachFace.split()
            face = [int(f[0],16)-1,int(f[1],16)-1,int(f[2],16)-1]
            RAW_FACES.append(face)
            FACES.append(face)
        FACESETS.append(FACES)
    #print (FACESETS[0])

    #----------------------------------------
    #read in mesh names
    #----------------------------------------
    for thisName in nameHdr.finditer(meshData):
        RAW_NAMES.append(thisName.group().split()[3].strip('()'))
    
    #----------------------------------------
    #Create Blender Objects
    #----------------------------------------
    mesh = bpy.data.meshes.new(objName)
    print ("ADDING POINTS TO MESH")
    mesh.add_geometry(int(len(RAW_NODES)), 0, int(len(RAW_FACES)))
    mesh.verts.foreach_set("co", unpack_list(RAW_NODES))
    print ("ADDING FACES TO MESH")
    mesh.faces.foreach_set("verts", unpack_face_list(RAW_FACES))
    
           
    print ("done")
    return mesh, FACESETS, RAW_NAMES
    

def addMeshObj(mesh, objName):
    scn = bpy.context.scene

    for o in scn.objects:
        o.select = False

    mesh.update()
    nobj = bpy.data.objects.new(objName, mesh)
    scn.objects.link(nobj)
    nobj.select = True
    
  
    if scn.objects.active == None or scn.objects.active.mode == 'OBJECT':
        scn.objects.active = nobj
    
    return nobj

def CreateVertexGroup(object, vertIDs, name):
    group = object.add_vertex_group(name)
    print ("...%s"%name)
    for IDs in vertIDs:
        for i in IDs:
            object.add_vertex_to_group(i, group, 1.0,'REPLACE')
    return group
        
from bpy.props import *

class MSHImporter(bpy.types.Operator):
    '''Load FLuent Mesh Data'''
    bl_idname = "import_mesh.msh"
    bl_label = "Import MSH"

    filepath = StringProperty(name="File Path", description="Filepath used for importing the MSH file", maxlen=1024, default="")

    def execute(self, context):

        #convert the filename to an object name
        objName = bpy.utils.display_name(self.properties.filepath.split("\\")[-1].split("/")[-1])

        mesh, surfaceSets, names = readMesh(self.properties.filepath, objName)
        
        print ("CREATING BLENDER OBJECTS")
        obj = addMeshObj(mesh, objName)
        
        print ("GROUPING SURFACE SETS")
        VGroups = {} #A dictionary of all of the vertex groups
        for i in range(len(names)):
            VGroups[names[i]] = CreateVertexGroup(obj, surfaceSets[i], names[i])
        
        
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.manager
        wm.add_fileselect(self)
        return {'RUNNING_MODAL'}

