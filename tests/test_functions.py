import unittest
from unittest.mock import patch, MagicMock
from awsrole.awsrole import (
    generate_url,
    int_range,
    parse_args,
)

import argparse


class TestAwsroleFunctions(unittest.TestCase):
    def test_int_range_function(self):
        # Test for value within range
        int_range_checker = int_range(1, 10)
        self.assertEqual(int_range_checker("5"), 5)
        # Test for value out of range
        with self.assertRaises(argparse.ArgumentTypeError):
            int_range_checker("15")
        # Test for non-integer input
        with self.assertRaises(ValueError):
            int_range_checker("abc")

    def test_parse_args_function(self):
        # Mocking argparse Namespace
        with patch("awsrole.awsrole.argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_parse_args.return_value = MagicMock(
                role="test-role", account="", time=3600
            )
            args = parse_args()
            self.assertEqual(args.role, "test-role")
            self.assertEqual(args.account, "")
            self.assertEqual(args.time, 3600)

    def test_generate_url_with_valid_credentials(self):
        # Mocking URL response and data for generate_url
        with patch("awsrole.awsrole.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value.decode.return_value = (
                '{"SigninToken": "mock_token"}'
            )
            mock_urlopen.return_value.__enter__.return_value = mock_response
            creds = {
                "sessionId": "mock_session_id",
                "sessionKey": "mock_session_key",
                "sessionToken": "mock_session_token",
            }
            url = generate_url(creds, 3600)
            self.assertTrue(url.startswith("https://signin.aws.amazon.com/federation?"))
