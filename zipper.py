# Simple script to zip all directories in the current folder.
# This is written in Python because I wanted an excuse to practice Python.
# I also shoved some statistics and such in at the end because I find that kind of thing interesting.

#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 
#This program is available under the MIT License:
#Copyright (c) 2026 David Albert

#Permission is hereby granted, free of charge, to any person obtaining a copy of this
#software and associated documentation files (the "Software"), to deal in the Software
#without restriction, including without limitation the rights to use, copy, modify, merge,
#publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
#to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or
#substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 


from pathlib import Path
import math
import shutil
import sys
import time


#Some functions we'll be using:
#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 

#Converts a number of bytes into a number of KB / MB / etc.
#Expects an integer and returns a string.
def convertBytesToString(numBytes):
    units = ["bytes", "KB", "MB", "GB", "TB"]
    pointer = 0
    
    #Condense this as much as is reasonable, within the bounds of the units I've decided to support.
    while pointer < len(units) and numBytes >= 1024:
        numBytes /= 1024
        pointer += 1
    
    ret = str(round(numBytes, 2)) + " " + units[pointer]
    
    return ret;
#End of convertBytesToString()


#Converts a number of seconds into a number of minutes / hours / days.
#seconds is expected to be a numeric number of seconds.
#precision is expected to be an integer.
#   Controls how many units are returned (0 is all)
#       ie: precision=2 means it might return something like "1 day, 2 hours" and omit the numer of minutes and seconds.
#Returns a string.
def convertSecondsToString(seconds, precision = 2):
    #I'm just going to hardcode this, since the steps between units vary and there are only a few of them.
    minutes = 0
    hours = 0
    days = 0
    
    #Parse this number and figure out what we're looking at.
    if seconds >= 60:
        minutes = math.floor(seconds / 60)
        seconds = seconds % 60
    
    if minutes >= 60:
        hours = math.floor(minutes / 60)
        minutes = minutes % 60
    
    if hours >= 24:
        days = math.floor(hours / 24)
        hours = hours % 24
    
    #We'll stop at days.
    
    #Round seconds to something reasonable.
    seconds = round(seconds, 2)
    
    ret = ""
    included = 0
    #Maybe include days.
    if days > 0:
        ret = str(days)+" day"
        if days > 1:
            ret += "s"
        
        #Is this the time to return?
        included += 1
        if precision > 0 and included >= precision:
            return ret
    
    #Maybe include hours.
    if hours > 0:
        if not ret == "":
            ret += ", "
        ret += str(hours)+" hour"
        if hours > 1:
            ret += "s"
        
        #Is this the time to return?
        included += 1
        if precision > 0 and included >= precision:
            return ret
    
    #Maybe include minutes.
    if minutes > 0:
        if not ret == "":
            ret += ", "
        ret += str(minutes)+" minute"
        if minutes > 1:
            ret += "s"
        
        #Is this the time to return?
        included += 1
        if precision > 0 and included >= precision:
            return ret
    
    #Maybe include seconds.
    if seconds > 0:
        if not ret == "":
            ret += ", "
        
        #Special case: treat seconds and fractions of seconds as two separate units.
        if precision == 0 or included + 2 <= precision:
            #We have enough room to include fractional seconds.
            ret += str(seconds)+" second"
        else:
            #We only have enough room to include whole seconds.
            ret += str(round(seconds))+" second"
        
        if seconds > 1:
            ret += "s"
    
    #If we get here, it's time to return.
    if ret == "":
        return "0 seconds"
    else:
        return ret
#End of convertSecondsToString()


#Prints some instructions to the user and then collects input until something valid is returned.
#   instructions can either be a string or a list of strings.
#   validInputs should be a list of strings.
#   makeLowercase should be boolean.
def getResponseFromUser(instructions, validInputs, makeLowercase = True):
    #We'll do some basic error checking to try to make peoples' lives a little easier before risking an infinite loop.
    #validInputs must be a list and must have at least one item in it.
    if not isinstance(validInputs, list):
        return False
    if len(validInputs) <= 0:
        return False
    
    #Make sure the instructions are in a standardized format so we can just blindly print them.
    if isinstance (instructions, str):
        instructions = [instructions]
    elif isinstance (instructions, list):
        #This is a list, but now we need to make sure that everything in it is a string.
        for line in instructions:
            if not isinstance (line, str):
                return False
        #If we get this far, it looks fine.
    else:
        return False
    
    while True:
        for line in instructions:
            print(line)
        response = input()
        if makeLowercase:
            response = response.lower()
        
        if response in validInputs:
            return response
        print("Invalid response.")
        print("")
#End of getResponseFromUser()


#Recursively checks the size of the specified folder.
def getSizeOfFolder(folderpath):
    size = 0
    folderToProcess = Path(folderpath)
    for item in folderToProcess.rglob("*"):
        if item.is_file() and not item.is_symlink():
            temp = item.stat().st_size
            size += temp
    
    return size
#End of getSizeOfFolder()


