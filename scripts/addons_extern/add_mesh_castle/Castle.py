################################################################################
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This is free software under the terms of the GNU General Public License
# you may redistribute it, and/or modify it.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License (http://www.gnu.org/licenses/) for more details.
#
# ***** END GPL LICENSE BLOCK *****
'''
Generate an object: (OBJ_N) "Castle", mesh complex collection.
 Derived from many sources, inspired by many in the "community",
 - see documentation for details on use and credits.
'''
# mod list, in order of complexity and necessity...
#  some want, some needed, some a feature not a bug just need controls.
#
# @todo: fix dome radius -  not complete when wall width or depth < 15
#        globe (z/2) is fun but not intended design.
# @todo: check width minimum as is done for height, maybe depth too.
# @todo: fix grout for bottom of first row (adjust wall base).
#
# @todo: get some very interesting positioning results when 3D Cursor is not (0,0,0)
#
# @todo: eleminate result of "None" if possible from  circ() and other subroutines.
# @todo: review defaults and limits for all UI entries.
#
#
# Abstract/experimental use only:
# @todo: Curve (wallSlope) inverts walls: reverse slope and adjust sizing to fit floor.
# @todo: Tunnel, paired sloped walls, need to create separate objects and adjust sizing.
# @todo: Turret/tower - uses rotated wall, need to change curvature/slope orientation/sizing.
#
#
# wish list:
# @todo: do not allow opening overlap.
# @todo: implement "Oculus" for dome (top center opening).
# @todo: integrate portal with doorway.
# @todo: add stair_builder; keep (wall) steps.
# @todo: integrate balcony with shelf.
# @todo: add block shapes: triangle, hexagon, octagon, round (disc/ball), "Rocks" (Brikbot author), etc...
#        - possible window/door/opening shapes?
#
################################################################################

import bpy
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty
from random import random

import math
from math import fmod, sqrt, sin, cos, atan

################################################################################

################################################################################

#####
# constants
#####

OBJ_N="Castle" # Primary object name
OBJ_F="CWallF"
OBJ_L="CWallL"
OBJ_B="CWallB"
OBJ_R="CWallR"

# not sure if this is more efficient or not, just seems no need to import value.
cPie=3.14159265359
cPieHlf=cPie/2 # used to rotate walls 90 degrees (1.570796...)

BLOCK_MIN=0.1 # Min block sizing; also used for openings.

WALL_MAX=100

WALL_MIN=BLOCK_MIN*3 # min wall block size*3 for each dimension.
WALL_DEF=20 # Default wall/dome size
WALL_DEF_HALF=WALL_DEF/2

LVL_MAX=10 # castle levels (vertical wall repeat).

# riser BLOCK_XDEF should be 0.75 and tread BLOCK_DDEF 1.0 for stair steps.
BLOCK_XDEF=0.75 # stanadard block width, including steps and shelf.
BLOCK_DDEF=1.0 # standard block depth.
BLOCK_MAX=WALL_MAX # Max block sizing.
# block variations
BLOCK_VMIN=0 # no negative values.
BLOCK_VMAX=BLOCK_MAX/2
BLOCK_VDEF=BLOCK_MIN

# gap 0 makes solid wall but affects other options, like openings, not in a good way.
# Negative gap creates "phantom blocks" (extraneous verts) inside the faces.
GAP_MIN=0.01 # min space between blocks.
GAP_MAX=BLOCK_MAX/2 # maybe later... -BLOCK_MIN # max space between blocks.

ROW_H_WEIGHT=0.5 # Use 0.5, else create parameter:
#  0=no effect, 1=1:1 relationship, negative values allowed.

BASE_TMIN=BLOCK_MIN # floor min thickness
BASE_TMAX=BLOCK_MAX/2 # floor max thickness, limit to half (current) block height.

# Default Door settings
DEF_DOORW=2.5
DEF_DOORH=3.5
DEF_DOORX=2.5

#####
# working variables, per option per level.
#####

# wall/block Settings
settings = {'w': 1.2, 'wv': 0.3, 'h': .6, 'd': 0.3, 'dv': 0.1,
            'g': 0.1, 'sdv': 0.1,
            'eoff':0.3,
            'Steps':False, 'StepsL':False, 'StepsB':False, 'StepsO':False,
            'Shelf':False, 'ShelfO':False,
            'Slope':False,'Dome':False}
# 'w':width 'wv':width Variation
# 'h':height
# 'd':depth 'dv':depth Variation
# 'g':grout
# 'sdv':subdivision(distance or angle)
# 'eoff':edge offset
# passed as params since modified per object; no sense to change UI values.
# 'Steps' create steps, 'StepsL'step left, 'StepsB' fill with blocks, 'StepsO' outside of wall.
# 'Shelf' add shelf/balcony, 'ShelfO'outside of wall.
# 'Slope': curve wall - forced for Dome
# 'Dome" - dome, globe when height/2

# dims = area of wall (centered/splitX from 3D cursor); modified for radial/dome.
dims = {'s':-10, 'e':10, 't':15}
#dims = {'s':0, 'e':cPie*3/2, 't':12.3} # radial
# 's' start, 'e' end, 't' top

# Apertures in wall, includes all openings for door, window, slot.
#openingSpecs = []
# openingSpecs indexes, based on order of creation.
OP_DOOR=0
OP_PORT=1
OP_CREN=2
OP_SLOT=3

openingSpecs = [{'a':False, 'w':0.5, 'h':0.5, 'x':0.8, 'z':0, 'n':0, 'bvl':0.0,
                 'v':0, 'vl':0, 't':0, 'tl':0}]
# 'a': active (apply to object),
# 'w': opening width, 'h': opening height,
# 'x': horizontal position, 'z': vertical position,
# 'n': repeat opening with a spacing of x,
# 'bvl': bevel the inside of the opening,
# 'v': height of the top arch, 'vl':height of the bottom arch,
# 't': thickness of the top arch, 'tl': thickness of the bottom arch

# need to create an array of arrays for each level...
levelSettings=[settings, dims, openingSpecs]


################################################################################

############################
#
# Psuedo macros:
#
# random values (in specific range).
    # random value +-0.5
def rndc(): return (random() - 0.5)

    # random value +-1
def rndd(): return rndc()*2

# line/circle intercepts
# COff = distance perpendicular to the line to the center
# cRad=radius
# return the distance paralell to the line to the center of the circle at the intercept.
# @todo: eleminate result of "None" if possible from  circ() and other subroutines.
def circ(COff=0,cRad=1):
    absCOff = abs(COff)
    if absCOff > cRad: return None
    elif absCOff == cRad: return 0
    else: return sqrt(cRad**2 - absCOff**2)

# bevel blocks.
# pointsToAffect are: left=(4,6), right=(0,2)
def bevelBlockOffsets(offsets,bevel,pointsToAffect):
    for num in pointsToAffect:
        offsets[num] = offsets[num][:]
        offsets[num][0] += bevel

############################
#
# Simple material management.
# Return new, existing, or modified material reference.
#
# @todo: create additional materials based on diffuse options.
#
def uMatRGBSet(matName,RGBs,matMod=False,dShader='LAMBERT',dNtz=1.0):

    if matName not in bpy.data.materials:
        mtl=bpy.data.materials.new(matName)
        matMod=True
    else:
        mtl=bpy.data.materials[matName]

    if matMod: # Set material values
        mtl.diffuse_color=RGBs
        mtl.diffuse_shader=dShader
        mtl.diffuse_intensity=dNtz

    return mtl

################################################################################

################################################################################
#
#  UI functions and object creation.
#
class add_castle(bpy.types.Operator):
    bl_idname="mesh.add_castle"
    bl_label=OBJ_N
    bl_description=OBJ_N
    bl_options = {'REGISTER', 'UNDO'}

    # only create object when True
    # False allows modifying several parameters without creating object
    ConstructTog = BoolProperty(name="Construct",description="Generate the object",default=True)

    # Base area - set dimensions - Width (front/back) and Depth (sides),
    # floor origin/offset, thickness, and, material/color.
    cBaseW=FloatProperty(name="Width",min=WALL_MIN,max=WALL_MAX,default=WALL_DEF,description="Base Width (X)")
    cBaseD=FloatProperty(name="Depth",min=WALL_MIN,max=WALL_MAX,default=WALL_DEF,description="Base Depth (Y)")
    cBaseO=FloatProperty(name='Base',min=0,max=WALL_MAX,default=0,description="vert offset from 3D cursor.")
    cBaseT=FloatProperty(min=BASE_TMIN,max=BASE_TMAX,default=BASE_TMIN,description="Base thickness")

    cBaseRGB=FloatVectorProperty(min=0,max=1,default=(0.1,0.1,0.1),subtype='COLOR',size=3)


    CBaseB=BoolProperty(name="BloX",default=False,description="Block flooring")
    CBaseR=BoolProperty(name="O",default=False,description="Round flooring")

    CLvls=IntProperty(name="Levels",min=1,max=LVL_MAX,default=1)

    # current wall level parameter value display.
    CLvl=IntProperty(name="Level",min=1,max=LVL_MAX,default=1)

    curLvl=CLvl

    wallRGB=FloatVectorProperty(min=0,max=1,default=(0.5,0.5,0.5),subtype='COLOR',size=3)


# track height with number of floors...?
    wallH=FloatProperty(name="Height",min=WALL_MIN,max=WALL_MAX,default=WALL_DEF)

    # Which walls to generate, per level - LVL_MAX
    wallF1=BoolProperty(name="F",default=False,description="Front")
    wallF2=BoolProperty(name="F",default=False,description="Front")
    wallF3=BoolProperty(name="F",default=False,description="Front")
    wallF4=BoolProperty(name="F",default=False,description="Front")
    wallF5=BoolProperty(name="F",default=False,description="Front")
    wallF6=BoolProperty(name="F",default=False,description="Front")
    wallF7=BoolProperty(name="F",default=False,description="Front")
    wallF8=BoolProperty(name="F",default=False,description="Front")
    wallF9=BoolProperty(name="F",default=False,description="Front")
    wallF10=BoolProperty(name="F",default=False,description="Front")

    wallL1=BoolProperty(name="L",default=False,description="Left")
    wallL2=BoolProperty(name="L",default=False,description="Left")
    wallL3=BoolProperty(name="L",default=False,description="Left")
    wallL4=BoolProperty(name="L",default=False,description="Left")
    wallL5=BoolProperty(name="L",default=False,description="Left")
    wallL6=BoolProperty(name="L",default=False,description="Left")
    wallL7=BoolProperty(name="L",default=False,description="Left")
    wallL8=BoolProperty(name="L",default=False,description="Left")
    wallL9=BoolProperty(name="L",default=False,description="Left")
    wallL10=BoolProperty(name="L",default=False,description="Left")

    wallB1=BoolProperty(name="B",default=False,description="Back")
    wallB2=BoolProperty(name="B",default=False,description="Back")
    wallB3=BoolProperty(name="B",default=False,description="Back")
    wallB4=BoolProperty(name="B",default=False,description="Back")
    wallB5=BoolProperty(name="B",default=False,description="Back")
    wallB6=BoolProperty(name="B",default=False,description="Back")
    wallB7=BoolProperty(name="B",default=False,description="Back")
    wallB8=BoolProperty(name="B",default=False,description="Back")
    wallB9=BoolProperty(name="B",default=False,description="Back")
    wallB10=BoolProperty(name="B",default=False,description="Back")

    wallR1=BoolProperty(name="R",default=False,description="Right")
    wallR2=BoolProperty(name="R",default=False,description="Right")
    wallR3=BoolProperty(name="R",default=False,description="Right")
    wallR4=BoolProperty(name="R",default=False,description="Right")
    wallR5=BoolProperty(name="R",default=False,description="Right")
    wallR6=BoolProperty(name="R",default=False,description="Right")
    wallR7=BoolProperty(name="R",default=False,description="Right")
    wallR8=BoolProperty(name="R",default=False,description="Right")
    wallR9=BoolProperty(name="R",default=False,description="Right")
    wallR10=BoolProperty(name="R",default=False,description="Right")

    CRoof=BoolProperty(name="Roof",default=False)

    # block sizing
    blockX=FloatProperty(name="Width",min=BLOCK_MIN,max=BLOCK_MAX,default=BLOCK_XDEF)
    blockWVar=FloatProperty(name="Variance",min=BLOCK_VMIN,max=BLOCK_VMAX,default=BLOCK_VDEF,description="Randomize")
    blockZ=FloatProperty(name="Height",min=BLOCK_MIN,max=BLOCK_MAX,default=BLOCK_XDEF)
    blockHVar=FloatProperty(name="Variance",min=BLOCK_VMIN,max=BLOCK_VMAX,default=BLOCK_VDEF,description="Randomize")
    blockD=FloatProperty(name="Depth",min=BLOCK_MIN,max=BLOCK_MAX,default=BLOCK_DDEF)
# allow 0 for test cases...
#    blockD=FloatProperty(name="Depth",min=0,max=BLOCK_MAX,default=BLOCK_DDEF)
    blockDVar=FloatProperty(name="Variance",min=BLOCK_VMIN,max=BLOCK_VMAX,default=0,description="Randomize")

    MergeBlock = BoolProperty(name="Merge",default=True,description="merge closely adjoining blocks")

