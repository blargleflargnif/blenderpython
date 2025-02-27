bl_info = {
    "name": "Curve Tools 2",
    "description": "Adds some functionality for bezier/nurbs curve/surface modeling",
    "author": "Mackraken, guy lateur",
    "version": (0, 2, 0),
    "blender": (2, 6, 8),
    "location": "Tool Panel",
    "warning": "WIP",
    "category": "Add Curve"}
    
    
import bpy
from bpy.props import *
import bpy.app

from . import Properties
from . import Operators
from . import Panel



_selected_objects = []
def get_selection(self):
    dels = set(_selected_objects) - set(bpy.context.selected_objects)
    if len(dels):
        for c in dels:
            _selected_objects.remove(c)
    
    for c in bpy.context.selected_objects:
        if c not in _selected_objects:
            _selected_objects.append(c)
    return _selected_objects

def get_selection_nr(self):
    return len(get_selection(self))
        
def UpdateDummy(object, context):
    pass
        
        
        
class CurveTools2Settings(bpy.types.PropertyGroup):
    # selection
    SelectedObjects = CollectionProperty(type = Properties.CurveTools2SelectedObject)
    NrSelectedObjects = IntProperty(name = "NrSelectedObjects", default = 0, description = "Number of selected objects", update = UpdateDummy)
    NrSelectedCurves = IntProperty(name = "NrSelectedCurves", default = 0, description = "Number of selected curves", update = UpdateDummy)

    # curve
    CurveLength = FloatProperty(name = "CurveLength", default = 0.0, precision = 6)
    
    # resolutions
    SplineResolution = IntProperty(name = "SplineResolution", default = 64, min = 2, max = 1024, soft_min = 2, description = "Spline resolution will be set to this value")
    AngularResolution = IntProperty(name = "AngularResolution", default = 16, min = 4, max = 1024, soft_min = 4, description = "Angular resolution -- used when resolution cannot be got from curves")
    
    #splines
    
    SplineRemoveLength = FloatProperty(name = "SplineRemoveLength", default = 0.001, precision = 6, description = "Splines shorter than this threshold length will be removed")
    SplineJoinDistance = FloatProperty(name = "SplineJoinDistance", default = 0.001, precision = 6, description = "Splines with starting/ending points closer to each other than this threshold distance will be joined")
    SplineJoinStartEnd = BoolProperty(name = "SplineJoinStartEnd", default = False, description = "Only join splines at the starting point of one and the ending point of the other")

    splineJoinModeItems = (('At midpoint', 'At midpoint', 'Join splines at midpoint of neighbouring points'), ('Insert segment', 'Insert segment', 'Insert segment between neighbouring points'))
    SplineJoinMode = EnumProperty(items = splineJoinModeItems, name = "SplineJoinMode", default = 'At midpoint', description = "Determines how the splines will be joined")

    
    # curve intersection
    LimitDistance = FloatProperty(name = "LimitDistance", default = 0.001, precision = 6, description = "Intersections will not be generated if the distance between compared points is bigger than this limit")

    intAlgorithmItems = (('3D', '3D', 'Detect where curves intersect in 3D'), ('From View', 'From View', 'Detect where curves intersect in the RegionView3D'))
    IntersectCurvesAlgorithm = EnumProperty(items = intAlgorithmItems, name = "IntersectCurvesAlgorithm", description = "Determines how the intersection points will be detected", default = '3D')

    intModeItems = (('Insert', 'Insert', 'Insert points into the existing spline(s)'), ('Split', 'Split', 'Split the existing spline(s) into 2'), ('Empty', 'Empty', 'Add empty at intersections'))
    IntersectCurvesMode = EnumProperty(items = intModeItems, name = "IntersectCurvesMode", description = "Determines what happens at the intersection points", default = 'Split')

    intAffectItems = (('Both', 'Both', 'Insert points into both curves'), ('Active', 'Active', 'Insert points into active curve only'), ('Other', 'Other', 'Insert points into other curve only'))
    IntersectCurvesAffect = EnumProperty(items = intAffectItems, name = "IntersectCurvesAffect", description = "Determines which of the selected curves will be affected by the operation", default = 'Both')
    

def register():
    bpy.utils.register_class(Properties.CurveTools2SelectedObject)
    
    bpy.utils.register_class(CurveTools2Settings)
    bpy.types.Scene.curvetools = bpy.props.PointerProperty(type=CurveTools2Settings)

    bpy.utils.register_class(Operators.OperatorSelectionInfo)

    bpy.utils.register_class(Operators.OperatorCurveInfo)
    bpy.utils.register_class(Operators.OperatorCurveLength)
    bpy.utils.register_class(Operators.OperatorSplinesInfo)
    bpy.utils.register_class(Operators.OperatorSegmentsInfo)
    bpy.utils.register_class(Operators.OperatorOriginToSpline0Start)
    
    bpy.utils.register_class(Operators.OperatorIntersectCurves)
    bpy.utils.register_class(Operators.OperatorLoftCurves)
    bpy.utils.register_class(Operators.OperatorSweepCurves)
    bpy.utils.register_class(Operators.OperatorRevolveCurves)
    
    bpy.utils.register_class(Operators.OperatorBirail)
    bpy.utils.register_class(Operators.OperatorSweepAndMorph)
    
    bpy.utils.register_class(Operators.OperatorSetOriginsToStart)
    bpy.utils.register_class(Operators.OperatorSplinesSetResolution)
    bpy.utils.register_class(Operators.OperatorSplinesRemoveZeroSegment)
    bpy.utils.register_class(Operators.OperatorSplinesRemoveShort)
    bpy.utils.register_class(Operators.OperatorSplinesJoinNeighbouring)
    
    bpy.utils.register_class(Panel.Panel)
    

    
def unregister():
    bpy.utils.unregister_class(Panel.Panel)
    
    bpy.utils.unregister_class(Operators.OperatorSplinesJoinNeighbouring)
    bpy.utils.unregister_class(Operators.OperatorSplinesRemoveShort)
    bpy.utils.unregister_class(Operators.OperatorSplinesRemoveZeroSegment)
    bpy.utils.unregister_class(Operators.OperatorSplinesSetResolution)
    bpy.utils.unregister_class(Operators.OperatorSetOriginsToStart)
    
    bpy.utils.unregister_class(Operators.OperatorSweepAndMorph)
    bpy.utils.unregister_class(Operators.OperatorBirail)
    
    bpy.utils.unregister_class(Operators.OperatorRevolveCurves)
    bpy.utils.unregister_class(Operators.OperatorSweepCurves)
    bpy.utils.unregister_class(Operators.OperatorLoftCurves)
    bpy.utils.unregister_class(Operators.OperatorIntersectCurves)
    
    bpy.utils.unregister_class(Operators.OperatorOriginToSpline0Start)
    bpy.utils.unregister_class(Operators.OperatorSegmentsInfo)
    bpy.utils.unregister_class(Operators.OperatorSplinesInfo)
    bpy.utils.unregister_class(Operators.OperatorCurveLength)
    bpy.utils.unregister_class(Operators.OperatorCurveInfo)

    bpy.utils.unregister_class(Operators.OperatorSelectionInfo)

    bpy.utils.unregister_class(CurveTools2Settings)

    bpy.utils.unregister_class(Properties.CurveTools2SelectedObject)

        
if __name__ == "__main__":
    register()
