#!/usr/bin/python

"""
    Grid.py G-Code Generator
    Version 1.0
    For grids on Rectangle 
    Copyright (C) <2010>  <Sammel Lothar > <Lothar at Sammellothar dot de>
    based on work by 
    <Lawrence Glaister> <ve7it at shaw dot ca>
    <John Thornton>  -- thanks John!

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

    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add
    the command python YourPathToThisFile/grid_generator.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at: 
    https://github.com/linuxcnc/simple-gcode-generators

    Version 1.0 

"""

from Tkinter import *
from math import *
import os


IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.DoIt()


    def createWidgets(self):
        self.CanvasDrawings = []
        self.gcode = []
        self.PreviewFrame = Frame(self,bd=3)
        self.PreviewFrame.grid(row=0, column=0)
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=300, height=300, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.XLine = self.PreviewCanvas.create_line(15,150,285,150, fill = 'green')
        self.YLine = self.PreviewCanvas.create_line(150,15,150,285, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.rownumber = 0
        self.st00 = Label(self.EntryFrame, text='Griding an Array')
        self.st00.grid(row=self.rownumber, column=0, columnspan=2)
 
        self.rownumber += 1

        self.st000 = Label(self.EntryFrame, text='Shape')
        self.st000.grid(row=self.rownumber,column=0,sticky=N)
        self.Shape = StringVar()
        self.Shape.set("Rectangular")
        Radiobutton(self.EntryFrame, text='Circle', variable=self.Shape, value = "Circel", command=self.DoIt,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=0, sticky = N)
        Radiobutton(self.EntryFrame, text=' Rect ', variable=self.Shape, value = "Rectangular", command=self.DoIt,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=0,sticky=N)
        self.stMove = Label(self.EntryFrame, text='Outline',width=7)
        self.stMove.grid(row=self.rownumber, column=1,sticky=W,padx=2)
        self.OutlineVar = StringVar()
        self.OutlineVar.set("yes")
        Radiobutton(self.EntryFrame, text='YES', variable=self.OutlineVar, value = "yes", command=self.DoIt ,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=1, sticky = W,padx=6)
        Radiobutton(self.EntryFrame, text='No', variable=self.OutlineVar, value = "no", command=self.DoIt ,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=1, sticky = W,padx=6)

        self.stspace = Label(self.EntryFrame, text='Grid Style',width=10)
        self.stspace.grid(row=self.rownumber, column=1,sticky=N,padx=45)
        self.grid_style = StringVar()
        self.grid_style.set("symetric")
        Radiobutton(self.EntryFrame, text='  Symetric', variable=self.grid_style, value = "symetric", command=self.DoIt ,indicatoron=0,width=10,).grid(row=self.rownumber+1, column=1, sticky = N,padx=35)
        Radiobutton(self.EntryFrame, text='Line Count', variable=self.grid_style, value = "count", command=self.DoIt ,indicatoron=0,width=10,).grid(row=self.rownumber+2, column=1, sticky = N,padx=15)
              

        self.st13 = Label(self.EntryFrame, text='Units',width=5)
        self.st13.grid(row=self.rownumber, column=0,sticky=W)
        self.UnitVar = IntVar()
        self.UnitVar.set(1)
        Radiobutton(self.EntryFrame, text='Inch', variable=self.UnitVar, value = 0, command=self.Change_Units ,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=0,sticky=W)
        Radiobutton(self.EntryFrame, text=' MM ', variable=self.UnitVar, value = 1, command=self.Change_Units ,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=0,sticky=W)

        self.cross_label = Label(self.EntryFrame, text='Cross',width=5)
        self.cross_label.grid(row=self.rownumber, column=0,sticky=E)
        self.Cross = StringVar()
        self.Cross.set("no")
        Radiobutton(self.EntryFrame, text='NO', variable=self.Cross, value = "no", command=self.DoIt ,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=0,sticky=E)
        Radiobutton(self.EntryFrame, text='YES', variable=self.Cross, value = "yes", command=self.DoIt ,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=0,sticky=E)
        self.grid_onVar=StringVar()
        self.grid_onVar.set("yes")
        self.label_grid_on = Label(self.EntryFrame, text='Grid ON',width=7)
        self.label_grid_on.grid(row=self.rownumber+1, column=1,sticky=W,padx=60)
        Checkbutton(self.EntryFrame, text="", variable=self.grid_onVar, onvalue = "yes",offvalue="no", command=self.DoIt ).grid(row=self.rownumber+2, column=1,sticky=W,padx=70)

        self.label_parallel = Label(self.EntryFrame, text='Parallel Outline',width=11)
        self.label_parallel.grid(row=self.rownumber, column=1,sticky=E)
        self.grid_parallelVar = StringVar()
        self.grid_parallelVar.set("no")
        Radiobutton(self.EntryFrame, text='YES', variable=self.grid_parallelVar, value = "yes", command=self.DoIt ,indicatoron=0,width=4,).grid(row=self.rownumber+1, column=1, sticky = E,padx=15)
        Radiobutton(self.EntryFrame, text='No', variable=self.grid_parallelVar, value = "no", command=self.DoIt ,indicatoron=0,width=4,).grid(row=self.rownumber+2, column=1, sticky = E,padx=15)


        self.rownumber += 3

        self.st01 = Label(self.EntryFrame, text='Preamble')
        self.st01.grid(row=self.rownumber, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G21 G90 G64 P0.01 M3 S3000 M7')
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=35)
        self.Preamble.grid(row=self.rownumber, column=1)
        self.NormalColor =  self.Preamble.cget('bg')

        self.rownumber += 1
        self.st02 = Label(self.EntryFrame, text='X Center ')
        self.st02.grid(row=self.rownumber, column=0)
        self.XPocketCenterVar = StringVar()
        self.XPocketCenterVar.set('20.0')
        self.XPocketCenter = Entry(self.EntryFrame, textvariable=self.XPocketCenterVar ,width=10)
        self.XPocketCenter.grid(row=self.rownumber, column=1,sticky=W)
        self.rownumber += 1
        self.st03 = Label(self.EntryFrame, text='Y Center ')
        self.st03.grid(row=self.rownumber, column=0)
        self.YPocketCenterVar = StringVar()
        self.YPocketCenterVar.set('15.0')
        self.YPocketCenter = Entry(self.EntryFrame, textvariable=self.YPocketCenterVar ,width=10)
        self.YPocketCenter.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber += 1
        self.st04 = Label(self.EntryFrame, text='Dimension (X/D,Y)',width=15)
        self.st04.grid(row=self.rownumber, column=0,sticky=N,padx=6)
        self.PocketXVar = StringVar()
        self.PocketXVar.set('40.0')
        self.PocketX = Entry(self.EntryFrame, textvariable=self.PocketXVar ,width=15)
        self.PocketX.grid(row=self.rownumber, column=1, sticky = W)
        self.PocketYVar = StringVar()
        self.PocketYVar.set('30.0')   
        self.PocketY = Entry(self.EntryFrame, textvariable=self.PocketYVar ,width=15)
        self.PocketY.grid(row=self.rownumber, column=1, sticky = E)

        self.rownumber += 1

        self.labellinecount = Label(self.EntryFrame, text='X,Y Line Count')
        self.labellinecount.grid(row=self.rownumber,column=0,sticky=N)
        self.grid_lines_X_var = StringVar()
        self.grid_lines_X_var.set('5')
        self.grid_lines_X = Entry(self.EntryFrame, textvariable=self.grid_lines_X_var ,width=5)
        self.grid_lines_X.grid(row=self.rownumber, column=1,sticky=W)
        self.grid_lines_Y_var = StringVar()
        self.grid_lines_Y_var.set('5')
        self.grid_lines_Y = Entry(self.EntryFrame, textvariable=self.grid_lines_Y_var ,width=5)
        self.grid_lines_Y.grid(row=self.rownumber, column=1,sticky=W,padx=50)

        self.rownumber +=1
        self.labellinecount2 = Label(self.EntryFrame, text='Symetric/Space')
        self.labellinecount2.grid(row=self.rownumber,column=0,sticky=N)
        self.StepoverVar = StringVar()
        self.StepoverVar.set('5.0')
        self.Stepover = Entry(self.EntryFrame, textvariable=self.StepoverVar ,width=5)
        self.Stepover.grid(row=self.rownumber, column=1,sticky=W)
        Label(self.EntryFrame, text=' Stepover/Unit').grid(row=self.rownumber, column=1,sticky=W,padx=35)

        self.rownumber +=1
        self.grid_border=IntVar()
        self.grid_border.set(1)
        Checkbutton(self.EntryFrame, text='Grid Border +/-', variable=self.grid_border, onvalue = 1,offvalue=0, command=self.DoIt ).grid(row=self.rownumber, column=0,sticky=W)
        self.borderVar = StringVar()
        self.borderVar.set('2.0')
        self.border = Entry(self.EntryFrame, textvariable=self.borderVar ,width=5)
        self.border.grid(row=self.rownumber, column=1,sticky=W)
        #cross
        self.cross_offset_label = Label(self.EntryFrame, text='Cross Overlab +/-')
        self.cross_offset_label.grid(row=self.rownumber, column=1,sticky=E,padx=55)
        self.cross_offset = StringVar()
        self.cross_offset.set('2.0')
        self.cross_offset_entry = Entry(self.EntryFrame, textvariable=self.cross_offset ,width=5)
        self.cross_offset_entry.grid(row=self.rownumber, column=1,sticky=E)

        #spidergrid
        self.rownumber +=1
        self.spider_grid=StringVar()
        self.spider_grid.set("no")
        Checkbutton(self.EntryFrame, text='Spider Grid', variable=self.spider_grid, onvalue = "yes",offvalue="no", command=self.DoIt ).grid(row=self.rownumber, column=0,sticky=W)
        self.spider_lines_entry_label = Label(self.EntryFrame, text='Lines').grid(row=self.rownumber, column=0,sticky=E,padx=1)
        self.spider_lines = StringVar()
        self.spider_lines.set('4')
        self.spider_lines_entry = Entry(self.EntryFrame, textvariable=self.spider_lines ,width=3)
        self.spider_lines_entry.grid(row=self.rownumber, column=1,sticky=W,padx=2)
        self.spider_startangel_entry_label = Label(self.EntryFrame, text='StartAngel').grid(row=self.rownumber, column=1,sticky=E,padx=35)
        self.spider_startangel = StringVar()
        self.spider_startangel.set('45')
        self.spider_startangel_entry = Entry(self.EntryFrame, textvariable=self.spider_startangel ,width=3)
        self.spider_startangel_entry.grid(row=self.rownumber, column=1,sticky=E,padx=4)
        self.spider_offset_entry_label = Label(self.EntryFrame, text='SpiderOffset+/-').grid(row=self.rownumber, column=1,sticky=W,padx=35)
        self.spider_offset = StringVar()
        self.spider_offset.set('2.0')
        self.spider_offset_entry = Entry(self.EntryFrame, textvariable=self.spider_offset ,width=5)
        self.spider_offset_entry.grid(row=self.rownumber, column=1,sticky=E,padx=105)

        self.rownumber +=1
        self.st06 = Label(self.EntryFrame, text='Final Depth')
        self.st06.grid(row=self.rownumber, column=0)
        self.FinalDepth = StringVar()
        self.FinalDepth.set('-1.0')
        self.HoleDepth = Entry(self.EntryFrame, textvariable=self.FinalDepth ,width=8)
        self.HoleDepth.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber +=1
        self.st08 = Label(self.EntryFrame, text='Safe Z')
        self.st08.grid(row=self.rownumber, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('3')
        self.SafeZ = Entry(self.EntryFrame, width=8, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=self.rownumber, column=1,sticky=W)

        self.st08a = Label(self.EntryFrame, text='Rapid Z down')
        self.st08a.grid(row=self.rownumber, column=1,sticky=N)
        self.RapidZVar = StringVar()
        self.RapidZVar.set('1')
        self.RapidZ = Entry(self.EntryFrame, width=8, textvariable = self.RapidZVar)
        self.RapidZ.grid(row=self.rownumber, column=1,sticky=E)

        self.rownumber +=1 
        self.st09 = Label(self.EntryFrame, text='Feedspeed XY')
        self.st09.grid(row=self.rownumber, column=0)
        self.FeedspeedVar = StringVar()
        self.FeedspeedVar.set('450.0')
        self.Feedspeed = Entry(self.EntryFrame, textvariable=self.FeedspeedVar ,width=8)
        self.Feedspeed.grid(row=self.rownumber, column=1,sticky=W)

        self.st09a = Label(self.EntryFrame, text='Feedspeed Z')
        self.st09a.grid(row=self.rownumber, column=1,sticky=N)
        self.FeedspeedZVar = StringVar()
        self.FeedspeedZVar.set('200.0')
        self.FeedspeedZ = Entry(self.EntryFrame, textvariable=self.FeedspeedZVar ,width=8)
        self.FeedspeedZ.grid(row=self.rownumber, column=1,sticky=E)

        self.rownumber += 1
        self.st11 = Label(self.EntryFrame, text='Postamble')
        self.st11.grid(row=self.rownumber, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=35)
        self.Postamble.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber += 1

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=self.rownumber, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=self.rownumber, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

    def Change_Units(self):
        if (self.UnitVar.get() == 0) :
            #Inch 
            self.PreambleVar.set('G17 G20 G90 G64 P0.001 M3 S3000 M7')
        else :
            #MM
            self.PreambleVar.set('G17 G21 G90 G64 P0.01 M3 S3000 M7')
        
    def DoIt(self):

        # range check inputs for matchor errors
        self.PocketX.configure( bg = self.NormalColor )
        if (float(self.PocketX.get()) <= 0.0 ):
            self.PocketX.configure( bg = 'red')
            return
        self.PocketY.configure( bg = self.NormalColor )
        if (float(self.PocketY.get()) <= 0.0 ):
            self.PocketY.configure( bg = 'red')
            return
        self.Stepover.configure( bg = self.NormalColor )
        if (float(self.Stepover.get()) <= 0.0 ):
            self.Stepover.configure( bg = 'red')
            return
        self.SafeZ.configure( bg = self.NormalColor )

        self.Feedspeed.configure( bg = self.NormalColor )
        if float(self.Feedspeed.get()) <= 0.0:
            self.Feedspeed.configure( bg = 'red' )
            return
        if self.grid_border.get() == 1:
            self.border.configure(state=NORMAL)
        else:
            self.border.configure(state=DISABLED)
        if self.Cross.get() == "yes":
            self.cross_offset_entry.configure(state=NORMAL)
        else:
            self.cross_offset_entry.configure(state=DISABLED)
            
        if self.grid_style.get()=="symetric":
            self.grid_lines_X.configure(state=DISABLED)
            self.grid_lines_Y.configure(state=DISABLED)
            self.Stepover.configure(state=NORMAL)
        else:
            self.grid_lines_X.configure(state=NORMAL)
            self.grid_lines_Y.configure(state=NORMAL)
            self.Stepover.configure(state=DISABLED)
        if self.spider_grid.get()=="yes":
            self.spider_lines_entry.configure(state=NORMAL)
            self.spider_startangel_entry.configure(state=NORMAL)
            self.spider_offset_entry.configure(state=NORMAL)
        else:
            self.spider_lines_entry.configure(state=DISABLED)
            self.spider_startangel_entry.configure(state=DISABLED)
            self.spider_offset_entry.configure(state=DISABLED)
            
        # erase old display objects as needed
        for draw in self.CanvasDrawings:
            self.PreviewCanvas.delete(draw)
        self.CanvasDrawings = []

        # erase old gcode as needed
        self.gcode = []
        self.gcode.append('( Code generated by Grid.py widget )')
        self.gcode.append('( by Sammel Lothar - 2010 )')
        self.gcode.append(self.PreambleVar.get()) # lead in
        self.gcode.append( 'G0 Z%.3f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
        self.gcode.append( 'G0 X%.3f Y%.3f ' %(float(self.XPocketCenterVar.get()),float(self.YPocketCenterVar.get())))#G0 CenterZsafe
        #get the inputs
        Spacing  = float(self.StepoverVar.get()) #spacing 
        centerx=float(self.XPocketCenter.get())
        centery=float(self.YPocketCenter.get())
        pocket_length_x=float(self.PocketX.get())
        pocket_length_y=float(self.PocketY.get())   
        pocket_diameter=pocket_length_x
        pocket_rad=pocket_diameter/2.0
        cross_offset=float(self.cross_offset_entry.get())
        border=float(self.border.get())
        
        #GRAFIK for screen
        if self.Shape.get() == "Circel":      # circel
            Scale = float(self.PocketXVar.get()) * 1.2 / 300.0
            canvCircRad = float(self.PocketXVar.get())/2.0
            self.PocketY.configure(state=DISABLED)
            self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
                150-canvCircRad/Scale,
                150-canvCircRad/Scale,
                150+canvCircRad/Scale,
                150+canvCircRad/Scale, outline='Black'))
 
            self.gcode.append('( %.3f circular gridPocket at %.3f,%.3f )'
                %(float(self.PocketXVar.get()),
                  float(self.XPocketCenterVar.get()),
                  float(self.YPocketCenterVar.get()) ))
            #circel outline
            if self.OutlineVar.get() == "yes":
                self.gcode.append('(Outline circel)')
                self.gcode.append('G0 X%.3f' %(centerx-(pocket_length_x/2.0)))
                self.Go_down()
                self.gcode.append('G03 I%.3f F%.2f' %((float(self.PocketXVar.get())/2.0) ,float(self.FeedspeedVar.get())))
                self.Go_up()
                self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
                    149-canvCircRad/Scale,
                    149-canvCircRad/Scale,
                    151+canvCircRad/Scale,
                    151+canvCircRad/Scale, outline='red'))
            if self.Cross.get() == "yes":
                newx=((float(self.PocketXVar.get())/2.0)+float(self.cross_offset_entry.get()))/Scale
                self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150-newx,150,150+newx,fill="red"))
                self.CanvasDrawings.append(self.PreviewCanvas.create_line(150-newx,150,150+newx,150,fill="red"))
                self.gcode.append('(Cross)')
                self.gcode.append('G0 X%.3f Y%.3f' %(centerx,(centery-pocket_rad-cross_offset)))
                self.Go_down()
                self.gcode.append('G1 Y%.3f F%.2f' %((centery+pocket_rad+cross_offset),float(self.FeedspeedVar.get())))
                self.Go_up()
                self.gcode.append('G0 X%.3f Y%.3f' %(centerx-pocket_rad-cross_offset,centery))
                self.Go_down()
                self.gcode.append('G1 X%.3f F%.2f' %((centerx+pocket_rad+cross_offset),float(self.FeedspeedVar.get())))
                self.Go_up()
            # circel grid 
            if self.grid_onVar.get()=="yes":
                if self.grid_style.get()=="symetric": #circle grid symetric
                    lines=int(pocket_diameter/Spacing) 
                    versatz=float(pocket_diameter/(lines+1))/Scale
                else:#grid line count
                    lines_x=int(self.grid_lines_X.get())
                    lines_y=int(self.grid_lines_Y.get())
                    lines=lines_x
                    versatz=float(pocket_diameter/(lines+1))/Scale
                    versatz_y=float(pocket_diameter/(lines_y+1))/Scale
                new_y_list=[]
                for line in xrange(1,lines+1):
                    newx=line*versatz+(150-pocket_rad/Scale)
                    if line <= ((lines+1)/2):
                        b= line*versatz
                        sr=b*(2*(pocket_rad/Scale)-b)
                        newy=sqrt(sr)
                        new_y_list.append(newy)
                    else:
                        newy=new_y_list[lines-line]
                    if self.grid_border.get()== 1:
                        newy=newy-(border/Scale)
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(newx,150-newy,newx,150+newy,fill='red'))
                    if self.grid_style.get()=="symetric":
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(150-newy,newx,150+newy,newx,fill='red'))
                        gcode_y=line*float(pocket_diameter/(lines+1))+centery-pocket_rad
                        self.gcode.append('G0 X%.3f Y%.3f' %(centerx-(newy*Scale),gcode_y))
                        self.Go_down()
                        self.gcode.append('G1 X%.3f F%.2f' %(centerx+(newy*Scale),float(self.FeedspeedVar.get())))
                        self.Go_up()
                    #gcode
                    gcode_x=line*float(pocket_diameter/(lines+1))+centerx-pocket_rad
                    self.gcode.append('G0 X%.3f Y%.3f' %(gcode_x,centery-(newy*Scale)))
                    self.Go_down()
                    self.gcode.append('G1 Y%.3f F%.2f' %(centery+(newy*Scale),float(self.FeedspeedVar.get())))
                    self.Go_up()
                if self.grid_style.get() == "count":
                    new_y_list=[]
                    lines=lines_y
                    versatz=versatz_y
                    self.gcode.append('(circel Grid Count Y lines)')
                    for line in xrange(1,lines+1):
                        newx=line*versatz+(150-pocket_rad/Scale)
                        if line <= ((lines+1)/2):
                            b= line*versatz
                            sr=b*(2*(pocket_rad/Scale)-b)
                            newy=sqrt(sr)
                            new_y_list.append(newy)
                        else:
                            newy=new_y_list[lines-line]
                        if self.grid_border.get()== 1:
                            newy=newy-(border/Scale)
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(150-newy,newx,150+newy,newx,fill='red'))
                        gcode_y=line*float(pocket_diameter/(lines+1))+centery-pocket_rad
                        self.gcode.append('G0 X%.3f Y%.3f' %(centerx-(newy*Scale),gcode_y))
                        self.Go_down()
                        self.gcode.append('G1 X%.3f F%.2f' %(centerx+(newy*Scale),float(self.FeedspeedVar.get())))
                        self.Go_up()
                    
                    
            #circel parallel TARGETShape
            if self.grid_parallelVar.get()=="yes":
                circels=int(pocket_rad/Spacing)
                space_x=float(pocket_rad/circels)
                for circle in xrange(1,circels):
                    self.gcode.append('G0 X%.3f Y%.3f' %(centerx-(circle*space_x),centery))
                    self.Go_down()
                    self.gcode.append('G03 I%.3f F%.2f' %((circle*space_x) ,float(self.FeedspeedVar.get())))
                    self.Go_up()
                    self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
                        150-(circle*space_x)/Scale,
                        150-(circle*space_x)/Scale,
                        150+(circle*space_x)/Scale,
                        150+(circle*space_x)/Scale, outline='red'))
            # circle spider
            if self.spider_grid.get()=="yes":
                start_angel=float(self.spider_startangel_entry.get())
                angel_lines=int(self.spider_lines_entry.get())
                spider_offset=float(self.spider_offset_entry.get())
                angel_space=360/angel_lines
                if start_angel < 0 or start_angel > 360:
                    start_angel = 0
                angel_space=360/angel_lines
                for line in range(angel_lines):
                    newx=sin(radians((line*angel_space)+start_angel))*(pocket_rad+spider_offset)
                    newy=cos(radians((line*angel_space)+start_angel))*(pocket_rad+spider_offset)
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150-newx/Scale,150-newy/Scale,fill="red"))
                    self.gcode.append('G0 X%.3f Y%.3f' %(centerx,centery))
                    self.Go_down()
                    self.gcode.append('G1 X%.3f Y%.3f F%.2f' %(centerx-newx,centery-newy,float(self.FeedspeedVar.get())))
                    self.Go_up()                      
        # --------------
        # RECTANGULAR
        # --------------              
        if self.Shape.get() == "Rectangular":      # rectangle
            self.PocketY.configure(state=NORMAL)
            # temps used for rectangular Pockets
            self.gcode.append('( %.3fx%.3f rectangular gridPocket at %.3f,%.3f )'
                %(float(self.PocketXVar.get()),
                  float(self.PocketYVar.get()),
                  float(self.XPocketCenterVar.get()),
                  float(self.YPocketCenterVar.get()) ))
            #view entry dimention Y
            self.PocketY.configure(state=NORMAL)
            # calculate canvas scale
            a = float(self.PocketXVar.get())/2.0
            b = float(self.PocketYVar.get())/2.0
            if a > b:
                Scale = float(self.PocketXVar.get()) * 1.2 / 300.0
            else:
                Scale = float(self.PocketYVar.get()) * 1.2 / 300.0
            #draw outer rect
            self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                150-a/Scale,
                150-b/Scale,
                150+a/Scale,
                150+b/Scale, outline='Black'))
            # Dimention rectangel
            if self.OutlineVar.get() == "yes":
                self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                    151-a/Scale,
                    151-b/Scale,
                    149+a/Scale,
                    149+b/Scale, outline='red'))
                self.gcode.append('(Outline)')
                self.gcode.append('G0 X%.3f Y%.3f' %(float(self.XPocketCenterVar.get())-(float(self.PocketXVar.get())/2.0),(float(self.YPocketCenterVar.get())-(float(self.PocketYVar.get())/2.0) )))
                self.gcode.append('G1 Z%.3f F%.2f' %(float(self.FinalDepth.get()) ,float(self.FeedspeedZVar.get())))
                self.gcode.append('G1 X%.3f F%.2f' %(float(self.XPocketCenterVar.get())+(float(self.PocketXVar.get())/2.0) ,float(self.FeedspeedVar.get())))
                self.gcode.append('G1 Y%.3f' %(float(self.YPocketCenterVar.get())+(float(self.PocketYVar.get())/2.0) ))
                self.gcode.append('G1 X%.3f' %(float(self.XPocketCenterVar.get())-(float(self.PocketXVar.get())/2.0) ))
                self.gcode.append('G1 Y%.3f' %(float(self.YPocketCenterVar.get())-(float(self.PocketYVar.get())/2.0) ))
                self.gcode.append('G0 Z%.3f' %(float(self.SafeZVar.get())))
            #parallel outine
            if self.grid_parallelVar.get()=="yes":
                if pocket_length_x < pocket_length_y:
                    recs=int(pocket_length_x/2/Spacing)
                else:
                    recs=int(pocket_length_y/2/Spacing)
                space_x=pocket_length_x/2.0/recs
                space_y=pocket_length_y/2.0/recs
                self.gcode.append('(Parallel Outline)')
                for rec in xrange(1,recs):
                    newx=rec*space_x
                    newy=rec*space_y
                    self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                        150-newx/Scale,
                        150-newy/Scale,
                        150+newx/Scale,
                        150+newy/Scale, outline='red'))
                    self.gcode.append('G0 X%.3f Y%.3f' %(centerx+newx,centery+newy))
                    self.Go_down()
                    self.gcode.append('G1 X%.3f F%.2f' %(centerx-newx,float(self.Feedspeed.get())))
                    self.gcode.append('G1 Y%.3f ' %(centery-newy))
                    self.gcode.append('G1 X%.3f ' %(centerx+newx))
                    self.gcode.append('G1 Y%.3f ' %(centery+newy))
                    self.Go_up()
                    
            # target cross
            if self.Cross.get() == "yes":
                newy=(b+float(self.cross_offset_entry.get()))/Scale
                newx=(a+float(self.cross_offset_entry.get()))/Scale
                self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150-newy,150,150+newy,fill="red"))
                self.CanvasDrawings.append(self.PreviewCanvas.create_line(150-newx,150,150+newx,150,fill="red"))
                self.gcode.append('(Cross)')
                #g-code Y cross
                self.gcode.append('G0 X%.3f Y%.3f' %(float(self.XPocketCenterVar.get()),
                    (float(self.YPocketCenterVar.get())-(float(self.PocketYVar.get())/2.0)-float(self.cross_offset_entry.get()) )))
                self.Go_down()
                self.gcode.append('G1 Y%.3f F%.2f' %((float(self.YPocketCenterVar.get())+(float(self.PocketYVar.get())/2.0)+float(self.cross_offset_entry.get())) 
                    ,float(self.FeedspeedVar.get())))
                self.Go_up()
                #g-code x cross
                self.gcode.append('G0 X%.3f Y%.3f' %((float(self.XPocketCenterVar.get())-(float(self.PocketXVar.get())/2.0)-float(self.cross_offset_entry.get()),
                    float(self.YPocketCenterVar.get()) )))
                self.Go_down()
                self.gcode.append('G1 X%.3f F%.2f' %((float(self.XPocketCenterVar.get())+(float(self.PocketXVar.get())/2.0)+float(self.cross_offset_entry.get())) 
                    ,float(self.FeedspeedVar.get())))
                self.Go_up()
                                            
            if self.grid_onVar.get()=="yes":#
                lines_x=int(self.grid_lines_X.get())
                lines_y=int(self.grid_lines_Y.get())
                space_x=float(self.PocketX.get())/(lines_x+1)/Scale
                space_y=float(self.PocketY.get())/(lines_y+1)/Scale
                
                if self.grid_style.get()=="symetric":
                    lines_x=int(float(self.PocketX.get())/float(self.Stepover.get()) )
                    lines_y=int(float(self.PocketY.get())/float(self.Stepover.get()) )
                    space_x=float(self.PocketX.get())/(lines_x+1)/Scale
                    space_y=float(self.PocketY.get())/(lines_y+1)/Scale
                
                #grafik
                for line in xrange(1,lines_x+1):
                    newx=line*space_x+(150-a/Scale)
                    if self.grid_border.get()== 1:
                        newy=(b-float(self.border.get()))/Scale
                    else:
                        newy=b/Scale
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(newx,150-newy,newx,150+newy,fill='red'))
                for line in xrange(1,lines_y+1):
                    newy=line*space_y+(150-b/Scale)
                    if self.grid_border.get()== 1:
                        newx=(a-float(self.border.get()))/Scale
                    else:
                        newx=a/Scale
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(150-newx,newy,150+newx,newy,fill='red'))
                #gcode
                self.gcode.append('(xGrid)')
                for line in xrange(1,lines_x+1):
                    newx=(float(self.XPocketCenter.get())-(float(self.PocketX.get())/2.0)) + line*(float(self.PocketX.get())/(lines_x+1))
                    if self.grid_border.get()== 1:
                        newy_center_offset=(float(self.PocketY.get())/2.0) - float(self.border.get())
                        y_mill_length=float(self.PocketY.get())-(2*float(self.border.get()))
                    else:
                        newy_center_offset=float(self.PocketY.get())/2.0
                        y_mill_length=float(self.PocketY.get())
                    #zig zag
                    if line %2==0:
                        newy=float(self.YPocketCenter.get())+newy_center_offset
                        self.gcode.append('G0 X%.3f Y%.3f' % (newx,newy))
                        self.Go_down()
                        self.gcode.append('G1 G91 Y-%.3f' % y_mill_length )

                    else:
                        newy=float(self.YPocketCenter.get())-newy_center_offset
                        self.gcode.append('G0 X%.3f Y%.3f' %(newx,newy))
                        self.Go_down()
                        self.gcode.append('G1 G91 Y+%.3f' % y_mill_length )
                    self.gcode.append('G0 G90 Z%.3f' %(float(self.SafeZVar.get())))
                #"""
                self.gcode.append('(yGrid)')
                for line in xrange(1,lines_y+1):
                    newy=(float(self.YPocketCenter.get())-(float(self.PocketY.get())/2.0)) + line*(float(self.PocketY.get())/(lines_y+1))
                    if self.grid_border.get()== 1:
                        newx_center_offset=(float(self.PocketX.get())/2.0)-float(self.border.get())
                        x_mill_length=float(self.PocketX.get())-(2*float(self.border.get()))
                    else:
                        newx_center_offset=float(self.PocketX.get())/2.0
                        x_mill_length=float(self.PocketX.get())
                    #zig zag
                    if line %2==0:
                        newx=float(self.XPocketCenter.get())+newx_center_offset
                        self.gcode.append('G0 X%.3f Y%.3f' %(newx,newy))
                        self.gcode.append('G0 Z%.3f' %(float(self.RapidZ.get())))
                        self.gcode.append('G1 Z%.3f F%.2f' %(float(self.FinalDepth.get()) ,float(self.FeedspeedZVar.get())))
                        self.gcode.append('G1 G91 X-%.3f' % x_mill_length )
                    else:
                        newx=float(self.XPocketCenter.get())-newx_center_offset
                        self.gcode.append('G0 X%.3f Y%.3f' %(newx,newy))
                        self.gcode.append('G0 Z%.3f' %(float(self.RapidZ.get())))
                        self.gcode.append('G1 Z%.3f F%.2f' %(float(self.FinalDepth.get()) ,float(self.FeedspeedZVar.get())))
                        self.gcode.append('G1 G91 X+%.3f' % x_mill_length )
                    self.gcode.append('G0 G90 Z%.3f' %(float(self.SafeZVar.get())))
            if self.spider_grid.get()=="yes":
                start_angel=float(self.spider_startangel_entry.get())
                angel_lines=int(self.spider_lines_entry.get())
                spider_offset=float(self.spider_offset_entry.get())
                angel_space=360.0/angel_lines
                b+=spider_offset
                a+=spider_offset
                for line in range(angel_lines):
                    line_angel=(line*angel_space)+start_angel
                    
                    line_x, line_y = b * tan(radians(line_angel)), b
                   
                    if abs(line_x) > a:
                        line_x, line_y = a, a / tan(radians(line_angel))
                   
                    if 135 <= line_angel < 135 + 180:
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150+line_x/Scale,150+line_y/Scale,fill="red"))
                        self.gcode.append('G0 X%.3f Y%.3f' %(centerx,centery))
                        self.Go_down()
                        self.gcode.append('G1 X%.3f Y%.3f F%.2f' %(centerx+line_x,centery+line_y,float(self.FeedspeedVar.get())))
                        self.Go_up()                      
                    else:
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150-line_x/Scale,150-line_y/Scale,fill="red")) 
                        self.gcode.append('G0 X%.3f Y%.3f' %(centerx,centery))
                        self.Go_down()
                        self.gcode.append('G1 X%.3f Y%.3f F%.2f' %(centerx-line_x,centery-line_y,float(self.FeedspeedVar.get())))
                        self.Go_up()                      
 
               #"""
        #G-code
        self.gcode.append(self.PostambleVar.get())
    def Go_up(self):
        self.gcode.append('G0 Z%.3f' %(float(self.SafeZVar.get())))
    def Go_down(self):
        self.gcode.append('G0 Z%.3f' %(float(self.RapidZ.get())))
        self.gcode.append('G1 Z%.3f F%.2f' %(float(self.FinalDepth.get()) ,float(self.FeedspeedZVar.get())))
        
    def CopyClipboard(self):
        self.clipboard_clear()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        for line in self.gcode:
            sys.stdout.write(line+'\n')
        self.quit()

app = Application()
app.master.title("Grid.py 1.0 by Sammel Lothar")
app.mainloop()
