import bpy

from . import Operators


def TestDriveCT2():
    print("hello")
    return 0.5


class Panel(bpy.types.Panel):
    bl_label = "Curve Tools 2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    
    @classmethod
    def poll(cls, context):
        currDriverFunc = bpy.app.driver_namespace.get("driveLoftCT2")
        if currDriverFunc is None:
            print("-- extending bpy.app.driver_namespace: driveLoftCT2")
            bpy.app.driver_namespace["driveLoftCT2"] = Operators.OperatorLoftCurves.driveLoft

            
        if len(context.selected_objects) > 0:
            return (context.active_object.type == "CURVE")
        
        
    def draw(self, context):
        # Selection
        colInfo = self.layout.column(align=True)
        colInfo.label(text = "Selection info:")
        split = colInfo.split()
            
        colSelInfo = split.column(align=True) 
        colSelInfo.operator("curvetools2.operatorselectioninfo", text = "Ordered list")
        colSelInfo.prop(context.scene.curvetools, "NrSelectedObjects", text = "# Objects")
        colSelInfo.prop(context.scene.curvetools, "NrSelectedCurves", text = "# Curves")
        
        colCrvInfo = split.column(align=True) 
        colCrvInfo.operator("curvetools2.operatorcurveinfo", text = "Curve")
        colCrvInfo.operator("curvetools2.operatorsplinesinfo", text = "Splines")
        colCrvInfo.operator("curvetools2.operatorsegmentsinfo", text = "Segments")
        colCrvInfo.separator()
        colCrvInfo.operator("curvetools2.operatorcurvelength", text = "Calc Curve Length")
        colCrvInfo.prop(context.scene.curvetools, "CurveLength", text = "")
                
        
        # Operators on 2 curves
        col2Crv = self.layout.column(align=True)
        col2Crv.label(text = "Operators on 2 curves:")
        
        colGen2 = col2Crv.column(align=True)
        split = colGen2.split()
        colLS = split.column(align=True)
        colLS.operator("curvetools2.operatorloftcurves", text = "Loft")
        colLS.operator("curvetools2.operatorsweepcurves", text = "Sweep")
        colRev = split.column(align=True)
        colRev.operator("curvetools2.operatorrevolvecurves", text = "Revolve")
        colRev.prop(context.scene.curvetools, "AngularResolution", text = "AngRes")
        col2Crv.separator()
        
        colInt = col2Crv.column(align=True)
        split = colInt.split()
        colIntBtn = split.column(align=True)
        colIntBtn.operator("curvetools2.operatorintersectcurves", text = "Intersect")
        colIntBtn.prop(context.scene.curvetools, "LimitDistance", text = "LimDst")
        colIntSett = split.column(align=True)
        colIntSett.prop(context.scene.curvetools, "IntersectCurvesAlgorithm", text = "Algo")
        colIntSett.separator()
        colIntSett.prop(context.scene.curvetools, "IntersectCurvesMode", text = "Mode")
        colIntSett.separator()
        colIntSett.prop(context.scene.curvetools, "IntersectCurvesAffect", text = "Affect")
        

        # Operators on 3 curves
        col3Crv = self.layout.column(align=True)
        col3Crv.label(text = "Operators on 3 curves:")
        colGen3 = col3Crv.column(align=True)
        row = colGen3.row(align = True)
        row.operator("curvetools2.operatorbirail", text = "Birail")
        row.operator("curvetools2.operatorsweepandmorph", text = "SweepAndMorph")

        
        # Operators on 1 or more curves
        col1OMCrv = self.layout.column(align=True)
        col1OMCrv.label(text = "Operators on 1 or more curves:")
        
        col3SetRem = col1OMCrv.column(align=True)
        split = col3SetRem.split()
        col3Set = split.column(align=True)
        col3Set.operator("curvetools2.operatorsetoriginstostart", text = "Set origin to start")
        col3Set.separator()
        col3Set.operator("curvetools2.operatorsplinessetresolution", text = "Set resolution")
        col3Set.prop(context.scene.curvetools, "SplineResolution", text = "")
        col3Rem = split.column(align=True)
        col3Rem.operator("curvetools2.operatorsplinesremovezerosegment", text = "Remove 0-seg-splines")
        col3Rem.separator()
        col3Rem.operator("curvetools2.operatorsplinesremoveshort", text = "Remove short splines")
        col3Rem.prop(context.scene.curvetools, "SplineRemoveLength", text = "LimLen")
        col3SetRem.separator()
        
        col3Join = col1OMCrv.column(align=True)
        split = col3Join.split()
        col3JoinBtn = split.column(align=True)
        col3JoinBtn.operator("curvetools2.operatorsplinesjoinneighbouring", text = "Join splines")
        col3JoinBtn.prop(context.scene.curvetools, "SplineJoinDistance", text = "LimDst")
        col3JoinSett = split.column(align=True)
        col3JoinSett.prop(context.scene.curvetools, "SplineJoinStartEnd", text = "Only at start & end")
        col3JoinSett.prop(context.scene.curvetools, "SplineJoinMode", text = "Mode")
        
        
