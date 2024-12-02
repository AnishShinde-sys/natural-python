import unittest
from app.interpreter.interpreter import AdvancedInterpreter

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
        ]
        
        for command, var_name, expected_value in test_cases:
            self.interpreter.process_line(command)
            self.assertIn(var_name, self.interpreter.variables)
            self.assertEqual(self.interpreter.variables[var_name], expected_value)

    def test_math_operations(self):
        """Test math operations"""
        self.interpreter.process_line("Make a number called score equal to 10")
        
        test_cases = [
            ("Add 5 to score", 15),
            ("Multiply score by 2", 30),
            ("Divide score by 3", 10),
            ("Double score", 20),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_line(command)
            self.assertEqual(self.interpreter.variables['score'], expected_value)

    def test_string_operations(self):
        """Test string operations"""
        self.interpreter.process_line('Create a string called greeting with "Hello World"')
        
        test_cases = [
            ("Convert greeting to uppercase", "HELLO WORLD"),
            ('Join greeting with "!"', "HELLO WORLD!"),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_line(command)
            self.assertEqual(self.interpreter.variables['greeting'], expected_value)

    def test_list_operations(self):
        """Test list operations"""
        self.interpreter.process_line("Make a list numbers equal to [1, 2, 3, 4, 5]")
        
        test_cases = [
            ("Add 6 to numbers", [1, 2, 3, 4, 5, 6]),
            ("Remove 3 from numbers", [1, 2, 4, 5, 6]),
            ("Sort numbers", [1, 2, 4, 5, 6]),
        ]
        
        for command, expected_value in test_cases:
            self.interpreter.process_line(command)
            self.assertEqual(self.interpreter.variables['numbers'], expected_value)

    def test_conditional_logic(self):
        """Test conditional logic"""
        self.interpreter.process_line("Make a number called score equal to 15")
        
        test_cases = [
            ("If score is bigger than 12:", True),
            ("If score is less than 10:", False),
            ("If score is equal to 15:", True),
        ]
        
        for condition, expected_result in test_cases:
            result = self.interpreter.evaluate_condition(condition[3:-1])  # Remove 'If' and ':'
            self.assertEqual(result, expected_result)

    def test_advanced_operations(self):
        """Test advanced operations"""
        self.interpreter.process_line("Make a list numbers equal to [1, 2, 3, 4, 5]")
        
        test_cases = [
            ("Calculate square root of 16", "Square root of 16 is 4.0"),
            ("Find maximum of numbers", "Maximum of numbers is 5"),
            ('Format string "Hello {}" with "Alice"', "Hello Alice"),
        ]
        
        for command, expected_output in test_cases:
            self.interpreter.process_line(command)
            self.assertIn(expected_output, self.interpreter.output[-1])

if __name__ == '__main__':
    unittest.main()