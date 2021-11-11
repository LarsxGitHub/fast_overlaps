import random, string, math
from tqdm import tqdm
import pybloomfilter, os, glob

DIR='./tmp/'
def get_new_id(ids):
    id = ''.join(random.choice(string.ascii_lowercase) for x in range(32))
    while id in ids:
        id = ''.join(random.choice(string.ascii_lowercase) for x in range(32))
    return id

def sets2bfs(prefixes, N, alpha):
    template = pybloomfilter.BloomFilter(N, alpha, DIR+'template.bf')
    bfs = {}
    codes = {'template'}
    for id, pset in tqdm(prefixes.items()):
        code = get_new_id(codes)
        codes.add(code)
        bfs[id] = template.copy_template(DIR+code+'.bf')
        bfs[id].update(pset)
    return bfs

def bloom_jaccard(bfa, bfb):
    ubf = bfa.copy(DIR+'tmp_u.bf')
    ibf = bfa.copy(DIR+'tmp_i.bf')
    u = len(ubf.union(bfb))
    i = len(ibf.union(bfb))
    ubf.close()
    ibf.close()
    return i/u

def set_jaccard(a, b):
    u = len(a.union(b))
    i = len(a.intersection(b))
    return i/u

def bf_clear(bfs):
    for file in glob.glob(DIR+'*.bf'):
        os.remove(file)
