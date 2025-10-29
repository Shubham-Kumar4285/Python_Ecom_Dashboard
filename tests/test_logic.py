import pandas as pd
import pytest
from dashboard import find_suspicious_emails

def test_find_suspicious_emails():
    """
    Tests the find_suspicious_emails function to ensure it correctly
    identifies emails from disposable domains and those using '+' aliasing.
    """
    data = {
        'customer_email': [
            'test.user@example.com',           # Normal
            'scammer@mailinator.com',          # Disposable domain
            'fraudster+123@gmail.com',         # '+' alias
            'another.user@temp-mail.org',      # Disposable domain
            'legit@work.com'                   # Normal
        ]
    }
    df = pd.DataFrame(data)

    suspicious_df = find_suspicious_emails(df)

    # Assertions
    assert len(suspicious_df) == 3, "Should find exactly 3 suspicious emails"

    flagged_emails = suspicious_df['customer_email'].tolist()
    assert 'scammer@mailinator.com' in flagged_emails
    assert 'fraudster+123@gmail.com' in flagged_emails
    assert 'another.user@temp-mail.org' in flagged_emails
    assert 'test.user@example.com' not in flagged_emails
