class Solution(object):
    def minCut(self, s):
        """
        :type s: str
        :rtype: int
        """
        n = len(s)
        is_pal = [[False] * n for _ in range(n)]

        for r in range(n):
            for l in range(r + 1):
                if s[l] == s[r] and (r - l <= 2 or is_pal[l + 1][r - 1]):
                    is_pal[l][r] = True

        cuts = [0] * n
        for i in range(n):
            if is_pal[0][i]:
                cuts[i] = 0
            else:
                best = i
                for j in range(i):
                    if is_pal[j + 1][i]:
                        best = min(best, cuts[j] + 1)
                cuts[i] = best
        return cuts[-1]