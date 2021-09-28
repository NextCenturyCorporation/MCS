#!/bin/bash

baseCmd="python scripts/run_human_input.py" 
unity="../ai2thor-devel/unity/build/mcs-kd-dev.x86_64"
unity=""

scene="docs/source/scenes/playroom.json"
outputFolder="playroom"
cmdFile="commandText.txt"

branch1="development"
branch2="MCS-409-SceneEventClass"




run_command() {
	config=$1
	configCmd=""
	echo $config
	if [ -n $config ]
	then
		configCmd="--config_file_path $config"
	else
		configCmd=""
	fi
	#echo $baseCmd
	##echo $unity
	##echo $configCmd
	#echo $scene
	cmd="$baseCmd $configCmd $unity $scene"
	echo $cmd
	$cmd < $cmdFile
}

run_diff() {
	rm SCENE_HISTORY/*
	inst=$2
	mkdir -p $inst
	dir1="$inst/test-branch1"
	dir2="$inst/test-branch2"
	#echo "dir1 = $dir1 $dir2"
	#sleep 3
	git checkout $branch1
	git status
	sleep 3
	run_command $1
	mkdir -p $dir1
	mv $outputFolder/* $dir1
	rm SCENE_HISTORY/temp.json
	mv SCENE_HISTORY/*.json SCENE_HISTORY/temp.json
	jq '.' SCENE_HISTORY/temp.json > $dir1/history.json

	rm SCENE_HISTORY/*
	git checkout $branch2
	git status
	sleep 3
	run_command $1
	mkdir -p $dir2
	mv $outputFolder/* $dir2
	rm SCENE_HISTORY/temp.json
	mv SCENE_HISTORY/*.json SCENE_HISTORY/temp.json
	jq '.' SCENE_HISTORY/temp.json > $dir2/history.json

	diff $dir1 $dir2 > $inst/diff-raw.txt
	diff $dir1 $dir2 | grep -v delta_time_millis | grep -v currentTime | grep -v timestamp | tee $inst/diff.txt
}

run_configs() {
	echo "$1"
	FILES=$1/*.ini
	for path in $FILES; do
		filename="$(basename -- $path)"
		run_diff $path test-$filename
	done
}

run_configs test-config


#run_diff scripts/kyle-test.ini "test-inst"
