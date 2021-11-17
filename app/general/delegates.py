"""
Delegates
"""
from app.general.services import TestEmailService


class TestEmailDelegate:
    @staticmethod
    def test_email():
        TestEmailService.test_email()



