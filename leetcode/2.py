# https://leetcode.com/problems/longest-unequal-adjacent-groups-subsequence-ii/description
class Solution:
    def getWordsInLongestSubsequence(self, words: list[str], groups: list[int]) -> list[str]:
        dp = []
        for word1, group1 in zip(words, groups):
            best_fit = max(
                (q for word2, group2, q in zip(words, groups, dp) 
                    if group1 != group2 and len(word1)==len(word2)
                        and sum(map(lambda a, b: a != b, word1, word2)) < 2
                ),
                key=len, default=[])
            dp.append([*best_fit, word1])
        return max(dp, key=len)
