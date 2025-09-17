class Solution(object):
    def ladderLength(self, beginWord, endWord, wordList):
        """
        :type beginWord: str
        :type endWord: str
        :type wordList: List[str]
        :rtype: int
        """
        wordSet = set(wordList)
        if endWord not in wordSet:
            return 0

        begin_front = {beginWord}
        end_front = {endWord}
        visited = set([beginWord, endWord])
        step = 1
        alpha = [chr(ord('a') + i) for i in range(26)]

        while begin_front and end_front:
            if len(begin_front) > len(end_front):
                begin_front, end_front = end_front, begin_front

            next_front = set()
            for w in begin_front:
                w_list = list(w)
                for i in range(len(w_list)):
                    orig = w_list[i]
                    for c in alpha:
                        if c == orig:
                            continue
                        w_list[i] = c
                        nw = ''.join(w_list)
                        if nw in end_front:
                            return step + 1
                        if nw in wordSet and nw not in visited:
                            visited.add(nw)
                            next_front.add(nw)
                    w_list[i] = orig
            begin_front = next_front
            step += 1

        return 0