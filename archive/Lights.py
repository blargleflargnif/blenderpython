################################################################################
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This is free software; you may redistribute it, and/or modify it,
# under the terms of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License (http://www.gnu.org/licenses/) for more details.
#
# ***** END GPL LICENSE BLOCK *****
'''
Create "light fixture" (lamp) at 3D cursor as decorative object in a scene.
'''
# Author(s): Antonio Vazquez (antonioya), jambay
# Version: 0, 1, 0
#
# @todo: Add "luminescence" for object as "true" lamp object. Cycles or other...
# @todo: Allow use in Edit mode.
#
################################################################################

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty
import math
import colorsys
import copy

# constants
BASE_ROWS = 10 # max lamp base rows/segments (stackable elements).

################################################################################
#from add_mesh_building_basics.tools import *
################################################################################
####### Scraps from tools - to be removed or consolidated...
#
#--------------------------------------------------------------------
# Set normals
# True faces inside, else (default) outside.
#--------------------------------------------------------------------
def set_normals(myObject,direction=False):
    bpy.context.scene.objects.active = myObject
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=direction)
    bpy.ops.object.editmode_toggle()

#--------------------------------------------------------------------
# Set shade smooth
#--------------------------------------------------------------------
def set_smooth(myObject):
    # deactivate others
    for o in bpy.data.objects:
        if (o.select == True):
            o.select = False
    myObject.select = True
    bpy.context.scene.objects.active = myObject
#what? just set active then check for it?
    if (bpy.context.scene.objects.active.name == myObject.name):
        bpy.ops.object.shade_smooth()

#--------------------------------------------------------------------
# Add modifier (subdivision)
#--------------------------------------------------------------------
def set_modifier_subsurf(myObject):
    bpy.context.scene.objects.active = myObject
#what? just set active then check for it?
    if (bpy.context.scene.objects.active.name == myObject.name):
        bpy.ops.object.modifier_add(type='SUBSURF')
        for mod in myObject.modifiers:
            if (mod.type == 'SUBSURF'):
                mod.levels = 2

################################################################################
# Add cycles diffuse material reference for element if new.
# Return new or existing material reference.
def create_diffuse_material(matName,dcR,dcG,dcB,vpR=0.8,vpG=0.8,vpB=0.8,mix = 0.1,twosides=False):

    if matName not in bpy.data.materials: # create new material
        scn = bpy.context.scene

        if not scn.render.engine == 'CYCLES': # Set cycles render engine if not selected
            scn.render.engine = 'CYCLES'

        mat = bpy.data.materials.new(matName)
        mat.diffuse_color = (vpR,vpG,vpB) # viewport color
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        node = nodes['Diffuse BSDF']
        node.inputs[0].default_value = [dcR,dcG,dcB, 1]
        node.location = 200, 320

        node = nodes.new('ShaderNodeBsdfGlossy')
        node.name = 'Glossy_0'
        node.location = 200, 0

        node = nodes.new('ShaderNodeMixShader')
        node.name = 'Mix_0'
        node.inputs[0].default_value = mix
        node.location = 500, 160

        node = nodes['Material Output']
        node.location = 1100, 160

        # Connect nodes
        outN = nodes['Diffuse BSDF'].outputs[0]
        inN = nodes['Mix_0'].inputs[1]
        mat.node_tree.links.new(outN, inN)   

        outN = nodes['Glossy_0'].outputs[0]
        inN = nodes['Mix_0'].inputs[2]
        mat.node_tree.links.new(outN, inN)   

        if twosides:
            node = nodes.new('ShaderNodeNewGeometry')
            node.name = 'Input_1'
            node.location = -80, -70

            node = nodes.new('ShaderNodeBsdfDiffuse')
            node.name = 'Diffuse_1'
            node.inputs[0].default_value = [0.30,0.30,0.30, 1]
            node.location = 200, -280

            node = nodes.new('ShaderNodeMixShader')
            node.name = 'Mix_1'
            node.inputs[0].default_value = mix
            node.location = 800, -70

            outN = nodes['Input_1'].outputs[6]
            inN = nodes['Mix_1'].inputs[0]
            mat.node_tree.links.new(outN, inN)   

            outN = nodes['Diffuse_1'].outputs[0]
            inN = nodes['Mix_1'].inputs[2]
            mat.node_tree.links.new(outN, inN)   

            outN = nodes['Mix_0'].outputs[0]
            inN = nodes['Mix_1'].inputs[1]
            mat.node_tree.links.new(outN, inN)

            outN = nodes['Mix_1'].outputs[0]
            inN = nodes['Material Output'].inputs[0]
            mat.node_tree.links.new(outN, inN)
        else:
            outN = nodes['Mix_0'].outputs[0]
            inN = nodes['Material Output'].inputs[0]
            mat.node_tree.links.new(outN, inN)

    return bpy.data.materials[matName]

