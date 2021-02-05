module load jaspy/2.7
x=0
#while [ 1 -eq 1 ];
while [ $x -le 20 ]
do
    # fast:
#    ./analysis_timeseries.py u-bz321 fast
#    ./analysis_timeseries.py u-bz360 fast
#    ./analysis_timeseries.py u-bz361 fast
#    ./analysis_timeseries.py u-bz362 fast
#    ./analysis_timeseries.py u-bz363 fast
#    ./analysis_timeseries.py u-bz364 fast
#    ./analysis_timeseries.py u-bz385 fast
#    ./analysis_timeseries.py u-bz393 fast
#    ./analysis_timeseries.py u-bz705 fast
#

    # UKESM1.1
    ./analysis_timeseries.py u-cb375 level1;
#    ./analysis_timeseries.py u-by791 level1;
#    ./analysis_timeseries.py u-bz502 level1;
#    ./analysis_timeseries.py u-bz897 level1;
#    ./analysis_timeseries.py u-ca306 level1;
    ./analysis_timeseries.py u-ca811 level1;

    ./analysis_timeseries.py u-by230 level1;
#    ./analysis_timeseries.py u-bx499 level1;
#    ./analysis_timeseries.py u-bw717 physics
    ./analysis_timeseries.py u-bx082 physics

#    ./analysis_timeseries.py u-bx188 level1;
    #./analysis_timeseries.py u-bw837 level1; 
#    ./analysis_timeseries.py u-bv936 level1; 
#    ./analysis_timeseries.py  u-bw462 level1;
    #./analysis_timeseries.py u-bv270 physics; 
    #/./analysis_timeseries.py u-bv334 level1; 
#    ./analysis_timeseries.py u-bu847 level1;
#    ./analysis_timeseries.py u-bu794 level1;
    #./analysis_timeseries.py u-bu737 level1; 
#    ./analysis_timeseries.py u-bu504 level1;
#     ./analysis_timeseries.py u-bg555 physics;
    ./analysis_timeseries.py u-ar766 physics; 
#/    ./analysis_timeseries.py u-bt931 level1;
#    ./analysis_timeseries.py u-bt670 physics
#/;    ./analysis_timeseries.py u-bt320 level1;
#    ./analysis_timeseries.py u-bt233 level1;
#    ./analysis_timeseries.py u-bt089 physics; 
#/    ./analysis_timeseries.py u-bk093 physics; 
#    ./analysis_timeseries.py u-bs733 physics; 
#    ./analysis_timeseries.py u-bs704 level1; 
#    ./analysis_timeseries.py u-bs522 level1; 

# These are in sci4_pi.sh
#    ./analysis_timeseries.py u-bb446 level1; 
#    ./analysis_timeseries.py u-aw310 level1;

    ./analysis_compare.py
    # rsync -av /home/users/ldemora/workspace/ukesm-validation/CompareReports2 /group_workspaces/jasmin4/esmeval/public/.
    #rsync -av /home/users/ldemora/workspace/ukesm-validation/CompareReports2 /group_workspaces/jasmin4/esmeval/public/CompareReports/v2/.
    rsync -av /home/users/ldemora/workspace/ukesm-validation/CompareReports2 /gws/nopw/j04/esmeval/public/CompareReports/v2/.
    echo "sleeping" $x
    x=$(( $x + 1 ))
    sleep 20000;
done
