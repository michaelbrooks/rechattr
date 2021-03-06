import web
from datetime import datetime, timedelta
import model
from utils.dtutils import utc_aware
from sqlalchemy.orm.session import Session as sess

class AlchemyStore(web.session.Store):
    """Store for saving a session in database using SQLAlchemy
    """
    def __init__(self, cache=True):
        self.orm = None
        if cache:
            self._cache = dict()
        else:
            self._cache = None
        
    def set_db(self, orm):
        # have to clear the cache because this object is re-used
        self._cache = dict()
        self.orm = orm
    
    def __contains__(self, key):
        # print 'CHECKING FOR %s'
        session = self._cache_get(key)
        return session is not None

    def _cache_get(self, key, refresh=False):
        if (not refresh) and (self._cache is not None) and (key in self._cache):
            return self._cache[key]
            
        session = self.orm.query(model.Session).get(key)
        if session is not None:
            self._cache[key] = session
            
        return session
        
    def _cache_put(self, key, session):
        if self._cache is not None:
            self._cache[key] = session
        
    def __getitem__(self, key):
        session = self._cache_get(key)

        if session is not None:
            value = self.decode(session.data)
            # print 'RETREIVING',key, value
            session.atime = utc_aware(datetime.utcnow())

            return value
        else:
            raise KeyError, key

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        session = self._cache_get(key)
        
        if session is not None:
            session.data = pickled
        else:
            session = model.Session(key, pickled)
            self.orm.add(session)
            self._cache_put(key, session)
        
        # print 'STORING',key, value
                
    def __delitem__(self, key):
        self.orm.query(model.Session).filter(model.Session.id==key).delete()

    def cleanup(self, timeout):
        timeout = timedelta(timeout/(24.0*60*60)) #timedelta takes numdays as arg
        last_allowed_time = datetime.utcnow() - timeout
        self.orm.query(model.Session).filter(model.Session.atime < last_allowed_time).delete()