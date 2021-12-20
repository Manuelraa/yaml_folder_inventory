=====================================================
manuelraa.yaml_folder_inventory Release Notes
=====================================================

.. contents:: Topics

v?.?.?
======

Minor Changes
-------------
- Updated example in repo

v1.2.0
======
Even tho changes here are bugfixes they change the behaviro therefore bigger version bump.
In general lots of fixes to wrong variable precedence.

Minor Changes
-------------
- Update README
- Sanitize internal tree level group names
- Don't try parsing non .yml files

Bugfixes
--------
- Fix IndexError when defining group_vars yaml file on top level
- Fix lower level group_vars do override variables of levels above
- Fix vars.yml vars not cleaned when going back up in tree therefore also affecting diffrent tree branches

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
