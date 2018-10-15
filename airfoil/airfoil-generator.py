#!/usr/bin/python

"""
    airfoil-generator.py G-Code Generator
    Copyright (C) 2012-2017  Sammel Lothar

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
from Tkinter import *
import tkFileDialog
from time import sleep
from PIL import Image, ImageTk
import urllib

path = os.path.dirname(os.path.realpath(__file__))
g_code = []
profile_points_xy = 0
profile_points_uv = 0
xy_point_data=[]
uv_point_data=[]
uv_plane_activated = False
xy_y_at_1=""
xy_y_at_0=""
uv_y_at_1=""
uv_y_at_0=""

def programm_schliesen():
    root.destroy()
def file_save():
    global g_code_code
    file_save = tkFileDialog.asksaveasfilename(title="NC-g_code-DATA", \
    filetypes=[("LinuxCNC file",".ngc"),("NCFRS file",".nc"),("NC TAP",".tap"),\
    ("txt file",".txt"),("All files",".*")],initialfile="g_code",initialdir="/home/sammel/xyuv-foam/nc_files")
    fobj = open(file_save, "w") 
    # hier brauch ich die liste g_code_code
    global g_code
    for line in g_code: 
        fobj.write(line) 
    fobj.close()

def info():
    info_label_text.config(text='     GPL Sammel Lothar 2012          ' )
    info_label_text.update()    
    sleep(1)
    info_label_text.config(text='   Just Hit the profile entry in the list    ' )
    info_label_text.update()    
    sleep(1)
    info_label_text.config(text=' and SAVE via File Menu the G-code   ' )
    info_label_text.update()    
    
def get_profilenames():
    profilnames = []
    filetoload= path+'/airfoil_bilder.txt'
    f = open(filetoload, 'r')
    for line in f:
        profilnames.append(line)
    f.close()
    return profilnames

def get_data(profilename):
    xy_data=[]
    url_dat = "http://www.ae.illinois.edu/m-selig/ads/coord/"
    profilenametoload= path+'/data/'+str(profilename)+'.dat'	
    try:
        #f = open(url_dat+str(profilename)+'.dat', 'r')
        f = open(profilenametoload, 'r')
    except:
        etype, evalue, etb = sys.exc_info()
        evalue = etype("Cannot open file: %s" % evalue)
    else:
        for line in f:
            if ("0." in line) or ("1." in line):
                xy_data.append(line) 
        f.close()
        return xy_data


def sort_data(data_to_sort):
    local_data = data_to_sort
    length = len(local_data)
    sorted_data = []
    reverse_point = 0
    for a in range(0,length):
        sorted_data.append(local_data[a])
        if ("1.000000  0.000000" in local_data[a]) and ("0.000000  0.000000" in local_data[a+1]) :
            reverse_point = a
            break
    if reverse_point > 0:
        print "hier"
        for a in range(length-1,reverse_point,-1):
            sorted_data.append(local_data[a])
    
    return sorted_data

def draw_on_xy_canvas(data):
    global xy_point_data
    xy_point_data=data
    first = True
    x_add = 5
    Factor = 500.
    y_zero = 150
    g_code_scale= xy_profile_width.get()
    global g_code,xy_y_at_0,xy_y_at_1
    g_code =[]
    g_code.append("(Airfoil Gcode Generator V1.0 by Lothar Sammel Germany)\n")
    g_code.append("(profile XY %s )\n"%xy_profil_name.get())
    g_code.append("(test on 3 Axis Linuxcnc sim )\n")
    g_code.append("(AXIS,GRID,5) \n")
    g_code.append("G17.1 G21 G54 G90 G40 G80 G64 P0.05 \n")
    
    xy_profile_draw.delete(ALL)
    xy_profile_draw.create_text((120,15), text="XY PROFILE %s "% xy_profil_name.get() ,font=('courier', 12, 'bold'))
    calculation_canvas.delete("xy")
    for line in data:
        linesplit=line.split()
        if "1.0000" in linesplit[0]:
            xy_y_at_1 = line
        if "0.0000" in linesplit[0] :
            xy_y_at_0 = line
        x_coord =int(float(linesplit[0])*Factor)+x_add
        y_coord =int(float(linesplit[1])*Factor)+y_zero
        x_gcode =float(linesplit[0])*g_code_scale
        y_gcode =float(linesplit[1])*g_code_scale
        if not first:
            gcode_line= "G1 X%.3f Y%.3f \n"%(x_gcode,y_gcode)
        else:
            gcode_line= "G1 X%.3f Y%.3f F%.3d \n"%(x_gcode,y_gcode,feed.get())
        g_code.append(gcode_line)
        if not first:
            xy_profile_draw.create_line(x_old_coord,y_old_coord,x_coord,y_coord,
            fill="black")
            draw_on_calculation_canvas("xy",(x_old_coord-x_add)*2,(y_old_coord-y_zero)*2,(x_coord-x_add)*2,(y_coord-y_zero)*2)
        x_old_coord = x_coord
        y_old_coord = y_coord
        first=False
    g_code.append("M30 \n")

def draw_on_calculation_canvas(xyuv,x_old_coord,y_old_coord,x_coord,y_coord):
    if xyuv == "xy":
        calculation_canvas.create_line(x_old_coord,y_old_coord+200,x_coord,y_coord+200,
            fill="black",tags="xy") 
    else:
        calculation_canvas.create_line(x_old_coord,y_old_coord+200,x_coord,y_coord+200,
            fill="blue",tags="uv") 
        
def draw_on_uv_canvas(data):
    global uv_point_data,uv_plane_activated,uv_y_at_0,uv_y_at_1
    uv_point_data=data
    first = True
    x_add = 5
    Factor = 500.
    y_zero = 150
    g_code_scale= xy_profile_width.get()
    uv_profile_draw.delete(ALL)
    calculation_canvas.delete("uv")
    uv_profile_draw.create_text((120,15), text="UV PROFILE %s"% uv_profil_name.get() ,font=('courier', 12, 'bold'))
    if uv_plane_activated:
        for line in data:
            linesplit=line.split()
            if "1.0000" in linesplit[0]:
                uv_y_at_1 = line
            if "0.0000" in linesplit[0] :
                uv_y_at_0 = line
            x_coord =int(float(linesplit[0])*Factor)+x_add
            y_coord =int(float(linesplit[1])*Factor)+y_zero
            if not first:
                uv_profile_draw.create_line(x_old_coord,y_old_coord,
                x_coord,y_coord,fill="black")
                draw_on_calculation_canvas("uv",(x_old_coord-x_add)*2,
                (y_old_coord-y_zero)*2,(x_coord-x_add)*2,(y_coord-y_zero)*2)
            x_old_coord = x_coord
            y_old_coord = y_coord
            first=False
    else:
        uv_profile_draw.delete(ALL)
        uv_profile_draw.create_text((250,100), text="UV PROFILE",font=('courier', 40, 'bold'))
        
def xy_profil_listbox_action(event):
    xy_index = xy_profil_listbox.curselection()
    xy_profil_listbox.selection_set(int(xy_index[0]))
    xy_profil_listbox.see(int(xy_index[0]))
    xy_profil_name_show_entry.config(state=NORMAL)
    xy_profil_name.set(xy_profil_listbox.get(xy_index[0]))   
    xy_profil_name_show_entry.config(state=DISABLED)
    #set_xy_photo(xy_profil_listbox.get(xy_index[0]))
    xy_profile_data=get_data(xy_profil_listbox.get(xy_index[0]))
    xy_profile_data=sort_data(xy_profile_data)
    if xy_profile_data:
        global profile_points_xy,uv_plane_activated
        profile_points_xy = len(xy_profile_data)
        draw_on_xy_canvas(xy_profile_data)
        if uv_plane_activated:
            generate()
        else:
            gcode_show_text.config(state=NORMAL,font=('courier', 12, 'normal'))
            gcode_show_text.delete(1.0,END)
            for line in g_code:
                gcode_show_text.insert(END,line)
            gcode_show_text.config(state=DISABLED)
    
    
def uv_profil_listbox_action(event):
    uv_index = uv_profil_listbox.curselection()
    #uv_profil_listbox.selection_set(int(uv_index[0]))
    uv_profil_listbox.see(int(uv_index[0]))
    uv_profil_name_show_entry.config(state=NORMAL)
    uv_profil_name.set(uv_profil_listbox.get(uv_index[0]))   
    uv_profil_name_show_entry.config(state=DISABLED)
    #set_uv_photo(uv_profil_listbox.get(uv_index[0]))
    uv_profile_data=get_data(uv_profil_listbox.get(uv_index[0]))
    uv_profile_data=sort_data(uv_profile_data)
    if uv_profile_data:
        global profile_points_uv,profile_points_uv
        profile_points_uv = len(uv_profile_data)
        draw_on_uv_canvas(uv_profile_data)
    generate()

def add_uv_plane():
    global uv_plane_activated
    if uv_plane_activated:
        uv_plane_activated = False
        uv_profil_search.config(bg='black')
        uv_profil_listbox.config(bg="black",selectbackground="black")
        uv_profil_name_show_entry.config(disabledbackground="black")
        uv_profile_width_entry.config(bg="black")   
        uv_profile_offset_x_entry.config(bg="black")
        uv_profile_offset_y_entry.config(bg="black")
        button_add_uv_plane.config(text='Add UV Plane')
    else:
        uv_plane_activated = True
        uv_profil_search.config(bg='white')
        uv_profil_listbox.config(bg="white",selectbackground="lightgray")
        uv_profil_listbox.see(uv_index)
        uv_profil_name_show_entry.config(disabledbackground="white")
        uv_profile_width_entry.config(bg="white")   
        uv_profile_offset_x_entry.config(bg="white")
        uv_profile_offset_y_entry.config(bg="white")
        button_add_uv_plane.config(text='Remove UV Plane')
    uv_profil_listbox.select_set(first=1166, last=None)
    uv_profil_listbox_action(uv_index)

def new_profil_data(xy_uv,lstart,lstop,lstep,c_image):
    start=lstart
    stop=lstop
    step =lstep
    local_image = c_image
    new_profil_data_list=[]
    #upper Profile check
    if xy_uv == "xy":
        startline = xy_y_at_1
        mittelline = xy_y_at_0
    else :
        startline = uv_y_at_1
        mittelline = uv_y_at_0
    new_profil_data_list.append(startline)
    for x in range(start,stop-5,step):
        for y in range(5,200):
            #print x,y
            if local_image.getpixel((x,y))[0] == 0:
                xf=round(x/1000.,4)
                yf=round((200-y)/1000.,4)
                new_profil_data_list.append(("%.4f %.4f"%(xf,yf)))
                break
    #lower Profile check
    new_profil_data_list.append(mittelline)
    step =step * -1
    for x in range(stop,start+5,step):
        for y in range(395,200,-1):
            #print x,y
            if local_image.getpixel((x,y))[0] == 0:
                xf=round(x/1000.,4)
                yf=round((y-200)/1000.,4)* -1
                new_profil_data_list.append(("%.4f %.4f"%(xf,yf)))
                break
    new_profil_data_list.append(startline)
    return  new_profil_data_list

def generate():
    #g_code_scale_xy= xy_profile_width.get()
    global g_code,xy_point_data,uv_point_data
    if len(xy_point_data) != len(uv_point_data):
        calculation_canvas.pack()
        #calculation_canvas.pack_propagate(0)
        calculation_canvas.itemconfigure("uv", fill="white")
        calculation_canvas.itemconfigure("xy", fill="black")
        root.update()
        L, T, R, B = calculation_canvas.bbox(ALL)
        calculation_canvas.postscript(x=L,y=T,width=R,height=B,pageheight = B,
        pagewidth = R,colormode="mono",file="0_xy_calculate.eps")
        xy_image=Image.open("0_xy_calculate.eps")
        calculation_canvas.itemconfigure("xy", fill="white")
        calculation_canvas.itemconfigure("uv", fill="black")
        root.update()
        calculation_canvas.postscript(x=L,y=T,width=R,height=B,pageheight = B,
        pagewidth = R,colormode="mono",file="0_uv_calculate.eps")
        uv_image=Image.open("0_uv_calculate.eps")
        calculation_canvas.pack_forget()
        calculation_lable.config(height=1)
        root.update()
        xy_point_data = new_profil_data("xy",950,25,-25,xy_image)
        uv_point_data = new_profil_data("uv",950,25,-25,uv_image)
        if xy_profil_name.get() == uv_profil_name.get():
            if len(xy_point_data) > len(uv_point_data) :
                uv_point_data = xy_point_data
            else:
                xy_point_data = uv_point_data
        whats_the_different = len(xy_point_data)-len(uv_point_data)
        if (whats_the_different != 0):
            g_code =[]
            g_code.append("(Airfoil Gcode Generator V1.0 by Lothar Sammel Germany)\n")
            g_code.append("(profile XY %s  profile UV %s )\n"
            %(xy_profil_name.get(),uv_profil_name.get()))
            g_code.append("(!!!! Pointdifferens !!!!)\n")
            g_code.append("(PLEASE EDIT Point to Point Manually )\n")
            g_code.append("( TO keep the profile SHAPE)\n")
            g_code.append("(XY Points %d  UV points %d ,Difference %d )\n"
            %(len(xy_point_data),len(uv_point_data),whats_the_different))
            g_code.append("(test on xyuv FOAM or 9Axis Linuxcnc sim )\n")
            g_code.append("(AXIS,XY_Z_POS,5)\n")
            g_code.append("(AXIS,UV_Z_POS,30)\n")
            g_code.append("(AXIS,GRID,5) \n")
            g_code.append("G17 G21 G54 G90 G40 G80 G64 P0.05 \n")
            if len(xy_point_data) < len(uv_point_data):
                runto=len(xy_point_data)
                max_run= len(uv_point_data)
                larger_pointlist= "uv"
            else :
                runto=len(uv_point_data)
                max_run= len(xy_point_data)
                larger_pointlist= "xy"
            firstrun=True
            for a in range(0,runto):
                xy_linesplit = xy_point_data[a].split()
                uv_linesplit = uv_point_data[a].split()
                x_gcode =float(xy_linesplit[0])*xy_profile_width.get()
                y_gcode =float(xy_linesplit[1])*xy_profile_width.get()
                u_gcode =(float(uv_linesplit[0])*uv_profile_width.get())+uv_profile_offset_x.get()
                v_gcode =(float(uv_linesplit[1])*uv_profile_width.get())+uv_profile_offset_y.get()
                if not firstrun:
                    gcode_line= "G1 X%.3f Y%.3f U%.3f V%.3f \n"%(x_gcode,y_gcode,u_gcode,v_gcode)
                else:
                    gcode_line= "G1 X%.3f Y%.3f U%.3f V%.3f F%.3d \n"%(x_gcode,y_gcode,u_gcode,v_gcode,feed.get())
                g_code.append(gcode_line)
                firstrun=False
            for a in range(runto,max_run):
                if larger_pointlist == "xy":
                    linesplit = xy_point_data[a].split()
                    x_gcode =float(xy_linesplit[0])*xy_profile_width.get()
                    y_gcode =float(xy_linesplit[1])*xy_profile_width.get()
                    gcode_line= "G1 X%.3f Y%.3f \n"%(x_gcode,y_gcode)
                    g_code.append(gcode_line)
                else:
                    linesplit = uv_point_data[a].split()
                    u_gcode =(float(uv_linesplit[0])*uv_profile_width.get())+uv_profile_offset_x.get()
                    v_gcode =(float(uv_linesplit[1])*uv_profile_width.get())+uv_profile_offset_y.get()
                    gcode_line= "G1 U%.3f V%.3f \n"%(u_gcode,v_gcode)
                    g_code.append(gcode_line)
        g_code.append("M30 \n")

    if len(xy_point_data) == len(uv_point_data):
        g_code =[]
        g_code.append("(Airfoil Gcode Generator V1.0 by Lothar Sammel Germany)\n")
        g_code.append("(profile XY %s  profile UV %s )\n"
        %(xy_profil_name.get(),uv_profil_name.get()))
        g_code.append("(test on xyuv FOAM or 9Axis Linuxcnc sim )\n")
        g_code.append("(AXIS,XY_Z_POS,5)\n")
        g_code.append("(AXIS,UV_Z_POS,30)\n")
        g_code.append("(AXIS,GRID,5) \n")
        g_code.append("G17 G21 G54 G90 G40 G80 G64 P0.05 \n")
        firstrun=True
        for a in range(0,len(xy_point_data)):
            xy_linesplit = xy_point_data[a].split()
            uv_linesplit = uv_point_data[a].split()
            x_gcode =float(xy_linesplit[0])*xy_profile_width.get()
            y_gcode =float(xy_linesplit[1])*xy_profile_width.get()
            u_gcode =(float(uv_linesplit[0])*uv_profile_width.get())+uv_profile_offset_x.get()
            v_gcode =(float(uv_linesplit[1])*uv_profile_width.get())+uv_profile_offset_y.get()
            if not firstrun:
                gcode_line= "G1 X%.3f Y%.3f U%.3f V%.3f \n"%(x_gcode,y_gcode,u_gcode,v_gcode)
            else:
                gcode_line= "G1 X%.3f Y%.3f U%.3f V%.3f F%.3d \n"%(x_gcode,y_gcode,u_gcode,v_gcode,feed.get())
            firstrun=False
            g_code.append(gcode_line)
        g_code.append("M30 \n")
    gcode_show_text.config(state=NORMAL,font=('courier', 12, 'normal'))
    gcode_show_text.delete(1.0,END)
    for line in g_code:
        gcode_show_text.insert(END,line)
    gcode_show_text.config(state=DISABLED)

def update_xy_profile_list():
    search = xy_profil_search.get()

    airfoils = get_profilenames()
    xy_profil_listbox.delete(0, END)
    for item in airfoils:
        p=item.split('.')
        if search.lower() in item.lower():
            xy_profil_listbox.insert(END, p[0])

def update_uv_profile_list():
    search = uv_profil_search.get()

    airfoils = get_profilenames()
    uv_profil_listbox.delete(0, END)
    for item in airfoils:
        p=item.split('.')
        if search.lower() in item.lower():
            uv_profil_listbox.insert(END, p[0])

root = Tk()
root.geometry("1080x1000")
# create a menu
menu = Menu(root)
root.config(menu=menu)
root.title('Airfoil XYUV G-code Generator Tool By Sammel Lothar Germany')
#root.tk.call('package', 'require', 'Img')
filemenu = Menu(menu)
menu.add_cascade(label="FILE", menu=filemenu)
#filemenu.add_command(label="Open", command=file_open)
filemenu.add_command(label="Save", command=file_save)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=programm_schliesen)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Info", command=info)

top_text = Label(root, bg="red", height=20)
top_text.pack(fill=X)
uv_lable = Label(root, bg="red")
uv_lable.pack(fill=BOTH)
draw_lable = Label(root)
draw_lable.pack(fill=X)
calculation_lable = Label(root)
calculation_lable.pack(fill=X)

# ****
#  XY Profile
# ****

xy_profile_label_text = Label(top_text,text='XY Profile',bg='black',fg='white')
xy_profile_label_text.pack(side=LEFT,ipadx=5,ipady=5,padx=5,pady=10)
xy_profil_name = StringVar()
xy_profil_name.set("naca0015")
xy_profil_name_show_entry = Entry(top_text,textvariable=xy_profil_name,
    disabledbackground="white",disabledforeground="black",
    justify=CENTER,state=DISABLED,width=15)
xy_profil_name_show_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

xy_profil_frame = Frame(top_text)
xy_profil_frame.pack(side=LEFT,fill=Y)
xy_profil_search_var = StringVar()
xy_profil_search_var.trace("w", lambda name, index, mode: update_xy_profile_list())
xy_profil_search = Entry(xy_profil_frame, textvariable=xy_profil_search_var, width=15)
xy_profil_search.pack(side=TOP, fill=X)
xy_profil_scrollbar = Scrollbar(xy_profil_frame, orient=VERTICAL)
xy_profil_listbox = Listbox(xy_profil_frame, selectmode=SINGLE, yscrollcommand=xy_profil_scrollbar.set, width=15,height=2)
xy_profil_scrollbar.config(command=xy_profil_listbox.yview)
xy_profil_scrollbar.pack(side=RIGHT, fill=Y)
xy_profil_listbox.pack(side=LEFT, fill=BOTH, ipadx=3,ipady=5,padx=1,pady=10)
profilenames= get_profilenames()
xy_index,index = 0,0
for item in profilenames:
    p=item.split('.')
    xy_profil_listbox.insert(END, p[0])
    if "naca0015" in item:
        xy_index=index
    index=index+1
xy_profil_listbox.see(xy_index)
xy_profil_listbox.select_set(first=1166, last=None)
xy_profil_listbox.bind("<Double-Button-1>", xy_profil_listbox_action)

text_xy_profile_width = Label(top_text,text='XY Profile Width',bg='red',fg='black')
text_xy_profile_width.pack(side=LEFT,ipadx=1,ipady=5,padx=1,pady=10)

xy_profile_width = IntVar()
xy_profile_width.set(200)
xy_profile_width_entry = Entry(top_text,textvariable=xy_profile_width,width=6)
xy_profile_width_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

button_add_uv_plane = Button(top_text, text="Add UV Plane", command=add_uv_plane)
button_add_uv_plane.pack(side=LEFT,ipadx=5,ipady=5,padx=5,pady=10)

feed = IntVar()
feed.set(200)

text = Label(top_text,text='Feed',bg='red',fg='black')
text.pack(side=LEFT,ipadx=5,ipady=5,padx=5,pady=10)
e_feed_xy = Entry(top_text,textvariable=feed,width=4)
e_feed_xy.pack(side=LEFT,ipadx=1,ipady=5,padx=1,pady=10)

# ****
#  UV Profile
# ****
uv_profile_label_text = Label(uv_lable,text='UV Profile',bg='black',fg='white')
uv_profile_label_text.pack(side=LEFT,ipadx=5,ipady=5,padx=5,pady=10)
uv_profil_name = StringVar()
uv_profil_name.set("naca0015")
uv_profil_name_show_entry = Entry(uv_lable,textvariable=uv_profil_name,
    disabledbackground="black",disabledforeground="black",
    justify=CENTER,state=DISABLED,width=15)
uv_profil_name_show_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

uv_profil_frame = Frame(uv_lable)
uv_profil_frame.pack(side=LEFT,fill=Y)
uv_profil_search_var = StringVar()
uv_profil_search_var.trace("w", lambda name, index, mode: update_uv_profile_list())
uv_profil_search = Entry(uv_profil_frame, textvariable=uv_profil_search_var, bg='black', width=15)
uv_profil_search.pack(side=TOP, fill=X)
uv_profil_scrollbar = Scrollbar(uv_profil_frame, orient=VERTICAL)
uv_profil_listbox = Listbox(uv_profil_frame,selectmode=SINGLE,yscrollcommand=uv_profil_scrollbar.set,bg="black",width=15,height=2)
uv_profil_scrollbar.config(command=uv_profil_listbox.yview)
uv_profil_scrollbar.pack(side=RIGHT, fill=Y)
uv_profil_listbox.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)
profilenames = get_profilenames()
uv_index,index = 0,0
for item in profilenames:
    p=item.split('.')
    uv_profil_listbox.insert(END, p[0])
    if "naca0015" in item:
        uv_index=index
    index=index+1
uv_profil_listbox.selection_set(uv_index)
uv_profil_listbox.see(uv_index+5)
uv_profil_listbox.bind("<Double-Button-1>", uv_profil_listbox_action)

text_uv_profile_width = Label(uv_lable,text='UV Profile Width',bg='red',fg='black')
text_uv_profile_width.pack(side=LEFT,ipadx=1,ipady=5,padx=1,pady=10)

uv_profile_width = IntVar()
uv_profile_width.set(100)
uv_profile_width_entry = Entry(uv_lable,textvariable=uv_profile_width,bg="black",width=6)
uv_profile_width_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

text_uv_profile_offset_x = Label(uv_lable,text='UV-Offset X',bg='red',fg='black')
text_uv_profile_offset_x.pack(side=LEFT,ipadx=1,ipady=5,padx=1,pady=10)
uv_profile_offset_x = IntVar()
uv_profile_offset_x.set(0)
uv_profile_offset_x_entry = Entry(uv_lable,textvariable=uv_profile_offset_x,bg="black",width=6)
uv_profile_offset_x_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

text_uv_profile_offset_y = Label(uv_lable,text='UV-Offset Y',bg='red',fg='black')
text_uv_profile_offset_y.pack(side=LEFT,ipadx=1,ipady=5,padx=1,pady=10)
uv_profile_offset_y = IntVar()
uv_profile_offset_y.set(0)
uv_profile_offset_y_entry = Entry(uv_lable,textvariable=uv_profile_offset_y,bg="black",width=6)
uv_profile_offset_y_entry.pack(side=LEFT,ipadx=3,ipady=5,padx=1,pady=10)

button_gcode = Button(top_text, text="Generate G-Code", command=generate)
button_gcode.pack(side=LEFT,ipadx=5,ipady=5,padx=5,pady=10)

xy_profile_draw = Canvas(draw_lable, width=510, height=300)
xy_profile_draw.pack(side=LEFT)

uv_profile_draw = Canvas(draw_lable, width=510, height=300)
uv_profile_draw.pack()
uv_profile_draw.create_text((250,100), text="UV PROFILE",font=('courier', 40, 'bold'))

calculation_canvas = Canvas(calculation_lable, width=1000, height=400,state=NORMAL,bg="white")
calculation_canvas.pack()
calculation_canvas.pack_forget()
calculation_canvas.create_rectangle((0,0,1000,400),fill="white")

gcode_show_text = Text(root,state=DISABLED,bg='lightblue',fg='black',width=60)
gcode_show_text.pack()

#preload some profile
xy_profil_listbox.select_set(first=1166, last=None)
xy_profil_listbox_action(xy_index)

mainloop()
