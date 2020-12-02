import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 


def pub_line_plot(input_df):
    print("Our dataset have {} rows and {} columns." .format(input_df.shape[0], input_df.shape[1]))
    monthly_counts = input_df.resample('MS')[['PMID']].count()

    plt.rcParams["figure.figsize"] = (12,6)
    plt.plot(monthly_counts.index, monthly_counts["PMID"], color='b', marker='o',  )
    plt.title('Pubications Trend Over Time',  fontsize=15)
    plt.xlabel('Date',  fontsize=12)
    plt.ylabel('Publication Count',  fontsize=12)
    # plt.grid(True)
    plt.show()
    return True


def pub_descriptions(input_df, print_output=True):
    monthly_counts = input_df.resample('M')[['PMID']].count()

    monthly_descriptions = monthly_counts.describe()
    monthly_descriptions.loc['range'] = monthly_descriptions.loc['max']-monthly_descriptions.loc['min']

    if print_output == True:
        print("The dataset has {} publications" .format(input_df.shape[0]))
        print("The earliest publication was published on {:%m/%d/%Y}" .format(pub_df.index.min()))
        print("The last publication was published on {:%m/%d/%Y}" .format(pub_df.index.max()))
        print("There were a total of {:d} months".format(int(monthly_descriptions.loc['count'][0])))

    return monthly_counts, monthly_descriptions


if __name__ == '__main__':
    pub_df = pd.read_csv("publication_output.csv", index_col=['Pub_Date'], parse_dates=['Pub_Date'])
    pub_line_plot(pub_df)
    pub_descriptions(pub_df)
