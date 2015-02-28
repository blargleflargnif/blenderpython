# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Mushroomer Tube Trunk - Public Release 4
# Confirmed working with r31856
# Josh Wedlake, Tube Project
# More scripts:     http://tube.freefac.org
# Documentation:    http://wiki.tube.freefac.org/wiki/Mushroomer

import random
import bpy
import math
import mathutils


def auto_detect_prefixes(mushroom_object):
    keys_list=list(mushroom_object.data.shape_keys.keys)
    dict_prefixes=dict()
    for index,each_key in enumerate(keys_list):
        name=each_key.name
        prefix=''
        for b in [[name[(len(name)-(a+1)):],name[:(len(name)-(a+1))]] for a in range(0,len(name))]:
            if b[0].isdigit():
                prefix=b[1]
                available_value=int(b[0])
            else:
                break
        if prefix !='':
            if prefix not in dict_prefixes:
                dict_prefixes[prefix]=[[available_value,index]]
            else:
                dict_prefixes[prefix].append([available_value,index])
    list_dict_keys=list(dict_prefixes.keys())
    for d_key in list_dict_keys:
        dict_prefixes[d_key]=sorted(dict_prefixes[d_key],key=lambda list_item: list_item[0])
    #returns dict[prefix, eg "s"]=sorted list of [(available value eg 1 for s1, shape key index),...]
    return dict_prefixes

def build_face_limit_enum(target_object):
    vertex_group_list=[]
    vertex_group_list.append(('TOVGM','Target Object Vertex Group Mask','Target Object Vertex Group Mask'))
    for vertex_group in target_object.vertex_groups:
        vertex_group_list.append((vertex_group.name, vertex_group.name, vertex_group.name))
    vertex_group_list.append(('-1','(Do not use: Mushrooms everywhere!)','no limits'))
    #rna fix
    #target_object.EnumProperty(attr="mushroomer_limit_group",items=vertex_group_list,default='-1')
    bpy.types.Object.mushroomer_limit_group=bpy.props.EnumProperty(items=vertex_group_list,default='-1')
    target_object.mushroomer_limit_group='-1'

def build_vertex_group_enum(mushroom_list,target_object):
    set_valid_groups=set()
    for mushroom_object in mushroom_list:
        for vertex_group in mushroom_object.vertex_groups:
            set_valid_groups.add(vertex_group.name)
    vertex_group_list=[]
    vertex_group_list.append(('VGID','Mushroom Vertex Group for Shrinkwrap','Mushroom Vertex Group for Shrinkwrap'))
    vertex_group_list.append(('-1','(Do not use shrinkwrapping)','no shrinkwrapping'))
    for vertex_group_name in list(set_valid_groups):
        vertex_group_list.append((vertex_group_name, vertex_group_name, vertex_group_name))
    #rna fix
    #target_object.EnumProperty(attr="mushroomer_shrinkwrap_vg",items=vertex_group_list,default='-1')
    bpy.types.Object.mushroomer_shrinkwrap_vg=bpy.props.EnumProperty(items=vertex_group_list,default='-1')

def build_timing_group_enum(target_object):
    vertex_group_list=[]
    vertex_group_list.append(('TVG','Vertex Group for Retiming','Vertex Group for Retiming'))
    for vertex_group in target_object.vertex_groups:
        if vertex_group.name.startswith('MT'):
            if vertex_group.name[2:] in bpy.data.groups:
                vertex_group_list.append((vertex_group.name, vertex_group.name, vertex_group.name))
    vertex_group_list.append(('-1','(Do not use: Mushrooms everywhere!)','no limits'))
    #rna fix
    #target_object.EnumProperty(attr="mushroomer_timing_vg",items=vertex_group_list,default='-1')
    bpy.types.Object.mushroomer_timing_vg=bpy.props.EnumProperty(items=vertex_group_list,default='-1')
    
def build_group_name_text(target_object):
    #find out if there are any groups named mushroomer_group_x, where x is an int.  Find the lowest free int
    lowest_free_id=-1
    for group in bpy.data.groups:
        if group.name.startswith('mushroomer_group_'):
            this_id=group.name.lstrip('mushroomer_group_')
            if this_id.isdigit():
                this_id_int=int(this_id)
                if this_id_int>lowest_free_id:
                    lowest_free_id=this_id_int
    group_name='mushroomer_group_'+str(lowest_free_id+1)
    #rna fix
    #target_object.StringProperty(attr="mushroomer_grouping", description="Group To Add Mushrooms To",default=group_name)
    bpy.types.Object.mushroomer_grouping=bpy.props.StringProperty(description="Group To Add Mushrooms To",default=group_name)

def build_prefixes_enum(mushroom_list,target_object):
    #builds a list of valid shape prefixes for the enum
    #builds a dictionary > mushroom name > prefixes > valid numerical values
    dict_all_prefixes=dict()
    #any - prefixes which are only available on some of the mushrooms
    #all - prefixes which are available on all of the mushrooms
    set_valid_prefixes_any=set()
    set_valid_prefixes_all=set()
    first_run=True
    for mushroom_object in mushroom_list:
        mushroom_dict=auto_detect_prefixes(mushroom_object)
        dict_all_prefixes[mushroom_object.name]=mushroom_dict
        set_valid_prefixes_any|=set(mushroom_dict.keys())
        if not first_run:
            set_valid_prefixes_all&=set(mushroom_dict.keys())
        else:
            set_valid_prefixes_all=set(mushroom_dict.keys())
            first_run=False
    set_valid_prefixes_any-=set_valid_prefixes_all
    prefixes_list=[]
    prefixes_list.append(('LSK','Life cycle shape key set','Life cycle shape key set'))
    prefixes_list.append(("IGNORE",'Don\'t Use','Don\'t Use'))
    for prefix in list(set_valid_prefixes_all):
        prefixes_list.append((prefix,prefix+'... [available on all mushrooms]',prefix))
    for prefix in list(set_valid_prefixes_any):
        prefixes_list.append((prefix,prefix+'... [NOT AVAILABLE ON ALL MUSHROOMS]',prefix))
    random_prefixes_list=prefixes_list[:]
    bend_prefixes_list=prefixes_list[:]
    random_prefixes_list[0]=('RSK','Random variation shape key set','Random variation shape key set')
    bend_prefixes_list[0]=('BSK','Bend variation shape key set','Random variation shape key set')
    prefixes_list.append(("USEEXIST",'Duplicate and retime pre-existing animations','Duplicate and retime pre-existing animations'))
    #rna fix
    #target_object.EnumProperty(attr="mushroomer_lifecycle_key_set",items=prefixes_list,default='USEEXIST')
    #target_object.EnumProperty(attr="mushroomer_random_key_set",items=random_prefixes_list,default='IGNORE')
    #target_object.EnumProperty(attr="mushroomer_bend_key_set",items=bend_prefixes_list,default='IGNORE')
    bpy.types.Object.mushroomer_lifecycle_key_set=bpy.props.EnumProperty(items=prefixes_list,default='USEEXIST')
    bpy.types.Object.mushroomer_random_key_set=bpy.props.EnumProperty(items=random_prefixes_list,default='IGNORE')
    bpy.types.Object.mushroomer_bend_key_set=bpy.props.EnumProperty(items=bend_prefixes_list,default='IGNORE')
    return dict_all_prefixes

