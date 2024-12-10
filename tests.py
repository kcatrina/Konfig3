import unittest
from main import ConfigParser

class TestConfigParser(unittest.TestCase):

    def setUp(self):
        self.parser = ConfigParser()

    def test_remove_comments(self):
        text = "value1 -> const1; \\ Это комментарий"
        result = self.parser.remove_comments(text)
        self.assertEqual(result, "value1 -> const1; ")

    def test_define_constant(self):
        self.parser.define_constant('42 -> const1;')
        self.assertEqual(self.parser.constants['const1'], 42)

    def test_parse_constant_usage(self):
        self.parser.constants = {'const1': 42}
        result = self.parser.parse_constant_usage("@{const1}")
        self.assertEqual(result, 42)

    def test_parse_list(self):
        result = self.parser.parse_list("(list 1 2 3)")
        self.assertEqual(result, [1, 2, 3])

    def test_parse_dict(self):
        result = self.parser.parse_dict('[key1 => 1, key2 => "value"]')
        self.assertEqual(result, {'key1': 1, 'key2': 'value'})

    def test_parse_value_integer(self):
        result = self.parser.parse_value("42")
        self.assertEqual(result, 42)

    def test_parse_value_string(self):
        result = self.parser.parse_value('"hello"')
        self.assertEqual(result, "hello")

    def test_parse_value_constant(self):
        self.parser.constants = {'const1': 100}
        result = self.parser.parse_value("@{const1}")
        self.assertEqual(result, 100)

    def test_syntax_error_on_invalid_syntax(self):
        with self.assertRaises(SyntaxError):
            self.parser.process_lines(["unknown syntax"])

    def test_name_error_on_undefined_constant(self):
        with self.assertRaises(NameError):
            self.parser.parse_constant_usage("@{undefined}")

    def test_split_dict_items(self):
        content = 'key1 => 1, key2 => (list 2 3), key3 => "value"'
        result = self.parser.split_dict_items(content)
        self.assertEqual(result, [
            'key1 => 1',
            'key2 => (list 2 3)',
            'key3 => "value"'
        ])

if __name__ == "__main__":
    unittest.main()
