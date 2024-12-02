import unittest
from app import AdvancedInterpreter

class TestAdvancedInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = AdvancedInterpreter()

    def test_variable_creation(self):
        """Test variable creation with different patterns"""
        test_cases = [
            ("Make a number called score equal to 10", "score", 10),
            ("Create a string named message with Hello World", "message", "Hello World"),
            ("Let x be 42", "x", 42),
            ("Define a list numbers as [1, 2, 3, 4, 5]", "numbers", [1, 2, 3, 4, 5]),
            ("Set counter to 0", "counter", 0),
        ]
        
        for command, var_name, expected_value in test_cases:
            self.interpreter.process_input(command)
            self.assertIn(var_name, self.interpreter.variables)
            self.assertEqual(self.interpreter.variables[var_name], expected_value)

    def test_math_operations(self):
        """Test basic math operations"""
        self.interpreter.process_input("Set score to 10")
        
        test_cases = [
            ("Add 5 to score", 15),
            ("Subtract 3 from score", 12),
            ("Multiply score by 2", 24),
            ("Divide score by 4", 6),
            ("Double score", 12),
            ("Half score", 6),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_input(command)
            self.assertEqual(self.interpreter.variables['score'], expected_value)

    def test_string_operations(self):
        """Test string manipulation operations"""
        self.interpreter.process_input("Make greeting equal to hello")
        
        test_cases = [
            ("Convert greeting to uppercase", "HELLO"),
            ("Make greeting lowercase", "hello"),
            ("Join greeting with world", "helloworld"),
            ("Split greeting by l", ["he", "", "o"]),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_input(command)
            self.assertEqual(self.interpreter.variables['greeting'], expected_value)

    def test_list_operations(self):
        """Test list manipulation operations"""
        self.interpreter.process_input("Create a list numbers with [1, 2, 3]")
        
        test_cases = [
            ("Add 4 to numbers", [1, 2, 3, 4]),
            ("Remove 2 from numbers", [1, 3, 4]),
            ("Insert 5 at position 1 in numbers", [1, 5, 3, 4]),
            ("Sort numbers", [1, 3, 4, 5]),
            ("Reverse numbers", [5, 4, 3, 1]),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_input(command)
            self.assertEqual(self.interpreter.variables['numbers'], expected_value)

    def test_boolean_operations(self):
        """Test boolean operations and comparisons"""
        self.interpreter.process_input("Set x to 10")
        
        test_cases = [
            ("Check if x is equal to 10", True),
            ("Is x greater than 5", True),
            ("Compare if x is less than 20", True),
            ("Test if x is between 5 and 15", True),
        ]
        
        for command, expected_value in test_cases:
            result = self.interpreter.process_input(command)
            self.assertEqual(result, expected_value)

    def test_type_casting(self):
        """Test type conversion operations"""
        test_cases = [
            ("Convert 123 to string", "123"),
            ("Change 3.14 to int", 3),
            ("Make True into string", "True"),
            ("Cast 0 to bool", False),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_input(command)
            self.assertEqual(self.interpreter.output[-1], str(expected_value))

    def test_error_handling(self):
        """Test error handling scenarios"""
        test_cases = [
            "Divide score by 0",
            "Add hello to 42",
            "Remove item from nonexistent_list",
            "Convert invalid to int",
        ]
        
        for command in test_cases:
            self.interpreter.process_input(command)
            self.assertTrue(any("Error" in output for output in self.interpreter.output))

    def test_math_functions(self):
        """Test mathematical functions"""
        test_cases = [
            ("Calculate square root of 16", 4),
            ("Find maximum of [1, 5, 3]", 5),
            ("Generate random number", lambda x: 0 <= x <= 1),
            ("What is the value of pi", 3.141592653589793),
        ]
        
        for command, expected in test_cases:
            result = self.interpreter.process_input(command)
            if callable(expected):
                self.assertTrue(expected(result))
            else:
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main() 