# @todo: fix edgeing for mis-matched row sizing (or just call it a feature).
    EdgeOffset=FloatProperty(name="Edging",min=0,max=WALL_MAX,default=0.25,description="stagger wall ends")

    # block spacing
    Grout=FloatProperty(name="Gap",min=GAP_MIN,max=GAP_MAX,default=0.05,description="Block separation")

    # Radiating from one point - round (disc), with slope makes dome.
    cDome=BoolProperty(name='Dome',default=False)
    cDomeRGB=FloatVectorProperty(min=0,max=1,default=(0.3,0.1,0),subtype='COLOR',size=3)

    cDomeH=FloatProperty(name='Height',min=WALL_MIN,max=WALL_MAX,default=WALL_DEF/2)
    cDomeZ=FloatProperty(name='Base',min=BASE_TMIN,max=WALL_MAX,default=WALL_DEF,description="offset from floor")
    cDomeO=FloatProperty(name='Oculus',min=0,max=WALL_MAX/2,default=0,description="Dome opening.")

    # holes/openings in wall - doors, windows or slots; affects block row size.
    wallDoor=BoolProperty(name="Door",default=False,description="Door opening")
    wallDoorW=FloatProperty(name="Width",min=BLOCK_MIN,max=WALL_MAX,default=DEF_DOORW)
    wallDoorH=FloatProperty(name="Height",min=BLOCK_MIN,max=WALL_MAX,default=DEF_DOORH)
    wallDoorX=FloatProperty(name="Indent",min=0,max=WALL_MAX,default=DEF_DOORX,description="horizontal offset from cursor")
    doorBvl=FloatProperty(name="Bevel",min=-10,max=10,default=0.25,description="Angle block face")
    doorRpt=BoolProperty(default=False,description="make multiple openings")
    doorArch=BoolProperty(name="Arch",default=True)
    doorArchC=FloatProperty(name="Curve",min=0.01,max=WALL_MAX,default=2.5,description="Arch curve height")
    doorArchT=FloatProperty(name="Thickness",min=0.001,max=WALL_MAX,default=0.75)

    wallDF=BoolProperty(name="F",default=True,description="Front wall")
    wallDL=BoolProperty(name="L",default=True,description="Left wall")
    wallDB=BoolProperty(name="B",default=True,description="Back wall")
    wallDR=BoolProperty(name="R",default=True,description="Right wall")

    # embrasure - classical slit for arrow/rifle ports.
#need to prevent overlap with arch openings - though inversion is an interesting effect.
    SlotV=BoolProperty(default=False,description="classical arrow/rifle ports")
    SlotVW=FloatProperty(name="Width",min=BLOCK_MIN,max=WALL_MAX,default=0.5)
    SlotVH=FloatProperty(name="Height",min=BLOCK_MIN,max=WALL_MAX,default=3.5)
    SlotVL=FloatProperty(name="Indent",min=-WALL_MAX,max=WALL_MAX,default=0,description="The x position or spacing")
    SlotVZ=FloatProperty(name="Bottom",min=-WALL_MAX,max=WALL_MAX,default=4.00)
    slotVArchT=BoolProperty(name="Top",default=True)
    slotVArchB=BoolProperty(name="Bottom",default=True)
    SlotVRpt = BoolProperty(name="Repeat",default=False)

    wallEF=BoolProperty(name="F",default=True,description="Front wall")
    wallEL=BoolProperty(name="L",default=True,description="Left wall")
    wallEB=BoolProperty(name="B",default=True,description="Back wall")
    wallER=BoolProperty(name="R",default=True,description="Right wall")

    # window opening in wall.
    wallPort=BoolProperty(default=False,description="Window opening")
    wallPortW=FloatProperty(name="Width",min=BLOCK_MIN,max=WALL_MAX,default=2,description="Window (hole) width")
    wallPortH=FloatProperty(name="Height",min=BLOCK_MIN,max=WALL_MAX,default=3,description="Window (hole) height")
    wallPortX=FloatProperty(name="Indent",min=-WALL_MAX,max=WALL_MAX,default=-2.5,description="The x position or spacing")
    wallPortZ=FloatProperty(name="Bottom",min=-WALL_MAX,max=WALL_MAX,default=5)
    wallPortBvl=FloatProperty(name="Bevel",min=-10,max=10,default=0.25,description="Angle block face")
    wallPortArchT=BoolProperty(name="Top",default=False)
    wallPortArchB=BoolProperty(name="Bottom",default=False)
    wallPortRpt = BoolProperty(name="Repeat",default=False)

    wallPF=BoolProperty(name="F",default=True,description="Front wall")
    wallPL=BoolProperty(name="L",default=True,description="Left wall")
    wallPB=BoolProperty(name="B",default=True,description="Back wall")
    wallPR=BoolProperty(name="R",default=True,description="Right wall")

    # Crenel = "gaps" on top of wall.
    Crenel=BoolProperty(name="Crenels",default=False,description="Make openings along top of wall")
# review and determine min for % - should allow less...
    CrenelXP=FloatProperty(name="Width %",min=0.10,max=1.0,default=0.15)
    CrenelZP=FloatProperty(name="Height %",min=0.10,max=1.0,default=0.10)

    wallCF=BoolProperty(name="F",default=True,description="Front wall")
    wallCL=BoolProperty(name="L",default=True,description="Left wall")
    wallCB=BoolProperty(name="B",default=True,description="Back wall")
    wallCR=BoolProperty(name="R",default=True,description="Right wall")

    # shelf location and size.
# see "balcony" options for improved capabilities.
    Shelf1=BoolProperty(name="Shelf",default=False,description="Shelf for walls.")
# should limit x and z to wall boundaries
    ShelfX=FloatProperty(name="XOff",min=-WALL_MAX,max=WALL_MAX,default=-WALL_DEF_HALF,description="x origin")
    ShelfZ=FloatProperty(name="Base",min=-WALL_MAX,max=WALL_MAX,default=WALL_DEF,description="z origin")
    ShelfW=FloatProperty(name="Width",min=BLOCK_MIN,max=WALL_MAX,default=WALL_DEF,description="The Width of shelf area")
# height seems to be double, check usage
    ShelfH=FloatProperty(name="Height",min=BLOCK_MIN,max=WALL_MAX,default=0.5,description="The Height of Shelf area")
    ShelfD = FloatProperty(name="Depth",min=BLOCK_MIN,max=WALL_MAX,default=BLOCK_DDEF,description="Depth of shelf")
    ShelfOut=BoolProperty(name="Out",default=True,description="Position outside of wall")

    wallBF=BoolProperty(name="F",default=True,description="Front wall")
    wallBL=BoolProperty(name="L",default=True,description="Left wall")
    wallBB=BoolProperty(name="B",default=True,description="Back wall")
    wallBR=BoolProperty(name="R",default=True,description="Right wall")

    # steps
    Step1=BoolProperty(name="Steps",default=False,description="Steps for walls.")
    StepX=FloatProperty(name="XOff",min=-WALL_MAX,max=WALL_MAX,default=-WALL_DEF_HALF,description="x origin")
    StepZ=FloatProperty(name="Base",min=-WALL_MAX,max=WALL_MAX,default=0,description="z origin")
    StepW=FloatProperty(name="Width",min=BLOCK_MIN,max=WALL_MAX,default=WALL_DEF,description="Width of step area")
    StepH=FloatProperty(name="Height",min=BLOCK_MIN,max=WALL_MAX,default=WALL_DEF,description="Height of step area")
    StepD=FloatProperty(name="Depth",min=BLOCK_MIN,max=WALL_MAX,default=BLOCK_XDEF,description="Step offset (distance) from wall")
    StepV=FloatProperty(name="Riser",min=BLOCK_MIN,max=WALL_MAX,default=BLOCK_XDEF,description="Step height")
    StepT=FloatProperty(name="Tread",min=BLOCK_MIN,max=WALL_MAX,default=BLOCK_DDEF,description="Step footing/tread")
    StepL=BoolProperty(name="Slant",default=False,description="Step direction.")
    StepF=BoolProperty(name="Fill",default=False,description="Fill with supporting blocks")
    StepOut=BoolProperty(name="Out",default=False,description="Position outside of wall")

    wallSF=BoolProperty(name="F",default=True,description="Front wall")
    wallSL=BoolProperty(name="L",default=True,description="Left wall")
    wallSB=BoolProperty(name="B",default=True,description="Back wall")
    wallSR=BoolProperty(name="R",default=True,description="Right wall")

    # Experimental options
    cXTest=BoolProperty(default=False)
    # wall shape modifiers
    # make the wall circular - if not curved it's a flat disc
    # Radiating from one point - round/disc; instead of square
#    wallDisc=BoolProperty(default=False,description="Make wall disc")
    # Warp/slope/curve wall - abstract use only (except for dome use)
    wallSlope=BoolProperty(default=False,description="Curve wall") # top to bottom mid
    CTunnel=BoolProperty(default=False,description="Tunnel wall") # bottom to top mid
# rotate tunnel?...
    CTower=BoolProperty(name='Tower',default=False)

##
####
################################################################################
# Show the UI - present properties to user.
    # Display the toolbox options
################################################################################
####
##
    def draw(self, context):

        layout = self.layout

        box = layout.box()
        box.prop(self,'ConstructTog')

        # Castle area.
        box=layout.box()
        row=box.row()
        row.prop(self,'cBaseRGB',text='Base')
        row=box.row()
        row.prop(self,'cBaseW')
        row.prop(self,'cBaseD')
# this is 0 until more complex settings allowed... like repeat or per-level (like wall) selection.
#        box.prop(self,'cBaseO') # vert offset from 3D cursor

        box.prop(self,'cBaseT',text="Thickness") # height/thickness of floor.
        row=box.row()
        row.prop(self,'CBaseB') # Blocks or slab
        if self.properties.CBaseB:
            row.prop(self,'CBaseR') # Round
        box.prop(self,'CLvls',text="Levels") # number of floors.

        # block sizing
        box=layout.box()
        row=box.row()
        row.label(text='Blocks:')
        row.prop(self,'MergeBlock')
        box.prop(self,'EdgeOffset')
        box.prop(self,'Grout')
        box.prop(self,'blockX')
#add checkbox for "fixed" sizing (ignore variance) a.k.a. bricks.
        box.prop(self, 'blockWVar')
        box.prop(self,'blockZ')
        box.prop(self, 'blockHVar')
        box.prop(self,'blockD')
        box.prop(self,'blockDVar')

        box=layout.box()
        box.prop(self,'CLvl',text="Level") # current "Level" (UI parameter values).

        # Walls
#        box=layout.box()
        row=box.row()
        row.prop(self,'wallRGB',text='Walls')
        row=box.row() # which walls to generate - show current level value.
        row.prop(self,'wallF'+str(self.properties.CLvl))
        row.prop(self,'wallL'+str(self.properties.CLvl))
        row.prop(self,'wallB'+str(self.properties.CLvl))
        row.prop(self,'wallR'+str(self.properties.CLvl))
        box.prop(self,'wallH')
        box.prop(self,'CRoof',text="Roof") # ceiling for wall.

        # Dome
        box = layout.box()
        row=box.row()
        row.prop(self,'cDome')
        if self.properties.cDome:
            row.prop(self,'cDomeRGB',text='')
            box.prop(self,'cDomeH')
            box.prop(self,'cDomeZ')
# Oculus - opening in top of dome
#            box.prop(self,'cDomeO')

        # Openings (doors, windows; arched)
        box = layout.box()
        row=box.row()
        row.prop(self,'wallDoor')
        if self.properties.wallDoor:
            row.prop(self,'doorRpt',text='Dupe')
            row=box.row() # which walls have a Door
            row.prop(self,'wallDF')
            row.prop(self,'wallDL')
            row.prop(self,'wallDB')
            row.prop(self,'wallDR')
            box.prop(self, 'wallDoorW')
            box.prop(self, 'wallDoorH')
            box.prop(self, 'wallDoorX')
            box.prop(self, 'doorBvl')

            box.prop(self,'doorArch')
            if self.doorArch:
                box.prop(self, 'doorArchC')
                box.prop(self, 'doorArchT')

        box = layout.box()
        row=box.row()
        row.prop(self,'SlotV',text='Slot')
        if self.properties.SlotV:
            row.prop(self,'SlotVRpt',text='Dupe')
            row=box.row() # which walls embrasures/slits
            row.prop(self,'wallEF')
            row.prop(self,'wallEL')
            row.prop(self,'wallEB')
            row.prop(self,'wallER')
            box.prop(self,'SlotVL')
            box.prop(self,'SlotVW')
            box.prop(self,'SlotVH')
            box.prop(self,'SlotVZ')
            box.label(text='Arch')
            row=box.row()
            row.prop(self,'slotVArchT')
            row.prop(self,'slotVArchB')

        box = layout.box()
        row=box.row()
        row.prop(self,'wallPort',text='Window')
        if self.properties.wallPort:
            row.prop(self,'wallPortRpt',text='Dupe')
            row=box.row() # which walls have portals
            row.prop(self,'wallPF')
            row.prop(self,'wallPL')
            row.prop(self,'wallPB')
            row.prop(self,'wallPR')
            row=box.row()
            row.prop(self,'wallPortW')
            row.prop(self,'wallPortH')
            box.prop(self,'wallPortX')
            box.prop(self,'wallPortZ')
            box.prop(self,'wallPortBvl')
            box.label(text='Arch')
            row=box.row()
            row.prop(self,'wallPortArchT')
            row.prop(self,'wallPortArchB')

        # Crenels: gaps in top of wall, base of dome.
        box = layout.box()
        box.prop(self,'Crenel')
        if self.properties.Crenel:
            row=box.row() # which walls have Crenellation
            row.prop(self,'wallCF')
            row.prop(self,'wallCL')
            row.prop(self,'wallCB')
            row.prop(self,'wallCR')
            box.prop(self, 'CrenelXP')
            box.prop(self, 'CrenelZP')

        # Steps
        box = layout.box()
        row=box.row()
        row.prop(self,'Step1')
        if self.properties.Step1:
            row.prop(self,'StepL')
            row=box.row()
            row.prop(self,'StepF')
            row.prop(self,'StepOut')
            row=box.row() # which walls have steps
            row.prop(self,'wallSF')
            row.prop(self,'wallSL')
            row.prop(self,'wallSB')
            row.prop(self,'wallSR')
            box.prop(self, 'StepX')
            box.prop(self, 'StepZ')
            box.prop(self, 'StepW')
            box.prop(self, 'StepH')
            box.prop(self, 'StepD')
            box.prop(self, 'StepV')
            box.prop(self, 'StepT')

        # Shelf/Balcony
        box = layout.box()
        row=box.row()
        row.prop(self,'Shelf1')
        if self.properties.Shelf1:
            row.prop(self,'ShelfOut')
            row=box.row() # which walls have a shelf
            row.prop(self,'wallBF')
            row.prop(self,'wallBL')
            row.prop(self,'wallBB')
            row.prop(self,'wallBR')
            box.prop(self,'ShelfX')
            box.prop(self,'ShelfZ')
            box.prop(self,'ShelfW')
            box.prop(self,'ShelfH')
            box.prop(self,'ShelfD')

        # Experimental
        box = layout.box()
        row=box.row()
        row.prop(self,'cXTest',text='Experimental')
        if self.properties.cXTest:
            box.prop(self,'wallSlope',text='Curve') # abstract/experimental
            box.prop(self,'CTunnel',text='Tunnel') # abstract/experimental
            box.prop(self,'CTower',text='Tower') # abstract/experimental
