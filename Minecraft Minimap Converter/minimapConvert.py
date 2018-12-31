#Author:    Darrick Ross
#Date:      12/30/18
#Note:      This was developed to convert minimap points in a REI's minimap
#               format into Voxel Map. This was specificly developed for
#               the purpose of converting minez minimap waypoints.


#===============================================================================
#                   Imports
#===============================================================================

import sys, getopt

#===============================================================================
#                   Arguments
#===============================================================================

shortDelim      = ":"
longEnd         = "="
shortPre        = "-"
longPre         = "--"

helpShort       = "h"
helpOpts        = (shortPre + helpShort)

eliteShort      = "e"
eliteLong       = "elite-file"
eliteOpts       = (shortPre + eliteShort, longPre + eliteLong)

dungeonShort    = "d"
dungeonLong     = "dungeon-file"
dungeonOpts     = (shortPre + dungeonShort, longPre + dungeonLong)

majorShort      = "M"
majorLong       = "major-file"
majorOpts       = (shortPre + majorShort, longPre + majorLong)

minorShort      = "m"
minorLong       = "minor-file"
minorOpts       = (shortPre + minorShort, longPre + minorLong)

nameShort       = "n"
nameLong        = "name"
nameOpts        = (shortPre + nameShort, longPre + nameLong)


shortOptionStr = (helpShort +
                    eliteShort + shortDelim +
                    dungeonShort + shortDelim +
                    majorShort + shortDelim +
                    minorShort + shortDelim +
                    nameShort + shortDelim
                )

longOptionList = [eliteLong + longEnd, dungeonLong + longEnd, majorLong + longEnd, minorLong + longEnd, nameLong + longEnd]

#===============================================================================
#                   Messages
#===============================================================================

standardHelp ="""
>>Python minimapConvert.py -h
gives this

>>Python minimapConvert.py -e <elite file path> -d <dungeon file>
would specify both the elite and dungeon waypoints file paths.

>>Python minimapConvert.py -M <major file path> -m <minor file path>
would specify both the major and minor waypoint file paths.

this can be combined to specify all 4 together
>>Python minimapConvert.py -e <fp1> -d <fp2> -M <fp3> -m <fp4>

and last you can specify the export file name with the -n tag
>>Python minimapConvert.py -n <name (does not include file extension)>

so a full command would look like,
>>Python minimapConvert.py -e <fp1> -d <fp2> -M <fp3> -m <fp4> -n <name>

"""

IOErrorOpenMessage ="""
There was a problem opening the {:s} file.
"""

IOErrorWritingMessage ="""
There was a problem writing to the file {:s}.
"""

IOErrorCloseMessage ="""
There was a problem closing the {:s} file.
"""

CleanExitMessage = """
Finished with no problems, Output: {:s}
"""

#===============================================================================
#                   Globals
#===============================================================================

_RESULTING_FILE = ""
_ELITE_FILE     = ""
_DUNGEON_FILE   = ""
_MAJOR_FILE     = ""
_MINOR_FILE     = ""

_OUTPUT_NAME    = "play.shotbow.net"
_EXTENSION      = ".points"     #change at your own risk

_RED    = 0
_GREEN  = 1
_BLUE   = 2

_ELITE_COLOR    = ("0.4980392","0.0","0.0")                 #~7F0000
_DUNGEON_COLOR  = ("1.0","0.5137254","0.0")                 #~FF8300
_MAJOR_COLOR    = ("0.4509803","0.7607843","0.9843137")     #~73C2FB
_MINOR_COLOR    = ("0.8549019","0.6470588","0.1254901")     #~DAA520

_ELITE_ICON     = "skull"
_DUNGEON_ICON   = "temple"
_MAJOR_ICON     = "house"
_MINOR_ICON     = "fish"

_WORLD          = "Minez"

_DIM_LIST       = "0#"

_PRE_FILE_STR   = """subworlds:Minez,Shotbow Hub,
oldNorthWorlds:
seeds:
"""

#===============================================================================
#                   Functions
#===============================================================================

