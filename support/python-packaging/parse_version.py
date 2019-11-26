from argparse import ArgumentParser
from sys import stdout

"""
Simple script to generate PEP 440 (Post) versions from `git-describe` output.

== Usage ==

This script is intended for generating Python package versions automatically from a tagged Git repository.

The script should be called as: `python support/python-packaging/parse_version.py [Git describe output]`

The script will output to stdout without a new line, `[Git describe content]` is the output of `git describe --tags`.

For convenience, command substitution can be used to get this value directly, and the output redirected into a file:

`python support/python-packaging/parse_version.py $(git describe --tags) > VERSION.txt`.

== Implementation ==

Where a commit is a tagged version (e.g. a final release) the version is the same as the tag minus its prefix:

Example input: 'v0.3.0'
Example output: '0.3.0'

Otherwise, the commit will be treated as a post development release and the version based on the most recent tag plus
the distance to the commit (e.g. 3 commits ahead).

Example input:  'v0.3.0-5-g345C2B1'
Example output: '0.3.0.post5.dev0'

The components in the generated version string are:

* `0.3.0` is the most recent tag as a version
* `.post5` is the number of commits since the tag (e.g. 5 commits)
* `.dev0` indicates the release is a development release (the 0 is a dummy/fixed version prefix)
"""


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('git_describe', help='Output of running `git describe --tags`')
    args = parser.parse_args()

    version_elements = str(args.git_describe).split('-')
    if len(version_elements) == 1:
        stdout.write(version_elements[0].replace('v', ''))
    elif len(version_elements) == 3:
        tag = version_elements[0].replace('v', '')
        distance = version_elements[1]

        stdout.write(f"{tag}.post{distance}.dev0")
    else:
        stdout.write('error - invalid number of elements')
