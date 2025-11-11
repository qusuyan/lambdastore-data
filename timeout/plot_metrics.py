#! /bin/env python3

''' Plots utilization and other metrics '''

# pylint: disable=too-many-locals,too-many-statements,too-many-branches,fixme

from sys import stderr
import os
import copy
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager

from extract_metrics import parse_start_time


def _main():
    font_path = '../LinLibertine_Rah.ttf'
    fontManager.addfont(font_path)

    # Set the font properties
    prop = FontProperties(fname=font_path)
    plt.rcParams.update({'lines.markersize': 8, 'font.family':prop.get_name()})

    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str)
    parser.add_argument('--metrics', type=str, default='all')
    parser.add_argument('--marker-at', type=int, required=False,
                        help="Draw a vertical marker line at the specified time (in milliseconds)")
    parser.add_argument('--start-at', type=int, help="Start time in milliseconds")
    parser.add_argument('--end-at', type=int, help="End time in milliseconds")
    parser.add_argument('--absolute-time', action='store_true',
        help="Treat the time as absolute (starting from the UNIX epoch)")
    parser.add_argument('--one-plot', action='store_true')
    parser.add_argument('--font-size', type=int, default=4)
    parser.add_argument('--linewidth', type=float, default=0.5)
    parser.add_argument('--report-frequency', type=int, default=200)
    parser.add_argument('--outfile', type=str, default='cluster-metrics.pdf')
    parser.add_argument('hide_legend', action='store_true')
    parser.add_argument('--height', type=float, default=6)
    parser.add_argument('--width', type=float, default=3)

    args = parser.parse_args()

    plt.rcParams.update({'font.size': args.font_size})

    metric_names = {
        'cpu-usage': 'CPU Usage\n(percent)',
        'compute-utilization': 'Compute Utilization\n(percent)',
        'active-transactions': 'Active Transactions',
        'running-jobs': 'Running Jobs',
        'blocked-jobs': 'Blocked Jobs',
        'ready-jobs': 'Ready Jobs',
        'num-objects': 'Number of Objects',
        'throughput': 'Throughput (ktps)',
        'total-commits': 'Total Commits',
        'total-aborts': 'Total Aborts',
        'abort-rate': 'Abort Rate (aborts/s)',
        'job-runtime': 'Avg. Job Runtime (ms)',
        'total-job-runtime': 'Total Job Runtime (ms)',
        'total-throughput': 'Total Throughput (ktps)',
        'num-full-replicas': 'Number of Full Replicas',
        'num-light-replicas': 'Number of Light Replicas',
        'num-shards': 'Number of Shards',
        'coord-cpu-usage': 'CPU Usage\n(Coordinator)',
        'mem-usage': "Memory Usage",
    }

    all_local_metrics = [
        'cpu-usage', 'mem-usage', 'compute-utilization', 'active-transactions',
        'running-jobs', 'blocked-jobs', 'ready-jobs', 'num-objects',
        'total-commits', 'total-aborts',
        'throughput', 'abort-rate', 'job-runtime',
    ]

    all_global_metrics = [
        'total-job-runtime', 'total-throughput', 'num-full-replicas',
        'num-light-replicas', 'num-shards', 'coord-cpu-usage',
    ]

    all_metrics = all_local_metrics + all_global_metrics

    if args.metrics == 'all':
        metrics = all_local_metrics + all_global_metrics
    else:
        metrics = args.metrics.split(',')

    keys = copy.deepcopy(metrics)
    labels = [None for _ in range(len(metrics))]

    # Filter keeps track of which metrics to use.
    # -1 means do not use
    # otherwise the number indicates the position of the plot
    metric_filter = []

    local_metric_count = 0

    for metric in all_metrics:
        if metric not in metric_names:
            stderr.write(f"No such metric: {metric}\n")
            sys.exit(1)

        if metric in keys:
            if metric not in all_global_metrics:
                local_metric_count += 1
            keys.remove(metric)

            # Make sure to keep input order specified by user
            pos = metrics.index(metric)
            metric_filter.append(pos)
            labels[pos] = metric_names[metric]
        else:
            if metric in metrics:
                print(f"WARN: Metric '{metric}' specified more than once")
            metric_filter.append(-1)

    for key in keys:
        stderr.write(f'ERROR: No such metric "{key}"\n')
        sys.exit(1)

    num_global_metrics = len(all_global_metrics)
    num_local_metrics = len(all_local_metrics)
    num_metrics = len(labels)

    if num_metrics == 0:
        stderr.write("ERROR: need at least one metric\n")
        sys.exit(1)

    if args.one_plot and num_metrics != 2:
        stderr.write("ERROR: one-plot needs exactly two metrics\n")
        sys.exit(1)

    times = []
    data = [[] for _ in range(num_metrics)]

    if os.path.isdir(args.path):
        path = args.path + '/cluster-metrics.csv'
        print(f'Path is a directory. Trying "{path}" instead.')
    else:
        path = args.path

    start_time = None
    num_nodes = 0
    last_num_nodes = 0

    with open(path, 'r', encoding='utf-8') as infile:
        for (line_no, line) in enumerate(infile.readlines()):
            if line_no == 0:
                start_time = parse_start_time(line)
                continue

            line = line.replace('\n', '')
            entries = [float(v) for v in line.split(',')]

            if len(entries) == 0 or (len(entries)-num_global_metrics) % num_local_metrics != 0:
                stderr.write(f"Line #{line_no} is invalid: {line}\n")
                sys.exit(1)

            line_no = line_no-1 # first line is only metadata
            times.append(line_no * args.report_frequency * 0.001)

            num_nodes = int((len(entries)-num_global_metrics) / num_local_metrics)
            assert num_nodes >= last_num_nodes

            #For each node metric, we need to add zeros for the time period
            # where the node was not connected yet
            for node_idx in range(last_num_nodes, num_nodes):
                for total_metric_idx in range(num_local_metrics):
                    idx = metric_filter[total_metric_idx]

                    if idx >= 0:
                        assert len(data[idx]) == line_no
                        for lno, _ in enumerate(data[idx]):
                            assert len(data[idx][lno]) == node_idx
                            data[idx][lno].append(0.0)

            last_num_nodes = num_nodes

            # Process local metrics
            # builds an array with an entry for each node
            for total_metric_idx in range(num_local_metrics):
                idx = metric_filter[total_metric_idx]

                if idx >= 0:
                    data_points = []
                    for node_idx in range(num_nodes):
                        pos = node_idx * num_local_metrics + total_metric_idx
                        data_points.append(entries[pos])
                    data[idx].append(data_points)

            # Process global metrics
            for global_idx in range(num_global_metrics):
                total_metric_idx = num_local_metrics + global_idx
                idx = metric_filter[total_metric_idx]
                if idx >= 0:
                    pos = num_nodes * num_local_metrics + global_idx
                    data[idx].append(entries[pos])

    if len(times) == 0:
        stderr.write("ERROR: No data found\n")
        sys.exit(1)

    node_labels = []
    for node_idx in range(num_nodes):
        node_labels.append(f"Node #{node_idx}")

    if args.one_plot:
        _fig, axis = plt.subplots(1, 1, figsize=(args.width, args.height))
        axes = [axis, axis.twinx()]
    else:
        _fig, axes = plt.subplots(num_metrics, 1, figsize=(args.width, args.height))
        if num_metrics == 1:
            axes = [axes]

    start_at = 0

    if args.start_at:
        if args.absolute_time:
            assert start_time
            assert args.start_at >= start_time
            start_at = (args.start_at - start_time) / 1000.0
            print(f"Relative start time is: {start_at}")
        else:
            start_at = args.start_at / 1000.0

        # remove data until we are at the start point
        while len(times) > 0 and times[0] < start_at:
            times.pop(0)
            for metric in data:
                metric.pop(0)

    if args.end_at:
        if args.absolute_time:
            assert start_time
            assert args.end_at >= start_time
            end_at = (args.end_at - start_time) / 1000.0
        else:
            end_at = args.end_at / 1000.0

        while len(times) > 0 and times[-1] > end_at:
            times.pop()
            for metric in data:
                metric.pop()

    if args.marker_at:
        if args.absolute_time:
            assert start_time
            assert args.marker_at >= start_time
            marker_at = (args.marker_at - start_time) / 1000.0
        else:
            marker_at = args.marker_at / 1000.0
    else:
        marker_at = None

    if args.start_at:
        # Make time relative to the start of the graph
        times[:] = [time-start_at for time in times]
        if marker_at:
            marker_at = marker_at - start_at

    for (metric_idx, metric_name) in enumerate(metrics):
        axis = axes[metric_idx]

        if metric_name in ["job-runtime", "total-job-runtime", "num-objects"]:
            # show runtime in log scale (first instance spawn takes long)
            axis.set_yscale("log")
        else:
            axis.set_yscale("linear")

        if metric_name in ["throughput", "total-throughput"]:
            for i in range(len(data[metric_idx])):
                for j in range(len(data[metric_idx][i])):
                    data[metric_idx][i][j] /= 1000

        if metric_name in all_global_metrics:
            # this is a global metric
            if metric_idx > 0 and args.one_plot:
                axis.plot(times, data[metric_idx], linewidth=args.linewidth,
                          color='red', linestyle='--')
            else:
                axis.plot(times, data[metric_idx], linewidth=args.linewidth)
        else:
            # this is a per node metric
            assert len(times) == len(data[metric_idx])
            per_node = [[] for _ in range(num_nodes)]
            for data_point in data[metric_idx]:
                assert len(data_point) == num_nodes
                for (idx, val) in enumerate(data_point):
                    per_node[idx].append(val)

            for (node_idx, node_data) in enumerate(per_node):
                axis.plot(times, node_data, label=node_labels[node_idx],
                        linewidth=args.linewidth)

            if not args.hide_legend:
                axis.legend()

        if marker_at:
            axis.vlines(marker_at, 0, 200)

        if metric_idx+1 == len(metrics) or args.one_plot:
            # only label x axis once
            axis.set_xlabel("Time (s)")
        elif not args.one_plot:
            xax = axis.get_xaxis()
            xax.set_visible(False)

        axis.set(ylim=(0, 110))
        axis.set_ylabel(labels[metric_idx])
        axis.set(xlim=(min(times), max(times)))

    plt.tight_layout()

    print(f'Writing output to {args.outfile}')
    plt.savefig(args.outfile)

if __name__ == "__main__":
    _main()
