=====================================================
manuelraa.yaml_folder_inventory Release Notes
=====================================================

.. contents:: Topics

v1.?.?
======

Minor Changes
-------------
- Update README

v1.1.0
======

Major Changes
-------------
- Added recurse level groups to fix group vars applied to every branch in tree instead of only it's own branch (Issue #1)

v1.0.1
======

Breaking Changes
----------------
- Rename inventory plugin from :code:`manuelraa.inventory.yaml_folder` to :code:`manuelraa.yaml_folder.yaml_folder`

Minor Changes
-------------
- Add type hints and basic docstrings

Bugfixes
--------
- Removed debug print from plugin
- Fix empty host vars in :code:`main.yml` causes error because parsed as None


v1.0.0
======

Major Changes
-------------
- Initial release
