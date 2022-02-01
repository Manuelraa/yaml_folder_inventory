#!/usr/bin/env bash
set -e

# Since ansible 2.8 in the output empty objects are removed
ansible_version=$(pip list 2>/dev/null | grep "ansible " | tr  -s ' ' | cut -d ' ' -f 2)
if [[ "$ansible_version" == "2.5."* || "$ansible_version" == "2.6."* || "$ansible_version" == "2.7."* ]]; then
    expected_file='old-expected.json'
else
    expected_file='expected.json'
fi

for folder in $(find -maxdepth 1 -type d -not -name '.'); do
    echo "Testing: $folder"
    # 'ungrouped' key was added in 2.8
    # Its always empty for our tests so just remove it
    ansible-inventory --list -i "$folder/inventory/yaml_folder.yml" | jq --sort-keys '.' > result.json
    echo "Diff < expected -- result >"
    diff <(jq --sort-keys '.' "$folder/$expected_file") result.json
    diff_exit_code=$?
    rm result.json
    if [[ $diff_exit_code -eq 0 ]]; then
        echo "Success"
    else
        echo "Failed"
        exit $?
    fi
done
