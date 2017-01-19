#!/usr/bin/python

"""
    engrave-lines.py G-Code Engraving Generator for command-line usage
    (C) ArcEye <2012>  <arceye at mgware dot co dot uk>
    syntax  ---   see helpfile below
    
    Allows the generation of multiple lines of engraved text in one go
    Will take each string arguement, apply X and Y offset generating code until last line done
    
  
    based upon code from engrave-11.py
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
    Rev v2 21.06.2012 ArcEye
"""
# change this if you want to use another font
fontfile = "/usr/share/qcad/fonts/romanc.cxf"

from Tkinter import *
from math import *
import os
import re
import sys
import string
import getopt

String =   ""
SafeZ =    2
XStart =   0
XLineOffset =   0
XIndentList = ""
YStart = 0
YLineOffset = 0
Depth =    0.1
XScale =   1
YScale =   1
CSpaceP =  25
WSpaceP=   100
Angle =    0
Mirror = 0
Flip = 0
Preamble = "G17 G21 G40 G90 G64 P0.003 F50"
Postamble = "M2"

stringlist = []

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

def __init__(key):
    key = key
    stroke_list = []

def __repr__():
    return "%s" % (stroke_list)

def get_xmax():
    try: return max([s.xmax for s in stroke_list[:]])
    except ValueError: return 0

def get_ymax():
    try: return max([s.ymax for s in stroke_list[:]])
    except ValueError: return 0



#=======================================================================


def __init__( coords):
    xstart, ystart, xend, yend = coords
    xmax = max(xstart, xend)
    ymax = max(ystart, yend)

def __repr__():
    return "Line([%s, %s, %s, %s])" % (xstart, ystart, xend, yend)


#=======================================================================
def sanitize(string):
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
def Rotn(x,y,xscale,yscale,angle):
    Deg2Rad = 2.0 * pi / 360.0
    xx = x * xscale
    yy = y * yscale
    rad = sqrt(xx * xx + yy * yy)
    theta = atan2(yy,xx)
    newx=rad * cos(theta + angle*Deg2Rad)
    newy=rad * sin(theta + angle*Deg2Rad)
    return newx,newy



#=======================================================================

def code(arg, visit, last):

    global SafeZ
    global XStart
    global XLineOffset
    global XIndentList
    global YStart
    global YLineOffset
    global Depth
    global XScale
    global YScale
    global CSpaceP
    global WSpaceP
    global Angle
    global Mirror
    global Flip
    global Preamble
    global Postamble
    global stringlist

    String = arg

    str1 = ""
    #erase old gcode as needed
    gcode = []
    
    file = open(fontfile)
  
    oldx = oldy = -99990.0      
    
                 
    if visit != 0:
        # all we need is new X and Y for subsequent lines
        gcode.append("(===================================================================)")
        gcode.append('( Engraving: "%s" )' %(String) )
        gcode.append('( Line %d )' %(visit))

        str1 = '#1002 = %.4f  ( X Start )' %(XStart)        
        if XLineOffset :
            if XIndentList.find(str(visit)) != -1 :
                str1 = '#1002 = %.4f  ( X Start )' %(XStart + XLineOffset)
            
        gcode.append(str1)
        gcode.append('#1003 = %.4f  ( Y Start )' %(YStart - (YLineOffset * visit)))
        gcode.append("(===================================================================)")
        
    else:
        gcode.append('( Line %d )' %(visit))
        gcode.append('( Code generated by engrave-lines.py )')
        gcode.append('( by ArcEye 2012, based on work by <Lawrence Glaister>)')
        gcode.append('( Engraving: "%s")' %(String) )
        gcode.append('( Fontfile: %s )' %(fontfile))
        # write out subroutine for rotation logic just once at head
        gcode.append("(===================================================================)")
        gcode.append("(Subroutine to handle x,y rotation about 0,0)")
        gcode.append("(input x,y get scaled, rotated then offset )")
        gcode.append("( [#1 = 0 or 1 for a G0 or G1 type of move], [#2=x], [#3=y])")
        gcode.append("o9000 sub")
        gcode.append("  #28 = [#2 * #1004]  ( scaled x )")
        gcode.append("  #29 = [#3 * #1005]  ( scaled y )")
        gcode.append("  #30 = [SQRT[#28 * #28 + #29 * #29 ]]   ( dist from 0 to x,y )")
        gcode.append("  #31 = [ATAN[#29]/[#28]]                ( direction to  x,y )")
        gcode.append("  #32 = [#30 * cos[#31 + #1006]]     ( rotated x )")
        gcode.append("  #33 = [#30 * sin[#31 + #1006]]     ( rotated y )")
        gcode.append("  o9010 if [#1 LT 0.5]" )
        gcode.append("    G00 X[#32+#1002] Y[#33+#1003]")
        gcode.append("  o9010 else")
        gcode.append("    G01 X[#32+#1002] Y[#33+#1003]")
        gcode.append("  o9010 endif")
        gcode.append("o9000 endsub")
        gcode.append("(===================================================================)")
    
        gcode.append("#1000 = %.4f" %(SafeZ))
        gcode.append('#1001 = %.4f  ( Engraving Depth Z )' %(Depth))
        
        str1 = '#1002 = %.4f  ( X Start )' %(XStart)        
        if XLineOffset :
            if XIndentList.find(str(visit)) != -1 :
                str1 = '#1002 = %.4f  ( X Start )' %(XStart + XLineOffset)
        gcode.append(str1)
        gcode.append('#1003 = %.4f  ( Y Start )' %(YStart))
        gcode.append('#1004 = %.4f  ( X Scale )' %(XScale))
        gcode.append('#1005 = %.4f  ( Y Scale )' %(YScale))
        gcode.append('#1006 = %.4f  ( Angle )' %(Angle))
        gcode.append(Preamble)
        
    gcode.append( 'G0 Z#1000')

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
            gcode.append("(character '%s')" % sanitize(char))

            first_stroke = True
            for stroke in font[char].stroke_list:
