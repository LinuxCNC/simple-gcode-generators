#!/usr/bin/python
"""
    engrave-xx.py G-Code Generator

    Copyright (C) <2008>  <Lawrence Glaister> <ve7it at shaw dot ca>
    based on work by John Thornton  -- GUI framwork from arcbuddy.py
                     Ben Lipkowitz  (fenn)-- cxf2cnc.py v0.5 font parsing code

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
    the command python YourPathToThisFile/grill.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with EMC2 see the instructions at:
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators

    Version 10 intial code
    version 11 - lpg 14oct2008  fixed sytax error that prevented code running on 
               python 2.4 (supplied with ubuntu 6.06)
"""
version = '11'
#fontfile = "/usr/share/qcad/fonts/romans2.cxf"
fontfile = "/usr/share/qcad/fonts/romanc.cxf"
#fontfile = "/usr/share/qcad/fonts/normal.cxf"

from Tkinter import *
from math import *
import os
import re

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

#=======================================================================
# This routine parses the .cxf font file and builds a font dictionary of
# line segment strokes required to cut each character.
# Arcs (only used in some fonts) are converted to a number of line
# segemnts based on the angular length of the arc. Since the idea of
# this font description is to make it support independant x and y scaling,
# we can not use native arcs in the gcode.
#=======================================================================
def parse(file):
    font = {}
    key = None
    num_cmds = 0
    line_num = 0
    for text in file:
        #format for a typical letter (lowercase r):
        ##comment, with a blank line after it
        #
        #[r] 3
        #L 0,0,0,6
        #L 0,6,2,6
        #A 2,5,1,0,90
        #
        line_num += 1
        end_char = re.match('^$', text) #blank line
        if end_char and key: #save the character to our dictionary
            font[key] = Character(key)
            font[key].stroke_list = stroke_list
            font[key].xmax = xmax
            if (num_cmds != cmds_read):
                print "(warning: discrepancy in number of commands %s, line %s, %s != %s )" % (fontfile, line_num, num_cmds, cmds_read)

        new_cmd = re.match('^\[(.*)\]\s(\d+)', text)
        if new_cmd: #new character
            key = new_cmd.group(1)
            num_cmds = int(new_cmd.group(2)) #for debug
            cmds_read = 0
            stroke_list = []
            xmax, ymax = 0, 0

        line_cmd = re.match('^L (.*)', text)
        if line_cmd:
            cmds_read += 1
            coords = line_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            stroke_list += [Line(coords)]
            xmax = max(xmax, coords[0], coords[2])

        arc_cmd = re.match('^A (.*)', text)
        if arc_cmd:
            cmds_read += 1
            coords = arc_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            xcenter, ycenter, radius, start_angle, end_angle = coords
            # since font defn has arcs as ccw, we need some font foo
            if ( end_angle < start_angle ):
                start_angle -= 360.0
            # approximate arc with line seg every 20 degrees
            segs = int((end_angle - start_angle) / 20) + 1
            angleincr = (end_angle - start_angle)/segs
            xstart = cos(start_angle * pi/180) * radius + xcenter
            ystart = sin(start_angle * pi/180) * radius + ycenter
            angle = start_angle
            for i in range(segs):
                angle += angleincr
                xend = cos(angle * pi/180) * radius + xcenter
                yend = sin(angle * pi/180) * radius + ycenter
                coords = [xstart,ystart,xend,yend]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])
                ymax = max(ymax, coords[1], coords[3])
                xstart = xend
                ystart = yend
    return font