##
####
################################################################################
# Respond to UI - process the properties set by user.
    # Check and process UI settings to generate castle.
################################################################################
####
##
    def execute(self, context):

        global openingSpecs
        global dims

        levelSettings=[]

        # Limit UI settings relative to other parameters,
        #  set globals and effeciency variables.

        # current level cannot exceed level setting...
        if self.properties.CLvl > self.properties.CLvls:
            self.properties.CLvl = self.properties.CLvls

        castleScene=bpy.context.scene
        blockWidth=self.properties.blockX
        blockHeight=self.properties.blockZ
        blockDepth=self.properties.blockD

        # wall "area" must be at least 3 blocks.
        minWallW=blockWidth*3 # min wall width/depth
        minWallH=blockHeight*3 # min wall height

        if self.properties.cBaseW < minWallW:
            self.properties.cBaseW = minWallW
        CastleX=self.properties.cBaseW
        midWallW=CastleX/2

        if self.properties.wallH < minWallH:
            self.properties.wallH = minWallH
        planeHL=self.properties.wallH
        planeHL2=planeHL*2
        # proportional crenel height, shared with roof positioning.
        crenelH=planeHL*self.properties.CrenelZP

        if self.properties.cBaseD < minWallW:
            self.properties.cBaseD = minWallW
        CastleD=self.properties.cBaseD
        midWallD=(CastleD+blockDepth)/2
#        midWallD=CastleD/2
#        midWallD=(CastleD-blockDepth)/2

        # gap cannot reduce block below minimum.
        if self.properties.Grout > blockHeight/2-BLOCK_MIN:
            self.properties.Grout=blockHeight/2-BLOCK_MIN

        # Variance limit for minimum block height.
# not quite right, but usuable.
        blockHMin=self.properties.Grout+BLOCK_MIN

        # floor "thickness" cannot exceed block height
        if self.properties.cBaseT > blockHeight:
            self.properties.cBaseT = blockHeight

############
#
        if self.properties.cDome:
            # base can't be lower than floor
# consider limiting to roof?
            domeLimit=self.properties.cBaseO+self.properties.cBaseT
            if self.properties.cDomeZ < domeLimit:
                self.properties.cDomeZ = domeLimit

            # base can't be higher than double wall height (per level)
            domeLimit=planeHL2*self.properties.CLvls
            if self.properties.cDomeZ > domeLimit:
                self.properties.cDomeZ = domeLimit

            # height limit to twice smallest wall width/depth.
            if CastleD < CastleX: # use least dimension for dome.
                domeLimit=CastleD*2
            else:
                domeLimit=CastleX*2

            if self.properties.cDomeH > domeLimit:
                self.properties.cDomeH = domeLimit
            domeMaxO=self.properties.cDomeH/2 

            # Dome Oculus (opening) can't be more than half dome height
            if self.properties.cDomeO > domeMaxO:
                self.properties.cDomeO = domeMaxO
############
#####
#
# After validating all the properties see if need to create...
# @todo: fix so last object preserved...
        # No build if construct off or just changing levels
        if not self.properties.ConstructTog:
#        if not self.properties.ConstructTog or self.properties.curLvl!=self.properties.CLvl:
            self.properties.curLvl=self.properties.CLvl
            return {'FINISHED'}
#
#####
############

        # rowprocessing() front/back wall, modified by sides and Dome.
# this centers the wall, maybe add flag to center or offset from cursor...
# if centerwall:
        dims['s'] = -midWallW
        dims['e'] = midWallW
# else:
#        dims['s'] = 0
#        dims['e'] = CastleX

        dims['t'] = planeHL

        # block sizing
        settings['w'] = blockWidth
        settings['wv'] = self.properties.blockWVar
        settings['sdv'] = blockWidth # divisions in area.

        settings['h']=blockHeight

        settings['d'] = blockDepth
        settings['dv'] = self.properties.blockDVar

        settings['g'] = self.properties.Grout

        settings['eoff'] = self.properties.EdgeOffset

#when openings overlap they create inverse stonework - interesting but not the desired effect
# if opening width == indent*2 the edge blocks fail (row of blocks cross opening) - bug.
        openingSpecs=[]
        archTop=[0,0]
        archBot=[0,0]
#
############
#
# make Door opening... always set info, flag for enable.
#
    # set locals
# @todo: fix this....
        openZ=self.properties.cBaseT+1 # track with floor - else 0

        if self.properties.doorArch:
            archTop[0]=self.properties.doorArchC
            archTop[1]=self.properties.doorArchT

        # create opening...
        openingSpecs += [{'a':self.properties.wallDoor,
            'w':self.properties.wallDoorW,'h':self.properties.wallDoorH,
            'x':self.properties.wallDoorX,'z':openZ,
            'n':self.properties.doorRpt,'bvl':self.properties.doorBvl,
            'v':archTop[0],'vl':archBot[0],'t':archTop[1],'tl':archBot[1]}]

############
# Window
#
        archTop[0]=0
        archTop[1]=0
        archBot[0]=0
        archBot[1]=0

        if self.properties.wallPortArchT:
            archTop[0]=self.properties.wallPortW/2
            archTop[1]=self.properties.wallPortW/4

        if self.properties.wallPortArchB:
            archBot[0]=self.properties.wallPortW/2
            archBot[1]=self.properties.wallPortW/4

        # create opening...
        openingSpecs += [{'a':self.properties.wallPort,
            'w':self.properties.wallPortW,'h':self.properties.wallPortH,
            'x':self.properties.wallPortX,'z':self.properties.wallPortZ,
            'n':self.properties.wallPortRpt,'bvl':self.properties.wallPortBvl,
            'v':archTop[0],'vl':archBot[0],'t':archTop[1],'tl':archBot[1]}]

############
# crenellation, top wall gaps...
# if crenel opening overlaps with arch opening it fills with blocks...
#
        archTop[0]=0
        archTop[1]=0
# add bottom arch option?
        archBot[0]=0
        archBot[1]=0

        crenelW = CastleX*self.properties.CrenelXP # Width % opening.
        crenelz=planeHL-(crenelH/2) # set bottom of opening

        crenelSpace=crenelW*2 # assume standard spacing
        crenelRpt=True
        # set indent 0 (center) if opening is 50% or more of wall width, no repeat.
        if crenelSpace >= CastleX:
            crenelSpace=0
            crenelRpt=False

        # create opening...
        openingSpecs += [{'a':self.properties.Crenel,
            'w':crenelW,'h':crenelH,
            'x':crenelSpace,'z':crenelz,
            'n':crenelRpt,'bvl':0,
            'v':archTop[0],'vl':archBot[0],'t':archTop[1],'tl':archBot[1]}]

############
# Slots
#
        archTop[0]=0
        archTop[1]=0
        archBot[0]=0
        archBot[1]=0

        if self.properties.slotVArchT:
            archTop[0]=self.properties.SlotVW
            archTop[1]=self.properties.SlotVW/2
        if self.properties.slotVArchB:
            archBot[0]=self.properties.SlotVW
            archBot[1]=self.properties.SlotVW/2

        # create opening...
        openingSpecs += [{'a':self.properties.SlotV,
            'w':self.properties.SlotVW,'h':self.properties.SlotVH,
            'x':self.properties.SlotVL,'z':self.properties.SlotVZ,
            'n':self.properties.SlotVRpt,'bvl':0,
            'v':archTop[0],'vl':archBot[0],'t':archTop[1],'tl':archBot[1]}]

##
####
################################################################################
# Process the user settings to generate castle.
################################################################################
####
##
        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        wallLoc=[castleScene.cursor_location.x,castleScene.cursor_location.y,castleScene.cursor_location.z]

        # set wall flags for first level.
        wallFLvl=self.properties.wallF1
        wallLLvl=self.properties.wallL1
        wallBLvl=self.properties.wallB1
        wallRLvl=self.properties.wallR1

        # Base/floor object (parent) - there is always a floor.
        wallExtOpts=[False,False] # no steps or shelf
# @todo: offset door by floor height
# @todo: replicate for "multi-floor" option-shared with roof.
#  - will need openings (in plane) for stairs and such...
        settings['Slope']=False # no curve
        settings['eoff']=0 # no edgeing
# need separate flag for floor/roof...
        settings['Dome']=False

        floorMtl=uMatRGBSet('cBase_mat',self.cBaseRGB,matMod=True)

        floorDisc=False # only when blocks and round...
        if self.properties.CBaseB: # floor blocks
            floorDisc=self.properties.CBaseR # rounded

        # set block "area": height, width, depth, and spacing for floor
        # - when rotated or disc shape, height is depth, depth is thickness.
        blockArea=[self.properties.cBaseD,self.properties.cBaseW,self.properties.cBaseT,self.properties.blockZ,self.properties.blockHVar,self.properties.Grout]

        floorRotate=False # rotate for blocks...
        if self.properties.CBaseB: # make floor with blocks.

            saveBD=settings['d'] # put back when done with floor...
            saveBDV=settings['dv']
            settings['d'] = self.properties.cBaseT
            settings['dv'] = 0

            if floorDisc: # make a disc shaped floor
# need separate flag for floor...
                settings['Dome']=True
                if self.properties.cBaseD < self.properties.cBaseW: # narrowest extent
                    blockArea[0]=self.properties.cBaseD/2
                else:
                    blockArea[0]=self.properties.cBaseW/2

                wallLoc[1]+=self.properties.cBaseW/2 # adjust location for radius

            else: # rotate if not disc.
                floorRotate=True

            castleObj=makeWallObj(self,castleScene,wallLoc,OBJ_N,blockArea,[],wallExtOpts,floorMtl)

            if floorRotate:
                castleObj.select=True # must select to rotate 
                # rotate 90 backward
                bpy.ops.transform.rotate(value=-cPieHlf,constraint_axis=[True,False,False])
                bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
                castleObj.select=False # deselect after rotate else joined with others...

            settings['d']=saveBD # restore block values
            settings['dv']=saveBDV

        else: # make solid plane
# trying to merge/share function with block floor, and roof.
#            wallLoc[1]+=self.properties.cBaseT/2
#            wallLoc[2]+=(self.properties.cBaseO+(self.properties.cBaseT/2))

            # no gaps or splits...
#            blockArea[5]=0
#            settings['sdv']=self.properties.cBaseW

            castleMesh=bpy.data.meshes.new(OBJ_N)

            # set plane dimensions and location
            floorBase=self.properties.cBaseO
            floorTop=floorBase+self.properties.cBaseT
            floorPW=self.properties.cBaseW
            floorD=self.properties.cBaseD
            floorXO=-floorPW/2 # center
            floorXE=floorPW/2

            floorBounds=[floorXO,floorXE,floorBase,floorTop,0,floorD]
            castleObj=makePlaneObj(OBJ_N,floorBounds,floorMtl,floorPW)
            castleScene.objects.link(castleObj) # must do for generation/rotation

############
# cieling/roof
# only when walls are enabled...
        if self.properties.CRoof:
# need separate flag for floor/roof...
            settings['Dome']=False # may have been set by floor...
            stepCut=self.properties.StepD
            stepCut2=stepCut+blockDepth/2

            roofMesh=bpy.data.meshes.new("CRoof")

            roofVs=[]
            roofFs=[]

            # set roof/plane size and location

            roofBase=planeHL
            # roof below wall height.
            if self.properties.Crenel: # Crenellations (top row openings)
                roofBase-=crenelH
#            roofBase-=RoofDrop:
                roofBase-=minWallH/2 # roof below wall height.

            roofTop=roofBase+self.properties.cBaseT
            roofPW=self.properties.cBaseW
            roofD=self.properties.cBaseD

            roofXMod=0 # offset roof for side wall options
            roofYMod=0 # offset roof for front or back wall options

            # adjust size and location for front or back walls.
#            if self.properties.'wallF'+str(self.properties.CLvl):
#                roofD-=blockDepth/2
#                roofYMod+=blockDepth/2
#            if self.properties.wallB:
#                roofD-=blockDepth/2

            # adjust size and location per wall that has steps enabled.
# more like a 2nd floor than roof.
            if self.properties.Step1:
                if wallFLvl and self.properties.wallSF:
                    roofD-=stepCut
                    roofYMod+=stepCut
                if self.properties.wallLLvl and self.properties.wallSL:
                    roofPW-=stepCut
                    roofXMod+=stepCut-blockDepth/2
                if self.properties.wallBLvl and self.properties.wallSB:
                    roofD-=stepCut
                if self.properties.wallRLvl and self.properties.wallSR:
                    roofPW-=stepCut

# @todo: change offest/sizing for wall and steps (not centered).
            roofXO=-roofPW/2 # center
            roofXE=roofPW/2

            roofBounds=[roofXO,roofXE,roofBase,roofTop,0,roofD]

            roofObj=makePlaneObj("CRoof",roofBounds,floorMtl,roofPW)
            castleScene.objects.link(roofObj) # must do for generation/rotation

            # shift "location" as needed...
            xMod=roofXMod # side wall offset roof.
            yMod=roofYMod # front wall offset roof.

            if floorDisc: # make a disc shaped floor
                yMod-=roofD/2

            roofObj.location.x+=xMod
            roofObj.location.y+=yMod

            roofObj.parent=castleObj # Connect to parent

