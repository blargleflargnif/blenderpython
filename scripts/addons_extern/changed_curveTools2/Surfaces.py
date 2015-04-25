import bpy
import bmesh

from . import Math
from . import Curves



class LoftedSplineSurface:
    def __init__(self, activeSpline, otherSpline, bMesh, vert0Index, resolution):
        self.splineA = activeSpline
        self.splineO = otherSpline
        
        self.bMesh = bMesh
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.vert0Index = vert0Index
        self.resolution = resolution

        
    def Apply(self, worldMatrixA, worldMatrixO):
        #deltaPar = 1.0 / float(self.resolution - 1)
        
        par = 0.0
        pointA = worldMatrixA * self.splineA.CalcPoint(par)
        pointO = worldMatrixO * self.splineO.CalcPoint(par)
        self.bMesh.verts[self.vert0Index].co = pointA
        self.bMesh.verts[self.vert0Index + 1].co = pointO
        
        fltResm1 = float(self.resolution - 1)
        for i in range(1, self.resolution):
            par = float(i) / fltResm1
        
            pointA = worldMatrixA * self.splineA.CalcPoint(par)
            pointO = worldMatrixO * self.splineO.CalcPoint(par)
            self.bMesh.verts[self.vert0Index + 2 * i].co = pointA
            self.bMesh.verts[self.vert0Index + 2 * i + 1].co = pointO

        
    def AddFaces(self):
        currIndexA = self.vert0Index
        currIndexO = self.vert0Index + 1
        
        bmVerts = self.bMesh.verts
        for i in range(1, self.resolution):
            nextIndexA = self.vert0Index + 2 * i
            nextIndexO = nextIndexA + 1
            
            self.bMesh.faces.new([bmVerts[currIndexA], bmVerts[currIndexO], bmVerts[nextIndexO], bmVerts[nextIndexA]])
            
            currIndexA = nextIndexA
            currIndexO = nextIndexO
            

class LoftedSurface:
    @staticmethod
    def FromSelection():
        selObjects = bpy.context.selected_objects
        if len(selObjects) != 2: raise Exception("len(selObjects) != 2") # shouldn't be possible
        
        blenderActiveCurve = bpy.context.active_object
        blenderOtherCurve = selObjects[0]
        if blenderActiveCurve == blenderOtherCurve: blenderOtherCurve = selObjects[1]
        
        aCurve = Curves.Curve(blenderActiveCurve)
        oCurve = Curves.Curve(blenderOtherCurve)
        
        name = "TODO: autoname"
        
        return LoftedSurface(aCurve, oCurve, name)
    

    def __init__(self, activeCurve, otherCurve, name = "LoftedSurface"):
        self.curveA = activeCurve
        self.curveO = otherCurve
        self.name  = name
        
        self.nrSplines = self.curveA.nrSplines
        if self.curveO.nrSplines < self.nrSplines: self.nrSplines = self.curveO.nrSplines
        
        self.bMesh = bmesh.new()
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.splineSurfaces = self.SetupSplineSurfaces()
        
        self.Apply()
        
        
    def SetupSplineSurfaces(self):
        rvSplineSurfaces = []
        
        currV0Index = 0
        for i in range(self.nrSplines):
            splineA = self.curveA.splines[i]
            splineO = self.curveO.splines[i]
            
            res = splineA.resolution
            if splineO.resolution < res: res = splineO.resolution
            
            for iv in range(2 * res): self.bMesh.verts.new()
            
            splSurf = LoftedSplineSurface(splineA, splineO, self.bMesh, currV0Index, res)
            splSurf.AddFaces()
            rvSplineSurfaces.append(splSurf)
            
            currV0Index += 2 * res
        
        return rvSplineSurfaces
        
        
    def Apply(self):
        for splineSurface in self.splineSurfaces: splineSurface.Apply(self.curveA.worldMatrix, self.curveO.worldMatrix)
        
        
    def AddToScene(self):
        mesh = bpy.data.meshes.new("Mesh" + self.name)
        
        self.bMesh.to_mesh(mesh)
        mesh.update()
        
        meshObject = bpy.data.objects.new(self.name, mesh)
        
        bpy.context.scene.objects.link(meshObject)