#=======================================================================
class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%s" % (self.stroke_list)

    def get_xmax(self):
        try: return max([s.xmax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymax(self):
        try: return max([s.ymax for s in self.stroke_list[:]])
        except ValueError: return 0



#=======================================================================
class Line:

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend)




#=======================================================================
class Application(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.DoIt()

    def createWidgets(self):
        self.segID = []
        self.gcode = []
        self.PreviewFrame = Frame(self,bd=5)
        self.PreviewFrame.grid(row=0, column=0)
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=300, height=300, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.XLine = self.PreviewCanvas.create_line(15,150,285,150, fill = 'green')
        self.YLine = self.PreviewCanvas.create_line(150,15,150,285, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.st00 = Label(self.EntryFrame, text='Engrave a Text String\n')
        self.st00.grid(row=0, column=0, columnspan=2)

        self.st01 = Label(self.EntryFrame, text='Preamble')
        self.st01.grid(row=1, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G20 G90 G64 P0.003 M3 S3000 M7 F5')
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=40)
        self.Preamble.grid(row=1, column=1)

        self.st02 = Label(self.EntryFrame, text='Font File (Qcad .cxf)')
        self.st02.grid(row=2, column=0)
        self.FontVar = StringVar()
        self.FontVar.set(fontfile)
        self.Font = Entry(self.EntryFrame, textvariable=self.FontVar ,width=40)
        self.Font.grid(row=2, column=1)
        self.NormalColor =  self.Font.cget('bg')

        self.st03 = Label(self.EntryFrame, text='Text')
        self.st03.grid(row=3, column=0)
        self.TextVar = StringVar()
        self.TextVar.set('*EMC2 Rocks*')
        self.Text = Entry(self.EntryFrame, textvariable=self.TextVar ,width=40)
        self.Text.grid(row=3, column=1)

        self.st04 = Label(self.EntryFrame, text='X Start')
        self.st04.grid(row=4, column=0)
        self.XStartVar = StringVar()
        self.XStartVar.set('1.0')
        self.XStart = Entry(self.EntryFrame, textvariable=self.XStartVar ,width=15)
        self.XStart.grid(row=4, column=1)

        self.st05 = Label(self.EntryFrame, text='Y Start')
        self.st05.grid(row=5, column=0)
        self.YStartVar = StringVar()
        self.YStartVar.set('2.0')
        self.YStart = Entry(self.EntryFrame, textvariable=self.YStartVar ,width=15)
        self.YStart.grid(row=5, column=1)

        self.st06 = Label(self.EntryFrame, text='Angle(degrees)')
        self.st06.grid(row=6, column=0)
        self.AngleVar = StringVar()
        self.AngleVar.set('0.0')
        self.Angle = Entry(self.EntryFrame, textvariable=self.AngleVar ,width=15)
        self.Angle.grid(row=6, column=1)

        self.st07 = Label(self.EntryFrame, text='XScale')
        self.st07.grid(row=7, column=0)
        self.XScaleVar = StringVar()
        self.XScaleVar.set('0.04')
        self.XScale = Entry(self.EntryFrame, textvariable=self.XScaleVar ,width=15)
        self.XScale.grid(row=7, column=1)

        self.st08 = Label(self.EntryFrame, text='YScale')
        self.st08.grid(row=8, column=0)
        self.YScaleVar = StringVar()
        self.YScaleVar.set('0.04')
        self.YScale = Entry(self.EntryFrame, textvariable=self.YScaleVar ,width=15)
        self.YScale.grid(row=8, column=1)

        self.st09 = Label(self.EntryFrame, text='Char Space (% of Char)')
        self.st09.grid(row=9, column=0)
        self.CSpacePVar = StringVar()
        self.CSpacePVar.set('25.0')
        self.CSpaceP = Entry(self.EntryFrame, textvariable=self.CSpacePVar ,width=15)
        self.CSpaceP.grid(row=9, column=1)

        self.st10 = Label(self.EntryFrame, text='Word Space (% of Char)')
        self.st10.grid(row=10, column=0)
        self.WSpacePVar = StringVar()
        self.WSpacePVar.set('100.0')
        self.WSpaceP = Entry(self.EntryFrame, textvariable=self.WSpacePVar ,width=15)
        self.WSpaceP.grid(row=10, column=1)


        self.st12 = Label(self.EntryFrame, text='Engraving Depth')
        self.st12.grid(row=12, column=0)
        self.DepthVar = StringVar()
        self.DepthVar.set('-0.010')
        self.Depth = Entry(self.EntryFrame, textvariable=self.DepthVar ,width=15)
        self.Depth.grid(row=12, column=1)

        self.st13 = Label(self.EntryFrame, text='Safe Z')
        self.st13.grid(row=13, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('+0.100')
        self.SafeZ = Entry(self.EntryFrame, width=15, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=13, column=1)

        self.st14 = Label(self.EntryFrame, text='Postamble')
        self.st14.grid(row=14, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=15)
        self.Postamble.grid(row=14, column=1)

        self.st15 = Label(self.EntryFrame, text='Text Orientation')
        self.st15.grid(row=15, column=0)
        self.MirrorVar = IntVar()
        self.MirrorVar.set(0)
        self.FlipVar = IntVar()
        self.FlipVar.set(0)
        Checkbutton(self.EntryFrame, text='Mirrored', variable=self.MirrorVar, command=self.DoIt).grid(row=15, column=1,sticky=W)
        Checkbutton(self.EntryFrame, text='Flipped', variable=self.FlipVar,command=self.DoIt).grid(row=15, column=1,sticky=E)

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=16, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=16, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

#=======================================================================
    def CopyClipboard(self):
        self.clipboard_clear()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

#=======================================================================
    def WriteToAxis(self):
        for line in self.gcode:
            sys.stdout.write(line+'\n')
        self.quit()

#=======================================================================
    def sanitize(self,string):
        retval = ''
        good=' ~!@#$%^&*_+=-{}[]|\:;"<>,./?'
        for char in string:
            if char.isalnum() or good.find(char) != -1:
                retval += char
            else: retval += ( ' 0x%02X ' %ord(char))
        return retval

#=======================================================================
# routine takes an x and a y in raw internal format
# x and y scales are applied and then x,y pt is rotated by angle
# Returns new x,y tuple
    def Rotn(self,x,y,xscale,yscale,angle):
        Deg2Rad = 2.0 * pi / 360.0
        xx = x * xscale
        yy = y * yscale
        rad = sqrt(xx * xx + yy * yy)
        theta = atan2(yy,xx)
        newx=rad * cos(theta + angle*Deg2Rad)
        newy=rad * sin(theta + angle*Deg2Rad)
        return newx,newy



#=======================================================================
    def DoIt(self):
        # range check inputs for gross errors
        try:
            self.Font.configure( bg = self.NormalColor )
            file = open(self.Font.get())
        except:
            self.Font.configure( bg = 'red' )
            return

        Angle =    float(self.AngleVar.get())
        self.Angle.configure( bg = self.NormalColor )
        if Angle <= -360.0 or Angle >= 360.0:
            self.Angle.configure( bg = 'red' )
            return

        XScale =   float(self.XScaleVar.get())
        self.XScale.configure( bg = self.NormalColor )
        if XScale <= 0.0:
            self.XScale.configure( bg = 'red' )
            return

        YScale =   float(self.YScaleVar.get())
        self.YScale.configure( bg = self.NormalColor )
        if YScale <= 0.0:
            self.YScale.configure( bg = 'red' )
            return

        CSpaceP=   float(self.CSpaceP.get())
        self.CSpaceP.configure( bg = self.NormalColor )
        if CSpaceP <= 0.0:
            self.CSpaceP.configure( bg = 'red' )
            return

        WSpaceP=   float(self.WSpaceP.get())
        self.WSpaceP.configure( bg = self.NormalColor )
        if WSpaceP <= 0.0:
            self.WSpaceP.configure( bg = 'red' )
            return



        # erase old segs/display objects as needed
        for seg in self.segID:
            self.PreviewCanvas.delete(seg)
        self.segID = []

        # erase old gcode as needed
        self.gcode = []

        # temps used for engraving calcs
        String =   self.TextVar.get()
        SafeZ =    float(self.SafeZVar.get())
        XStart =   float(self.XStart.get())
        YStart =   float(self.YStart.get())
        Depth =    float(self.DepthVar.get())

        XScale =   float(self.XScaleVar.get())
        YScale =   float(self.YScaleVar.get())
        CSpaceP=   float(self.CSpaceP.get())

        oldx = oldy = -99990.0      # last engraver position

        self.gcode.append('( Code generated by engrave-'+version+'.py widget )')
        self.gcode.append('( by Lawrence Glaister VE7IT - 2008 )')
        self.gcode.append('( Engraving: "%s" at %.1f degrees)' %(self.sanitize(self.TextVar.get()),Angle))
        self.gcode.append('( Fontfile: %s )' %(self.FontVar.get()))
        self.gcode.append('#1000 = %.4f  ( Safe Z )' %(SafeZ))
        self.gcode.append('#1001 = %.4f  ( Engraving Depth Z )' %(Depth))
        self.gcode.append('#1002 = %.4f  ( X Start )' %(XStart))
        self.gcode.append('#1003 = %.4f  ( Y Start )' %(YStart))
        self.gcode.append('#1004 = %.4f  ( X Scale )' %(XScale))
        self.gcode.append('#1005 = %.4f  ( Y Scale )' %(YScale))
        self.gcode.append('#1006 = %.4f  ( Angle )' %(Angle))

        # write out subroutine for rotation logic
        self.gcode.append("(===================================================================)")
        self.gcode.append("(Subroutine to handle x,y rotation about 0,0)")
        self.gcode.append("(input x,y get scaled, rotated then offset )")
        self.gcode.append("( [#1 = 0 or 1 for a G0 or G1 type of move], [#2=x], [#3=y])")
        self.gcode.append("o9000 sub")
        self.gcode.append("  #28 = [#2 * #1004]  ( scaled x )")
        self.gcode.append("  #29 = [#3 * #1005]  ( scaled y )")
        self.gcode.append("  #30 = [SQRT[#28 * #28 + #29 * #29 ]]   ( dist from 0 to x,y )")
        self.gcode.append("  #31 = [ATAN[#29]/[#28]]                ( direction to  x,y )")
        self.gcode.append("  #32 = [#30 * cos[#31 + #1006]]     ( rotated x )")
        self.gcode.append("  #33 = [#30 * sin[#31 + #1006]]     ( rotated y )")
        self.gcode.append("  o9010 if [#1 LT 0.5]" )
        self.gcode.append("    G00 X[#32+#1002] Y[#33+#1003]")
        self.gcode.append("  o9010 else")
        self.gcode.append("    G01 X[#32+#1002] Y[#33+#1003]")
        self.gcode.append("  o9010 endif")
        self.gcode.append("o9000 endsub")
        self.gcode.append("(===================================================================)")
        self.gcode.append(self.PreambleVar.get())
        self.gcode.append( 'G0 Z#1000')

        font = parse(file)          # build stroke lists from font file
        file.close()

        font_line_height = max(font[key].get_ymax() for key in font)
        font_word_space =  max(font[key].get_xmax() for key in font) * (WSpaceP/100.0)
        font_char_space = font_word_space * (CSpaceP /100.0)

        xoffset = 0                 # distance along raw string in font units

        # calc a plot scale so we can show about first 15 chars of string
        # in the preview window
        PlotScale = 15 * font['A'].get_xmax() * XScale / 150

        for char in String:
            if char == ' ':
                xoffset += font_word_space
                continue
            try:
                self.gcode.append("(character '%s')" % self.sanitize(char))

                first_stroke = True
                for stroke in font[char].stroke_list:
#                    self.gcode.append("(%f,%f to %f,%f)" %(stroke.xstart,stroke.ystart,stroke.xend,stroke.yend ))
                    dx = oldx - stroke.xstart
                    dy = oldy - stroke.ystart
                    dist = sqrt(dx*dx + dy*dy)

                    x1 = stroke.xstart + xoffset
                    y1 = stroke.ystart
                    if self.MirrorVar.get() == 1:
                        x1 = -x1
                    if self.FlipVar.get() == 1:
                        y1 = -y1

                    # check and see if we need to move to a new discontinuous start point
                    if (dist > 0.001) or first_stroke:
                        first_stroke = False
                        #lift engraver, rapid to start of stroke, drop tool
                        self.gcode.append("G0 Z#1000")
                        self.gcode.append('o9000 call [0] [%.4f] [%.4f]' %(x1,y1))
                        self.gcode.append("G1 Z#1001")

                    x2 = stroke.xend + xoffset
                    y2 = stroke.yend
                    if self.MirrorVar.get() == 1:
                        x2 = -x2
                    if self.FlipVar.get() == 1:
                        y2 = -y2
                    self.gcode.append('o9000 call [1] [%.4f] [%.4f]' %(x2,y2))
                    oldx, oldy = stroke.xend, stroke.yend

                    # since rotation and scaling is done in gcode, we need equivalent for plotting
                    # note that plot shows true shape and orientation of chrs, but starting x,y
                    # is always at the center of the preview window (offsets not displayed)
                    x1,y1 = self.Rotn(x1,y1,XScale,YScale,Angle)
                    x2,y2 = self.Rotn(x2,y2,XScale,YScale,Angle)
                    self.segID.append( self.PreviewCanvas.create_line(
                        150+x1/PlotScale, 150-y1/PlotScale,150+x2/PlotScale, 150-y2/PlotScale,
                        fill = 'black', width = 1))

                # move over for next character
                char_width = font[char].get_xmax()
                xoffset += font_char_space + char_width

            except KeyError:
               self.gcode.append("(warning: character '0x%02X' not found in font defn)" % ord(char))

            self.gcode.append("")       # blank line after every char block

        self.gcode.append( 'G0 Z#1000')     # final engraver up

        # finish up with icing
        self.gcode.append(self.PostambleVar.get())


app = Application()
app.master.title("engrave-"+version+".py by Lawrence Glaister ")
app.mainloop()