####################
# Make "Walls"
        wallMtl=uMatRGBSet('cWall_mat',self.wallRGB,matMod=True)

        wallLvl=0 # make walls per levels as selected...
        wallLoc=[castleScene.cursor_location.x,castleScene.cursor_location.y,castleScene.cursor_location.z]

        while wallLvl < self.properties.CLvls: # make castle wall levels
            if wallLvl == 1: # wallLvl is 0 based, first level flag already set.
                wallFLvl=self.properties.wallF2
                wallLLvl=self.properties.wallL2
                wallBLvl=self.properties.wallB2
                wallRLvl=self.properties.wallR2
            if wallLvl == 2:
                wallFLvl=self.properties.wallF3
                wallLLvl=self.properties.wallL3
                wallBLvl=self.properties.wallB3
                wallRLvl=self.properties.wallR3
            if wallLvl == 3:
                wallFLvl=self.properties.wallF4
                wallLLvl=self.properties.wallL4
                wallBLvl=self.properties.wallB4
                wallRLvl=self.properties.wallR4
            if wallLvl == 4:
                wallFLvl=self.properties.wallF5
                wallLLvl=self.properties.wallL5
                wallBLvl=self.properties.wallB5
                wallRLvl=self.properties.wallR5
            if wallLvl == 5:
                wallFLvl=self.properties.wallF6
                wallLLvl=self.properties.wallL6
                wallBLvl=self.properties.wallB6
                wallRLvl=self.properties.wallR6
            if wallLvl == 6:
                wallFLvl=self.properties.wallF7
                wallLLvl=self.properties.wallL7
                wallBLvl=self.properties.wallB7
                wallRLvl=self.properties.wallR7
            if wallLvl == 7:
                wallFLvl=self.properties.wallF8
                wallLLvl=self.properties.wallL8
                wallBLvl=self.properties.wallB8
                wallRLvl=self.properties.wallR8
            if wallLvl == 8:
                wallFLvl=self.properties.wallF9
                wallLLvl=self.properties.wallL9
                wallBLvl=self.properties.wallB9
                wallRLvl=self.properties.wallR9
            if wallLvl == 9:
                wallFLvl=self.properties.wallF10
                wallLLvl=self.properties.wallL10
                wallBLvl=self.properties.wallB10
                wallRLvl=self.properties.wallR10

            wallSides=[wallFLvl,wallLLvl,wallBLvl,wallRLvl]
            wallLoc[2]=wallLvl*planeHL # each segment base...
            makeWalls(self,castleScene,castleObj,wallSides,wallLoc,wallMtl,wallLvl)
            wallLvl+=1

####################
# Make "Tower"
        if self.properties.cXTest and self.properties.CTower:
            # no steps or shelf for tower...
            wallExtOpts[0]=False
            wallExtOpts[1]=False

            settings['Slope']=True # force curvature

            dims['s'] = 0.0 # radial origin
            dims['e']=CastleX/2 # effective tower height; affects radius.

            # set block "area": height, width, depth, and spacing.
            blockArea=[dims['e'],CastleX,blockDepth,self.properties.blockZ,self.properties.blockHVar,self.properties.Grout]

            # Make "tower" wall.
            wallLoc[0]=0
            wallLoc[1]=0
            wallLoc[2]=castleScene.cursor_location.z

            # generate tower...
            cTower1Obj=makeWallObj(self,castleScene,wallLoc,"CTower1",blockArea,[],wallExtOpts,wallMtl)

            cTower1Obj.select=True # must select to rotate 
# rotate 90 forward (face plant)...
#            bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[True,False,False])
# rotate 90 ccw along side
            bpy.ops.transform.rotate(value=-cPieHlf,constraint_axis=[False,True,False])
            bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
            cTower1Obj.select=False # deselect after rotate else joined with others...

            cTower1Obj.parent=castleObj # Connect to parent

####################
# Make "Dome"
        settings['Dome']=self.properties.cDome
        if self.properties.cDome:
            # no steps or shelf for dome...
            wallExtOpts[0]=False
            wallExtOpts[1]=False

            settings['Slope']=True # force curvature
            settings['sdv'] = 0.12

            wallLoc[0]=castleScene.cursor_location.x
            wallLoc[1]=midWallD
            wallLoc[2]=self.properties.cDomeZ

            domeMtl=uMatRGBSet('cDome_mat',self.cDomeRGB,matMod=True)

            # set block "area": height, width, depth, and spacing.
            blockArea=[self.properties.cDomeH,CastleX,blockDepth,self.properties.blockZ,self.properties.blockHVar,self.properties.Grout]

# eliminate to allow user control for start/completion by width setting.
            dims['s'] = 0.0 # complete radial

            if midWallD < midWallW: # use shortest dimension for dome.
                dims['e'] = midWallD
            else:
                dims['e'] = midWallW

            # generate dome...
            cDomeObj=makeWallObj(self,castleScene,wallLoc,"cDome",blockArea,[],wallExtOpts,domeMtl)

            yMod=0 # shift "location" as needed...
            if floorDisc: # make a disc shaped floor
                yMod-=(CastleD+blockDepth)/2
            cDomeObj.location.y+=yMod

            cDomeObj.parent=castleObj # Connect to parent

        castleObj.select = True
        context.scene.objects.active = castleObj

        return {'FINISHED'}

################################################################################


####################
#
    # Walls
#
# different blocks are generated for each wall when variations or merge settings selected;
# edges/ends don't match.
#
####################
def makeWalls(sRef,objScene,objParent,objSides,objLoc,objMat,objLvl):

    settings['Dome']=False # disable disc/dome
    wallExtOpts=[False,False] # no steps or shelf

    floorDisc=False # only when blocks and round...
    if sRef.properties.CBaseB:
        floorDisc=sRef.properties.CBaseR # round, flat, floor

    WobjH=sRef.properties.wallH
    WobjW=sRef.properties.cBaseW
    WobjY=sRef.properties.cBaseD
    WobjD=sRef.properties.blockD

    segWidth=sRef.properties.blockX

    # center wall...
    midWallD=(WobjY+WobjD)/2
    midWallW=(WobjW+WobjD)/2

    settings['eoff'] = sRef.properties.EdgeOffset
    settings['sdv']=sRef.properties.blockX

    settings['Slope']=False
    if sRef.properties.cXTest:
        if sRef.properties.CTunnel:
            settings['Slope']=True # force curve
        else:
            settings['Slope']=sRef.properties.wallSlope # user select curve walls...

    # passed as params since modified by wall and dome...
    settings['StepsB']=sRef.properties.StepF # fill under with blocks
    settings['StepsL']=sRef.properties.StepL # up to left
    settings['StepsO']=sRef.properties.StepOut # outside of wall

    # set block "area": height, width, depth, and spacing for front and back walls.
    blockArea=[WobjH,WobjW,WobjD,sRef.properties.blockZ,sRef.properties.blockHVar,sRef.properties.Grout]
    dims['s'] = -midWallW
    dims['e'] = midWallW

    yMod=0 # shift front/back "location" as needed...
    if floorDisc: # make a disc shaped floor
        yMod=WobjY

####################
    if objSides[0]: # Make "front" wall.
        objName=OBJ_F+str(objLvl)

        wallSteps=False
        wallShelf=False
        wallHoles=[]

#        if not objLvl: # wall options first floor only
        if sRef.properties.wallDoor:
            openingSpecs[OP_DOOR]['a']=sRef.properties.wallDF
        else:
            openingSpecs[OP_DOOR]['a']=False

        if sRef.properties.wallPort:
            openingSpecs[OP_PORT]['a']=sRef.properties.wallPF
        else:
            openingSpecs[OP_PORT]['a']=False

        if sRef.properties.SlotV:
            openingSpecs[OP_SLOT]['a']=sRef.properties.wallEF
        else:
            openingSpecs[OP_SLOT]['a']=False

        if sRef.properties.Crenel:
            openingSpecs[OP_CREN]['a']=sRef.properties.wallCF
        else:
            openingSpecs[OP_CREN]['a']=False

        wallHoles=openList(sRef)

        # set steps/shelf extrusion options for this wall...
        if sRef.properties.Step1 and sRef.properties.wallSF:
            wallSteps=True
        if sRef.properties.Shelf1 and sRef.properties.wallBF:
            wallShelf=True
# end first floor only ;)

        wallExtOpts[0]=wallSteps
        wallExtOpts[1]=wallShelf

        objLoc[0]=objScene.cursor_location.x
        if sRef.properties.cXTest and sRef.properties.CTunnel:
            objLoc[1]=WobjY/2
        else:
            objLoc[1]=objScene.cursor_location.y

        objLoc[1]-=yMod/2 # offset for disc

        # generate wall...
        cFrontObj=makeWallObj(sRef,objScene,objLoc,objName,blockArea,wallHoles,wallExtOpts,objMat)
        cFrontObj.parent=objParent # Connect to parent

####################
    if objSides[2]: # Make "back" wall.
        objName=OBJ_B+str(objLvl)

        wallSteps=False
        wallShelf=False
        wallHoles=[]

#        if not objLvl: # only for first lvl...
        if sRef.properties.wallDoor:
            openingSpecs[OP_DOOR]['a']=sRef.properties.wallDB
        else:
            openingSpecs[OP_DOOR]['a']=False

        if sRef.properties.wallPort:
            openingSpecs[OP_PORT]['a']=sRef.properties.wallPB
        else:
            openingSpecs[OP_PORT]['a']=False

        if sRef.properties.SlotV:
            openingSpecs[OP_SLOT]['a']=sRef.properties.wallEB
        else:
            openingSpecs[OP_SLOT]['a']=False

        if sRef.properties.Crenel:
            openingSpecs[OP_CREN]['a']=sRef.properties.wallCB
        else:
            openingSpecs[OP_CREN]['a']=False

        wallHoles=openList(sRef)
        # set steps/shelf extrusion options for this wall... 
        if sRef.properties.Step1 and sRef.properties.wallSB:
            wallSteps=True
        if sRef.properties.Shelf1 and sRef.properties.wallBB:
            wallShelf=True
# end first floor only ;)

        wallExtOpts[0]=wallSteps
        wallExtOpts[1]=wallShelf

        objLoc[0]=objScene.cursor_location.x
        if sRef.properties.cXTest and sRef.properties.CTunnel:
            objLoc[1]=WobjY/2
        else:
            objLoc[1]=WobjY
        objLoc[1]-=yMod/2 # offset for disc

        # generate wall...
        cBackObj=makeWallObj(sRef,objScene,objLoc,objName,blockArea,wallHoles,wallExtOpts,objMat)
        cBackObj.parent=objParent # Connect to parent

        cBackObj.select=True # must select to rotate 
        bpy.ops.transform.rotate(value=cPie,constraint_axis=[False,False,True])
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
        cBackObj.select=False # de-select after rotate else joined with others...

####################
    # set block "area": height, width, depth, and spacing for side walls...
    blockArea=[WobjH,WobjY-segWidth*2,WobjD,sRef.properties.blockZ,sRef.properties.blockHVar,sRef.properties.Grout]
#    blockArea=[WobjH,WobjY-segWidth,WobjD,sRef.properties.blockZ,sRef.properties.blockHVar,sRef.properties.Grout]
#    blockArea=[WobjH,WobjY,WobjD,sRef.properties.blockZ,sRef.properties.blockHVar,sRef.properties.Grout]
    # rowprocessing() side walls
    dims['s'] = -midWallD
    dims['e'] = midWallD
####################

    if objSides[1]: # Make "Left" wall.
        objName=OBJ_L+str(objLvl)

        wallSteps=False
        wallShelf=False
        wallHoles=[]

#        if not objLvl: # only for first lvl...
        if sRef.properties.wallDoor:
            openingSpecs[OP_DOOR]['a']=sRef.properties.wallDL
        else:
            openingSpecs[OP_DOOR]['a']=False

        if sRef.properties.wallPort:
            openingSpecs[OP_PORT]['a']=sRef.properties.wallPL
        else:
            openingSpecs[OP_PORT]['a']=False

        if sRef.properties.SlotV:
            openingSpecs[OP_SLOT]['a']=sRef.properties.wallEL
        else:
            openingSpecs[OP_SLOT]['a']=False

        if sRef.properties.Crenel:
            openingSpecs[OP_CREN]['a']=sRef.properties.wallCL
        else:
            openingSpecs[OP_CREN]['a']=False

        wallHoles=openList(sRef)
        # set steps/shelf extrusion options for this wall...
        if sRef.properties.Step1 and sRef.properties.wallSL:
           wallSteps=True
        if sRef.properties.Shelf1 and sRef.properties.wallBL:
           wallShelf=True
# end first floor only ;)

        wallExtOpts[0]=wallSteps
        wallExtOpts[1]=wallShelf

        if sRef.properties.cXTest and sRef.properties.CTunnel:
            objLoc[0]=0
        else:
            objLoc[0]=-midWallW

        if floorDisc: # make a disc shaped floor
            objLoc[1]=0
        else:
            objLoc[1]=midWallD-(WobjD/2)
#        objLoc[1]=midWallD

        # generate wall...
        cSideLObj=makeWallObj(sRef,objScene,objLoc,objName,blockArea,wallHoles,wallExtOpts,objMat)

        cSideLObj.select=True # must select to rotate 
        if sRef.properties.cXTest and sRef.properties.CTunnel:
# rotate 90 horizontal, ccw...
            bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[False,False,True])
        else:
# rotate 90 horizontal, cw...
            bpy.ops.transform.rotate(value=-cPieHlf,constraint_axis=[False,False,True])
# rotate 90 forward (face plant)...
#            bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[True,False,False])
# rotate 90 cw along side
#            bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[False,True,False])
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
        cSideLObj.select=False # deselect after rotate else joined with others...

        cSideLObj.parent=objParent # Connect to parent

####################
    if objSides[3]: # Make "Right" wall.
        objName=OBJ_R+str(objLvl)

        wallSteps=False
        wallShelf=False
        wallHoles=[]

#        if not objLvl: # only for first lvl...
        if sRef.properties.wallDoor:
            openingSpecs[OP_DOOR]['a']=sRef.properties.wallDR
        else:
            openingSpecs[OP_DOOR]['a']=False

        if sRef.properties.wallPort:
            openingSpecs[OP_PORT]['a']=sRef.properties.wallPR
        else:
            openingSpecs[OP_PORT]['a']=False

        if sRef.properties.SlotV:
            openingSpecs[OP_SLOT]['a']=sRef.properties.wallER
        else:
            openingSpecs[OP_SLOT]['a']=False

        if sRef.properties.Crenel:
            openingSpecs[OP_CREN]['a']=sRef.properties.wallCR
        else:
            openingSpecs[OP_CREN]['a']=False

        wallHoles=openList(sRef)
        # set steps/shelf extrusion options for this wall...
        if sRef.properties.Step1 and sRef.properties.wallSR:
           wallSteps=True
        if sRef.properties.Shelf1 and sRef.properties.wallBR:
           wallShelf=True
