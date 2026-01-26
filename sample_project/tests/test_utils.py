"""Tests for utility functions."""

import pytest
from datetime import datetime
from utils import format_date, parse_date, is_overdue


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_valid_date(self):
        """Test formatting a valid ISO date."""
        result = format_date("2024-03-15T10:30:00")
        assert result == "2024-03-15"

    def test_format_none(self):
        """Test formatting None."""
        result = format_date(None)
        assert result is None

    def test_format_invalid_date(self):
        """Test formatting an invalid date string."""
        result = format_date("not-a-date")
        assert result == "not-a-date"


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_iso_format(self):
        """Test parsing ISO format date."""
        result = parse_date("2024-03-15")
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15

    def test_parse_invalid(self):
        """Test parsing invalid date."""
        result = parse_date("invalid")
        assert result is None


class TestIsOverdue:
    """Tests for is_overdue function."""

    def test_overdue_task(self):
        """Test that past date is overdue."""
        result = is_overdue("2020-01-01")
        assert result is True

    def test_future_task(self):
        """Test that future date is not overdue."""
        result = is_overdue("2099-12-31")
        assert result is False

    def test_none_date(self):
        """Test that None date is not overdue."""
        result = is_overdue(None)
        assert result is False
