Timing comparison for pull request #402: Fix #153: buildout should cache working set environments
=================================================================================================

.. contents::

Overview
--------

The goal of the experiment is to understand the performance gains of the pull request #402 to
``zc.recipe.egg``.

Two buildouts were constructed in order to run the experiments:

- ``simple_buildout``: Typical buildout to install and test a single egg.
- ``plone_deploy_buildout``: Install Plone with multiple Zope instances.

The general strategy for the experiment is to run each buildout multiple times, always in a clean
environment. The procedure is:

- Create a temporary directory.
- Copy the buildout directory into the temporary directory (only versioned files).
- Run ``virtualenv .``.
- Run ``bin/pip install -r buildout_requirements.txt``.
- Run ``bin/buildout``.

Then the average elapsed time for the last step (``bin/buildout``) is computed. This is done two
times: using the latest published version of ``zc.recipe.egg`` (2.0.3) and using the the pull
request code.

.. NOTE::
   From now on we'll refer to the last published version of ``zc.recipe.egg`` as _old_ and the
   version from the pull request as _new_.

For the ``plone_deploy_buildout`` we do multiple measures, varying the number of Zope instances.

The ``time_buildout.py`` program allows to run a buildout ``N`` times and collect the timings.
It allows for choosing which version of ``zc.recipe.egg`` to use by passing the
``buildout:develop`` option. We use a development egg even for the published ``zc.recipe.egg``
version, to minimize timing differences.


Experiment description
----------------------

Following the strategy above the ``experiment.py`` was written, which performs the experiment
with the following parameters:

Buildout run repetitions for each set of parameters (``REPETITIONS``)
    5
Maximum number of extra Zope instances for ``plone_deploy_buildout`` (``MAX_EXTRA_INSTANCES``)
    9

This pseudo-code explains ``experiment.py``:

.. code-block:: python

   def test_buildout_with_rev(name, zc_recipe_egg_rev, **kwargs):
       zc_recipe_egg_path = checkout_rev_of_zc_recipe_egg(zc_recipe_egg_rev)
       avg = run(
           'time_buildout.py',
           count=REPETITIONS,
           develop=zc_recipe_egg_path,
           **kwargs
        )
       log(buildout=name, zc_recipe_egg_rev=zc_recipe_egg_rev, time=avg)


   def test_buildout(name, **kwargs):
       test_buildout_with_rev(name, OLD_REV, **kwargs)
       test_buildout_with_rev(name, NEW_REV, **kwargs)

    test_buildout('simple_buildout')

    for i in xrange(0, MAX_EXTRA_INSTANCES + 1):
        test_buildout('plone_deploy_buildout-{}'.format(i), num_extra_instances=i)


Results
-------

The ``output/experiment.log`` file contains the output of ``experiment.py``. The times were
extracted from the log and put on a `Google Spreadsheet`_, with charts. This spreadsheet was
exported to other formats for archiving.


Analysis
--------

Definitions:

Speedup
    ``old_execution_time / new_execution_time``
Execution time difference (%)
    ``100*((new_execution_time - old_execution_time)/old_execution_time)``

For the ``simple_buildout`` and the ``plone_deploy_buildout`` with no extra instances, the new
version performance was almost unchanged compared to the old, with execution execution time
differences of -2.55% and 2.28% respectively.

This indicates the overhead in order to cache the working sets is small.

For the other cases, ie., ``plone_deploy_buildout`` with multiple instances, there was a linear
increase in speedup, directly proportional to the number of instances.

Looking at the chart, we can say that, the execution time function for the old code is ``O(N)``
and the new code is ``O(1)``, where ``N`` is the number of Zope instances.

This indicates that:

1. The time to construct a Zope instance is almost entirely consumed calculating the working set.
2. The working set caching mechanism works well and the overhead is small.

.. References:

.. _`Google Spreadsheet`: https://docs.google.com/spreadsheets/d/1XivBiQgzJEnGFm0eqbkfyjI0jDkR11JdA6O3z69iGb8/edit?usp=sharing


