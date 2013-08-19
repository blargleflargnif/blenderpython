bl_info = {
    "name": "Jamb Generator 2",
    "author": "SayPRODUCTIONS",
    "version": (2, 0),
    "blender": (2, 6, 8),
    "api": 33333,
    "location": "View3D > Add > Mesh",
    "description": "Jamb Generator 2",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Parametric Objects"}
import bpy
from bpy.props import *
import operator
from math import pi, sin, cos, sqrt, atan
def MAT(AD,R,G,B):
    if AD not in bpy.data.materials:
        mtl=bpy.data.materials.new(AD)
        mtl.diffuse_color     = ([R,G,B])
        mtl.diffuse_shader    = 'LAMBERT'
        mtl.diffuse_intensity = 1.0
    else:
        mtl=bpy.data.materials[AD]
    return mtl
def update_mesh(self, context):
    fc=[];vr=[]
    SM=[];ON=[];FLR=[];GAP=[];MER=[]
    mx =self.gen/200;my =self.yuk/100;k1=self.knr/100;fd=self.fd/100;fh=self.fh/100
    alt=self.alt/100;ust=my-self.ust/100;drn=-self.sdr/100;pdr=self.pdr/100
    vr.extend([[-mx-k1,  0,  0],[ mx+k1,  0,  0],[ mx+k1,  0,my],[-mx-k1,  0,my],
               [-mx,   pdr,alt],[ mx,   pdr,alt],[ mx,   pdr,my],[-mx,   pdr,my],
               [-mx-k1,drn,  0],[ mx+k1,drn,  0],[ mx+k1,drn,my],[-mx-k1,drn,my],
               [-mx,   drn,alt],[ mx,   drn,alt],[ mx,   drn,my],[-mx,   drn,my]])
    if  self.fg==0:
        fc.extend([[0,8,11,3],[8,12,15,11],[12,4,7,15],[5,13,14,6],[13,9,10,14],[9,1,2,10]])
    else:
        fc.extend([[11,3,16,17],[15,11,17,18],[7,15,18,24],[25,19,14,6],[19,20,10,14],[20,21,2,10]])
        ou=self.fg*12
        fc.extend([[4,7,12+ou,24+ou],[6,5,25+ou,13+ou]])
    h = self.fg;e = int(h//2);z = my
    for i in range(h):
        if   i==0:z-=self.f0/100
        elif i==1:z-=self.f1/100
        elif i==2:z-=self.f2/100
        elif i==3:z-=self.f3/100
        elif i==4:z-=self.f4/100
        elif i==5:z-=self.f5/100
        elif i==6:z-=self.f6/100
        elif i==7:z-=self.f7/100
        elif i==8:z-=self.f8/100
        elif i==9:z-=self.f9/100
        vr.extend([[   -mx-k1,     0,z],[   -mx-k1,   drn,z],[     -mx,   drn,z]])
        vr.extend([[       mx,   drn,z],[    mx+k1,   drn,z],[   mx+k1,     0,z]])
        vr.extend([[-mx-k1+fd,     0,z],[-mx-k1+fd,drn+fd,z],[     -mx,drn+fd,z]])
        vr.extend([[       mx,drn+fd,z],[ mx+k1-fd,drn+fd,z],[mx+k1-fd,     0,z]])
        z-=fh
        vr.extend([[   -mx-k1,     0,z],[   -mx-k1,   drn,z],[     -mx,   drn,z]])
        vr.extend([[       mx,   drn,z],[    mx+k1,   drn,z],[   mx+k1,     0,z]])
        vr.extend([[-mx-k1+fd,     0,z],[-mx-k1+fd,drn+fd,z],[     -mx,drn+fd,z]])
        vr.extend([[       mx,drn+fd,z],[ mx+k1-fd,drn+fd,z],[mx+k1-fd,     0,z]])
        n=len(vr)
        fc.extend([[n- 1,n- 2,n- 8,n- 7],[n- 3,n- 9,n- 8,n- 2],[n- 2,n- 1,n-13,n-14]])
        fc.extend([[n- 3,n- 2,n-14,n-15],[n-15,n-14,n-20,n-21],[n-14,n-13,n-19,n-20]])
        fc.extend([[n- 4,n- 5,n-11,n-10],[n- 5,n- 6,n-12,n-11],[n- 5,n- 4,n-16,n-17]])
        fc.extend([[n- 6,n- 5,n-17,n-18],[n-24,n-18,n-17,n-23],[n-23,n-17,n-16,n-22]])
        GAP.extend([len(fc)-4,len(fc)-3, len(fc)-10,len(fc)-9 ])

        if  h>1:
            if  h%2==0:
                if i < e          :fc.extend([[7,n-16,n-4],[6,n-3,n-15]])
                if i+1<e          :fc.extend([[7,n- 4,n+8],[6,n+9,n- 3]])
                if i+1>e          :fc.extend([[4,n-16,n-4],[5,n-3,n-15]])
                if i+1>e and i+1<h:fc.extend([[4,n- 4,n+8],[5,n+9,n -3]])
            else:
                if i < e          :fc.extend([[7,n-16,n-4],[6,n-3,n-15],[7,n-4,n+8],[6,n+9,n-3]])
                if i > e          :fc.extend([[4,n-16,n-4],[5,n-3,n-15]])
                if i+1>e and i+1<h:fc.extend([[4,n- 4,n+8],[5,n+9,n -3]])
        if i <h-1 and h>1:fc.extend([[n-7,n-8,n +4,n +5],[n-8,n-9,n+3,n+4],[n-9,n-3,n+9,n+3],[n-10,n-11,n+1,n+2],[n-11,n-12,n,n+1],[n-4,n-10,n+2,n+8]])
        if i==h-1        :fc.extend([[  0,  8,n-11,n-12],[ 8,12,n-10,n-11],[ 12, 4,n-4,n-10],[   5,  13,n-9,n-3],[  13, 9,n-8,n-9],[  9,   1,n-7,n-8]])
    if  self.DT0=='1':#---ACIK-------------------------------------------
        if self.DT1!='3':
            if  my==ust:
                if  pdr==0:
                    if self.DT1=='2':fc.extend([[6,14,10,2],[3,11,15,7]])
                elif   self.DT1=='2':
                    vr.extend([[mx+k1,pdr,my],[-mx-k1,pdr,my]]);n=len(vr)-1
                    fc.extend([[6,14,10,2,n-1],[3,11,15,7,n]])
            else:
                vr[2][2]=ust;vr[3][2]=ust
                vr[6][2]=ust;vr[7][2]=ust
                vr.extend([[mx+k1,pdr,my],[-mx-k1,pdr,my],[mx,pdr,my],[-mx,pdr,my]]);n=len(vr)-1
                if  self.DT1=='2':fc.extend([[n-1,14,10,n-3],[11,15,n,n-2]])#ust
                fc.extend([[n-1,6,14],[n,15,7]])#ic
                if  pdr==0:
                    fc.extend([[6,n-1,n-3,2],[7,3,n-2,n]])#arka
                    fc.extend([[n-2, 3, 11 ],[n-3,10, 2]])
                else:
                    vr.extend([[mx+k1,pdr,ust],[-mx-k1,pdr,ust]])
                    fc.extend([[ 6 ,n-1,n-3,n+1],[ 7 ,n+2,n-2, n ]])#arka
                    fc.extend([[n-2,n+2, 3 , 11],[n-3, 10, 2 ,n+1]])
            if  self.DT1=='1':
                e=self.mrx/100;h=self.mry/100
                vr.extend([[ mx-e,drn-e,my  ],[ mx+k1+e,drn-e,my  ],
                           [ mx-e,pdr+e,my  ],[ mx+k1+e,pdr+e,my  ],
                           [ mx-e,drn-e,my+h],[ mx+k1+e,drn-e,my+h],
                           [ mx-e,pdr+e,my+h],[ mx+k1+e,pdr+e,my+h]])
                n=len(vr)-1;fc.extend([[n,n-1,n-3,n-2],[n-5,n-4,n-6,n-7],[n-1,n,n-4,n-5],[n-2,n-3,n-7,n-6],[n,n-2,n-6,n-4],[n-3,n-1,n-5,n-7]])
                vr.extend([[-mx+e,drn-e,my  ],[-mx-k1-e,drn-e,my  ],
                           [-mx+e,pdr+e,my  ],[-mx-k1-e,pdr+e,my  ],
                           [-mx+e,drn-e,my+h],[-mx-k1-e,drn-e,my+h],
                           [-mx+e,pdr+e,my+h],[-mx-k1-e,pdr+e,my+h]])
                n=len(vr)-1;fc.extend([[n-1,n,n-2,n-3],[n-4,n-5,n-7,n-6],[n,n-1,n-5,n-4],[n-3,n-2,n-6,n-7],[n-2,n,n-4,n-6],[n-1,n-3,n-7,n-5]])
                n=len(fc);MER.extend([n-1,n-2,n-3,n-4,n-5,n-6,n-7,n-8,n-9,n-10,n-11,n-12])
    else:#---KAPALI------------------------------------------------------
        if  self.DT1=='1':
            e=self.mrx/100;h=self.mry/100
            vr.extend([[-mx-k1-e,drn-e,my  ],[ mx+k1+e,drn-e,my  ],
                       [-mx-k1-e,    e,my  ],[ mx+k1+e,    e,my  ],
                       [-mx-k1-e,drn-e,my+h],[ mx+k1+e,drn-e,my+h],
                       [-mx-k1-e,    e,my+h],[ mx+k1+e,    e,my+h]])
            n=len(vr)-1;fc.extend([[n,n-1,n-3,n-2],[n-5,n-4,n-6,n-7],[n-1,n,n-4,n-5],[n-2,n-3,n-7,n-6],[n,n-2,n-6,n-4],[n-3,n-1,n-5,n-7]])
            n=len(fc);MER.extend([n-1,n-2,n-3,n-4,n-5,n-6])
        elif self.DT1=='2':fc.append([11,10,2,3])
        if  self.UST=='1' or self.VL1==0:#Duz----------------------------
            T1=ust;T2=ust
        elif self.UST=='2':#Yuvarlak-----------
            if  self.DT2=='1':
                if  self.VL1<1:
                    H=0.01
                    h=sqrt(mx**2+H**2)/2
                    e=h*(mx/H)
                    R=sqrt(h**2+e**2)
                elif self.VL1/100>=mx:
                    H=mx;R=mx
                else:
                    H=self.VL1/100
                    h=sqrt(mx**2+H**2)/2
                    e=h*(mx/H)
                    R=sqrt(h**2+e**2)
                T1=ust-H;T2=T1
            elif self.DT2=='2':
                R =self.VL2/100
                if R<mx:R=mx
                T1=sqrt(R**2-mx**2)+ust-R;T2=T1
            M=ust-R
            r=self.RES
            for a in range(0,r):
                C =-cos(a*pi/r)*R;S =-sin(a*pi/r)*R
                if -mx<C and C<mx:
                    vr.extend([[C,pdr,M-S],[C,drn,M-S]])
                    ON.append(len(vr))
        elif self.UST=='3':#Egri---------------
            if   self.DT3=='1':H= self.VL1/200
            elif self.DT3=='2':H=(self.VL3/400)/mx
            elif self.DT3=='3':H=(sin(self.VL4*pi/180)/cos(self.VL4*pi/180))/2
            T1=ust-H;T2=ust+H
        elif self.UST=='4':#Ucgen--------------
            if   self.DT3=='1':H= self.VL1/100
            elif self.DT3=='2':H=(self.VL3/400)/mx
            elif self.DT3=='3':H=(sin(self.VL4*pi/180)/cos(self.VL4*pi/180))/2
            vr.extend([[0,pdr,ust],[0,drn,ust]])
            ON=[len(vr)]
            T1=ust-H;T2=T1
    
        vr[ 6][2]=T1;vr[ 7][2]=T2
        vr[14][2]=T1;vr[15][2]=T2
    
        if   ON    ==[]:fc.append([7,6,14,15])
        elif len(ON)==1:fc.extend([[15,7,ON[0]-2,ON[0]-1],[6,14,ON[0]-1,ON[0]-2]])
        else:
            fc.append([15,7,ON[ 0]-2,ON[ 0]-1]);SM.append(len(fc))
            for i in range(0,len(ON)-1):fc.append([ON[i]-1,ON[i]-2,ON[i+1]-2,ON[i+1]-1]);SM.append(len(fc))
            fc.append([6,14,ON[-1]-1,ON[-1]-2]);SM.append(len(fc))
        M=[10,11,15]
        if  ON!=[]:
            for i in ON:M.append(i-1)
        M.append(14)
        fc.append(M)
    #ALT-----------------------------------------------------------------
    if  self.DB0=='1':#---ACIK-------------------------------------------
        vr[4][2]=0;vr[5][2]=0;vr[12][2]=0;vr[13][2]=0
        if  self.DB1=='1':
            e=self.mbx/100;h=self.mby/100
            vr.extend([[-mx-k1-e,drn-e,-h],[-mx+e,drn-e,-h],
                       [-mx-k1-e,    0,-h],[-mx+e,    0,-h],
                       [-mx-k1-e,drn-e, 0],[-mx+e,drn-e, 0],
                       [-mx-k1-e,    0, 0],[-mx+e,    0, 0]])
            n=len(vr)-1;fc.extend([[n,n-1,n-3,n-2],[n-5,n-4,n-6,n-7],[n-2,n-3,n-7,n-6],[n,n-2,n-6,n-4],[n-3,n-1,n-5,n-7]])
            vr.extend([[mx-e,drn-e,-h],[mx+k1+e,drn-e,-h],
                       [mx-e,    0,-h],[mx+k1+e,    0,-h],
                       [mx-e,drn-e, 0],[mx+k1+e,drn-e, 0],
                       [mx-e,    0, 0],[mx+k1+e,    0, 0]])
            n=len(vr)-1;fc.extend([[n,n-1,n-3,n-2],[n-5,n-4,n-6,n-7],[n-2,n-3,n-7,n-6],[n,n-2,n-6,n-4],[n-3,n-1,n-5,n-7]])
            n=len(fc);MER.extend([n-1,n-2,n-3,n-4,n-5,n-6,n-7,n-8,n-9,n-10])
        elif self.DB1=='2':fc.extend([[8,0,4,12],[1,9,13,5]])
    else:
        fc.extend([[8,9,13,12],[12,13,5,4]])
        if  self.DB1=='1':
            e=self.mbx/100;h=self.mby/100
            vr.extend([[-mx-k1-e,drn-e,-h],[ mx+k1+e,drn-e,-h],
                       [-mx-k1-e,    0,-h],[ mx+k1+e,    0,-h],
                       [-mx-k1-e,drn-e, 0],[ mx+k1+e,drn-e, 0],
                       [-mx-k1-e,    0, 0],[ mx+k1+e,    0, 0]])
            n=len(vr)-1;fc.extend([[n,n-1,n-3,n-2],[n-5,n-4,n-6,n-7],[n-2,n-3,n-7,n-6],[n,n-2,n-6,n-4],[n-3,n-1,n-5,n-7]])
            n=len(fc);MER.extend([n-1,n-2,n-3,n-4,n-5])
        elif self.DB1=='2':fc.append([8,0,1,9])
        elif self.DB1=='3':
            e= self.mdx/100
            h=-self.mdy/100
            vr.extend([[-mx-k1+e,drn+e,0],[ mx+k1-e,drn+e,0],[-mx-k1+e,0,0],[ mx+k1-e,0,0]])
            n=len(vr)-1;fc.extend([[8,0,n-1,n-3],[9,8,n-3,n-2],[1,9,n-2,n]])
            if  h==0:fc.append([n-1,n,n-2,n-3])
            else:
                vr.extend([[-mx-k1+e,drn+e,h],[ mx+k1-e,drn+e,h],[-mx-k1+e,0,h],[ mx+k1-e,0,h]])
                n=len(vr)-1;fc.append([n-1,n,n-2,n-3])
                fc.extend([[n-7,n-5,n-1,n-3],[n-6,n-7,n-3,n-2],[n-4,n-6,n-2,n]])
            n = len(fc)-1
            if   h< 0:FLR.extend([n,n-1,n-2,n-3])
            elif h==0:FLR.append( n )
            else     :FLR.append(n-3)
    e = self.sd/100;h = self.sh/100;z = my
    for i in range(0,self.sg):
        if   i==0:z-=self.s0/100
        elif i==1:z-=self.s1/100
        elif i==2:z-=self.s2/100
        elif i==3:z-=self.s3/100
        elif i==4:z-=self.s4/100
        elif i==5:z-=self.s5/100
        elif i==6:z-=self.s6/100
        elif i==7:z-=self.s7/100
        elif i==8:z-=self.s8/100
        elif i==9:z-=self.s9/100
        vr.extend([[-mx-k1  ,0,z],[-mx-k1  ,drn  ,z],[-mx,drn  ,z]])
        vr.extend([[-mx-k1-e,0,z],[-mx-k1-e,drn-e,z],[-mx,drn-e,z]])
        n=len(vr)-1
        fc.extend([[n-1,n,n-3,n-4],[n-5,n-2,n-1,n-4]])
        z-=h
        vr.extend([[-mx-k1  ,0,z],[-mx-k1  ,drn  ,z],[-mx,drn  ,z]])
        vr.extend([[-mx-k1-e,0,z],[-mx-k1-e,drn-e,z],[-mx,drn-e,z]])
        fc.extend([[n+6,n+5,n+2,n+3],[n+4,n+1,n+2,n+5]])
        fc.extend([[n-3,n,n+6,n+3],[n,n-1,n+5,n+6],[n+5,n-1,n-2,n+4]])
        z+=h
        vr.extend([[mx+k1  ,0,z],[mx+k1  ,drn  ,z],[mx,drn  ,z]])
        vr.extend([[mx+k1+e,0,z],[mx+k1+e,drn-e,z],[mx,drn-e,z]])
        n=len(vr)-1
        fc.extend([[n,n-1,n-4,n-3],[n-2,n-5,n-4,n-1]])
        z-=h
        vr.extend([[mx+k1  ,0,z],[mx+k1  ,drn  ,z],[mx,drn  ,z]])
        vr.extend([[mx+k1+e,0,z],[mx+k1+e,drn-e,z],[mx,drn-e,z]])
        fc.extend([[n+5,n+6,n+3,n+2],[n+1,n+4,n+5,n+2]])
        fc.extend([[n,n-3,n+3,n+6],[n-1,n,n+6,n+5],[n-1,n+5,n+4,n-2]])
        n=len(fc);MER.extend([n-1,n-2,n-3,n-4,n-5,n-6,n-7,n-8,n-9,n-10,n-11,n-12,n-13,n-14])
#OBJE -----------------------------------------------------------
    o=bpy.context.active_object
    emesh=o.data
    mesh =bpy.data.meshes.new(name='Jamb')
    mesh.from_pydata(vr,[],fc)

    mesh.materials.append(    MAT('Jamb',  0.40,0.08,0.04))
    if  self.DT1=='1' or self.DB1=='1' or self.sg>0:
        mesh.materials.append(MAT('Marble',1.00,0.90,0.80))
    if  self.DB1=='3':
        mesh.materials.append(MAT('Floor', 1.00,1.00,1.00))
    if  self.fg>0 and self.fm==True:
        mesh.materials.append(MAT('Gap',   1.00,0.80,0.50))

    e=1
    for i in MER:mesh.polygons[i].material_index=e
    if  MER!=[]:e+=1
    for i in FLR:mesh.polygons[i].material_index=e
    if  FLR!=[]:e+=1
    if  self.fm==True:
        for i in GAP:mesh.polygons[i].material_index=e
    for i in SM:mesh.polygons[i-1].use_smooth=1

    mesh.update(calc_edges=True)

    for i in bpy.data.objects:
        if  i.data==emesh:i.data=mesh

    name=emesh.name
    emesh.user_clear()
    bpy.data.meshes.remove(emesh)
    mesh.name=name
    if  bpy.context.mode!='EDIT_MESH':
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.editmode_toggle()
#----------------------------------------------------------------
bpy.types.Object.reg = StringProperty(default='SayPRODUCTIONS - Jamb Generator 2')
bpy.types.Object.gen=IntProperty(name='Width',     min=1,max= 400,default=180,update=update_mesh)
bpy.types.Object.knr=IntProperty(name='Thick',     min=1,max= 100,default= 15,update=update_mesh)
bpy.types.Object.yuk=IntProperty(name='Height',    min=1,max=3000,default=590,update=update_mesh)
bpy.types.Object.alt=IntProperty(name='Bottom',    min=1,max= 300,default= 44,update=update_mesh)
bpy.types.Object.ust=IntProperty(name='Top',       min=1,max= 300,default= 33,update=update_mesh)
bpy.types.Object.sdr=IntProperty(name='Depth',     min=1,max= 100,default= 15,update=update_mesh)
bpy.types.Object.pdr=IntProperty(name='Wall Depth',min=0,max= 100,default= 20,update=update_mesh)

bpy.types.Object.DT0=EnumProperty(items =(('1','Open',''),('2','Closed' ,'')                ),name='',default='2',update=update_mesh)
bpy.types.Object.DT1=EnumProperty(items =(('1','Sill',''),('2','Polygon',''),('3','None','')),name='',default='2',update=update_mesh)
bpy.types.Object.mrx=IntProperty( name='',min=0,max=20,default=4,update=update_mesh)#Kenar
bpy.types.Object.mry=IntProperty( name='',min=1,max=20,default=4,update=update_mesh)#Yukseklik

bpy.types.Object.DB0=EnumProperty(items =(('1','Open',''),('2','Closed' ,'')                                 ),name='',default='2',update=update_mesh)
bpy.types.Object.DB1=EnumProperty(items =(('1','Sill',''),('2','Polygon',''),('3','Floor',''),('4','None','')),name='',default='2',update=update_mesh)
bpy.types.Object.mbx=IntProperty( name='',min=  0,max=20,default= 4,update=update_mesh)#Kenar
bpy.types.Object.mby=IntProperty( name='',min=  1,max=20,default= 4,update=update_mesh)#Yukseklik
bpy.types.Object.mdx=IntProperty( name='',min=  1,max=50,default=10,update=update_mesh)#Kenar
bpy.types.Object.mdy=IntProperty( name='',min=-50,max=50,default=10,update=update_mesh)#Yukseklik

bpy.types.Object.UST=EnumProperty(items =(('1','Flat',''),('2','Arch',''),('3','Inclined',''),('4','Triangle','')),name='Window Top',default='2',update=update_mesh)
bpy.types.Object.DT2=EnumProperty(items =(('1','Difference',''),('2','Radius',   '')),                             name='',          default='1',update=update_mesh)
bpy.types.Object.DT3=EnumProperty(items =(('1','Difference',''),('2','Incline %',''),('3','Incline Angle','')),    name='',          default='1',update=update_mesh)

bpy.types.Object.VL1=IntProperty( name='',min=-10000,max=10000,default=30,update=update_mesh)#Fark
bpy.types.Object.VL2=IntProperty( name='',min=     1,max=10000,default=30,update=update_mesh)#Cap
bpy.types.Object.VL3=IntProperty( name='',min=  -100,max=  100,default=30,update=update_mesh)#Egim %
bpy.types.Object.VL4=IntProperty( name='',min=   -45,max=   45,default=30,update=update_mesh)#Egim Aci

bpy.types.Object.RES=IntProperty(name='Resolution pi/',min=2,max=360,default=36,update=update_mesh)#Res

bpy.types.Object.fm =BoolProperty(name='',default=True,update=update_mesh)
bpy.types.Object.fg =IntProperty(name='Gap Count',min=0,max=10,default=2,update=update_mesh)
bpy.types.Object.fh =IntProperty(name='',         min=1,max=10,default=3,update=update_mesh)
bpy.types.Object.fd =IntProperty(name='',         min=1,max=10,default=2,update=update_mesh)

bpy.types.Object.f0 =IntProperty(name='Above Distance',min=1,max=3000,default=120,update=update_mesh)
bpy.types.Object.f1 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f2 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f3 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f4 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f5 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f6 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f7 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f8 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)
bpy.types.Object.f9 =IntProperty(name='Distance'      ,min=1,max=3000,default= 30,update=update_mesh)

bpy.types.Object.sg =IntProperty(name='Sill Count',min=0,max=10,default=0,update=update_mesh)
bpy.types.Object.sh =IntProperty(name='',          min=1,max=10,default=4,update=update_mesh)
bpy.types.Object.sd =IntProperty(name='',          min=1,max=10,default=4,update=update_mesh)

bpy.types.Object.s0 =IntProperty(name='Above Distance',min=1,max=3000,default=90,update=update_mesh)
bpy.types.Object.s1 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s2 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s3 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s4 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s5 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s6 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s7 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s8 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
bpy.types.Object.s9 =IntProperty(name='Distance'      ,min=1,max=3000,default=30,update=update_mesh)
#----------------------------------------------------------------
class JambGenerator2Panel(bpy.types.Panel):
    bl_idname      ="JambGenerator2Panel"
    bl_label       ="Jamb Generator"
    bl_space_type  ='PROPERTIES'
    bl_region_type ='WINDOW'
    bl_context     ="modifier"
    bl_options     ={'DEFAULT_CLOSED'}
    def draw(self, context):
        layout=self.layout
        if  bpy.context.mode=='EDIT_MESH':
            layout.label('does not work in edit mode.')
        else:
            o = context.object
            if 'reg' in o:
                if  o['reg']=='SayPRODUCTIONS - Jamb Generator 2':
                    box=layout.box()
                    box.label('Body Settings')
                    box.prop(o,'gen')
                    box.prop(o,'yuk')
                    box.prop(o,'knr')
                    row=box.row();row.prop(o,'sdr');row.prop(o,'pdr')
                    #-----------------------------------------
                    box=layout.box();box.label('Top Settings')
                    row=box.row();row.prop(o,'DT0');row.prop(o,'ust')
                    if o.DT1=='1':row=box.row();row.prop(o,'DT1');row.prop(o,'mrx');row.prop(o,'mry')
                    else         :row=box.row();row.prop(o,'DT1');row.label('');row.label('')
                    if  o.DT0=='2':
                        box.prop(o,'UST')
                        if  o.UST=='2':
                            row= box.row(); row.prop(o,'DT2')
                            if   o.DT2=='1':row.prop(o,'VL1')
                            elif o.DT2=='2':row.prop(o,'VL2')
                            box.prop(o,'RES')
                        elif o.UST=='3':
                            row= box.row(); row.prop(o,'DT3')
                            if   o.DT3=='1':row.prop(o,'VL1')
                            elif o.DT3=='2':row.prop(o,'VL3')
                            elif o.DT3=='3':row.prop(o,'VL4')
                        elif o.UST=='4':
                            row= box.row(); row.prop(o,'DT3')
                            if   o.DT3=='1':row.prop(o,'VL1')
                            elif o.DT3=='2':row.prop(o,'VL3')
                            elif o.DT3=='3':row.prop(o,'VL4')
                    #-----------------------------------------
                    box=layout.box();box.label('Bottom Settings')
                    row=box.row();row.prop(o,'DB0');row.prop(o,'alt')

                    if   o.DB1=='1':row=box.row();row.prop(o,'DB1');row.prop(o,'mbx');row.prop(o,'mby')
                    elif o.DB1=='3':row=box.row();row.prop(o,'DB1');row.prop(o,'mdx');row.prop(o,'mdy')
                    else           :row=box.row();row.prop(o,'DB1');row.label(''    );row.label(''    )

                    box=layout.box()
                    row=box.row();row.prop(o, 'fg');row.prop(o, 'fm')
                    row=box.row();row.prop(o, 'fh');row.prop(o, 'fd')
                    for i in range(o.fg):box.prop(o,'f'+str(i))

                    box=layout.box();box.prop(o,'sg')
                    row=box.row();row.prop(o, 'sh');row.prop(o, 'sd')
                    for i in range(o.sg):box.prop(o,'s'+str(i))
                    #-----------------------------------------
                else:layout.operator('jamb.generator_convert')
            else:layout.operator('jamb.generator_convert')
class JambConvert(bpy.types.Operator) :
    bl_idname ='jamb.generator_convert'
    bl_label  ='Convert to Parametric'
    bl_options={"UNDO"}
    def invoke(self,context,event):
        o=context.object
        o.reg='SayPRODUCTIONS - Jamb Generator 2'
        o.gen=180
        return {"FINISHED"}
def register()  :bpy.utils.register_class(  JambGenerator2Panel);bpy.utils.register_class(JambConvert)
def unregister():bpy.utils.unregister_class(JambGenerator2Panel)
if __name__ == '__main__':register()