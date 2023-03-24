12.0.1.1.0 (2022-06-23)
**Features**

- Do not apply a penalty to irregular customers twice in a row. Best explained
  through an example.

  Imagine the following 'sr' of an irregular worker:

  0 -> -2 (cron, penalty) -> -1 (work a shift) -> 0 (work another shift)
  -> ??? (cron)

  The last step should go to -1 instead of -2. The penalty should not be given
  again until sr has reached 1. (`#388 <https://github.com/beescoop/obeesdoo/issues/388>`_)