def get_number_for_generation(generation,generations_max,mode,min,max,jitter):
    import random,math
    #gen is input
    #pass a minimum and a maximum number
    #jitter is % random error
    #modes 0-constant,1-linear,2-square,3-fibbonacci,4-root
    jitter_amount=(((random.random()*2)-1)*jitter)+1
    if mode==0:
        value=(jitter_amount*0.5*(max-min))+min
    elif mode==1:
        value=((generation/generations_max)*(max-min)*jitter_amount)+min
    elif mode==2:
        value=(((generation**2)/(generations_max**2))*(max-min)*jitter_amount)+min
    elif mode==3:
        root5 = math.sqrt(5)
        fib_c=(0.5 + root5/2)
        fib_g=fib_c**generation
        fib_c=int(0.5+fib_g/root5)
        fib_g=fib_c**generations_max
        fib_max=int(0.5+fib_g/root5)
        if fib_max==0:
            fib_max=1
        value=((fib_c/fib_max)*(max-min)*jitter_amount)+min
    elif mode==4:
        root_max=generations_max**0.5
        root_c=generation**0.5
        value=((root_c/root_max)*(max-min)*jitter_amount)+min
    return int(value)
        
def make_vertex_parent(target_object,ob_to_distribute,faceid):
    initialise_object_mode()
    #find the closest 3 verts
    face_verts=target_object.data.faces[faceid].vertices
    vert_list=[]
    for each_vert in face_verts:
        vert_list.append([(ob_to_distribute.location-(target_object.matrix_world*target_object.data.vertices[each_vert].co)).length,each_vert])
    sorted_verts=sorted(vert_list,key=lambda vertinfo: vertinfo[0])
    verts_to_parent=[sorted_verts[0][1],sorted_verts[1][1],sorted_verts[2][1]]
    #only select the target
    bpy.ops.object.select_all(action='DESELECT')
    target_object.select=True
    
    initialise_edit_mode()
    #in edit mode: deselect verts
    existing_sel_mode=bpy.context.tool_settings.mesh_select_mode
    bpy.context.tool_settings.mesh_select_mode=[True,False,False]
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()
    #not in edit mode:select verts
    for each_vert in verts_to_parent:
        target_object.data.vertices[each_vert].select=True
    #now select the mushroom aswell
    ob_to_distribute.select=True
    bpy.context.scene.objects.active=target_object
    #get into edit mode for the active object
    bpy.ops.object.editmode_toggle()
    #now in edit mode with mushroom selected and appropriate verts selected
    bpy.ops.object.vertex_parent_set()
    bpy.context.tool_settings.mesh_select_mode=existing_sel_mode
    
    #out of edit mode
    initialise_object_mode()
    bpy.ops.object.select_all(action='DESELECT')

def place_on_face(target_object, faceid, mushroom_object, pc, sc):
    if bpy.context.mode=='EDIT_MESH':
        bpy.ops.object.editmode_toggle()
    #where pc is center point
    if len(bpy.context.selected_objects)>0:
        bpy.ops.object.select_all()
    mushroom_object.select=True
    #change this line if keyframe path fails
    bpy.ops.object.duplicate(linked=False)
    ob_to_distribute_handle=bpy.context.selected_editable_objects[0]
    ob_to_distribute_handle.location=pc
    sc_x=sc.x*ob_to_distribute_handle.scale.x
    sc_y=sc.y*ob_to_distribute_handle.scale.y
    sc_z=sc.z*ob_to_distribute_handle.scale.z
    ob_to_distribute_handle.scale=mathutils.Vector((sc_x,sc_y,sc_z))
    d_start=target_object.matrix_world.copy().invert()*mathutils.Vector((0,0,0))
    d_end=target_object.matrix_world.copy().invert()*target_object.data.faces[faceid].normal.copy()
    d=d_end-d_start
    d=d.normalize()
    e = mathutils.Vector((0,0,1))
    f=e.copy().cross(d)
    f=f.normalize()
    e=d.copy().cross(f)
    e=e.normalize()
    mat = (mathutils.Matrix(f,e,d)).rotation_part().to_euler()
    ob_to_distribute_handle.rotation_euler=mat
    make_vertex_parent(target_object,ob_to_distribute_handle,faceid)
    return [ob_to_distribute_handle,mushroom_object.name]

def get_face_dimensions(target_object, faceid):
    v1=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[0]].co
    v2=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[1]].co
    v3=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[2]].co
    fx=v2-v1
    fy=v3-v2
    return [fx.length,fy.length]

def convert_dec_to_pt(target_object,faceid,dec):
    v1=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[0]].co
    v2=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[1]].co
    v3=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[2]].co
    if len(target_object.data.faces[faceid].vertices)>3:
        v4=target_object.matrix_world*target_object.data.vertices[target_object.data.faces[faceid].vertices[3]].co
    else:
        v4=v3
    va=((v2-v1)*dec[0])+v1
    vb=((v3-v4)*dec[0])+v4
    vp=((vb-va)*dec[1])+va
    return vp

def get_points_random(target_object,faceid,n):
    pl=[]
    pl_xyz=[]
    for tmp in range(0,n):
        pl.append([random.random(),random.random()])
    for index in range(0,len(pl)):
        pl_xyz.append(convert_dec_to_pt(target_object,faceid,pl[index]))
    return pl_xyz
    
def get_points_jittered(target_object,faceid,n,jitter):
    #jitter is a decimal 0 - 1
    #returns a list of XYZ vectors referring to points jitter distrib on face
    fdim=get_face_dimensions(target_object,faceid)
    ndim=propose_dimensions(fdim,n)
    pl=[]
    pl_xyz=[]
    for x in range(0,ndim[0]):
        for y in range(0,ndim[1]):
            rx=(jitter*random.random())-0.5
            ry=(jitter*random.random())-0.5
            pl.append([((x+0.5)/ndim[0]),((y+0.5)/ndim[1])])
    for index in range(0,len(pl)):
        pl_xyz.append(convert_dec_to_pt(target_object,faceid,pl[index]))
    return pl_xyz

def get_points_scales(target_object,faceid,pl_xyz):
    pl_xyz_s=[]
    pl_xyz_l=list(pl_xyz)
    if len(pl_xyz)>1:
        for pa in pl_xyz_l:
            closest_dist=-1
            for pb in pl_xyz_l:
                if pb!=pa:
                    dist_vec=pb-pa
                    dist=dist_vec.length
                    if closest_dist==-1:
                        closest_dist=dist
                    elif dist<closest_dist:
                        closest_dist=dist
            pl_xyz_s.append([pa,closest_dist/2])
    else:
        fdim=get_face_dimensions(target_object, faceid)
        if fdim[0]<fdim[1]:
            psc=fdim[0]/2
        else:
            psc=fdim[1]/2
        pl_xyz_s.append([pl_xyz[0],psc])
    return pl_xyz_s

def get_points_scales_tightpack(target_object,faceid,pl_xyz):
    pl_xyz_l=list(pl_xyz)
    #point data has a list of [pid,dist] sorted by dist
    point_data=[]
    if len(pl_xyz)>1:
        for index,pa in enumerate(pl_xyz_l):
            point_data.append([])
            for neighbour_index,pb in enumerate(pl_xyz_l):
                if pb!=pa:
                    dist_vec=pb-pa
                    dist=dist_vec.length
                    point_data[index].append((neighbour_index,dist))
            point_data[index]=sorted(point_data[index], key=lambda dp: dp[1])
        #data point is now sorted.
        #priority list is a list ordered by pids' closest neighbour dists
        priority_list=[]
        for index,point_data_item in enumerate(point_data):
            priority_list.append((index,point_data_item[0][1]))
        priority_list=sorted(priority_list,key=lambda dp: dp[1])
        #ringed points[dict]=ringsize
        ringed_points=dict()
        #starting with the first item in priority list
        for point_id in priority_list:
            #find the closest ring
            ring_size=-1
            for neighbour_point in point_data[point_id[0]]:
                if neighbour_point[0] in ringed_points.keys():
                    ring_size=neighbour_point[1]-ringed_points[neighbour_point[0]]
                    break
            for neighbour_point in point_data[point_id[0]]:
                if neighbour_point[0] not in ringed_points.keys():
                    if ring_size==-1:
                        ring_size=neighbour_point[1]/2
                    elif ring_size>(neighbour_point[1]/2):
                        ring_size=neighbour_point[1]/2
                    break
            ringed_points[point_id[0]]=ring_size
            pl_xyz_l[point_id[0]]=[pl_xyz[point_id[0]],ring_size]
        #pl_xyz is a list of [point, ringsize]
    else:
        #if there is only one point, use the face dimensions
        fdim=get_face_dimensions(target_object, faceid)
        if fdim[0]<fdim[1]:
            psc=fdim[0]/2
        else:
            psc=fdim[1]/2
        pl_xyz_l=[pl_xyz[0],psc]
    return pl_xyz_l

