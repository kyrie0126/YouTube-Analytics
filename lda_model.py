from youtube_transcript_api import YouTubeTranscriptApi
import nltk
from nltk.corpus import stopwords
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.models import LdaModel

nltk.download('stopwords')

custom_stop_words = [
    "fishing", "fish", "angler", "catch", "angling", "bait", "lure", "hook", 
    "reel", "rod", "line", "boat", "water", "lake", "river", "ocean", 
    "pond", "species", "tackle", "equipment", "angling", "angling", 
    "video", "watch", "subscribe", "channel", "comment", "like", "share",
    "tip", "trick", "tutorial", "how-to", "guide", "advice", "vlog", 
    "subscribe", "click", "notification", "bell", "new", "latest", "today",
    "recent", "upload", "post", "episode", "season", "series", "show",
    "check", "visit", "website", "shop", "store", "purchase", "buy", "sale",
    "discount", "offer", "promo", "code", "link", "description", "comment",
    "follow", "social", "media", "twitter", "facebook", "instagram",
    "subscribe", "subscribers", "viewer", "viewers", "audience", "fan", 
    "fans", "follower", "followers", "click", "clicks", "watch", "watches",
    "watching", "view", "views", "watcher", "watchers", "video", "videos",
    "clip", "clips", "episode", "episodes", "content", "channel", "channels",
    "show", "shows", "season", "seasons", "series", "playlist", "playlists",
    "channel", "channels", "video", "videos", "upload", "uploads", "watch",
    "watching", "watchers", "viewer", "viewers", "subscribe", "subscribers",
    "like", "likes", "dislike", "dislikes", "comment", "comments", "share",
    "shares", "click", "clicks", "channel", "channels", "video", "videos",
    "watch", "watching", "view", "views", "viewer", "viewers", "subscribe",
    "subscribers", "like", "likes", "comment", "comments", "share", "shares",
    "click", "clicks", "watch", "watching", "view", "views", "subscriber",
    "subscribers", "like", "likes", "comment", "comments", "share", "shares",
    "video", "videos", "channel", "channels", "watch", "watching", "view",
    "views", "subscribe", "subscribers", "like", "likes", "comment", "comments",
    "share", "shares", "click", "clicks", "video", "videos", "channel", "channels",
    "watch", "watching", "view", "views", "subscribe", "subscribers", "like",
    "likes", "comment", "comments", "share", "shares", "click", "clicks",
    "watch", "watching", "view", "views", "subscriber", "subscribers", "like",
    "likes", "comment", "comments", "share", "shares", "fishermen", "caught",
    "huge", "one", "found","back","ever"
]

stop_words = set(stopwords.words('english'))
stop_words.update(custom_stop_words)

def get_lda_topics(vid_id, stop_words=stop_words):
    srt = YouTubeTranscriptApi.get_transcript(vid_id)
    audio_transcription = ""
    for vals in srt:
        audio_transcription += vals['text'] + " "
        
    

    # # Sample audio transcription
    # audio_transcription = out_text

    # Tokenize and preprocess the text
    tokenized_text = [word for word in simple_preprocess(audio_transcription, deacc=True, min_len=2, max_len=15) if word not in stop_words]

    # Create a Gensim Dictionary from the tokenized text
    dictionary = Dictionary([tokenized_text])

    # Convert the tokenized text into a bag-of-words corpus
    corpus = [dictionary.doc2bow(tokenized_text)]

    # Train the LDA model
    num_topics = 10  # Number of topics
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)

    # Print the 10 most frequent topics and their words
    topics = lda_model.show_topics(num_topics=num_topics, num_words=5, formatted=False)

    # Sum values within 10 iterations
    topics_vals = {}

    for i in topics:
        for v in i[1]:
            if v[0] in topics_vals:
                topics_vals[v[0]] += v[1]
            else:
                topics_vals[v[0]] = v[1]
    return topics_vals
