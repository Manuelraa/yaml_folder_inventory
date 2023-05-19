"""yaml_folder ansible inventory plugin."""
from pathlib import Path
from typing import (
    List,
    Union,
)

from ansible.cli import display
from ansible.inventory.data import InventoryData
from ansible.inventory.group import Group
from ansible.parsing.dataloader import DataLoader
from ansible.parsing.yaml.objects import (
    AnsibleSequence,
    AnsibleUnicode,
)
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display


DOCUMENTATION = """
    module: yaml_folder
    plugin_type: inventory
    short_description: YAML folder inventory
    description:
      - Recursivly parsed a tree based folder structure and processes it into a single inventory
    options:
      exclude_last_group_in_name:
        description: Changes behaviour if last group name is added to instance names or not
        default: False
        env:
          - name: EXCLUDE_LAST_GROUP_IN_NAME
        ini:
          - section: inventory
            key: exclude_last_group_in_name
        required: False
        type: bool
        version_added: 1.4.0
      enable_allhostnames:
        description: Adds special 'allhostnames' group which contains all ansible_hosts instead of the instance name
        default: False
        env:
          - name: ENABLE_ALLHOSTNAMES
        ini:
          - section: inventory
            key: enable_allhostnames
        required: False
        type: bool
        version_added: 1.4.2
      enable_level_groups:
        description: When enabled generate a group for each inventory level containing all hosts of this level.
        default: False
        env:
          - name: ENABLE_LEVEL_GROUPS
        ini:
          - section: inventory
            key: enable_level_groups
        required: False
        type: bool
        version_added: 1.5.0
    author:
        - Manuel Rapp (@manuelraa)
"""


EXAMPLES = """
# Example can be found in the github repo: https://github.com/Manuelraa/yaml_folder_inventory/tree/master/example
"""


ALLHOSTNAMES = "allhostnames"
ANSIBLE_HOST = "ansible_host"
TREE_LEVEL_GROUP_TEMPLTE = "__yaml_folder__{}{}"
PREFIX_TEMPLATE = "{}{}-"


def yml_or_yaml(file_name: str):
    """Return true if the file extension is '.yml' or '.yaml'."""
    return file_name.rsplit(".", 1)[-1] in ("yml", "yaml")


def raise_wrong_type(template: str, obj: object, path: str):
    """Function used to display wrong type messages during validation.

    Takes care of converting special ansible types
    to normal names like 'list' everyone understands.
    """
    if isinstance(obj, AnsibleSequence):
        obj_type = list
    elif isinstance(obj, AnsibleUnicode):
        obj_type = str
    else:
        obj_type = type(obj)
    msg = template.format(obj_type, path)
    raise ValueError(msg)


class YamlFolderDisplay(Display):
    """Subclass to always add prefix."""

    def __init__(self):
        super().__init__(verbosity=display.verbosity)

    # pylint: disable=too-many-arguments
    def display(self, msg, *args, **kwargs):
        super().display(f"[yaml_folder] {msg}", *args, **kwargs)