#Zips one folder and returns the number of seconds spent doing so.
#   foldername should be a string containing the name of the folder in question.
#       Yes, it -can- be something else, but it -should- be the folder's name for the overall program to work properly.
#   folderpath should be a string containing the path to the folder in question.
def zipFolder(foldername, folderpath):
    startTime = time.perf_counter()
    try:
        shutil.make_archive(foldername, "zip", folderpath)
        #Returns the filename created.
    except ValueError:
        #We were unable to zip this folder for some reason.
        return False
    endTime = time.perf_counter()
    return endTime - startTime
#End of zipFolder()



#Setting things up before the main event:
#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 

#Settings we might want to make configurable at some point:
#Controls the output level. True is more output and False is less.
verboseMode = False

#An approximate limit for how long the program is allowed to run.
#   At certain points, the program will check how long it's been running.
#   If it's been longer than maxExecutionTimeGoal seconds, the program will quit.
#   A limit of 0 seconds (or less) functions as no limit.
maxExecutionTimeGoal = 3600     #1 hour

#Tracking data for the maybe-interesting statistics we'll display upon completion.
foldersZipped = 0
foldersSkipped = 0
zippingTime = 0
fileSizeBefore = 0
fileSizeAfter = 0

currentFolder = str(Path(__file__).parent.resolve())
print("Scanning "+currentFolder+" for folders to zip...")

#First, we need to get a list of directories in this folder.
folderToProcess = Path(".")
folderNames = []
numConflicts = 0
for item in folderToProcess.iterdir():
    if item.is_dir():
        folderNames.append(item.name)
        if verboseMode: print("Found folder: " + item.name)
        
        #Check if there's already a zip file matching the name we expect for this folder.
        temp = Path(item.name+".zip")
        if temp.is_file():
            numConflicts += 1
    elif item.is_file():
        if verboseMode: print("Found file: " + item.name)
    else:
        print("Found unknown item: " + item.name)

print("")

#Check what the user wants us to do in the event a filename is already taken.
#Also give them the opportunity to quit without running.
response = getResponseFromUser(["This program will create zipped versions of each subfolder this directory.", \
                                "It currently contains "+str(len(folderNames))+" folders, and "+str(numConflicts)+" of them already have zip files with matching filenames.", \
                                "When there is a conflict, what would you like this program to do?", \
                                "Enter A to Ask about each conflict", \
                                "Enter O to Overwrite the existing file", \
                                "Enter S to Skip that folder", \
                                "Enter Q to Quit"], \
                                ["a", "o", "s", "q"])

#For when the zipped name of a folder already exists.
#We start by asking every time, with the option to always skip or always overwrite.
#Can be:
    #ask - asks the user what to do every time there's a conflict.
    #overwrite - blindly overwrites the existing file every time there's a conflict.
    #skip - skips zipping the folder every time there's a conflict.
onConflict = "ask"

if response == "a":
    onConflict = "ask"
    print("This program will ask what to do about each conflict.")
elif response == "o":
    onConflict = "overwrite"
    print("This program will overwrite the existing file for each conflict.")
elif response == "s":
    onConflict = "skip"
    print("This program will skip each folder with a conflict.")
elif response == "q":
    print("Quitting...")
    sys.exit(0)
else:
    print("Error: unknown response "+str(response)+", quitting.")
    sys.exit(1)

print("")

