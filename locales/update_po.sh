#!/bin/sh


LOCALES_DIR="locales/"


cd_to_current_script_location()
{
    current_script_location="$(dirname "$0")"
    cd "$current_script_location"
}

cd_to_project_root()
{
    cd_to_current_script_location
    # hardcoded for now...
    cd ..
}


generate_pot_file()
{
    local domain="$1"
    local file="$2"
    xgettext "$file" --from-code=utf-8 --default-domain="$domain" --output="$domain.pot" --output-dir="$LOCALES_DIR"
}

generate_pot_files()
{
    generate_pot_file pole bot/action/extra/pole.py
}


cd_to_project_root

generate_pot_files
