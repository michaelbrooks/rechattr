import db, model
import appconfig as conf

from model import Tweet, Poll

from datetime import datetime
from dateutil import parser
#import threading

from twittermon import TermChecker, DynamicTwitterStream, JsonStreamListener
from tweepy import OAuthHandler

class DbListener(JsonStreamListener):

    def __init__(self, dbsession, checker):
        super(DbListener, self).__init__()
        
        self.orm = dbsession
        self.checker = checker
        
    def on_status(self, status):
        """Called when a new status arrives"""
        print "status %s received" % (status['id'])
        
        #self.checker.lock()
        # termsToPolls = self.checker.get_terms_to_polls()
        #self.checker.unlock()
        
        tweet = Tweet()
        self.orm.add(tweet)
        
        tweet.id = status['id']
        tweet.created = parser.parse(status['created_at'])
        tweet.user_id = status['user']['id']
        tweet.screen_name = status['user']['screen_name']
        tweet.user_name = status['user']['name']
        tweet.text = status['text']
        tweet.reply_to_tweet_id = status['in_reply_to_status_id']
        if 'retweet_of_status_id' in status:
            tweet.retweet_of_status_id = status['retweet_of_status_id']
        
        # for key, polls in termsToPolls.iteritems():
            # match = False
            
            # for ht_entity in status['entities']['hashtags']:
                # if '#' + ht_entity['text'] == key:
                    # match = True
                    # break
            
            # if not match:
                # for mention in status['entities']['user_mentions']:
                    # if '@' + mention['screen_name'] == key:
                        # match = True
                        # break
            
            # if not match:
                # if '@' + status['user']['screen_name'] == key:
                    # match = True
            
            # if not match:
                # if key in status['text']:
                    # match = True
            
            # if match:
                # tweet.polls.extend(polls)
            
        if len(tweet.polls) == 0:
            print "Received tweet with no polls? %s" %(tweet.text)
        
        self.orm.commit()
        
        return True

    def on_delete(self, status_id, user_id):
        """Called when a delete notice arrives for a status"""
        print "delete received"
        return True
        
    def on_scrub_geo(self, user_id, up_to_status_id):
        """Called when geolocated data must be stripped for user_id for statuses before up_to_status_id"""
        print "scrub_geo received"
        return True
        
    def on_limit(self, track):
        """Called when a limitation notice arrvies"""
        print 'limit received'
        return True
        
    def on_status_withheld(self, status_id, user_id, countries):
        """Called when a status is withheld"""
        print 'status withheld'
        return True
        
    def on_user_withheld(self, user_id, countries):
        """Called when a user is withheld"""
        print 'user withheld'
        return True
        
    def on_disconnect(self, code, stream_name, reason):
        """Called when a disconnect is received"""
        print 'disconnect'
        return True

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        print 'Twitter returned error code %s' %(status_code)
        return False
        
    def on_unknown(self, entity):
        """Called when an unrecognized object arrives"""
        print 'unknown'
        return True

class PollTermChecker(TermChecker):
    
    def __init__(self, dbsession):
        super(PollTermChecker, self).__init__()
        
        self.trackingPolls = set()
        self.termsToPolls = dict()
        #self.termsToPollsLock = threading.Lock()
        
        self.orm = dbsession
        
    # def lock(self):
        # self.termsToPollsLock.acquire()
        
    # def unlock(self):
        # self.termsToPollsLock.release()
        
    def get_terms_to_polls(self):
        return self.termsToPolls;
        
    def _get_tracking_terms(self):
        # Check the database for events that are happening right now
        activePolls = Poll.get_active(self.orm)
        
        #print '%s active polls' %( len(activePolls) )
        
        # Generate a new map from terms to polls
        newTermsToPolls = dict()
        newTrackingTerms = set()
        newTrackingPolls = set()
        
        trackingTermsChanged = False
        for poll in activePolls:
        
            pollTermList = poll.twitter_track_list()
            
            # add all the terms to the map
            for term in pollTermList:
                
                # add the poll to the map for this term
                if term not in newTermsToPolls:
                    newTermsToPolls[term] = []
                newTermsToPolls[term].append(poll)
                
                newTrackingTerms.add(term)
                newTrackingPolls.add(poll)
        
        # Go ahead and store the new data (polls may have changed)
        self.trackingPolls = newTrackingPolls
        
        # we need to lock this because the listener looks at this object also
        #self.lock()
        self.termsToPolls = newTermsToPolls
        #self.unlock()
        
        return newTrackingTerms
        
        
if __name__ == '__main__':
    dbsession = db.db_session()
    
    checker = PollTermChecker(dbsession)
    
    listener = DbListener(dbsession, checker)
    
    
    auth = OAuthHandler(conf.TWITTER_STREAM_CONSUMER_KEY, conf.TWITTER_STREAM_CONSUMER_SECRET)
    auth.set_access_token(conf.TWITTER_STREAM_ACCESS_KEY, conf.TWITTER_STREAM_ACCESS_SECRET)

    tracker = DynamicTwitterStream(auth, listener, checker)
    tracker.start(conf.STREAM_TERM_POLLING_INTERVAL)
    
