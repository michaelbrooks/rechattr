import re

TWITTER_LENGTH_LIMIT = 140

##
# From https://github.com/twitter/twitter-text-java/blob/master/src/com/twitter/Regex.java
##
LATIN_ACCENTS_CHARS = "\\u00c0-\\u00d6\\u00d8-\\u00f6\\u00f8-\\u00ff" + \
                      "\\u0100-\\u024f" + \
                      "\\u0253\\u0254\\u0256\\u0257\\u0259\\u025b\\u0263\\u0268\\u026f\\u0272\\u0289\\u028b" + \
                      "\\u02bb" + \
                      "\\u0300-\\u036f" + \
                      "\\u1e00-\\u1eff";
HASHTAG_ALPHA_CHARS = "a-z" + LATIN_ACCENTS_CHARS + \
                        "\\u0400-\\u04ff\\u0500-\\u0527" + \
                        "\\u2de0-\\u2dff\\ua640-\\ua69f" + \
                        "\\u0591-\\u05bf\\u05c1-\\u05c2\\u05c4-\\u05c5\\u05c7" + \
                        "\\u05d0-\\u05ea\\u05f0-\\u05f4" + \
                        "\\ufb1d-\\ufb28\\ufb2a-\\ufb36\\ufb38-\\ufb3c\\ufb3e\\ufb40-\\ufb41" + \
                        "\\ufb43-\\ufb44\\ufb46-\\ufb4f" + \
                        "\\u0610-\\u061a\\u0620-\\u065f\\u066e-\\u06d3\\u06d5-\\u06dc" + \
                        "\\u06de-\\u06e8\\u06ea-\\u06ef\\u06fa-\\u06fc\\u06ff" + \
                        "\\u0750-\\u077f\\u08a0\\u08a2-\\u08ac\\u08e4-\\u08fe" + \
                        "\\ufb50-\\ufbb1\\ufbd3-\\ufd3d\\ufd50-\\ufd8f\\ufd92-\\ufdc7\\ufdf0-\\ufdfb" + \
                        "\\ufe70-\\ufe74\\ufe76-\\ufefc" + \
                        "\\u200c" + \
                        "\\u0e01-\\u0e3a\\u0e40-\\u0e4e" + \
                        "\\u1100-\\u11ff\\u3130-\\u3185\\uA960-\\uA97F\\uAC00-\\uD7AF\\uD7B0-\\uD7FF" + \
                        "\\p{InHiragana}\\p{InKatakana}" + \
                        "\\p{InCJKUnifiedIdeographs}" + \
                        "\\u3003\\u3005\\u303b" + \
                        "\\uff21-\\uff3a\\uff41-\\uff5a" + \
                        "\\uff66-\\uff9f" + \
                        "\\uffa1-\\uffdc";
HASHTAG_ALPHA_NUMERIC_CHARS = "0-9\\uff10-\\uff19_" + HASHTAG_ALPHA_CHARS;
HASHTAG_ALPHA = "[" + HASHTAG_ALPHA_CHARS +"]";
HASHTAG_ALPHA_NUMERIC = "[" + HASHTAG_ALPHA_NUMERIC_CHARS +"]";

VALID_HASHTAG = re.compile("(^|[^&" + HASHTAG_ALPHA_NUMERIC_CHARS + \
                           "])(#|\uFF03)(" + HASHTAG_ALPHA_NUMERIC + "*" + \
                           HASHTAG_ALPHA + HASHTAG_ALPHA_NUMERIC + "*)", \
                           re.IGNORECASE);
VALID_HASHTAG_GROUP_BEFORE = 1;
VALID_HASHTAG_GROUP_HASH = 2;
VALID_HASHTAG_GROUP_TAG = 3;
INVALID_HASHTAG_MATCH_END = re.compile("^(?:[##]|://)");

def valid_hashtag(input):
    if not len(input):
        return False
        
    if input[0] != '#':
        input = '#' + input
    
    return VALID_HASHTAG.match(input)

def hashtag_contains(hashtag):
    htmatch = VALID_HASHTAG.match(hashtag);
    if htmatch is None:
        raise Exception("Invalid hashtag")
        
    hashtag = htmatch.group(VALID_HASHTAG_GROUP_TAG)
    
    hashtagRegex = re.compile("(^|[^0-9A-Z&/]+)(#|\uFF03)(" + \
                              hashtag + \
                              ")($|[^#\uFF03" + HASHTAG_ALPHA_NUMERIC_CHARS + "])", \
                              re.IGNORECASE);
                              
    return lambda inputStr : hashtagRegex.search(inputStr)