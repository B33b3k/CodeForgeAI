import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_sum_pair(nums, target):
    """Finds two numbers in a list that sum to a target value."""
    if not isinstance(nums, list):
        logger.error("Invalid input: nums must be a list.")
        return {"status": "error", "message": "nums must be a list"}
    if not all(isinstance(num, int) for num in nums):
        logger.error("Invalid input: nums list must contain only integers.")
        return {"status": "error", "message": "nums list must contain only integers"}
    if not isinstance(target, int):
        logger.error("Invalid input: target must be an integer.")
        return {"status": "error", "message": "target must be an integer"}
    if len(nums) < 2:
        logger.warning("Input list has less than 2 elements.")
        return {"status": "warning", "message": "List must contain at least two numbers"}

    try:
        seen = set()
        for num in nums:
            complement = target - num
            if complement in seen:
                logger.info(f"Found pair: ({num}, {complement})")
                return {"status": "success", "pair": (num, complement)}
            seen.add(num)
        logger.info("No pair found that sums to the target.")
        return {"status": "success", "message": "No pair found"}
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}