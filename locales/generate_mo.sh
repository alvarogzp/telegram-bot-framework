#!/bin/sh


cd_to_current_script_location()
{
    current_script_location="$(dirname "$0")"
    cd "$current_script_location"
}


clear_mo_files()
{
    for file in */LC_MESSAGES/*.mo
    do
        rm --verbose "$file"
    done
}

generate_mo_files()
{
    for file in */LC_MESSAGES/*.po
    do
        out_file="${file%.*}.mo"
        msgfmt "$file" --output-file="$out_file" --check --statistics --verbose
    done
}


cd_to_current_script_location

clear_mo_files
generate_mo_files
