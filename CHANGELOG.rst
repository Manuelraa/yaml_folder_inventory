=====================================================
manuelraa.yaml_folder_inventory Release Notes
=====================================================

.. contents:: Topics

v1.4.1
========

Bugfixes
--------
- Fix yaml file extension check not working as intendet if file had no extension or more then one extension

v1.4.0
========

Breaking Changes
----------------
- Rename option :code:`EXCLUDE_LAST_GROUP_IN_NAME` to :code:`exclude_last_group_in_name` 
- Moved config from :code:`yaml_folder.yml` to :code:`ansible.cfg`

Major Changes
-------------
- Allow both :code:`.yml` and :code:`.yaml` file ending

Minor Changes
-------------
- Little code cleanups

v1.3.0
========

Major Changes
-------------
- Allow main.yml file to be a yaml list
- Allow yaml_folder.yml to act as a config
- Allow removing last folder name from instance name 

Bugfixes
--------
- Wrong type error causes crash because of wrong function name

v1.2.4
========
- Ansible Galaxy import of 1.2.3 failed and I'm not able to upload same version again. So I have to change the version number.

v1.2.3
======

Major Changes
-------------
- Improved Ansible downwards compatibility by removing import which first worked with Ansible 2.8
- Added e2e tests to the repo

Minor Changes
-------------
- Added logging

v1.2.2
======

Bugfixes
--------
- Fix #28 recursive variable collection not working correctly

v1.2.1
======

Minor Changes
-------------
- Updated example in repo
- Fix pylint errors
- Split bigger methods into smaller methods

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
