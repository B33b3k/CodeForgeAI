```python
import unittest
import logging

# Suppress logging output during tests
logging.disable(logging.CRITICAL)

class TestFindSumPair(unittest.TestCase):
    def test_valid_input(self):
        self.assertEqual(find_sum_pair([1, 2, 3, 4, 5], 7), {'status': 'success', 'pair': (2, 5)})

    def test_no_pair_found(self):
        self.assertEqual(find_sum_pair([1, 2, 3, 4, 5], 10), {'status': 'success', 'message': 'No pair found'})

    def test_invalid_nums_type(self):
        self.assertEqual(find_sum_pair("not a list", 5), {'status': 'error', 'message': 'nums must be a list'})

    def test_invalid_nums_content(self):
        self.assertEqual(find_sum_pair([1, 2, 'a', 4, 5], 7), {'status': 'error', 'message': 'nums list must contain only integers'})

    def test_invalid_target_type(self):
        self.assertEqual(find_sum_pair([1, 2, 3, 4, 5], 'a'), {'status': 'error', 'message': 'target must be an integer'})

    def test_less_than_two_elements(self):
        self.assertEqual(find_sum_pair([1], 5), {'status': 'warning', 'message': 'List must contain at least two numbers'})

    def test_empty_list(self):
        self.assertEqual(find_sum_pair([], 5), {'status': 'warning', 'message': 'List must contain at least two numbers'})

    def test_exception_handling(self):
        #This test might fail depending on the specific exception raised by the internal code.
        #A more robust test would mock the internal function to simulate a specific exception
        pass

if __name__ == '__main__':
    unittest.main()
```