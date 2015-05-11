import time

import bpy
from bpy.props import *
import bpy.app



class CurveTools2SelectedObject(bpy.types.PropertyGroup):
    name = StringProperty(name = "name", default = "??")
        
        
    def __getattr__(self, attrName):
        # general blender object
        if attrName == "blenderObject":
            try: rvObject = bpy.data.objects[self.name]
            except: rvObject = None
            
            return rvObject
            
        if attrName == "type":
            try: rvType = self.blenderObject.type
            except: rvType = None
            
            return rvType
            
        # curve object
        if attrName == "isCurve":
            try: rvBool = (self.blenderObject.type == "CURVE")
            except: rvBool = False
            
            return rvBool
            
        if attrName == "curveData":
            if not self.isCurve: return None
            
            try: rvData = self.blenderObject.data
            except: rvData = None
            
            return rvData
            
        if attrName == "curveSplines":
            try: rvSplines = self.curveData.splines
            except: rvSplines = None
            
            return rvSplines
            
        if attrName == "nrSplines":
            try: rvNrSplines = len(self.curveSplines)
            except: rvNrSplines = None
            
            return rvNrSplines
            
        if attrName == "curveType":
            try: rvType = self.curveSplines[0].type
            except: rvType = None
            
            return rvType
        
    
    @staticmethod
    def UpdateThreadTarget(lock, sleepTime, selectedObjectNames, selectedBlenderObjectNames):
        time.sleep(sleepTime)
        
        newSelectedObjectNames = []
        
        for name in selectedObjectNames:
            if name in selectedBlenderObjectNames: newSelectedObjectNames.append(name)
            
        for name in selectedBlenderObjectNames:
            if not (name in selectedObjectNames): newSelectedObjectNames.append(name)
            
        # sometimes it still complains about the context
        try:
            nrNewSelectedObjects = len(newSelectedObjectNames)
            bpy.context.scene.curvetools.NrSelectedObjects = nrNewSelectedObjects
            
            selectedObjects = bpy.context.scene.curvetools.SelectedObjects
            selectedObjects.clear()
            for i in range(nrNewSelectedObjects): selectedObjects.add()
            for i, newSelectedObjectName in enumerate(newSelectedObjectNames):
                selectedObjects[i].name = newSelectedObjectName
                
            selectedCurves = CurveTools2SelectedObject.GetSelectedCurves()
            bpy.context.scene.curvetools.NrSelectedCurves = len(selectedCurves)
        except: pass
        
        
    @staticmethod
    def GetSelectedBlenderObjects():
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        
        rvObjects = []
        for selObj in selectedObjects: rvObjects.append(selObj.blenderObject)
        
        return rvObjects
        
        
    @staticmethod
    def GetSelectedCurves():
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        
        rvCurves = []
        for selObj in selectedObjects: 
            if selObj.isCurve: rvCurves.append(selObj.blenderObject)
        
        return rvCurves
        
        
    @staticmethod
    def GetSelectedBlenderObjects():
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        
        rvObjects = []
        for selObj in selectedObjects: rvObjects.append(selObj.blenderObject)
        
        return rvObjects

        
    @staticmethod
    def GetSelectedObjectNames():
        selectedObjects = bpy.context.scene.curvetools.SelectedObjects
        
        rvNames = []
        selectedObjectValues = selectedObjects.values()
        for selectedObject in selectedObjectValues: rvNames.append(selectedObject.name)
        
        return rvNames
        
        
    @staticmethod
    def GetSelectedBlenderObjectNames():
        blenderSelectedObjects = bpy.context.selected_objects
        
        rvNames = []
        for blObject in blenderSelectedObjects: rvNames.append(blObject.name)
        
        return rvNames
        
