print('\033[91m' +"""
 ██▓    ▄▄▄        █████▒▄▄▄      
▓██▒   ▒████▄    ▓██   ▒▒████▄    
▒██░   ▒██  ▀█▄  ▒████ ░▒██  ▀█▄  
▒██░   ░██▄▄▄▄██ ░▓█▒  ░░██▄▄▄▄██ 
░██████▒▓█   ▓██▒░▒█░    ▓█   ▓██▒
░ ▒░▓  ░▒▒   ▓▒█░ ▒ ░    ▒▒   ▓▒█░
░ ░ ▒  ░ ▒   ▒▒ ░ ░       ▒   ▒▒ ░
  ░ ░    ░   ▒    ░ ░     ░   ▒   
    ░  ░     ░  ░             ░  ░  
                                ȜΞΔ"""+ '\033[0m')
from concurrent.futures import process
import cv2
import numpy as np
import os
import concurrent.futures
import keyboard
import open3d as o3d
def D_REBUILD_COLOR (goemetry_ply) :
    color = np.asarray(goemetry_ply.vertex_colors)
    uiq_color = np.unique(color,axis=0)
    new_color = np.concatenate(((np.linspace(0,1,np.shape(uiq_color)[0]+1)[1:][:,np.newaxis]),np.zeros((np.shape(uiq_color)[0],2))),axis=1)
    for i in range (0,np.shape(uiq_color)[0]) :
        new_color[i] = np.roll(new_color[i],i)
    for i in range(0,np.shape(uiq_color)[0]) :
        color[np.all(color==uiq_color[i],axis=1)] = [new_color[i]]
    return color,new_color
def D_BUILD_FOLDER(dir_texture,assign_color) :
    if os.path.exists(dir_texture) != True : 
        os.mkdir(dir_texture)
    for i in range(0,np.shape(assign_color)[0]+1) : 
        if os.path.exists(dir_texture+"\\"+("0000"+str(i))[-3:]) != True : 
            os.mkdir(dir_texture+"\\"+("0000"+str(i))[-3:])
    for i in range(0,np.shape(assign_color)[0]) :
        cv2.imwrite(dir_texture+"\\"+("0000"+str(i))[-3:]+".png",assign_color[i][np.newaxis,:]*255+np.zeros((10000,3)).reshape(100,100,3))
def D_LABEL_COLOR (img,label):
    return np.unique(np.concatenate((img.reshape(-1,1),label.reshape(-1,1)),axis=1),axis=0).astype(int)
def D_SETUP_RENDER (goemetry_ply_copy,size,paint_uniforme_color,Sun,Shadow):
    render = o3d.visualization.rendering.OffscreenRenderer(width=size[1],height=size[0])
    white = o3d.visualization.rendering.MaterialRecord()
    white.base_color = [1.0, paint_uniforme_color[0], paint_uniforme_color[1], paint_uniforme_color[2]]
    white.shader = "defaultLit"
    render.scene.scene.set_sun_light(Sun[0].tolist(), Sun[1].tolist(),Sun[2])
    render.scene.view.ShadowType(int(Shadow[0]))
    goemetry_ply_copy.paint_uniform_color((paint_uniforme_color[0], paint_uniforme_color[1], paint_uniforme_color[2]))
    render.scene.add_geometry("main",goemetry_ply_copy,white)
    return render
def D_POST_PROD (render,img,assign_color,dir_texture,assign_tex,Shadow):
    Material_print,img_shape = np.zeros_like(render),np.shape(img)
    for c in range(0,int(np.max(img))) :
        locals()["PROC_D_POST_PROD_SPEED" + str(c)] = executor.submit(D_POST_PROD_SPEED,img,assign_tex,img_shape,c)
    for c in range(0,int(np.max(img))) :
        Material_print = Material_print+locals()["PROC_D_POST_PROD_SPEED" + str(c)].result()
    return (Material_print/255)*((((render/255-1)*(np.abs(np.array((Shadow[2]))-1).reshape(1,1,3)))+1)*Shadow[1])
