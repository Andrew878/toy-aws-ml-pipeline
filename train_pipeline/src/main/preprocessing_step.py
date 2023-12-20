import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

def scale_data(input_data_path, output_data_path):
    """Reads data from the input path, scales it, and writes the scaled data to the output path."""
    # Load dataset
    df = pd.read_csv(input_data_path)

    # Assuming the last column is the target variable
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Create a DataFrame from the scaled features
    df_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    df_scaled['target'] = y

    # Save the scaled dataset
    df_scaled.to_csv(output_data_path, index=False)

if __name__ == '__main__':
    input_folder = '/opt/ml/processing/input'
    output_folder = '/opt/ml/processing/output'

    # Scale training data
    scale_data(os.path.join(input_folder, 'train.csv'),
               os.path.join(output_folder, 'train_scaled.csv'))

    # Scale testing data (if exists)
    test_input_path = os.path.join(input_folder, 'test.csv')
    test_output_path = os.path.join(output_folder, 'test_scaled.csv')
    if os.path.exists(test_input_path):
        scale_data(test_input_path, test_output_path)
