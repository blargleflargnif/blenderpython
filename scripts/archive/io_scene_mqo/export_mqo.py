
import os
import shutil
from math import radians

import bpy
from bpy.props import *
from mathutils import *

#Default Config
def_scale = 100
def_axis = 1
def_shader = 2
def_selection = 0

#Config Class
class OptionConfig:
	def __init__(self, context, path, scale=def_scale, axis=def_axis, shader=def_shader, selection=def_selection):
		self.context = context
		self.path = path
		self.scale = scale
		self.axis = int(axis)
		self.shader = shader
		self.selection = int(selection)

class OutputData:
	def __init__(self):
		self.mesh = None
		self.matrix = None
		self.depth = 0
		self.visivle = 15
		self.lock = 0
		
#Writing Metasequoia File
def writeMQO(config):
	print("\n----------Export----------\n")
	print("Filename:" + config.path)

	scene = config.context.scene
	buf = open(config.path, "w")

	buf.write("Metasequoia Document\n")
	buf.write("Format Text Ver 1.0\n\n")

	buf.write("Scene {\n")
	buf.write("\tpos 0.0000 0.0000 1806.0579\n")
	buf.write("\tlookat -0.4346 9.5125 14.4147\n")
	buf.write("\thead 7.1400\n")
	buf.write("\tpich 0.2700\n")
	buf.write("\tortho 0\n")
	buf.write("\tzoom2 8.0579\n")
	buf.write("\tamb 0.250 0.250 0.250\n")
	buf.write("}\n")

	meshes = []
	mtrls = []
	mtrlnames = []
	
	objects = scene.objects.values()
	
	#Selection Objects
	if(config.selection):
		objects = config.context.selected_objects #Selected Only
	
	mesh_objects = [target for target in objects if target.type == "MESH"]
	
	for obj in mesh_objects:
		#Get Mesh
		mesh = obj.data
		materials = mesh.materials
		
		for mtrl in materials:
			if(not mtrl.name in mtrlnames):
				mtrlnames.append(mtrl.name)
				mtrls.append(mtrl)
				
		#Set Level
		parent = obj.parent
		level = 0
		
		while(parent):
			if((parent in mesh_objects) and parent.type=="MESH"):
				level += 1
			else:
				break
				
			parent = parent.parent
			
		#Hidden
		visible = 15
		if(obj.hide):
			visible = 0
			
		#Lock
		lock = 0
		if(obj.hide_select):
			lock = 1
			
		data = OutputData()
		data.mesh = mesh
		data.matrix = obj.matrix_world.copy()
		data.depth = level
		data.visible = visible
		data.lock = lock
		
		meshes.append(data)
			
	#Material
	if(len(mtrls) > 0):
		buf.write("Material " + str(len(mtrls)) + " {\n")
		for mtrl in mtrls:
			buf.write("\t\"" + mtrl.name + "\" ")
			buf.write("shader(" + str(config.shader) + ") ")
			buf.write("col(" + "{:.3f} {:.3f} {:.3f} {:.3f}".format(mtrl.diffuse_color[0], mtrl.diffuse_color[1], mtrl.diffuse_color[2], mtrl.alpha) + ") ")
			buf.write("dif(" + "{:.3f}".format(mtrl.diffuse_intensity) + ") ")
			buf.write("amb(" + "{:.3f}".format(mtrl.mirror_color[0]) + ") ")
			buf.write("emi(" + "{:.3f}".format(mtrl.emit) + ") ")
			buf.write("spc(" + "{:.3f}".format(mtrl.specular_color[0]) + ") ")
			buf.write("power(" + "{:.2f}".format(mtrl.specular_intensity) + ")")
			
			#Texture
			slots = mtrl.texture_slots
			for slot in slots:
				if(slot != None and slot.texture.type == "IMAGE"):
					imagePath = slot.texture.image.filepath
					imageName = os.path.basename(imagePath)
					
					buf.write(" tex(\"" + imageName + "\")")
					
					#Copy ImageFile
					if(os.path.exists(imagePath)):
						dirName = os.path.dirname(config.path).replace("\\", "/")
						
						if(not os.path.exists(dirName + "/" + imageName)):
							shutil.copy(imagePath, dirName)
						
			buf.write("\n")
		buf.write("}\n")

	#Object
	for data in meshes:
		mesh = data.mesh
		matrix = data.matrix
		level = data.depth
		visible = data.visible
		lock = data.lock
		
		buf.write("Object \"" + mesh.name + "\" {\n")
		
		buf.write("\tdepth " + str(level) + "\n")
		buf.write("\tfolding 0\n")
		buf.write("\tscale 1.000000 1.000000 1.000000\n")
		buf.write("\trotation 0.000000 0.000000 0.000000\n")
		buf.write("\ttranslation 0.000000 0.000000 0.000000\n")
		buf.write("\tvisible " + str(visible) + "\n")
		buf.write("\tlocking " + str(lock) + "\n")
		buf.write("\tshading 1\n")
		buf.write("\tfacet 60.0\n")
		buf.write("\tcolor 0.000 0.000 0.000\n")
		buf.write("\tcolor_type 0\n")
	
		#Vertex
		buf.write("\tvertex " + str(len(mesh.vertices)) + " {\n")
		transformMatrix = Matrix()
		
		#Scaling
		transformMatrix *= Matrix.Scale(config.scale, 4, Vector((1, 0, 0)))
		transformMatrix *= Matrix.Scale(config.scale, 4, Vector((0, 1, 0)))
		transformMatrix *= Matrix.Scale(config.scale, 4, Vector((0, 0, 1)))
		
		#Change AxisY
		if(config.axis == 1):
			transformMatrix *= Matrix.Rotation(radians(-90), 4, "X")
			
		#Change AxisZ
		if(config.axis == 2):
			transformMatrix *= Matrix.Rotation(radians(90), 4, "X")
		
		for vertex in mesh.vertices:
			#Transform
			position = vertex.co.copy() * matrix
			position *= transformMatrix
			buf.write("\t\t" + "{:.4f} {:.4f} {:.4f}".format(position[0], position[1], position[2]) + "\n")
			
		buf.write("\t}\n")

		#Index
		mtrl = mesh.materials
		
		buf.write("\tface " + str(len(mesh.faces)) + " {\n")
		index1 = [0,2,1]
		index2=[0,3,2,1]
		faces = mesh.faces
		uv_faces = []
		
		if((len(mesh.uv_textures) > 0) and (mesh.uv_textures.active != None)):
			uv_faces = mesh.uv_textures.active.data[:]
		
		for i in range(len(faces)):
			index = faces[i].vertices
			count = len(index)
			
			buf.write("\t\t" + str(count) + " V(")
		
			for j in range(count):
				if(count == 3):
					buf.write(str(index[index1[j]]))
					
				else:
					buf.write(str(index[index2[j]]))
					
				if(j < count - 1):
					buf.write(" ")
				else:
					buf.write(") ") 
			
			if(len(mtrl) > 0):
				ma = mtrl[mesh.faces[i].material_index]
				buf.write("M(" + str(mtrls.index(ma)) + ")")
				
			if(len(uv_faces) > 0):
				buf.write(" UV(")
				uv = uv_faces[i]
				texcoord = [uv.uv1, uv.uv2, uv.uv3, uv.uv4]
				texlist = []
				
				for j in range(count):
					if(count == 3):
						texlist.append(texcoord[index1[j]])
					else:
						texlist.append(texcoord[index2[j]])
				
				for j in range(count):
					uv = texlist[j]
					buf.write("{:.5f} {:.5f}".format(uv[0], 1 - uv[1]))
						
					if(j < count - 1):
						buf.write(" ")
					else:
						buf.write(")")

			buf.write("\n")

		buf.write("\t}\n")
		buf.write("}\n")
	
	buf.write("Eof")
	buf.close()

	print("finished!")