class RevolvedSplineSurface:
    def __init__(self, profileSpline, axisSpline, bMesh, vert0Index, linearRes, angularRes):
        self.profileSpline = profileSpline
        self.axisSpline = axisSpline
        
        self.bMesh = bMesh
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.vert0Index = vert0Index
        self.linearRes = linearRes
        self.angularRes = angularRes

        
    def Apply(self, worldMatrixProfile, worldMatrixAxis):
        worldMatrixAxis3x3 = worldMatrixAxis.to_3x3()
    
        # TODO: we probably don't need to calculate this in advance; we can do it in the 'main' loop
        worldPointsProfile = []
        worldPointsAxis = []
        globalDerivativesAxis = []
        fltLinResMin1 = float(self.linearRes - 1)
        for iLinear in range(self.linearRes):
            par = float(iLinear) / fltLinResMin1
            
            pointProfile = self.profileSpline.CalcPoint(par)
            worldPointsProfile.append(worldMatrixProfile * pointProfile)
            
            pointAxis = self.axisSpline.CalcPoint(par)
            worldPointsAxis.append(worldMatrixAxis * pointAxis)
            
            derivativeAxis = self.axisSpline.CalcDerivative(par)
            globalDerivativesAxis.append(worldMatrixAxis3x3 * derivativeAxis)
        
        for iLinear in range(self.linearRes):
            center = worldPointsAxis[iLinear]
            pointProfile = worldPointsProfile[iLinear]
            dirX = (pointProfile - center)
            radius = dirX.magnitude
            dirY = globalDerivativesAxis[iLinear].cross(dirX).normalized()
            dirX.normalize()
            
            currPoints = Math.GenerateCircle(center, radius, dirX, dirY, self.angularRes)
            for iAngular in range(self.angularRes):
                iVert = (self.angularRes * iLinear) + iAngular
                self.bMesh.verts[self.vert0Index + iVert].co = currPoints[iAngular]
                 
        
    def AddFaces(self):
        bmVerts = self.bMesh.verts
        
        for iLinear in range(self.linearRes - 1):
            for iAngular in range(self.angularRes - 1):
                currIndexProfile1 = self.vert0Index + (self.angularRes * iLinear) + iAngular
                currIndexProfile2 = currIndexProfile1 + 1
                nextIndexProfile1 = self.vert0Index + (self.angularRes * (iLinear + 1)) + iAngular
                nextIndexProfile2 = nextIndexProfile1 + 1
        
                self.bMesh.faces.new([bmVerts[currIndexProfile1], bmVerts[currIndexProfile2], bmVerts[nextIndexProfile2], bmVerts[nextIndexProfile1]])
        
        # close it
        for iLinear in range(self.linearRes - 1):
            iAngular = self.angularRes - 1

            currIndexProfile1 = self.vert0Index + (self.angularRes * iLinear) + iAngular
            currIndexProfile2 = self.vert0Index + (self.angularRes * iLinear)
            nextIndexProfile1 = self.vert0Index + (self.angularRes * (iLinear + 1)) + iAngular
            nextIndexProfile2 = self.vert0Index + (self.angularRes * (iLinear + 1))
    
            self.bMesh.faces.new([bmVerts[currIndexProfile1], bmVerts[currIndexProfile2], bmVerts[nextIndexProfile2], bmVerts[nextIndexProfile1]])
               
        
