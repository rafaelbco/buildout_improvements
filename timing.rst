Timing comparison for pull request #402: Fix #153: buildout should cache working set environments
=================================================================================================

Overview
--------

Two buildouts were constructed in order to run the experiments:

- ``simple_buildout``: Typical buildout to install and test a single egg.
- ``plone_deploy_buildout``: Install Plone with multiple Zope instances.

The general strategy for the experiments is to run each buildout multiple times, always in a clean
environment. The procedure is:

- Create a temporary directory.
- Copy the buildout directory into the temporary directory (only versioned files).
- Run ``virtualenv .``.
- Run ``bin/pip install -r buildout_requirements.txt``.
- Run ``bin/buildout``.

Then the average elapsed time for the last step (``bin/buildout``) is computed. This is done two
times: using the latest published version of ``zc.recipe.egg`` (2.0.3) and using the the pull
request.

For the ``plone_deploy_buildout`` we do multiple measures, varying the number of Zope instances.

The ``time_buildout.py`` program allows to run a buildout ``N`` times and collect the timings.
It allows for choosing which version of ``zc.recipe.egg`` to use by passing the
``buildout:develop`` option. We use a development egg even for the published ``zc.recipe.egg``
version, to minimize timing differences.
