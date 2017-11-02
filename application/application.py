import nltk
import numpy as np
import pickle
import html
import re
import time
import os
from nltk import word_tokenize, pos_tag

try:
    from nltk.corpus import wordnet as wn
except:
    nltk.download("wordnet")
    from nltk.corpus import wordnet as wn

vectors_dir = "application/task_relevant_vectors.txt"


def test_nltk_packages():
    test_string = "Hello world"
    try:
        tokens = word_tokenize(test_string)
    except:
        nltk.download('punkt')
        tokens = word_tokenize(test_string)
    try:
        tags = pos_tag(tokens)
    except:
        nltk.download("averaged_perceptron_tagger")
        tags = pos_tag(tokens)
    try:
        synsets = wn.synsets('world', 'n')[0]
    except:
        nltk.download("wordnet")
        synsets = wn.synsets('world', 'n')[0]
test_nltk_packages()


def get_stop_words(directory="data_analysis/stop_words.txt"):
    with open(directory, 'r') as f:
        stop_words = [line.rstrip() for line in f]
    return stop_words

stop_words = get_stop_words("data_analysis/stop_words.txt")
vocab = []  # stores all tokens provided in dataset


def clean_q(qs):
    qs = re.sub(r'<pre>(.|\n)*</pre>', '', qs)  # remove code snippets
    qs = re.sub(r'<(a|/a).*?>', '', qs)  # remove links (but not text that is hyperlinked)
    qs = re.sub(r'(?i)<(?!code|/code).*?>', '', qs)  # remove html tags except <code></code>
    qs = re.sub(r'\n{3,}', '\n\n', qs)  # remove multiple (i.e. >= 3) consecutive '\n'
    qs = qs.strip()  # strip any extra whitespace
    qs = html.unescape(qs)  # unescape HTML entities (e.g. &amp;)
    return qs


def clean_text_and_tokenize(q_string):
    '''Replace parts with custom tokenizer and cleaners if needed'''
    q_tokens = word_tokenize(q_string)  # replace with our own if needed
    q_string_clean = [token.lower() for token in q_tokens if token.lower() not in stop_words]
    vocab.extend(q_string_clean)
    return q_string_clean


def get_all_existing_questions(directory="pickles/threads.pkl"):  # give the threads here
    with open(directory, 'rb') as f:
        threads = pickle.load(f)
    qs = [clean_q(threads[i][0]['Body']) for i in threads.keys()]
    return qs


def obtain_only_relevant_vectors(word_vectors):
    ndims = word_vectors.vector_size
    res_vectors = []
    words_done = []
    for word in set(vocab):
        try:
            res_vectors.append((word, list(word_vectors[word])))
        except:
            continue
    with open('task_relevant_vectors.txt', 'w') as f:
        f.write("{} {}\n".format(len(res_vectors), ndims))
        print(len(res_vectors))
        for word_vec_tuple in res_vectors:
            vec = [str(i) for i in word_vec_tuple[1]]
            f.write("{} {}\n".format(str(word_vec_tuple[0]), ' '.join(vec)))


def get_wnet_wordtag(word_tag):
    if (word_tag.startswith('N')):
        return 'n'
    if (word_tag.startswith('V')):
        return 'v'
    if (word_tag.startswith('J')):
        return 'a'
    if (word_tag.startswith('R')):
        return 'r'
    return None


def get_synonyms_wnet(word, word_tag):
    wnet_tag = get_wnet_wordtag(word_tag)
    if (wnet_tag is None):
        return None  # no synonyms
    try:
        return wn.synsets(word, wnet_tag)[0]
    except:
        return None  # no synonym found


def question_similarity_wnet(q1, q2, symm=True):
    '''
    Inputs q1, q2 are assumed to be cleaned string tokens lists representing questions
    '''
    if (symm):
        return (question_similarity_wnet(q1, q2, False) + question_similarity_wnet(q2, q1, False)) / 2
    '''Tokenization and tagging'''

    q1_tagged = pos_tag(q1)
    q2_tagged = pos_tag(q2)

    '''Obtain synonyms'''
    synsets1 = [get_synonyms_wnet(*word_and_tag) for word_and_tag in q1_tagged]
    synsets2 = [get_synonyms_wnet(*word_and_tag) for word_and_tag in q2_tagged]
    score, count = 0.0, 0

    for synset in synsets1:
        try:
            best_score = max([synset.path_similarity(ss) for ss in synsets2 if ss])
        except:
            best_score = None
        if best_score is not None:
            score += best_score
            count += 1
    try:
        score /= count
    except:
        return -1
    return score


