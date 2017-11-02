import re
import pickle
import os

# Global variables for evaluating the tokenizer
true_negatives = 0
true_positives = 0

# Load list of all programming languages & text emoticons
with open('tokenization/custom_tokenizer/programming_languages.txt', 'r') as file:
    langs = file.read().split()
with open('tokenization/custom_tokenizer/text_emoticons.txt', 'r') as file:
    emoticons = file.read().split()


def _matches(regex):
    """
    Regular expression compiling function decorator.
    Input: regex, function
    Output: Wrapped function
    """
    def match_decorator(fn):
        # compile the regular expression
        automaton = re.compile(regex, 32)
        # function wrappings for the class methods
        fn.split = automaton.split
        fn.match = automaton.match
        fn.search = automaton.search
        return fn

    return match_decorator


@_matches(r'\s+')
def space_tokenizer(sentence):
    """Returns a list of space separated tokens."""
    # __FT__ is a marker for evaluating the tokenizer
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in space_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(<code>.*?<\/code>)')
def code_tokenizer(sentence):
    """Returns a list of tokenized code blocks."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in code_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9]\.[^\s]{2,})')
def url_tokenizer(sentence):
    """Returns a list of tokenized URLs."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in url_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(\W)')
def non_alphanum_tokenizer(sentence):
    """Returns a list of tokenized non alpha-numerals."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in non_alphanum_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'([A-Za-z][A-Za-z0-9_]*(\.[a-z0-9_]+)+[0-9a-z_A-Z])')
def package_tokenizer(sentence):
    """Returns a list of tokenized package names."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in package_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'((.*)?(\/[^/\n ]*)+\/?\n?)')
def filepath_tokenizer(sentence):
    """Returns a list of tokenized filepaths."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in filepath_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(([+|-]?\d+)?\.((\d+)|[\w]))')
def decimal_tokenizer(sentence):
    """Returns a list of tokenized decimal numbers & version numbers."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in decimal_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(\S+\'\S+)')
def contraction_tokenizer(sentence):
    """Returns a list of tokenized contractions."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in contraction_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'([a-zA-z]\.([a-zA-z]\.)+)')
def abbreviation_tokenizer(sentence):
    """Returns a list of tokenized abbreviations."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in abbreviation_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(\.\.\.|->|[(){}\[\],])')
