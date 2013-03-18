from tweepy.streaming import StreamListener
import simplejson as json

class JsonStreamListener(StreamListener):
        
    def on_data(self, data):
        try:
            entity = json.loads(data)
            keys = entity.keys()
        except ValueError:
            print "Invalid data received: %s" % (data)
            return True
        except AttributeError:
            print "Non-object received: %s" % (data)
            return True
            
        if 'delete' in keys:
            status = entity['delete']['status']
            return self.on_delete(status['id'], status['user_id'])
            
        elif 'scrub_geo' in keys:
            scrub_geo = entity['scrub_geo']
            return self.on_scrub_geo(scrub_geo['user_id'], scrub_geo['up_to_status_id'])
            
        elif 'limit' in keys:
            limit = entity['limit']
            return self.on_limit(limit['track'])
            
        elif 'status_withheld' in keys:
            status = entity['status_withheld']
            return self.on_status_withheld(status['id'], status['user_id'], status['withheld_in_countries'])
        
        elif 'user_withheld' in keys:
            user = entity['user_withheld']
            return self.on_user_withheld(user['id'], status['withheld_in_countries'])
            
        elif 'disconnect' in keys:
            disconnect = entity['disconnect']
            return self.on_disconnect(disconnect['code'], disconnect['stream_name'], disconnect['reason'])
            
        elif 'warning' in keys:
            warning = entity['warning']
            return self.on_stall_warning(warning['code'], warning['message'], warning['percent_full'])
            
        elif 'in_reply_to_status_id' in keys:
            return self.on_status(entity)
        else:
            return self.on_unknown(entity)

    def on_status(self, status):
        """Called when a new status arrives"""
        print "status %s received" % (status['id'])
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