class RevolvedSurface:
    @staticmethod
    def FromSelection():
        nrSelectedObjects = bpy.context.scene.curvetools.NrSelectedObjects
        if nrSelectedObjects != 2: raise Exception("nrSelectedObjects != 2") # shouldn't be possible
        
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        selectedObjectValues = selectedObjects.values()

        curveName = selectedObjectValues[0].name
        profileBlenderCurve = None
        try: profileBlenderCurve = bpy.data.objects[curveName]
        except: profileBlenderCurve = None
        if profileBlenderCurve is None: raise Exception("profileBlenderCurve is None")

        curveName = selectedObjectValues[1].name
        axisBlenderCurve = None
        try: axisBlenderCurve = bpy.data.objects[curveName]
        except: axisBlenderCurve = None
        if axisBlenderCurve is None: raise Exception("axisBlenderCurve is None")        
        
        profileCurve = Curves.Curve(profileBlenderCurve)
        axisCurve = Curves.Curve(axisBlenderCurve)
        
        name = "TODO: autoname"
        
        return RevolvedSurface(profileCurve, axisCurve, name)
    

    def __init__(self, profileCurve, axisCurve, name = "RevolvedSurface"):
        self.profileCurve = profileCurve
        self.axisCurve = axisCurve
        self.name  = name
        
        # this can't be right..
        self.nrSplines = self.profileCurve.nrSplines
        if self.axisCurve.nrSplines < self.nrSplines: self.nrSplines = self.axisCurve.nrSplines
        
        self.bMesh = bmesh.new()
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.splineSurfaces = self.SetupSplineSurfaces()
        
        self.Apply()
        
        
    def SetupSplineSurfaces(self):
        rvSplineSurfaces = []
        
        currV0Index = 0
        for i in range(self.nrSplines):
            splineProfile = self.profileCurve.splines[i]
            splineAxis = self.axisCurve.splines[i]
            
            linearRes = splineProfile.resolution
            if splineAxis.resolution < linearRes: linearRes = splineAxis.resolution
            angularRes = bpy.context.scene.curvetools.AngularResolution
            
            for iv in range(linearRes * angularRes): self.bMesh.verts.new()
            
            splSurf = RevolvedSplineSurface(splineProfile, splineAxis, self.bMesh, currV0Index, linearRes, angularRes)
            splSurf.AddFaces()
            rvSplineSurfaces.append(splSurf)
            
            currV0Index += linearRes * angularRes
        
        return rvSplineSurfaces
        
        
    def Apply(self):
        for splineSurface in self.splineSurfaces: splineSurface.Apply(self.profileCurve.worldMatrix, self.axisCurve.worldMatrix)
        
        
    def AddToScene(self):
        mesh = bpy.data.meshes.new("Mesh" + self.name)
        
        self.bMesh.to_mesh(mesh)
        mesh.update()
        
        meshObject = bpy.data.objects.new(self.name, mesh)
        
        bpy.context.scene.objects.link(meshObject)
        
        
        
    

        


# active spline is swept over other spline (rail)
class SweptSplineSurface:
    def __init__(self, activeSpline, otherSpline, bMesh, vert0Index, resolutionA, resolutionO):
        self.splineA = activeSpline     # profile
        self.splineO = otherSpline      # rail
        
        self.bMesh = bMesh
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.vert0Index = vert0Index
        self.resolutionA = resolutionA
        self.resolutionO = resolutionO

        
    def Apply(self, worldMatrixA, worldMatrixO):
        localPointsA = []
        fltResAm1 = float(self.resolutionA - 1)
        for i in range(self.resolutionA):
            par = float(i) / fltResAm1
            pointA = self.splineA.CalcPoint(par)
            localPointsA.append(pointA)

        
        worldPointsO = []
        localDerivativesO = []
        fltResOm1 = float(self.resolutionO - 1)
        for i in range(self.resolutionO):
            par = float(i) / fltResOm1
            
            pointO = self.splineO.CalcPoint(par)
            worldPointsO.append(worldMatrixO * pointO)
            
            derivativeO = self.splineO.CalcDerivative(par)
            localDerivativesO.append(derivativeO)
        
        
        currWorldMatrixA = worldMatrixA
        worldMatrixOInv = worldMatrixO.inverted()
        prevDerivativeO = localDerivativesO[0]
        for iO in range(self.resolutionO):
            currDerivativeO = localDerivativesO[iO]
            localRotMatO = Math.CalcRotationMatrix(prevDerivativeO, currDerivativeO)
            
            currLocalAToLocalO = worldMatrixOInv * currWorldMatrixA       
            worldPointsA = []
            for iA in range(self.resolutionA):
                pointALocalToO = currLocalAToLocalO * localPointsA[iA]
                rotatedPointA = localRotMatO * pointALocalToO
                worldPointsA.append(worldMatrixO * rotatedPointA)
                
            worldOffsetsA = []
            worldPoint0A = worldPointsA[0]
            for i in range(self.resolutionA): worldOffsetsA.append(worldPointsA[i] - worldPoint0A)
            
            
            for iA in range(self.resolutionA):
                iVert = self.vert0Index + (self.resolutionA * iO) + iA
                currVert = worldPointsO[iO] + worldOffsetsA[iA]
                self.bMesh.verts[iVert].co = currVert
                
            prevDerivativeO = currDerivativeO
            currWorldMatrixA = worldMatrixO * localRotMatO * currLocalAToLocalO

        
    def AddFaces(self):
        bmVerts = self.bMesh.verts
        
        for iO in range(self.resolutionO - 1):
            for iA in range(self.resolutionA - 1):
                currIndexA1 = self.vert0Index + (self.resolutionA * iO) + iA
                currIndexA2 = currIndexA1 + 1
                nextIndexA1 = self.vert0Index + (self.resolutionA * (iO + 1)) + iA
                nextIndexA2 = nextIndexA1 + 1
        
                self.bMesh.faces.new([bmVerts[currIndexA1], bmVerts[currIndexA2], bmVerts[nextIndexA2], bmVerts[nextIndexA1]])
          

