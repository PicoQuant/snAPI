from snAPI.Main import *
from matplotlib import pyplot as plt
import click
from pathlib import Path
import pandas as pd


@click.command()
@click.argument('filename',type=click.Path(exists=True), metavar='FILENAME.ptu')
@click.option('--A', '-a', type=int, default=1, help='Correlation channel A (default: 1)')
@click.option('--B', '-b', type=int, default=2, help='Correlation channel B (default: 2)')
@click.option('--windowsize', '-ws', type=int, default=10000, help='size of the correlation window in ps (default: 100000)')
@click.option('--binsize', '-bs', type=int, default=10, help='size of the correlation bin size in ps (default: 10)')
def g2correlation(filename, a=1, b=2, windowsize=10000, binsize=10):
    sn = snAPI()
    sn.getFileDevice(filename)
    sn.correlation.setG2Parameters(a, b, windowsize, binsize)
    sn.correlation.measure(waitFinished=True)
    g2, lagtimes = sn.correlation.getG2Data()
    
    df = pd.DataFrame({"lagtime": list(lagtimes), "g2": list(g2)})

    # Plot the DataFrame
    df.plot(x='lagtime', y='g2', label=f'{filename}')
    plt.xlabel('lagtime (s)')
    plt.ylabel('g(2) amplitude')
    plt.title("g(2) correlation")

    # Save the plot to a PDF file   
    plt.savefig(Path(filename).with_suffix('.' + 'pdf'), format='pdf')
    # Save the plot to a PNG file   
    plt.savefig(Path(filename).with_suffix('.' + 'png'), format='png')
    # Save the g2-correlation to csv
    df.to_csv(Path(filename).with_suffix('.' + 'csv'))
    # Save the g2-correlation to Excel
    df.to_excel(Path(filename).with_suffix('.' + 'xlsx'))
    # Save the g2-correlation to json
    df.to_json(Path(filename).with_suffix('.' + 'json'))
if(__name__ == "__main__"):
    g2correlation()
