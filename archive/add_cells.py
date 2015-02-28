# Id: Cells.py, v1.3 - 03.07.2007  add_cells.py 15.04.2011 v1.3.0
#
# -------------------------------------------------------------------------- 
# Cells v1.3.2 (C) Michael Schardt and PKHG 17-4-2011
# -------------------------------------------------------------------------- 
#
#
# ***** BEGIN GPL LICENSE BLOCK ***** 
# 
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program; if not, write to the Free Software Foundation, 
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. 
# 
# ***** END GPL LICENCE BLOCK ***** 
#
# -------------------------------------------------------------------------- 


bl_info = {
    'name': 'Cells',
    'author': ' Michael Schardt &modified by  PKHG',
    'version': (1,3,2),
    "blender": (2, 5, 7),
    "api": 36159,
    'location': 'UI (type N)  => make cells',
    'description': 'Adds  CELLS',
    'warning': 'This version only for Windows!', # used for warning icon and text in addons panel
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Add Mesh'}


__bpydoc__ = """\
Because of myPrompt, it runs only under Windows!
Select 2 objects: the mesh object to be voxelized and a (small) object used as cell.\n\
The menu is only visible, if two meshes are selected\n\
Order of selection is important, see the info in the menu!\n\
Caution: Script may take some time to execute! Please be patient!\n\
After completion a new object is created, parented to the cell-object and selected.\n\
'DupliVerts' is automatically activated for the new object.\n\
\n\
Known issues:\n\
    Mesh object to be voxelized must be triangulated.\n\
    For solid voxel model, mesh object must be closed and manifold (each edge shared by exactly 2 faces).\n\
"""


import bpy
from bpy.props import * #BoolProperty,IntProperty
from math import fabs
from time import time
from mathutils import Matrix,Vector
from  mathutils.geometry import normal as TriangleNormal 



#for (error) messages
from ctypes import *
user32 = windll.user32
def myPrompt(message,type="ErrorMessage"):
    Answer = user32.MessageBoxW(None, message, type, 1)
    return Answer # OK = 1 Cancel = 2

#####################################################################

def InsideZProjection(point, faces,mesh):

    # calculate boundary:    
    boundary_edges = set()
    for face in faces:
        for edge in ((face.vertices[0], face.vertices[1]),
                         (face.vertices[1], face.vertices[2]),
                         (face.vertices[2], face.vertices[0])):
            if (edge[0], edge[1]) in boundary_edges:
                boundary_edges.remove((edge[0], edge[1]))
            elif (edge[1], edge[0]) in boundary_edges:
                boundary_edges.remove((edge[1], edge[0]))
            else:
                boundary_edges.add(edge)

    # point in 2D-polygon test:
    
    inside = False
    
    for edge in boundary_edges:
        p0 = mesh.vertices[edge[0]].co
        p1 = mesh.vertices[edge[1]].co
                
        if (p0[1] <= point[1] < p1[1]):
            if TriangleNormal(point, p0, p1)[2] < 0.0:
                inside = not inside
            continue
            
        if (p1[1] <= point[1] < p0[1]):
            if TriangleNormal(point, p0, p1)[2] > 0.0:
                inside = not inside
            continue
            
    return inside
    
#####################################################################

def Cells(object, cell, solid = False):
    print("L130 ===Cells called=== object is =",object.name," cell is", cell.name)    
    t0 = time()
    
    es = [Vector((1.0, 0.0, 0.0)),
            Vector((0.0, 1.0, 0.0)),
            Vector((0.0, 0.0, 1.0))]

    # transform object/mesh (to get cell-alignment right)
    ######################################################
    
    cm  = cell.matrix_local.copy()
    cmi = cm.inverted() # is different matrix!

    om = object.matrix_local.copy()
    omi = om.inverted()
    
    tm  = om * cmi
    tmi = cm * omi
    
    mesh = object.data
        
    # transform mesh to align with cell
    mesh.transform(tm)
    
    # calculate cell dimensions
    ########################### boundingbox is a box with (0 1 2 3)(4 5 6 7)
    # 0 and 6 are diagonal 1 7, 2 4, 3 5 too 
        
    cell_gbb_min = cell.bound_box[0]
#for debug pkhg    print("L153 cellinfo =",type(cell_gbb_min),cell_gbb_min)
    cell_lbb_min = Vector(cell_gbb_min).to_4d() * cmi
    cell_lbb_max = cell.bound_box[6]
    cell_lbb_max = Vector(cell_lbb_max).to_4d() * cmi


    cell_dimensions = cell_lbb_max - cell_lbb_min
    cell_dimension_x,cell_dimension_y,cell_dimension_z = cell_dimensions[0:3]

    # bin vertices
    ##############
    # everything in object's local coordinates (aligned with cell)
    
    v_cells = {}        
        
    for vert in mesh.vertices:
        coords = vert.co
        v_cells[vert.index] = (int(round(coords[0] / cell_dimension_x)),
                              int(round(coords[1] / cell_dimension_y)),
                              int(round(coords[2] / cell_dimension_z)))
#dbg pkhg        print("L161 v_CELLS",v_cells)
    # bin faces
    ###########
    # everything in object's local coordinates (aligned with cell)
    
    f_cells = {}
        
    for face in mesh.faces:
        
        verts = face.vertices
#dbg pkhg        print("L190 verts",verts[:])
        fidxs = [v_cells[vert][0] for vert in verts] 
#dbg pkhg        print("l192 fidxs ",fidxs,min(fidxs))
        fidxs.sort()          
        min_fidx = fidxs[0]
        max_fidx = fidxs[-1]           
        fidys = [v_cells[vert][1] for vert in verts]
        fidys.sort()
        min_fidy = fidys[0]
        max_fidy = fidys[-1]
        fidzs = [v_cells[vert][2] for vert in verts]
        fidzs.sort()
        min_fidz = fidzs[0]
        max_fidz = fidzs[-1]
                
        # fast path for special cases (especially small faces spanning a single cell only)

        category = 0
        if (max_fidx > min_fidx): 
            category |= 1
        if (max_fidy > min_fidy): 
            category |= 2
        if (max_fidz > min_fidz): 
            category |= 4
        
        if category == 0: # single cell
            f_cells.setdefault((min_fidx, min_fidy, min_fidz), set()).add(face)
            continue
        
        if category == 1: # multiple cells in x-, single cell in y- and z-direction
            for fidx in range(min_fidx, max_fidx + 1):
                f_cells.setdefault((fidx, min_fidy, min_fidz), set()).add(face)
            continue
        
        if category == 2: # multiple cells in y-, single cell in x- and z-direction
            for fidy in range(min_fidy, max_fidy + 1):
                f_cells.setdefault((min_fidx, fidy, min_fidz), set()).add(face)
            continue

        if category == 4: # multiple cells in z-, single cell in x- and y-direction
            for fidz in range(min_fidz, max_fidz + 1):
                f_cells.setdefault((min_fidx, min_fidy, fidz), set()).add(face)
            continue
                        
        # long path (face spans multiple cells in more than one direction)
########### pkhg ???? I think I have not checked this??? possible? ##########
        a0 = face.normal

        r0 =  0.5 * (fabs(a0[0]) * cell_dimension_x +
                         fabs(a0[1]) * cell_dimension_y +
                         fabs(a0[2]) * cell_dimension_z)
                                            
#xrange -> range?!          
        cc = Vector((0.0, 0.0, 0.0))          
        for fidx in range(min_fidx, max_fidx + 1):
            cc[0] = fidx * cell_dimensions[0]
            for fidy in range(min_fidy, max_fidy + 1):
                cc[1] = fidy * cell_dimensions[1]
                for fidz in range(min_fidz, max_fidz + 1):
                    cc[2] = fidz * cell_dimensions[2]
                        
                    if not solid and (fidx, fidy, fidz) in f_cells: 
                        continue 
                        # cell already populated -> no further processing needed for hollow model
                    vertsNew = [mesh.vertices[el] for el in verts] 
#dbg pkhg                    print("L261-----------\n verts vertsNew",verts[:], vertsNew[:])   
                    vs = [vert.co - cc for vert in vertsNew]
                                                            
                    if not (-r0 <= a0 * vs[0] <= r0): continue # cell not intersecting face hyperplane

                    # check overlap of cell with face (separating axis theorem)
                                                
                    fs = [vs[1] - vs[0],
                            vs[2] - vs[1],
                            vs[0] - vs[2]]
                                                
                    overlap = True

                    for f in fs:
                        if not overlap: 
                            break

                        for e in es:
                            if not overlap: 
                                break
                            
#                            a = CrossVecs(e, f)
                            a = e.cross(f)
                            
                            r = 0.5 * (fabs(a[0]) * cell_dimension_x +
                                          fabs(a[1]) * cell_dimension_y +
                                          fabs(a[2]) * cell_dimension_z)                        

                            ds = [a * v for v in vs] 
                            ds.sort()
                                                            
                            if (ds[0] > r or ds[-1] < -r): 
                                overlap = False
                                                    
                    if overlap:
                        f_cells.setdefault((fidx, fidy, fidz), set()).add(face)
    
    # the hollow voxel representation is complete
#dbg pkhg    print("L301 f_cells = ",f_cells)
#dbg    for i,el in enumerate(f_cells.keys()):
#dbg       tmp = [t.index  for t in f_cells[el]]
#dbg       print("L298",tmp)
      
    # fill
    ######

    if solid:
        
        # find min, max cells in x, y, z
##### ERROR f_cell may contain only two elments!???? for open?        
        idxs = [id[0] for id in f_cells]
        min_idx = min(idxs)
        max_idx = max(idxs)
        idys = [id[1] for id in f_cells]
        min_idy = min(idys)
        max_idy = max(idys)
        idzs = [id[2] for id in f_cells]
        min_idz = min(idzs)
        max_idz = max(idzs)

        testpoint = Vector((0.0, 0.0, 0.0))
        
        # for x,y
        
        for idx in range(min_idx, max_idx + 1):
            testpoint[0] = idx * cell_dimension_x   
            for idy in range(min_idy, max_idy + 1):
                testpoint[1] = idy * cell_dimension_y

                odd_parity = False

                tested_faces = set()

                # walk the z pile and keep track of parity
                
                for idz in range(min_idz, max_idz + 1):
                
                    fs = f_cells.get((idx, idy, idz), set()) - tested_faces
                    
                    # cell contains faces                    
                    if fs:
                        # categorize faces in this cell by normal    
                        pfaces = []
                        nfaces = []
                        
                        for f in fs:
                            fnoz = f.normal[2] #was no pkhg
                            if fnoz >= 0.0:
                                pfaces.append(f)
                            if fnoz <= 0.0:
                                nfaces.append(f)                        
                            tested_faces.add(f)
                        
                        # check if testpoint inside z projections
                                                        
                        if pfaces:
#,mesh added in InsideZProjection pkhg
                            if InsideZProjection(testpoint, pfaces,mesh): 
                                odd_parity = not odd_parity
                                
                        if nfaces:
                            if InsideZProjection(testpoint, nfaces,mesh): 
                                odd_parity = not odd_parity

                    # cell contains no faces (empty cell)
                    
                    else:
                        if odd_parity:  
                            f_cells[(idx, idy, idz)] = 1 # odd parity -> empty cell inside object
                                
    # create new object
    ###################
            
    mesh_new = bpy.data.meshes.new("Cells("+object.name+")")
    vertexList = [[(id[0] * cell_dimension_x,id[1] * cell_dimension_y,
       id[2] * cell_dimension_z)] for id in f_cells]
#### debug ??? #####
#    print("L386===============================\n f_cells=",f_cells)
#    print("L369 =========\n vertexList =",vertexList)
#    for el in vertexList:print(el)
#    scene = Scene.GetCurrent()
    scene = bpy.context.scene                
    mesh_new = bpy.data.meshes.new("Cells("+object.name+")")
#####startpkhg added
    edges = []
    faces = []
    verts = []
    for el in vertexList:
        verts.extend(el)
    mesh_new.from_pydata(verts, edges, faces)

    # Update mesh geometry after adding stuff.
    mesh_new.update()
    import add_object_utils
    add_object_utils.object_data_add(bpy.context, mesh_new, operator=None)
    object_new = bpy.context.active_object
#dbg pkhg    print("\n---------L409 object_new",object_new,object_new.name)

########end pkhg added
    object_new.layers = object.layers
    object_new.name = "Cells("+object.name+")"

    # transform objects/meshes back
    ###############################

    object_new.matrix_local = om
    mesh.transform(tmi)
    mesh_new.transform(tmi)

    # parent new object to cell for dupliverts
    ###########################################
    

    cell.location  = object.location

    cell.layers = object_new.layers
    scene.update()   
#???    object.select = True   
#    object_new.select = False
#    cell.select = False
    #??? bpy.ops.object.editmode_toggle()
    #co oc  no 
#    cell.select = True
#    object_new.select = True

#    bpy.ops.object.editmode_toggle()
#    bpy.ops.object.editmode_toggle()

#    bpy.context.scene.objects.active = cell
#    bpy.ops.object.select_all(action='TOGGLE')
#    cell.select = True
#    object_new.select = True
    
    #bpy.ops.object.parent_set(type='OBJECT')
#    object_new.makeParent([cell])
    object_new.dupli_type = "VERTS"
    
    # select
    ########
    
    object.select = False
    cell.select= False
#    object_new.select= True
        
    # done
    ######
    
    t1 = time()
    
    print(str(len(mesh.faces))+" faces ... "+str(len(f_cells))+" cells: "+str(round(t1-t0, 3))+" s")

    bpy.context.scene.update()
    return object_new 

#####################################################################
#####################################################################

def CheckMesh(object):
    
    if object.type != "MESH":
#        Draw.PupMenu("object '"+object.name+"' is not a mesh-object - exit")
        print("======> ERROR: active object not a mesh\n")
        return False
    
    return True

# *******************************************************************

def CheckManifold(object):
    
    mesh = object.data
    result = True
    edgeusers = {}
    
    for face in mesh.faces:
        for edgekey in face.edge_keys:
            edgeusers.setdefault(edgekey, 0)
            edgeusers[edgekey] += 1
    
    for val in edgeusers.values():
        if val != 2: 
#            Draw.PupMenu("object '"+object.name+"' is not manifold - exit")
            print("======> Error: object not a manifold\n")
            myPrompt("object not a manifold,\nany choice stops")
            result = False
            break
    
    return result

# *******************************************************************

def CheckTriangles(object):
    
    mesh = object.data
        
    for face in mesh.faces:
        
        if len(face.vertices) != 3:
#            Draw.PupMenu("object '"+object.name+"' must be triangulated - Ctrl/t in edit mode")
             print("======> ERROR: active object not triangulated\n")
             res = myPrompt("active object not triangulated\nany choice stops")
             return False
    
    return True

#####################################################################
#####################################################################
def getSelected():
   result = []
   for el in bpy.data.objects:
       if el.type == 'MESH' and el.select:
           result.append(el)
   return result

def doIt(context,hollow):
    print("doit called, context = ", context)    
    selection = getSelected() #old: Object.GetSelected()
    
    ok = True
    res1 = 0 #
    if len(selection) != 2:
#        Draw.PupMenu("please select 2 objects: mesh-object to be voxelized and cell object")
        myPrompt("No two meshes selected!\nplease select 2 objects: mesh-object to be voxelized and cell object") 
        ok = False

#    if ok:
#        res1 = Draw.PupMenu("choose object to be voxelized%t|"+selection[0].name+"%x0|"+selection[1].name+"%x1")        

#myPrompt OK gives 1 CANCEL gives 2

#        res1 = -1 +  myPrompt("Voxelize this: " + selection[0].name +" then OK,\nCanceL takes: "+ selection[1].name,"get Info") 
#        print("L533===========\n res1 = ", res1)
    
    if (bpy.context.active_object != selection[0]):
        tmp = selection[0]
        selection[0] = bpy.context.scene.objects.active
        selection[1] = tmp
      
#pkhg next two lines not needed because of getSelected       
#    if ok:
#        ok &= CheckMesh(selection[res1])
        
#    if ok:          
    ok &= CheckTriangles(selection[res1])
        

#???pkhg    if ok:          
#        res2 = Draw.PupMenu("create voxel model%t|hollow (from "+selection[res1].name+" surface)%x0| solid   (from "+selection[res1].name+" volume)%x1")
 
#    res2 = -1 + myPrompt("hollow chose OK\nsolid chose CAnCEL","choice")        
    res2 = 1 # 0 hollow, 1 solid
    if hollow:
        res2 = 0
 
     
    if ok:
        if res2 == 1:
            ok &= CheckManifold(selection[res1])    
    result = []
    if ok:
        if res1 == 0:
            print("\n====== Calculating Cells("+selection[0].name+"):\n")
            obj = Cells(selection[0], selection[1], res2)
            result.append(obj)
            result.append(selection[1])
        if res1 == 1:
            print("\nCalculating Cells("+selection[1].name+"):\n")
            obj= Cells(selection[1], selection[0], res2)
            result.append(obj)
            result.append(selection[0])

        print("\nDone, result = ",result)
    if result:
        bpy.context.scene.update()
        bpy.ops.object.select_all(action='DESELECT')
        result[1].select = True
        result[0].select = True
        bpy.context.scene.objects.active = result[0]

    return result
       
#Classes
def initSceneProperties(scn):
    bpy.types.Scene.MyInt = IntProperty(
        name = "Integer", 
        description = "Enter an integer")
    scn['MyInt'] = 17

    bpy.types.Scene.MyFloat = FloatProperty(
        name = "Float", 
        description = "Enter a float",
        default = 33.33,
        min = -100,
        max = 100)

    bpy.types.Scene.MyBool = BoolProperty(
        name = "Boolean", 
        description = "hollow or solid?", default=True)
    scn['MyBool'] = True
    
    bpy.types.Scene.MyEnum = EnumProperty(
        items = [('Eine', 'Un', 'One'), 
                 ('Zwei', 'Deux', 'Two'),
                 ('Drei', 'Trois', 'Three')],
        name = "Ziffer")
    scn['MyEnum'] = 2
    
    bpy.types.Scene.MyString = StringProperty(
        name = "String")
    scn['MyString'] = "Lorem ipsum dolor sit amet"
    return

initSceneProperties(bpy.context.scene)


class OBJECT_PT_cells_call(bpy.types.Panel):
    bl_label = "run the script"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
#    bl_options = {'DEFAULT_CLOSED'}
    
    

    @classmethod
    def poll(cls, context):
#        view = context.space_data
#        return (view)
        
        result = False
        obj = context.active_object
        if (obj and obj.type == 'MESH'):
            result = len(getSelected()) == 2
        return result   
#        return True


#    def draw_header(self, context):
#        layout = self.layout
#        view = context.space_data
#        layout.prop(view, "run cells script", text="")


    def draw(self,context):
        objects = getSelected()
        sce = context.scene
        view = context.active_object
        layout = self.layout
        box = layout.box()
        box.label("Select two meshes")
        box.operator("mesh.generate_cells")
        box = layout.box()
        box.label("make a choice")
        box.prop(sce,'MyBool',text="hollow")
        box.label(text="choose Voxel object")
        box.label(objects[0].name)
        box.label(objects[1].name)

        box.prop(view,"name", text="good?") 

class MESH_OT_generate_cells(bpy.types.Operator):
    bl_idname = "mesh.generate_cells"
    bl_label = "make cells"
    bl_description = "two meshes used to make cells"
    bl_options = {'REGISTER', 'UNDO'}

    ## Check for curve
    @classmethod
    def poll(cls, context):
        result = False
        obj = context.active_object
        if (obj and obj.type == 'MESH'):
            result = len(getSelected()) == 2
        return result   
#        return True

    def execute(self,context):
        sce = context.scene
        hollow = sce.MyBool
        print("==================context=======",context,"\n============>??????? hollow?",hollow)
        res = doIt(context,hollow)
#        print(dir(context))
#        context.area.type = "VIEW_3D"  #<<<<<NEEDED
        bpy.ops.object.parent_set(type='OBJECT')
#dbg pkhg        print(res)
        return {'FINISHED'}
        

#registering
def register():
    myPrompt("add_cells registerd, press either button\n\
activate two meshes, the last one is to be voxeld\nand must be triagulated\
\nType N to see the menu","Info")
    bpy.utils.register_module(__name__)

def unregister():
    myPrompt("add_cells unregistered","Info")
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
