import re
import pickle
import nltk
import os

# Load pickled posts
if not os.path.exists('pickles/posts.pkl'):
    print('Please run extract_clean_posts.py to generate pickled file. Exiting...')
    exit(0)
with open('pickles/posts.pkl', 'rb') as f:
    posts = pickle.load(f)

sentences = []  # list of sentences to tag
pos_tags = {}  # {sentence: [(Word, POS Tag), (Word, POS Tag)...]}

# Perform sentence tokenization to get sentences
for post in posts:
    post = re.sub(r'<code>.*</code>', '', post)  # remove inline code snippets

    for paragraph in post.split('\n'):
        if len(paragraph) == 0:
            continue
        sentences = sentences + nltk.tokenize.sent_tokenize(paragraph)  # returns tokenized sentence

    if len(sentences) >= 10:
        break

# Perform word tokenization on the sentences
for sentence in sentences:
    if len(pos_tags) == 10:
        break
    words = nltk.word_tokenize(sentence)  # returns word tokens
    pos_tags[sentence] = nltk.pos_tag(words)  # returns list of (Word, POS Tag) tuples

# Write original sentences and POS tags to file
with open('data_analysis/sentences_pos_tags.txt', 'w') as f:
    for key in list(pos_tags.keys()):
        f.write(str(key) + '\n')
        f.write(str(pos_tags[key]) + '\n')
        f.write('\n----\n' + '\n')

# Pickle data
if not os.path.exists('pickles/'):
    os.makedirs('pickles/')
with open('pickles/pos_tags.pkl', 'wb') as f:
    pickle.dump(pos_tags, f)
