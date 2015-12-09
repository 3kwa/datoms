A simplistic, Datomic inspired, SQLite backed, REST influenced, *schemaless*
auditable facts storage.


`Data + Atom = Datom`
=====================

A datom has 4 properties:

* entity: the *thing* you want to record information about (akin to primary key)
* attribute: a *label* for the information you want to record
* value: the information itself (JSON serializable)
* time: when datom was stored

>>> from datoms import Datom
>>> datom = Datom('entity', 'some/attribute', 'value')
>>> datom.time is None
True

A datom (a fact) is immutable!

>>> try:
...     datom.entity = 'immutable' #doctest:+ELLIPSIS
... except AttributeError, e:
...     pass
>>> e.message
"can't set attribute"


Datoms
======

Datoms is where you store datoms.

>>> from datoms import Datoms
>>> datoms = Datoms()

With no argument the datams are stored in memory only, with a filename they are
persisted to disk.

>>> datoms = Datoms('persisted.datoms') #doctest:+SKIP

POST
----

To store a datom you `post` it.

>>> datoms.post(datom)

If the datom had its `time` property set it will be replaced in storage by
the UTC time at insertion.

You can think of `Datoms` as an append only collection of *facts*.

GET
---

To retrieve data from a `Datoms` you use `get`.

The bare minimum is to call `get` with an `entity` which returns a list of datoms
belonging to `entity`. It returns the latest known facts about `entity` i.e. the
latest value of every `attribute` attached to `entity`.

>>> datoms.get('entity') #doctest:+ELLIPSIS
[Datom(entity=u'entity', attribute=u'some/attribute', value=u'value', time=datetime.datetime(...)]

`get` returns an empty list if the `entity` is not known or all its `attribute`s
have been *deleted*.

When called with en `entity` and and `attribute` it returns the latest matching
`Datom`.

>>> datoms.get('entity', 'some/attribute') #doctest:+ELLIPSIS
Datom(entity=u'entity', attribute=u'some/attribute', value=u'value', time=datetime.datetime(...)

`get` returns None if there is not matching `Datom`.

DELETE
------

Immutably! What?

You cannot ever delete a fact from a Datoms instance, but you can *void* it i.e.
make it not show up when calling `get`.

>>> datoms.post(Datom('entity', 'void/soon', True))
>>> len(datoms.get('entity'))
2

>>> datoms.delete('entity', 'void/soon')
>>> len(datoms.get('entity'))
1

You can also *void* an entire `entity`.

>>> datoms.delete('entity')
>>> len(datoms.get('entity'))
0