class SweptSurface:
    @staticmethod
    def FromSelection():
        selObjects = bpy.context.selected_objects
        if len(selObjects) != 2: raise Exception("len(selObjects) != 2") # shouldn't be possible
        
        blenderActiveCurve = bpy.context.active_object
        blenderOtherCurve = selObjects[0]
        if blenderActiveCurve == blenderOtherCurve: blenderOtherCurve = selObjects[1]
        
        aCurve = Curves.Curve(blenderActiveCurve)
        oCurve = Curves.Curve(blenderOtherCurve)
        
        name = "TODO: autoname"
        
        return SweptSurface(aCurve, oCurve, name)
    

    def __init__(self, activeCurve, otherCurve, name = "SweptSurface"):
        self.curveA = activeCurve
        self.curveO = otherCurve
        self.name  = name
        
        self.nrSplines = self.curveA.nrSplines
        if self.curveO.nrSplines < self.nrSplines: self.nrSplines = self.curveO.nrSplines
        
        self.bMesh = bmesh.new()
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.splineSurfaces = self.SetupSplineSurfaces()
        
        self.Apply()
        
        
    def SetupSplineSurfaces(self):
        rvSplineSurfaces = []
        
        currV0Index = 0
        for i in range(self.nrSplines):
            splineA = self.curveA.splines[i]
            splineO = self.curveO.splines[i]
            
            resA = splineA.resolution
            resO = splineO.resolution
            
            for iv in range(resA * resO): self.bMesh.verts.new()
            
            splSurf = SweptSplineSurface(splineA, splineO, self.bMesh, currV0Index, resA, resO)
            splSurf.AddFaces()
            rvSplineSurfaces.append(splSurf)
            
            currV0Index += resA * resO
        
        return rvSplineSurfaces
        
        
    def Apply(self):
        for splineSurface in self.splineSurfaces: splineSurface.Apply(self.curveA.worldMatrix, self.curveO.worldMatrix)
        
        
    def AddToScene(self):
        mesh = bpy.data.meshes.new("Mesh" + self.name)
        
        self.bMesh.to_mesh(mesh)
        mesh.update()
        
        meshObject = bpy.data.objects.new(self.name, mesh)
        
        bpy.context.scene.objects.link(meshObject)
        

        