#--------------------------------------------------------------------
# Create cycles translucent material
#--------------------------------------------------------------------
def create_translucent_material(matName,dcR,dcG,dcB,vpR=0.8,vpG=0.8,vpB=0.8,mix = 0.1):
    
    if matName not in bpy.data.materials: # create new material
        scn = bpy.context.scene
        # Set cycles render engine if not selected
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'

        mat = bpy.data.materials.new(matName)
        mat.diffuse_color = (vpR,vpG,vpB) # viewport color
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        node = nodes['Diffuse BSDF']
        node.inputs[0].default_value = [dcR,dcG,dcB, 1]
        node.location = 200, 320

        node = nodes.new('ShaderNodeBsdfTranslucent')
        node.name = 'Translucent_0'
        node.location = 200, 0

        node = nodes.new('ShaderNodeMixShader')
        node.name = 'Mix_0'
        node.inputs[0].default_value = mix
        node.location = 500, 160

        node = nodes['Material Output']
        node.location = 1100, 160

        # Connect nodes
        outN = nodes['Diffuse BSDF'].outputs[0]
        inN = nodes['Mix_0'].inputs[1]
        mat.node_tree.links.new(outN, inN)   

        outN = nodes['Translucent_0'].outputs[0]
        inN = nodes['Mix_0'].inputs[2]
        mat.node_tree.links.new(outN, inN)   

        outN = nodes['Mix_0'].outputs[0]
        inN = nodes['Material Output'].inputs[0]
        mat.node_tree.links.new(outN, inN)

    return bpy.data.materials[matName]

#--------------------------------------------------------------------
# Create cycles emission material
#--------------------------------------------------------------------
def create_emission_material(matName,dcR,dcG,dcB,energy):
    
    if matName not in bpy.data.materials: # create new material
        scn = bpy.context.scene
        # Set cycles render engine if not selected
        if not scn.render.engine == 'CYCLES':
            scn.render.engine = 'CYCLES'

        mat = bpy.data.materials.new(matName)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        node = nodes['Diffuse BSDF']
        mat.node_tree.nodes.remove(node) # remove not used

        node = nodes.new('ShaderNodeEmission')
        node.name = 'Emission_0'
        node.inputs[0].default_value = [dcR,dcG,dcB,1]
        node.inputs[1].default_value = energy
        node.location = 200, 160

        node = nodes['Material Output']
        node.location = 700, 160

        # Connect nodes
        outN = nodes['Emission_0'].outputs[0]
        inN = nodes['Material Output'].inputs[0]
        mat.node_tree.links.new(outN, inN)

    return bpy.data.materials[matName]
#
####### Scraps from tools - to be removed or consolidated...
################################################################################




################################################################################
# Set UI options for style.
def LightStyles(sRef,LightStyle):

