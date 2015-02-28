#!/usr/bin/python3
# To change this template, choose Tools | Templates
# and open the template in the editor.
#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

bl_info = {
    "name": "Import: Sound to Animation Data",
    "author": "Vlassius",
    "version": "0.0.1",
    "blender": (2, 5, 3),
    "location": "File > Import > Sound to Animation",
    "description": "Extract movement from sound file, to help in animations. Easy way to install: <blender dir>/2.53/scripts/templates. Into Blender: Script screen-> Text-> ScriptsTemplates -> import_sound_to_anim.py-> Run Script. See the Object Panel at the end.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import/Export"}

"""
-- Extract movement from sound file, to help in animation - export script v0.0.1 --<br> 

- NOTES:
- This script takes a wav file and get sound "movement" to help you in sync the movement to words in the wave file. <br>
- Blender 2.5.3.1 r31540

- v0.0.1
- Initial version

Credit to:
Vlassius

- http://vlassius.com.br
- vlassius@vlassius.com.br

"""

import bpy
from bpy.props import *

import wave

#TODO
#    Arrumar - não tem rotacao para objeto - so transformacao
#    alterar OBJETO NOMEADO

#
#    Colocar opção de arrendondamento 0~3=0 4~6=5 7~9=10 
#    Pode ajudar muito no optimizer
#
#    Colocar Escolha do Canal!!
#


