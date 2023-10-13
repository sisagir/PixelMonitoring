#!/bin/csh

set datestart_=`date -d 2023-9-1 +%s`
set datefinish_=`date -d 2023-10-12 +%s`
set step_=86400
set period_=`echo ${datestart_} ${datefinish_} ${step_} | awk '{printf "%.0f",($2-$1)/$3}'`
set counter_=0
if (-e list.log )then
mv list.log .list.log
endif
touch list.log
set endWhile_ = `echo $period_ + 1 | bc`
while ($counter_ < $endWhile_)
    @ time_ = ${datestart_} + ${step_} * (${counter_} + 1)
    set thisrun_=`date -u --date "1970-01-01 ${time_} sec GMT" +%Y-%m-%d`
    echo "${thisrun_}_lumi.txt" >> list.log
    @ counter_++
end

#set dates_=`cat list.log | awk -F"_lumi" '{print $1}' | sed 's/202/2/g'`
set dates_=`cat list.log | awk -F"_lumi" '{print $1}'`

foreach d_(${dates_})

	set checkExistingFile_=`echo "data_lumi/"${d_}"_lumi.txt"`    
	if ( -e ${checkExistingFile_} ) then
	echo "File: "$checkExistingFile_" exits! I will not overwrite! Continuing ..."
	continue
	endif

	#set y_=`echo ${d_} | awk -F"-" '{print $1}'`
	set y_=`echo ${d_} | awk -F"-" '{print $1}' | sed 's/202/2/g'`
	set m_=`echo ${d_} | awk -F"-" '{print $2}'`
	set d_=`echo ${d_} | awk -F"-" '{print $3}'`

	if ( -e data_lumi/20${y_}-${m_}-${d_}_lumi.txt ) then
	rm data_lumi/20${y_}-${m_}-${d_}_lumi.txt
	endif

	#echo "CUMULATIVE_LUMI" >& lumi/20${y_}-${m_}-${d_}_lumi.txt

	echo "brilcalc lumi --begin ${m_}/${d_}/${y_} 00:00:00 --end ${m_}/${d_}/${y_} 23:59:59"

	brilcalc lumi --begin "${m_}/${d_}/${y_} 00:00:00" --end "${m_}/${d_}/${y_} 23:59:59"  >> data_lumi/20${y_}-${m_}-${d_}_lumi.txt

end