#    if LightStyle=='0': # set/reset defaults
    sRef.baseZ = 0.20
    sRef.baseRows = 6
    sRef.baseSegs = 16
    sRef.smooth = True
    sRef.subdivide = True

    sRef.br1 = 0.06
    sRef.br2 = 0.08
    sRef.br3 = 0.09
    sRef.br4 = 0.08
    sRef.br5 = 0.06
    sRef.br6 = 0.03

    sRef.bz1 = 0
    sRef.bz2 = 0
    sRef.bz3 = 0
    sRef.bz4 = 0
    sRef.bz5 = 0
    sRef.bz6 = 0

    if LightStyle=='1': # Sphere
        sRef.baseZ = 0.22
        sRef.br1 = 0.05
        sRef.br2 = 0.07
        sRef.br3 = 0.11
        sRef.br4 = 0.11
        sRef.br5 = 0.07
        sRef.br6 = 0.03

        sRef.bz1 = 0
        sRef.bz2 = -1
        sRef.bz3 = -0.456
        sRef.bz4 = 0.089
        sRef.bz5 = -0.038
        sRef.bz6 = -0.165

    if LightStyle=='2': # Pear
        sRef.br1 = 0.056
        sRef.br2 = 0.062
        sRef.br3 = 0.072
        sRef.br4 = 0.090
        sRef.br5 = 0.074
        sRef.br6 = 0.03

    if LightStyle=='3': # Vase
        sRef.baseSegs = 8
        sRef.br1 = 0.05
        sRef.br2 = 0.11
        sRef.br3 = 0.15
        sRef.br4 = 0.07
        sRef.br5 = 0.05
        sRef.br6 = 0.03

    if LightStyle=='4': # Square
        sRef.baseZ = 0.15
        sRef.baseSegs = 4
        sRef.baseRows = 5
        sRef.smooth = False
        sRef.subdivide = False
        sRef.br1 = 0.08
        sRef.br2 = 0.08
        sRef.br3 = 0.08
        sRef.br4 = 0.08
        sRef.br5 = 0.03

#        sRef.bz1 = 0
#        sRef.bz2 = 0
#        sRef.bz3 = 0
        sRef.bz4 = 0.25
#        sRef.bz5 = 0

    if LightStyle=='5': # Jug
        sRef.br1 = 0.08
        sRef.br2 = 0.08
        sRef.br3 = 0.08
        sRef.br4 = 0.08
        sRef.br5 = 0.03

#        sRef.bz1 = 0
#        sRef.bz2 = 0
#        sRef.bz3 = 0
        sRef.bz4 = 0.25
#        sRef.bz5 = 0


#------------------------------------------------------------------------------
# Create lamp base
#
# objName: Name for the new object
# height: Size in Z axis
# pX: position X axis
# pY: position Y axis
# pZ: position Z axis
# segments: number of segments
# baseRows: number of rows
# radios: ring radios
# ratios: Z shift ratios
# subdivide: Subdivision flag
# mat: Flag for creating materials
# hue: Hue of the color
# saturation: Saturation of color
# value: Value of color
#------------------------------------------------------------------------------
def create_lamp_base(objName,height,pX,pY,pZ,segments,baseRows,radios,ratios,subdivide,mat,hue,saturation,value):

    # Calculate heights
    segH = height/(baseRows - 1)
    listHeight = []
    z = 0
    for f in range(0,baseRows):
        listHeight.extend([z + (z * ratios[f])])
        z += segH
        
    myData = create_cylinder_data(segments,listHeight,radios,True,True,False,0,subdivide)
    myVertex = myData[0]
    myFaces = myData[1]

    mymesh = bpy.data.meshes.new(objName)
    myCylinder = bpy.data.objects.new(objName, mymesh)
    bpy.context.scene.objects.link(myCylinder)
    
    mymesh.from_pydata(myVertex, [], myFaces)
    mymesh.update(calc_edges=True)
    # Position
    myCylinder.location.x = pX
    myCylinder.location.y = pY
    myCylinder.location.z = pZ

    # Materials
    if mat:
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        myMat = create_diffuse_material(myCylinder.name + "_material", rgb[0], rgb[1], rgb[2], rgb[0], rgb[1], rgb[2], 0.1)
        myCylinder.data.materials.append(myMat)
    
    return (myCylinder,listHeight[len(listHeight)-1])

