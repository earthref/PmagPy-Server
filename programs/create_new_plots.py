#!/usr/bin/env python
import sys,os
import pmagpy.pmag as pmag
import datetime
from datetime import timedelta
import time as t

def main():
    """
    NAME
      create_new_plots.py

    DESCRIPTION
      Used on the MagIC pmagpy sever. Not for general use. 

      Queries the AWS S3 magic-contributions bucket for a list of files created since a number of seconds
      in the past specified by the user (-p option). Files in the new directory containing '.txt' are 
      processed by make_magic_plots.py to create plots for displaying on the MagIC website. People could
      also grab plot files from here. User can specify the time to wait between querries. When the -a flag 
      is set the program will use the command run time for the look-back time to reduce the likelyhood of 
      missing processing a file. The wait time is reduced by the length of time it took to make the plots. 
      After creating the plots locally, they are copied over to /var/www/html/plots for easy external access.

    SYNTAX
       create_new_plots.py [command line options]

    OPTIONS
       -p the time in seconds to check in the past for a new file to process. Default 35.
       -w the time in seconds to wait after processing before checking again. Default 30.
       -a add the time the last cycle took to run to the -p value so it is less likely files are missed.
       -pt [TYPE] set to either 'public' or 'private'. This determines if the program looks for and
           processes private contributions or public ones. Default 'public'.
       -out [FILENAME] redirect stdout to this file. File will be appended to.

    OUTPUT:
        plots files created in the /plots/[$MagIC_ID_number] of the MagIC contribution

    EXAMPLE:
        create_new_plots.py -p 65 -w 60
        will wait 60 seconds before checking AWS for new files and process any that were created
        less than 65 seconds ago.

        Nick Jarboe
    """
    past=35
    wait=30
    addTime=False
    commandLength = timedelta(seconds=1)
    startTime=datetime.datetime.now() 
    bucketName=''
    if '-h' in sys.argv: # check if help is needed
        print(main.__doc__)
        sys.exit() # graceful quit
    if '-p' in sys.argv:
        ind=sys.argv.index('-p')
        past=int(sys.argv[ind+1])
    if '-w' in sys.argv:
        ind=sys.argv.index('-w')
        wait=int(sys.argv[ind+1])
    if '-a' in sys.argv:
        addTime=True
    if '-out' in sys.argv:
        ind=sys.argv.index('-out')
        logFile=int(sys.argv[ind+1])
        f = open(logFile, "a")
    else:
        f = sys.stdout
    if '-pt' in sys.argv:
        ind=sys.argv.index('-pt')
        bucketName=''
        if sys.argv[ind+1] == 'private':
            bucketName='private-'
        elif sys.argv[ind+1] != 'public':
            print ('Unknown contribution type ',sys.argv[ind+1], '. "public" or "private" are acceptable types.')
    while(True):
        startTime=datetime.datetime.now() 
        d = timedelta(seconds=past)
        printout="startTime="+str(startTime) + "\n"
        f.write(printout)
        printout="commandLength=" + str(commandLength) +"\n"
        f.write(printout)
        pastTime=startTime
        if d < commandLength:
            pastTime=startTime-commandLength
            printout="Due to long processing time the look-back time has been extended to " +str(commandLength.total_seconds()) + " seconds" + "\n"
            f.write(printout)
        else:
            pastTime=startTime-d

        command='aws s3api list-objects --bucket "magic-' + bucketName +'contributions" --query' +" 'Contents[?LastModified>=`" + pastTime.isoformat() + "`][].{Key: Key, LastModified: LastModified}' > fileList" 
        printout="command=" + command + "\n"
        f.write(printout)
        os.system(command)
    
        fileList=open("fileList",'r')
        line=fileList.readline()
        f.write(line)
        while line!="":
            if "Key" in line:
                splitline=line.split('"')
                fileName=splitline[3]
                printout="fileName=" + fileName + "\n"
                f.write(printout)
                if ".txt" in fileName:
                    command='aws s3 cp s3://magic-' + bucketName + 'contributions/' + fileName +' ' + fileName
                    printout="command=" + command + "\n"
                    f.write(printout)
                    os.system(command)
                    splitline=fileName.split('/')
                    magicId=splitline[0]
                    # clear the bucket for Website "Making Plots" display purposes
                    command='aws s3 mb s3://magic-' + bucketName + 'plots/' +magicId  
                    f.write(command+'\n')
                    os.system(command) 
                    contribId=splitline[1]
                    os.chdir(magicId)
                    command='download_magic.py -f ' + contribId 
                    os.system(command)
                    os.system('make_magic_plots.py')
                    os.chdir('..')
                    command='rm -rf  /var/www/html/plots/' + magicId 
                    f.write(command+'\n')
                    os.system(command) 
                    command='cp -rf ' + magicId + ' /var/www/html/plots' 
                    f.write(command+'\n')
                    os.system(command) 
                    command='aws s3 rm s3://magic-' + bucketName + 'plots/' +magicId + ' --recursive' 
                    f.write(command+'\n')
                    os.system(command) 
                    command='aws s3 cp ' + magicId + ' s3://magic' + bucketName + '-plots/' +magicId + ' --recursive --include "*.png"'
                    f.write(command+'\n')
                    os.system(command) 
                    command='aws s3 cp ' + magicId + ' s3://magic' + bucketName + '-plots/' +magicId + ' --recursive --include "contributions.txt" --include "errors.txt"' 
                    f.write(command+'\n')
                    os.system(command) 
                    command='rm -r processed/' + magicId
                    f.write(command+'\n')
                    os.system(command) 
                    command='mv ' + magicId +' processed' 
                    f.write(command+'\n')
                    os.system(command) 
            line =fileList.readline()
            f.write(line)
        fileList.close()
        endTime=datetime.datetime.now() 
        commandLength=endTime-startTime
        if addTime:
            w=wait-commandLength.total_seconds()
            if w<0:
                    w=0
                    printout="Warning: new_make_magic_plots took longer to run than the wait time.\n"
                    printout=printout +"Checking S3 for new MagIC data files immediately.\n"
                    f.write(printout)
            printout = "\nsleep will be " +str(w)+ " seconds\n"
            f.write(printout)
            t.sleep(w)
        else:
            printout = "\nsleep will be " +str(wait)+ " seconds\n"
            f.write(printout)
            t.sleep(wait)
        if f != sys.stdout:
            f.close() 
#  end while

if __name__ == "__main__":
    main()
