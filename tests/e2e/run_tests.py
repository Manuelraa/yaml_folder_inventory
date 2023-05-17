"""Run e2e tests."""
from argparse import (
    ArgumentParser,
    Namespace,
)
from dataclasses import dataclass
from subprocess import (
    PIPE,
    Popen,
    SubprocessError,
    TimeoutExpired,
)
from pathlib import Path
from typing import (
    Dict,
    List,
    Tuple,
    Union,
)
import json
import logging
import os
import sys

from deepdiff import DeepDiff


def get_args() -> Namespace:
    """Parse CLI args."""
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    return parser.parse_args()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)


def main() -> None:
    """Entrypoint for script."""
    args = get_args()
    setup_logging(args.verbose)
    e2e_tester = E2ETester()
    success = e2e_tester.run()
    sys.exit(0 if success else 1)


def run_process(cmd: Union[List[str], Tuple[str]], env: Dict[str, str] = None, cwd: str = None, timeout: int = None):
    """Run process and return stdout and stderr."""
    # Running process
    logging.debug("Running subprocess with CMD: '%s', ENV: '%s', CWD: %s", cmd, env, cwd)
    process = Popen(
        cmd,
        env=env,
        cwd=cwd,
        stdout=PIPE,
        stderr=PIPE,
    )

    # First try waiting for process to exit.
    # If timeout is reached kill process, log stdout/stderr and raise error.
    try:
        (stdout, stderr) = process.communicate(timeout=timeout)
    except TimeoutExpired:
        logging.error("Test timeout after %s seconds", timeout)
        process.kill()
        (stdout, stderr) = process.communicate()
        logging.error("STDOUT:\n%s", stdout)
        logging.error("STDERR:\n%s", stderr)
        raise

    return (stdout, stderr)


class TestError(Exception):
    """Error raised if test failed."""


@dataclass
class Test:
    """Object representating one test."""
    name: str
    path: Path


class E2ETester:
    """Class collecting and executing e2e tests."""

    tests: List[Test]
    cwd: Path
    test_timeout: int

    def __init__(self, cwd: Path = Path.cwd(), test_timeout: int = 30) -> None:
        self.cwd = cwd
        self.tests = []
        self.test_timeout = test_timeout

    def run(self) -> bool:
        """Collect and run tests."""
        logging.debug("Start test run")
        success = True

        # Collect tests
        self.collect_tests()

        # Run each test
        for test in self.tests:
            try:
                self.run_test(test)
            except TestError:
                success = False

        # Completed
        logging.debug("Complete test run. Success: %s", success)
        return success

    def collect_tests(self) -> None:
        """Build list of test cases."""
        logging.debug("Start collecting tests")
        # Iterate over each folder in CWD
        for element in self.cwd.iterdir():
            # Skip files
            if not element.is_dir():
                continue

            # Build object and add to list
            test = Test(name=element.name, path=element)
            logging.debug("Adding test: %s", test)
            self.tests.append(test)

    def run_test(self, test: Test) -> bool:
        """Run a test."""
        logging.info("Running test: %s", test.name)

        # Get expected inventory
        with open(test.path / "expected.json") as expected_file:
            expected_inventory = json.load(expected_file)

        # Get actuall inventory
        cmd = ["{}/bin/ansible-inventory".format(os.environ["VIRTUAL_ENV"]), "--list"]
        env = {
            "ANSIBLE_CONFIG": "./ansible.cfg",
        }
        cwd = test.path
        logging.info("Running ansible-inventory to get inventory as json")
        try:
            (stdout, stderr) = run_process(cmd, env, cwd, self.test_timeout)
        except SubprocessError as err:
            test_error = TestError("Failed while running ansible-inventory")
            logging.exception(test_error)
            raise test_error from err
        actuall_inventory = json.loads(stdout.decode())

        # Compare expected and actuall inventory
        diff = DeepDiff(expected_inventory, actuall_inventory, ignore_order=True)
        if diff:
            logging.error("Found difference: %s", diff)
            raise TestError("Expected and actuall inventory are diffrent")


if __name__ == "__main__":
    main()
