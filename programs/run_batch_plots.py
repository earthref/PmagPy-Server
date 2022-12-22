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
        Downloads all activated MagIC data files from S3 and then creates plots using new_make_magic_plots.
        Plots are uploaded to the S3 MagIC server and copied the local webserver for easy web access for debugging.
        Skips files in the bad_files list that have data formatting or missing data issues.

    SYNTAX
        run_batch_plots.py [command line options]

    OPTIONS
        -out [FILENAME] redirect stdout to this file. File will be appended to.
        -sb [BUCKETNAME] name of the AWS S3 bucket that has the magic datafiles in it to make the plots from (source bucket).
                         Default value - magic-contributions 
        -pb [BUCKETNAME] name of the AWS S3 bucket to place the plots into (plot bucket).
                         Default value - magic-plots 

    OUTPUT:
        plots created to 
    EXAMPLE:
        run_batch_plots.py

    """
    badFiles=[11773, 11846, 14019, 14127, 14290, 14575, 15417, 15454, 15454, 15736, 15640, 16072, 16273, 16320, 16338, 16410, 16416, 16418, 16497, 16501, 13742, 16279, 16426, 15444, 16335, 15349, 15897, 16240, 16619, 16450, 16308, 16501, 16238, 16291, 16497, 16515, 13709, 14359, 16334, 15890, 16452, 16358, 11943, 14868, 12450, 16609, 16263, 16273, 16505, 11881, 15221, 14614, 16416, 11189, 16269, 14575, 16421, 11883, 16353, 11821, 16301, 15435, 16508, 16280, 16305, 12638, 16258, 16237, 16233, 14891, 16410, 15551, 11906, 13538, 16624, 16411, 16529, 16313, 15803, 15040, 14384, 16626, 15461, 15085, 11773, 11929, 11846, 13969, 16618, 16623, 11189, 13727, 14809, 16457, 16015, 15283, 15840, 16458, 16460, 16277, 16671, 19602, 19215, 17130, 17129, 17039, 17000]

# 16671, 19602, 19205, 17130, 17129, 17039, 17000 not bad, just very large with no plots available to be made, so skipped also

    startTime=datetime.datetime.now() 
    if '-h' in sys.argv: # check if help is needed
        print(main.__doc__)
        sys.exit() # graceful quit
    if '-sb' in sys.argv: # check if help is needed
        ind=sys.argv.index('-sb')
        sourceBucket=sys.argv[ind+1]
    else:
        sourceBucket="magic-contributions"
    if '-pb' in sys.argv: # check if help is needed
        ind=sys.argv.index('-pb')
        plotBucket=sys.argv[ind+1]
    else:
        plotBucket="magic-plots"
    if '-out' in sys.argv:
        ind=sys.argv.index('-out')
        logFile=int(sys.argv[ind+1])
        f = open(logFile, "a")
    else:
        f = sys.stdout

# Create tmp directory and copy MagIC files from S3
    print("start:", startTime)
    os.system('rm -r tmp')
    command="aws s3 cp s3://" + sourceBucket + " tmp --recursive" 
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
            os.system("new_make_magic_plots.py")
            os.chdir("..")
            os.system("cp -r " + magicDir + " /var/www/html/plots/")
            os.system("cp " + magicDir + "/errors.txt .") 
            os.system("cp " + magicDir + "/contribution.txt .")
            os.system("cp " + magicDir + "/images.txt .")
            os.system("rm " + magicDir + "/*.txt")
            os.system("mv errors.txt " + magicDir)
            os.system("mv contribution.txt " + magicDir)
            os.system("mv images.txt " + magicDir)
            command="aws s3 rm s3://" + plotBucket + "/" + magicDir + " --recursive"
            printout= command + "\n"
            f.write(printout)
            os.system(command)
            command="aws s3 cp " + magicDir + " s3://" + plotBucket + "/" + magicDir + " --recursive"
            printout= command + "\n"
            f.write(printout)
            os.system(command)
    fileList=os.listdir()
    print('file_list=', fileList)

    endTime=datetime.datetime.now() 
    print("end:",endTime)

if __name__ == "__main__":
    main()