AxisModes = []
AxisModes.append(("0", "Default", ""))
AxisModes.append(("1", "AxisY(Rotate X-90)", ""))
AxisModes.append(("2", "AxisZ(Rotate X90)", ""))

ShaderModes = []
ShaderModes.append(("0", "Classic", ""))
ShaderModes.append(("1", "Constant", ""))
ShaderModes.append(("2", "Lambert", ""))
ShaderModes.append(("3", "Phong", ""))
ShaderModes.append(("4", "Blinn", ""))

SystemModes = []
SystemModes.append(("0", "Right-Hand(Default)", ""))
SystemModes.append(("1", "Left-Hand", ""))

SelectionModes = []
SelectionModes.append(("0", "All Objects", ""))
SelectionModes.append(("1", "Selected Only", ""))

class MetasequoiaExporter(bpy.types.Operator):
    """Export to the Metasequoia format (.mqo)"""

    bl_idname = "export.metasequoia"
    bl_label = "Export Metasequoia"
    
    filepath = StringProperty()
    filename = StringProperty()
    directory = StringProperty()
    
    #Option
    ExportScale = FloatProperty(name="Scale", description="Change of scale value.", min=0.01, max=100, soft_min=0.01, soft_max=10, default=def_scale)
    ExportAxis = EnumProperty(name="Upper Axis", description="Setting of the above axis.", items=AxisModes, default=str(def_axis))
    ExportShader = EnumProperty(name="Select Shader", description="Schaeder's selection.", items=ShaderModes, default=str(def_shader))
    ExportSelection = EnumProperty(name="Selection Objects", description="Selection of output object.", items=SelectionModes, default=str(def_selection))
    
    #Config
    def execute(self, context):
        writeMQO( OptionConfig(context, self.filepath, self.ExportScale, self.ExportAxis, self.ExportShader, self.ExportSelection) )
        return {"FINISHED"}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}