def ellipsis_bracket_tokenizer(sentence):
    """Returns a list of tokenized ellipses and parentheses."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in ellipsis_bracket_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(^[^\/]+[\/][^\/]+$)')
def eitheror_tokenizer(sentence):
    """Returns a list of tokens separated by '/'."""
    if not re.match(r'.*(__FT__).*', sentence):
        return [token for token in eitheror_tokenizer.split(sentence) if token]
    else:
        return [sentence]


@_matches(r'(.*\.[\s]*$)+')
def period_tokenizer(sentence):
    """Returns a list of tokens separated by '.'."""
    if not re.match(r'.*(__FT__).*', sentence):
        idx = sentence.rindex('.')
        return [sentence[:idx], '.']
    else:
        return [sentence]


def mark_tokens(tokens, filter):
    """Marks tokens with '__FT__' to evaluate the performance of the tokenizer."""
    return ['__FT__' + token if filter(token) and '__FT__' not in token else token for token in tokens]


def handle_clitics(token):
    """Handles special clitics in the token."""
    tokens = []
    if token[-1].lower() == 's' and token[-2] in ["'"]:
        tokens.append(token[:-2])
        tokens.append(token[-2:])
    else:
        idx = 0
        sub_tokens = [token]
        length = len(token)
        if length > 1:
            for pos in range(length - 1, 0, -1):
                if token[pos] in ["'"]:
                    if 2 < length and pos + 2 == length and token[-1] == 't' and token[pos - 1] == 'n':
                        pos -= 1
                    sub_tokens.insert(idx, token[:pos])
                    idx += 1
                    sub_tokens[idx] = token[pos:]
        tokens.extend(sub_tokens)
    return tokens


def custom_tokenizer(text):
    global true_positives
    global true_negatives

    # Tokenize inline code blocks
    code_tokenized = code_tokenizer(text)

    # Separate tokens based on whitespace
    space_tokenized = []
    for token in code_tokenized:
        if not code_tokenizer.match(token):
            space_tokenized.extend(space_tokenizer(token))
        else:
            space_tokenized.append(token)

    # Mark text emoticons and programming languages
    emoticon_and_lang_marked_tokens = mark_tokens(space_tokenized, lambda token: token.lower(
    ) in emoticons or token.lower() in langs or code_tokenizer.match(token) is not None)

    # Tokenize ellipses and parentheses
    ellipsis_bracket_tokenized = []
    for token in emoticon_and_lang_marked_tokens:
        ellipsis_bracket_tokenized.extend(ellipsis_bracket_tokenizer(token))

    # Handle special period tokens
    special_periods_tokens = mark_tokens(ellipsis_bracket_tokenized, lambda token: token.lower() in
                                         ['e.g.', 'i.e.', '...', 'etc.'])

    # Get period tokens
    period_tokenized = []
    for token in special_periods_tokens:
        if not code_tokenizer.match(token) and period_tokenizer.match(token):
            returned = period_tokenizer(token)
            period_tokenized.extend(returned)
        else:
            period_tokenized.append(token)

    # Mark text emoticons and programming languages
    emoticon_and_lang_marked_tokens = mark_tokens(period_tokenized, lambda token: token.lower(
    ) in emoticons or token.lower() in langs or code_tokenizer.match(token) is not None)

    # Get contraction tokens
    contraction_tokenized = []
    for token in emoticon_and_lang_marked_tokens:
        if contraction_tokenizer.match(token) is not None:
            contraction_tokenized.extend(['__FT__' + sub_token for sub_token in handle_clitics(token)])
        else:
            contraction_tokenized.append(token)

    # Helper function to check token
    def to_be_filtered(sub_token):
        checklist = [
            ellipsis_bracket_tokenizer.match(sub_token) is None,
            abbreviation_tokenizer.match(sub_token) is None,
            decimal_tokenizer.match(sub_token) is None,
            url_tokenizer.match(sub_token) is None,
            package_tokenizer.match(sub_token) is None,
            filepath_tokenizer.match(sub_token) is None
        ]
        return False in checklist

    # Filter tokens
    filter_marked_tokens = mark_tokens(contraction_tokenized, to_be_filtered)

    # Get non alpha-numerical tokens
    non_alphanum_tokenized = []
    for token in filter_marked_tokens:
        non_alphanum_tokenized.extend(non_alphanum_tokenizer(token))

    # Get tokens separated by '/'
    eitheror_tokenized = []
    for token in non_alphanum_tokenized:
        if eitheror_tokenizer.match(token) is not None and code_tokenizer.match(token[6:]) is None:
            eitheror_tokenized.extend([token.split('/')[0], '/', token.split('/')[1]])
        else:
            eitheror_tokenized.append(token)

    # Evaluate tokenizer
    clean_tokens = []
    for token in eitheror_tokenized:
        if token.find('__FT__') >= 0:
            true_negatives += 1
        else:
            true_positives += 1

    for token in eitheror_tokenized:
        clean_tokens.append(token.replace('__FT__', ''))

    for token in clean_tokens:
        yield token


def tokenize():
    if not os.path.exists('pickles/posts.pkl'):
        print('Please run extract_clean_posts.py to generate pickled file. Exiting...')
        exit(0)

    with open('pickles/posts.pkl', 'rb') as f:
        posts = pickle.load(f)

    f = open('tokenization/custom_tokenizer/tokenized_data.txt', 'w+')

    complete_token_list = []
    post_no = 1
    for post in posts:
        f.write('POST {}\n\n'.format(post_no))
        f.write('{}\n\n'.format(post))
        f.write('{}\n\n'.format('-' * 72))

        tokens = []
        for token in custom_tokenizer(post):
            if token:
                tokens.append(token)

        f.write('[{}]\n\n'.format(', '.join(('"' + token + '"' for token in tokens))))
        f.write('{}\n\n\n\n'.format('=' * 72))
        complete_token_list.extend(tokens)
        post_no += 1

    # Print tokenization results
    print('Total Number of Tokens: ', len(complete_token_list))
    print('True Positives: ', true_positives)
    print('True Negatives: ', true_negatives)

    # Pickle data
    if not os.path.exists('pickles/'):
        os.makedirs('pickles/')
    with open('pickles/tokens.pkl', 'wb') as f:
        pickle.dump(complete_token_list, f)

    f.close()


if __name__ == '__main__':
    tokenize()
