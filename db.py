from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import appconfig as conf
import web

# Connect to the database    
engine = create_engine(conf.DATABASE_URL, echo=conf.DEBUG)

def load_sqla(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()
        # If the above alone doesn't work, uncomment 
        # the following line:
        #web.ctx.orm.expunge_all() 