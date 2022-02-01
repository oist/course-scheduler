FILE=$3
WARNING=`echo $FILE | sed s/schedule.csv/warnings.txt/` 
PDF=`echo $FILE | sed s/.csv/_GS.pdf/` 

/usr/local/bin/python3 Scheduler.py $1 $2 $3 > /dev/null 

echo "" 

cat $WARNING 

echo "" 

open $PDF 
