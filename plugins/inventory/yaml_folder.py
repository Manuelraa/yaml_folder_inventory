"""yaml_folder ansible inventory plugin."""
from pathlib import Path
from typing import List

from ansible.inventory.data import InventoryData
from ansible.inventory.group import (
    Group,
    to_safe_group_name,
)
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.inventory import BaseInventoryPlugin


DOCUMENTATION = """
    name: yaml_folder
    plugin_type: inventory
    author:
        - Manuel Rapp (@manuelraa)
"""


EXAMPLES = """
"""


TREE_LEVEL_GROUP_TEMPLTE = "__yaml_folder__{}{}"


class InventoryModule(BaseInventoryPlugin):
    """yaml_folder ansible inventory plugin."""

    NAME = "manuelraa.yaml_folder.yaml_folder"

    # Type hints for instance variables set in self.parse
    inventory: InventoryData
    loader: DataLoader

    def __init__(self):
        super().__init__()

        # Set in self.parse function
        self.inventory = None
        self.loader = None

    def verify_file(self, path: str) -> bool:
        """Return if the specified inventory path is valid."""
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith("/yaml_folder.yml"):
                valid = True
        return valid

    def parse(self, inventory: InventoryData, loader: DataLoader, path: str, cache: bool = True):
        """Parse the inventory folder. Called by ansible."""
        self.inventory = inventory
        self.loader = loader

        # Inventory folder to parse is the one containing the "yaml_folder.yml" file
        inventory_folder = Path(path).parent
        # Start recursion
        self._parse_inventory(inventory_folder)

    def _search_tree_level_group(self, prefixes: List[str], group: str) -> Group:
        """Search for lowest level tree_level_group and return it."""
        possible_higher_level_groups = [
            to_safe_group_name(TREE_LEVEL_GROUP_TEMPLTE.format(prefix, group).replace("-", "_"))
            for prefix in prefixes
        ]
        # Search bottum to up
        for possible_higher_level_group in reversed(possible_higher_level_groups):
            try:
                return self.inventory.groups[possible_higher_level_group]
            except KeyError:
                pass
        return None

    def _parse_inventory(self, folder: Path, vars: dict = None, prefixes: List[str] = None):
        """Recurse inventory folder and parse all group_vars, hosts etc."""
        # Default value for vars
        if vars is None:
            vars = {}
        else:
            # To avoid changing vars in higher level of the tree make a copy of it
            vars = vars.copy()
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
            if path.name == "yaml_folder.yml":
                continue
            # Skip file not ending with ".yml"
            if (not path.is_dir()) and (not path.name.endswith(".yml")):
                continue

            # Recurse dirs after processing all files
            if path.is_dir():
                sub_dirs.append(path)
                continue

            # Parse yaml
            obj = self.loader.load_from_file(str(path))

            # Global vars apply to all groups
            if path.name == "vars.yml":
                vars.update(obj)
            # Add instances
            elif path.name == "main.yml":
                hosts_obj = obj
                hosts_path = path
            # Group vars
            else:
                # Filename is group name
                group = path.name.replace(".yml", "")
                tree_level_group = to_safe_group_name(
                    TREE_LEVEL_GROUP_TEMPLTE.format(prefixes[-1], group).replace("-", "_")
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
                for (varname, value) in tree_level_group_vars.items():
                    self.inventory.set_variable(tree_level_group, varname, value)

        # Process hosts from host_obj
        if hosts_obj:
            for (host_name_base, host_vars) in hosts_obj.items():
                # If no vars are define for host object it is parsed as None
                if host_vars is None:
                    host_vars = {}

                # Build host_name
                host_name = f"{prefixes[-1]}{host_name_base}"

                # Combine host_vars with other vars collected
                combined_vars = vars.copy()
                combined_vars.update(host_vars)

                # Allow override of groups by defining the "groups" variable
                groups = combined_vars.pop("groups", None) or [hosts_path.parent.name]

                # Add host to specified group and set host variables
                for group in groups:
                    # Add group if not exist
                    self.inventory.add_group(group)

                    # Add host to each group
                    self.inventory.add_host(host_name, group)

                    # Apply group_vars of tree level
                    tree_level_group = self._search_tree_level_group(prefixes, group)
                    if tree_level_group:
                        self.inventory.add_host(host_name, tree_level_group.name)

                    # Set variables for host
                    for (varname, value) in combined_vars.items():
                        self.inventory.set_variable(host_name, varname, value)

        # Recurse into folders
        for sub_dir in sub_dirs:
            prefixes.append("{}{}-".format(prefixes[-1], sub_dir.name))
            self._parse_inventory(sub_dir, vars, prefixes)

        # Going up a recursion level on method return. Therefore also remove prefix of this level.
        try:
            prefixes.pop(-1)
        except IndexError:  # On top level prefixes is empty
            pass
