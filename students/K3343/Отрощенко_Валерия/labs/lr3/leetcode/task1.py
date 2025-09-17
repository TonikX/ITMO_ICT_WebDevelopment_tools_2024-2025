class Solution(object):
    def findLadders(self, beginWord, endWord, wordList):
        """
        :type beginWord: str
        :type endWord: str
        :type wordList: List[str]
        :rtype: List[List[str]]
        """
        wordSet = set(wordList)
        if endWord not in wordSet:
            return []

        from collections import deque, defaultdict

        parents = defaultdict(set)
        level = {beginWord}
        found = False
        alpha = [chr(ord('a') + i) for i in range(26)]

        while level and not found:
            next_level = set()
            for w in level:
                if w in wordSet:
                    wordSet.remove(w)
            for w in level:
                w_list = list(w)
                for i in range(len(w_list)):
                    orig = w_list[i]
                    for c in alpha:
                        if c == orig:
                            continue
                        w_list[i] = c
                        nw = ''.join(w_list)
                        if nw in wordSet:
                            if nw == endWord:
                                found = True
                            if nw not in next_level:
                                next_level.add(nw)
                            parents[nw].add(w)
                    w_list[i] = orig
            level = next_level

        if not found:
            return []

        res = []
        path = [endWord]

        def backtrack(word):
            if word == beginWord:
                res.append(path[::-1])
                return
            for p in parents[word]:
                path.append(p)
                backtrack(p)
                path.pop()

        backtrack(endWord)
        return res