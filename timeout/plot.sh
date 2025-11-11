START=1708760803626
END=1708760810694
SPIN_TIME=1708760804619

./plot_metrics.py . \
    --metrics=throughput \
    --outfile=output.pdf \
    --start-at $START \
    --end-at $END \
    --marker-at $SPIN_TIME \
    --absolute-time \
    --font-size=14 \
    --width=5 --height=2.1 \
    --report-frequency=100
