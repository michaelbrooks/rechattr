import web

class Flash(object):

    def get(self, clear=False):
        flash = web.ctx.session.get('flash')
        
        if clear and flash is not None:
            del web.ctx.session['flash']
            
        return flash
    
    def set(self, **kargs):
        web.ctx.session['flash'] = kargs
    
    def error(self, message):
        self.set(type="error", message=message)
    
    def warn(self, message):
        self.set(type="warn", message=message)
    
    def info(self, message):
        self.set(type="info", message=message)
        
        