# end first floor only ;)

        wallExtOpts[0]=wallSteps
        wallExtOpts[1]=wallShelf

        if sRef.properties.cXTest and sRef.properties.CTunnel:
            objLoc[0]=0
        else:
            objLoc[0]=midWallW

        if floorDisc: # make a disc shaped floor
            objLoc[1]=0
        else:
            objLoc[1]=midWallD-(WobjD/2)

        cSideRObj=makeWallObj(sRef,objScene,objLoc,objName,blockArea,wallHoles,wallExtOpts,objMat)
#        objScene.objects.active=cSideRObj

        cSideRObj.select=True # must select to rotate 
        if sRef.properties.cXTest and sRef.properties.CTunnel:
# rotate 90 horizontal, cw...
            bpy.ops.transform.rotate(value=-cPieHlf,constraint_axis=[False,False,True])
# rotate 90 horizontal, ccw...
        else:
            bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[False,False,True])
# rotate 90 forward (face plant)...
#        bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[True,False,False])
# rotate 90 cw along side
#        bpy.ops.transform.rotate(value=cPieHlf,constraint_axis=[False,True,False])
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
        cSideRObj.select=False # deselect after rotate...

        cSideRObj.parent=objParent # Connect to parent


################################################################################

def makeWallObj(sRef,objScene,objLoc,objName,blockArea,openList,wallExtOpts,objMat):

    settings['Steps']=wallExtOpts[0]
    settings['Shelf']=wallExtOpts[1]

    meshVs,meshFs = wallBuild(sRef,wallPlan(sRef,blockArea,openList),openList)

    newMesh=bpy.data.meshes.new(objName)
    newMesh.from_pydata(meshVs,[],meshFs)
#    newMesh.update(calc_edges=True) # doesn't seem to matter...
    newMesh.materials.append(objMat)

    newObj=bpy.data.objects.new(objName,newMesh)
    newObj.location.x=objLoc[0]
    newObj.location.y=objLoc[1]
    newObj.location.z=objLoc[2]

    objScene.objects.link(newObj) # must do for generation/rotation

    return newObj


########################
##
# objArea[leftX,rightX,zBase,zTop,0,yDepth]
# objDiv will subdivide plane based on sizing;
#  - see MakeABlock(objArea,objDiv) for details.
#
def makePlaneObj(objName,objArea,objMat,objDiv):
    objVs=[]
    objFs=[]

    objVs,objFs=MakeABlock(objArea,objDiv)

    objMesh=bpy.data.meshes.new(objName)
    objMesh.from_pydata(objVs,[],objFs)
    objMesh.update()
#    objMesh.update(calc_edges=True) # doesn't seem to matter...
    objMesh.materials.append(objMat)

    newObj=bpy.data.objects.new(objName,objMesh)
    newObj.location=bpy.context.scene.cursor_location

    return newObj


################################################################################
################
########################
##
#
# Blocks module/script inclusion
# - to be reduced significantly.
##
# Module notes:
#
# consider removing wedge crit for small "c" and "cl" values
# wrap around for openings on radial stonework?
# repeat for opening doesn't distribute evenly when radialized
#  - see wrap around note above.
# if opening width == indent*2 the edge blocks fail (row of blocks cross opening).
# if block width variance is 0, and edging is on, right edge blocks create a "vertical seam".
#
##
#######################
################
################################################################################
##


###################################
#
# create lists of blocks.
#
# blockArea defines the "space" (vertical, horizontal, depth) to fill,
#  and provides block height, variation, and gap/grout. May affect "door" opening.
#
# holeList identifies "openings" in area.
#
# Returns: list of rows.
#  rows = [[center height,row height,edge offset],[...]]
#
def wallPlan(sRef,blockArea,holeList):

    rows = []

    blockAreaZ=blockArea[0]
    blockAreaX=blockArea[1]
    blockAreaY=blockArea[2]
    blockHMax=blockArea[3]
    blockHVarW=blockArea[4]
    blockGap=blockArea[5]
# this is wrong! should be...?
    blockHMin=BLOCK_MIN+blockGap

    # no variation for slopes so walls match curvature
    if sRef.properties.cXTest:
        if sRef.properties.wallSlope or sRef.properties.CTunnel:
            blockHVarW=0

    rowHMin=blockHMin
# alternate rowHMin=blockHMax-blockHVarW+blockGap

    # splits are a row division, for openings
    splits=[0] # split bottom row
    #add a split for each critical point on each opening
    for hole in holeList: splits += hole.crits()
    #and, a split for the top row
    splits.append(blockAreaZ)
    splits.sort() # needed?

    #divs are the normal old row divisions, add them between the top and bottom split
# what's with "[1:-1]" at end????
    divs = fill(splits[0],splits[-1],blockHMax,blockHMin,blockHVarW)[1:-1]

    #remove the divisions that are too close to the splits, so we don't get tiny thin rows
    for i in range(len(divs)-1,-1,-1):
        for j in range(len(splits)):
            if abs(divs[i] - splits[j]) < rowHMin:
                del(divs[i])
                break

    #now merge the divs and splits lists
    divs += splits
    divs.sort()

    #trim the rows to the bottom and top of the wall
    if divs[0] < 0: divs[:1] = []
    if divs[-1] > blockAreaZ: divs[-1:] = []

    # process each row
    divCount = len(divs)-1 # number of divs to check
    divCheck = 0 # current div entry

    while divCheck < divCount:
        RowZ = (divs[divCheck]+divs[divCheck+1])/2
        RowHeight = divs[divCheck+1]-divs[divCheck]-blockGap
        rowEdge = settings['eoff']*(fmod(divCheck,2)-0.5)

        if RowHeight < rowHMin: # skip row if too shallow
            del(divs[divCheck+1]) # delete next div entry
            divCount -= 1 # Adjust count for removed div entry.
            continue

#        rows.append(rowOb(RowZ, RowHeight, rowEdge))
        rows.append(rowOb(RowZ, RowHeight, rowEdge))

        divCheck += 1 # on to next div entry

    # set up opening object to handle the edges of the wall
    WallBoundaries = OpeningInv((dims['s'] + dims['e'])/2,blockAreaZ/2,blockAreaX,blockAreaZ)

    #Go over each row in the list, set up edge blocks and block sections
    for rownum in range(len(rows)):
        rowProcessing(rows[rownum], holeList, WallBoundaries)

    return rows


################################################################################
#
# Build the wall, based on rows, "holeList", and parameters;
#     geometry for the blocks, arches, steps, platforms...
#
# Return: verts and faces for wall object.
#
def wallBuild(sRef,rows,holeList):

    wallVs=[]
    wallFs=[]

    AllBlocks = []

    # create local references for anything that's used more than once...
    rowCount=len(rows)

    wallTop=rows[rowCount-1].z
#    wallTop=sRef.properties.wallH
    wallTop2=wallTop*2

    wallDome=settings['Dome']
    wallSlope=settings['Slope']

    blockWidth=sRef.properties.blockX

    blockGap=sRef.properties.Grout
    halfGrout = blockGap/2 # half grout for block size modifier
    blockHMin=BLOCK_MIN+blockGap

    blockDhalf=settings['d']/2 # offset by half block depth to match UI setting

    for rowidx in range(rowCount): # add blocks for each row.
        rows[rowidx].FillBlocks()

    if sRef.properties.MergeBlock: # merge (vertical) blocks in close proximity...
        blockSpace=blockGap
        for rowidx in range(rowCount-1):
            if wallDome:
                blockSpace=blockGap/(wallTop*sin(abs(rows[rowidx].z)*cPie/wallTop2))
#            else: blockSpace=blockGap/(abs(rows[rowidx].z)) # make it flat

            idxThis = len(rows[rowidx].BlocksNorm[:]) - 1
            idxThat = len(rows[rowidx+1].BlocksNorm[:]) - 1

            while True:
                # end loop when either array idx wraps
                if idxThis < 0 or idxThat < 0: break

                blockThis = rows[rowidx].BlocksNorm[idxThis]
                blockThat = rows[rowidx+1].BlocksNorm[idxThat]

                cx, cz, cw, ch, cd = blockThis[:5]
                ox, oz, ow, oh, od = blockThat[:5]

                if (abs(cw - ow) < blockSpace) and (abs(cx - ox) < blockSpace) :
                    if cw > ow: BlockW = ow
                    else: BlockW = cw

                    AllBlocks.append([(cx+ox)/2,(cz+oz+(oh-ch)/2)/2,BlockW,abs(cz-oz)+(ch+oh)/2,(cd+od)/2,None])

                    rows[rowidx].BlocksNorm.pop(idxThis)
                    rows[rowidx+1].BlocksNorm.pop(idxThat)
                    idxThis -= 1
                    idxThat -= 1

                elif cx > ox: idxThis -= 1
                else: idxThat -= 1


    if settings['Shelf']: # Add blocks to create a "shelf/platform".
# Does not account for openings (crosses gaps - which is a good thing)

        # Use wall block settings for shelf
        shelfBW=blockWidth
        shelfBWVar=settings['wv']
        shelfBH=sRef.properties.blockZ

        ShelfLft = sRef.properties.ShelfX
        ShelfBtm = sRef.properties.ShelfZ
        ShelfRt = ShelfLft + sRef.properties.ShelfW
        ShelfTop = ShelfBtm + sRef.properties.ShelfH
        ShelfThk = sRef.properties.ShelfD
        ShelfThk2= ShelfThk*2 # double-depth to position at cursor.

        if sRef.properties.ShelfOut: # place blocks on outside of wall
            ShelfOffsets = [[0,-blockDhalf,0],[0,-ShelfThk,0],[0,-blockDhalf,0],[0,-ShelfThk,0],[0,-blockDhalf,0],[0,-ShelfThk,0],[0,-blockDhalf,0],[0,-ShelfThk,0]]
        else:
            ShelfOffsets = [[0,ShelfThk,0],[0,blockDhalf,0],[0,ShelfThk,0],[0,blockDhalf,0],[0,ShelfThk,0],[0,blockDhalf,0],[0,ShelfThk,0],[0,blockDhalf,0]]

        while ShelfBtm < ShelfTop: # Add blocks for each "shelf row" in area
            divs = fill(ShelfLft, ShelfRt, shelfBW, shelfBW, shelfBWVar)

            for i in range(len(divs)-1): # add blocks for row divisions
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-halfGrout
                AllBlocks.append([ThisBlockx, ShelfBtm, ThisBlockw, shelfBH, ShelfThk2, ShelfOffsets])

            ShelfBtm += shelfBH + halfGrout # moving up to next row...

# Set shelf material/color... on wish list.


    if settings['Steps']: # Add blocks to create "steps".
# Does not account for openings (crosses gaps - which is a good thing)

        stepsFill=settings['StepsB']
        steps2Left=settings['StepsL']

        # step block "filler" by wall block settings.
        stepFW=blockWidth
        StepFWVar=settings['wv']

        StepXMod = sRef.properties.StepT # step tread, also sets basic block size.
        StepZMod = sRef.properties.StepV

        StepLft = sRef.properties.StepX
        StepWide = sRef.properties.StepW
        StepRt = StepLft + StepWide
        StepBtm = sRef.properties.StepZ + StepZMod/2 # Start offset for centered blocks
        StepTop = StepBtm + sRef.properties.StepH

        StepThk = sRef.properties.StepD
        StepThk2=StepThk*2 # use double-depth due to offsets to position at cursor.

        # Use "corners" to adjust steps so not centered on depth.
        # steps at cursor so no gaps between steps and wall face due to wall block depth.
        if settings['StepsO']: # place blocks on outside of wall
            StepOffsets = [[0,-blockDhalf,0],[0,-StepThk,0],[0,-blockDhalf,0],[0,-StepThk,0],[0,-blockDhalf,0],[0,-StepThk,0],[0,-blockDhalf,0],[0,-StepThk,0]]
        else:
            StepOffsets = [[0,StepThk,0],[0,blockDhalf,0],[0,StepThk,0],[0,blockDhalf,0],[0,StepThk,0],[0,blockDhalf,0],[0,StepThk,0],[0,blockDhalf,0]]

        # Add steps for each "step row" in area (neg width is interesting but prevented)
        while StepBtm < StepTop and StepWide > 0:

            # Make blocks for each step row - based on rowOb:fillblocks
            if stepsFill:
                divs = fill(StepLft, StepRt, StepXMod, stepFW, StepFWVar)

                #loop through the row divisions, adding blocks for each one
                for i in range(len(divs)-1):
                    ThisBlockx = (divs[i]+divs[i+1])/2
                    ThisBlockw = divs[i+1]-divs[i]-halfGrout

                    AllBlocks.append([ThisBlockx, StepBtm, ThisBlockw, StepZMod, StepThk2, StepOffsets])
            else: # "cantilevered steps"
                if steps2Left:
                    stepStart=StepRt-StepXMod
                else:
                    stepStart=StepLft

                AllBlocks.append([stepStart, StepBtm, StepXMod, StepZMod, StepThk2, StepOffsets])

            StepBtm += StepZMod + halfGrout # moving up to next row...
            StepWide -= StepXMod # reduce step width

            # adjust side limit depending on direction of steps
            if steps2Left:
                StepRt-=StepXMod # move from right
            else:
                StepLft+=StepXMod # move from left

    for row in rows: # Copy all the blocks out of the rows
        AllBlocks+=row.BlocksEdge
        AllBlocks+=row.BlocksNorm

    # make individual blocks for each block specified in the plan

    subDivision=settings['sdv']

    for block in AllBlocks:
        x,z,w,h,d,corners = block
        holeW2=w/2

        geom = MakeABlock([x-holeW2, x+holeW2, z-h/2, z+h/2, -d/2, d/2], subDivision, len(wallVs), corners)
        wallVs += geom[0]
        wallFs += geom[1]

    # make Arches for every opening specified in the plan.
    for hole in holeList:
        # lower arch stones
        if hole.vl > 0 and hole.rtl > blockHMin:
            archGeneration(hole, wallVs, wallFs, -1)

        # top arch stones
        if hole.v > 0 and hole.rt > blockHMin:
            archGeneration(hole, wallVs, wallFs, 1)

    if wallSlope: # Curve wall, dome shape if "radialized".
        for i,vert in enumerate(wallVs):
            wallVs[i] = [vert[0],(wallTop+vert[1])*cos(vert[2]*cPie/wallTop2),(wallTop+vert[1])*sin(vert[2]*cPie/wallTop2)]

    if wallDome: # Make wall circular, dome if sloped, else disc (flat round).
        for i,vert in enumerate(wallVs):
            wallVs[i] = [vert[2]*cos(vert[0]),vert[2]*sin(vert[0]),vert[1]]

    return wallVs,wallFs


