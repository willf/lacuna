# Lacuna

Just saving code here temporarily.

```python
import math
from collections import Counter, namedtuple
from itertools import islice

# Set up a named tuple for sequence, log_probability
Result = namedtuple("Result", ["sequence", "log_probability"])


def log_prob(p):
    return math.log(p)


def suffixes(s, k=1):
    # return all suffixes of string of length k, k-1, k-2, ... 1
    # return in that order (of longest to shortest)
    for i in range(min(len(s), k), 0, -1):
        yield s[-i:]


def ngrams(s, k=1):
    for i in range(len(s) - k + 1):
        yield s[i : i + k]


def sliding_window(s, k=1):
    for i in range(len(s) - k + 1):
        yield s[i : i + k]


class TransitionMatrixWithBackoff:
    def __init__(self, k=1, default_probability=1e-5, BOS="␂", EOS="␃"):
        self.BOS = BOS
        self.EOS = EOS
        self.k = k
        self.default_probability = default_probability
        self.counters = {}
        self.compiled = False
        for i in range(k):
            self.counters[i] = Counter()
        self.transitions = {}
        for i in range(k):
            self.transitions[i] = {}

    def add(self, sequence):
        # ok, we want to add the sequence for example abcdef to the transition matrix with for example k=4
        # then we want to add the following ngrams:
        # onegram: ␂, a, b, c, d, e, f, ␃
        # bigram: ␂a, ab, bc, cd, de, ef, f␃
        # trigram: ␂ab, abc, bcd, cde, def, ef␃
        # fourgram: ␂abc, abcd, bcde, cdef, def␃
        self.compiled = False
        for i in range(self.k):
            extended_sequence = sequence  # self.BOS + sequence + self.EOS
            for ngram in ngrams(extended_sequence, i + 1):
                # print("Adding [", ngram, "]")
                self.counters[i][ngram] += 1

    def compile(self):
        for i in range(self.k):
            s = sum(self.counters[i].values())
            self.transitions[i] = {
                suffix: count / s for suffix, count in self.counters[i].items()
            }

    def __getitem__(self, sequence):
        # print("Looking for [", sequence, "]")
        if not self.compiled:
            self.compile()
            self.compiled = True
        for suffix in suffixes(sequence, self.k):
            # print("Looking for suffix [", suffix, "] with k=", self.k)
            if suffix in self.transitions[len(suffix) - 1]:
                return self.transitions[len(suffix) - 1][suffix]
        return self.default_probability

    def read(self, filename):
        with open(filename, "r") as f:
            for line in f:
                self.add(line.lower())

    def alphabet(self):
        return set(self.counters[0].keys())


# x = TransitionMatrixWithBackoff(2)
# x.add('ACGT')


# Problem statement:
# Given:
# 1. A transition matrix Transition, which is the P(x | S) where
#    x is the next character and S is the n previous characters (ngram transition matrix)
# 2. # 3. A set of characters A, which is the alphabet of the sequence
# 3. A query string Q, which is a string of characters, in which
#    each character is either an element the the alphabet A or a '?'
#    (which represents an unknown character)
# Yield:
#    In descending order of probability, the most probable *sequences* of characters,
#    along with their probabilities
#    that matches the query string Q, given the transition matrix Transition
# Note that if the letter is given, then the probability of that letter is 1
# and the probability of the other letters is 0. If the letter is not given, then
# the probability of that letter is given by the transition matrix.
# For example,
# Transition = {'A': {'A': 0.1, 'C': 0.4, 'G': 0.5, 'T': 0.0},
#               'C': {'A': 0.5, 'C': 0.1, 'G': 0.0, 'T': 0.4},
#               'G': {'A': 0.0, 'C': 0.0, 'G': 0.1, 'T': 0.9},
#               'T': {'A': 0.0, 'C': 0.0, 'G': 0.0, 'T': 1.0}}
# A = 'ACGT'
# Q = 'A?T'
# Then max_probable_sequences(Transition, A, Q) will yield:
# ('AAT', 0.5)
# ('ACT', 0.4)
# ('AGT', 0.05)
# ('ATT', 0.01)
# etc


def max_probable_sequences(Transition, A, Q):
    return sorted(
        unsorted_max_probable_sequences(Transition, A, Q),
        key=lambda x: x.log_probability,
        reverse=True,
    )


def unsorted_max_probable_sequences(Transition, A, Q):
    for result in max_probable_sequences_recur(
        Transition, A, sliding_window(Q, Transition.k), []
    ):
        yield result


def max_probable_sequences_recur(Transition, A, Qs, results):
    for q in Qs:
        if q[-1] != "?":
            # Get the probability q[-1] given q[:-1]
            prob = Transition[q]
            lp = log_prob(prob)
            # for each of the results, add the last character and the probability
            # if the result is empty, cause we are at the start, then add a (list of) a new result
            if results == []:
                results = [Result(q, lp)]
            else:
                results = [
                    Result(r.sequence + q[-1], r.log_probability + lp) for r in results
                ]
        else:
            # If the last character is '?', then for each character in the alphabet A, then
            # add the character and the probability to a new list of result for each of the results
            if results == []:
                results = [Result(a, log_prob(Transition[a])) for a in A]
            else:
                results = [
                    Result(
                        r.sequence + a,
                        r.log_probability + log_prob(Transition[r.sequence + a]),
                    )
                    for r in results
                    for a in A
                    if Transition[r.sequence + a] > Transition.default_probability
                ]
    for r in results:
        yield r


# Test the function
Transition = TransitionMatrixWithBackoff(6)
Transition.read("/Users/willf/projects/aima-python/aima-data/EN-text/federalist.txt")

A = Transition.alphabet()
print(A)
Q = "friend?"
results = islice(max_probable_sequences(Transition, A, Q), 10)
for r in results:
    print(r.sequence, r.log_probability, math.exp(r.log_probability))
```