#The main loop where we zip things:
#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 
startTime = time.perf_counter()
#Loop through each of these folders.
for foldername in folderNames:
    #Check if we've been running for too long.
    elapsedTime = time.perf_counter() - startTime
    if maxExecutionTimeGoal > 0 and elapsedTime > maxExecutionTimeGoal:
        print("Program has now run for "+str(round(elapsedTime, 2))+" seconds, which is longer than the configured limit of "+str(maxExecutionTimeGoal)+" seconds.")
        print("Quitting early.")
        sys.exit(0)
    
    folderpath = currentFolder + "\\" + foldername
    createdZip = False
    
    #Make sure this folder is still there. The user might have moved it since we scanned this directory.
    folderPointer = Path(folderpath)
    if not folderPointer.is_dir():
        print("Warning: the folder"+foldername+" seems to have been moved. Skipping.")
        foldersSkipped += 1
        continue
    
    #We want to ask for the user's permission before overwriting anything.
    expectedZipPath = Path(folderpath+".zip")
    if expectedZipPath.is_dir() or expectedZipPath.is_file():
        #There's already something with the filename we expect the zip file will be given.
        if onConflict == "overwrite":
            #We've been told to overwrite all conflicts.
            print("Overwriting "+foldername+".zip...")
            temp = zipFolder(foldername, folderpath)
            if temp == False:
                #Zipping failed, just quit.
                print("Error: unable to zip folder "+foldername+", quitting.")
                sys.exit(1)
            zippingTime += temp
            foldersZipped += 1
            createdZip = True
        elif onConflict == "skip":
            #We've been told to skip all conflicts.
            print("Skipping "+foldername)
            foldersSkipped += 1
        elif onConflict == "ask":
            #We'll ask the user whether they want to overwrite this file or not.
            response = getResponseFromUser(["The folder "+foldername+" already has a zipped version, do you want to overwrite?", \
                                            "Enter Y for Yes", \
                                            "Enter O for Always Overwrite", \
                                            "Enter N for No", \
                                            "Enter S for Always Skip", \
                                            "Enter Q to Quit"], \
                                            ["y", "n", "o", "s", "q"])
            if response == "y":
                print("Overwriting "+foldername+".zip...")
                temp = zipFolder(foldername, folderpath)
                if temp == False:
                    #Zipping failed, just quit.
                    print("Error: unable to zip folder "+foldername+", quitting.")
                    sys.exit(1)
                zippingTime += temp
                foldersZipped += 1
                createdZip = True
            elif response == "o":
                onConflict = "overwrite"
                print("Overwriting "+foldername+".zip and all future conflicts...")
                temp = zipFolder(foldername, folderpath)
                if temp == False:
                    #Zipping failed, just quit.
                    print("Error: unable to zip folder "+foldername+", quitting.")
                    sys.exit(1)
                zippingTime += temp
                foldersZipped += 1
                createdZip = True
            elif response == "n":
                print("Skipping "+foldername)
                foldersSkipped += 1
            elif response == "s":
                onConflict = "skip"
                print("Skipping "+foldername+" and all future conflicts.")
                foldersSkipped += 1
            elif response == "q":
                print("Quitting early.")
                sys.exit(0)
            elif response == False:
                #We failed to get a valid response from this, so we'll default to skipping.
                print("Error: unable to read response from user, skipping folder.")
                foldersSkipped += 1
            else:
                #This shouldn't be possible, but we'll check for it just in case.
                print("Error: received unknown response "+str(response))
                foldersSkipped += 1
        else:
            #onConflict is in an unsupported state.
            #We don't know what happened, so we'll just quit.
            print("Error: conflict resolution choice is set to "+onConflict)
            sys.exit(1)
    else:
        #There's no file conflict, we can just zip the thing.
        print("Creating "+foldername+".zip...")
        temp = zipFolder(foldername, folderpath)
        if temp == False:
            #Zipping failed, just quit.
            print("Error: unable to zip folder "+foldername+", quitting.")
            sys.exit(1)
        zippingTime += temp
        foldersZipped += 1
        createdZip = True
    
    #Check how much space we saved, if we created a zip of this folder:
    if createdZip:
        beforeSize = getSizeOfFolder(folderpath)
        if not expectedZipPath.is_file():
            #Either it wasn't created or it was given a different name than we expect.
            #We don't know what's going on, so we'll just quit.
            print("Error: zip file "+foldername+".zip not found.")
            sys.exit(1)
        afterSize = expectedZipPath.stat().st_size
        
        fileSizeBefore += beforeSize
        fileSizeAfter += afterSize
        
        if beforeSize > afterSize:
            if verboseMode: print("Reduced "+foldername+" from "+convertBytesToString(beforeSize)+" to "+convertBytesToString(afterSize)+".");
        elif beforeSize == afterSize:
            if verboseMode: print("Did not change size of folder.")
        else:
            if verboseMode: print("Increased "+foldername+" from "+convertBytesToString(beforeSize)+" to "+convertBytesToString(afterSize)+". Is it empty?");
#End of loop for each folder found.
endTime = time.perf_counter()


#Calculate and output some maybe-interesting statistics.
#-------- -------- -------- -------- -------- -------- -------- -------- -------- -------- 
print("")
print("Some maybe-interesting statistics, in case you care:")

elapsedTime = endTime - startTime
print("The program ran for approximately "+convertSecondsToString(elapsedTime)+", zipped "+str(foldersZipped)+" folders, and skipped "+str(foldersSkipped)+" folders.")
if foldersZipped > 0:
    print("  That's an average of about "+convertSecondsToString(elapsedTime / foldersZipped)+" per folder zipped.")

if zippingTime == 0:
    print("Total time spent zipping was exactly 0 seconds.")
else:
    print("Total time spent zipping was approximately "+convertSecondsToString(zippingTime)+".")
if foldersZipped > 0:
    print("  That's an average of about "+convertSecondsToString(zippingTime / foldersZipped)+" per folder.")

if fileSizeBefore > fileSizeAfter:
    print("Decreased the total file size from "+convertBytesToString(fileSizeBefore)+" to "+convertBytesToString(fileSizeAfter))
    print("  That's a savings of "+convertBytesToString(fileSizeBefore - fileSizeAfter))
    print("  The zipped files are "+str(round(100 * fileSizeAfter / fileSizeBefore,2))+"% of the original folders' size.")
elif fileSizeBefore == fileSizeAfter:
    print("File size stayed at "+convertBytesToString(fileSizeBefore))
else:
    print("Increased the total file size from "+convertBytesToString(fileSizeBefore)+" to "+convertBytesToString(fileSizeAfter))
    print("  That's an increase of "+convertBytesToString(fileSizeAfter - fileSizeBefore))
    print("  The zipped files are "+str(round(100 * fileSizeAfter / fileSizeBefore,2))+"% of the original folders' size.")


#We're done, but we want to give the user time to read the output before we risk closing the window.
print("Press enter to close.")
input()
