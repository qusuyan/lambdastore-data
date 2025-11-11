#! /bin/bash
./plot_metrics.py --metrics=total-throughput,num-light-replicas,num-full-replicas --one-plot ./cluster-metrics.csv --start-at=0 --font-size=8 --linewidth=1.0 --report-frequency=50 --start-at=130 --end-at=170 --outfile=output.pdf --font-size=14 --width=5 --height=2.4 