#------------------------------------------------------------------------------
# Create lampholder
#
# objName: Name for the new object
# height: Size in Z axis
# pX: position X axis
# pY: position Y axis
# pZ: position Z axis
# mat: Flag for creating materials
#------------------------------------------------------------------------------
def create_lampholder(objName,height,pX,pY,pZ,mat):

    myData = create_cylinder_data(16,[0,height,height + 0.005,height + 0.008,height + 0.05]
                                  ,[0.005,0.005,0.010,0.018,0.018]
                                  ,False,False,False,0,False)
    myVertex= myData[0]
    myFaces= myData[1]
    
    mymesh = bpy.data.meshes.new(objName)
    myCylinder = bpy.data.objects.new(objName, mymesh)
    bpy.context.scene.objects.link(myCylinder)
    
    mymesh.from_pydata(myVertex, [], myFaces)
    mymesh.update(calc_edges=True)
    # Position
    myCylinder.location.x = pX        
    myCylinder.location.y = pY       
    myCylinder.location.z = pZ        

    # Materials
    if mat:
        mat = create_diffuse_material(myCylinder.name + "_material", 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.1)
        myCylinder.data.materials.append(mat)
   
    return myCylinder

#------------------------------------------------------------------------------
# Create lampholder strings
#
# objName: Name for the new object
# height: Size in Z axis
# pX: position X axis
# pY: position Y axis
# pZ: position Z axis
# radio: radio of lampshade
# shadeh: height of lampshader
# mat: Flag for creating materials
#------------------------------------------------------------------------------
def create_lampholder_strings(objName,height,pX,pY,pZ,radio,shadeh,mat):

    myData = create_cylinder_data(32,[height + 0.005,height + 0.005,height + 0.006,height + 0.006]
                                  ,[0.018,0.025,0.025,0.018]
                                  ,False,False,False,0,False)
    myVertex= myData[0]
    myFaces= myData[1]

    mymesh = bpy.data.meshes.new(objName)
    myCylinder = bpy.data.objects.new(objName, mymesh)
    bpy.context.scene.objects.link(myCylinder)
    
    mymesh.from_pydata(myVertex, [], myFaces)
    mymesh.update(calc_edges=True)
    # Position
    myCylinder.location.x = pX
    myCylinder.location.y = pY
    myCylinder.location.z = pZ

    if mat:
        mat = create_diffuse_material(myCylinder.name + "_material", 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.1)
        myCylinder.data.materials.append(mat)

    # Box1
    Box1 = create_box_segments("Lamp_B1",shadeh-0.036,radio-0.023)
    Box1.parent = myCylinder
    Box1.location = (0.021,0,height + 0.004)

    if mat:
        Box1.data.materials.append(mat)

    # Box2
    Box2 = create_box_segments("Lamp_B2",shadeh-0.036,-radio+0.023)
    Box2.parent = myCylinder
    Box2.location = (-0.021,0,height + 0.004)

    # Materials
    if mat:
        Box2.data.materials.append(mat)
    
    return myCylinder