def wavimport(infile, context):
    #================================================================================================== 
    # Insert Key Frame
    #================================================================================================== 

    #Instrução -> Selecione o objeto -> escolha o arquivo e ser processado -> Aguarde processamento
    #o processamento pode levar varios minutos. Veja o andamento pela tela terminal 
    
    iAudioSensib= int(context.scene.audio_sense)-1    #sensibilidade volume do audio 0 a 5. Quanto maior, mais sensibilidade
    if iAudioSensib <0: iAudioSensib=0
    elif iAudioSensib>5: iAudioSensib=5
    
    iFramesPorSeg= int(context.scene.frames_per_second)  #Frames por segundo para key frame
    iMovPorSeg= int(context.scene.action_per_second)      #Sensibilidade de movimento. 3= 3 movimentos por segundo
    iDivScala= int(context.scene.action_escale)     #scala do valor do movimento. [se =1 - 0 a 255 ] [se=255 - 0,00000 a 1,00000] [se=1000 - 0 a 0.255]
    
    bNaoValorIgual=True
    if context.scene.action_valor_igual: bNaoValorIgual= False    # não deixa repetir valores
    
    iStartFrame= int(context.scene.frames_initial)

    iMaxValue= int(context.scene.action_max_value)
    iMinValue= int(context.scene.action_min_value)
    
    strObjName= context.scene.object_field

    bEixoX= context.scene.action_eixo_x    
    bEixoY= context.scene.action_eixo_y
    bEixoZ= context.scene.action_eixo_z

    # atencao, nao é boolean
    iEixoXneg= iEixoYneg= iEixoZneg=1
    if context.scene.action_eixo_NEG_x: iEixoXneg=-1 
    if context.scene.action_eixo_NEG_y: iEixoYneg=-1
    if context.scene.action_eixo_NEG_z: iEixoZneg=-1
    
    bEscalaX=context.scene.action_escala_x
    bEscalaY=context.scene.action_escala_y
    bEscalaZ=context.scene.action_escala_z

    # atencao, nao é boolean
    iEscalaYneg= iEscalaZneg= iEscalaXneg=1
    if context.scene.action_escala_NEG_x: iEscalaXneg=-1 
    if context.scene.action_escala_NEG_y: iEscalaYneg=-1
    if context.scene.action_escala_NEG_z: iEscalaZneg=-1   

    bRotationX=context.scene.action_rotation_x
    bRotationY=context.scene.action_rotation_y
    bRotationZ=context.scene.action_rotation_z

    # atencao, nao é boolean
    iRotationNeg=1   # usado com BONES para angulo negativo!!!
    if context.scene.action_rotation_signal_to_bones: iRotationNeg=-1     

    # atencao, nao é boolean
    iRotationXneg= iRotationYneg= iRotationZneg=1
    if context.scene.action_rotation_NEG_x: iRotationXneg= -1 
    if context.scene.action_rotation_NEG_y: iRotationYneg= -1
    if context.scene.action_rotation_NEG_z: iRotationZneg= -1

    iMinBaseX= int(context.scene.action_base_location_x)
    iMinBaseY= int(context.scene.action_base_location_y)
    iMinBaseZ= int(context.scene.action_base_location_z)
    
    iMinScaleBaseX= int(context.scene.action_base_scale_x)
    iMinScaleBaseY= int(context.scene.action_base_scale_y)
    iMinScaleBaseZ= int(context.scene.action_base_scale_z)   

    iRotationAxisBaseX= int(context.scene.action_base_rotation_x)
    iRotationAxisBaseY= int(context.scene.action_base_rotation_y)
    iRotationAxisBaseZ= int(context.scene.action_base_rotation_z)   

    bEixo=False
    if bEixoX: bEixo=True
    if bEixoY: bEixo=True
    if bEixoZ: bEixo=True
    
    bEscala=False
    if bEscalaX: bEscala=True
    if bEscalaY: bEscala=True
    if bEscalaZ: bEscala=True

    bRotacao=False
    if bRotationX: bRotacao=True 
    if bRotationY: bRotacao=True
    if bRotationZ: bRotacao=True

    bLimitValue=False    #limita ou nao o valor - velocidade        
    if iMinValue!= 0: bLimitValue= True
    if iMaxValue!= 255: bLimitValue= True


    #DivMovPorSeg Padrao - taxa 4/s ou a cada 0,25s  => iFramesPorSeg/DivMovPorSeg= ~0.25
    for i in range(iFramesPorSeg):
        DivMovPorSeg=iFramesPorSeg/(i+1)
        if iFramesPorSeg/DivMovPorSeg >=iMovPorSeg:
            break    

    array= SoundConv(infile, int(DivMovPorSeg), iAudioSensib, iFramesPorSeg)

    print('')
    print("================================================================")   
    from time import strftime
    print(strftime("Start Import:  %H:%M:%S"))
    print("================================================================")   
    print('')

    ilocationXAnt=0
    ilocationYAnt=0
    ilocationZAnt=0                
    iscaleXAnt=0
    iscaleYAnt=0
    iscaleZAnt=0
    iRotateValAnt=0
    ivalAnt=0
    
    if array:
        for i in range(len(array)):

            # opcao de NAO colocar valores iguais sequenciais
            if bNaoValorIgual and ivalAnt== array[i]:
                print("Importing Frame: "+str(i)+"\tof "+str(len(array)-1) + "\t(skipped by optimizer)")
            else: 
                ivalAnt= array[i]
                
                # otimizacao - não preciso mais que 2 valores iguais. pular key frame intermediario - Ex b, a, -, -, -, a
                if i< len(array)-1 and i>1 and array[i] == array[i-1] and array[i]==array[i+1]:# valor atual == anterior e posterior -> pula
                        print("Importing Frame: "+str(i)+"\tof "+str(len(array)-1) + "\t(skipped by optimizer)")
                else:           
                        ival=array[i]/iDivScala
                        if bLimitValue:
                            if ival > iMaxValue: ival=iMaxValue
                            if ival < iMinValue: ival=iMinValue
                                        
                        bpy.context.scene.frame_current = i+iStartFrame                                             
                        if len(strObjName)>0:
                            if bpy.context.active_object.type=='ARMATURE':                    
                                print("Sorry, this script does not allow use of ARMATURE by name.")
                                print("Please, Select the ARMATURE and don't use the name.")
                                return False
            
                            if bpy.context.active_object.type=='LATTICE':   #precisa ser objeto ativo. Nao achei como passar para editmode
                                print('Sorry, LATTICES cannot be used in this script.')
                                return False
    
                            ###############  MESH  ######################
                            if bpy.context.active_object.type=='MESH':   #precisa fazer objeto ativo
                                if bEixo:                                
                                    if bEixoX: bpy.context.scene.objects[strObjName].location.x = ival*iEixoXneg+iMinBaseX                                
                                    if bEixoY: bpy.context.scene.objects[strObjName].location.y = ival*iEixoYneg+iMinBaseY
                                    if bEixoZ: bpy.context.scene.objects[strObjName].location.z = ival*iEixoZneg+iMinBaseZ
                
                                if bEscala:
                                    if bEscalaX: bpy.context.scene.objects[strObjName].scale.x = ival*iEscalaXneg+iMinScaleBaseX
                                    if bEscalaY: bpy.context.scene.objects[strObjName].scale.y = ival*iEscalaYneg+iMinScaleBaseY
                                    if bEscalaZ: bpy.context.scene.objects[strObjName].scale.z = ival*iEscalaZneg+iMinScaleBaseZ
