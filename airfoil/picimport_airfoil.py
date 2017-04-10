#!/usr/bin/env python

import cStringIO # *much* faster than StringIO
import urllib

filename = []
f = open('airfoil_bilder.txt', 'r')
for line in f:
    ls=line.split(".")
    filename.append(ls[0])
f.close()
numb= len(filename)
print numb

url_gif = "http://www.ae.illinois.edu/m-selig/ads/afplots/"
url_dat = "http://www.ae.illinois.edu/m-selig/ads/coord/"
x = 0
for line in filename:
    file_name=str(url_dat)+str(line)+".dat"
    try:
        file =urllib.urlopen(file_name)
    except IOError:
        print 'cannot open', file_name
    else:
        inhalt = file.read() 
        file.close()
        name= "data/"+str(line)+".dat"
        f = open(name , 'w')
        f.write(inhalt)
        f.close()
        x=x+1
        print x

print "done"
