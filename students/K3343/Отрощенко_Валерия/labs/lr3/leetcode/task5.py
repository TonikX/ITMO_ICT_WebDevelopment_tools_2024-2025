class Solution(object):
    def candy(self, ratings):
        """
        :type ratings: List[int]
        :rtype: int
        """
        n = len(ratings)
        if n == 0:
            return 0
        left = [1] * n
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                left[i] = left[i - 1] + 1
        right = 1
        total = left[-1]
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                right += 1
            else:
                right = 1
            total += max(left[i], right)
        return total