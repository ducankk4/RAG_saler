import pandas as pd

df = pd.read_csv("data.csv")
def main():
    print("Data loaded successfully!")
    print(df.head())        
if __name__ == "__main__":
    main()
# This code reads a CSV file named "data.csv" and prints the first few rows of the DataFrame.
# Ensure that the "data.csv" file is in the same directory as this script.  