#               gcode.append("(%f,%f to %f,%f)" %(stroke.xstart,stroke.ystart,stroke.xend,stroke.yend ))
                dx = oldx - stroke.xstart
                dy = oldy - stroke.ystart
                dist = sqrt(dx*dx + dy*dy)

                x1 = stroke.xstart + xoffset
                y1 = stroke.ystart
                if Mirror == 1:
                    x1 = -x1
                if Flip == 1:
                    y1 = -y1

                # check and see if we need to move to a new discontinuous start point
                if (dist > 0.001) or first_stroke:
                    first_stroke = False
                    #lift engraver, rapid to start of stroke, drop tool
                    gcode.append("G0 Z#1000")
                    gcode.append('o9000 call [0] [%.4f] [%.4f]' %(x1,y1))
                    gcode.append("G1 Z#1001")

                x2 = stroke.xend + xoffset
                y2 = stroke.yend
                if Mirror == 1:
                    x2 = -x2
                if Flip == 1:
                    y2 = -y2
                gcode.append('o9000 call [1] [%.4f] [%.4f]' %(x2,y2))
                oldx, oldy = stroke.xend, stroke.yend

            # move over for next character
            char_width = font[char].get_xmax()
            xoffset += font_char_space + char_width

        except KeyError:
           gcode.append("(warning: character '0x%02X' not found in font defn)" % ord(char))

        gcode.append("")       # blank line after every char block

    gcode.append( 'G0 Z#1000')     # final engraver up

    # finish up with icing
    if last:
        gcode.append(Postamble)
  
    for line in gcode:
            sys.stdout.write(line+'\n')

################################################################################################################

def help_message():
    print '''engrave-lines.py G-Code Engraving Generator for command-line usage
            (C) ArcEye <2012> 
            based upon code from engrave-11.py
            Copyright (C) <2008>  <Lawrence Glaister> <ve7it at shaw dot ca>'''
            
    print '''engrave-lines.py -X -x -i -Y -y -S -s -Z -D -C -W -M -F -P -p -0 -1 -2 -3 ..............
       Options: 
       -h   Display this help message
       -X   Start X value                       Defaults to 0
       -x   X offset between lines              Defaults to 0
       -i   X indent line list                  String of lines to indent in single quotes
       -Y   Start Y value                       Defaults to 0
       -y   Y offset between lines              Defaults to 0
       -S   X Scale                             Defaults to 1
       -s   Y Scale                             Defaults to 1       
       -Z   Safe Z for moves                    Defaults to 2mm
       -D   Z depth for engraving               Defaults to 0.1mm
       -C   Charactor Space %                   Defaults to 25%
       -W   Word Space %                        Defaults to 100%
       -M   Mirror                              Defaults to 0 (No)
       -F   Flip                                Defaults to 0 (No)
       -P   Preamble g code                     Defaults to "G17 G21 G40 G90 G64 P0.003 F50"
       -p   Postamble g code                    Defaults to "M2"
       -0   Line0 string follow this
       -1   Line1 string follow this
       -2   Line2 string follow this        
       -3   Line3 string follow this
       -4   Line4 string follow this
       -5   Line5 string follow this
       -6   Line6 string follow this
       -7   Line7 string follow this                                
       -8   Line8 string follow this
       -9   Line9 string follow this
      Example
      engrave-lines.py -X7.5 -x5 -i'123' -Y12.75 -y5.25 -S0.4 -s0.5 -Z2 -D0.1 -0'Line0' -1'Line1' -2'Line2' -3'Line3' > test.ngc
    '''
    sys.exit(0)

#===============================================================================================================