################################################################################
#
# create a list of openings from the general specifications.
#
def openList(sRef):
    boundlist = []

    # initialize variables
    areaStart=dims['s']
    areaEnd=dims['e']

    SetWid = sRef.properties.blockX
    wallDisc=settings['Dome']

    for x in openingSpecs:
        if x['a']: # apply opening to object
            # hope this is faster, at least for repeat.
            xOpenW=x['w']
            xOpenX=x['x']
            xOpenZ=x['z']

            if x['n']: # repeat...
                if wallDisc: r1 = xOpenZ
                else: r1 = 1

                if xOpenX > (xOpenW + SetWid): spacing = xOpenX/r1
                else: spacing = (xOpenW + SetWid)/r1

                minspacing = (xOpenW + SetWid)/r1

                divs = fill(areaStart,areaEnd,spacing,minspacing,center=1)

                for posidx in range(len(divs)-2):
                    boundlist.append(opening(divs[posidx+1],xOpenZ,xOpenW,x['h'],x['v'],x['t'],x['vl'],x['tl'],x['bvl']))

            else: boundlist.append(opening(xOpenX,xOpenZ,xOpenW,x['h'],x['v'],x['t'],x['vl'],x['tl'],x['bvl']))
            #check for edge overlap?

    return boundlist


################################################################################
#
# fill a linear space with divisions
#
#    objXO: x origin
#    objXL: x limit
#    avedst: the average distance between points
#    mindst: the minimum distance between points
#    dev: the maximum random deviation from avedst
#    center: flag to center the elements in the range, 0 == disabled
#
# returns an ordered list of points, including the end points.
#
def fill(objXO,objXL,avedst,mindst=0.0,dev=0.0,center=0):

    curpos = objXO
    poslist = [curpos] # set starting point

    # Set offset by average spacing, then add blocks (fall through);
    # if not at edge.
    if center:
        curpos += ((objXL-objXO-mindst*2)%avedst)/2+mindst
        if curpos-poslist[-1]<mindst: curpos = poslist[-1]+mindst+random()*dev/2

        # clip to right edge.
        if (objXL-curpos<mindst) or (objXL-curpos< mindst):
            poslist.append(objXL)
            return poslist
        else: poslist.append(curpos)

    # make block edges
    while True:
        curpos += avedst+rndd()*dev
        if curpos-poslist[-1]<mindst:
            curpos = poslist[-1]+mindst+random()*dev/2

        if (objXL-curpos<mindst) or (objXL-curpos< mindst):
            poslist.append(objXL) # close off edges at limit
            return poslist
        else: poslist.append(curpos)


#######################################################################
#
# MakeABlock: Generate block geometry
#  to be made into a square cornered block, subdivided along the length.
#
#  bounds: a list of boundary positions:
#      0:left, 1:right, 2:bottom, 3:top, 4:front, 5:back
#  segsize: the maximum size before subdivision occurs
#  vll: the number of vertexes already in the mesh. len(mesh.verts) should
#          give this number.
#  Offsets: list of coordinate delta values.
#      Offsets are lists, [x,y,z] in
#          [
#          0:left_bottom_back,
#          1:left_bottom_front,
#          2:left_top_back,
#          3:left_top_front,
#          4:right_bottom_back,
#          5:right_bottom_front,
#          6:right_top_back,
#          7:right_top_front,
#          ]
#  FaceExclude: list of faces to exclude from the faces list; see bounds above for indices
#
#  return lists of points and faces.
#
def MakeABlock(bounds, segsize, vll=0, Offsets=None, FaceExclude=[]):

    slices = fill(bounds[0], bounds[1], segsize, segsize, center=1)
    points = []
    faces = []

    if Offsets == None:
        points.append([slices[0],bounds[4],bounds[2]])
        points.append([slices[0],bounds[5],bounds[2]])
        points.append([slices[0],bounds[5],bounds[3]])
        points.append([slices[0],bounds[4],bounds[3]])

        for x in slices[1:-1]:
            points.append([x,bounds[4],bounds[2]])
            points.append([x,bounds[5],bounds[2]])
            points.append([x,bounds[5],bounds[3]])
            points.append([x,bounds[4],bounds[3]])

        points.append([slices[-1],bounds[4],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[2]])
        points.append([slices[-1],bounds[5],bounds[3]])
        points.append([slices[-1],bounds[4],bounds[3]])

    else:
        points.append([slices[0]+Offsets[0][0],bounds[4]+Offsets[0][1],bounds[2]+Offsets[0][2]])
        points.append([slices[0]+Offsets[1][0],bounds[5]+Offsets[1][1],bounds[2]+Offsets[1][2]])
        points.append([slices[0]+Offsets[3][0],bounds[5]+Offsets[3][1],bounds[3]+Offsets[3][2]])
        points.append([slices[0]+Offsets[2][0],bounds[4]+Offsets[2][1],bounds[3]+Offsets[2][2]])

        for x in slices[1:-1]:
            xwt = (x-bounds[0])/(bounds[1]-bounds[0])
            points.append([x+Offsets[0][0]*(1-xwt)+Offsets[4][0]*xwt,bounds[4]+Offsets[0][1]*(1-xwt)+Offsets[4][1]*xwt,bounds[2]+Offsets[0][2]*(1-xwt)+Offsets[4][2]*xwt])
            points.append([x+Offsets[1][0]*(1-xwt)+Offsets[5][0]*xwt,bounds[5]+Offsets[1][1]*(1-xwt)+Offsets[5][1]*xwt,bounds[2]+Offsets[1][2]*(1-xwt)+Offsets[5][2]*xwt])
            points.append([x+Offsets[3][0]*(1-xwt)+Offsets[7][0]*xwt,bounds[5]+Offsets[3][1]*(1-xwt)+Offsets[7][1]*xwt,bounds[3]+Offsets[3][2]*(1-xwt)+Offsets[7][2]*xwt])
            points.append([x+Offsets[2][0]*(1-xwt)+Offsets[6][0]*xwt,bounds[4]+Offsets[2][1]*(1-xwt)+Offsets[6][1]*xwt,bounds[3]+Offsets[2][2]*(1-xwt)+Offsets[6][2]*xwt])

        points.append([slices[-1]+Offsets[4][0],bounds[4]+Offsets[4][1],bounds[2]+Offsets[4][2]])
        points.append([slices[-1]+Offsets[5][0],bounds[5]+Offsets[5][1],bounds[2]+Offsets[5][2]])
        points.append([slices[-1]+Offsets[7][0],bounds[5]+Offsets[7][1],bounds[3]+Offsets[7][2]])
        points.append([slices[-1]+Offsets[6][0],bounds[4]+Offsets[6][1],bounds[3]+Offsets[6][2]])

    faces.append([vll,vll+3,vll+2,vll+1])

    for x in range(len(slices)-1):
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll+1,vll+5,vll+4])
        vll+=1
        faces.append([vll,vll-3,vll+1,vll+4])
        vll+=1

    faces.append([vll,vll+1,vll+2,vll+3])

    return points, faces


#
#For generating Keystone Geometry
def MakeAKeystone(xpos, width, zpos, ztop, zbtm, thick, bevel, vll=0, FaceExclude=[], xBevScl=1):
    __doc__ = """\
    MakeAKeystone returns lists of points and faces to be made into a square cornered keystone, with optional bevels.
    xpos: x position of the centerline
    width: x width of the keystone at the widest point (discounting bevels)
    zpos: z position of the widest point
    ztop: distance from zpos to the top
    zbtm: distance from zpos to the bottom
    thick: thickness
    bevel: the amount to raise the back vertex to account for arch beveling
    vll: the number of vertexes already in the mesh. len(mesh.verts) should give this number
    faceExclude: list of faces to exclude from the faces list.  0:left, 1:right, 2:bottom, 3:top, 4:back, 5:front
    xBevScl: how much to divide the end (+- x axis) bevel dimensions.  Set to current average radius to compensate for angular distortion on curved blocks
    """

    points = []
    faces = []
    faceinclude = [1 for x in range(6)]
    for x in FaceExclude: faceinclude[x]=0
    Top = zpos + ztop
    Btm = zpos - zbtm
    Wid = width/2.
    Thk = thick/2.

    # The front top point
    points.append([xpos, Thk, Top])
    # The front left point
    points.append([xpos-Wid, Thk, zpos])
    # The front bottom point
    points.append([xpos, Thk, Btm])
    # The front right point
    points.append([xpos+Wid, Thk, zpos])

    MirrorPoints = []
    for i in points:
        MirrorPoints.append([i[0],-i[1],i[2]])
    points += MirrorPoints
    points[6][2] += bevel

    faces.append([3,2,1,0])
    faces.append([4,5,6,7])
    faces.append([4,7,3,0])
    faces.append([5,4,0,1])
    faces.append([6,5,1,2])
    faces.append([7,6,2,3])
    # Offset the vertex numbers by the number of verticies already in the list
    for i in range(len(faces)):
        for j in range(len(faces[i])): faces[i][j] += vll

    return points, faces


#class openings in the wall
class opening:
    __doc__ = """\
    This is the class for holding the data for the openings in the wall.
    It has methods for returning the edges of the opening for any given position value,
    as well as bevel settings and top and bottom positions.
    It stores the 'style' of the opening, and all other pertinent information.
    """
    # x = 0. # x position of the opening
    # z = 0. # x position of the opening
    # w = 0. # width of the opening
    # h = 0. # height of the opening
    r = 0  # top radius of the arch (derived from 'v')
    rl = 0 # lower radius of the arch (derived from 'vl')
    rt = 0 # top arch thickness
    rtl = 0# lower arch thickness
    ts = 0 # Opening side thickness, if greater than average width, replaces it.
    c = 0  # top arch corner position (for low arches), distance from the top of the straight sides
    cl = 0 # lower arch corner position (for low arches), distance from the top of the straight sides
    # form = 0 # arch type (unused for now)
    # b = 0. # back face bevel distance, like an arrow slit
    v = 0. # top arch height
    vl = 0.# lower arch height
    # variable "s" is used for "side" in the "edge" function.
    # it is a signed int, multiplied by the width to get + or - of the center

    def btm(self):
        if self.vl <= self.w/2 : return self.z-self.h/2-self.vl-self.rtl
        else: return self.z - sqrt((self.rl+self.rtl)**2 - (self.rl - self.w/2 )**2)  - self.h/2


    def top(self):
        if self.v <= self.w/2 : return self.z+self.h/2+self.v+self.rt
        else: return sqrt((self.r+self.rt)**2 - (self.r - self.w/2 )**2) + self.z + self.h/2


    #crits returns the critical split points, or discontinuities, used for making rows
    def crits(self):
        critlist = []
        if self.vl>0: # for lower arch
            # add the top point if it is pointed
            #if self.vl >= self.w/2.: critlist.append(self.btm())
            if self.vl < self.w/2.:#else: for low arches, with wedge blocks under them
                #critlist.append(self.btm())
                critlist.append(self.z-self.h/2 - self.cl)

        if self.h>0: # if it has a height, append points at the top and bottom of the main square section
            critlist += [self.z-self.h/2,self.z+self.h/2]
        else:  # otherwise, append just one in the center
            critlist.append(self.z)

        if self.v>0:  # for the upper arch
            if self.v < self.w/2.: # add the splits for the upper wedge blocks, if needed
                critlist.append(self.z+self.h/2 + self.c)
                #critlist.append(self.top())
            #otherwise just add the top point, if it is pointed
            #else: critlist.append(self.top())

        return critlist

    #
    # get the side position of the opening.
    # ht is the z position; s is the side: 1 for right, -1 for left
    # if the height passed is above or below the opening, return None
    #
    def edgeS(edgeParms, ht, s):

        wallTopZ=dims['t']
        wallHalfH=edgeParms.h/2
        wallHalfW=edgeParms.w/2
        wallBase=edgeParms.z

        # set the row radius: 1 for standard wall (flat)
        if settings['Dome']:
            if settings['Slope']: r1 = abs(wallTopZ*sin(ht*cPie/(wallTopZ*2)))
            else: r1 = abs(ht)
        else: r1 = 1

        #Go through all the options, and return the correct value
        if ht < edgeParms.btm(): #too low
            return None
        elif ht > edgeParms.top(): #too high
            return None


        # in this range, pass the lower arch info
        elif ht <= wallBase-wallHalfH-edgeParms.cl:
            if edgeParms.vl > wallHalfW:
                circVal = circ(ht-wallBase+wallHalfH,edgeParms.rl+edgeParms.rtl)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*(wallHalfW-edgeParms.rl+circVal)/r1
            else:
                circVal = circ(ht-wallBase+wallHalfH+edgeParms.vl-edgeParms.rl,edgeParms.rl+edgeParms.rtl)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*circVal/r1

        #in this range, pass the top arch info
        elif ht >= wallBase+wallHalfH+edgeParms.c:
            if edgeParms.v > wallHalfW:
                circVal = circ(ht-wallBase-wallHalfH,edgeParms.r+edgeParms.rt)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*(wallHalfW-edgeParms.r+circVal)/r1
            else:
                circVal = circ(ht-(wallBase+wallHalfH+edgeParms.v-edgeParms.r),edgeParms.r+edgeParms.rt)
                if circVal == None:
                    return None
                else: return edgeParms.x + s*circVal/r1

        #in this range pass the lower corner edge info
        elif ht <= wallBase-wallHalfH:
            d = sqrt(edgeParms.rtl**2 - edgeParms.cl**2)
            if edgeParms.cl > edgeParms.rtl/sqrt(2.): return edgeParms.x + s*(wallHalfW + (wallBase - wallHalfH - ht)*d/edgeParms.cl)/r1
            else: return edgeParms.x + s*( wallHalfW + d )/r1

        #in this range pass the upper corner edge info
        elif ht >= wallBase+wallHalfH:
            d = sqrt(edgeParms.rt**2 - edgeParms.c**2)
            if edgeParms.c > edgeParms.rt/sqrt(2.): return edgeParms.x + s*(wallHalfW + (ht - wallBase - wallHalfH )*d/edgeParms.c)/r1
            else: return edgeParms.x + s*( wallHalfW + d )/r1

        #in this range, pass the middle info (straight sides)
        else: return edgeParms.x + s*wallHalfW/r1


    # get the top or bottom of the opening
    # ht is the x position; archSide: 1 for top, -1 for bottom
    #
    def edgeV(self, ht, archSide):
        wallTopZ=dims['t']
        dist = abs(self.x-ht)

        def radialAdjust(dist, sideVal): # adjust distance and for radial geometry.
            if settings['Dome']:
                if settings['Slope']:
                    dist = dist * abs(wallTopZ*sin(sideVal*cPie/(wallTopZ*2)))
                else:
                    dist = dist * sideVal
            return dist

        if archSide > 0 : #check top down
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.top())

            #no arch on top, flat
            if not self.r: return self.z+self.h/2

            #pointed arch on top
            elif self.v > self.w/2:
                circVal = circ(dist-self.w/2+self.r,self.r+self.rt)
                if circVal == None:
                    return 0.0
                else: return self.z+self.h/2+circVal

            #domed arch on top
            else:
                circVal = circ(dist,self.r+self.rt)
                if circVal == None:
                    return 0.0
                else: return self.z+self.h/2+self.v-self.r+circVal

        else: #check bottom up
            #hack for radialized masonry, import approx Z instead of self.top()
            dist = radialAdjust(dist, self.btm())

            #no arch on bottom
            if not self.rl: return self.z-self.h/2

            #pointed arch on bottom
            elif self.vl > self.w/2:
                circVal = circ(dist-self.w/2+self.rl,self.rl+self.rtl)
                if circVal == None:
                    return 0.0
                else: return self.z-self.h/2-circVal

            #old conditional? if (dist-self.w/2+self.rl)<=(self.rl+self.rtl):
            #domed arch on bottom
            else:
                circVal = circ(dist,self.rl+self.rtl) # dist-self.w/2+self.rl
                if circVal == None:
                    return 0.0
                else: return self.z-self.h/2-self.vl+self.rl-circVal

    #
    def edgeBev(self, ht):
        wallTopZ=dims['t']
        if ht > (self.z + self.h/2): return 0.0
        if ht < (self.z - self.h/2): return 0.0
        if settings['Dome']:
            if settings['Slope']: r1 = abs(wallTopZ*sin(ht*cPie/(wallTopZ*2)))
            else: r1 = abs(ht)
        else: r1 = 1
        bevel = self.b / r1
        return bevel
