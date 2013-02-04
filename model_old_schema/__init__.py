from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

class EqualityByIDMixin(object):
    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
#The following unique-ness code is from http://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject
def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    def f(session):
        cache = getattr(session, '_unique_cache', None)
        if cache is None:
            session._unique_cache = cache = {}
    
        key = (cls, hashfunc(*arg, **kw))
        if key in cache:
            return cache[key]
        else:
            with session.no_autoflush:
                q = session.query(cls)
                q = queryfunc(q, *arg, **kw)
                obj = q.first()
                if not obj:
                    obj = constructor(session, *arg, **kw)
                    session.add(obj)
            cache[key] = obj
            return obj
    return f if session is None else f(session)
    
class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
                    session,
                    cls,
                    cls.unique_hash,
                    cls.unique_filter,
                    cls,
                    arg, kw
               )

SCHEMA = None  
Base = None
metadata = None