from gensim.models.keyedvectors import KeyedVectors
'''
Learn word vectors through pretrained and continue training to obtain data specific word embeddings --> resolves issue with unknown words. Then, use wmd implementation and simple averaged vector representation.
'''
word_vectors_loaded = False
try:
    print("Loading word vectors...")
    word_vectors = KeyedVectors.load_word2vec_format(vectors_dir, binary=False)
    ndims = word_vectors.vector_size
    word_vectors_loaded = True
    print("Loaded word vectors")
except:
    print("Failed in loading word vectors")

np.random.seed(5)
out_of_vocab_wordvec = np.random.random((1, ndims))


def get_sen_vector(tokenized_cleaned_sentence_list, reduced_by_words=True):
    '''
    Get sentence vector averaged by words
    '''
    sentence_vector_1 = np.zeros((len(tokenized_cleaned_sentence_list), ndims))
    count_out_of_vocab = 0
    for i, token in enumerate(tokenized_cleaned_sentence_list):
        try:
            sentence_vector_1[i] = word_vectors[token]
        except:
            sentence_vector_1[i] = out_of_vocab_wordvec
    if (reduced_by_words):
        sentence_vector_averaged_by_words = np.mean(sentence_vector_1, axis=0)
        return sentence_vector_averaged_by_words
    else:
        return sentence_vector_1


def cosine_similarity(vec1, vec2):
    cos_thet = (np.dot(vec1, np.transpose(vec2))) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return cos_thet


def activation(x):
    '''Formula for activation function'''
    return 1 / (1 + np.exp(-x))


def word_mov_distance(q1_list, q2_list):
    '''Inputs are q1 and q2 clean tokenized lists'''
    if (word_vectors_loaded):
        return word_vectors.wmdistance(q1_list, q2_list)
    else:
        return 0


def avg_w2v(q1, q2):
    '''Inputs are q1 and q2 clean tokenized lists'''
    if (not word_vectors_loaded):
        return 0
    s1 = get_sen_vector(q1)
    s2 = get_sen_vector(q2)
    return cosine_similarity(s1, s2)


def get_similarity(q1, q2, print_out=False):
    # retrieve cleaned and tokenized questions
    q1, q2 = clean_text_and_tokenize(q1), clean_text_and_tokenize(q2)

    # determine similarity scores of the questions using word2vec, word_move_distance and wordnet
    similarity_w2v = avg_w2v(q1, q2)
    similarity_wmd = activation(1 / (word_mov_distance(q1, q2) + 1e-10))
    similarity_wordnet = question_similarity_wnet(q1, q2)
    if (print_out):
        print("Similarity score word2vec averaged vectors: {}".format(similarity_w2v))
        print("Similarity score word mover distance: {}".format(similarity_wmd))
        print("Similarity wordnet: {}".format(similarity_wordnet))
    try:
        if (word_vectors_loaded):
            average_similarity = 0.43 * similarity_wmd + 0.42 * similarity_wordnet + 0.15 * similarity_w2v
        else:
            average_similarity = similarity_wordnet
        return average_similarity
    except:
        return 0


def most_similar_to_q(q1, k=5, need_qs=False):
    if not os.path.exists('pickles/threads.pkl'):
        print('Please run retrieve_threads.py to generate pickled file. Exiting...')
        exit(0)

    all_existing_questions_list = get_all_existing_questions("pickles/threads.pkl")
    similarity_scores = [(i, get_similarity(q1, qk)) for i, qk in enumerate(all_existing_questions_list)]
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    print("Most similar {} questions:\n".format(k))
    count = 0
    for sim_id, sim_score in similarity_scores:
        if (count > k):
            break
        print("{}".format(''.join(['*'] * 50)))
        print("Question ID:{}\n --------------------------\n {} \n Similarity score:{}"
              .format(sim_id,
                      all_existing_questions_list[sim_id],
                      sim_score))
        if (sim_score > 0.9):
            print("Possible duplicate!")
        count += 1
    if (need_qs):
        return [(all_existing_questions_list[sim_id], sim_score) for sim_id, sim_score in similarity_scores]


def main():
    choice = 1
    while(True):
        choice = int(input("1: Enter Question; -1: Exit Program\n"))  # supply list of questions
        if (choice == -1):
            # user exit
            break
        if (choice == 1):
            ques = input("Enter Question: ")
            k = 5  # number of similar questions to find
            print("......Finding {} most similar questions and possible duplicates......".format(k))
            most_similar_to_q(ques)


if __name__ == '__main__':
    main()
