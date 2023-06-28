12.0.5.0.1 (2023-06-20)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- Fixed a bug where writing to multiple cooperative.status records simultaneously
  caused a singleton error. Writing to multiple records simultaneously is now
  possible. (`#514 <https://github.com/beescoop/Obeesdoo/issues/514>`_)


12.0.2.1.0 (2022-06-21)
~~~~~~~~~~~~~~~~~~~~~~~

**Features**

- When subscribing a worker to a shift template in the backend :
  if no super cooperator is set on template and worker is super cooperator
  automatically set them as super cooperator.
  The worker must have a user linked to it. (`#303 <https://github.com/beescoop/obeesdoo/issues/303>`_)


12.0.1.1.4 (2022-05-26)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- When changing a regular worker to an irregular worker via the wizard, no longer
  give an error when their (former) shift is full. (`#390 <https://github.com/beescoop/obeesdoo/issues/390>`_)


12.0.1.1.1 (2022-05-26)
~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- No longer raise an error when unsubscribing a replacement worker using the
  wizard. (`#389 <https://github.com/beescoop/obeesdoo/issues/389>`_)
