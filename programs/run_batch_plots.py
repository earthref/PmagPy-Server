#!/usr/bin/env python
# Nick Jarboe
import sys,os
import pmagpy.pmag as pmag
import datetime


def main():
    """
    NAME
        run_batch_plots.py

    DESCRIPTION
        Used only the MagIC pmagpy plot sever. It will create a tmp directory in the location where it is run. 
        Downloads all activated MagIC data files from S3 and then creates plots using make_magic_plots.
        Plots are uploaded to the S3 MagIC server and copied the local webserver for easy web access for debugging.
        Skips files in the bad_files list that have data formatting or missing data issues.

    SYNTAX
        run_batch_plots.py [command line options]

    OPTIONS
        -out [FILENAME] redirect stdout to this file. File will be appended to.

    OUTPUT:

    EXAMPLE:
        run_batch_plots.py

    """
    badFiles=[11773, 11846, 14019, 14127, 14290, 14575, 15417, 15454, 15454, 15736, 15640, 16072, 16273, 16320, 16338, 16410, 16416, 16418, 16497, 16501, 13742, 16279, 16426, 15444, 16335, 15349, 15897, 16240, 16619, 16450, 16308, 16501, 16238, 16291, 16497, 16515, 13709, 14359, 16334, 15890, 16452, 16358, 11943, 14868, 12450, 16609, 16263, 16273, 16505, 11881, 15221, 14614, 16416, 11189, 16269, 14575, 16421, 11883, 16353, 11821, 16301, 15435, 16508, 16280, 16305, 12638, 16258, 16237, 16233, 14891, 16410, 15551, 11906, 13538, 16624, 16411, 16529, 16313, 15803, 15040, 14384, 16626, 15461, 15085, 11773, 11929, 11846, 13969, 16618, 16623, 11189, 13727, 14809, 16457, 16015, 15283, 15840, 16458, 16460, 16277]

    startTime=datetime.datetime.now() 
    if '-h' in sys.argv: # check if help is needed
        print(main.__doc__)
        sys.exit() # graceful quit
    if '-out' in sys.argv:
        ind=sys.argv.index('-out')
        logFile=int(sys.argv[ind+1])
        f = open(logFile, "a")
    else:
        f = sys.stdout

# Create tmp directory and copy MagIC files from S3
    print("start:", startTime)
    os.system('rm -r tmp')
    command="aws s3 cp s3://test-magic tmp --recursive" 
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    os.chdir("tmp")
    fileList=os.listdir()
    print('file_list=', fileList)
    print("badFiles=", badFiles)
    for magicDir in fileList:
        if int(magicDir) in badFiles:
            print("Bad file ", magicDir, "- skipping")
        else:
            os.chdir(magicDir)
            magicFile=os.listdir()
            magicFile=magicFile[0]
            command="download_magic.py -f " + magicFile 
            printout= command + "\n"
            f.write(printout)
            os.system(command)
            os.system("make_magic_plots.py")
            os.chdir("..")
            os.system("cp -r " + magicDir + " /var/www/html/plots/")
            os.system("cp " + magicDir + "/errors.txt .") 
            os.system("cp " + magicDir + "/contribution.txt .")
            os.system("rm " + magicDir + "/*.txt")
            os.system("mv errors.txt " + magicDir)
            os.system("mv contribution.txt " + magicDir)
            command="aws s3 rm s3://magic-plots/" + magicDir + " --recursive"
            printout= command + "\n"
            f.write(printout)
            os.system(command)
            command="aws s3 cp " + magicDir + " s3://magic-plots/" + magicDir + " --recursive"
            printout= command + "\n"
            f.write(printout)
            os.system(command)
    fileList=os.listdir()
    print('file_list=', fileList)

    endTime=datetime.datetime.now() 
    print("end:",endTime)

    exit()



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

        command='aws s3api list-objects --bucket "magic-contributions" --query' +" 'Contents[?LastModified>=`" + pastTime.isoformat() + "`][].{Key: Key, LastModified: LastModified}' > fileList" 
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
                    command='aws s3 cp s3://magic-contributions/' + fileName +' ' + fileName
                    printout="command=" + command + "\n"
                    f.write(printout)
                    os.system(command)
                    splitline=fileName.split('/')
                    magicId=splitline[0]
                    # clear the bucket for Website "Making Plots" display purposes
                    command='aws s3 mb s3://magic-plots/' +magicId  
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
                    command='aws s3 rm s3://magic-plots/' +magicId + ' --recursive' 
                    f.write(command+'\n')
                    os.system(command) 
                    command='aws s3 cp ' + magicId + ' s3://magic-plots/' +magicId + ' --recursive --include "*.png"'
                    f.write(command+'\n')
                    os.system(command) 
                    command='aws s3 cp ' + magicId + ' s3://magic-plots/' +magicId + ' --recursive --include "contributions.txt" --include "errors.txt"' 
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
                    printout="Warning: make_magic_plots took longer to run than the wait time.\n"
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
