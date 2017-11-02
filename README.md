# NLP for Stack Overflow Posts

This repository contains the source code used to perform basic NLP tasks on posts extracted from Stack Overflow.

### Team

1. Suyash Lakhotia ([SuyashLakhotia](https://github.com/SuyashLakhotia))
2. Nikhil Venkatesh ([nikv96](https://github.com/nikv96))
3. Shantanu Jaiswal ([shantanuj](https://github.com/shantanuj))
4. Jacob Sunny ([jacobsunny1995](https://github.com/jacobsunny1995))
5. Shantanu Kamath ([ShantanuKamath](https://github.com/ShantanuKamath))

## Setup

This project is entirely written in [Python 3](https://www.python.org/downloads/) and depends on the packages listed in `requirements.txt`. In order to setup your development environment, run:

```
$ pip install -r requirements.txt
```

You can also find a complete list of dependencies at the end of this document.

You will also need to download a few NLTK pickled models and corpora (`punkt`, `averaged_perceptron_tagger`, `wordnet`) that our project depends on. On a Python interpreter, run the following:

```
>>> import nltk
>>> nltk.download('punkt')
>>> nltk.download('averaged_perceptron_tagger')
>>> nltk.download('wordnet')
```

## Running StackOverflowNLP

All codes in this project must be run from the root of this repository.

### Dataset Collection

The first step is to download the Stack Overflow data dump (i.e. `stackoverflow.com-Posts.7z`) from [Internet Archive](https://archive.org/details/stackexchange) and uncompress the file. Set the `filepath` variable in `dataset_collection/retrieve_threads.py` to point to the uncompressed `Posts.xml` and run the following:

```
$ python dataset_collection/retrieve_threads.py
$ python dataset_collection/thread_stats.py
$ python dataset_collection/extract_clean_posts.py
$ python dataset_collection/post_stats.py
```

Alternatively, you can use the 500 extracted threads available in `pickles/threads.pkl` and sanitized posts in `pickles/posts.pkl`. These files are what the rest of the project uses and will be created if you run the above scripts.

### Dataset Analysis

To find the most frequent words & stems in the dataset, run:

```
$ python data_analysis/stemming.py
```

This will store the most frequent words and the most frequent stems in the files `data_analysis/frequent_words.txt` and `data_analysis/frequent_stems.txt` respectively.

To run POS tagging on the first 10 sentences of the dataset, run:

```
$ python data_analysis/pos_tagging.py
```

This will store the original sentences and corresponding POS tags in the file `data_analysis/sentences_pos_tags.txt`.

### Tokenization

Since off-the-shelf tokenizers are not robust enough to handle tokens that are specific to a particular subject (in this case, computer programming), we built our own custom tokenizer.

The token definition can be found in `tokenization/annotation/token_definition.txt`. Based on this token definition, a ground truth is established for the first 100 posts in `tokenization/annotation/ground_truth.txt`, which will be used to benchmark the performance of our custom tokenizer. This ground truth is created by running a preliminary tokenizer (`tokenization/annotation/preliminary_tokenizer.py`) and manually correcting the tokenization.

The actual custom tokenizer built based on regular expression rules, is implemented in `tokenization/custom_tokenizer/tokenizer.py`. A sample tokenized sentence is shown below:

**Original Sentence:**

```
Maybe this might help: JSefa

You can read CSV file with this tool and serialize it to XML.
```

**Tokens Extracted:**

```
["Maybe", "this", "might", "help", ":", "JSefa", "You", "can", "read", "CSV", "file", "with", "this", "tool", "and", "serialize", "it", "to", "XML", "."]
```

### Further Analysis

Further analysis is performed by investigating irregular tokens (i.e. non-English words) using the custom tokenizer in `tokenization/custom_tokenizer/further_analysis.py`.

### Application: Detecting Question Similarity

Given a question, our application outputs similar questions (and possible duplicates) by using a weighted ensemble of WordNet synonym distance, word vector distance and word mover's distance.

We obtain Stack Exchange specific word vectors from [AskUbuntu](https://github.com/taolei87/askubuntu), and further prune it (to save memory) by only including word vectors for words in our corpus' vocabulary.

Our application's source code is located in `application/application.py`.

To use the application, run:

```
$ python application/application.py
```

Upon running, either enter `1` to enter a question or `-1` to exit the program when the application prompts for an instruction.

Depending on the underlying processor, finding duplicate questions may take anywhere between 10 seconds and 1 minute.

## Dependencies

- NLTK v3.2.5 (http://www.nltk.org/)
- Matplotlib v2.1.0 (https://matplotlib.org/)
- PyEnchant v1.6.11 (http://pythonhosted.org/pyenchant/)
- Gensim v3.0.1 (https://radimrehurek.com/gensim/) 
- scipy v0.18.1 (https://www.scipy.org/)
- pyemd v0.4.4 (https://github.com/wmayner/pyemd) 

> Please note that these Python packages may depend on other Python packages, so it is advised to simply use the `pip` command described in **Setup** above.

****

***Disclaimer:*** This repo is no longer maintained and was submitted as part of the course project for CZ 4045 Natural Language Processing at NTU in AY 17/18 Semester 1.