def propose_dimensions(f=[],n=1):
    #where fx,fy are face dimensions
    #n is the number needed
    #fx should be longer than fy
    fx=f[0]
    fy=f[1]
    if fx>fy:
        swap=0
    else:
        t=fy
        fy=fx
        fx=t
        swap=1
    nx=math.floor(fx*((n/(fx*fy))**0.5))
    ny=math.ceil(fy*((n/(fx*fy))**0.5))
    # so nx and ny are approximately the number in x and y directions
    closest_pair=[math.fabs((n**0.5)-(nx*ny)),[nx,ny]]
    count=0.5
    tnx=tny=0
    while (tnx*tny<n):
        tnx=round(nx+count)
        tny=round(ny+((ny/nx)*count))
        t_cp=math.fabs((n**0.5)-(tnx*tny))
        if t_cp<closest_pair[0]:
            closest_pair=[t_cp,[tnx,tny]]
        count+=0.5
    if swap==1:
        t=closest_pair[1][1]
        closest_pair[1][1]=closest_pair[1][0]
        closest_pair[1][0]=t
    return closest_pair[1]

def getneighbouringfaces(faces,faceid,vertshare,set_allowed_faces):
    #vertshare is the number of vertices which must be in common
    cset=set(faces[faceid].vertices)
    neighbourfaces=set()
    for count in range(0,len(faces)):
        vset=set(faces[count].vertices)
        if len(cset&vset)>(vertshare-1):
            neighbourfaces.add(count)
    neighbourfaces=neighbourfaces&set_allowed_faces
    return neighbourfaces

def build_neighbour_faces_dict(target_object,set_allowed_faces):
    print('building a neighbour face lookup...')
    neighbour_faces=dict()
    for index,each_face in enumerate(target_object.data.faces):
        neighbour_faces[index]=getneighbouringfaces(target_object.data.faces,index,1,set_allowed_faces)
    print('done.')
    return neighbour_faces

def dofacesneighbour(faces,faceset1,faceset2,set_allowed_faces):
    for iface in faceset2:
        neighbouringfaceset=getneighbouringfaces(faces,iface,1,set_allowed_faces)
        if len(neighbouringfaceset&faceset1)>0:
            return True
    return False

def doesfaceneighbour(faces,faceset1,sface,set_allowed_faces):
    neighbouringfaceset=getneighbouringfaces(faces,sface,1,set_allowed_faces)
    if len(neighbouringfaceset&faceset1)>0:
        return True
    return False

def sortfacelistbyz(faces,facelist):
    nfacelist=[]
    sfacelist=[]
    for ifaceref in facelist:
        nfacelist.append((ifaceref,faces[ifaceref].center.z))
    nfacelist=sorted(nfacelist, key=lambda nfaces: -nfaces[1])
    for nface in nfacelist:
        sfacelist.append(nface[0])
    return sfacelist

def sortfacelistbyrandom(faces,facelist):
    nfacelist=[]
    sfacelist=[]
    for ifaceref in facelist:
        nfacelist.append((ifaceref,random.random()))
    nfacelist=sorted(nfacelist, key=lambda nfaces: nfaces[1])
    for nface in nfacelist:
        sfacelist.append(nface[0])
    return sfacelist

def getallneighbours(livefaces,neighbour_face_dict,set_allowed_faces):
    neighbour_set=set()
    for each_face in livefaces:
        neighbour_set|=neighbour_face_dict[each_face]
    neighbour_set-=livefaces
    neighbour_set&=set_allowed_faces
    return neighbour_set

#-------------------choose next algorithms----------------

def choosenextfaces_simpleincrease(target_object,faces,livefaces,includedfaces,set_allowed_faces):
    
    initialise_object_mode()
    bpy.ops.object.select_all(action='DESELECT')
    target_object.select=True
    bpy.context.scene.objects.active=target_object
    
    #set the selection
    selectset(faces,set(livefaces.keys()))
    
    #increase the selection - in edit mode
    initialise_edit_mode()
    bpy.ops.mesh.select_more()
    initialise_object_mode()
    
    #get the selection
    selection_list=list((selectget(faces)&set_allowed_faces)-includedfaces)
    
    new_livefaces=dict()
    for selected_item in selection_list:
        new_livefaces[selected_item]=-1
    return new_livefaces

def choosenextfaces_conways(faces,livefaces,neighbour_face_dict,set_allowed_faces):
    new_live_faces=dict()
    for each_face in list(livefaces.keys()):
        n_neighbours=len(neighbour_face_dict[each_face]&set(livefaces.keys()))
        print(n_neighbours)
        if n_neighbours>1 and n_neighbours<4:
            new_live_faces[each_face]=-1
    list_neighbours=list(getallneighbours(livefaces.keys(),neighbour_face_dict,set_allowed_faces))
    print(list_neighbours)
    for each_face in list_neighbours:
        n_neighbours=len(neighbour_face_dict[each_face]&set(livefaces.keys()))
        if n_neighbours==3:
            new_live_faces[each_face]=-1
    return new_live_faces
    
def choosenextfaces(faces,livefaces,includedfaces,fork_chance,upward_chance,death_chance,growth_mode,set_allowed_faces):
    tnlivefaces=dict()
    livefaceslist=list(livefaces.keys())
    for iface in livefaceslist:
        nlivefaces=dict()
        if random.random()<fork_chance:
            willfork=1
        else:
            willfork=0
        if random.random()<upward_chance:
            willclimb=1
            print('Path will attempt to climb...')
        else:
            willclimb=0
        if random.random()<death_chance and len(tnlivefaces)>0:
            print('Dead end')
        else:
            #not dieing out
            neighbourfacesset=getneighbouringfaces(faces,iface,2,set_allowed_faces)
            if iface in neighbourfacesset:
                neighbourfacesset.remove(iface)
            neighbourfaceslist=list(neighbourfacesset)
            acceptedneighbours=[]
            #remove unsuitable options
            if growth_mode==0 or growth_mode==1:
                for neighbourface in neighbourfaceslist:
                    #so if the value()=-1 then remove all of the neighbours of the liveface
                    if doesfaceneighbour(faces,(includedfaces-set([iface]))-set([livefaces[iface]]),neighbourface,set_allowed_faces)==False:
                        acceptedneighbours.append(neighbourface)
            elif growth_mode==2:
                acceptedneighbours=neighbourfaceslist
            if growth_mode==0:
                #need a list >= length 1+willfork
                while len(acceptedneighbours)<(willfork+1) and len(neighbourfacesset)>0:
                    #pop a random item from the neighbourfacesset into the acceptedneighbours list
                    tmpset=set(acceptedneighbours)
                    tmpset.add(neighbourfacesset.pop())
                    acceptedneighbours=list(tmpset)        
                #now acceptedneighbours contains a list of possible options
                #if willclimb==1 then sort them by z
                #else sort them randomly
                if willclimb==1:
                    acceptedneighbours=sortfacelistbyz(faces,acceptedneighbours)
                else:
                    acceptedneighbours=sortfacelistbyrandom(faces,acceptedneighbours)
                #if willfork==1 then select first two
                #if willfork==0 then select first one
                if len(acceptedneighbours)>0:
                    nlivefaces[acceptedneighbours[0]]=iface
                if willfork==1 and len(acceptedneighbours)>1:
                    nlivefaces[acceptedneighbours[1]]=iface
                    print('Path Forked')
            elif (growth_mode==1 or growth_mode==2) and len(acceptedneighbours)>0:
                if willclimb==1:
                    acceptedneighbours=sortfacelistbyz(faces,acceptedneighbours)
                else:
                    acceptedneighbours=sortfacelistbyrandom(faces,acceptedneighbours)
                if len(acceptedneighbours)<(willfork+1):
                    willfork=0
                nlivefaces[acceptedneighbours[0]]=iface
                if willfork==1 and len(acceptedneighbours)>1:
                    nlivefaces[acceptedneighbours[1]]=iface
                    print('Path forked')
                else:
                    print('Could not fork')        
            tnlivefaces.update(nlivefaces)
    return tnlivefaces

