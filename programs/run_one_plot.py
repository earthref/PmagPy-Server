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
        Downloads all one MagIC data files from S3 and then creates plots using new_make_magic_plots.
        Plots are uploaded to the S3 MagIC server and copied the local webserver for easy web access for debugging.
        Skips files in the bad_files list that have data formatting or missing data issues.

    SYNTAX
        run_batch_plots.py [command line options]

    OPTIONS
        -mcn [MagIC contribution number] MagIC contribution number of the data file.  
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

    if '-h' in sys.argv: # check if help is needed
        print(main.__doc__)
        sys.exit() # graceful quit
    if '-sb' in sys.argv:
        ind=sys.argv.index('-sb')
        sourceBucket=sys.argv[ind+1]
    else:
        sourceBucket="magic-contributions"
    if '-mcn' in sys.argv:
        ind=sys.argv.index('-mcn')
        mcn=sys.argv[ind+1]
    else:
        print("MagIC contribution number not specified. Use -mcn to specify")
        sys.exit() # graceful quit
    if '-pb' in sys.argv:
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

    startTime=datetime.datetime.now() 
    print("start:", startTime)

# Create tmp directory and copy MagIC files from S3
    magicFile="magic_contribution_" + mcn + ".txt" 
    command="aws s3 cp s3://" + sourceBucket + "/" + mcn + "/" + magicFile + " . "
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    command="download_magic.py -f " + magicFile 
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    os.system("new_make_magic_plots.py")
    os.system("rm locations.txt sites.txt samples.txt speciments.txt measurements.txt ages.txt criteria.txt")
    command="aws s3 rm s3://" + plotBucket + "/" + mcn + " --recursive"
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    command="aws s3 cp " + "." + " s3://" + plotBucket + "/" + mcn + " --recursive"
    printout= command + "\n"
    f.write(printout)
    os.system(command)

    endTime=datetime.datetime.now() 
    print("end:",endTime)

if __name__ == "__main__":
    main()
