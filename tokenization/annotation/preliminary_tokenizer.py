import re
import pickle
import os

# Load pickled posts
if not os.path.exists('pickles/posts.pkl'):
    print('Please run extract_clean_posts.py to generate pickled file. Exiting...')
    exit(0)
with open('pickles/posts.pkl', 'rb') as f:
    posts = pickle.load(f)

# Write preliminary tokenization results to ground truth file (to be manually checked & corrected)
f = open('tokenization/annotation/ground_truth.txt', 'w+')

# Extract the first 100 posts
posts = posts[:100]

# Run preliminary tokenizer
post_no = 1
for post in posts:
    f.write('POST {}\n\n'.format(post_no))
    f.write('{}\n\n'.format(post))
    f.write('{}\n\n'.format('-' * 72))

    # Clitics
    post = re.sub(r'\'s', ' \'s', post)
    post = re.sub(r'\'ve', ' \'ve', post)
    post = re.sub(r'n\'t', ' n\'t', post)
    post = re.sub(r'\'re', ' \'re', post)
    post = re.sub(r'\'d', ' \'d', post)
    post = re.sub(r'\'ll', ' \'ll', post)
    post = re.sub(r'\'m', ' \'m', post)

    # Non-alphanumerals
    post = re.sub(r'([^0-9a-zA-Z\'])', r' \1 ', post)

    # Inline code blocks
    post = re.sub(r'<\s*code\s*>', ' <code> ', post)
    post = re.sub(r'<\s*/\s*code\s*>', ' </code> ', post)

    # Words separated by spaces
    post = re.sub(r'\s{2,}', ' ', post)

    tokens = []
    code_block = ''
    code_flag = False
    for word in post.split(' '):
        # Add code blocks to list of tokens
        if code_flag and word == '</code>':
            code_block += word
            tokens.append(code_block.strip())
            code_block = ''
            code_flag = False
        elif word == '<code>':
            code_block += word
            code_flag = True
        elif code_flag:
            code_block += word
        # If not code block, add the word to list of tokens
        else:
            tokens.append(word.strip())

    # Write tokenization results to the ground truth file
    f.write('[{}]\n\n'.format(', '.join(('"' + token + '"' for token in tokens))))
    f.write('{}\n\n\n\n'.format('=' * 72))

    post_no += 1

f.close()
