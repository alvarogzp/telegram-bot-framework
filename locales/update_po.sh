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

update_po_files()
{
    local domain="$1"
    local pot_path="$LOCALES_DIR/$domain.pot"
    for file in ${LOCALES_DIR}/*/LC_MESSAGES/${domain}.po
    do
        msgmerge --update --no-fuzzy-matching --verbose "$file" "$pot_path"
    done
}

generate_pot_file_and_update_po_files()
{
    local domain="$1"
    local file="$2"
    generate_pot_file "$domain" "$file"
    update_po_files "$domain"
}

generate_pot_and_update_po_files()
{
    generate_pot_file_and_update_po_files pole bot/action/extra/pole.py
}


cd_to_project_root

generate_pot_and_update_po_files
