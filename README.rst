===========
 dh-python
===========

``dh-python`` provides various tools that help packaging Python related files
in Debian.

* ``pybuild`` is a tool that implements ``dh`` sequencer's ``dh_auto_foo``
  commands (but it can be used outside ``dh`` as well). It builds and installs
  files.

* ``dh_python3`` is a tool that takes what ``pybuild`` produces and
  generates runtime dependencies and maintainer scripts.
  It fixes some common mistakes, like installing files into
  ``site-packages`` instead of ``dist-packages``, ``/usr/local/bin/`` 
  shebangs, removes ``.py`` files from ``-dbg`` packages, etc.)

  To translate ``requires.txt`` (a file installed in
  ``dist-packages/foo.egg-info/``) into Debian dependencies, a list of
  packages that provide given egg distribution is used. If the dependency
  is not found there, ``dpkg -S`` is used (i.e. a given dependency has to be
  installed; you need it in ``Build-Depends`` in order to run tests anyway).
  See *dependencies* section in ``dh_python3``'s manpage for more details.

  * ``dh_python3`` works on ``./debian/python3-foo/`` files and other binary
    packages that have ``${python3:Depends}`` in the ``Depends`` field.
    See ``dh_python3`` manpage for more details.

How it works
============

A simplified work flow looks like this:

.. code:: python

    # dh_auto_clean stage
    for interpreter in REQUESTED_INTERPRETERS:
        for version in interpreter.REQUESTED_VERSIONS:
            PYBUILD_BEFORE_CLEAN
            pybuild --clean
            PYBUILD_AFTER_CLEAN

    plenty_of_other_dh_foo_tools_invoked_here

    # dh_auto_configure stage
    for interpreter in REQUESTED_INTERPRETERS:
        for version in interpreter.REQUESTED_VERSIONS:
            PYBUILD_BEFORE_CONFIGURE
            pybuild --configure
            PYBUILD_AFTER_CONFIGURE

    plenty_of_other_dh_foo_tools_invoked_here

    # dh_auto_build stage
    for interpreter in REQUESTED_INTERPRETERS:
        for version in interpreter.REQUESTED_VERSIONS:
            PYBUILD_BEFORE_BUILD
            pybuild --build
            PYBUILD_AFTER_BUILD

    plenty_of_other_dh_foo_tools_invoked_here

    # dh_auto_test stage
    for interpreter in REQUESTED_INTERPRETERS:
        for version in interpreter.REQUESTED_VERSIONS:
            PYBUILD_BEFORE_TEST
            pybuild --test
            PYBUILD_AFTER_TEST

    plenty_of_other_dh_foo_tools_invoked_here

    # dh_auto_install stage
    for interpreter in REQUESTED_INTERPRETERS:
        for version in interpreter.REQUESTED_VERSIONS:
            PYBUILD_BEFORE_INSTALL
            pybuild --install
            PYBUILD_AFTER_INSTALL

    plenty_of_other_dh_foo_tools_invoked_here

    dh_python3

    plenty_of_other_dh_foo_tools_invoked_here


pybuild --$step
---------------

This command is auto-detected, it currently supports distutils, autotools,
cmake and a custom build system where you can define your own set of
commands. Why do we need it? ``dh_auto_foo`` doesn't know each command has to
be invoked for each interpreter and version.


REQUESTED_INTERPRETERS
----------------------

is parsed from ``Build-Depends`` if ``--buildsystem=pybuild`` is set.  If it's
not, you have to pass ``--interpreter`` to ``pybuild`` (more in its manpage)

* ``python3-all{,-dev}`` - all CPython interpreters (for packages that
  provide public modules / extensions)
* ``python3-all-dbg`` - all CPython debug interpreters (if ``-dbg`` package
  is provided)
* ``python3`` - default CPython or closest to default interpreter only (use
  this if you build a Python application)
* ``python3-dbg`` - default CPython debug (or closest to the default one)
  only

REQUESTED_VERSIONS
------------------

is parsed from ``X-Python3-Version`` and ``Build-Depends``.


BEFORE and AFTER commands
-------------------------

can be different for each interpreter and/or version, examples:

* ``PYBUILD_AFTER_BUILD_python3.5=rm {destdir}/{build_dir}/foo/bar2X.py``
* ``PYBUILD_BEFORE_INSTALL_python3=touch {destdir}/{install_dir}/foo/bar/__init__.py``

These commands should be used only if overriding ``dh_auto_foo`` is not enough
(example below)

.. code::

  override_dh_auto_install:
        before_auto_install_commands
        dh_auto_install
        after_auto_install_commands

See the ``pybuild`` manpage for more details (search for ``BUILD SYSTEM ARGUMENTS``)


overrides
---------

How to override ``pybuild`` autodetected options:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


* Each ``pybuild`` call can be disabled (for given interpreter, version or
  stage). See the ``pybuild`` manpage for more details (search for
  ``--disable`` description).
* You can pass options in ``override_dh_auto_foo`` via command line options:

  .. code::

   dh_auto_test -- --system=custom --test-args='{interpreter} setup.py test'

  or env. variables:

  .. code::

   PYBUILD_SYSTEM=custom PYBUILD_TEST_ARGS='{interpreter} setup.py test' dh_auto_test

* You can export env. variables globally at the beginning of debian/rules

  .. code::

   export PYBUILD_TEST_ARGS={dir}/tests/

How to override dh_python3 options:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 * via command line, f.e.
   
.. code::

   override_dh_python3:
        dh_python3 --shebang=/usr/bin/python3

