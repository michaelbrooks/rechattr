import threading
from tweepy import Stream
from . import tlog

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
        self.streamException = None
        self.termChecker.reset() # clear the stored list of terms - we aren't tracking any
        self.stream = None # there is no stream running
        tlog("Starting term poll")
        while self.polling:
            if self.termChecker.check():
                self.trackingTerms = self.termChecker.tracking_terms()
                self._update_stream()

            # check to see if an exception was raised
            if self.streamException is not None:
                raise self.streamException

            # wait for the interval unless interrupted
            try:
                self.pollingInterrupt.wait(interval)
            except KeyboardInterrupt:
                tlog("Polling canceled by user")
                return

        tlog("Term poll ceased")

    def _stop_stream(self):
        if self.stream is not None:
            tlog("Stopping twitter stream...")
            self.stream.disconnect()
            self.stream = None
            
            # wait a few seconds to allow the streaming to actually stop
            try:
                self.streamInterrupt.wait(60)
            except KeyboardInterrupt:
                tlog("Polling cancelled by user.")
        
    def _update_stream(self):
        
        # Stop any old stream
        self._stop_stream()
        
        if len(self.trackingTerms) > 0:
        
            # build a new stream
            self.stream = Stream(self.auth, self.listener, stall_warnings=True, timeout=90)
            
            self.streamingThread = threading.Thread(target=self._launch_stream)
            self.streamingThread.start()
            
    # Meant to be run in a thread
    def _launch_stream(self):
        # Reset the stream exception tracker
        self.streamException = None
    
        # get updated terms
        tlog("Starting new twitter stream with %s terms" %(len(self.trackingTerms)))
        tlog(self.trackingTerms)
        
        # run the stream
        try:
            self.stream.filter(track=self.trackingTerms, async=False)
            raise Exception("Twitter stream filter returned")
        except Exception, exception:
            tlog("Forwarding exception from streaming thread.")
            self.streamException = exception
            
            # interrupt the main polling thread
            if self.pollingInterrupt is not None:
                self.pollingInterrupt.set()
                self.pollingInterrupt.clear()
        finally:
            if self.streamInterrupt is not None:
                self.streamInterrupt.set()
                self.streamInterrupt.clear()
            tlog("Twitter stream stopped.")