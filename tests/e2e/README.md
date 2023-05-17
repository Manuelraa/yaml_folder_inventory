# e2e tests
E2E tests in this case are parsed inventories by `ansible-inventory` using this plugin.
The excpected output is once validated by a human. By making a testcase as simple as possible to prevent human errors

## Test structure
- A test consists of a `inventory/` folder which contains the inventory to be parsed by the plugin.
- The `expected.json` contains the expected output of the plugin.
- The `ansible.cfg` should contain all required information and point the inventory to the test local inventory folder.