#-------------------end choose next algorithms----------------

def initialise_edit_mode():
    #returns boolean - True=restore to edit mode, False=restore to object mode
    if bpy.context.mode!='EDIT_MESH':
        bpy.ops.object.editmode_toggle()
        return False
    else:
        return True

def initialise_object_mode():
    #returns boolean - True=restore to edit mode, False=restore to object mode
    if bpy.context.mode=='EDIT_MESH':
        bpy.ops.object.editmode_toggle()
        return True
    else:
        return False

def resume_mode(was_in_edit_mode):
    if bpy.context.mode=='EDIT_MESH' and not was_in_edit_mode:
        bpy.ops.object.editmode_toggle()
    if bpy.context.mode!='EDIT_MESH' and was_in_edit_mode:
        bpy.ops.object.editmode_toggle()

def selectset(faces,selset):
    was_in_edit_mode=initialise_edit_mode()
    bpy.context.tool_settings.mesh_select_mode=[False,False,True]
    bpy.ops.mesh.select_all(action='DESELECT')
    initialise_object_mode()
    list_selset=list(selset)
    for each_face in selset:
        faces[each_face].select=True
    resume_mode(was_in_edit_mode)
    return faces

def selectget(faces):
    was_in_edit_mode=initialise_object_mode()
    if bpy.context.tool_settings.mesh_select_mode!=[False,False,True]:
        bpy.context.tool_settings.mesh_select_mode=[False,False,True]
    select_set=set()
    for index,each_face in enumerate(faces):
        if each_face.select==1:
            select_set.add(index)
    resume_mode(was_in_edit_mode)
    return select_set

def find_corresponding_mushroom_vertex_groups(mushrooms_list,target_object,prefix):
    #prefix is OB for objects
    #prefix is MA for materials, mushrooms_list=materials_list
    vertex_group_lookup=dict()
    mushroom_names=[each_mushroom.name for each_mushroom in mushrooms_list]
    for index,vertex_group in enumerate(target_object.vertex_groups):
        if vertex_group.name[:len(prefix)]==prefix and vertex_group.name[len(prefix):] in mushroom_names:
            vertex_group_lookup[index]=vertex_group.name
    return vertex_group_lookup

def get_face_groupchance_dict(target_object,faceid,mushrooms_list,lookup):
    group_chance=dict()
    for each_vertex in [target_object.data.vertices[vertex_index] for vertex_index in target_object.data.faces[faceid].vertices]:
        for vertex_group in each_vertex.groups:
            if vertex_group.group in lookup.keys():
                if vertex_group.group in group_chance.keys():
                    group_chance[vertex_group.group]+=vertex_group.weight
                else:
                    group_chance[vertex_group.group]=vertex_group.weight 
    return group_chance

def choose_mushroom_from_vertex_weights(mushrooms_list,lookup,return_random,group_chance):
    #mushrooms list can be a list of materials
    #lookup can be a material lookup
    #returns a name only not a data path
    #if return_random==True then a random object from the list is returned if no valid vert weights exist
    #if return_random!=True then -1 is returned is [ditto]
    list_group_chance=list(group_chance.keys())
    sum_weights=0
    for index in list_group_chance:
        sum_weights+=group_chance[index]
    if sum_weights>0:
        result=random.random()*sum_weights
        sum_weights=0
        for index in list_group_chance:
            sum_weights+=group_chance[index]
            if sum_weights>result:
                return lookup[index][2:]
        return lookup[list(group_chance.keys())[index]][2:]
    elif return_random:
        return random.choice(mushrooms_list).name
    else:
        return -1
            
def place_many_on_face(target_object, faceid, mushrooms_list, number_to_distribute, distribute_method, distribute_jitter,pack_mode,vertex_group_lookup):
    #distribute method
    #0=uniform
    #1=random
    #2=jitter
    if distribute_method==0:
        place_points=get_points_jittered(target_object,faceid,number_to_distribute,distribute_jitter)
    elif distribute_method==1:
        place_points=get_points_random(target_object,faceid,number_to_distribute)
    else:
        print('incorrect jitter mode!')
        return -1
    if pack_mode=='TIGHT':
        place_points_with_scales=get_points_scales_tightpack(target_object,faceid,place_points)
    else:
        place_points_with_scales=get_points_scales(target_object,faceid,place_points)
    placed_data=[]
    groupchance=get_face_groupchance_dict(target_object,faceid,mushrooms_list,vertex_group_lookup)
    for point in place_points_with_scales:
        mushroom_choice=bpy.data.objects[choose_mushroom_from_vertex_weights(mushrooms_list,vertex_group_lookup,True,groupchance)]
        placed_data.append(place_on_face(target_object, faceid, mushroom_choice, point[0],mathutils.Vector((point[1],point[1],point[1]))))
    return placed_data

def insert_keyframes(target_object,start_frame,shapes_lifecycle,frames_per_shape,jitter):
    #target_object=target object name
    #start frame = start frame number
    #shapes available is an int referring to the max number of shapes s+str(a+1) for a in range(0,shapes_available)
    #frames_per_shape - how much to advace between each shape
    #jitter - 0>1 ... affects frames_per_shape
    last_shape_name=''
    #set frame
    bpy.context.scene.frame_current=int(start_frame)
    actual_start_frame=bpy.context.scene.frame_current=int(bpy.context.scene.frame_current+(frames_per_shape*(1+(2*random.random()*jitter))))
    shapes_available=len(shapes_lifecycle)
    for shape_id,current_shape_name in enumerate(shapes_lifecycle):
        if shape_id<(shapes_available-1):
            next_shape_name=shapes_lifecycle[shape_id+1]
            target_object.data.shape_keys.keys[next_shape_name].value=0
            target_object.data.shape_keys.keys[next_shape_name].keyframe_insert('value')
            #target_object.keyframe_insert('data.shape_keys.keys[\"'+next_shape_name+'\"].value')
        if last_shape_name!='':
            target_object.data.shape_keys.keys[last_shape_name].value=0
            target_object.data.shape_keys.keys[last_shape_name].keyframe_insert('value')
            #target_object.keyframe_insert('data.shape_keys.keys[\"'+last_shape_name+'\"].value')
        target_object.data.shape_keys.keys[current_shape_name].value=1
        target_object.data.shape_keys.keys[current_shape_name].keyframe_insert('value')
        #target_object.keyframe_insert('data.shape_keys.keys[\"'+current_shape_name+'\"].value')
        #advance frames
        bpy.context.scene.frame_current=int(bpy.context.scene.frame_current+(frames_per_shape*(1+(2*random.random()*jitter))))
        last_shape_name=current_shape_name
    return [actual_start_frame,int(bpy.context.scene.frame_current)]

