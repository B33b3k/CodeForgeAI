import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
MOD = 10**9 + 7

def count_subsequences(nums, target):
    """Counts non-empty subsequences meeting criteria."""
    try:
        if not isinstance(nums, list):
            raise TypeError("Input nums must be a list.")
        if not all(isinstance(num, int) for num in nums):
            raise ValueError("All elements in nums must be integers.")
        if not nums:
            return {"status": "error", "message": "Input list cannot be empty."}
        if not isinstance(target, int) or target <=0:
            raise ValueError("Target must be a positive integer.")

        n = len(nums)
        count = 0
        for i in range(1, 1 << n):  # Iterate through all non-empty subsequences
            subsequence = []
            for j in range(n):
                if (i >> j) & 1:
                    subsequence.append(nums[j])
            
            if subsequence:
                min_val = min(subsequence)
                max_val = max(subsequence)
                if min_val + max_val <= target:
                    count = (count + 1) % MOD

        return {"status": "success", "count": count}

    except (TypeError, ValueError) as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": "An unexpected error occurred."}

result= count_subsequences([1, 2, 3, 4, 5], 10)
print(result)