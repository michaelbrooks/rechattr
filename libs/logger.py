levels = {
    'INFO': 0, 
    'WARN': 1, 
    'ERROR': 2
}

class Logger(object):
    
    def __init__(self, level="WARN"):
        self._loglevel = level
    
    def _level_passes(self, level):
        return levels[level] >= levels[self._loglevel]
    
    def log(self, level='INFO', message='', *args):
        if not self._level_passes(level):
            return
        
        if len(args) > 0:
            print "%s: %s; %s" %(level, message, args)
        else:
            print "%s: %s" %(level, message)
    
    def error(self, message, *args):
        self.log("ERROR", message, args)
    
    def warn(self, message, *args):
        self.log("WARN", message, args)
    
    def info(self, message, *args):
        self.log("INFO", message, args)
        
        