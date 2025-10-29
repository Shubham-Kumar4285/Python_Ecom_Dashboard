# tests/test_ui.py
from streamlit.testing.v1 import AppTest
import pytest
import pandas as pd
from unittest.mock import patch

@pytest.fixture(scope="module")
def create_dummy_dataframe():
    """Creates a dummy pandas DataFrame."""
    data = {
        'order_id': ['ORD001'], 'order_date': [pd.to_datetime('2025-10-29')],
        'customer_name': ['Test User'], 'customer_email': ['test@example.com'],
        'product_name': ['Laptop'], 'category': ['Electronics'], 'quantity': [1],
        'price_per_unit': [1200.0], 'total_price': [1200.0], 'total_discount': [120.0],
        'coupon_code': ['SAVE10'], 'cost_price_per_unit': [800.0],
        'total_cost': [800.0], 'profit': [280.0], 'payment_method': ['Credit Card'],
        'shipping_address': ['123 Test St'], 'city': ['Testville'], 'state': ['CA'],
        'postal_code': ['90210'], 'is_fraud': [0]
    }
    return pd.DataFrame(data)

@pytest.fixture(scope="module")
def dummy_file_path(tmp_path_factory, create_dummy_dataframe):
    """
    Creates a dummy CSV file from a DataFrame and returns its path.
    This fixture depends on `create_dummy_dataframe`.
    """

    df = create_dummy_dataframe


    tmp_dir = tmp_path_factory.mktemp("data")
    csv_path = tmp_dir / "dummy_orders.csv"

    # Save the DataFrame to the temporary file
    df.to_csv(csv_path, index=False)

    return str(csv_path)


@patch('streamlit.file_uploader')
def test_app_with_mocked_file_upload(mock_file_uploader, dummy_file_path):
    """
    Tests the full app by mocking the st.file_uploader to return a dummy file path.
    """

    mock_file_uploader.return_value = dummy_file_path

    at = AppTest.from_file("dashboard.py")
    at.run()

    assert not at.exception
    assert at.title[0].value == "🛒 Analytics Dashboard"
    assert len(at.metric) == 4
    assert at.metric[0].value == "1"
    assert at.metric[1].value == "$1,200.00"
