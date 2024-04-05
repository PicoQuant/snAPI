from snAPI.Main import *
from matplotlib import pyplot as plt
import click
from pathlib import Path
import csv
import json
import pandas as pd


@click.command()
@click.argument('filename',type=click.Path(exists=True), metavar='FILENAME.ptu')
@click.option('--A', '-a', type=int, default=1, help='Correlation channel A (default: 1)')
@click.option('--B', '-b', type=int, default=2, help='Correlation channel B (default: 2)')
@click.option('--windowsize', '-ws', type=int, default=10000, help='size of the correlation window in ps (default: 100000)')
@click.option('--binsize', '-bs', type=int, default=10, help='size of the correlation bin size in ps (default: 10)')
def g2correlation(filename, a=1, b=2, windowsize=10000, binsize=10):
    sn = snAPI(libType=LibType.Undefined)
    sn.getFileDevice(filename)
    sn.correlation.setG2Parameters(a, b, windowsize, binsize)
    sn.correlation.measure(waitFinished=True)
    g2, lagtimes = sn.correlation.getG2Data()

    plt.plot(lagtimes, g2, linewidth=2.0, label='g(2)')
    plt.xlabel('Time [s]')
    plt.ylabel('g(2)')
    plt.legend()
    plt.title("g(2)")
    
    plt.savefig(Path(filename).with_suffix('.' + 'png'), format='png')

    # Save data to csv
    with open(Path(filename).with_suffix('.' + 'csv'), mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write the header row
        writer.writerow(['lagtime', 'g2'])
    
        # Write the data rows using writerows() and zip()
        writer.writerows(zip(lagtimes, g2))
    
    # Save data to json
    # Combine x_values and y_values into a list of dictionaries
    data_dic = [{'lagtime': x, 'g2': y} for x, y in zip(lagtimes, g2)]

    # Specify the file name
    json_file = Path(filename).with_suffix('.' + 'json')

    # Write the data to a JSON file
    with open(json_file, 'w') as file:
        json.dump(data_dic, file)

    # Save to Excel
    # Combine x_values and y_values into a DataFrame
    df = pd.DataFrame(data_dic)

    # Drop rows where either 'X' or 'Y' value is zero
    df = df[(df != 0).all(1)]

    # Specify the file name
    excel_file = Path(filename).with_suffix('.' + 'xlsx')

    # Write the data to an Excel file
    df.to_excel(excel_file, index=False)  


if(__name__ == "__main__"):

    g2correlation()
