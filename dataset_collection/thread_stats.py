import pickle
import matplotlib.pyplot as plt
import os

# Load pickled threads
if not os.path.exists('pickles/threads.pkl'):
    print('Please run retrieve_threads.py to generate pickled file. Exiting...')
    exit(0)
with open('pickles/threads.pkl', 'rb') as f:
    threads = pickle.load(f)

num_of_posts = 0
thread_stats = {}
for question_id, posts in list(threads.items()):
    posts_in_thread = len(posts)
    num_of_posts += posts_in_thread

    if posts_in_thread in thread_stats:
        thread_stats[posts_in_thread] += 1
    else:
        thread_stats[posts_in_thread] = 1

# Print dataset statistics
print('Threads: %d' % (len(threads)))
print('Posts: %d' % (num_of_posts))
print('Questions: %d' % (len(threads)))
print('Answers: %d' % (num_of_posts - len(threads)))
print('Thread Count per No. of Posts: %s' % (str(thread_stats)))

# Look for 'plots' directory
if not os.path.exists('plots/'):
    os.makedirs('plots/')

# Plot thread_stats
plt.figure()
plt.bar(list(thread_stats.keys()), list(thread_stats.values()))
plt.xlabel('No. of Posts')
plt.ylabel('No. of Threads')
plt.tight_layout()
plt.savefig('plots/thread_stats.png', dpi=800)
plt.close('all')
