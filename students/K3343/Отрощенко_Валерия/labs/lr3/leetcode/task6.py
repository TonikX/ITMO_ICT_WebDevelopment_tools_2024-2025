class Solution(object):
    def shortestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        if not s:
            return ""
        rev = s[::-1]
        t = s + "#" + rev
        lps = [0] * len(t)
        j = 0
        for i in range(1, len(t)):
            while j > 0 and t[i] != t[j]:
                j = lps[j - 1]
            if t[i] == t[j]:
                j += 1
                lps[i] = j
        longest = lps[-1]
        return rev[:len(s) - longest] + s