import numpy as np
import yaml, sys
from matplotlib import pylab
from reprep import Report


def main():
    data = yaml.load(sys.stdin)

    r = Report("plot_activities")

    with r.data_pylab("activities") as pylab:
        for activity, stats in data.items():
            ndays = max(stats.keys()) + 1
            accum = np.zeros(ndays)
            for day, amount in stats.items():
                accum[day] = amount

            x = range(ndays)
            pylab.plot(x, accum, label=activity)
        pylab.legend()
    r.to_html("out/plots.html")


if __name__ == "__main__":
    main()
