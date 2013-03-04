import web
import dj_database_url

DATABASE =  dj_database_url.config()
print DATABASE

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        return "Hello, world!"

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
