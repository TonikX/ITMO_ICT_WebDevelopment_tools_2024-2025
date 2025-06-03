class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        window = []
        max_len = 0
        left = 0

        for right in range(len(s)):
            while s[right] in window:
                window.pop(0)
                left += 1
            window.append(s[right])
            max_len = max(max_len, len(window))

        return max_len
