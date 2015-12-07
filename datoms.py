"""
A Datomic inspired SQLite backed storage

datom:
    - entity
    - attribute
    - value (JSON serializable)
    - time

A Datom is immutable!

>>> datom = Datom('entity', 'some/attribute', 'value')
>>> datom.time is None
True

>>> datoms =  Datoms()
>>> datoms.post(datom)
>>> datoms.get('entity') #doctest:+ELLIPSIS
[Datom(entity=u'entity', attribute=u'some/attribute', value=u'value', ...)]

>>> type(_.pop().time)
<type 'datetime.datetime'>

>>> datoms.get('entity', 'some/attribute') #doctest:+ELLIPSIS
Datom(entity=u'entity', attribute=u'some/attribute', value=u'value', ...)

>>> datoms.post(Datom('entity', 'another/attribute', True))
>>> [datom.attribute for datom in datoms.get('entity')]
[u'another/attribute', u'some/attribute']

>>> datoms.post(Datom('entity', 'another/attribute', False))
>>> [datom.value for datom in datoms.get('entity')]
[False, u'value']

>>> datoms.get('entity', 'another/attribute') #doctest:+ELLIPSIS
Datom(entity=u'entity', attribute=u'another/attribute', value=False, ...)

>>> datoms.delete('entity', 'another/attribute')
>>> datoms.get('entity', 'another/attribute') is None
True

>>> datoms.get('entity', 'never/existed/attribute') is None
True

>>> datoms.get('not_an_entity')
[]

>>> datoms.post(Datom('delete_me', 'one/attribute', None))
>>> datoms.post(Datom('delete_me', 'two/attribute', None))
>>> datoms.delete('delete_me')
>>> datoms.get('delete_me')
[]
"""

import json
import sqlite3
from collections import namedtuple

import sql


class Datom(namedtuple('Datom', ['entity', 'attribute', 'value', 'time'])):
    """A datom of data"""

    def __new__(cls, entity, attribute, value, time=None):
        return super(Datom, cls).__new__(cls, entity, attribute, value, time)

    @classmethod
    def from_record(cls, record):
        return cls(record.entity,
                   record.attribute,
                   json.loads(record.value),
                   record.time)

    def as_record(self):
        return (self.entity,
                self.attribute,
                json.dumps(self.value),
                self.time)

class Datoms(object):
    """Storing Datoms of data"""

    def __init__(self):
        self._connection = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        self._sql = sql.SQL(self._connection)
        self._sql.run("""CREATE TABLE IF NOT EXISTS datoms
                         (entity, attribute, value, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                         _deleted BOOLEAN DEFAULT FALSE)
                      """)
        self._sql.run("""CREATE INDEX IF NOT EXISTS entity_attribute
                         ON datoms (entity, attribute)""")
        self._sql.run("""CREATE VIEW IF NOT EXISTS current
                         AS SELECT max(_ROWID_)
                            FROM datoms
                            GROUP BY entity, attribute""")

    def post(self, datom):
        """Persist datom"""
        if datom.time is None:
            record = datom.as_record()
            self._sql.run("""INSERT INTO datoms (entity, attribute, value)
                             VALUES (?, ?, ?)
                          """,
                          [record[:3]])

    def get(self, entity, attribute=None):
        """Retrieve datoms from storage"""
        if attribute is None:
            return self._get_entity(entity)
        else:
            return self._get_entity_attribute(entity, attribute)

    def delete(self, entity, attribute=None):
        """Mark datoms as deleted"""
        if attribute is None:
            self._delete_entity(entity)
        else:
            self._delete_entity_attribute(entity, attribute)

    def _get_entity(self, entity):
        return [Datom.from_record(record)
                for record in self._sql.all("""SELECT entity, attribute, value, time
                                               FROM datoms
                                               WHERE entity='{0}'
                                               AND _ROWID_ IN current
                                               AND NOT _deleted
                                            """.format(entity))]

    def _get_entity_attribute(self, entity, attribute):
        record = self._sql.one("""SELECT entity, attribute, value, time
                                  FROM datoms
                                  WHERE entity='{0}'
                                  AND attribute='{1}'
                                  AND _ROWID_ IN current
                                  AND NOT _deleted
                               """.format(entity, attribute))
        if record:
            return Datom.from_record(record)

    def _delete_entity(self, entity):
        self._sql.run("""INSERT INTO datoms (entity, attribute, _deleted)
                         VALUES (?, ?, 1)
                      """,
                      [(entity, datom.attribute)
                       for datom in self._get_entity(entity)])

    def _delete_entity_attribute(self, entity, attribute):
        self._sql.run("""INSERT INTO datoms (entity, attribute, _deleted)
                         VALUES (?, ?, 1)
                      """,
                      [(entity, attribute)])
