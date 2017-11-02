import pickle
import re
import html
import os

# Load pickled threads
if not os.path.exists('pickles/threads.pkl'):
    print('Please run retrieve_threads.py to generate pickled file. Exiting...')
    exit(0)
with open('pickles/threads.pkl', 'rb') as f:
    threads = pickle.load(f)

# Extract the body of every post
posts = []
for thread_key in list(threads.keys()):
    thread = threads[thread_key]
    for post in thread:
        posts.append(post['Body'])

# Sanitize the content of each post
for i in range(len(posts)):
    posts[i] = re.sub(r'<pre>(.|\n)*</pre>', '', posts[i])  # remove code snippets
    posts[i] = re.sub(r'<(a|/a).*?>', '', posts[i])  # remove links (but not text that is hyperlinked)
    posts[i] = re.sub(r'(?i)<(?!code|/code).*?>', '', posts[i])  # remove html tags except <code></code>
    posts[i] = re.sub(r'\n{3,}', '\n\n', posts[i])  # remove multiple (i.e. >= 3) consecutive '\n'
    posts[i] = posts[i].strip()  # strip any extra whitespace
    posts[i] = html.unescape(posts[i])  # unescape HTML entities (e.g. &amp;)

# Pickle data
if not os.path.exists('pickles/'):
    os.makedirs('pickles/')
with open('pickles/posts.pkl', 'wb') as f:
    pickle.dump(posts, f)
