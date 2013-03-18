import threading
from tweepy import Stream
        
class DynamicTwitterStream(object):
        
    def __init__(self, auth, listener, termChecker):
        self.auth = auth
        self.listener = listener
        self.termChecker = termChecker
        
        self.stream = None
        self.streamException = None
        self.streamInterrupt = threading.Event()
        self.pollingInterrupt = threading.Event()
    
    def start(self, interval):
        self.polling = True
        
        while self.polling:
            if self.termChecker.check():
                self.trackingTerms = self.termChecker.tracking_terms()
                self._update_stream()
                
            # wait for the interval unless interrupted
            
            try:
                self.pollingInterrupt.wait(interval)
            except KeyboardInterrupt:
                print "Polling canceled by user"
                return
            
            # check to see if an exception was raised
            if self.streamException is not None:
                raise self.streamException
        
    def _stop_stream(self):
        if self.stream is not None:
            print "Stopping twitter stream..."
            self.stream.disconnect()
            self.stream = None
            
            # wait a few seconds to allow the streaming to actually stop
            try:
                self.streamInterrupt.wait(60)
            except KeyboardInterrupt:
                print "Polling cancelled by user."
        
    def _update_stream(self):
        
        # Stop any old stream
        self._stop_stream()
        
        if len(self.trackingTerms) > 0:
        
            # build a new stream
            self.stream = Stream(self.auth, self.listener, stall_warnings=True)
            
            self.streamingThread = threading.Thread(target=self._launch_stream)
            self.streamingThread.start()
            
    # Meant to be run in a thread
    def _launch_stream(self):
        # Reset the stream exception tracker
        self.streamException = None
    
        # get updated terms
        print "Starting new twitter stream with %s terms" %(len(self.trackingTerms))
        
        # run the stream
        try:
            self.stream.filter(track=self.trackingTerms, async=False)
            
        except Exception, exception:
            print "Forwarding exception from treaming thread."
            self.streamException = exception
            
            # interrupt the main polling thread
            if self.pollingInterrupt is not None:
                self.pollingInterrupt.set()
                self.pollingInterrupt.clear()
        finally:
            if self.streamInterrupt is not None:
                self.streamInterrupt.set()
                self.streamInterrupt.clear()
            print "Twitter stream stopped."
            