def add_z_up_driver(mushroom_object,bend_key_name,start_frame,end_frame):
    driver_curve=mushroom_object.data.shape_keys.keys[bend_key_name].driver_add('value')
    #driver_curve=mushroom_object.driver_add('data.shape_keys.keys[\"'+bend_key_name+'\"].value')
    z_var=driver_curve.driver.variables.new()
    z_var.type='SINGLE_PROP'
    z_var.targets[0].id_type='OBJECT'
    z_var.targets[0].id=mushroom_object
    #[11] is combined xy
    z_var.targets[0].data_path='matrix_world[10]'
    
    z_sc=driver_curve.driver.variables.new()
    z_sc.type='SINGLE_PROP'
    z_sc.targets[0].id_type='OBJECT'
    z_sc.targets[0].id=mushroom_object
    z_sc.targets[0].data_path='scale[z]'
    
    if start_frame!=-1 and end_frame!=-1:
        current_frame_var=driver_curve.driver.variables.new()
        current_frame_var.type='SINGLE_PROP'
        current_frame_var.targets[0].id_type='SCENE'
        current_frame_var.targets[0].id=bpy.context.scene
        current_frame_var.targets[0].data_path='frame_current'
        mid_frame=(start_frame+end_frame)/2
        range_frame=(end_frame-start_frame)
        driver_curve.driver.expression='(1-('+z_var.name+'/'+z_sc.name+'))*(2.7182**(-1*((('+current_frame_var.name+'-'+str(mid_frame)+')/('+str(range_frame)+'*0.2))**2)))'
    else:
        driver_curve.driver.expression='1-('+z_var.name+'/'+z_sc.name+')'

def zero_all_shape_keys(mushroom_object):
    mushroom_object.data.shape_keys.animation_data_clear()
    for each_key in mushroom_object.data.shape_keys.keys:
        each_key.value=0

def insert_keyframes_multi(mushrooms_list,start_frame,mushrooms_shapes_database,lifetime,lifetime_jitter,start_frame_variation,start_frame_jitter,random_shape_mode,bend_shape_mode):
    #try '["blah"]' or "['dfdf']"
    target_frame=start_frame
    for mushroom_object in mushrooms_list:
        #load shapes_lifecycle etc. based on the mushroom.name
        shapes_lifecycle=mushrooms_shapes_database[0][mushroom_object[1]]
        shapes_random=mushrooms_shapes_database[1][mushroom_object[1]]
        shapes_bend=mushrooms_shapes_database[2][mushroom_object[1]]
        frame_spread=[]
        
        if shapes_lifecycle==['USEEXIST']:
            frame_spread=reanimate_actions(mushroom_object[0],target_frame,target_frame+lifetime,lifetime_jitter)
        elif shapes_lifecycle!=[]:
            zero_all_shape_keys(mushroom_object[0])
            frame_spread=insert_keyframes(mushroom_object[0],target_frame,shapes_lifecycle,lifetime/len(shapes_lifecycle),lifetime_jitter)
        else:
            #there script has not inserted any animation on the mushroom, and no animation data should be preserved
            zero_all_shape_keys(mushroom_object[0])
            
        if len(shapes_random)>0:
            if frame_spread!=[] and random_shape_mode!="ON":
                #if keyframes have been inserted/edited
                #add the random shape key data
                halfway_frame=int((frame_spread[0]+frame_spread[1])/2)
                random_shape=shapes_random[int(random.random()*(len(shapes_random)-1))]
                bpy.context.scene.frame_current=frame_spread[0]
                mushroom_object[0].data.shape_keys.keys[random_shape].value=0
                mushroom_object[0].data.shape_keys.keys[random_shape].keyframe_insert('value')
                #mushroom_object[0].keyframe_insert('data.shape_keys.keys[\"'+random_shape+'\"].value')
                bpy.context.scene.frame_current=halfway_frame
                mushroom_object[0].data.shape_keys.keys[random_shape].value=random.random()
                mushroom_object[0].data.shape_keys.keys[random_shape].keyframe_insert('value')
                #mushroom_object[0].keyframe_insert('data.shape_keys.keys[\"'+random_shape+'\"].value')
                bpy.context.scene.frame_current=frame_spread[1]
                mushroom_object[0].data.shape_keys.keys[random_shape].value=0
                mushroom_object[0].data.shape_keys.keys[random_shape].keyframe_insert('value')
                #mushroom_object[0].keyframe_insert('data.shape_keys.keys[\"'+random_shape+'\"].value')
            else:
                #just set a shape key value for random
                random_shape=shapes_random[int(random.random()*(len(shapes_random)-1))]
                mushroom_object[0].data.shape_keys.keys[random_shape].value=random.random()
            
        if len(shapes_bend)>0:
            if frame_spread!=[] and bend_shape_mode!="ON":
                bend_shape=shapes_bend[int(random.random()*(len(shapes_bend)-1))]
                #add a gaussion rise and fall with y rotation driven shape key
                add_z_up_driver(mushroom_object[0],bend_shape,frame_spread[0],frame_spread[1])
            else:
                bend_shape=shapes_bend[int(random.random()*(len(shapes_bend)-1))]
                #add a gaussion rise and fall with y rotation driven shape key
                #calling the z driver adder with -1 and -1 tells it to skip the gaussian curve falloff and just add a simple driver
                add_z_up_driver(mushroom_object[0],bend_shape,-1,-1)
                
        target_frame+=start_frame_variation*(1+(2*random.random()*start_frame_jitter))
        
def add_mushroom_shrinkwrap(target_object,mushroom_object_list,vertex_group):
    #this is only called if vertex group!=-1
    for mushroom_object in mushroom_object_list:
        mushroom_shrinkwrap_modifier=mushroom_object[0].modifiers.new(type='SHRINKWRAP', name='mushroom_shrinkwrap')
        mushroom_shrinkwrap_modifier.target=target_object
        mushroom_shrinkwrap_modifier.vertex_group=vertex_group
        
def add_mushrooms_to_group(mushroom_object_list,group_name):
    for mushroom_object in mushroom_object_list:
        bpy.data.groups[group_name].objects.link(mushroom_object[0])
        
def build_materials_list(mushrooms_list):
    materials_list=[]
    for each_mushroom in mushrooms_list:
        for each_material in each_mushroom.material_slots:
            materials_list.append(each_material.material)
    return materials_list

def set_materials(mushrooms_list,target_object,faceid,randomize_material,materials_list,vertex_group_lookup_materials):
    groupchance=get_face_groupchance_dict(target_object,faceid,materials_list,vertex_group_lookup_materials)
    for mushroom_object in mushrooms_list:
        for material_slot in mushroom_object[0].material_slots:
            if 'material' in dir(material_slot):
                material_slot_new=choose_mushroom_from_vertex_weights(materials_list,vertex_group_lookup_materials,False,groupchance)
                if material_slot_new!=-1:
                    material_slot.material=bpy.data.materials[material_slot_new]
                elif randomize_material:
                    material_slot.material=random.choice(materials_list)

def get_allowed_faces(target_object,vertex_group_name):
    if bpy.context.mode!='EDIT_MESH':
        bpy.context.scene.objects.active=target_object
        bpy.ops.object.editmode_toggle()
    #now in edit mode
    bpy.context.tool_settings.mesh_select_mode=[True,False,False]
    if vertex_group_name!='-1':
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_set_active(group=vertex_group_name)
        bpy.ops.object.vertex_group_select()
        #leave edit mode
        bpy.ops.object.editmode_toggle()
        set_allowed_faces=selectget(target_object.data.faces)
    else:
        #leave edit mode
        bpy.ops.object.editmode_toggle()
        set_allowed_faces=set(range(0,len(target_object.data.faces)))
    return set_allowed_faces

