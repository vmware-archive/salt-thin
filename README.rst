salt-thin
=========

Salt Thin creates a single deployment tarball, just untar salt-thin and then
the salt-call command can be called directly.

Usage
-----

To create the tarball, run this command from a terminal:

.. code-block:: bash

    $ python setup.py sdist --git-version='v2014.7.0rc3'

This will create a tarball containing the Salt Thin environment, for the given Git
version, at:

.. code-block:: bash

    ./dist/salt-thin-v2014.7.0rc3.tar.gz

Tested on Ubuntu 14.04.1 (x64)

Authors
-------

Thomas S Hatch <thatch@saltstack.com>
Mario del Pozo <mariodpros@gmail.com>
