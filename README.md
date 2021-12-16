# manuelraa.yaml_folder_inventory.yaml_folder
Ansible inventory plugin for better inventory structure

## Usage
```
> ansible-galaxy collection install manuelraa.yaml_folder_inventory
> cat ansible.cfg
[defaults]
inventory = ./inventory/yaml_folder.yml

[inventory]
enable_plugins = manuelraa.yaml_folder_inventory.yaml_folder
```

## Inventory plugin overview
### Main folder
Inventory folder root must contain a file called `yaml_folder.yml` it can be empty or contain whatever you want.
This marks the root for the recusive inventory building.

### Folder structure
Inside your inventory you can create so many folders you want. The plugin will pick all of them up.
Inside each folder you can place files described in the "Special files" section.

Each folder will be added to the `inventory_hostname` of the actuall hosts.

**Example**
```
inventory/yaml_folder.yml
=========================
...

inventory/prod/app/main.yml
===========================
app1:
    ansible_host: app1.prod.example.localhost

inventory/prod/web/main.yml
===========================
web1:
    ansible_host: web1.prod.example.localhost

inventory/simu/app/main.yml
=======================
app1:
    ansible_host: app1.simu.example.localhost

inventory/simu/web/main.yml
===========================
web1:
    ansible_host: web1.simu.example.localhost
```

This will be converted to:
```
> ansible -i ./inventory --list-hosts
- prod-app-app1
- prod-web-web1
- simu-app-app1
- simu-web-web1

> ansible -i ./inventory --list-hosts --limit 'simu-*'
- simu-app-app1
- simu-web-web1
```

### Special files
#### **`vars.yml`**
Variables applied recusive to all subelements
```yml
var1: 1
var2: test
var3: false
var4:
    - value1
    - value2
```
#### **`main.yml`**
Containing actuall hosts. Group of the host by default is the name of the folder containing the `main.yml` file
```yml
app1:
    ansible_host: app1.example.localhost
    cluster_name: test

app2:
    ansible_host: app2.example.localhost
    cluster_name: test
```

#### Group yml files **`*.yml`**
All other `.yml` files which are neither `main.yml` or `var.yml` are group_var files which are applied recusivly down the inventory

## Example
Can be found [here](./example)