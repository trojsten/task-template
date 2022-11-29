import pytest
from .filters import render_list, roman, textbf


class TestFilters():
    def test_render_list_nolist(self):
        assert render_list('string') == "string"

    def test_render_list_empty(self):
        assert render_list([]) == ""

    def test_render_list_one(self):
        assert render_list(["x"]) == "x"

    def test_render_list_two(self):
        assert render_list(["x", "y"]) == "x a y"

    def test_render_list_three(self):
        assert render_list(["x", "y", "z"]) == "x, y a z"

    def test_render_list_four(self):
        assert render_list(["Hovi", "Enka", "Fek", "Lista"]) == "Hovi, Enka, Fek a Lista"

    def test_render_list_wrap(self):
        assert render_list(["Tvoja", "mama"], func=textbf) == r"\textbf{Tvoja} a \textbf{mama}"

    def test_render_list_f(self):
        assert render_list(["x", "y", "z"], func=lambda x: f'f({x})') == r"f(x), f(y) a f(z)"


class TestRoman():
    def test_roman_str(self):
        with pytest.raises(TypeError):
            roman('ryba')

    def test_roman_float(self):
        with pytest.raises(TypeError):
            roman(3.0)

    def test_roman_zero(self):
        with pytest.raises(ValueError):
            roman(0)

    def test_roman_too_big(self):
        with pytest.raises(ValueError):
            roman(123456)

    def test_roman_1(self):
        assert roman(1) == 'I'

    def test_roman_1234(self):
        assert roman(1234) == 'MCCXXXIV'

    def test_roman_49(self):
        assert roman(49) == 'XLIX'

    def test_roman_1990(self):
        assert roman(1990) == 'MCMXC'

    def test_roman_2022(self):
        assert roman(2022) == 'MMXXII'