# beginProfile is swept along rail and morphed into endProfile
class SweptAndMorphedSplineSurface:
    def __init__(self, beginProfileSpline, endProfileSpline, railSpline, bMesh, vert0Index, resolutionProfiles, resolutionRail):
        self.beginProfileSpline = beginProfileSpline     
        self.endProfileSpline = endProfileSpline      
        self.railSpline = railSpline      
        
        self.bMesh = bMesh
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.vert0Index = vert0Index
        self.resolutionProfiles = resolutionProfiles
        self.resolutionRail = resolutionRail

        
    def Apply(self, worldMatrixBeginProfile, worldMatrixEndProfile, worldMatrixRail):
        # 1. rail
        worldPointsRail = []
        localDerivativesRail = []
        fltResRailMin1 = float(self.resolutionRail - 1)
        for i in range(self.resolutionRail):
            par = float(i) / fltResRailMin1
            
            pointRail = self.railSpline.CalcPoint(par)
            worldPointsRail.append(worldMatrixRail * pointRail)
            
            derivativeRail = self.railSpline.CalcDerivative(par)
            localDerivativesRail.append(derivativeRail)

        worldMatrixRailInv = worldMatrixRail.inverted()
                        
        # 2. beginProfile
        localPointsBeginProfile = []
        fltResProfilesMin1 = float(self.resolutionProfiles - 1)
        for iProfile in range(self.resolutionProfiles):
            par = float(iProfile) / fltResProfilesMin1
            pointBeginProfile = self.beginProfileSpline.CalcPoint(par)
            localPointsBeginProfile.append(pointBeginProfile)
        
        currWorldMatrixBeginProfile = worldMatrixBeginProfile
        prevDerivativeRail = localDerivativesRail[0]
        vertsBeginProfile = [None] * (self.resolutionRail * self.resolutionProfiles)
        for iRail in range(self.resolutionRail):
            currDerivativeRail = localDerivativesRail[iRail]
            localRotMatRail = Math.CalcRotationMatrix(prevDerivativeRail, currDerivativeRail)
            
            currLocalProfileToLocalRail = worldMatrixRailInv * currWorldMatrixBeginProfile       
            worldPointsProfile = []
            for iProfile in range(self.resolutionProfiles):
                pointProfileLocalToRail = currLocalProfileToLocalRail * localPointsBeginProfile[iProfile]
                rotatedPointProfile = localRotMatRail * pointProfileLocalToRail
                worldPointsProfile.append(worldMatrixRail * rotatedPointProfile)
                
            worldOffsetsProfile = []
            worldPoint0Profile = worldPointsProfile[0]
            for iProfile in range(self.resolutionProfiles): worldOffsetsProfile.append(worldPointsProfile[iProfile] - worldPoint0Profile)
            
            for iProfile in range(self.resolutionProfiles):
                # iVert = self.vert0Index + (self.resolutionProfiles * iRail) + iProfile
                iVert = (self.resolutionProfiles * iRail) + iProfile
                currVert = worldPointsRail[iRail] + worldOffsetsProfile[iProfile]
                # self.bMesh.verts[iVert].co = currVert   # TEMP
                vertsBeginProfile[iVert] = currVert
                
            prevDerivativeRail = currDerivativeRail
            currWorldMatrixBeginProfile = worldMatrixRail * localRotMatRail * currLocalProfileToLocalRail

        # 3. endProfile
        localPointsEndProfile = []
        for iProfile in range(self.resolutionProfiles):
            par = float(iProfile) / fltResProfilesMin1
            pointEndProfile = self.endProfileSpline.CalcPoint(par)
            localPointsEndProfile.append(pointEndProfile)
        
        currWorldMatrixEndProfile = worldMatrixEndProfile
        prevDerivativeRail = localDerivativesRail[-1]
        vertsEndProfile = [None] * (self.resolutionRail * self.resolutionProfiles)
        for iRail in reversed(range(self.resolutionRail)):
            currDerivativeRail = localDerivativesRail[iRail]
            localRotMatRail = Math.CalcRotationMatrix(prevDerivativeRail, currDerivativeRail)
            
            currLocalProfileToLocalRail = worldMatrixRailInv * currWorldMatrixEndProfile       
            worldPointsProfile = []
            for iProfile in range(self.resolutionProfiles):
                pointProfileLocalToRail = currLocalProfileToLocalRail * localPointsEndProfile[iProfile]
                rotatedPointProfile = localRotMatRail * pointProfileLocalToRail
                worldPointsProfile.append(worldMatrixRail * rotatedPointProfile)
                
            worldOffsetsProfile = []
            worldPoint0Profile = worldPointsProfile[0]
            for iProfile in range(self.resolutionProfiles): worldOffsetsProfile.append(worldPointsProfile[iProfile] - worldPoint0Profile)
            
            for iProfile in range(self.resolutionProfiles):
                # iVert = self.vert0Index + (self.resolutionProfiles * iRail) + iProfile
                iVert = (self.resolutionProfiles * iRail) + iProfile
                currVert = worldPointsRail[iRail] + worldOffsetsProfile[iProfile]
                # self.bMesh.verts[iVert].co = currVert   # TEMP
                vertsEndProfile[iVert] = currVert
                
            prevDerivativeRail = currDerivativeRail
            currWorldMatrixEndProfile = worldMatrixRail * localRotMatRail * currLocalProfileToLocalRail
        
        # 4. morph
        for iRail in range(self.resolutionRail):
            weightEnd = float(iRail) / fltResRailMin1
            weightBegin = 1.0 - weightEnd
            # weightEnd = 1.0
            # weightBegin = 0.0
            for iProfile in range(self.resolutionProfiles):
                iVert = (self.resolutionProfiles * iRail) + iProfile
                vertBegin = vertsBeginProfile[iVert]
                vertEnd = vertsEndProfile[iVert]
                vertMorphed = (vertBegin * weightBegin) + (vertEnd * weightEnd)
                self.bMesh.verts[self.vert0Index + iVert].co = vertMorphed
                
        
    def AddFaces(self):
        bmVerts = self.bMesh.verts
        
        for iRail in range(self.resolutionRail - 1):
            for iProfile in range(self.resolutionProfiles - 1):
                currIndexProfile1 = self.vert0Index + (self.resolutionProfiles * iRail) + iProfile
                currIndexProfile2 = currIndexProfile1 + 1
                nextIndexProfile1 = self.vert0Index + (self.resolutionProfiles * (iRail + 1)) + iProfile
                nextIndexProfile2 = nextIndexProfile1 + 1
        
                self.bMesh.faces.new([bmVerts[currIndexProfile1], bmVerts[currIndexProfile2], bmVerts[nextIndexProfile2], bmVerts[nextIndexProfile1]])

        
