#/bin/bash
ansible-inventory --list -i inventory_testing/yaml_folder.yml > inventory_testing/parsed_tmp.json
ansible-inventory --list -i inventory/yaml_folder.yml > inventory/parsed_tmp.json
echo "=== Diff inventory/"
diff inventory/parsed.json inventory/parsed_tmp.json
echo "=== Diff inventory_testing/"
diff inventory_testing/parsed.json inventory_testing/parsed_tmp.json
rm inventory/parsed_tmp.json inventory_testing/parsed_tmp.json
