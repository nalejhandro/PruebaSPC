#!/bin/bash

path=$(readlink -e $1)
read -r -d '' appsscript << EOM
{
  "timeZone": "America/Costa_Rica",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER"
}
EOM
read -r -d '' code << EOM
//BC Version 32 / 2018-11-20
EOM

thread_count=8
declare -a pids
declare -a ids
retries_clasp=10
sleep_clasp=0.5
sleep_pid=0.5

clasp_clone() {
	local id=$1
	#Clone project
	echo "$id: cloning"
	local count=0
	while [ $count -lt $retries_clasp ]; do
		clasp clone $id 1>/dev/null
		#Clasp error
		if [ $? -ne 0 ]; then
			((count++))
			if [ $count -lt $retries_clasp ]; then
				echo "$id: Claps clone error, retrying $count/$retries_clasp"
				sleep $sleep_clasp
				#Delete all partially cloned files
				find . -name '*.js*' -delete
			else
				echo "$id: Clasp clone error, tries $retries_clasp exiting."
				return 1
			fi
		else
			return 0
		fi
	done
	return 1
}

clasp_push() {
	local id=$1
	#Push project
	echo "$id: pushing"
	local count=0
	while [ $count -lt $retries_clasp ]; do
		clasp push 1>/dev/null
		#Clasp error
		if [ $? -ne 0 ]; then
			((count++))
			if [ $count -lt $retries_clasp ]; then
				echo "$id: Claps push error, retrying $count/$retries_clasp"
				sleep $sleep_clasp
			else
				echo "$id: Clasp push error, tries $retries_clasp exiting."
				return 1
			fi
		else
			return 0
		fi
	done
	return 1
}

update_id() {
	#Clean id
	local id=$(echo $1 | tr -d '\n' | tr -d '\r')
	echo "$id: starting"
	local error=false
	
	#Make working dir
	if [ -d "$id" ]; then
		rm -r $id
	fi
	mkdir $id
	cd $id
	
	clasp_clone $id
	#Clasp error
	if [ $? -ne 0 ]; then
		error=true
	fi
	
	#Test if other files found.
	if [ $(ls -a -I . -I .. -I appsscript.json -I .clasp.json -I Código.js -I Code.js | wc -l) -ne 0 ]; then
		echo "$id: More files than necessary found, exiting."
		error=true
	fi
	
	push=false
	
	if [ "$error" = false ]; then
		if [ ! -f appsscript.json ]; then
			echo "$id: appsscript,json does not exist. Exiting."
			error=true
		elif [[ "$(cat appsscript.json)" != "$appsscript" ]]; then
			echo "$id: appsscript.json differ, updating."
			echo "$appsscript" > appsscript.json
			push=true
		else
			echo "$id: appsscript.json is up-to-date, skipping."
		fi
	fi
	
	if [ "$error" = false ]; then
		if [ ! -f Code.js ]; then
			echo "$id: Code.js not found, creating it."
			echo "$code" > Code.js
			push=true
		elif [[ "$(cat Code.js)" != "$code" ]]; then
			echo "$id: Code.js differ, updating."
			echo "$code" > Code.js
			push=true
		else
			echo "$id: Code.js is up-to-date, skipping."
		fi
	fi
	
	if [ "$error" = false ]; then
		if [ -f Código.js ]; then
			echo "$id: Código.js found, deleting it."
			rm Código.js
			push=true
		fi
	fi
	
	#Push if necessary
	if [[ ( "$error" = false ) && ( "$push" = true ) ]]; then
		echo "$id: pushing changes"
		clasp_push 1>/dev/null
		#Clasp error
		if [ $? -ne 0 ]; then
			error=true
		fi
	fi
	
	cd ..
	rm -r $id
	
	#Pop the line from the file if no error found.
	if [ "$error" = false ]; then
		echo "$id: done"
		sed -i "/$id/d" $path
	else
		echo "$id: ERROR -- ERROR -- ERROR -- ERROR -- ERROR -- ERROR"
		touch .error.tmp
	fi
}

process_ids() {
	while [ ${#ids[@]} -ne 0 ] || [ ${#pids[@]} -ne 0 ]; do
		# Check if any PID has finished to free the slot.
		local range=$(eval echo {0..$((${#pids[@]}-1))})
		local i
		for i in $range; do
			if [ ${#pids[@]} -ne 0 ] && ! ps -p ${pids[$i]} > /dev/null; then
				unset pids[$i]
			fi
		done
		pids=("${pids[@]}") # Expunge nulls created by unset.

		# Check if there are slots available and ids to process to fill the slot.
		if [ ${#pids[@]} -lt $thread_count ] && [ ${#ids[@]} -ne 0 ]; then
			#sleep $[ ( $RANDOM % 10 )  + 6 ]s &
			update_id ${ids[0]} &
			pids+=($!)
			unset ids[0]
			ids=("${ids[@]}") # Expunge null created by unset.
		fi
		sleep $sleep_pid
	done
}


#Create backup of the original file
cp --backup=t $path ${path}.bak

if [ -f .error.tmp ]; then
	rm .error.tmp
fi
readarray ids < $path
process_ids
if [ ! -f .error.tmp ]; then
	echo "Process finished OK. All ids processed."
	mv ${path}.bak $path
else
	echo "Process error. ids with errors are left in $path. Original file in ${path}.bak."
	rm .error.tmp
fi
