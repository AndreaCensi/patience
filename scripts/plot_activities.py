import numpy as np
import yaml, sys
from matplotlib import pylab
from reprep import Report

def main():
    data = yaml.load(sys.stdin)
    
    r  = Report()
    
    
    for activity, stats in data.items():
        ndays = max(stats.keys()) + 1
        accum = np.zeros(ndays)
        for day, amount in stats.items():
            accum[day] = amount
            
        x = range(ndays)
        with r.data_pylab(activity) as pylab:
            pylab.plot(x, accum)

    r.to_html('out/plots.html')
    
if __name__ == '__main__':
    main()