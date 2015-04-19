bl_info = {
    "name": "arrange tools",
    "category": "Object",
}

import bpy


def ObjectArrangeB(self, isX, isY, isZ, ofsX=0, ofsY=0, ofsZ=0):
    def order(sels, isX, isY, isZ, ofsX=0, ofsY=0, ofsZ=0):
        if len(sels[:]) > 1:
            # VARIABLES
            dif = sels[-1].location - sels[0].location
            chunkglobal = dif / (len(sels[:]) - 1)
            chunkx = 0
            chunky = 0
            chunkz = 0
            deltafst = sels[0].location

            # ORDENA
            for idx in range(0, len(sels)):
                obj = sels[idx]
                if isX:  obj.location.x = deltafst[0] + chunkx
                if isY:  obj.location.y = deltafst[1] + chunky
                if isZ:  obj.location.z = deltafst[2] + chunkz
                if ofsX:
                    chunkx += ofsX
                else:
                    chunkx += chunkglobal[0]
                if ofsY:
                    chunky += ofsY
                else:
                    chunky += chunkglobal[1]
                if ofsZ:
                    chunkz += ofsZ
                else:
                    chunkz += chunkglobal[2]
        else:
            self.report({'ERROR'}, "Selection is only 1!")

    sels = bpy.context.selected_objects
    if isX:
        order(sorted(sels, key=lambda obj: obj.location.x), isX, False, False, ofsX=ofsX)
    if isY:
        order(sorted(sels, key=lambda obj: obj.location.y), False, isY, False, ofsY=ofsY)
    if isZ:
        order(sorted(sels, key=lambda obj: obj.location.z), False, False, isZ, ofsZ=ofsZ)


class DialogArrangeB(bpy.types.Operator):
    bl_idname = "object.arrange_objs"
    bl_label = "Arrange object"
    bl_options = {'REGISTER', 'UNDO'}  # change after ok
    BoolX = bpy.props.BoolProperty(name="X")
    BoolY = bpy.props.BoolProperty(name="Y")
    BoolZ = bpy.props.BoolProperty(name="Z")
    OffsetX = bpy.props.FloatProperty(name='offset')
    OffsetY = bpy.props.FloatProperty(name='offset')
    OffsetZ = bpy.props.FloatProperty(name='offset')

    def execute(self, context):
        ObjectArrangeB(self, self.BoolX, self.BoolY, self.BoolZ, self.OffsetX, self.OffsetY, self.OffsetZ)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.BoolX = False
        self.BoolY = False
        self.Boolz = False
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row()
        row.prop(self, "BoolX")
        row.prop(self, "OffsetX")
        row = col.row()
        row.prop(self, "BoolY")
        row.prop(self, "OffsetY")
        row = col.row()
        row.prop(self, "BoolZ")
        row.prop(self, "OffsetZ")


def register():
    bpy.utils.register_class(DialogArrangeB)


def unregister():
    bpy.utils.unregister_class(DialogArrangeB)


if __name__ == "__main__":
    register()