class SweptAndMorphedSurface:
    @staticmethod
    def FromSelection():
        nrSelectedObjects = bpy.context.scene.curvetools.NrSelectedObjects
        if nrSelectedObjects != 3: raise Exception("nrSelectedObjects != 3") # shouldn't be possible
        
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        selectedObjectValues = selectedObjects.values()

        curveName = selectedObjectValues[0].name
        beginProfileBlenderCurve = None
        try: beginProfileBlenderCurve = bpy.data.objects[curveName]
        except: beginProfileBlenderCurve = None
        if beginProfileBlenderCurve is None: raise Exception("beginProfileBlenderCurve is None")

        curveName = selectedObjectValues[1].name
        endProfileBlenderCurve = None
        try: endProfileBlenderCurve = bpy.data.objects[curveName]
        except: endProfileBlenderCurve = None
        if endProfileBlenderCurve is None: raise Exception("endProfileBlenderCurve is None")

        curveName = selectedObjectValues[2].name
        railBlenderCurve = None
        try: railBlenderCurve = bpy.data.objects[curveName]
        except: railBlenderCurve = None
        if railBlenderCurve is None: raise Exception("railBlenderCurve is None")
        
        
        beginProfileCurve = Curves.Curve(beginProfileBlenderCurve)
        endProfileCurve = Curves.Curve(endProfileBlenderCurve)
        railCurve = Curves.Curve(railBlenderCurve)
        
        name = "TODO: autoname"
        
        return SweptAndMorphedSurface(beginProfileCurve, endProfileCurve, railCurve, name)
    

    def __init__(self, beginProfileCurve, endProfileCurve, railCurve, name = "SweptAndMorphedSurface"):
        self.beginProfileCurve = beginProfileCurve
        self.endProfileCurve = endProfileCurve
        self.railCurve = railCurve
        self.name  = name
        
        # this can't be right..
        self.nrSplines = self.beginProfileCurve.nrSplines
        if self.endProfileCurve.nrSplines < self.nrSplines: self.nrSplines = self.endProfileCurve.nrSplines
        if self.railCurve.nrSplines < self.nrSplines: self.nrSplines = self.railCurve.nrSplines
        
        self.bMesh = bmesh.new()
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.splineSurfaces = self.SetupSplineSurfaces()
        
        self.Apply()
        
        
    def SetupSplineSurfaces(self):
        rvSplineSurfaces = []
        
        currV0Index = 0
        for i in range(self.nrSplines):
            splineBeginProfile = self.beginProfileCurve.splines[i]
            splineEndProfile = self.endProfileCurve.splines[i]
            splineRail = self.railCurve.splines[i]
            
            resProfiles = splineBeginProfile.resolution
            if splineEndProfile.resolution < resProfiles: resProfiles = splineEndProfile.resolution
            resRail = splineRail.resolution
            
            for iv in range(resProfiles * resRail): self.bMesh.verts.new()
            
            splSurf = SweptAndMorphedSplineSurface(splineBeginProfile, splineEndProfile, splineRail, self.bMesh, currV0Index, resProfiles, resRail)
            splSurf.AddFaces()
            rvSplineSurfaces.append(splSurf)
            
            currV0Index += resProfiles * resRail
        
        return rvSplineSurfaces
        
        
    def Apply(self):
        for splineSurface in self.splineSurfaces: splineSurface.Apply(self.beginProfileCurve.worldMatrix, self.endProfileCurve.worldMatrix, self.railCurve.worldMatrix)
        
        
    def AddToScene(self):
        mesh = bpy.data.meshes.new("Mesh" + self.name)
        
        self.bMesh.to_mesh(mesh)
        mesh.update()
        
        meshObject = bpy.data.objects.new(self.name, mesh)
        
        bpy.context.scene.objects.link(meshObject)










