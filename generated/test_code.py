```python
import unittest
import logging
from your_module import calculate_median_of_sorted_arrays #Replace your_module


class TestCalculateMedian(unittest.TestCase):

    def test_valid_input(self):
        arr1 = [1, 3, 5]
        arr2 = [2, 4, 6]
        expected = {"median": 3.5, "status": "Success"}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_empty_arrays(self):
        arr1 = []
        arr2 = []
        expected = {"median": None, "status": "Error: Input arrays cannot be empty."}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_non_numeric_input(self):
        arr1 = [1, 3, 5]
        arr2 = [2, 4, "a"]
        expected = {"median": None, "status": "Error: Arrays must contain only numbers."}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_non_list_input(self):
        arr1 = (1, 3, 5)
        arr2 = [2, 4, 6]
        expected = {"median": None, "status": "Error: Input arrays must be lists."}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_unsorted_arrays(self):
        arr1 = [5, 3, 1]
        arr2 = [6, 4, 2]
        #Since the function doesn't explicitly throw an error for unsorted arrays, we test for the expected result after sorting.
        expected = {"median": 3.5, "status": "Success"}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_odd_length_arrays(self):
        arr1 = [1, 2, 3]
        arr2 = [4, 5, 6]
        expected = {"median": 3.5, "status": "Success"}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)

    def test_one_empty_array(self):
        arr1 = []
        arr2 = [1,2,3]
        expected = {"median": None, "status": "Error: Input arrays cannot be empty."}
        self.assertEqual(calculate_median_of_sorted_arrays(arr1, arr2), expected)


if __name__ == '__main__':
    unittest.main()
```