#------------------------------------------------------------------------------
# Create lampshade
#
# objName: Name for the new object
# shadeZ: height of lamp shade
# pX: position X axis
# pY: position Y axis
# pZ: position Z axis
# segments: number of segments
# shadeB: shade base radius
# shadeT: shade top radius
# pleats: flag for pleats
# pleatD: indent from shade.
# opacity: opacity factor - 1 = transparent
# mat: Flag to create "Cycles" material
#------------------------------------------------------------------------------
def create_lampshade(objName,shadeZ,pX,pY,pZ,segments,shadeB,shadeT,pleats,pleatD,opacity,mat):

    gap = 0.002
    shadeRs = [shadeB-gap,shadeB-gap,shadeB,shadeT,shadeT-gap,shadeT-gap]

    heights = [gap*2,0,0,shadeZ,shadeZ,shadeZ-(gap*2)]

    myData = create_cylinder_data(segments,heights,shadeRs,False,False,pleats,pleatD,False)

    myVertex = myData[0]
    myFaces = myData[1]

    mymesh = bpy.data.meshes.new(objName)
    myCylinder = bpy.data.objects.new(objName, mymesh)
    bpy.context.scene.objects.link(myCylinder)
    
    mymesh.from_pydata(myVertex, [], myFaces)
    mymesh.update(calc_edges=True)

    # Position
    myCylinder.location.x = pX
    myCylinder.location.y = pY
    myCylinder.location.z = pZ

    #material
    if mat:
        myMat = create_translucent_material(myCylinder.name + "_material",0.8, 0.65, 0.45, 0.8, 0.65, 0.45,opacity)
        myCylinder.data.materials.append(myMat)
    
    return myCylinder

#------------------------------------------------------------------------------
# Create box segments
#
# objName: Name for the new object
# height: Size in Z axis
# shift: Shift movement
#------------------------------------------------------------------------------
def create_box_segments(objName,height,shift):

    gap = 0.001
    myVertex = [(0,0,0),(0,gap,0),(gap,gap,0),(gap,0,0)
                ,(shift,0,height)
                ,(shift,gap,height)
                ,(shift+gap,gap,height)
                ,(shift+gap,0,height)]
    myFaces = [(6, 5, 1, 2),(7, 6, 2, 3),(4, 7, 3, 0),(1, 5, 4, 0)]
    
    mymesh = bpy.data.meshes.new(objName)
    mySegment = bpy.data.objects.new(objName, mymesh)
    bpy.context.scene.objects.link(mySegment)
    
    mymesh.from_pydata(myVertex, [], myFaces)
    mymesh.update(calc_edges=True)
    # Position
    mySegment.location.x = 0        
    mySegment.location.y = 0       
    mySegment.location.z = 0        
    
    return mySegment


#------------------------------------------------------------------------------
# Create cylinders data
#
# segments: Number of pies
# listHeight: list of heights
# listRadio: list of radios
# top: top face flag
# bottom: bottom face flag
# pleats: flag for pleats
# pleatsize: difference in radios (less)
# subdiv: fix subdivision problem
#------------------------------------------------------------------------------
def create_cylinder_data(segments,listHeight,listRadio,bottom,top,pleats,pleatsize,subdiv):
         
    myVertex = []
    myFaces = []
    if (subdiv):
        # Add at element 0 to fix subdivision problems
        listHeight.insert(0,listHeight[0]+0.001)
        listRadio.insert(0,listRadio[0])
        # Add at last element to fix subdivision problems
        e = len(listHeight) - 1
        listHeight.insert(e,listHeight[e]+0.001)
        listRadio.insert(e,listRadio[e])
    #------------------------------------- 
    # Vertices
    #------------------------------------- 
    idx = 0
    rp = 0
    for z in listHeight:
        seg = 0
        for i in range(segments):
            x = math.cos(math.radians(seg)) * (listRadio[idx] + rp)
            y = math.sin(math.radians(seg)) * (listRadio[idx] + rp)
            myPoint = [(x,y,z)]
            myVertex.extend(myPoint)
            seg = seg + (360 / segments)
            # pleats
            if (pleats == True and rp == 0):
                rp = -pleatsize
            else:
                rp = 0    
            
            
        idx = idx + 1
    #------------------------------------- 
    # Faces
    #-------------------------------------
    for r in range(0, len(listHeight)-1): 
        s = r * segments
        t = 1       
        for n in range(0,segments):        
            t = t + 1
            if (t > segments): 
                t = 1
                myFace = [(n+s,n+s - segments + 1,n+s + 1,n+s + segments)]
                myFaces.extend(myFace)
            else:
                myFace = [(n+s,n+s+1,n+s + segments + 1,n+s + segments)]
                myFaces.extend(myFace)
         
    #-----------------
    # bottom face
    #-----------------
    if (bottom):
        fa = []
        for f in range(0,segments):
            fa.extend([f])
        myFaces.extend([fa])
    #-----------------
    # top face
    #-----------------
    if (top):
        fa = []
        for f in range(len(myVertex) - segments,len(myVertex)):
            fa.extend([f])
        myFaces.extend([fa])

    return (myVertex,myFaces)