class InventoryModule(BaseInventoryPlugin):
    """yaml_folder ansible inventory plugin."""

    NAME = "manuelraa.yaml_folder.yaml_folder"

    # Type hints for instance variables set in self.parse
    inventory: InventoryData
    loader: DataLoader

    def __init__(self):
        # Sets some defaults to instance variables (e.g. self.inventory = None)
        super().__init__()

        self.display = YamlFolderDisplay()

        # Config might be overriden in self.parse
        self.exclude_last_group_in_name = False
        self.enable_allhostnames = False
        self.enable_level_groups = False

    def verify_file(self, path: str) -> bool:
        """Return if the specified inventory path is valid."""
        valid = False
        path_obj = Path(path)
        if super().verify_file(path) and (
            path_obj.name.startswith("yaml_folder.") and yml_or_yaml(path_obj.name)
        ):
            valid = True
        return valid

    def parse(
        self,
        inventory: InventoryData,
        loader: DataLoader,
        path: str,
        cache: bool = True,
    ):
        """Parse the inventory folder. Called by ansible."""
        super().parse(inventory, loader, path, cache)

        # set config settings
        self.exclude_last_group_in_name = self.get_option("exclude_last_group_in_name")
        self.enable_allhostnames = self.get_option("enable_allhostnames")
        self.enable_level_groups = self.get_option("enable_level_groups")

        # Add 'allhostnames' group if enabled
        if self.enable_allhostnames:
            self.inventory.add_group(ALLHOSTNAMES)

        # Inventory folder to parse is the one containing the "yaml_folder.yml" file
        inventory_folder = Path(path).parent
        self.display.v(f"YAML Inventory: {inventory_folder}")
        # Start recursion
        self._parse_inventory(inventory_folder)

    def _search_tree_level_group(self, prefixes: List[str], group: str) -> Group:
        """Search for lowest level tree_level_group and return it."""
        possible_higher_level_groups = [
            TREE_LEVEL_GROUP_TEMPLTE.format(prefix, group).replace("-", "_")
            for prefix in prefixes[:-1]  # Exclude current level from prefixes
        ]
        # Search bottum to up
        for possible_higher_level_group in reversed(possible_higher_level_groups):
            try:
                return self.inventory.groups[possible_higher_level_group]
            except KeyError:
                pass
        return None

    def _parse_group_vars(self, obj: dict, path: Path, prefixes: List[str]) -> None:
        """Parse group vars file. aka group_name.yml (haproxy.yml)"""
        self.display.vvv(f"Parsing group variables: {path}")

        # Filename is group name
        group = path.name.replace(".yml", "").replace(".yaml", "")
        tree_level_group = TREE_LEVEL_GROUP_TEMPLTE.format(prefixes[-1], group).replace(
            "-", "_"
        )
        self.display.vvv(
            f"Group name / Tree level group name: {group} / {tree_level_group}"
        )

        # Add group if not exist
        self.inventory.add_group(group)
        self.inventory.add_group(tree_level_group)

        # Tree level group vars
        tree_level_group_vars = {}

        # Try to get existing group vars of upper level
        higher_tree_level_group = self._search_tree_level_group(prefixes, group)
        if higher_tree_level_group is not None:
            tree_level_group_vars.update(higher_tree_level_group.get_vars())

        # Override existing vars with this levels variables
        tree_level_group_vars.update(obj)

        # Set variables to tree level group
        for varname, value in tree_level_group_vars.items():
            self.inventory.set_variable(tree_level_group, varname, value)

    # pylint: disable=too-many-locals,too-many-arguments
    def _parse_hosts(
        self,
        hosts_obj: Union[dict, str],
        hosts_path: Path,
        global_vars: dict,
        prefixes: List[str],
        additional_groups: List[str],
    ) -> None:
        """Parse hosts file. aka main.yml"""
        self.display.vvv(f"Parsing hosts: {hosts_path}, prefixes: {prefixes}")
        for host_obj in hosts_obj:
            # Allow for dict or list definition of main.yml files
            if isinstance(hosts_obj, list):
                (host_name_base, host_vars) = next(iter(host_obj.items()))
            else:
                host_name_base = host_obj
                host_vars = hosts_obj[host_obj]

            # If no vars are define for host object it is parsed as None
            if host_vars is None:
                host_vars = {}

            # Build host_name
            if self.exclude_last_group_in_name:
                host_name = f"{prefixes[-2]}{host_name_base}"
            else:
                host_name = f"{prefixes[-1]}{host_name_base}"

            # Add host
            self.inventory.add_host(host_name)

            # Combine host_vars with other vars collected
            combined_vars = global_vars.copy()
            combined_vars.update(host_vars)

            # Allow override of groups by defining the "groups" variable
            groups = combined_vars.pop("groups", None) or [hosts_path.parent.name]
            if not isinstance(groups, list):
                raise_wrong_type(
                    "[ERROR] Expected 'groups' variable to be a list. Got {}. File: {}",
                    groups,
                    hosts_path,
                )

            # Allow extra groups by defining the "extra_groups" variable
            extra_groups = combined_vars.pop("extra_groups", [])
            if not isinstance(extra_groups, list):
                raise_wrong_type(
                    "[ERROR] Expected 'extra_groups' variable to be a list. Got {}. File: {}",
                    extra_groups,
                    hosts_path,
                )
            groups.extend(extra_groups)

            # Add additional groups when defined
            groups.extend(additional_groups)

            # Set variables for host
            for varname, value in combined_vars.items():
                self.inventory.set_variable(host_name, varname, value)

            # Add host to specified groups
            for group in groups:
                # Add group if not exist
                self.inventory.add_group(group)

                # Add host to each group
                self.inventory.add_host(host_name, group)

                # Apply group_vars of tree level
                tree_level_group = self._search_tree_level_group(prefixes, group)
                if tree_level_group:
                    self.inventory.add_host(host_name, tree_level_group.name)

            # Add hosts to 'allhostnames' if enabled
            if self.enable_allhostnames:
                ansible_host = (
                    self.inventory.get_host(host_name)
                    .get_vars()
                    .get(ANSIBLE_HOST, host_name)
                )
                self.inventory.add_host(ansible_host, ALLHOSTNAMES)

    # pylint: disable=too-many-branches
    def _parse_inventory(
        self, folder: Path, global_vars: dict = None, prefixes: List[str] = None
    ):
        """Recurse inventory folder and parse all group_vars, hosts etc."""
        # Default value for vars
        if global_vars is None:
            global_vars = {}
        else:
            # To avoid changing vars in higher level of the tree make a copy of it
            global_vars = global_vars.copy()
        # Default for prefixes
        if prefixes is None:
            prefixes = [""]

        # Collect subfolders to recurse after parsing the rest
        sub_dirs = []

        # Those variables are set later down when "main.yml" is found
        # They have to be processed last so all variables are included
        hosts_obj = None
        hosts_path = None

        # Iter over dir files and folders
        for path in folder.iterdir():
            # Skip "yaml_folder.yml" file
            if path.name.startswith("yaml_folder") and yml_or_yaml(path.name):
                continue
            # Recurse dirs after processing all files
            if path.is_dir():
                sub_dirs.append(path)
                continue
            # Skip file not ending with ".yml" or ".yaml"; Check must be after is_dir() check
            if not yml_or_yaml(path.name):
                self.display.vvv(f"Skip non yaml file {path}")
                continue

            # Parse yaml
            obj = self.loader.load_from_file(str(path))

            # Global vars apply to all groups
            if path.name.startswith("vars."):
                global_vars.update(obj)
            # Add instances
            elif path.name.startswith("main."):
                if not isinstance(obj, (dict, list)):
                    raise_wrong_type(
                        "[ERROR] Expected file content to be a dict/object or list. Got {}. File: {}",
                        obj,
                        path,
                    )
                hosts_obj = obj
                hosts_path = path
            # Group vars
            else:
                self._parse_group_vars(obj, path, prefixes)

        # Add hosts to level group if enabled
        if self.enable_level_groups:
            # Generate level group name from prefixes and ensure it is added to inventory
            # Prefix = 'level1-level2-' -> 'level1_level2'
            level_groups = []
            for prefix in prefixes:
                if prefix == "":
                    continue
                level_group = prefix[:-1].replace("-", "_")
                level_groups.append(level_group)
                self.inventory.add_group(level_group)
        else:
            level_groups = []

        # Process hosts from host_obj
        if hosts_obj:
            self._parse_hosts(
                hosts_obj, hosts_path, global_vars, prefixes, additional_groups=level_groups
            )

        # Recurse into folders
        for sub_dir in sub_dirs:
            self.display.vvv(f"Recurse into folder: {sub_dir}")
            prefixes.append(PREFIX_TEMPLATE.format(prefixes[-1], sub_dir.name))
            self._parse_inventory(sub_dir, global_vars, prefixes)

        # Going up a recursion level on method return. Therefore also remove prefix of this level.
        prefixes.pop(-1)
