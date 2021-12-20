#/bin/bash
ansible-inventory --list -i inventory_testing/yaml_folder.yml > inventory_testing/parsed.json
ansible-inventory --list -i inventory/yaml_folder.yml > inventory/parsed.json
