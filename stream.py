import db
import appconfig as conf

from model import Tweet, Poll

from threading import Lock
import time

from twittermon import TermChecker, DynamicTwitterStream, JsonStreamListener, tlog
from tweepy import OAuthHandler, Status
import tweepy

if conf.DEBUG:
    try:
        import pydevd
        pydevd.settrace(conf.DEBUG_SERVER_HOST, port=conf.DEBUG_SERVER_PORT, stdoutToServer=True, stderrToServer=True, suspend=False)
    except ImportError:
        print 'ERROR: Unable to import pydevd for remote debugging!'
    except:
        print 'ERROR: Could not connect to remote debugging server'

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
            tlog("putting status %s in backlog" % (status['id']))
        else:
            # we have a lock so clear the backlog now
            self.checker.tweets.extend(self.backlog)
            self.backlog = []
            
            # and also add the status we care about
            self.checker.tweets.append(status)
            
            self.checker.lock.release()
        
        return True

    def on_error(self, status_code):
        """Called when a non-200 status code is returned"""
        tlog('Twitter returned error code %s' %(status_code))
        if status_code in [400, 401, 403]:
            return False
        else:
            return True

class PollTermChecker(TermChecker):
    
    def __init__(self, dbsession, tweet_api):
        super(PollTermChecker, self).__init__()

        self.tweet_api = tweet_api
        self.lock = Lock()
        self.tweets = []
        self.trackingPolls = set()
        self.termsToPolls = dict()
        self.time = time.time()
        
        self.orm = dbsession
        
    def get_terms_to_polls(self):
        return self.termsToPolls
        
        
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
            tlog("No matches for: %s" %(tweet.text.encode('ascii', 'replace')))
            if rt_status is not None:
                tlog("with RT: %s" %(retweet.text.encode('ascii', 'replace')))
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
        
        tlog("Inserted %s tweets, %s unmapped, at %s tps" %(len(tweets), unmapped, len(tweets) / diff))
        
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
        tweeted = False
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

            if poll.can_tweet():
                # make sure it has been advertised!
                if not poll.announcement_tweet_id:
                    tw = poll.post_tweet(self.tweet_api)
                    if tw:
                        tlog("posted tweet for poll %d" % poll.id)
                        tweeted = True
                    else:
                        tlog("ERROR: posting tweet for poll %d" % poll.id)

                activeQuestions = poll.triggered_questions(session=self.orm, limit=None)
                for question in activeQuestions:
                    if not question.announcement_tweet_id:
                        # tweet any that have not yet been tweeted
                        tw = question.post_tweet(self.tweet_api)
                        if tw:
                            tlog("posted tweet for question %d" % question.id)
                            tweeted = True
                        else:
                            tlog("ERROR: posting tweet for question %d" % question.id)

        if tweeted:
            self.orm.commit()

        # Go ahead and store the new data (polls may have changed)
        self.trackingPolls = newTrackingPolls
        self.termsToPolls = newTermsToPolls

        return newTrackingTerms

if __name__ == '__main__':
    import traceback

    dbsession = db.db_session()

    # a tweepy instance for tweeting on behalf of users
    user_oauth = OAuthHandler(conf.TWITTER_STREAM_CONSUMER_KEY, conf.TWITTER_STREAM_CONSUMER_SECRET)
    tweet_api = tweepy.API(user_oauth)
    checker = PollTermChecker(dbsession, tweet_api)

    listener = DbListener(checker)

    oauth = OAuthHandler(conf.TWITTER_STREAM_CONSUMER_KEY, conf.TWITTER_STREAM_CONSUMER_SECRET)
    oauth.set_access_token(conf.TWITTER_STREAM_ACCESS_KEY, conf.TWITTER_STREAM_ACCESS_SECRET)

    tracker = DynamicTwitterStream(oauth, listener, checker)

    errorCount = 0

    while errorCount < 5:
        # a short delay so nobody gets upset
        time.sleep(1)

        try:
            tracker.start(conf.STREAM_TERM_POLLING_INTERVAL)
            tlog('Poll thread returned.')
        except Exception, e:
            errorCount += 1
            tlog('Exception #%d in poll thread.' %(errorCount))
            traceback.print_exc()

    tlog('Terminating stream - %d errors.' %(errorCount))

