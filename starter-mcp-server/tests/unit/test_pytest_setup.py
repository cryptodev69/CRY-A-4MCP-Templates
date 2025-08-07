"""Simple test to verify pytest setup is working."""

import pytest


def test_basic_functionality():
    """Test that basic Python functionality works."""
    assert 1 + 1 == 2
    assert "hello" == "hello"
    assert [1, 2, 3] == [1, 2, 3]


def test_string_operations():
    """Test string operations."""
    text = "pytest is working"
    assert "pytest" in text
    assert text.upper() == "PYTEST IS WORKING"
    assert len(text) == 17


def test_list_operations():
    """Test list operations."""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15
    assert max(numbers) == 5
    assert min(numbers) == 1


@pytest.mark.parametrize("input_val,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (5, 25),
])
def test_square_function(input_val, expected):
    """Test parametrized square function."""
    assert input_val ** 2 == expected


class TestClassExample:
    """Example test class."""
    
    def test_class_method(self):
        """Test method in a class."""
        assert True
    
    def test_another_class_method(self):
        """Another test method in a class."""
        data = {"key": "value"}
        assert data["key"] == "value"
        assert "key" in data