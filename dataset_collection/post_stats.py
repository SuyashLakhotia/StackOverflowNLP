import pickle
import re
import matplotlib.pyplot as plt
import nltk
import os

# Load pickled posts
if not os.path.exists('pickles/posts.pkl'):
    print('Please run extract_clean_posts.py to generate pickled file. Exiting...')
    exit(0)
with open('pickles/posts.pkl', 'rb') as f:
    posts = pickle.load(f)

# Obtain the token count for each post
post_length = {}
for post in posts:
    post = re.sub(r'<code>.*</code>', '', post)  # remove inline code snippets
    words = nltk.word_tokenize(post)

    if len(words) in post_length:
        post_length[len(words)] += 1
    else:
        post_length[len(words)] = 1

# Look for 'plots' directory
if not os.path.exists('plots/'):
    os.makedirs('plots/')

# Plot token count
plt.figure()
plt.bar(list(post_length.keys()), list(post_length.values()), width=1.0)
plt.xlabel('Word Count')
plt.ylabel('No. of Posts')
plt.tight_layout()
plt.savefig('plots/post_length.png', dpi=800)
plt.close('all')