def main():

    debug = 0
    # need to declare the globals because we want to write to them
    # otherwise python will create a local of the same name and
    # not change the global - stupid python
    global SafeZ
    global XStart
    global XLineOffset
    global XIndentList
    global YStart
    global YLineOffset
    global Depth
    global XScale
    global YScale
    global CSpaceP
    global WSpaceP
    global Angle
    global Mirror
    global Flip
    global Preamble
    global Postamble
    global stringlist
    
    try:
        options, xarguments = getopt.getopt(sys.argv[1:], 'hd:X:x:i:Y:y:S:s:Z:D:C:W:M:F:P:p:L:0:1:2:3:4:5:6:7:8:9:')
    except getopt.error:
        print 'Error: You tried to use an unknown option. Try `engrave-lines.py -h\' for more information.'
        sys.exit(0)
        
    if len(sys.argv[1:]) == 0:
        help_message()
        sys.exit(0)    
    
    for a in options[:]:
        if a[0] == '-h':
            help_message()
            sys.exit(0)
#  hidden debug option for testing            
    for a in options[:]:
        if a[0] == '-d' and a[1] != '':
            debug = int(a[1])
            print'debug set to %d' %(debug)
            options.remove(a)
            break

    for a in options[:]:
        if a[0] == '-X' and a[1] != '':
            XStart = float(a[1])
            if debug:            
                print'X = %.4f' %(XStart)
            options.remove(a)
            break

    for a in options[:]:
        if a[0] == '-x' and a[1] != '':
            XLineOffset = float(a[1])
            if debug:
                print'x = %.4f' %(XLineOffset)
            options.remove(a)
            break

    for a in options[:]:
        if a[0] == '-i' and a[1] != '':
            XIndentList = a[1]
            if debug:
                print'i = %s' %(a[1])
            options.remove(a)
            break
            
    for a in options[:]:
        if a[0] == '-Y' and a[1] != '':
            YStart = float(a[1])
            if debug:
                print'Y = %.4f' %(YStart)
            options.remove(a)
            break

    for a in options[:]:
        if a[0] == '-y' and a[1] != '':
            YLineOffset = float(a[1])
            if debug:
                print'y = %.4f' %(YLineOffset)
            options.remove(a)
            break
            
    for a in options[:]:
        if a[0] == '-S' and a[1] != '':
            XScale = float(a[1])
            if debug:
                print'S = %.4f' %(XScale)
            options.remove(a)
            break            
  
    for a in options[:]:
        if a[0] == '-s' and a[1] != '':
            YScale = float(a[1])
            if debug:
                print's = %.4f' %(YScale)
            options.remove(a)
            break              
  
    for a in options[:]:
        if a[0] == '-Z' and a[1] != '':
            SafeZ = float(a[1])
            if debug:
                print'Z = %.4f' %(SafeZ)
            options.remove(a)
            break  
  
    for a in options[:]:
        if a[0] == '-D' and a[1] != '':
            Depth = float(a[1])
            if debug:
                print'D = %.4f' %(Depth)
            options.remove(a)
            break    
  
    for a in options[:]:
        if a[0] == '-C' and a[1] != '':
            CSpaceP = float(a[1])
            if debug:
                print'C = %.4f' %(CSpaceP)
            options.remove(a)
            break      

    for a in options[:]:
        if a[0] == '-W' and a[1] != '':
            WSpaceP = float(a[1])    
            if debug:
                print'W = %.4f' %(WSpaceP)
            options.remove(a)
            break      

    for a in options[:]:
        if a[0] == '-A' and a[1] != '':
            Angle = float(a[1])
            if debug:
                print'A = %.4f' %(Angle)
            options.remove(a)
            break  
            
            
    for a in options[:]:
        if a[0] == '-M' and a[1] != '':
            Mirror = float(a[1])
            if debug:
                print'M = %.4f' %(Mirror)
            options.remove(a)
            break  
              
    for a in options[:]:
        if a[0] == '-F' and a[1] != '':
            Flip = float(a[1])
            if debug:
                print'F = %.4f' %(Flip)
            options.remove(a)
            break  

    for a in options[:]:
        if a[0] == '-P' and a[1] != '':
            Preamble = a[1]
            if debug:
                print'P = %s' %(a[1])
            options.remove(a)
            break  

    for a in options[:]:
        if a[0] == '-p' and a[1] != '':            
            Postamble = a[1]
            if debug:
                print'p = %s' %(a[1])
            options.remove(a)
            break  

    for a in options[:]:
        if a[0] == '-0' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'0 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-1' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'1 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-2' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'2 = %s' %(a[1])
            options.remove(a)
            break  

    for a in options[:]:
        if a[0] == '-3' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'3 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-4' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'4 = %s' %(a[1])
            options.remove(a)
            break  

    for a in options[:]:
        if a[0] == '-5' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'5 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-6' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'6 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-7' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'7 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-8' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'8 = %s' %(a[1])
            options.remove(a)
            break  
            
    for a in options[:]:
        if a[0] == '-9' and a[1] != '':
            stringlist.append(a[1])
            if debug:
                print'9 = %s' %(a[1])
            options.remove(a)
            break  
            
    for index, item in enumerate(stringlist):
        code(item,index, index == (len(stringlist) - 1) )
   
            
#===============================================================================================
            
if __name__ == "__main__":
	    main()

#===============================================================================================END
