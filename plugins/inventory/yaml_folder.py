"""yaml_folder ansible inventory plugin."""
from pathlib import Path
from typing import List

from ansible.cli import display
from ansible.inventory.data import InventoryData
from ansible.inventory.group import Group
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.utils.display import Display


DOCUMENTATION = """
    name: yaml_folder
    plugin_type: inventory
    author:
        - Manuel Rapp (@manuelraa)
"""


EXAMPLES = """
"""


TREE_LEVEL_GROUP_TEMPLTE = "__yaml_folder__{}{}"
PREFIX_TEMPLATE = "{}{}-"


class YamlFolderDisplay(Display):
    """Subclass to always add prefix."""

    def __init__(self):
        super().__init__(verbosity=display.verbosity)

    # pylint: disable=too-many-arguments
    def display(
        self, msg, color=None, stderr=False, screen_only=False, log_only=False, newline=True
    ):
        super().display(f"[yaml_folder] {msg}", color, stderr, screen_only, log_only, newline)


DISPLAY = YamlFolderDisplay()


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
        if super().verify_file(path):
            if path.endswith("/yaml_folder.yml"):
                valid = True
        return valid

    def parse(self, inventory: InventoryData, loader: DataLoader, path: str, cache: bool = True):
        """Parse the inventory folder. Called by ansible."""
        self.inventory = inventory
        self.loader = loader

        # Inventory folder to parse is the one containing the "yaml_folder.yml" file
        inventory_folder = Path(path).parent
        DISPLAY.v(f"YAML Inventory: {inventory_folder}")
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
        DISPLAY.vvv(f"Parsing group variables: {path}")

        # Filename is group name
        group = path.name.replace(".yml", "")
        tree_level_group = TREE_LEVEL_GROUP_TEMPLTE.format(prefixes[-1], group).replace("-", "_")
        DISPLAY.vvv(f"Group name / Tree level group name: {group} / {tree_level_group}")

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

    def _parse_hosts(
        self, hosts_obj: dict, hosts_path: Path, global_vars: dict, prefixes: List[str]
    ) -> None:
        """Parse hosts file. aka main.yml"""
        DISPLAY.vvv(f"Parsing hosts: {hosts_path}")
        for (host_name_base, host_vars) in hosts_obj.items():
            # If no vars are define for host object it is parsed as None
            if host_vars is None:
                host_vars = {}

            # Build host_name
            host_name = f"{prefixes[-1]}{host_name_base}"

            # Combine host_vars with other vars collected
            combined_vars = global_vars.copy()
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

    def _parse_inventory(self, folder: Path, global_vars: dict = None, prefixes: List[str] = None):
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
            if path.name == "yaml_folder.yml":
                continue
            # Recurse dirs after processing all files
            if path.is_dir():
                sub_dirs.append(path)
                continue
            # Skip file not ending with ".yml"; Check must be after is_dir() check
            if not path.name.endswith(".yml"):
                continue

            # Parse yaml
            obj = self.loader.load_from_file(str(path))

            # Global vars apply to all groups
            if path.name == "vars.yml":
                global_vars.update(obj)
            # Add instances
            elif path.name == "main.yml":
                hosts_obj = obj
                hosts_path = path
            # Group vars
            else:
                self._parse_group_vars(obj, path, prefixes)

        # Process hosts from host_obj
        if hosts_obj:
            self._parse_hosts(hosts_obj, hosts_path, global_vars, prefixes)

        # Recurse into folders
        for sub_dir in sub_dirs:
            DISPLAY.vvv(f"Recurse into folder: {sub_dir}")
            prefixes.append(PREFIX_TEMPLATE.format(prefixes[-1], sub_dir.name))
            self._parse_inventory(sub_dir, global_vars, prefixes)

        # Going up a recursion level on method return. Therefore also remove prefix of this level.
        prefixes.pop(-1)
