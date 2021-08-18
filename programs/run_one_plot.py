#!/usr/bin/env python
# Nick Jarboe
import sys,os
import pmagpy.pmag as pmag
import datetime


def main():
    """
    NAME
        run_one_plot.py

    DESCRIPTION
        Used only on the MagIC pmagpy plot sever. It will create a tmp directory in the location where it is run. 
        Downloads one MagIC data file from S3 and then creates plots using make_magic_plots.
        Plots are uploaded to the S3 MagIC server and copied the local webserver for easy web access for debugging.

    SYNTAX
        run_one_plot.py [command line options]

    OPTIONS
        -mcn [MagIC contribution number] MagIC contribution number of the data file.  
        -out [FILENAME] redirect stdout to this file. File will be appended to.
        -sb  [BUCKETNAME] name of the AWS S3 bucket that has the magic datafiles in 
             it to make the plots from (source bucket).
             Default value - magic-contributions 
        -pb  [BUCKETNAME] name of the AWS S3 bucket to place the plots into (plot bucket).  
             Default value - magic-plots 

    OUTPUT:
        plots created put on S3 

    EXAMPLE:
        run_one_plot.py -mcn 16769

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
    elif len(sys.argv) == 2:
        mcn=sys.argv[1]
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
    print("")
    print("Is isServer set to 'True' in pmag_env/set_env.py?")
    isServer = input("Type 'n' or Ctrl-C to exit. Hit enter to continue.")
    if isServer == 'n' or isServer == 'N':
        sys.exit()


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
    command="make_magic_plots.py"
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    command="rm locations.txt sites.txt samples.txt speciments.txt measurements.txt ages.txt criteria.txt"
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    command="aws s3 rm s3://" + plotBucket + "/" + mcn + " --recursive"
    printout= command + "\n"
    f.write(printout)
    os.system(command)
    command="aws s3 cp " + "." + " s3://" + plotBucket + "/" + mcn + " --recursive"
    printout= command + "\n"
    f.write(printout)
    os.system(command)

    endTime=datetime.datetime.now() 
    print("")
    print("isServer must be set to 'True' in pmag_env/set_env.py to produce website plots.")
    print("This is a warning if you are running plots on your normal pmagpy install")
    print("end:",endTime)

if __name__ == "__main__":
    main()
