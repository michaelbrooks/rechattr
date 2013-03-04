import web, os

from sqlalchemy import create_engine

DATABASE_URL = os.environ.get('DATABASE_URL', None)
if DATABASE_URL == None:
    print "DATABASE_URL not in environment"
    
    
engine = create_engine(DATABASE_URL, echo=True)
print engine.execute("select 1").scalar()
urls = (
    '/', 'index'
)

class index:
    def GET(self):
        return "Hello, world!"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
