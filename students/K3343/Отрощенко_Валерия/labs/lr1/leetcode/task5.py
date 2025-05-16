class Solution(object):
    def nextPermutation(self, nums):
        """
        :type nums: List[int]
        :rtype: None. Do not return anything, modify nums in-place instead.
        """
        n = len(nums)
        i = n - 2

        # Найти первый индекс i, такой что nums[i] < nums[i + 1]
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1

        if i >= 0:
            # Найти наименьший элемент справа от i, который больше nums[i]
            j = n - 1
            while nums[j] <= nums[i]:
                j -= 1
            # Поменять их местами
            nums[i], nums[j] = nums[j], nums[i]

        # Перевернуть суффикс справа от позиции i
        left, right = i + 1, n - 1
        while left < right:
            nums[left], nums[right] = nums[right], nums[left]
            left += 1
            right -= 1