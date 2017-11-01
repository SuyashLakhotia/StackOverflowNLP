import re
import pickle
import nltk

with open('pickles/posts.pkl', 'rb') as f:
    posts = pickle.load(f)

with open('data_analysis/stop_words.txt', 'r') as f:
    stop_words = [line.rstrip() for line in f]

porter_stemmer = nltk.stem.porter.PorterStemmer()

words = {}  # dictionary of words {word: count}
stems = {}  # dictionary of stems {stem: { 'orig_words': (set), 'count': 123 }, ...}

for post in posts:
    post = re.sub(r'<code>.*</code>', '', post)  # remove inline code snippets

    for paragraph in post.split('\n'):
        paragraph = paragraph.lower()  # lowercase text
        tokens = nltk.word_tokenize(paragraph)

        for token in tokens:
            token = re.sub(r'[^a-z]', '', token)  # remove any non-alphabet characters
            if token == '' or token in stop_words:
                continue

            if token in words.keys():
                words[token] += 1
            else:
                words[token] = 1

            stem = porter_stemmer.stem(token)
            if stem in stems:
                stems[stem]['count'] += 1
                stems[stem]['orig_words'].add(token)
            else:
                stems[stem] = {}
                stems[stem]['count'] = 1
                stems[stem]['orig_words'] = set([token])

with open('pickles/stems.pkl', 'wb') as f:
    pickle.dump(stems, f)

frequent_words = sorted(words, key=words.__getitem__, reverse=True)[:20]
frequent_stems = sorted(stems.items(), key=lambda k_v: k_v[1]['count'], reverse=True)[:20]

with open('data_analysis/frequent_words.txt', 'w') as f:
    for word in frequent_words:
        f.write(str(word) + ': ' + str(words[word]) + '\n')

with open('data_analysis/frequent_stems.txt', 'w') as f:
    for stem_dict in frequent_stems:
        f.write(str(stem_dict) + '\n')
