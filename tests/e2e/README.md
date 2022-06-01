# e2e tests
E2E tests in this case are parsed inventories by `ansible-inventory` using this plugin.
The excpected output is once validated by a human. By making a testcase as simple as possible to prevent human errors

## Difference between expected.json and old-expected.json
Starting with ansible 2.8 empty group_vars are now not visible in the json.
Before the empty group_vars were still shown.

To allow testing of ansible<=2.7 the old-excpected.json files contain the empty dicts/objects
