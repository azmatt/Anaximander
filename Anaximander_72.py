# Anaximander v20190819
# Python 3.7.x
# Written by Matt Edmondson
# Thanks to Ed Michael & Douglas Kein
# Modified to Python 3.7x and other things by Micah "WebBreacher" Hoffman

from xml.dom import minidom
import sqlite3
import os
import optparse
import signal
import sys

#### Functions
def keyboardInterruptHandler(signal, frame):
    # Capture Ctrl-C and finalize the KML before we leave to capture whatever content we have in there
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    closeKml()
    exit(0)

def closeKml():
    #### Finalizing and Closing KML
    z.write("</Document>\n")
    z.write("</kml>\n")
    z.close()
    print("[+] Finished generating the KML file\n")

#### Forces input of xml file
parser = optparse.OptionParser('correct usage is: Anaximander.py -t' + ' CellebriteTowers.xml')
parser.add_option('-t', dest='targetpage', type='string', help='Specify the Cellebrite cellphone tower XML output file')
(options, args) = parser.parse_args()
tgtFile = options.targetpage
if (tgtFile == None):
    print(parser.usage)
    sys.exit(1)

#### Creates KML header
z = open('cellTowers.kml', 'w')
z.write("<?xml version='1.0' encoding='UTF-8'?>\n")
z.write("<kml xmlns='http://www.opengis.net/kml/2.2'>\n" )
z.write("<Document>\n")
z.write("<name>Cell Towers from Anaximander</name>\n")
z.write("<description>Automatically generated using Anaximander (https://github.com/azmatt/Anaximander)</description>\n")
# Use Pink Paddle icons for the points so they stand out in Google Earth
z.write("   <Style id='pinkPaddle'><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/pink-blank.png</href></Icon></IconStyle></Style>\n\n")

#### Open XML document using minidom parser
DOMTree = minidom.parse(tgtFile)
models = DOMTree.getElementsByTagName('model')

#### Open SQLite Database with Cell Tower Location Info
db = sqlite3.connect('cellTowers.sqlite')
cursor = db.cursor()

#### Start signal to wait for CTRL-C and finish gracefully
signal.signal(signal.SIGINT, keyboardInterruptHandler)

#### Find each record and cycle through them
for model in models:
    fields = model.getElementsByTagName('field')
    varModelId = model.attributes['id'].value
    for field in fields:
        #print(field.attributes['name'].value) #DEBUG
        if field.getAttribute("name") == "TimeStamp":
            varTimestampEle = field.getElementsByTagName('value')[0]
            varTimestamp = varTimestampEle.firstChild.data
        if field.getAttribute("name") == "Name":
            nameDataRaw = field.getElementsByTagName('value')[0]
            #print(nameDataRaw.firstChild.data) #DEBUG
            nameDatasplit = nameDataRaw.firstChild.data.splitlines()
            varCellTowerType = nameDatasplit[0]
            varMcc = nameDatasplit[1].split()[1]
            varMnc = nameDatasplit[2].split()[1]
            varLac = nameDatasplit[3].split()[1]
            varCid = nameDatasplit[4].split()[1]
            #print(varCellTowerType, varMcc, varMnc, varLac, varCid) #DEBUG
    print("[+] Extracted record (MCC: %s, MNC: %s, LAC: %s, CID: %s)" % (varMcc, varMnc, varLac, varCid))

    ### Search DB for Cell Tower Locations
    print("[+]    Searching DB for this record.")
    cursor.execute("select * from towers where mcc = '%s' and net = '%s' and area = '%s' and cell = '%s' limit 1" % (varMcc, varMnc, varLac, varCid))
    for row in cursor:
        try:
            varLon = row[6]
            varLat = row[7]
            print("[+]    Found: (Lon: %s, Lat: %s), Writing to KML." % (varLon, varLat))
            kml_contents = "<Placemark>\n<TimeStamp><when>"+ varTimestamp +"</when></TimeStamp><name>" + str(varTimestamp)+ "</name>\n<description><p><b>Cell ID:</b> " + varCid + "</p><p><b>Date:</b> " + varTimestamp + "</p></description>\n<Point>\n<coordinates>" + varLon + "," + varLat + ",0</coordinates>\n</Point>\n<styleUrl>#pinkPaddle</styleUrl></Placemark>\n"
            z.write(kml_contents)
        except Exception as e:
            print("\n[!!!]    Error (%s) with the following record (MCC: %s, MNC: %s, LAC: %s, CID: %s)\n" % (e, varMcc, varMnc, varLac, varCid))
cursor.close

closeKml()
print("[+] Script completed with %s Records Parsed" % len(models))