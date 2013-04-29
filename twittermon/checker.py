from . import tlog

class TermChecker(object):

    def __init__(self):
        self.trackingTerms = set()

    # Override this
    def _get_tracking_terms(self):
        return set(['#afakehashtag'])

    def reset(self):
        self.trackingTerms = set()

    def check(self):
        newTrackingTerms = self._get_tracking_terms()
        
        trackingTermsChanged = False
        
        # any deleted terms?
        if self.trackingTerms > newTrackingTerms:
            trackingTermsChanged = True
        # any added terms?
        elif self.trackingTerms < newTrackingTerms:
            trackingTermsChanged = True
            
        # Go ahead and store for later
        self.trackingTerms = newTrackingTerms
        
        # If the terms changed, we need to restart the stream
        return trackingTermsChanged
    
    def tracking_terms(self):
        return list(self.trackingTerms)

class FileTermChecker(TermChecker):
    def __init__(self, filename):
        super(FileTermChecker, self).__init__()
        self.filename = filename
        
    def _get_tracking_terms(self):
        with open(self.filename) as input:
            # read all the lines
            lines = input.readlines()
            tlog("Read %s lines from %s" % (len(lines), self.filename))
            # build a set of terms
            newTerms = {line.strip() for line in lines}
            return newTerms
