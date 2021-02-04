module load jaspy/2.7
x=0
while [ $x -le 20 ]
do
    ./analysis_timeseries.py u-bb446 level1; 
    ./analysis_timeseries.py u-aw310 level1;

    ./analysis_timeseries.py u-by242 kmf  
    ./analysis_timeseries.py u-by242 fast;


    ./analysis_compare.py
    # rsync -av /home/users/ldemora/workspace/ukesm-validation/CompareReports2 /group_workspaces/jasmin4/esmeval/public/.
    rsync -av /home/users/ldemora/workspace/ukesm-validation/CompareReports2 /group_workspaces/jasmin4/esmeval/public/CompareReports/v2/.

    echo "sleeping" $x
    x=$(( $x + 1 ))
    sleep 20000;
done
