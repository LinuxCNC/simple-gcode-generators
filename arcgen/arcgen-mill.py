#!/usr/bin/env python

"""
Arc Generator G-Code Generator
Version 1.8
Copyright (C) <2008>  <John Thornton>

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

e-mail me any suggestions to "bjt 128 at gmail dot com"
If you make money using this software
you must donate $20 USD to a local food bank
or the food police will get you! Think of others from time to time...

To make it a menu item in Ubuntu use the Alacarte Menu Editor and add 
the command python YourPathToThisFile/face.py
make sure you have made the file execuatble by right
clicking and selecting properties then Permissions and Execute

To use with LinuxCNC see the instructions at: 
https://github.com/linuxcnc/simple-gcode-generators

Inspired by Sebastian Jardi Estadella's addition to send the output to gEdit
I've decided to incorporate it into Arc Buddy and make some additions that
should make this program actually useful.

The following instructions are for Ubuntu 10.04
Open Gedit and navigate to Edit > Preferences > Plugins and check off
External Tools to add them to your menu.
Go to Tools > Manage External Tools and click on the page with a star in the
lower left corner above the Help button. This adds a new Tool. Change the name
of New Tool to something that makes sense to you like Arc Buddy and hit Enter
to save the new name. Add a shortcut key if you like. Change Output: to 
Insert at cursor position. In the Edit: box change line 1 to:
python full/path/to/arcbuddy/arcbuddy.py

Close the External Tools Manager and your ready to use Arc Buddy in Gedit
after you close and reopen Gedit.

When your creating G code in Gedit go to Tools > External Tools > Arc Buddy
Add the required data and click Show Me to see or click Send to send the
output to Gedit.

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

  def createWidgets(self):
    self.PreviewFrame = Frame(self,bd=5)
    self.PreviewFrame.grid(row=0, column=0)
    self.PreviewCanvas = Canvas(self.PreviewFrame,width=300, height=300, bg='white')
    self.PreviewCanvas.grid(sticky=N+S+E+W)
    self.XLine = self.PreviewCanvas.create_line(75,150,225,150)
    self.YLine = self.PreviewCanvas.create_line(150,75,150,225)
    self.Deg0 = self.PreviewCanvas.create_text(245, 150, text='0 X+')
    self.Deg90 = self.PreviewCanvas.create_text(150, 60, text='Y+\n90')
    self.Deg180 = self.PreviewCanvas.create_text(50, 150, text='X- 180')
    self.Deg270 = self.PreviewCanvas.create_text(150, 240, text='270\nY-')

    self.EntryFrame = Frame(self,bd=5)
    self.EntryFrame.grid(row=0, column=1)

    self.st00 = Label(self.EntryFrame, text='Figure out the G2/3 Code')
    self.st00.grid(row=0, column=0, columnspan=2)

    self.st01 = Label(self.EntryFrame, text='X Center of Arc')
    self.st01.grid(row=1, column=0)
    self.XArcCenterVar = StringVar()
    self.XArcCenter = Entry(self.EntryFrame, textvariable=self.XArcCenterVar ,width=15)
    self.XArcCenter.grid(row=1, column=1)

    self.st02 = Label(self.EntryFrame, text='Y Center of Arc')
    self.st02.grid(row=2, column=0)
    self.YArcCenterVar = StringVar()
    self.YArcCenter = Entry(self.EntryFrame, textvariable=self.YArcCenterVar ,width=15)
    self.YArcCenter.grid(row=2, column=1)

    self.st03 = Label(self.EntryFrame, text='Diameter of Arc')
    self.st03.grid(row=3, column=0)
    self.ArcDiameterVar = StringVar()
    self.ArcDiameter = Entry(self.EntryFrame, textvariable=self.ArcDiameterVar ,width=15)
    self.ArcDiameter.grid(row=3, column=1)

    self.st04 = Label(self.EntryFrame, text='Start Angle')
    self.st04.grid(row=4, column=0)
    self.StartAngleVar = StringVar()
    self.StartAngle = Entry(self.EntryFrame, textvariable=self.StartAngleVar ,width=15)
    self.StartAngle.grid(row=4, column=1)

    self.st05 = Label(self.EntryFrame, text='End Angle')
    self.st05.grid(row=5, column=0)
    self.EndAngleVar = StringVar()
    self.EndAngle = Entry(self.EntryFrame, textvariable=self.EndAngleVar ,width=15)
    self.EndAngle.grid(row=5, column=1)

    self.st05 = Label(self.EntryFrame, text='Direction')
    self.st05.grid(row=6, column=0)
    self.DirectionVar = IntVar()
    Radiobutton(self.EntryFrame, text='CCW', value=0, variable=self.DirectionVar)\
        .grid(row=6, column=1, sticky = W)

    Radiobutton(self.EntryFrame, text='CW', value=1, variable=self.DirectionVar)\
        .grid(row=6, column=1, sticky = E)

    self.st07 = Label(self.EntryFrame, text='Feed Value')
    self.st07.grid(row=7, column=0)
    self.FeedRateVar = StringVar()
    self.FeedRate = Entry(self.EntryFrame, textvariable=self.FeedRateVar ,width=15)
    self.FeedRate.grid(row=7, column=1)


    self.sp00 = Label(self.EntryFrame, text=' ')
    self.sp00.grid(row=8)

    self.st06 = Label(self.EntryFrame, text='Starting Point for the Arc')
    self.st06.grid(row=9, column=0, columnspan=2) 
    self.StartPointVar = StringVar()  
    self.StartPoint = Entry(self.EntryFrame, width=30, textvariable = self.StartPointVar)
    self.StartPoint.grid(row=10, column=0, columnspan=2)

    self.st06 = Label(self.EntryFrame, text='G Code for the Arc')
    self.st06.grid(row=11, column=0, columnspan=2) 
    self.ArcCodeVar = StringVar()  
    self.ArcCode = Entry(self.EntryFrame, width=35, textvariable = self.ArcCodeVar)
    self.ArcCode.grid(row=12, column=0, columnspan=2)

    self.sp01 = Label(self.EntryFrame, text=' ')
    self.sp01.grid(row=13)
    
    self.DoItButton = Button(self.EntryFrame, text='Show Me', command=self.DoIt)
    self.DoItButton.grid(row=14, column=0)
    
    self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
    self.ToClipboard.grid(row=14, column=1)
    

    if IN_AXIS:
      self.quitButton = Button(self, text='Write to AXIS and Quit',\
          command=self.WriteToAxis)
    else:
      self.quitButton = Button(self, text='Quit', command=self.quit)
      self.sendArcButton = Button(self, text='Send All', command=self.SendAll)
      self.sendArcButton.grid(row=13, column=0)
      self.sendAllButton = Button(self, text='Send Arc', command=self.SendArc)
      self.sendAllButton.grid(row=13, column=1)

    self.quitButton.grid(row=13, column=2, sticky=S)

  def DoIt(self):
      # draw the arc
      try:
          self.PreviewCanvas.delete(self.ArcId)
      except AttributeError:
          pass
      self.XArcCenterN = float(self.XArcCenterVar.get())
      self.YArcCenterN = float(self.YArcCenterVar.get())
      self.ArcStart = float(self.StartAngleVar.get())
      self.ArcEnd = float(self.EndAngleVar.get())
      self.ArcDirection = int(self.DirectionVar.get())

      if self.ArcDirection == 0: #CCW
          if self.ArcStart < self.ArcEnd:
              self.ArcDegrees = self.ArcEnd - self.ArcStart
          elif self.ArcStart > self.ArcEnd:
              self.ArcDegrees = (360 - self.ArcStart) + self.ArcEnd
          elif self.ArcStart == self.ArcEnd:
              self.ArcDegrees = 360
          self.ArcId = self.PreviewCanvas.create_arc(75,75,225,225,extent=self.ArcDegrees,\
              start=self.ArcStart, style='arc')

      elif self.ArcDirection == 1: # CW
          if self.ArcStart > self.ArcEnd:
              self.ArcDegrees = self.ArcStart - self.ArcEnd
          elif self.ArcStart < self.ArcEnd:
              self.ArcDegrees = (360 - self.ArcEnd) + self.ArcStart
          elif self.ArcStart == self.ArcEnd:
              self.ArcDegrees = 360
          self.ArcId = self.PreviewCanvas.create_arc(75,75,225,225,extent=self.ArcDegrees,\
              start=self.ArcEnd, style='arc')

      # generate the G code
      self.ArcRadius = float(self.ArcDiameterVar.get())/2
      
      # find the X and Y start point and offset
      if self.ArcStart <= 90: # Quadrant 1
          self.XStart = self.XArcCenterN + (self.ArcRadius * cos(radians(self.ArcStart)))
          self.YStart = self.YArcCenterN + (self.ArcRadius * sin(radians(self.ArcStart)))
          self.StartPointVar.set('X%3.4f Y%3.4f' %(self.XStart, self.YStart))
          self.IOffset = -(self.XStart - self.XArcCenterN)
          self.JOffset = -(self.YStart - self.YArcCenterN)

      elif self.ArcStart > 90 and self.ArcStart <= 180: # Quadrant 2
          self.XStart = self.XArcCenterN - (self.ArcRadius*sin(radians(self.ArcStart-90)))
          self.YStart = self.YArcCenterN + (self.ArcRadius*cos(radians(self.ArcStart-90)))
          self.StartPointVar.set('X%3.4f Y%3.4f' %(self.XStart, self.YStart))
          self.IOffset = abs(self.XStart - self.XArcCenterN)
          self.JOffset = -(self.YStart - self.YArcCenterN)

      elif self.ArcStart > 180 and self.ArcStart <= 270: # Quadrant 3
          self.XStart = self.XArcCenterN - (self.ArcRadius*cos(radians(self.ArcStart-180)))
          self.YStart = self.YArcCenterN - (self.ArcRadius*sin(radians(self.ArcStart-180)))
          self.StartPointVar.set('X%3.4f Y%3.4f' %(self.XStart, self.YStart))
          self.IOffset = abs(self.XStart - self.XArcCenterN)
          self.JOffset = abs(self.YStart - self.YArcCenterN)

      elif self.ArcStart > 270 and self.ArcStart <= 360: # Quadrant 4
          self.XStart = self.XArcCenterN + (self.ArcRadius*sin(radians(self.ArcStart-270)))
          self.YStart = self.YArcCenterN - (self.ArcRadius*cos(radians(self.ArcStart-270)))
          self.StartPointVar.set('X%3.4f Y%3.4f' %(self.XStart, self.YStart))
          self.IOffset = -(self.XStart - self.XArcCenterN)
          self.JOffset = -(self.YStart - self.YArcCenterN)

      # find the X and Y end point
      if self.ArcEnd <= 90: # Quadrant 1
          self.XEnd = self.XArcCenterN + (self.ArcRadius * cos(radians(self.ArcEnd)))
          self.YEnd = self.YArcCenterN + (self.ArcRadius * sin(radians(self.ArcEnd)))
          self.ArcEndPoint = 'X%3.4f Y%3.4f' %(self.XStart, self.YStart)
      elif self.ArcEnd > 90 and self.ArcEnd <= 180: # Quadrant 2
          self.XEnd = self.XArcCenterN - (self.ArcRadius*sin(radians(self.ArcEnd-90)))
          self.YEnd = self.YArcCenterN + (self.ArcRadius*cos(radians(self.ArcEnd-90)))
          self.ArcEndPoint = 'X%3.4f Y%3.4f' %(self.XStart, self.YStart)
      elif self.ArcEnd > 180 and self.ArcEnd <= 270: # Quadrant 3
          self.XEnd = self.XArcCenterN - (self.ArcRadius*cos(radians(self.ArcEnd-180)))
          self.YEnd = self.YArcCenterN - (self.ArcRadius*sin(radians(self.ArcEnd-180)))
          self.ArcEndPoint = 'X%3.4f Y%3.4f' %(self.XStart, self.YStart)
      elif self.ArcEnd > 270 and self.ArcEnd <= 360: # Quadrant 4
          self.XEnd = self.XArcCenterN + (self.ArcRadius*sin(radians(self.ArcEnd-270)))
          self.YEnd = self.YArcCenterN - (self.ArcRadius*cos(radians(self.ArcEnd-270)))
          self.ArcEndPoint = 'X%3.4f Y%3.4f' %(self.XStart, self.YStart)

      if self.ArcDirection == 0: # CCW
          self.ArcCodeVar.set('G3 X%.4f Y%.4f I%.4f J%.4f' \
          %(self.XEnd, self.YEnd, self.IOffset, self.JOffset))
      elif self.ArcDirection == 1: # CW
          self.ArcCodeVar.set('G2 X%.4f Y%.4f I%.4f J%.4f' \
          %(self.XEnd, self.YEnd, self.IOffset, self.JOffset))

      self.gcode = 'F' + self.FeedRateVar.get() + '\n'
      self.gcode += 'G0 '+ self.StartPointVar.get() + '\n'
      self.gcode += self.ArcCodeVar.get() + '\n'
      self.gcode += 'M2'

  def CopyClipboard(self):
      self.ArcCode.clipboard_clear()
      self.ArcCode.clipboard_append(self.ArcCode.get())
          
  def WriteToAxis(self):
      sys.stdout.write(self.gcode)
      self.quit()

  def SendArc(self):
    self.DoIt()
    sys.stdout.write(self.ArcCode.get() + "\r\n")
    self.quit()

  def SendAll(self):
    self.DoIt()
    if self.FeedRateVar.get() <> '':
      sys.stdout.write('F' + self.FeedRateVar.get() + "\r\n")
    sys.stdout.write('G1 ' + self.StartPoint.get() + "\r\n")
    sys.stdout.write(self.ArcCode.get() + "\r\n")
    self.quit()


app = Application()
app.master.title("Mill Arc Generator 1.8")
app.mainloop()