#
##
#

    def __init__(self, xpos, zpos, width, height, archHeight=0, archThk=0,
                 archHeightLower=0, archThkLower=0, bevel=0, edgeThk=0):
        self.x = float(xpos)
        self.z = float(zpos)
        self.w = float(width)
        self.h = float(height)
        self.rt = archThk
        self.rtl = archThkLower
        self.v = archHeight
        self.vl = archHeightLower

        #find the upper arch radius
        if archHeight >= width/2:
            # just one arch, low long
            self.r = (self.v**2)/self.w + self.w/4
        elif archHeight <= 0:
            # No arches
            self.r = 0
            self.v = 0
        else:
            # Two arches
            self.r = (self.w**2)/(8*self.v) + self.v/2.
            self.c = self.rt*cos(atan(self.w/(2*(self.r-self.v))))

        #find the lower arch radius
        if archHeightLower >= width/2:
            self.rl = (self.vl**2)/self.w + self.w/4
        elif archHeightLower <= 0:
            self.rl = 0
            self.vl = 0
        else:
            self.rl = (self.w**2)/(8*self.vl) + self.vl/2.
            self.cl = self.rtl*cos(atan(self.w/(2*(self.rl-self.vl))))

        #self.form = something?
        self.b = float(bevel)
        self.ts = edgeThk
#
#
#class for the whole wall boundaries; a sub-class of "opening"
class OpeningInv(opening):
    #this is supposed to switch the sides of the opening
    #so the wall will properly enclose the whole wall.

   def edgeS(self, ht, s):
       return opening.edgeS(self, ht, -s)

   def edgeV(self, ht, s):
       return opening.edgeV(self, ht, -s)

#class rows in the wall
class rowOb:
    __doc__ = """\
    This is the class for holding the data for individual rows of blocks.
    each row is required to have some edge blocks, and can also have
    intermediate sections of "normal" blocks.
    """

    #z = 0.
    #h = 0.
    radius = 1
    rowEdge = 0

    def FillBlocks(self):
        wallTopZ=dims['t']

        # Set the radius variable, in the case of radial geometry
        if settings['Dome']:
            if settings['Slope']: self.radius = wallTopZ*(sin(self.z*cPie/(wallTopZ*2)))
            else: self.radius = self.z

        #initialize internal variables from global settings
        SetH = settings['h']
# no HVar?
        SetWid = settings['w']
        SetWidVar = settings['wv']
        SetGrt = settings['g']
        SetDepth = settings['d']
        SetDepthVar = settings['dv']

        # height weight, make shorter rows have narrower blocks, and vice-versa
        rowHWt=((self.h/SetH-1)*ROW_H_WEIGHT+1)

        # set variables for persistent values: loop optimization, readability, single ref for changes.
        avgDist = rowHWt*SetWid/self.radius
        minDist = SetWid/self.radius
        deviation = rowHWt*SetWidVar/self.radius
        grtOffset = SetGrt/(2*self.radius)

        # init loop variables that may change...
        blockGap=SetGrt/self.radius
        ThisBlockHeight = self.h
        ThisBlockDepth = SetDepth+(rndd()*SetDepthVar)

        for segment in self.RowSegments:
            divs = fill(segment[0]+grtOffset, segment[1]-grtOffset, avgDist, minDist, deviation)

            # loop through the divisions, adding blocks for each one
            for i in range(len(divs)-1):
                ThisBlockx = (divs[i]+divs[i+1])/2
                ThisBlockw = divs[i+1]-divs[i]-blockGap

                self.BlocksNorm.append([ThisBlockx, self.z, ThisBlockw, ThisBlockHeight, ThisBlockDepth, None])

                if SetDepthVar: # vary depth
                    ThisBlockDepth = SetDepth+(rndd()*SetDepthVar)

    def __init__(self,centerheight,rowheight,rowEdge=0):
        self.z = float(centerheight)
        self.h = float(rowheight)
        self.rowEdge = float(rowEdge)

#THIS INITILIZATION IS IMPORTANT!  OTHERWISE ALL OBJECTS WILL HAVE THE SAME LISTS!
        self.BlocksEdge = []
        self.RowSegments = []
        self.BlocksNorm = []

#
def arch(ra,rt,x,z, archStart, archEnd, bevel, bevAngle, vll):
    __doc__ = """\
    Makes a list of faces and vertexes for arches.
    ra: the radius of the arch, to the center of the bricks
    rt: the thickness of the arch
    x: x center location of the circular arc, as if the arch opening were centered on x = 0
    z: z center location of the arch
    anglebeg: start angle of the arch, in radians, from vertical?
    angleend: end angle of the arch, in radians, from vertical?
    bevel: how much to bevel the inside of the arch.
    vll: how long is the vertex list already?
    """
    avlist = []
    aflist = []

    #initialize internal variables for global settings
    SetH = settings['h']
    SetWid = settings['w']
    SetWidVar = settings['wv']
    SetGrt = settings['g']
    SetDepth = settings['d']
    SetDepthVar = settings['dv']
    wallTopZ=dims['t']

    wallDome=settings['Dome']

    ArchInner = ra-rt/2
    ArchOuter = ra+rt/2-SetGrt

    DepthBack = -SetDepth/2-rndc()*SetDepthVar
    DepthFront = SetDepth/2+rndc()*SetDepthVar

# there's something wrong here...
    if wallDome: subdivision = settings['sdv']
    else: subdivision = 0.12

    blockGap=SetGrt/(2*ra) # grout offset
    # set up the offsets, it will be the same for every block
    offsets = ([[0]*2 + [bevel]] + [[0]*3]*3)*2

    #make the divisions in the "length" of the arch
    divs = fill(archStart, archEnd, settings['w']/ra, settings['w']/ra, settings['wv']/ra)

    for i in range(len(divs)-1):
         # modify block offsets for bevel.
        if i == 0:
            ThisOffset = offsets[:]
            pointsToAffect=(0,2,3)

            for num in pointsToAffect:
                offsets[num]=ThisOffset[num][:]
                offsets[num][0]+=bevAngle
        elif i == len(divs)-2:
            ThisOffset=offsets[:]
            pointsToAffect=(4,6,7)

            for num in pointsToAffect:
                offsets[num]=ThisOffset[num][:]
                offsets[num][0]-=bevAngle
        else:
            ThisOffset = offsets

        geom = MakeABlock([divs[i]+blockGap, divs[i+1]-blockGap, ArchInner, ArchOuter, DepthBack, DepthFront],
                          subdivision, len(avlist) + vll, ThisOffset, [])

        avlist += geom[0]
        aflist += geom[1]

        if SetDepthVar: # vary depth
            DepthBack = -SetDepth/2-rndc()*SetDepthVar
            DepthFront = SetDepth/2+rndc()*SetDepthVar

    for i,vert in enumerate(avlist):
        v0 = vert[2]*sin(vert[0]) + x
        v1 = vert[1]
        v2 = vert[2]*cos(vert[0]) + z

        if wallDome:
            r1 = wallTopZ*(sin(v2*cPie/(wallTopZ*2)))
#            if settings['Slope']: r1 = wallTopZ*(sin(v2*cPie/(wallTopZ*2)))
#            else: r1 = v2 # disc
            v0 = v0/r1

        avlist[i] = [v0,v1,v2]

    return (avlist,aflist)


#################################################################
#
# Make wedge blocks for openings.
#
#  example:
#   wedgeBlocks(row, LeftWedgeEdge, LNerEdge, LEB, r1)
#   wedgeBlocks(row, RNerEdge, RightWedgeEdge, rSide, r1)
#
def wedgeBlocks(row, opening, leftPos, rightPos, edgeSide, r1):

    wedgeWRad=settings['w']/r1

    wedgeEdges = fill(leftPos, rightPos, wedgeWRad, wedgeWRad, settings['wv']/r1)

    blockDepth=settings['d']
    blockDepthV=settings['dv']
    blockGap=settings['g']/r1

    for i in range(len(wedgeEdges)-1):
        x = (wedgeEdges[i+1] + wedgeEdges[i])/2
        w = wedgeEdges[i+1] - wedgeEdges[i] - blockGap
        halfBW=w/2

        ThisBlockDepth = blockDepth+rndd()*blockDepthV

        LVert=-((row.z-((row.h/2)*edgeSide))-opening.edgeV(x-halfBW,edgeSide))
#        LVert =  -( row.z - (row.h/2)*edgeSide - (opening.edgeV(x-halfBW,edgeSide)))
        RightVertOffset = -( row.z - (row.h/2)*edgeSide - opening.edgeV(x+halfBW,edgeSide) )

        #Wedges are on top = Voff, blank, Voff, blank
        #Wedges are on btm = blank, Voff, blank, Voff
        ThisBlockOffsets = [[0,0,LVert]]*2 + [[0]*3]*2 + [[0,0,RightVertOffset]]*2
        # Instert or append "blank" for top or bottom wedges.
        if edgeSide == 1: ThisBlockOffsets = ThisBlockOffsets + [[0]*3]*2
        else: ThisBlockOffsets = [[0]*3]*2 + ThisBlockOffsets

        row.BlocksEdge.append([x,row.z,w,row.h,ThisBlockDepth,ThisBlockOffsets])


############################################################
#
#
    #set end blocks
    #check for openings, record top and bottom of row for right and left of each
    #if both top and bottom intersect create blocks on each edge, appropriate to the size of the overlap
    #if only one side intersects, run fill to get edge positions, but this should never happen
    #
#
def rowProcessing(row, holeList, WallBoundaries):

    if settings['Dome']:# radial stonework sets the row radius
        if settings['Slope']: r1 = abs(dims['t']*sin(row.z*cPie/(dims['t']*2)))
        else: r1 = abs(row.z)
    else: r1 = 1

    # set block working values
    blockWidth=settings['w']
    blockWVar=settings['wv']
    blockDepth=settings['d']
    blockDVar=settings['dv']

    blockGap=settings['g']/r1
    blockHMin=BLOCK_MIN+blockGap

    # set row working values
    rowH=row.h
    rowH2=rowH/2
    rowEdge=row.rowEdge/r1
    rowStart=dims['s']+rowEdge
# shouldn't rowEnd be minus rowEdge?
    rowEnd=dims['e']+rowEdge
    rowTop = row.z+rowH2
    rowBtm = row.z-rowH2

    # left and right wall limits for top and bottom of row.
    edgetop=[[rowStart,WallBoundaries],[rowEnd,WallBoundaries]]
    edgebtm=[[rowStart,WallBoundaries],[rowEnd,WallBoundaries]]

    for hole in holeList:
        #check the top and bottom of the row, looking at the opening from the right
        holeEdge = [hole.edgeS(rowTop, -1), hole.edgeS(rowBtm, -1)]

        # If either one hit the opening, make split points for the side of the opening.
        if holeEdge[0] or holeEdge[1]:
            holeEdge += [hole.edgeS(rowTop, 1), hole.edgeS(rowBtm, 1)]

            # If one of them missed for some reason, set that value to
            # the middle of the opening.
            for i,pos in enumerate(holeEdge):
                if pos == None: holeEdge[i] = hole.x

            # add the intersects to the list of edge points
            edgetop.append([holeEdge[0],hole])
            edgetop.append([holeEdge[2],hole])
            edgebtm.append([holeEdge[1],hole])
            edgebtm.append([holeEdge[3],hole])

    # make the walls in order, sort the intersects.