def find_live_faces(selected_faces,set_allowed_faces):
    #returns a dict
    #keys are the live faces keys, values are -1 (indicating initial state)
    livefaces=dict()
    for index in selected_faces:
        if index in set_allowed_faces:
            livefaces[index]=-1
    if len(livefaces.keys())==0:
        print('Nothing in the masking group was selected... randomizing... ')
        livefaces[random.choice(list(set_allowed_faces))]=-1
    print ('Selection is: '+str(livefaces))
    return livefaces

def save_timing(target_object,faces,livefaces,timing_group_name,value):
    was_in_edit_mode=initialise_object_mode()
    bpy.context.scene.objects.active=target_object
    bpy.ops.object.vertex_group_set_active(group=timing_group_name)
    selectset(faces,set(livefaces.keys()))
    bpy.ops.object.editmode_toggle()
    #now in edit mode
    bpy.context.tool_settings.vertex_group_weight=value
    bpy.ops.object.vertex_group_assign(new=False)
    resume_mode(was_in_edit_mode)

#-------------new animation defs---------------

def prepend_data_path(list_fcurve,data_path_prefix):
    #data path prefix does not include the dot
    for each_fcurve in list_fcurve:
        each_fcurve.data_path=data_path_prefix+'.'+each_fcurve.data_path
        
def copy_fcurves(mushroom_object,host_action,data_path_prefix,time_scale,time_shift,time_jitter):
    #this def is for when blender gets fixed
    #time_scale is time multiplier about zero, followed by adding time_shift
    time_scale+=time_jitter*(time_scale*random.uniform(-1,1))
    mushroom_object.animation_data_create()
    mushroom_object.animation_data.action=bpy.data.actions.new('mushroom_AC')
    for each_fcurve in host_action.fcurves:
        copy_fcurve=mushroom_object.animation_data.action.fcurves.new(data_path_prefix+'.'+each_fcurve.data_path)
        copy_fcurve.data_path=(data_path_prefix+'.'+each_fcurve.data_path)
        #adjust the keyframe on the newly created fcurve
        last_time=(time_scale*each_fcurve.keyframe_points[0].co.x)+time_shift
        for o_kp in each_fcurve.keyframe_points:
            new_time=(time_scale*o_kp.co.x)+time_shift
            new_time=(new_time*(1-time_jitter))+((new_time-((new_time-last_time)*random.random()))*time_jitter)
            print(copy_fcurve.keyframe_points.add(0,0))
            c_kp=copy_fcurve.keyframe_points.add(new_time, o_kp.co.y, True,False,True)
            c_kp.interpolation=o_kp.interpolation
            c_kp.handle_left=o_kp.handle_left
            c_kp.handle_left_type=o_kp.handle_left_type
            c_kp.handle_right=o_kp.handle_right
            c_kp.handle_right_type=o_kp.handle_right_type
            last_time=new_time
            
def adjust_fcurves(host_action,time_scale,time_shift,time_jitter):
    if 'fcurves' in dir(host_action):
        for each_fcurve in host_action.fcurves:
            last_time=(time_scale*each_fcurve.keyframe_points[0].co.x)+time_shift
            for o_kp in each_fcurve.keyframe_points:
                new_time=(time_scale*o_kp.co.x)+time_shift
                new_time=(new_time*(1-time_jitter))+((new_time-((new_time-last_time)*random.random()))*time_jitter)
                o_kp.co.x=new_time
                last_time=new_time

def reanimate_actions(mushroom_object,start_frame,end_frame,time_jitter):
    #assuming the duplicate is linked, transfer the animation data to object level
    if 'action' in dir(mushroom_object.data.shape_keys.animation_data):
        #copy_fcurves(mushroom_object,mushroom_object.data.shape_keys.animation_data.action,'data.shape_keys',(end_frame-start_frame)/100,start_frame,time_jitter)
        adjust_fcurves(mushroom_object.data.shape_keys.animation_data.action,(end_frame-start_frame)/100,start_frame,time_jitter)
    for mat_index,material_slot in enumerate(mushroom_object.material_slots):
        if 'material' in dir(material_slot):
            if is_animated(material_slot.material):
                #copy_fcurves(mushroom_object,material_slot.material.animation_data.action,'material_slot['+str(mat_index)+'].material',(end_frame-start_frame)/100,start_frame,time_jitter)
                material_slot.material=material_slot.material.copy()
                adjust_fcurves(material_slot.material.animation_data.action,(end_frame-start_frame)/100,start_frame,time_jitter)
            for tex_index,texture_slot in enumerate(material_slot.material.texture_slots):
                if 'texture' in dir(texture_slot):
                    if is_animated(texture_slot.texture):
                        texture_slot.texture=texture_slot.texture.copy()
                        #copy_fcurves(mushroom_object,texture_slot.texture.animation_data.action,'material_slot['+str(mat_index)+'].material.texture_slot['+str(tex_index)+'].texture',(end_frame-start_frame)/100,start_frame,time_jitter)
                        adjust_fcurves(texture_slot.texture.animation_data.action,(end_frame-start_frame)/100,start_frame,time_jitter)
    return [int(start_frame),int(end_frame)]
    

#-----------------------------------------------

def is_animated(datablock):
    if ('animation_data' in dir(datablock)) and ('action' in dir(datablock.animation_data)) and ('fcurves' in dir(datablock.animation_data.action)) and len(datablock.animation_data.action.fcurves)>0:
        return True
    else:
        return False

def generate_mushrooms_shapes_database(mushrooms_list,target_object,shape_key_dict_prefixes):
    #list[0=lifecycle,1=random,2=bend]=dict[mushroom_object.name]=[names of shapes...]
    #target_object.mushroomer_lifecycle_key_set is a string prefix, for examples "s"
    #shape_key_dict_prefixes [mushroom name][prefix]
    mushroom_shapes_database=[dict(),dict(),dict()]
    for mushroom_object in mushrooms_list:
        if target_object.mushroomer_lifecycle_key_set!="IGNORE" and target_object.mushroomer_lifecycle_key_set!="USEEXIST" and (target_object.mushroomer_lifecycle_key_set in shape_key_dict_prefixes[mushroom_object.name]):
            mushroom_shapes_database[0][mushroom_object.name]=[target_object.mushroomer_lifecycle_key_set+str(dict_list_item[0]) for dict_list_item in shape_key_dict_prefixes[mushroom_object.name][target_object.mushroomer_lifecycle_key_set]]
        elif target_object.mushroomer_lifecycle_key_set=="USEEXIST" and is_animated(mushroom_object.data.shape_keys):
            mushroom_shapes_database[0][mushroom_object.name]=['USEEXIST']
        else: mushroom_shapes_database[0][mushroom_object.name]=[]
        
        if target_object.mushroomer_random_key_set!="IGNORE" and (target_object.mushroomer_random_key_set in shape_key_dict_prefixes[mushroom_object.name]):
            mushroom_shapes_database[1][mushroom_object.name]=[target_object.mushroomer_random_key_set+str(dict_list_item[0]) for dict_list_item in shape_key_dict_prefixes[mushroom_object.name][target_object.mushroomer_random_key_set]]
        else: mushroom_shapes_database[1][mushroom_object.name]=[]
        
        if target_object.mushroomer_bend_key_set!="IGNORE" and (target_object.mushroomer_bend_key_set in shape_key_dict_prefixes[mushroom_object.name]):
            mushroom_shapes_database[2][mushroom_object.name]=[target_object.mushroomer_bend_key_set+str(dict_list_item[0]) for dict_list_item in shape_key_dict_prefixes[mushroom_object.name][target_object.mushroomer_bend_key_set]]
        else: mushroom_shapes_database[2][mushroom_object.name]=[]
        
    print(mushroom_shapes_database)
    return mushroom_shapes_database
    
