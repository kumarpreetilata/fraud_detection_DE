import logging
import pandas as pd
import numpy as np
from feature_engineering import feature_engineering  # Import your feature engineering function

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_sample_data():
    """Create a sample dataset for testing the feature engineering."""
    data = {
        'transaction_id': np.arange(1, 101),
        'amount': np.random.rand(100) * 1000,  # Random transaction amounts
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'is_fraud': np.random.choice([0, 1], size=100)  # Binary classification target
    }
    return pd.DataFrame(data)

def test_feature_engineering():
    """Test the feature engineering process."""
    sample_data = create_sample_data()
    
    # Apply feature engineering
    processed_data = feature_engineering(sample_data)

    # Validate processed data
    expected_columns = ['transaction_id', 'amount', 'hour_of_day', 'is_fraud']  # Example expected columns
    assert all(column in processed_data.columns for column in expected_columns), "Processed data does not contain expected columns."
    
    # Validate the shape of processed data
    assert processed_data.shape[0] == sample_data.shape[0], "Processed data shape mismatch."
    
    # Additional checks for feature values (modify based on actual feature engineering logic)
    assert processed_data['hour_of_day'].min() >= 0 and processed_data['hour_of_day'].max() < 24, "Hour of day feature out of range."

    logging.info("Feature engineering tests passed successfully.")

def main():
    """Main function to execute the processing tests."""
    test_feature_engineering()

if __name__ == "__main__":
    main()