#------------------------------------------------------------------------------
# Generate object for scene
#------------------------------------------------------------------------------
def create_lampObj(self,context):
    # deactivate others
    for o in bpy.data.objects:
        if (o.select == True):
            o.select = False
    bpy.ops.object.select_all(False)

    location = bpy.context.scene.cursor_location
    myLoc = copy.copy(location) # copy location to keep 3D cursor position
    #---------------------
    # Lamp base
    #---------------------
    myData = create_lamp_base("Lamp_base",self.baseZ,myLoc.x,myLoc.y,myLoc.z,
        self.baseSegs,self.baseRows,
        [self.br1,self.br2,self.br3,self.br4,self.br5,self.br6,self.br7,
            self.br8,self.br9,self.br10],
        (self.bz1,self.bz2,self.bz3,self.bz4,self.bz5,self.bz6,self.bz7,
            self.bz8,self.bz9,self.bz10),self.subdivide,self.crt_mat,self.hue,self.saturation,self.value)
    myBase = myData[0]
    posZ = myData[1]
    set_normals(myBase)
    # Smooth
    if (self.smooth):
        set_smooth(myBase)

    if (self.subdivide):
        set_modifier_subsurf(myBase)
    #---------------------
    # Light stem/pipe, includes socket shape.
    #---------------------
    myHolder = create_lampholder("LightStem",self.stem,myLoc.x,myLoc.y,myLoc.z,self.crt_mat)
    # refine
    set_normals(myHolder)
    set_smooth(myHolder)

    myHolder.parent = myBase
    myHolder.location.x = 0
    myHolder.location.y = 0
    myHolder.location.z = posZ

    #---------------------
    # Lamp strings
    #---------------------
    myStrings = create_lampholder_strings("Lampstrings",self.stem,myLoc.x,myLoc.y,myLoc.z,
        self.tr02,self.shadeZ,self.crt_mat)
    # refine
    set_normals(myStrings)

    myStrings.parent = myHolder
    myStrings.location.x = 0
    myStrings.location.y = 0
    myStrings.location.z = 0.03

    #---------------------
    # Lampshade
    #---------------------
    myTop = create_lampshade("Lampshade",self.shadeZ,myLoc.x,myLoc.y,myLoc.z,
        self.shadeSeg,self.tr01,self.tr02,self.pleats,self.pleatD,self.opacity,self.crt_mat)
    # refine
    set_normals(myTop)
    if self.pleats == False:
        set_smooth(myTop)

    myTop.parent = myBase
    myTop.location.x = 0
    myTop.location.y = 0
    myTop.location.z = posZ+self.stem

    #---------------------
    # Light bulb
    #---------------------
    radbulb= 0.02
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, size=radbulb)
    myBulb = bpy.data.objects[bpy.context.active_object.name]
    myBulb.name = "Lamp_Bulb"
    myBulb.parent = myHolder
    myBulb.location = (0,0,radbulb + self.stem + 0.04)

    if self.crt_mat:
        mat = create_emission_material(myBulb.name,0.8,0.8,0.8,self.energy)
        myBulb.data.materials.append(mat)
        
    # deactivate others
#    bpy.ops.object.select_all(action='DESELECT')
#    for o in bpy.data.objects:
#        if (o.select == True):
#            o.select = False
    
    myBase.select = True        
    bpy.context.scene.objects.active = myBase

    bpy.ops.object.join()
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.editmode_toggle()


