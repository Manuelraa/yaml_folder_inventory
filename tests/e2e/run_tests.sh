#!/usr/bin/env bash
set -e

for folder in $(find -maxdepth 1 -type d -not -name '.'); do
    echo -n "Testing: $folder -> "
    # 'ungrouped' key was added in 2.8
    # Its always empty for our tests so just remove it
    ansible-inventory --list -i "$folder/inventory/yaml_folder.yml" | jq --sort-keys 'del(.ungrouped)' > result.json
    diff <(jq --sort-keys . "$folder/expected.json") result.json
    if [[ $? -eq 0 ]]; then
        echo "Success"
    else
        echo "Failed"
        exit $?
    fi
done
