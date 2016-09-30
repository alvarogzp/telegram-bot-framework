#!/bin/sh

cd_to_current_script_location()
{
    current_script_location="$(dirname "$0")"
    cd "$current_script_location"
}

cd_to_current_script_location

for file in */LC_MESSAGES/*.po
do
    out_file="${file%.*}.mo"
    msgfmt "$file" --output-file="$out_file" --check --statistics --verbose
done
