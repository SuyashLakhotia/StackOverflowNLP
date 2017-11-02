import pickle
import xml.etree.ElementTree as ET
import os

# Useful XML Attributes & Values in Posts.xml (non-exhaustive list):
#
# 1. ID
# 2. Body
# 3. PostTypeID: '1' (Question), '2' (Answer)
# 4. AcceptedAnswerID (if PostTypeID = '1')
# 5. ParentID (if PostTypeID = '2')
# 6. AnswerCount (nullable)
# 7. Tags: '&lt;tag_name&gt;' repeated (nullable)
#
# 37,215,530 lines. 37,215,527 post <row>s.

filepath = 'data/uncompressed/Posts.xml'

threads_threshold = 500
tag = '<java>'  # ET parses &lt; and &gt;

question_posts = set()
threads = {}
num_of_threads = 0

# Get threads from XML file
for event, elem in ET.iterparse(filepath):
    if elem.tag == 'row':
        attr = elem.attrib

        # Add question post if it has the needed tag & enough answers
        if attr['PostTypeId'] == '1' and attr['Tags'].find(tag) != -1 and int(attr['AnswerCount']) >= 1:
            threads[attr['Id']] = []
            threads[attr['Id']].append(attr)
            question_posts.add(attr['Id'])
            num_of_threads += 1
        # Add answer post if corresponding question post has been added
        elif attr['PostTypeId'] == '2' and attr['ParentId'] in question_posts:
            threads[attr['ParentId']].append(attr)

        if num_of_threads >= threads_threshold:
            # Check for valid threads (i.e. >= 2 posts)
            num_of_valid_threads = 0
            for posts in list(threads.values()):
                if len(posts) >= 2:
                    num_of_valid_threads += 1

            # Stop searching once threshold is met
            if num_of_valid_threads >= threads_threshold:
                break

# Delete threads that are not valid
for question_id, posts in list(threads.items()):
    if len(posts) < 2:
        del threads[question_id]

# Pickle data
if not os.path.exists('pickles/'):
    os.makedirs('pickles/')
with open('pickles/threads.pkl', 'wb') as f:
    pickle.dump(threads, f)
