FILE=$1
WARNING=`echo $FILE | sed s/schedule.csv/warnings.txt/` 
PDF=`echo $FILE | sed s/.csv/_GS.pdf/` 

python3 Scheduler.py $1 > /dev/null 

echo "" 

cat $WARNING 

echo "" 

open $PDF 
