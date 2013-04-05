import db, model
import appconfig as conf

from model import Tweet, Poll

from datetime import datetime
from threading import Lock
import time

from twittermon import TermChecker, DynamicTwitterStream, JsonStreamListener
from tweepy import OAuthHandler, Status

class DbListener(JsonStreamListener):

    def __init__(self, checker):
        super(DbListener, self).__init__()
        self.checker = checker
        self.backlog = []
        
    def on_status(self, status):
        """Called when a new status arrives"""
        
        # build a Status object out of the json
        status = Status.parse(self.api, status)
        
        # add the status to the queue on the checker
        if not self.checker.lock.acquire(False):
            self.backlog.append(status)
            print "putting status %s in backlog" % (status['id'])
        else:
            # we have a lock so clear the backlog now
            self.checker.tweets.extend(self.backlog)
            self.backlog = []
            
            # and also add the status we care about
            self.checker.tweets.append(status)
            
            self.checker.lock.release()
        
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
        
        self.lock = Lock()
        self.tweets = []
        self.trackingPolls = set()
        self.termsToPolls = dict()
        self.time = time.time()
        
        self.orm = dbsession
        
    def get_terms_to_polls(self):
        return self.termsToPolls;
        
        
    def _normalize_entities(self, status):
        for ht_entity in status.entities['hashtags']:
            ht_entity['text_n'] = '#' + ht_entity['text'].lower()
        
        for mention in status.entities['user_mentions']:
            mention['screen_name_n'] = '@' + mention['screen_name'].lower()
        
        status.user.screen_name_n = '@' + status.user.screen_name.lower()
        status.text_n = status.text.lower()
        
    def _process_tweet(self, status, rt_status=None):
        new_tweet = False
        new_retweet = False
        self._normalize_entities(status)
        
        # look in database first to see if it is there already
        tweet = self.orm.query(Tweet).get(status.id)
        if tweet is None:
            tweet = Tweet(status)
            new_tweet = True
        
        if rt_status is not None:
            self._normalize_entities(rt_status)
            # look in database first to see if it is there already
            retweet = self.orm.query(Tweet).get(rt_status.id)
            if retweet is None:
                retweet = Tweet(rt_status)
                new_retweet = True
        
        matches = 0
        for key, polls in self.termsToPolls.iteritems():
            
            key = key.lower()
            
            # match the key against the main tweet
            match = self._status_matches(key, status)
            
            # if there is a retweet, also match against it separately
            if rt_status is not None:
                match = match or self._status_matches(key, rt_status)
        
            if match:
                # add these polls to the tweet's matches
                tweet.polls.extend(polls)
                matches += 1
                
        if matches == 0:
            print "No matches for: %s" %(tweet.text.encode('ascii', 'replace'))
            if rt_status is not None:
                print "with RT: %s" %(retweet.text.encode('ascii', 'replace'))
        else:
            # uniquify poll list so we don't try to insert duplicates
            uniquePolls = set(tweet.polls)
            tweet.polls = list(uniquePolls)
            if rt_status is not None:
                # the retweet inherits all polls from the original
                retweet.polls = list(uniquePolls)
        
        if matches > 0 or new_tweet:
            self.orm.merge(tweet)
        if rt_status is not None and (matches > 0 or new_retweet):
            self.orm.merge(retweet)
        
        # we mapped the tweet to polls
        return matches > 0
        
    def _status_matches(self, key, status):

        match = False
        
        for ht_entity in status.entities['hashtags']:
            if ht_entity['text_n'] == key:
                match = True
                break
        
        if not match:
            for mention in status.entities['user_mentions']:
                if mention['screen_name_n'] == key:
                    match = True
                    break
        
        if not match:
            if status.user.screen_name_n == key:
                match = True
        
        if not match:
            if key in status.text_n:
                match = True
            
        return match
        
    def _process_tweet_queue(self):
        
        now = time.time()
        diff = now - self.time
        self.time = now
        
        self.lock.acquire()
        tweets = list(self.tweets)
        self.tweets = []
        self.lock.release()
        
        if len(tweets) == 0:
            return
            
        unmapped = 0
        
        for status in tweets:
            # process the embedded tweets first
            if hasattr(status, 'retweeted_status'):
                original = status.retweeted_status
                # and any terms associated with the original will also get put on the retweet
                if not self._process_tweet(original, status):
                    unmapped += 1
            else:
                # otherwise just the one tweet
                if not self._process_tweet(status):
                    unmapped += 1
        
        print "Inserted %s tweets, %s unmapped, at %s tps" %(len(tweets), unmapped, len(tweets) / diff)
        
        self.orm.commit()
        
    def _get_tracking_terms(self):
        # any tweets currently in the queue were retrieve
        # with previous track list, so process them before
        # updating the track list
        self._process_tweet_queue()
    
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
        self.termsToPolls = newTermsToPolls
        
        return newTrackingTerms
        
        
if __name__ == '__main__':
    dbsession = db.db_session()
    
    checker = PollTermChecker(dbsession)
    
    listener = DbListener(checker)
    
    
    auth = OAuthHandler(conf.TWITTER_STREAM_CONSUMER_KEY, conf.TWITTER_STREAM_CONSUMER_SECRET)
    auth.set_access_token(conf.TWITTER_STREAM_ACCESS_KEY, conf.TWITTER_STREAM_ACCESS_SECRET)

    tracker = DynamicTwitterStream(auth, listener, checker)
    tracker.start(conf.STREAM_TERM_POLLING_INTERVAL)
    
