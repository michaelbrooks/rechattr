import threading

def tlog(msg):
    print "%s (t %s)" %(msg, thread_id())

def thread_id():
    return threading.current_thread().ident

from checker import TermChecker
from dts import DynamicTwitterStream
from listener import JsonStreamListener