#begin UI code

def find_mushrooms(context):
    mushrooms_list=[]
    for try_object in context.selected_objects:
        if try_object!=context.active_object:
            mushrooms_list.append(try_object)
    return mushrooms_list
    

class Mushroomer(bpy.types.Operator):
    '''plants mushrooms on your mesh'''
    bl_idname = "mesh.mushroom_maker"
    bl_label = "Mushroomer"
    bl_options = {'REGISTER', 'UNDO'}
    dialog_width=600
    
    title_label_text=''    
    mushrooms_list=[]
    shape_key_dict_prefixes=dict()

    target_object_name=bpy.props.StringProperty(name="Target Object", description="Object receiving the mushrooms",default="")
    iterations=bpy.props.IntProperty(name="Generations of Mushrooms", description="Number of generations",default=5,min=0,max=200)
    global_start_frame=bpy.props.IntProperty(name="Start Frame", description="Start Frame",default=1,min=0)
    children_first_generation=bpy.props.IntProperty(name="1st Generation Mushroom Family Size", description="1st Generation Mushroom Family Size",default=1,min=0)
    children_last_generation=bpy.props.IntProperty(name="Last Generation Mushroom Family Size", description="Last Generation Mushroom Family Size",default=5,min=0)
    children_mode_list=[("CHM","Family Size Growth Mode","Family Size Growth Mode"),
                        ("0","Constant","Constant"),
                        ("1","Linear","Linear"),
                        ("2","Square","Square"),
                        ("3","Fibonacci","Fibonacci"),
                        ("4","Square Root","Square Root")]
    children_mode=bpy.props.EnumProperty(attr="children_mode",items=children_mode_list,default="1")
    children_jitter=bpy.props.FloatProperty(name="Family Size Jitter", description="Number of generations",default=0.1,min=0,max=1,step=0.1,precision=2)
    gen_frame_adv=bpy.props.IntProperty(name="Child Bearing Age", description="Child Bearing Age",default=10,min=2)
    gen_frame_adv_jitter=bpy.props.FloatProperty(name="Child Bearing Age Jitter", description="Child Bearing Age Jitter",default=0.1,min=0,max=1,step=0.1,precision=2)
    instance_lifetime=bpy.props.IntProperty(name="Death Age", description="Death Age",default=20,min=2)
    instance_lifetime_jitter=bpy.props.FloatProperty(name="Death Age Jitter", description="Death Age Jitter",default=0.1,min=0,max=1,step=0.1,precision=2)
    sub_gen_spread=bpy.props.IntProperty(name="Generational Spread (frames)", description="The maximum length of time from the first birth to the last birth",default=10,min=0)
    sub_gen_spread_jitter=bpy.props.FloatProperty(name="Generational Spread Jitter", description="Generational Spread Jitter",default=0.1,min=0,max=1,step=0.1,precision=2)
    distribute_method_list=[("DM","Distribution Method","How the mushrooms are distributed on each face"),
                            ("0","Uniform","Uniform"),
                            ("1","Random","Random")]
    distribute_method=bpy.props.EnumProperty(attr="distribute_method",items=distribute_method_list,default="1")
    distribute_jitter=bpy.props.FloatProperty(name="Distribution Jitter", description="Distribution Jitter",default=0.5,min=0,max=1,step=0.1,precision=2)
    growth_mode_list=[("GM","Growth Method","How the mushrooms spread out from their start face"),
                            ("0","Crossed Paths","Crossed Paths"),
                            ("1","Forked Paths","Forked Paths"),
                            ("2","Splurge","Splurge"),
                            ("3","Conway's Game of Life","Game of Life"),
                            ("4","Simple Selection Growth","Simple Selection Growth")]
    growth_mode=bpy.props.EnumProperty(attr="growth_mode",items=growth_mode_list,default="1")
    death_chance=bpy.props.FloatProperty(name="Family Wipeout Chance", description="Family Wipeout Chance",default=0.1,min=0,max=1,step=0.1,precision=2)
    upward_chance=bpy.props.FloatProperty(name="Upwards Attraction (climb chance)", description="Probability children will choose to move up",default=0.7,min=0,max=1,step=0.1,precision=2)
    fork_chance=bpy.props.FloatProperty(name="Probability of Family/Fork Split", description="Probability the family will split into two different groups of children",default=0.5,min=0,max=1,step=0.1,precision=2)
    pack_mode_list=[("PM","Packing Method","Algorithm for Packing/Sizing Mushrooms"),
                            ("LAZY","Lazy Pack (faster)","Lazy Pack - Half Nearest Neighbour Distance"),
                            ("TIGHT","Tight Pack","Tight Pack")]
    pack_mode=bpy.props.EnumProperty(attr="pack_mode",items=pack_mode_list,default="LAZY")
    randomize_materials=bpy.props.BoolProperty(name="Randomize Materials",description="if ticked materials from any slot on any object an be shuffled between objects: beware UV people!",default=False)
    shape_mode_list=[("SBM","Shape Blending Mode","Shape Blending Mode"),
                            ("SMOOTH","Smooth Off-On-Off Bezier Curve","Smooth Off-On-Off Bezier Curve"),
                            ("ON","Always On (Default when animation data not present)","On (Default when animation data not present)")]
    random_shape_mode=bpy.props.EnumProperty(attr="random_shape_mode",items=shape_mode_list,default="SMOOTH")
    bend_shape_mode=bpy.props.EnumProperty(attr="bend_shape_mode",items=shape_mode_list,default="SMOOTH")
    
    
    #in invoke to do automatically...
    #get the first selected but not active mushroom -> name -> self.properties.ob_to_distribute....
    def invoke(self, context, event):
        #all the generator functions stoe their result on the target object
        #but take info from the list of mushrooms
        self.properties.target_object_name=context.active_object.name
        self.mushrooms_list=find_mushrooms(context)
        self.title_label_text='Mushrooming: '
        for mushroom_object in self.mushrooms_list:
            self.title_label_text=self.title_label_text+mushroom_object.name+', '
        self.title_label_text=self.title_label_text.rstrip(', ')+' all over '+self.properties.target_object_name
        self.shape_key_dict_prefixes=build_prefixes_enum(self.mushrooms_list,bpy.data.objects[self.properties.target_object_name])
        build_vertex_group_enum(self.mushrooms_list,bpy.data.objects[self.properties.target_object_name])
        build_group_name_text(bpy.data.objects[self.properties.target_object_name])
        build_face_limit_enum(bpy.data.objects[self.properties.target_object_name])
        self.properties.global_start_frame=bpy.context.scene.frame_current
        wm = context.window_manager
        wm.invoke_props_dialog(self, self.dialog_width)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        props = self.properties

        layout.label(text=self.title_label_text)
        layout.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_grouping", text="Group To Append Mushrooms To")
        layout.prop(props, "iterations")
        layout.prop(props, "global_start_frame")

        layout.label(text="Family Settings")
        row = layout.row()
        split = row.split(percentage=0.5)
        colL = split.column()
        colR = split.column()
        colL.prop(props, "children_first_generation")
        colR.prop(props, "children_last_generation")
        colL.prop(props, "children_mode")
        colR.prop(props, "children_jitter",slider=True)
        colL.prop(props, "gen_frame_adv")
        colR.prop(props, "gen_frame_adv_jitter",slider=True)
        colL.prop(props, "instance_lifetime")
        colR.prop(props, "instance_lifetime_jitter",slider=True)
        colL.prop(props, "sub_gen_spread")
        colR.prop(props, "sub_gen_spread_jitter",slider=True)
        colL.prop(props, "distribute_method")
        colR.prop(props, "distribute_jitter",slider=True)
        colL.prop(props, "pack_mode")
        colR.prop(props, "randomize_materials")

        layout.label(text="Spread & Conquer Settings")
        layout.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_limit_group", text="Limit to Vertex Group")
        row = layout.row()
        split = row.split(percentage=0.5)
        colL = split.column()
        colR = split.column()
        colL.prop(props, "growth_mode")
        colR.prop(props, "fork_chance",slider=True)
        colL.prop(props, "upward_chance",slider=True)
        colR.prop(props, "death_chance",slider=True)
        
        layout.label(text="Shape Key Settings")
        layout.label(text="NB. Pre-animated mushrooms must have actions from frames 0-100")
        layout.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_lifecycle_key_set", text="Animation: Manual / Lifecycle Shape Set")
        row = layout.row()
        split = row.split(percentage=0.7)
        colL = split.column()
        colR = split.column()
        colL.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_random_key_set", text="Random Shape Set")
        colR.prop(props, "random_shape_mode")
        colL.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_bend_key_set", text="Bend Upwards Shape Set")
        colR.prop(props, "bend_shape_mode")
        layout.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_shrinkwrap_vg", text="Vertex Group for Shrinkwrap")
        
    def execute(self,context):
        if len(self.mushrooms_list)==0:
            print('Select a mushroom first, you monkey.')
            return {'FINISHED'}
        target_object=bpy.data.objects[self.properties.target_object_name]
        mushroom_group_name=target_object.mushroomer_grouping
        if mushroom_group_name!='':
            if (mushroom_group_name not in bpy.data.groups):
                bpy.data.groups.new(mushroom_group_name)
            if (("MT"+mushroom_group_name) not in target_object.vertex_groups):
                timing_group_name=(target_object.vertex_groups.new("MT"+mushroom_group_name)).name
        mushrooms_shapes_database=generate_mushrooms_shapes_database(self.mushrooms_list,target_object,self.shape_key_dict_prefixes)
        generation_frame=self.properties.global_start_frame
        vertex_group_lookup=find_corresponding_mushroom_vertex_groups(self.mushrooms_list,target_object,'OB')
        materials_list=build_materials_list(self.mushrooms_list)
        vertex_group_lookup_materials=find_corresponding_mushroom_vertex_groups(materials_list,target_object,'MA')
        includedfaces=set()
        #save the selection before the other defs mess with it
        faces=target_object.data.faces
        selected_faces=list(selectget(faces))
        set_allowed_faces=get_allowed_faces(target_object,str(target_object.mushroomer_limit_group))
        #if nothing is selected then randomise the selection
        #livefaces is a dict... livefaces[faceid]=
        livefaces=find_live_faces(selected_faces,set_allowed_faces)
        if self.properties.growth_mode=="3":
            neighbour_face_dict=build_neighbour_faces_dict(target_object,set_allowed_faces)
        if len(livefaces)>0:
            includedfaces|=set(livefaces.keys())
            for count in range(0,self.properties.iterations):
                print ('Iteration:'+str(count))
                if self.properties.growth_mode=="3":
                    livefaces=choosenextfaces_conways(faces,livefaces,neighbour_face_dict,set_allowed_faces)
                    populate_list=livefaces.keys()
                elif self.properties.growth_mode=="4":
                    livefaces=choosenextfaces_simpleincrease(target_object,faces,livefaces,includedfaces,set_allowed_faces)
                    populate_list=list(set(livefaces.keys())-includedfaces)
                else:
                    livefaces=choosenextfaces(faces,livefaces,includedfaces,self.properties.fork_chance,self.properties.upward_chance,self.properties.death_chance,int(self.properties.growth_mode),set_allowed_faces)
                    populate_list=list(set(livefaces.keys())-includedfaces)
                
                print('\n\tPopulating '+str(len(populate_list))+' faces...')
                print('\tLivefaces are: '+str(livefaces)+'\n')
                for face_to_populate in populate_list:
                    children_this_generation=get_number_for_generation(count,self.properties.iterations,int(self.properties.children_mode),self.properties.children_first_generation,self.properties.children_last_generation,self.properties.children_jitter)
                    print('\t\tPlacing '+str(children_this_generation)+' mushrooms...')
                    placed_objects=place_many_on_face(target_object, face_to_populate, self.mushrooms_list,children_this_generation, int(self.properties.distribute_method), self.properties.distribute_jitter,self.properties.pack_mode,vertex_group_lookup)
                    print('\t\tMaterialing '+str(children_this_generation)+' mushrooms...')
                    set_materials(placed_objects,target_object,face_to_populate,self.properties.randomize_materials,materials_list,vertex_group_lookup_materials)
                    #placed objects is a list of [object structures (not names),names of types]
                    print('\t\tKeyframing '+str(children_this_generation)+' mushrooms...\n')
                    insert_keyframes_multi(placed_objects,generation_frame,mushrooms_shapes_database,self.properties.instance_lifetime,self.properties.instance_lifetime_jitter,self.properties.sub_gen_spread/children_this_generation,self.properties.sub_gen_spread_jitter,self.properties.random_shape_mode,self.properties.bend_shape_mode)
                    if target_object.mushroomer_shrinkwrap_vg!='-1':
                        add_mushroom_shrinkwrap(target_object,placed_objects,target_object.mushroomer_shrinkwrap_vg)
                    if mushroom_group_name!='':
                        add_mushrooms_to_group(placed_objects,mushroom_group_name)
                
                if mushroom_group_name!='':
                    save_timing(target_object,faces,livefaces,timing_group_name,count/self.properties.iterations)
                #if everything has died out then regenerate...
                if len(livefaces)<1:
                    if self.properties.growth_mode!="3":
                        print('Regenerating...')
                        tmplist=list(includedfaces)
                        livefaces[random.choice(tmplist)]=-1
                        #so if the value()=-1 then all of the neighbouring faces can be considered for expansion onto
                    else:
                        print('Everything died, Conway\'s game over.')
                        break  
                includedfaces|=set(livefaces.keys())
                generation_frame+=self.properties.gen_frame_adv*(1+(2*random.random()*self.properties.gen_frame_adv_jitter))
            #display the last set of included faces
            print('Building selection for user...')
            selectset(faces,includedfaces)
            initialise_edit_mode()
            print('Finished!')
            
        else:
            print('The masking group is empty - can\'t contnue!')
        return {'FINISHED'}
        
        
#end UI code

class MushroomerRetime(bpy.types.Operator):
    '''retimes mushrooms in a given group from group weights'''
    bl_idname = "mesh.mushroom_retimer"
    bl_label = "Mushroomer Retimer"
    bl_options = {'REGISTER', 'UNDO'}
    dialog_width=250
    
    target_object_name=bpy.props.StringProperty(name="Target Object", description="Object receiving the mushrooms",default="")
    global_start_frame=bpy.props.IntProperty(name="Start Frame", description="Start Frame",default=1,min=0)
    
    def invoke(self, context, event):
        #all the generator functions store their result on the target object
        #but take info from the list of mushrooms
        self.properties.target_object_name=context.active_object.name
        build_timing_group_enum(bpy.data.objects[self.properties.target_object_name])
        self.properties.global_start_frame=bpy.context.scene.frame_current
        wm = context.manager
        wm.invoke_props_dialog(self, self.dialog_width)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        props = self.properties
        layout.label(text="Retiming "+self.properties.target_object_name)
        layout.prop(props, "global_start_frame")
        layout.prop(bpy.data.objects[self.properties.target_object_name], "mushroomer_timing_vg", text="Vertex Group for Retiming")
        
    def execute(self,context):

        return {'FINISHED'}