############################################################
#
# Add a lamp/light fixture mesh.
#
#    UI functions and object creation.
#
class AddLightFixture(bpy.types.Operator):
    bl_idname = "mesh.add_light"
    bl_label = "Lamps"
    bl_description = "Lamp Generator"
#    bl_category = 'Archimesh'
    bl_options = {'REGISTER', 'UNDO'}

    Style = EnumProperty(items=(
        ('0',"None",""),
        ('1',"Sphere",""),
        ('2',"Pear",""),
        ('3',"Vase",""),
        ('4',"Square",""),
        ('5',"Jug","")
        ),
        name="Style",description="Predefined design")

    oldpreset=Style

    baseZ= FloatProperty(name='Height',min=0.01,max= 10, default= 0.20,precision=3,description='base height')
    baseSegs= IntProperty(name='Segments',min=3,max= 128,default= 16,description='Base radial sections.')
    baseRows= IntProperty(name='Rows',min=2,max=BASE_ROWS,default=6,description='Base vertical sections.')
    stem= FloatProperty(name='Stem',min=0.001,max= 10, default= 0.02,precision=3,description='Light stem height')
    smooth = BoolProperty(name="Smooth",default=True,description="Use smooth shader")
    subdivide = BoolProperty(name="Subdivide",default=True,description="Add subdivision modifier")

    bz1= FloatProperty(name='S1',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz2= FloatProperty(name='S2',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz3= FloatProperty(name='S3',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz4= FloatProperty(name='S4',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz5= FloatProperty(name='S5',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz6= FloatProperty(name='S6',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz7= FloatProperty(name='S7',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz8= FloatProperty(name='S8',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz9= FloatProperty(name='S9',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')
    bz10= FloatProperty(name='S10',min=-1,max= 1, default= 0,precision=3, description='Z shift factor')

    br1= FloatProperty(name='R1',min=0.001,max= 10, default= 0.06,precision=3, description='Ring radio')
    br2= FloatProperty(name='R2',min=0.001,max= 10, default= 0.08,precision=3, description='Ring radio')
    br3= FloatProperty(name='R3',min=0.001,max= 10, default= 0.09,precision=3, description='Ring radio')
    br4= FloatProperty(name='R4',min=0.001,max= 10, default= 0.08,precision=3, description='Ring radio')
    br5= FloatProperty(name='R5',min=0.001,max= 10, default= 0.06,precision=3, description='Ring radio')
    br6= FloatProperty(name='R6',min=0.001,max= 10, default= 0.03,precision=3, description='Ring radio')
    br7= FloatProperty(name='R7',min=0.001,max= 10, default= 0.10,precision=3, description='Ring radio')
    br8= FloatProperty(name='R8',min=0.001,max= 10, default= 0.10,precision=3, description='Ring radio')
    br9= FloatProperty(name='R9',min=0.001,max= 10, default= 0.10,precision=3, description='Ring radio')
    br10= FloatProperty(name='R10',min=0.001,max= 10, default= 0.10,precision=3, description='Ring radio')

    # Material - Cycles color for base
    crt_mat = BoolProperty(name="Cycles materials",default=True,description="Create materials for Cycles render.")
    hue= FloatProperty(name='H',min=0,max= 1, default= 0.044,precision=3, description='Base color Hue')
    saturation= FloatProperty(name='S',min=0,max= 1, default= 0.90,precision=3, description='Base color Saturation')
    value= FloatProperty(name='V',min=0,max= 1, default= 0.8,precision=3, description='Base color Value')

    shadeZ= FloatProperty(name='Height',min=0.01,max= 10, default= 0.20,precision=3, description='lampshade height')
    shadeSeg= IntProperty(name='Segments',min=3,max= 128, default= 32, description='Number of segments (vertical)')
    tr01= FloatProperty(name='R1',min=0.001,max= 10, default= 0.16,precision=3, description='lampshade bottom radius')
    tr02= FloatProperty(name='R2',min=0.001,max= 10, default= 0.08,precision=3, description='lampshade top radius')
    pleats = BoolProperty(name="Pleats",default=False,description="Create pleats in the lampshade")
    pleatD= FloatProperty(name='R3',min=0.001,max= 1,default= 0.01,precision=3,description='Pleat depth')
    energy= FloatProperty(name='Light',min=0.00,max= 1000, default= 15,precision=3, description='Light (bulb) intensity')
    opacity= FloatProperty(name='Translucency',min=0.00,max= 1,default= 0.3,precision=3,description='Lampshade opaqueness (1=clear)')

    #-----------------------------------------------------
    # Draw (create UI)
    #-----------------------------------------------------
    def draw(self, context):
        layout = self.layout

        if not bpy.context.space_data.local_view:
            # Imperial units warning
            if (bpy.context.scene.unit_settings.system == "IMPERIAL"):
                row=layout.row()
                row.label("Warning: Imperial units not supported", icon='COLOR_RED')

            box=layout.box()
            box.label("Lamp base")
            row=box.row()
            row.prop(self,'Style')
            row=box.row()
            row.prop(self,'baseZ')
            row.prop(self,'baseSegs')
            row.prop(self,'baseRows')
            row=box.row()
            row.prop(self,'smooth')
            row.prop(self,'subdivide')
            row=box.row()
            row.prop(self,'stem')

# replace this with "For" loop?
            # display "row" entries based on property min=2, rest optional.
            row = box.row()
            row.prop(self,'br1')
            row.prop(self,'bz1',slider=True)

            row = box.row()
            row.prop(self,'br2')
            row.prop(self,'bz2',slider=True)

            if (self.baseRows >= 3): 
                row = box.row()
                row.prop(self,'br3')
                row.prop(self,'bz3',slider=True)
            
            if (self.baseRows >= 4): 
                row = box.row()
                row.prop(self,'br4')
                row.prop(self,'bz4',slider=True)
            if (self.baseRows >= 5): 
                row = box.row()
                row.prop(self,'br5')
                row.prop(self,'bz5',slider=True)
            if (self.baseRows >= 6): 
                row = box.row()
                row.prop(self,'br6')
                row.prop(self,'bz6',slider=True)
            if (self.baseRows >= 7): 
                row = box.row()
                row.prop(self,'br7')
                row.prop(self,'bz7',slider=True)
            if (self.baseRows >= 8): 
                row = box.row()
                row.prop(self,'br8')
                row.prop(self,'bz8',slider=True)
            if (self.baseRows >= 9): 
                row = box.row()
                row.prop(self,'br9')
                row.prop(self,'bz9',slider=True)
            if (self.baseRows >= 10): 
                row = box.row()
                row.prop(self,'br10')
                row.prop(self,'bz10',slider=True)

            box.prop(self,'crt_mat')
            if (self.crt_mat):
                row=box.row()
                row.prop(self,'hue',slider=True)
                row=box.row()
                row.prop(self,'saturation',slider=True)
                row=box.row()
                row.prop(self,'value',slider=True)

            box=layout.box()
            box.label("Lampshade")
            row=box.row()
            row.prop(self,'shadeZ')
            row.prop(self,'shadeSeg')
            row=box.row()
            row.prop(self,'tr01')
            row.prop(self,'tr02')
            row=box.row()
            row.prop(self,'energy')
            row.prop(self,'opacity',slider=True)
            row=box.row()
            row.prop(self,'pleats')
            if self.pleats:
                row.prop(self,'pleatD')

# what's this? and does it need to be accounted for in other scripts?
        else:
            row=layout.row()
            row.label("Warning: Operator does not work in local view mode", icon='ERROR')

    ##########-##########-##########-##########

    def execute(self, context):
        if bpy.context.mode == "OBJECT":
            if self.oldpreset!=self.Style: # Don't modify/reset unless new style selected.
                LightStyles(self,self.Style)
                self.oldpreset=self.Style

            create_lampObj(self,context)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Option only valid in Object mode")
            return {'CANCELLED'}
