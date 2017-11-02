#!/bin/sh


cd_to_current_script_location()
{
    current_script_location="$(dirname "$0")"
    cd "$current_script_location"
}

clean()
{
    rm -rfv build/ dist/
}

build()
{
    python setup.py sdist bdist_wheel
}

sign()
{
    for file in dist/*
    do
        gpg --detach-sign --armor "$file"
    done
}

publish()
{
    twine upload dist/*
}


cd_to_current_script_location
clean
build
sign
publish