def createLineStr(str, color, icon, world, dim):
    #input str format
    #<name>:<x>:<y>:<z>:<visable>:<color>

    #output str format (all one line, wrapped here for readability)
    #name:<name>,x:<x>,z:<z>,y:<y>,enabled:<visable>,red:{color[_RED]},
    #   green:{color[_GREEN]},blue:{color[_BLUE]},suffix:{icon},world:{world},
    #   dimensions:{dim}

    #color: tuple of size 3, holding doubles, [red, green, blue]

    #icon: str from list of _<name>_ICON or blank

    #world: the name of the world

    #dim: the dimensions this will show up in

    #start

    #split the input by ":"
    splitChar = ":"
    listOfSplitStrings = str.split(splitChar)

    #0: name
    #1: x
    #2: y
    #3: z
    #4: visable
    #5: color       (unused)

    #Build      name:<name>,
    resultStr = "name:"
    resultStr = resultStr + listOfSplitStrings[0]
    resultStr = resultStr + ","

    #Build      x:<x>,
    resultStr = resultStr + "x:"
    resultStr = resultStr + listOfSplitStrings[1]
    resultStr = resultStr + ","

    #Build      z:<z>,
    resultStr = resultStr + "z:"
    resultStr = resultStr + listOfSplitStrings[3]
    resultStr = resultStr + ","

    #Build      y:<y>,
    resultStr = resultStr + "y:"
    resultStr = resultStr + listOfSplitStrings[2]
    resultStr = resultStr + ","

    #Build      enabled:<visable>,
    resultStr = resultStr + "enabled:"
    resultStr = resultStr + listOfSplitStrings[4]
    resultStr = resultStr + ","

    #Build      red:{color[_RED]},
    resultStr = resultStr + "red:"
    resultStr = resultStr + color[_RED]
    resultStr = resultStr + ","

    #Build      green:{color[_GREEN]},
    resultStr = resultStr + "green:"
    resultStr = resultStr + color[_GREEN]
    resultStr = resultStr + ","

    #Build      blue:{color[_BLUE]},
    resultStr = resultStr + "blue:"
    resultStr = resultStr + color[_BLUE]
    resultStr = resultStr + ","

    #Build      suffix:{icon},
    resultStr = resultStr + "suffix:"
    resultStr = resultStr + icon
    resultStr = resultStr + ","

    #Build      world:{world},
    resultStr = resultStr + "world:"
    resultStr = resultStr + world
    resultStr = resultStr + ","

    #Build      dimensions:{dim}
    resultStr = resultStr + "dimensions:"
    resultStr = resultStr + dim

    #Finish Building

    return resultStr

def parseArg():
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv,shortOptionStr,longOptionList)
    except getopt.GetoptError:
        print("test.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in helpOpts:
            print(standardHelp)
            sys.exit(1)
        elif opt in eliteOpts:
            global _ELITE_FILE
            try:
                _ELITE_FILE = open(arg,"r")
            except IOError:
                print(IOErrorOpenMessage.format("Elite"))
                sys.exit(2)
        elif opt in dungeonOpts:
            global _DUNGEON_FILE
            try:
                _DUNGEON_FILE = open(arg,"r")
            except IOError:
                print(IOErrorOpenMessage.format("Dungeon"))
                sys.exit(2)
        elif opt in majorOpts:
            global _MAJOR_FILE
            try:
                _MAJOR_FILE = open(arg,"r")
            except IOError:
                print(IOErrorOpenMessage.format("Major"))
                sys.exit(2)
        elif opt in minorOpts:
            global _MINOR_FILE
            try:
                _MINOR_FILE = open(arg,"r")
            except IOError:
                print(IOErrorOpenMessage.format("Minor"))
                sys.exit(2)
        elif opt in nameOpts:
            global _OUTPUT_NAME
            arg = arg.strip().replace(" ","")
            _OUTPUT_NAME = arg

def dealWithFile(fileObj, resultingFile, color, icon, world, dim, fileName):
    #check that file is readable

    #Loop thru each line adding it to the new file
    for line in fileObj:
        newLine = createLineStr(line, color, icon, world, dim)
        try:
            resultingFile.write(newLine + "\n")
        except IOError:
            print(IOErrorOpenMessage.format(fileName))

def cleanUp():
    closeFile(_ELITE_FILE, "Elite")

    closeFile(_DUNGEON_FILE, "Dungeon")

    closeFile(_MINOR_FILE, "Major")

    closeFile(_MINOR_FILE, "Minor")

def closeFile(fileObj, name):
    try:
        fileObj.close()
    except IOError:
        print(IOErrorCloseMessage.format(name))

def writeMessage(fileObj, name, msg):
    try:
        fileObj.write(msg)
    except IOError:
        print(IOErrorWritingMessage.format(name))
        sys.exit(1)

#===============================================================================
#                   Main
#===============================================================================

def main():
    parseArg()      #Initializes args, and opens any files (files not provided)
                    #   will be empty strings ("").

    try:
        _RESULTING_FILE = open(_OUTPUT_NAME + _EXTENSION, "w")
    except IOError:
        print(IOErrorOpenMessage.format("Output"))
        sys.exit(2)

    writeMessage(_RESULTING_FILE, "Output", _PRE_FILE_STR)  #write the pretext

    if _ELITE_FILE != "":
        dealWithFile(_ELITE_FILE, _RESULTING_FILE, _ELITE_COLOR, _ELITE_ICON, _WORLD, _DIM_LIST, "Elite")

    if _DUNGEON_FILE != "":
        dealWithFile(_DUNGEON_FILE, _RESULTING_FILE, _DUNGEON_COLOR, _DUNGEON_ICON, _WORLD, _DIM_LIST, "Dungeon")

    if _MAJOR_FILE != "":
        dealWithFile(_MAJOR_FILE, _RESULTING_FILE, _MAJOR_COLOR, _MAJOR_ICON, _WORLD, _DIM_LIST, "Major")

    if _MINOR_FILE != "":
        dealWithFile(_MINOR_FILE, _RESULTING_FILE, _MINOR_COLOR, _MINOR_ICON, _WORLD, _DIM_LIST, "Minor")

    writeMessage(_RESULTING_FILE, "Output", "\n")       #add an endline

    #finish up...
    cleanUp()
    print(CleanExitMessage.format((_OUTPUT_NAME + _EXTENSION)))
    sys.exit(0)
#===============================================================================
#                   Start
#===============================================================================

if __name__ == "__main__":
   main()