def D_POST_PROD_SPEED (img,assign_tex,img_shape,c) :
    tex_c = assign_tex[c]
    return np.roll(np.roll(tex_c,np.random.randint(0,np.shape(tex_c)[0]),axis=0),np.random.randint(0,np.shape(tex_c)[1]),axis=1)[0:img_shape[0],0:img_shape[1],:]*((img==c)[:,:,np.newaxis])
def D_FIND_TEX (dir_texture,assign_color) :
    return [cv2.imread(dir_texture+"/"+(("0000"+str(i))[-3:])+"/"+os.listdir(dir_texture+"/"+("0000"+str(i))[-3:])[0]) for i in range(0,len(assign_color))]
dir_texture = "C:/Users/EBA/Desktop/fre"
np.warnings.filterwarnings('ignore',category=np.VisibleDeprecationWarning)
np.seterr(divide='ignore',invalid='ignore')
goemetry_ply = "C:/Users/EBA/Desktop/fre.ply"
goemetry_ply,goemetry_ply_copy=o3d.io.read_triangle_mesh(goemetry_ply),o3d.io.read_triangle_mesh(goemetry_ply)
color,assign_color = D_REBUILD_COLOR(goemetry_ply)
goemetry_ply.vertex_colors=o3d.utility.Vector3dVector(color)
goemetry_ply_copy.vertex_colors=o3d.utility.Vector3dVector(color)
D_BUILD_FOLDER(dir_texture,assign_color)
assign_tex=D_FIND_TEX (dir_texture,assign_color)
with concurrent.futures.ThreadPoolExecutor() as executor:
    vis=o3d.visualization.Visualizer()
    vis.create_window(width=2560,height=1440)
    render_option=vis.get_render_option()
    render_option.background_color=(0,0,0)
    render_option.point_size = 0.5
    render_option.line_width=0.1
    render_option.light_on=True
    view_control=vis.get_view_control()
    camera_params=view_control.convert_to_pinhole_camera_parameters()
    vis.add_geometry(goemetry_ply, reset_bounding_box=True)
    view_control.change_field_of_view(60)
    vis.poll_events()
    paint_uniforme_color = [1,1,1]
    Sun = [np.array((0.717,0,0.717)),np.array((0.2,0.2,0.2)),65000]
    Shadow =[True,1,[0,0,0]]
    render = D_SETUP_RENDER(goemetry_ply_copy,np.shape(np.asarray(vis.capture_screen_float_buffer())),paint_uniforme_color,Sun,Shadow)
    render_alrd = False
    while True :
        vis.update_renderer()
        vis.poll_events()
        if  keyboard.is_pressed("l"):
            if render_alrd :
                render = D_SETUP_RENDER(goemetry_ply_copy,np.shape(np.asarray(vis.capture_screen_float_buffer())),paint_uniforme_color,Sun,Shadow)
                cv2.destroyAllWindows()
            camera_params=view_control.convert_to_pinhole_camera_parameters()
            render.setup_camera(camera_params.intrinsic,camera_params.extrinsic)
            
            img=np.flip(np.asarray(vis.capture_screen_float_buffer()),2)
            img = np.round(np.sum(img,axis=2)*np.shape(assign_color)[0])
            render=np.asarray((render.render_to_image()))
            output = D_POST_PROD (render,img,assign_color,dir_texture,assign_tex,Shadow)
            cv2.imshow('output',output)
            render_alrd = True
        if keyboard.is_pressed("m"):
            cv2.destroyAllWindows()
            render = D_SETUP_RENDER(goemetry_ply_copy,np.shape(np.asarray(vis.capture_screen_float_buffer())),paint_uniforme_color,Sun,Shadow)
            render_alrd = False
        if  keyboard.is_pressed("q"):
                cv2.destroyAllWindows()
                break
        if keyboard.is_pressed("s") :
            print('\033[95m' +"\nSetup \n---------------"+ '\033[0m')
            while True :
                Commande = input("Command = ")
                if Commande == "h" :
                    print('\033[95m' +"\nHelp \n---------------"+ '\033[0m')
                    print("""h => help
q => quit
s => sun
b => shadow
p => paint uniform
c => camera angle""")
                if Commande == "s" :
                    print('\033[95m' +"\nSun vector \n---------------"+ '\033[0m')
                    [print(["X = ","Y = ","Z = "][i]+str(Sun[0][i])) for i in range(0,3)]
                    print("actual")
                    Sun_D = [input(["X = ","Y = ","Z = "][i]) for i in range(0,3)]
                    try : 
                        Sun[0] = np.array((float(Sun_D[0]),float(Sun_D[1]),float(Sun_D[2])))/np.linalg.norm(np.array((float(Sun_D[0]),float(Sun_D[1]),float(Sun_D[2]))))*np.sign(np.array((float(Sun_D[0]),float(Sun_D[1]),float(Sun_D[2]))))
                    except :
                        print("bad value")
                    print('\033[95m' +"\nSun color \n---------------"+ '\033[0m')
                    print("actual")
                    [print(["R = ","G = ","B = "][i]+str(Sun[1][i])) for i in range(0,3)]
                    Sun_C = [input(["R = ","G = ","B = "][i]) for i in range(0,3)]
                    try : 
                        if np.all([0<= float(i) and float(i) <= 1  for i in Sun_C]) :
                            Sun[1] = np.array(([float(i) for i in Sun_C]))
                        else : 
                            print("bad value")
                    except :
                        print("bad value")
                    print('\033[95m' +"\nSun strong \n---------------"+ '\033[0m')
                    print("actual = "+ str(Sun[2]))
                    Sun_S = input("New = ")
                    try : 
                        if float(Sun_S) >= 0 :
                            Sun[2] = float(Sun_S)
                    except :
                        print("bad value")
                        
                if Commande == "p" :
                    print('\033[95m' +"\nFrom Paint uniforme\n---------------"+ '\033[0m')
                    print("actual")
                    [print(["R = ","G = ","B = "][i],paint_uniforme_color[i]) for i in range(0,3)]
                    new = [input(["R = ","G = ","B = "][i]) for i in range(0,3)]
                    try : 
                        if np.all([0<= float(i) and float(i) <= 1  for i in new]) :
                            paint_uniforme_color = np.array(([float(i) for i in new]))
                        else :
                            print("bad value")
                    except :
                        print("bad value")
                if Commande == "c" :
                    print('\033[95m' +"\nFrom Camera angle\n---------------"+ '\033[0m')
                    print("actual = "+ str(view_control.get_field_of_view()))
                    new_angle = input("step = ")
                    try :
                        view_control.change_field_of_view(step=float(new_angle))
                        vis.update_renderer()
                        vis.poll_events()
                    except :
                        print("bad value")
                if Commande == "b" :
                    print('\033[95m' +"\nShadow type\n---------------"+ '\033[0m')
                    print("actual = "+["vtm","vtm"](Shadow[0]))
                    Sha_T = input("new (True for PSF, False for VSM) = ")
                    try : 
                        Shadow = bool(Sha_T)
                    except :
                        print("bad value")
                    print('\033[95m' +"\nShadow opcaity\n---------------"+ '\033[0m')
                    print("actual = "+str(Shadow[1]))
                    Sha_O = input("new = ")
                    try : 
                        if float(Sha_O) >= 0 and float(Sha_O) <= 1 :
                            Shadow = float(Sha_O)
                        else :
                            print("bad value")
                    except :
                        print("bad value")
                    print('\033[95m' +"\nShadow color\n---------------"+ '\033[0m')
                    print("actual")
                    [print(["R = ","G = ","B = "][i],Shadow[2]) for i in range(0,3)]
                    Sha_C = [input(["R = ","G = ","B = "][i]) for i in range(0,3)]
                    try : 
                        if np.all([0<= float(i) and float(i) <= 1  for i in new]) :
                            Shadow[2] = np.array(([float(i) for i in Sha_C]))
                        else :
                            print("bad value")
                    except :
                        print("bad value")
                if Commande == "q" :
                    break
            vis.poll_events()