#TODO
#ERROOOOoooooo
#

                                if bRotacao:
                                    if bRotationX: bpy.context.scene.objects[strObjName].rotation.x = ival*iRotationXneg+iRotationAxisBaseX
                                    if bRotationY: bpy.context.scene.objects[strObjName].rotation.y = ival*iRotationYneg+iRotationAxisBaseY
                                    if bRotationZ: bpy.context.scene.objects[strObjName].rotation.z = ival*iRotationZneg+iRotationAxisBaseZ                       
                            
                        else: # nao nomeado
                            if bpy.context.active_object.type=='MESH' or bpy.context.active_object.type=='CAMERA':   #precisa fazer objeto ativo
                                if bEixo:                   
                                    if bEixoX: bpy.context.active_object.location.x = ival*iEixoXneg+iMinBaseX
                                    if bEixoY: bpy.context.active_object.location.y = ival*iEixoYneg+iMinBaseY
                                    if bEixoZ: bpy.context.active_object.location.z = ival*iEixoZneg+iMinBaseZ               
                                
                                if bEscala:
                                    if bEscalaX: bpy.context.active_object.scale.x = ival*iEscalaXneg+iMinScaleBaseX
                                    if bEscalaY: bpy.context.active_object.scale.y = ival*iEscalaYneg+iMinScaleBaseY
                                    if bEscalaZ: bpy.context.active_object.scale.z = ival*iEscalaZneg+iMinScaleBaseZ                                        

