#!/usr/local/bin/python

# Bolt Circle Array G-code Generator
# Author: Dan Falck  <dfalck  at a domain called verizon dot net>
# Big John T inspired me to put this together today
# Big John T's face.py was used as a template to stay consistant with his programs
# boltcircle.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# boltcircle.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CADvas; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import math
from Tkinter import *
import tkMessageBox
import os


IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.Gcode_label=Label(self, text="Canned Cycle")
        self.Gcode_label.grid(row=1, column=0, sticky=E)
        self.Gcode_value=StringVar()
        self.Gcode_value.set('G81')
        self.Gcode_entry=Entry(self,width=10,textvariable=self.Gcode_value)
        self.Gcode_entry.grid(row=1, column=1, sticky=W)
        self.Gcode_entry.focus_set()

        self.Gcode_descr_label=Label(self, text="(ie G81,G82 etc...)")
        self.Gcode_descr_label.grid(row=1, column=2, sticky=E)


        self.feed_label=Label(self, text="Feed Rate")
        self.feed_label.grid(row=2, column=0, sticky=E)
        self.feed_value=DoubleVar()
        self.feed_entry=Entry(self,width=10,textvariable=self.feed_value)
        self.feed_entry.grid(row=2, column=1, sticky=W)
 
        self.Rplane_label=Label(self, text="Clearance Plane")
        self.Rplane_label.grid(row=3, column=0, sticky=E)
        self.Rplane_value=DoubleVar()
        self.Rplane_value.set(.75)
        self.Rplane_entry=Entry(self,width=10,textvariable=self.Rplane_value)
        self.Rplane_entry.grid(row=3, column=1, sticky=W)
 
        self.x_label=Label(self, text="X Position")
        self.x_label.grid(row=4, column=0, sticky=E)
        self.x_center_value=DoubleVar()
        self.x_center_entry=Entry(self,width=10,textvariable=self.x_center_value)
        self.x_center_entry.grid(row=4, column=1, sticky=W)

        self.y_label=Label(self, text="Y Position")
        self.y_label.grid(row=5, column=0, sticky=E)
        self.y_center_value=DoubleVar()
        self.y_center_entry=Entry(self,width=10,textvariable=self.y_center_value)
        self.y_center_entry.grid(row=5, column=1, sticky=W)

        self.z_label=Label(self, text="Z Depth")
        self.z_label.grid(row=6, column=0, sticky=E)
        self.z_center_value=DoubleVar()
        self.z_center_entry=Entry(self,width=10,textvariable=self.z_center_value)
        self.z_center_entry.grid(row=6, column=1, sticky=W)

        self.z_descr_label=Label(self, text="(use a negative value)")
        self.z_descr_label.grid(row=6, column=2, sticky=E)

        self.holes_label=Label(self, text="Number of Holes")
        self.holes_label.grid(row=7, column=0, sticky=E)
        self.no_of_holes_value=IntVar()
        self.no_of_holes_value.set(2)
        self.no_of_holes_entry = Entry(self,width=10,textvariable=self.no_of_holes_value)
        
        
        self.no_of_holes_entry.grid(row=7, column=1, sticky=W)

        self.holes_descr_label=Label(self, text="(should be 1 or more)")
        self.holes_descr_label.grid(row=7, column=2, sticky=E)

        self.dia_label=Label(self, text="Bolt Circle Diameter")
        self.dia_label.grid(row=8, column=0, sticky=E)
        self.bolt_circle_diameter_value=DoubleVar()
        self.bolt_circle_diameter_value.set(1.0)
        self.bolt_circle_diameter_entry=Entry(self,width=10,textvariable=self.bolt_circle_diameter_value)
        self.bolt_circle_diameter_entry.grid(row=8, column=1, sticky=W)

        self.dia_descr_label=Label(self, text="(should be positive value)")
        self.dia_descr_label.grid(row=8, column=2, sticky=E)

        self.angle_label=Label(self, text="Start Angle")
        self.angle_label.grid(row=9, column=0, sticky=E)
        self.start_angle_value=DoubleVar()
        self.start_angle_entry=Entry(self,width=10,textvariable=self.start_angle_value)
        self.start_angle_entry.grid(row=9, column=1, sticky=W)

        self.Scale_label=Label(self, text="Scale")
        self.Scale_label.grid(row=10, column=0, sticky=E)
        self.Scale_value=DoubleVar()
        self.Scale_value.set(1.0)
        self.Scale_entry=Entry(self,width=10,textvariable=self.Scale_value)
        self.Scale_entry.grid(row=10, column=1, sticky=W)


        self.scale_descr_label=Label(self, text="(should be positive value)")
        self.scale_descr_label.grid(row=10, column=2, sticky=E)


        self.g_code = Text(self, width=65, height=25)
        self.g_code.grid(row=11, column=0, columnspan=4)

        self.GenButton = Button(self, text='Generate G-Code')
        self.GenButton.grid(row=12, column=0)
        self.GenButton.bind("<Button-1>", self.GenCode)
        
        self.CopyButton = Button(self, text='Copy to Clipboard')
        self.CopyButton.grid(row=12, column=1)
        self.CopyButton.bind('<Button-1>', self.CopyClpBd)

        self.ClearButton = Button(self, text="Clear Screen", command=self.ClearText)
        self.ClearButton.grid(row=12, column=2)
        
        #self.quitButton = Button(self, text="Quit", command=self.quit)
        #self.quitButton.grid(row=12, column=3)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=12, column=3)

    def GenCode(self, event):
        """ Generate the G-Code for a bolt circle using a canned drill 
        cycle. Fill in center of canned cycle, feed rate, center of circle etc..."""

        x_center=float(self.x_center_value.get())
        y_center=float(self.y_center_value.get())
        z_center=float(self.z_center_value.get())
        no_of_holes=float(self.no_of_holes_value.get())
        bolt_circle_diameter=float(self.bolt_circle_diameter_value.get())
        start_angle=float(self.start_angle_value.get())
        scale=float(self.Scale_value.get())    
        count = 0
        anglecount=1   
        circle_division_angle=(360/no_of_holes)
        calc_angle=start_angle
        self.g_code.insert(END,(self.Gcode_value.get()))
        while (count < no_of_holes):
	    x1=math.cos(math.radians(calc_angle))*(bolt_circle_diameter/2)
	    y1=math.sin(math.radians(calc_angle))*(bolt_circle_diameter/2)
            x=(x1+x_center)*scale
            y=(y1+y_center)*scale        
            z=(z_center)*scale
	                                 
            
            #self.g_code.insert(END,(self.Gcode_value.get()))
            self.g_code.insert(END,' ')
            self.g_code.insert(END,'X%.4f Y%.4f Z%.4f '% (x, y, z))
            self.g_code.insert(END,' R')
            self.g_code.insert(END,(self.Rplane_value.get()))
            self.g_code.insert(END,' F') 
            self.g_code.insert(END,(self.feed_value.get()))
            self.g_code.insert(END,'\n') 
	    anglecount=anglecount+1
	
	    calc_angle=calc_angle + circle_division_angle	

            count=count+1
	   
        self.g_code.insert(END, 'G80 (End of Cycle)\n')
        
    def CopyClpBd(self, event):
        '''This function copies the contents of g_code to the clipboard '''
        self.g_code.clipboard_clear()
        self.g_code.clipboard_append(self.g_code.get(0.0, END))
        self.g_code.clipboard_append('M2\n')

    def ClearText(self):
        self.g_code.delete(1.0,END)

    def WriteToAxis(self):
        self.g_code.insert(END, 'M2\n')
        sys.stdout.write(self.g_code.get(0.0, END)+'\n')
        self.quit()

app = Application()
app.master.title("Bolt Circle Array G-Code Generator")
app.mainloop()
