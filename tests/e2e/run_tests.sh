#!/usr/bin/env bash
set -e

# Random result file for parallel runs
result_file="result-$RANDOM.json"

# Since ansible 2.8 in the output empty objects are removed. We need two diffrent expected results...
ansible_version=$(pip list 2>/dev/null | grep "ansible " | tr  -s ' ' | cut -d ' ' -f 2)
if [[ "$ansible_version" == "2.5"* || "$ansible_version" == "2.6"* || "$ansible_version" == "2.7"* ]]; then
    expected_file='old-expected.json'
else
    expected_file='expected.json'
fi

# Output version info (Output contains ansible and python version)
echo "====Versions==="
ansible-inventory --version
echo "==============="

# Loop over all e2e tests
for folder in $(find -maxdepth 1 -type d -not -name '.'); do
    # Get result
    echo "Testing: $folder"
    ansible-inventory --list -i "$folder/inventory/yaml_folder.yml" | jq --sort-keys '.' > "$result_file"

    # Get possible diff (Expected: No diff)
    echo "Diff < expected -- result >"
    diff <(jq --sort-keys '.' "$folder/$expected_file") "$result_file"
    diff_exit_code=$?

    # Clean result
    rm "$result_file"

    # Decide if all was correct
    if [[ $diff_exit_code -eq 0 ]]; then
        echo "Success"
    else
        echo "Failed"
        exit $?
    fi
done
