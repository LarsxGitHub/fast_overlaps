from utils import sets2bfs, bloom_jaccard, set_jaccard, bf_clear
import glob, gzip, sys, math
from collections import defaultdict
from datetime import datetime
import numpy as np
from tqdm import tqdm

def read_prefixes():
    # just loads a bunch of prefix files
    DIR='../data/'
    prefixes = defaultdict(set)
    for file in tqdm(glob.glob(DIR+'*v4.gz')[:int(sys.argv[2])]):
        id = file.split('/')[-1].split('.')[0]
        with gzip.open(file, 'rt') as ifile:
            for line in ifile:
                prefixes[id].add(line.rstrip())
    return prefixes

def diff(a,b):
    if a > b:
        return a-b
    return b-a

def egligable_pair(a,b, LIM = 10.0):
    # checks for same cardinality order of magnitude
    if a > b:
        if a/b < LIM: return True
        return False
    if b/a < LIM: return True
    return False


# Read Prefixes
print('Reading prefixes')
prefixes = read_prefixes()
print('Finished reading prefixes')

# some tests went slightly above the provided alpha when using the exact
# max number of prefixes.
# we allocate 3 times usual BF capacity to ensure to stay below alpha ...
N = max([3*len(x) for x in prefixes.values()])
alpha = float(sys.argv[1])
alpha_fixed = 1.0-math.sqrt((1.0-alpha))

# Produce BFs
print('Producing bloom filters')
bfs = sets2bfs(prefixes, N, alpha_fixed)
print('Finished producing bloom filters')


thekeys = list(prefixes.keys())
K = len(thekeys)
diff_jaccard = []
diff_times = []
pbar = tqdm(total=K*(K-1)/2)

# NxN comparison
for i in range(K):
    for j in range(i+1, K):
        pbar.update(1)
        pa, pb, ba, bb = prefixes[thekeys[i]], prefixes[thekeys[j]], bfs[thekeys[i]], bfs[thekeys[j]]
        if not egligable_pair(len(pa), len(pb)): continue
        ta = datetime.now()
        sj = set_jaccard(pa, pb)
        tb =  datetime.now()
        bfj = bloom_jaccard(ba, bb)
        tc =  datetime.now()
        diff_jaccard.append(diff(sj, bfj))
        first = (tb - ta).microseconds
        second = (tc - tb).microseconds
        diff_times.append(second/first)

pbar.close()


print('\n\n############ Statistics for alpha = '+str(alpha)+' ############\n')

print('Ran %d comparisons in total.\n' % (len(diff_jaccard)))
print('0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99 percentile for jaccard inaccuracy [numerical difference]:\n', *np.percentile(diff_jaccard, [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]))
print('\n0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99 percentile for saved time [percent milliseconds]:\n', *np.percentile(diff_times, [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]))
print()

for bf in bfs.values():
    bf.close()

bf_clear(bfs)
