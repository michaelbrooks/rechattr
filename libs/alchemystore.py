import web
from datetime import datetime, timedelta
from model import Session, utc_aware

class AlchemyStore(web.session.Store):
    """Store for saving a session in database using SQLAlchemy
    """
    def __init__(self):
        self.orm = None
        
    def set_db(self, orm):
        self.orm = orm
    
    def __contains__(self, key):
        # print 'CHECKING FOR %s'
        session = self.orm.query(Session).get(key)
        return session is not None

    def __getitem__(self, key):
        session = self.orm.query(Session).get(key)
        if session is not None:
            value = self.decode(session.data)
            # print 'RETREIVING',key, value
            
            session.atime = utc_aware(datetime.utcnow())
            self.orm.commit()
            return value
        else:
            raise KeyError, key

    def __setitem__(self, key, value):
        pickled = self.encode(value)
        session = self.orm.query(Session).get(key)
        if session is not None:
            session.data = pickled
        else:
            session = Session(key, pickled)
            self.orm.add(session)
        
        # print 'STORING',key, value
        self.orm.commit()
                
    def __delitem__(self, key):
        self.orm.query(Session).filter(Session.id==key).delete()

    def cleanup(self, timeout):
        timeout = timedelta(timeout/(24.0*60*60)) #timedelta takes numdays as arg
        last_allowed_time = datetime.utcnow() - timeout
        self.orm.query(Session).filter(Session.atime < last_allowed_time).delete()