# profileSpline is swept over rail1Spline and scaled/rotated to have its endpoint on rail2Spline
class BirailedSplineSurface:
    def __init__(self, rail1Spline, rail2Spline, profileSpline, bMesh, vert0Index, resolutionRails, resolutionProfile):
        self.rail1Spline = rail1Spline
        self.rail2Spline = rail2Spline
        self.profileSpline = profileSpline
        
        self.bMesh = bMesh
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()

        self.vert0Index = vert0Index
        self.resolutionRails = resolutionRails
        self.resolutionProfile = resolutionProfile

        
    def Apply(self, worldMatrixRail1, worldMatrixRail2, worldMatrixProfile):
        localPointsProfile = []
        fltResProfilem1 = float(self.resolutionProfile - 1)
        for i in range(self.resolutionProfile):
            par = float(i) / fltResProfilem1
            pointProfile = self.profileSpline.CalcPoint(par)
            localPointsProfile.append(pointProfile)

        
        worldPointsRail1 = []
        localDerivativesRail1 = []
        worldPointsRail2 = []
        fltResRailsm1 = float(self.resolutionRails - 1)
        for i in range(self.resolutionRails):
            par = float(i) / fltResRailsm1
            
            pointRail1 = self.rail1Spline.CalcPoint(par)
            worldPointsRail1.append(worldMatrixRail1 * pointRail1)
            
            derivativeRail1 = self.rail1Spline.CalcDerivative(par)
            localDerivativesRail1.append(derivativeRail1)
            
            pointRail2 = self.rail2Spline.CalcPoint(par)
            worldPointsRail2.append(worldMatrixRail2 * pointRail2)
        
        
        currWorldMatrixProfile = worldMatrixProfile
        worldMatrixRail1Inv = worldMatrixRail1.inverted()
        prevDerivativeRail1 = localDerivativesRail1[0]
        for iRail in range(self.resolutionRails):
            currDerivativeRail1 = localDerivativesRail1[iRail]
            localRotMatRail1 = Math.CalcRotationMatrix(prevDerivativeRail1, currDerivativeRail1)
            
            currLocalProfileToLocalRail1 = worldMatrixRail1Inv * currWorldMatrixProfile       
            worldPointsProfileRail1 = []
            for iProfile in range(self.resolutionProfile):
                pointProfileLocalToRail1 = currLocalProfileToLocalRail1 * localPointsProfile[iProfile]
                rotatedPointProfile = localRotMatRail1 * pointProfileLocalToRail1
                worldPointsProfileRail1.append(worldMatrixRail1 * rotatedPointProfile)
                
            worldOffsetsProfileRail1 = []
            worldPoint0ProfileRail1 = worldPointsProfileRail1[0]
            for iProfile in range(self.resolutionProfile): worldOffsetsProfileRail1.append(worldPointsProfileRail1[iProfile] - worldPoint0ProfileRail1)
                
            worldStartPointProfileRail1 = worldPointsRail1[iRail]
            worldEndPointProfileRail1 = worldStartPointProfileRail1 + worldOffsetsProfileRail1[-1]
            v3From = worldEndPointProfileRail1 - worldStartPointProfileRail1
            v3To = worldPointsRail2[iRail] - worldStartPointProfileRail1
            scaleFactorRail2 = v3To.magnitude / v3From.magnitude
            rotMatRail2 = Math.CalcRotationMatrix(v3From, v3To)
            
            worldOffsetsProfileRail2 = []
            for iProfile in range(self.resolutionProfile):
                offsetProfileRail1 = worldOffsetsProfileRail1[iProfile]
                worldOffsetsProfileRail2.append(rotMatRail2 * (offsetProfileRail1 * scaleFactorRail2))
            
            
            for iProfile in range(self.resolutionProfile):
                iVert = self.vert0Index + (self.resolutionProfile * iRail) + iProfile
                currVert = worldPointsRail1[iRail] + worldOffsetsProfileRail2[iProfile]
                self.bMesh.verts[iVert].co = currVert
                
            prevDerivativeRail1 = currDerivativeRail1
            currWorldMatrixProfile = worldMatrixRail1 * localRotMatRail1 * currLocalProfileToLocalRail1

        
    def AddFaces(self):
        bmVerts = self.bMesh.verts
        
        for iRail in range(self.resolutionRails - 1):
            for iProfile in range(self.resolutionProfile - 1):
                currIndex1 = self.vert0Index + (self.resolutionProfile * iRail) + iProfile
                currIndex2 = currIndex1 + 1
                nextIndex1 = self.vert0Index + (self.resolutionProfile * (iRail + 1)) + iProfile
                nextIndex2 = nextIndex1 + 1
        
                self.bMesh.faces.new([bmVerts[currIndex1], bmVerts[currIndex2], bmVerts[nextIndex2], bmVerts[nextIndex1]])
        

