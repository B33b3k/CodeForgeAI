import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_median_of_sorted_arrays(arr1, arr2):
    """
    Calculates the median of two sorted input arrays.

    Args:
        arr1: The first sorted array.
        arr2: The second sorted array.

    Returns:
        A dictionary containing the median and a status message.  Returns an error dictionary if input is invalid.
    """

    # Input validation
    if not isinstance(arr1, list) or not isinstance(arr2, list):
        logging.error("Invalid input: arr1 and arr2 must be lists.")
        return {"median": None, "status": "Error: Input arrays must be lists."}
    if not all(isinstance(x, (int, float)) for x in arr1 + arr2):
        logging.error("Invalid input: Arrays must contain only numbers.")
        return {"median": None, "status": "Error: Arrays must contain only numbers."}
    if not all(arr1[i] <= arr1[i+1] for i in range(len(arr1)-1)) or not all(arr2[i] <= arr2[i+1] for i in range(len(arr2)-1)):
        logging.warning("Warning: Input arrays are not necessarily sorted.  Results may be unexpected.")


    merged_array = sorted(arr1 + arr2)
    n = len(merged_array)
    
    if n == 0:
        logging.error("Invalid input: Arrays cannot be empty.")
        return {"median": None, "status": "Error: Input arrays cannot be empty."}

    midpoint = n // 2
    if n % 2 == 0:
        median = (merged_array[midpoint - 1] + merged_array[midpoint]) / 2
    else:
        median = merged_array[midpoint]

    logging.info(f"Median calculated successfully: {median}")
    return {"median": median, "status": "Success"}


#Example Usage
arr1 = [1, 3, 5]
arr2 = [2, 4, 6]
result = calculate_median_of_sorted_arrays(arr1, arr2)
print(result)

arr3 = [1, 3, 5]
arr4 = [2, 4, "a"]
result = calculate_median_of_sorted_arrays(arr3, arr4)
print(result)

arr5 = []
arr6 = []
result = calculate_median_of_sorted_arrays(arr5, arr6)
print(result)

arr7 = [5,3,1]
arr8 = [6,4,2]
result = calculate_median_of_sorted_arrays(arr7, arr8)
print(result)