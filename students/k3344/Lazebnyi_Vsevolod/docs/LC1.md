# Долг Литкод

## Задача №1 - https://leetcode.com/problems/integer-to-roman/
```python
class Solution:
    def intToRoman(self, num: int) -> str:
        symList = [
            ["I", 1], ["IV", 4], ["V", 5], ["IX", 9],
            ["X", 10], ["XL", 40], ["L", 50], ["XC", 90],
            ["C", 100], ["CD", 400], ["D", 500], ["CM", 900],
            ["M", 1000]
        ]

        res = ""
        for sym, val in reversed(symList):
            count = num // val
            if count:
                res += sym * count
                num %= val

        return res
```
## Задача №2 - https://leetcode.com/problems/sort-an-array/
```python
class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        def shell_sort(nums, n):
            gap = n // 2
            while gap >= 1:
                for i in range(gap, n):
                    tmp = nums[i]
                    j = i - gap
                    while j >= 0 and nums[j] > tmp:
                        nums[j + gap] = nums[j]
                        j -= gap
                    nums[j + gap] = tmp
                gap //= 2
        
        n = len(nums)
        if n == 1:
            return nums
        shell_sort(nums, n)
        return nums
```
## Задача №3 - https://leetcode.com/problems/maximum-number-of-points-with-cost/
```python
class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        num_columns = len(points[0])
        dp = points[0][:]
        for row in points[1:]:
            new_dp = [0] * num_columns
            left_max = -999999999999999
            for j in range(num_columns):
                left_max = max(left_max, dp[j] + j)
                new_dp[j] = max(new_dp[j], row[j] + left_max - j)
            right_max = -999999999999999
            for j in range(num_columns - 1, -1, -1):
                right_max = max(right_max, dp[j] - j)
                new_dp[j] = max(new_dp[j], row[j] + right_max + j)
            dp = new_dp
        return max(dp)
```
## Задача №4 - https://leetcode.com/problems/largest-number/
```python
class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        for i, num in enumerate(nums):
            nums[i] = str(num)
        def compare(n1, n2):
            if n1 + n2 > n2 + n1:
                return -1
            else:
                return 1
        nums = sorted(nums, key=cmp_to_key(compare))
        return str(int("".join(nums)))
```
## Задача №5 - https://leetcode.com/problems/multiply-strings/
```python
class Solution:
    def multiply(self, num1: str, num2: str) -> str:
        return str(int(num1)*int(num2))
```
## Задача №6 - https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/description/
```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        return sum((prices[idx + 1] - prices[idx]) for idx in range(len(prices) - 1) if prices[idx] < prices[idx + 1])
```
## Задача №7 - https://leetcode.com/problems/rotate-array/
```python
class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        n = len(nums)
        k %= n
        nums.reverse()
        nums[:k] = reversed(nums[:k])
        nums[k:] = reversed(nums[k:])
```
## Задача №8 - https://leetcode.com/problems/reverse-integer/
```python
class Solution:
    def reverse(self, x: int) -> int:
        rev = int(str(abs(x))[::-1])
        return (-rev if x < 0 else rev) if rev.bit_length() < 32 else 0
```