class BirailedSurface:
    @staticmethod
    def FromSelection():
        nrSelectedObjects = bpy.context.scene.curvetools.NrSelectedObjects
        if nrSelectedObjects != 3: raise Exception("nrSelectedObjects != 3") # shouldn't be possible
        
        
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        selectedObjectValues = selectedObjects.values()

        curveName = selectedObjectValues[0].name
        rail1BlenderCurve = None
        try: rail1BlenderCurve = bpy.data.objects[curveName]
        except: rail1BlenderCurve = None
        if rail1BlenderCurve is None: raise Exception("rail1BlenderCurve is None")

        curveName = selectedObjectValues[1].name
        rail2BlenderCurve = None
        try: rail2BlenderCurve = bpy.data.objects[curveName]
        except: rail2BlenderCurve = None
        if rail2BlenderCurve is None: raise Exception("rail2BlenderCurve is None")

        curveName = selectedObjectValues[2].name
        profileBlenderCurve = None
        try: profileBlenderCurve = bpy.data.objects[curveName]
        except: profileBlenderCurve = None
        if profileBlenderCurve is None: raise Exception("profileBlenderCurve is None")
        
        
        rail1Curve = Curves.Curve(rail1BlenderCurve)
        rail2Curve = Curves.Curve(rail2BlenderCurve)
        profileCurve = Curves.Curve(profileBlenderCurve)
        
        name = "TODO: autoname"
        
        return BirailedSurface(rail1Curve, rail2Curve, profileCurve, name)
    

    def __init__(self, rail1Curve, rail2Curve, profileCurve, name = "BirailedSurface"):
        self.rail1Curve = rail1Curve
        self.rail2Curve = rail2Curve
        self.profileCurve = profileCurve
        self.name  = name
        
        self.nrSplines = self.rail1Curve.nrSplines
        if self.rail2Curve.nrSplines < self.nrSplines: self.nrSplines = self.rail2Curve.nrSplines
        if self.profileCurve.nrSplines < self.nrSplines: self.nrSplines = self.profileCurve.nrSplines
        
        self.bMesh = bmesh.new()
        if hasattr(self.bMesh.verts, "ensure_lookup_table"): self.bMesh.verts.ensure_lookup_table()
        if hasattr(self.bMesh.edges, "ensure_lookup_table"): self.bMesh.edges.ensure_lookup_table()
        if hasattr(self.bMesh.faces, "ensure_lookup_table"): self.bMesh.faces.ensure_lookup_table()
        
        self.splineSurfaces = self.SetupSplineSurfaces()
        
        self.Apply()
        
        
    def SetupSplineSurfaces(self):
        rvSplineSurfaces = []
        
        currV0Index = 0
        for i in range(self.nrSplines):
            splineRail1 = self.rail1Curve.splines[i]
            splineRail2 = self.rail2Curve.splines[i]
            splineProfile = self.profileCurve.splines[i]
            
            resProfile = splineProfile.resolution
            resRails = splineRail1.resolution
            if splineRail2.resolution < resRails: resRails = splineRail2.resolution
            
            for iv in range(resProfile * resRails): self.bMesh.verts.new()
            
            splSurf = BirailedSplineSurface(splineRail1, splineRail2, splineProfile, self.bMesh, currV0Index, resRails, resProfile)
            splSurf.AddFaces()
            rvSplineSurfaces.append(splSurf)
            
            currV0Index += resProfile * resRails
        
        return rvSplineSurfaces
        
        
    def Apply(self):
        for splineSurface in self.splineSurfaces: splineSurface.Apply(self.rail1Curve.worldMatrix, self.rail2Curve.worldMatrix, self.profileCurve.worldMatrix)
        
        
    def AddToScene(self):
        mesh = bpy.data.meshes.new("Mesh" + self.name)
        
        self.bMesh.to_mesh(mesh)
        mesh.update()
        
        meshObject = bpy.data.objects.new(self.name, mesh)
        
        bpy.context.scene.objects.link(meshObject)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


    