#  remove edge points that are out of order;
#  else the "oddity" where opening overlap creates blocks inversely.
    edgetop.sort()
    edgebtm.sort()

    # These two loops trim the edges to the limits of the wall.
    # This way openings extending outside the wall don't enlarge the wall.
    while True:
        try:
            if (edgetop[-1][0] > rowEnd) or (edgebtm[-1][0] > rowEnd):
                edgetop[-2:] = []
                edgebtm[-2:] = []
            else: break
        except IndexError: break
    #still trimming the edges...
    while True:
        try:
            if (edgetop[0][0] < rowStart) or (edgebtm[0][0] < rowStart):
                edgetop[:2] = []
                edgebtm[:2] = []
            else: break
        except IndexError: break

    # finally, make edge blocks and rows!

    # Process each section, a pair of points in edgetop,
    # and place the edge blocks and inbetween normal block zones into the row object.

    #maximum distance to span with one block
    MaxWid = (blockWidth+blockWVar)/r1

    for OpnSplitNo in range(int(len(edgetop)/2)):
        lEdgeIndx=2*OpnSplitNo
        rEdgeIndx=lEdgeIndx+1

        leftOpening = edgetop[lEdgeIndx][1]
        rightOpening = edgetop[rEdgeIndx][1]

        #find the difference between the edge top and bottom on both sides
        LTop = edgetop[lEdgeIndx][0]
        LBtm = edgebtm[lEdgeIndx][0]
        RTop = edgetop[rEdgeIndx][0]
        RBtm = edgebtm[rEdgeIndx][0]
        LDiff = LBtm-LTop
        RDiff = RTop-RBtm

        # set side edge limits from top and bottom
        if LDiff > 0: # if furthest edge is top,
            LEB = 1
            LFarEdge = LTop #The furthest edge
            LNerEdge = LBtm #the nearer edge
        else: # furthest edge is bottom
            LEB = -1
            LFarEdge = LBtm
            LNerEdge = LTop

        if RDiff > 0: # if furthest edge is top,
            rSide = 1
            RFarEdge = RTop #The furthest edge
            RNerEdge = RBtm #the nearer edge
        else: # furthest edge is bottom
            rSide = -1
            RFarEdge = RBtm # The furthest edge
            RNerEdge = RTop # the nearer edge

        blockXx=RNerEdge-LNerEdge # The space between the closest edges of the openings in this section of the row
        blockXm=(RNerEdge + LNerEdge)/2 # The mid point between the nearest edges

        #check the left and right sides for wedge blocks
        #find the edge of the correct side, offset for minimum block height.  The LEB decides top or bottom
        ZPositionCheck = row.z + (rowH2-blockHMin)*LEB
#edgeS may return "None"
        LeftWedgeEdge = leftOpening.edgeS(ZPositionCheck,1)

        if (abs(LDiff) > blockWidth) or (not LeftWedgeEdge):
            #make wedge blocks
            if not LeftWedgeEdge: LeftWedgeEdge = leftOpening.x
            wedgeBlocks(row, leftOpening, LeftWedgeEdge, LNerEdge, LEB, r1)
            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            LFarEdge , LTop , LBtm = LNerEdge, LNerEdge, LNerEdge
            LDiff = 0

        #Now do the wedge blocks for the right, same drill... repeated code?
        #find the edge of the correct side, offset for minimum block height.
        ZPositionCheck = row.z + (rowH2-blockHMin)*rSide
#edgeS may return "None"
        RightWedgeEdge = rightOpening.edgeS(ZPositionCheck,-1)
        if (abs(RDiff) > blockWidth) or (not RightWedgeEdge):
            #make wedge blocks
            if not RightWedgeEdge: RightWedgeEdge = rightOpening.x
            wedgeBlocks(row, rightOpening, RNerEdge, RightWedgeEdge, rSide, r1)

            #set the near and far edge settings to vertical, so the other edge blocks don't interfere
            RFarEdge , RTop , RBtm = RNerEdge, RNerEdge, RNerEdge
            RDiff = 0

        # Single block - needed for arch "point" (keystone).
        if blockXx < MaxWid:
            x = (LNerEdge + RNerEdge)/2.
            w = blockXx
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            BtmOff = LBtm - LNerEdge
            TopOff = LTop - LNerEdge
            ThisBlockOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
            BtmOff = RBtm - RNerEdge
            TopOff = RTop - RNerEdge
            ThisBlockOffsets += [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2

            pointsToAffect=(0,2)
            bevelBlockOffsets(ThisBlockOffsets,leftOpening.edgeBev(rowTop),pointsToAffect)

            pointsToAffect=(4,6)
            bevelBlockOffsets(ThisBlockOffsets,-rightOpening.edgeBev(rowTop),pointsToAffect)

            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,ThisBlockOffsets])
            continue

        # must be two or more blocks

        # Left offsets
        BtmOff = LBtm - LNerEdge
        TopOff = LTop - LNerEdge
        leftOffsets = [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2 + [[0]*3]*4
        bevelL = leftOpening.edgeBev(rowTop)

        pointsToAffect=(0,2)
        bevelBlockOffsets(leftOffsets,bevelL,pointsToAffect)

        # Right offsets
        BtmOff = RBtm - RNerEdge
        TopOff = RTop - RNerEdge
        rightOffsets = [[0]*3]*4 + [[BtmOff,0,0]]*2 + [[TopOff,0,0]]*2
        bevelR = rightOpening.edgeBev(rowTop)

        pointsToAffect=(4,6)
        bevelBlockOffsets(rightOffsets,-bevelR,pointsToAffect)

        if blockXx < MaxWid*2: # only two blocks?
            #div is the x position of the dividing point between the two bricks
            div = blockXm + (rndd()*blockWVar)/r1

            #set the x position and width for the left block
            x = (div + LNerEdge)/2 - blockGap/4
            w = (div - LNerEdge) - blockGap/2
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            #For reference: EdgeBlocks = [[x,z,w,h,d,[corner offset matrix]],[etc.]]
            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,leftOffsets])

            #Initialize for the block on the right side
            x = (div + RNerEdge)/2 + blockGap/4
            w = (RNerEdge - div) - blockGap/2
            ThisBlockDepth = rndd()*blockDVar+blockDepth
            row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,rightOffsets])
            continue

        # more than two blocks in the row, and no wedge blocks

        #make Left edge block
        #set the x position and width for the block
        widOptions = [blockWidth, bevelL + blockWidth, leftOpening.ts]
        baseWidMax = max(widOptions)
        w = baseWidMax+row.rowEdge+(rndd()*blockWVar)
        widOptions[0] = blockWidth
        widOptions[2] = w
        w = max(widOptions) / r1 - blockGap
        x = w/2 + LNerEdge + blockGap/2
        BlockRowL = x + w/2
        ThisBlockDepth = rndd()*blockDVar+blockDepth
        row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,leftOffsets])

        #make Right edge block
        #set the x position and width for the block
        widOptions = [blockWidth, bevelR + blockWidth, rightOpening.ts]
        baseWidMax = max(widOptions)
        w = baseWidMax+row.rowEdge+(rndd()*blockWVar)
        widOptions[0] = blockWidth
        widOptions[2] = w
        w = max(widOptions) / r1 - blockGap
        x = RNerEdge - w/2 - blockGap/2
        BlockRowR = x - w/2
        ThisBlockDepth = rndd()*blockDVar+blockDepth
        row.BlocksEdge.append([x,row.z,w,rowH,ThisBlockDepth,rightOffsets])

        row.RowSegments.append([BlockRowL,BlockRowR])


#####################################
#
# Makes arches for the top and bottom
# hole is the "wall opening" that the arch is for.
#
def archGeneration(hole, vlist, flist, sideSign):

    avlist = []
    aflist = []

    if sideSign == 1: # top
        r = hole.r #radius of the arch
        rt = hole.rt #thickness of the arch (stone height)
        v = hole.v #height of the arch
        c = hole.c
    else: # bottom
        r = hole.rl #radius of the arch
        rt = hole.rtl #thickness of the arch (stone height)
        v = hole.vl #height of the arch
        c = hole.cl

    ra = r + rt/2 #average radius of the arch
    x = hole.x
    w = hole.w
    holeW2=w/2
    h = hole.h
    z = hole.z
    bev = hole.b

    
    blockGap=settings['g']
    blockHMin=BLOCK_MIN+blockGap

    blockDepth=settings['d']
    blockDVar=settings['dv']

    if v > holeW2: # two arcs, to make a pointed arch
        # positioning
        zpos = z + (h/2)*sideSign
        xoffset = r - holeW2
        #left side top, right side bottom
        #angles reference straight up, and are in radians
        bevRad = r + bev
        bevHt = sqrt(bevRad**2 - (bevRad - (holeW2 + bev))**2)
        midHalfAngle = atan(v/(r-holeW2))
        midHalfAngleBevel = atan(bevHt/(r-holeW2))
        bevelAngle = midHalfAngle - midHalfAngleBevel
        anglebeg = (cPieHlf)*(-sideSign)
        angleend = (cPieHlf)*(-sideSign) + midHalfAngle

        avlist,aflist = arch(ra,rt,(xoffset)*(sideSign),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]
        vlist += avlist
        flist += aflist

        #right side top, left side bottom
        #angles reference straight up, and are in radians
        anglebeg = (cPieHlf)*(sideSign) - midHalfAngle
        angleend = (cPieHlf)*(sideSign)

        avlist,aflist = arch(ra,rt,(xoffset)*(-sideSign),zpos,anglebeg,angleend,bev,bevelAngle,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+hole.x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        #keystone
        Dpth = blockDepth+rndc()*blockDVar
        angleBevel = (cPieHlf)*(sideSign) - midHalfAngle
        Wdth = (rt - blockGap - bev) * 2 * sin(angleBevel) * sideSign #note, sin may be negative
        MidZ = ((sideSign)*(bevHt + h/2.0) + z) + (rt - blockGap - bev) * cos(angleBevel) #note, cos may come out negative too
        nearCorner = sideSign*(MidZ - z) - v - h/2

        if sideSign == 1:
            TopHt = hole.top() - MidZ - blockGap
            BtmHt = nearCorner
        else:
            BtmHt =  - (hole.btm() - MidZ) - blockGap
            TopHt = nearCorner

        # set the amout to bevel the keystone
        keystoneBevel = (bevHt - v)*sideSign
        if Wdth >= blockHMin:
            avlist,aflist = MakeAKeystone(x, Wdth, MidZ, TopHt, BtmHt, Dpth, keystoneBevel, len(vlist))

            if settings['Dome']:
                for i,vert in enumerate(avlist):
                    if settings['Slope']: r1 = dims['t']*sin(vert[2]*cPie/(dims['t']*2))
                    else: r1 = vert[2]
                    avlist[i] = [((vert[0]-hole.x)/r1)+hole.x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist

    else: # only one arc - curve not peak.
#bottom (sideSign -1) arch has poorly sized blocks...

        zpos = z + (sideSign * (h/2 + v - r)) # single arc positioning

        #angles reference straight up, and are in radians
        if sideSign == -1: angleOffset = cPie
        else: angleOffset = 0.0

        if v < holeW2:
            halfangle = atan(w/(2*(r-v)))

            anglebeg = angleOffset - halfangle
            angleend = angleOffset + halfangle
        else:
            anglebeg = angleOffset - cPieHlf
            angleend = angleOffset + cPieHlf

        avlist,aflist = arch(ra,rt,0,zpos,anglebeg,angleend,bev,0.0,len(vlist))

        for i,vert in enumerate(avlist): avlist[i] = [vert[0]+x,vert[1],vert[2]]

        vlist += avlist
        flist += aflist

        # Make the Side Stones
        archBW=sqrt(rt**2 - c**2)
        archBWG=archBW-blockGap

        if c > blockHMin and c < archBW:
            subdivision=settings['sdv']
            if settings['Dome']:
                subdivision*=(zpos+(h/2)*sideSign)

            #set the height of the block, it should be as high as the max corner position, minus grout
            height = c - blockGap*(0.5 + c/archBW)

            #the vertical offset for the short side of the block
            voff = sideSign * (blockHMin - height)
            xstart = holeW2
            zstart = z + sideSign * (h/2 + blockGap/2)
            woffset = archBWG*(blockHMin)/(c - blockGap/2)
#            woffset = archBWG*(BLOCK_MIN + blockGap/2)/(c - blockGap/2)
            depth = blockDepth+(rndd()*blockDVar)

            if sideSign == 1:
                offsets = [[0]*3]*6 + [[0]*2 + [voff]]*2
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*3]*4 + [[0]*2 + [voff]]*2 + [[0]*3]*2
                topSide = zstart
                btmSide = zstart-height

            pointsToAffect=(4,6) # left
            bevelBlockOffsets(offsets,bev,pointsToAffect)

            avlist,aflist = MakeABlock([x-xstart-archBWG, x-xstart- woffset, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if settings['Dome']:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist

            if sideSign == 1:
                offsets = [[0]*3]*2 + [[0]*2 + [voff]]*2 + [[0]*3]*4
                topSide = zstart+height
                btmSide = zstart
            else:
                offsets = [[0]*2 + [voff]]*2 + [[0]*3]*6
                topSide = zstart
                btmSide = zstart-height

            pointsToAffect=(0,2) # right
            bevelBlockOffsets(offsets,bev,pointsToAffect)

            avlist,aflist = MakeABlock([x+xstart+woffset, x+xstart+archBWG, btmSide, topSide, -depth/2, depth/2], subdivision, len(vlist), Offsets=offsets)

# top didn't use radialized in prev version; just noting for clarity - may need to revise for "sideSign == 1"
            if settings['Dome']:
                for i,vert in enumerate(avlist): avlist[i] = [((vert[0]-x)/vert[2])+x,vert[1],vert[2]]

            vlist += avlist
            flist += aflist