#
#TODO
#
#FAZER LATTICE!!!!
#
                            if bpy.context.active_object.type=='LATTICE' or bpy.context.active_object.type=='ARMATURE' or (bpy.context.active_object.type=='MESH' and bRotacao) or (bpy.context.active_object.type=='CAMERA' and bRotacao): 
                                                
                                ###############  LATICE ######################
                                if bpy.context.active_object.type=='LATTICE':   #precisa ser objeto ativo. Nao achei como passar para editmode
                                    print('Sorry, LATTICES cannot be used in this script')
                                    return False
                                    
                                    if bpy.context.mode!= 'EDIT_LATTICE':    #editmode                                                      
                                        bpy.ops.object.editmode_toggle()
                                        
            
                                ###############  BONE ######################
                                if bpy.context.active_object.type=='ARMATURE':   #precisa ser objeto ativo. Nao achei como passar para editmode
                                    if bpy.context.mode!= 'POSE':    #posemode                                                      
                                        bpy.ops.object.posemode_toggle()
    
                                ###############  BONE & LATTICE ######################    
                                if bEixo:
                                    if ilocationXAnt!=0 or ilocationYAnt!=0 or ilocationZAnt!=0: 
                                        bpy.ops.transform.translate(value=(ilocationXAnt*-1, ilocationYAnt*-1, ilocationZAnt*-1), constraint_axis=(bEixoX, bEixoY,bEixoZ), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)                                            
                                    
                                    ilocationX=ilocationY=ilocationZ=0                
                                    if bEixoX: ilocationX = ival*iEixoXneg+iMinBaseX
                                    if bEixoY: ilocationY = ival*iEixoYneg+iMinBaseY
                                    if bEixoZ: ilocationZ = ival*iEixoZneg+iMinBaseZ                    
                                    bpy.ops.transform.translate(value=(ilocationX, ilocationY, ilocationZ), constraint_axis=(bEixoX, bEixoY,bEixoZ), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
                                    ilocationXAnt= ilocationX
                                    ilocationYAnt= ilocationY
                                    ilocationZAnt= ilocationZ                       
            
                                if bEscala:
                                    if iscaleXAnt!=0 or iscaleYAnt!=0 or iscaleZAnt!=0:
                                        tmpscaleXAnt=0
                                        tmpscaleYAnt=0
                                        tmpscaleZAnt=0
                                        if iscaleXAnt: tmpscaleXAnt=1/iscaleXAnt
                                        if iscaleYAnt: tmpscaleYAnt=1/iscaleYAnt
                                        if iscaleZAnt: tmpscaleZAnt=1/iscaleZAnt                            
                                        bpy.ops.transform.resize(value=(tmpscaleXAnt, tmpscaleYAnt, tmpscaleZAnt ), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)                                            
                                    
                                    iscaleX=iscaleY=iscaleZ=0                
                                    if bEscalaX: iscaleX = ival*iEscalaXneg+iMinScaleBaseX
                                    if bEscalaY: iscaleY = ival*iEscalaYneg+iMinScaleBaseY
                                    if bEscalaZ: iscaleZ = ival*iEscalaZneg+iMinScaleBaseZ                        
                                    bpy.ops.transform.resize(value=(iscaleX, iscaleY, iscaleZ), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
                                    iscaleXAnt= iscaleX
                                    iscaleYAnt= iscaleY
                                    iscaleZAnt= iscaleZ                       
    
                                if bpy.context.active_object.type=='ARMATURE' or bpy.context.active_object.type=='MESH':   #precisa ser objeto ativo. Nao achei como passar para editmode
                                    if bRotacao:                        
                                        if iRotateValAnt!=0: 
                                            bpy.ops.transform.rotate(value= (iRotateValAnt*-1,), axis=(iRotationAxisBaseX, iRotationAxisBaseY, iRotationAxisBaseZ), constraint_axis=(bRotationX, bRotationY, bRotationZ), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)                                                                   
                                        
                                        bpy.ops.transform.rotate(value= (ival*iRotationNeg,), axis=(iRotationAxisBaseX, iRotationAxisBaseY, iRotationAxisBaseZ), constraint_axis=(bRotationX, bRotationY, bRotationZ), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
                                        iRotateValAnt= ival*iRotationNeg
       
                                #tira o LATTICE do modo EDIT
            #                    if bpy.context.mode== 'EDIT_LATTICE':    #editmode                                                      
            #                        bpy.ops.object.editmode_toggle()
                                    
            #                    bpy.context.active_object.update(bpy.context.scene)
                
                        if bEixo and not bEscala and not bRotacao:
                            bpy.ops.anim.keyframe_insert_menu(type=-1)
                            
                        if bRotacao and not bEixo and not bEscala:
                            bpy.ops.anim.keyframe_insert_menu(type=-2)
                            
                        if bEscala and not bEixo and not bRotacao:
                            bpy.ops.anim.keyframe_insert_menu(type=-3)               
            
                        if bEixo and bRotacao:
                            bpy.ops.anim.keyframe_insert_menu(type=-4)
                           
                        if bEscala and bEixo:
                            bpy.ops.anim.keyframe_insert_menu(type=-5)
            
                        if bEixo and bRotacao and bEscala:
                            bpy.ops.anim.keyframe_insert_menu(type=-6)
            
                        if bEscala and bRotacao:
                            bpy.ops.anim.keyframe_insert_menu(type=-7)
                                     
                    
                        print("Importing Frame: "+str(i)+"\tof "+str(len(array)-1) + "\tValue Base: "+ str(ival))
                        
                # FIm do ELSE otimizador 
            # Fim bNaoValorIgual
            
    print('')
    print("================================================================")   
    print(strftime("End Import:  %H:%M:%S - by Vlassius"))
    print("================================================================")   
    print('')
    
    
#================================================================================================== 
# Sound Converter
#================================================================================================== 

def SoundConv(File, DivSens, Sensibil, Resol):

    try:
        Wave_read= wave.open(File, 'rb')
    except IOError as e:
        print("File Open Error: ", e)
        return False

    NumCh=      Wave_read.getnchannels()
    SampW=      Wave_read.getsampwidth() // NumCh # 8, 16, 24 32 bits
    FrameR=     Wave_read.getframerate() // NumCh
    NumFr=      Wave_read.getnframes()
    ChkCompr=   Wave_read.getcomptype()
    
    if ChkCompr != "NONE":
        print('Formato de Compressão Nao Suportado ', ChkCompr)
        return False
    
    # com 8 bits/S - razao Sample/s por resolucao
    # usado para achar contorno da onda - achando picos 
    BytesResol= int(FrameR/Resol)
    
    # com 8 bits/S - razao Sample/s por resolucao
    # tamanho do array
    BytesDadosTotProcess= NumFr // BytesResol 
    
    print('')
    print("================================================================")   
    from time import strftime
    print(strftime("Go!  %H:%M:%S"))
    print("================================================================")   
    print('')   
    print('Audio Time: \t ' + str(NumFr//FrameR) + 's (' + str(NumFr//FrameR//60) + 'min)')
    print('Interactions: \t', BytesDadosTotProcess)
    print('Audio Frames: \t', NumFr)
    print('Frame Rate: \t', FrameR)
    print('Chan in File: \t', NumCh)
    print('Bit/Samp/Chan: \t', SampW*8)
    print('Channel in use: \t1 (TODO!!!!!!!!!!!!!!!!!!!!!!!!!)')
    print('Sensitivity: \t', Sensibil)
    print('DivMovim: \t', DivSens)
    print(' ')

    _array= bytearray(BytesDadosTotProcess)  # cria array
    j=0  # usado de indice
    

    # laço total leitura bytes
    # armazena dado de pico
    looptot= int(BytesDadosTotProcess // DivSens)
    for jj in range(looptot):      
        
        # caso de 2 canais (esterio)
        # uso apenas 2 bytes em 16 bits
        # [0] e [1] para CH L
        # [2] e [3] para CH R      
        # uso 1 byte se em 8 bits              
        ValorPico=0
        for i in range(BytesResol):            
            frame = Wave_read.readframes(DivSens)            
            if len(frame)==0: break

            if SampW ==1:
                if frame[0]> ValorPico: 
                    ValorPico= frame[0]               

            if SampW ==2:                # frame[0] baixa       frame[1] ALTA BIT 1 TEM SINAL
                if Sensibil ==0:
                    if frame[1] <127:    # se bit1 =0, usa o valor
                        fr = frame[1] << 1
                        if fr > ValorPico: 
                            ValorPico= fr               
                        
                if Sensibil ==4:
                    if frame[1] < 127:     # se bit1 =0, usa o valor
                        frame0= ((frame[0] & 0b11111100) >> 2) | ((frame[1] & 0b00000011) << 6)                        
                        if frame0 > ValorPico: 
                                ValorPico= frame0               

                if Sensibil ==3:
                    if frame[1] < 127:    # se bit1 =0, usa o valor
                        frame0= ((frame[0] & 0b11110000) >> 4) | ((frame[1] & 0b00001111) << 4)                        
                        if frame0 > ValorPico: 
                                ValorPico= frame0               

                if Sensibil ==2:
                    if frame[1] < 127:    # se bit1 =0, usa o valor
                        frame0= ((frame[0] & 0b11100000) >> 5) | ((frame[1] & 0b00011111) << 3)                        
                        if frame0 > ValorPico: 
                                ValorPico= frame0               

                if Sensibil ==1:
                    if frame[1] < 127:    # se bit1 =0, usa o valor
                        frame0= ((frame[0] & 0b11000000) >> 6) | ((frame[1] & 0b00111111) << 2)                        
                        if frame0 > ValorPico: 
                                ValorPico= frame0               

                if Sensibil ==5:
                    if frame[0] > ValorPico: 
                        ValorPico= frame[0]               


        for ii in range(DivSens):           
            _array[j]=ValorPico  # valor de pico encontrado
            j +=1;           # incrementa indice prox local
                
        print ("Sample-> " + str(ValorPico) + "\tAudio Frame # " + str(jj) + " of " + str(looptot-1))
                
# fim
#    print(_array)
    print("================================================================")   
    print(strftime("End Process:  %H:%M:%S"))
    print(strftime("End:  %H:%M:%S"))
    print("================================================================")   

    try:
        Wave_read.close()
    except:
        print('File Close Error') 

    return _array


#
#
#================================================================================================== 
#================================================================================================== 
#================================================================================================== 
#
#
# BLENDER Configuration - Blender Beta 2.5.3.1 r31540
#
#
#================================================================================================== 
#================================================================================================== 
#================================================================================================== 
#    
#

def getInputFilename(filename, context):
    print ("  Selected file = ",filename)
    checktype = filename.split('\\')[-1].split('.')[1]
    if checktype.upper() != 'WAV':
        print ("ERROR!! Selected file = ", filename)
        print ("ERROR!! Its not a .wav file")
        
        return   
    wavimport(filename, context)


class VIEW3D_PT_CustomMenuPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Import Movement From Wav File"
    
    

    #definicoes    
    def draw_header(self, context):
#        sce = context.scene
    
        #Nome do objeto
        context.scene.StringProperty(name="",
            attr="object_field",# this a variable that will set or get from the scene
            description="(OPTIONAL) Object Name. You can use the select object if this is blank.",
            maxlen= 1024,
            default= "")#this set the initial text
        
        #    iAudioSensib=0    #sensibilidade volume do audio 0 a 5. Quanto maior, mais sensibilidade
        context.scene.StringProperty(name="",
            attr="audio_sense",# this a variable that will set or get from the scene
            description="Audio Sensibility. Values from 1 to 6.",
            maxlen= 1,
            default= "1")#this set the initial text
        
        #    iFramesPorSeg=15  #Frames por segundo para key frame
        context.scene.StringProperty(name="",
            attr="frames_per_second",# this a variable that will set or get from the scene
            description="How much frames you want per second. Better Match your set up in Blender scene.",
            maxlen= 2,
            default= '30')#this set the initial text
        
        #    iMovPorSeg=1      #Sensibilidade de movimento. 3= 3 movimentos por segundo
        context.scene.StringProperty(name="",
            attr="action_per_second",# this a variable that will set or get from the scene
            description="How much actions per second",
            maxlen= 2,
            default= "4")#this set the initial text
        
        #    iDivScala=200     #scala do valor do movimento. [se =1 - 0 a 255 ] [se=255 - 0,00000 a 1,00000] [se=1000 - 0 a 0.255]
        context.scene.StringProperty(name="",
            attr="action_escale",# this a variable that will set or get from the scene
            description="Scale the result values. (if 1, values from 0 to 255) (if 1000, values from 0 to 0.255)",
            maxlen= 5,
            default= "100")#this set the initial text
        
        #    iMaxValue=255
        context.scene.StringProperty(name="",
            attr="action_max_value",# this a variable that will set or get from the scene
            description="Set the max value (cut). The max value ever is 255.",
            maxlen= 3,
            default= "255")#this set the initial text
        
        #    iMinValue=0
        context.scene.StringProperty(name="",
            attr="action_min_value",# this a variable that will set or get from the scene
            description="Set the min value. The min value ever is 0.",
            maxlen= 3,
            default= "0")#this set the initial text
        
        #    iStartFrame=0#
        context.scene.StringProperty(name="",
            attr="frames_initial",# this a variable that will set or get from the scene
            description="Where to start to put computed values.",
            maxlen= 10,
            default= "0")#this set the initial text
        
        
        #########  ADICIONAIS ################
        
        #    iMinBaseX=0
        context.scene.StringProperty(name="",
            attr="action_base_location_x",# this a variable that will set or get from the scene
            description="Base value to add to location values",
            maxlen= 10,
            default= "0")#this set the initial text
        
        #    iMinBaseY=0
        context.scene.StringProperty(name="",
            attr="action_base_location_y",# this a variable that will set or get from the scene
            description="Base value to add to location values",
            maxlen= 10,
            default= "0")#this set the initial text
        
        #    iMinBaseZ=0
        context.scene.StringProperty(name="",
            attr="action_base_location_z",# this a variable that will set or get from the scene
            description="Base value to add to location values",
            maxlen= 10,
            default= "0")#this set the initial text
            
        #    iMinScaleBaseX=0
        context.scene.StringProperty(name="",
            attr="action_base_scale_x",# this a variable that will set or get from the scene
            description="Base value to add to scale values",
            maxlen= 10,
            default= "0")#this set the initial text
        
        #    iMinScaleBaseY=0
        context.scene.StringProperty(name="",
            attr="action_base_scale_y",# this a variable that will set or get from the scene
            description="Base value to add to scale values",
            maxlen= 10,
            default= "0")#this set the initial text
        
        #    iMinScaleBaseZ=0   
        context.scene.StringProperty(name="",
            attr="action_base_scale_z",# this a variable that will set or get from the scene
            description="Base value to add to scale values",
            maxlen= 10,
            default= "0")#this set the initial text
        
        #    iRotationAxisBaseX=1
        context.scene.StringProperty(name="",
            attr="action_base_rotation_x",# this a variable that will set or get from the scene
            description="Base value to add to rotation values",
            maxlen= 10,
            default= "1")#this set the initial text
        
        #    iRotationAxisBaseY=1
        context.scene.StringProperty(name="",
            attr="action_base_rotation_y",# this a variable that will set or get from the scene
            description="Base value to add to rotation values",
            maxlen= 10,
            default= "1")#this set the initial text
        
        #    iRotationAxisBaseZ=1   
        context.scene.StringProperty(name="",
            attr="action_base_rotation_z",# this a variable that will set or get from the scene
            description="Base value to add to rotation values",
            maxlen= 10,
            default= "1")#this set the initial text
        
        
        
        ############## Propriedades boolean  ###################
        
        #
        #  Location
        #
        
        #  INVERTIDO!!!  bNaoValorIgual=True    # não deixa repetir valores     INVERTIDO!!!   
        context.scene.BoolProperty(name="Use Repeated Key Values (default on)",
            attr="action_valor_igual",
            description="Use to movements like a mouth. Maybe to a hand movement, you will not use this.",
            default=1)
        
        #   bEixoX=True
        context.scene.BoolProperty(name="L.X",
            attr="action_eixo_x",
            description="Import to X location",
            default=0)
            
        #    bEixoY=False
        context.scene.BoolProperty(name="L.Y",
            attr="action_eixo_y",
            description="Import to Y location",
            default=0)
        
        #    bEixoZ=False
        context.scene.BoolProperty(name="L.Z",
            attr="action_eixo_z",
            description="Import to Z location",
            default=0)
        
        #    iEixoXneg=-1
        context.scene.BoolProperty(name="-X",
            attr="action_eixo_NEG_x",
            description="Turn to NEGATIVE X location",
            default=0)
        
        #    iEixoYneg=1
        context.scene.BoolProperty(name="-Y",
            attr="action_eixo_NEG_y",
            description="Turn to NEGATIVE Y location",
            default=0)
        
        #    iEixoZneg=1
        context.scene.BoolProperty(name="-Z",
            attr="action_eixo_NEG_z",
            description="Turn to NEGATIVE Z location",
            default=0)
        
        
        #
        #  SCALE
        #
        
        
        #    bEscalaX=False
        context.scene.BoolProperty(name="S.X",
            attr="action_escala_x",
            description="Import to X scale",
            default=0)
        
        #    bEscalaY=False
        context.scene.BoolProperty(name="S.Y",
            attr="action_escala_y",
            description="Import to Y scale",
            default=0)
        
        #    bEscalaZ=False
        context.scene.BoolProperty(name="S.Z",
            attr="action_escala_z",
            description="Import to Z scale",
            default=0)
        
        #    iEscalaXneg=1
        context.scene.BoolProperty(name="-X",
            attr="action_escala_NEG_x",
            description="Turn to NEGATIVE X scale",
            default=0)
        
        #    iEscalaYneg=1
        context.scene.BoolProperty(name="-Y",
            attr="action_escala_NEG_y",
            description="Turn to NEGATIVE Y scale",
            default=0)
        
        #    iEscalaZneg=1
        context.scene.BoolProperty(name="-Z",
            attr="action_escala_NEG_z",
            description="Turn to NEGATIVE Z scale",
            default=0)
        
        
        
        #
        #  ROTATION
        #
        
        
        #    bRotationX=False
        context.scene.BoolProperty(name="R.X",
            attr="action_rotation_x",
            description="Import to X rotation",
            default=0)
        
        #    bRotationY=False
        context.scene.BoolProperty(name="R.Y",
            attr="action_rotation_y",
            description="Import to Y rotation",
            default=0)
        
        #    bRotationZ=False
        context.scene.BoolProperty(name="R.Z",
            attr="action_rotation_z",
            description="Import to Z rotation",
            default=1)
        
        #    iRotationNeg=1   # usado com BONES para angulo negativo!!!
        context.scene.BoolProperty(name="Rotation Negative to Bones",
            attr="action_rotation_signal_to_bones",
            description="Rotation Signal to Bones",
            default=0)
            
        #    iRotationXneg=1
        context.scene.BoolProperty(name="-X",
            attr="action_rotation_NEG_x",
            description="Turn to NEGATIVE X rotation",
            default=0)
        
        #    iRotationYneg=1
        context.scene.BoolProperty(name="-Y",
            attr="action_rotation_NEG_y",
            description="Turn to NEGATIVE Y rotation",
            default=0)
        
        #    iRotationZneg=1
        context.scene.BoolProperty(name="-Z",
            attr="action_rotation_NEG_z",
            description="Turn to NEGATIVE Z rotation",
            default=0)
    
    
    
    def draw(self, context):
        layout = self.layout

        row=layout.row()
        row.label(text="Select a Object, choose where to import,") 
        row=layout.row()
        row.label(text="click button \"Import Wav\",")
        row=layout.row()
        row.label(text="run the animation (alt A) and enjoy")        
        row=layout.row()
        row.label(text="Main Configuration:")        
        row=layout.row()

###################################################################                
        #colunas
        column= layout.column()
        split=column.split(percentage=0.3)
        col=split.column()
        row=col.row()

        row.label(text="Audio Sens:")
        row=col.row()        
        row.label(text="Frames/s:")
        col=split.column()
        row=col.row()        
        row.prop(context.scene,"audio_sense")
        row=col.row()
        row.prop(context.scene,"frames_per_second")

        col=split.column()
        row=col.row()

        row.label(text="Acts/s:")        
        row=col.row()
        row.label(text="Scale:")        
        col=split.column()
        row=col.row()        
        row.prop(context.scene,"action_per_second")
        row=col.row()
        row.prop(context.scene,"action_escale")

        row=layout.row()
        row.label(text="Where to apply:")       

###################################################################
        # 3 colunas
        column= layout.column()
        split=column.split(percentage=0.3)
        col=split.column()

        row=col.row()
        row.label(text='Location:')
        row=col.row()               
        row.prop(context.scene,"action_eixo_x")
        row.prop(context.scene,"action_eixo_NEG_x")
        row=col.row()
        row.prop(context.scene,"action_eixo_y")
        row.prop(context.scene,"action_eixo_NEG_y")
        row=col.row()
        row.prop(context.scene,"action_eixo_z")
        row.prop(context.scene,"action_eixo_NEG_z")

        col=split.column()

        row=col.row()
        row.label(text="Scale:")
        row=col.row()               
        row.prop(context.scene,"action_escala_x")
        row.prop(context.scene,"action_escala_NEG_x")
        row=col.row()
        row.prop(context.scene,"action_escala_y")
        row.prop(context.scene,"action_escala_NEG_y")
        row=col.row()
        row.prop(context.scene,"action_escala_z")
        row.prop(context.scene,"action_escala_NEG_z")

        col=split.column()

        row=col.row()
        row.label(text='Rotation:')        
        row=col.row()               
        row.prop(context.scene,"action_rotation_x")
        row.prop(context.scene,"action_rotation_NEG_x")
        row=col.row()
        row.prop(context.scene,"action_rotation_y")
        row.prop(context.scene,"action_rotation_NEG_y")
        row=col.row()
        row.prop(context.scene,"action_rotation_z")
        row.prop(context.scene,"action_rotation_NEG_z")
        row=col.row()
        row.prop(context.scene,"action_rotation_signal_to_bones")
        row=layout.row()
        row.label(text='More Options:')

        row=layout.row()
        row.label(text='Min. value:')        
        row.prop(context.scene,"action_min_value")
        row.label(text='Max. value:')        
        row.prop(context.scene,"action_max_value")
        row=layout.row()
        row=layout.row()
        row.label(text="Obj Name:")        
        row.prop(context.scene,"object_field")
        row.label(text="Start Frame")                
        row.prop(context.scene,"frames_initial")               
        row=layout.row()

        row.label(text='Base value to add to location values XYZ:')       
        row=layout.row()
        row.prop(context.scene,"action_base_location_x")
        row.prop(context.scene,"action_base_location_y")
        row.prop(context.scene,"action_base_location_z")
        row=layout.row()
        row.label(text='Base value to add to scale values XYZ:')       
        row=layout.row()
        row.prop(context.scene,"action_base_scale_x")
        row.prop(context.scene,"action_base_scale_y")
        row.prop(context.scene,"action_base_scale_z")
        row=layout.row()
        row.label(text='Value to add to rotation values XYZ:')       
        row=layout.row()
        row.prop(context.scene,"action_base_rotation_x")
        row.prop(context.scene,"action_base_rotation_y")
        row.prop(context.scene,"action_base_rotation_z")       
        row=layout.row()
        row.prop(context.scene,"action_valor_igual")        

        #operator button
        #OBJECT_OT_Botao_Go => Botao_GO
        layout.operator("Botao_GO")
        

from bpy.props import *

class OBJECT_OT_Botao_Go(bpy.types.Operator):
    '''Process a .wav file, take movement from the sound and import to the scene as Key'''
    bl_idname = "Botao_GO"
    bl_label = "Import Wav"

    path = StringProperty(name="File Path", description="Filepath used for importing the WAV file", maxlen= 1024, default= "")

    filename = StringProperty(name="File Name",
                              description="Name of the file")
                              
    directory = StringProperty(name="Directory",
                               description="Directory of the file")


    def execute(self, context):   
        # nao funciona self.properties.path
#        print("File Selected: ", self.properties.path)#display the file name and current path
#        print("Filename: ", self.properties.filename)#display the file name and current path
#        print("Directory Selected: ", self.properties.directory)#display the file name and current path       
        getInputFilename(self.properties.directory + self.properties.filename, context)        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        #need to set a path so so we can get the file name and path
        wm = context.manager
        wm.add_fileselect(self)
        return {'RUNNING_MODAL'}


        
def register():
    bpy.types.register(VIEW3D_PT_CustomMenuPanel)

def unregister():
    bpy.types.unregister(VIEW3D_PT_CustomMenuPanel)

if __name__ == "__main__":
    register()
    
    