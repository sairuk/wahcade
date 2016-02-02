#!/bin/bash

#run mess with all parameters passed to the script
#you need to change this to the name of (and possibly full path to) your MESS binary.

export SDL_VIDEODRIVER=x11
export SDL_NOMOUSE=1
cd ~

/usr/local/bin/messat "$@";

#get last parameter of script (should be the full path to the game!)
eval 'game=$'$#;

#determine the name of the game without the path and the file extension
#note: if the game doesn't have an extension, this will cause errors
#(this can probably be done more elegantly... :P
game2=$(echo $game | awk -F \/ '{ print $(NF) }\' | awk -F \. '{ print $(NF-1) }');

#go to the snapshot folder of the emulated console $1 if it exists
if [ -d "$HOME/emulators/snap/$1" ]; then

cd "$HOME/emulators/snap/$1";
#if [ ! -d "$HOME/emulators/snap/$1/renamed" ]; then
#mkdir "$HOME/emulators/snap/$1/renamed";
#fi

#find all unrenamed screenshots and rename them according to the game name
#note: before the first usage of this script, the folder should be empty. Otherwise, the existing screenshots will be wrongly attributed to the current game!
for i in *.png; do
#	echo Renaming and moving "$i" to "$HOME/.mess/snap/$1/screens/$game2".png;
	mv "$i" "$HOME/emulators/snap/$1/screens/$game2".png;
done

else echo "no screenshot folder";
fi
