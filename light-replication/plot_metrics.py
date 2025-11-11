#! /bin/env python3

''' Plots utilization and other metrics '''

# pylint: disable=too-many-locals,too-many-statements,too-many-branches,fixme

from sys import stderr
import os
import copy
import sys
import argparse
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
    parser.add_argument('--start-at', type=int)
    parser.add_argument('--end-at', type=int)
    parser.add_argument('--one-plot', action='store_true')
    parser.add_argument('--font-size', type=int, default=4)
    parser.add_argument('--linewidth', type=float, default=0.5)
    parser.add_argument('--report-frequency', type=int, default=100)
    parser.add_argument('--outfile', type=str, default='cluster-metrics.pdf')
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
        'throughput': 'Throughput (tps)',
        'abort-rate': 'Abort Rate (aborts/s)',
        'job-runtime': 'Avg. Job Runtime (ms)',
        'total-job-runtime': 'Total Job Runtime (ms)',
        'total-throughput': 'Total Throughput (tps)',
        'num-full-replicas': 'Number of Full Replicas',
        'num-light-replicas': 'Num. of Light Replicas',
        'num-shards': 'Number of Shards',
    }

    all_local_metrics = [
        'cpu-usage', 'compute-utilization', 'active-transactions', 'running-jobs', 'blocked-jobs',
        'ready-jobs', 'num-objects', 'throughput', 'abort-rate', 'job-runtime',
    ]

    all_global_metrics = [
        'total-job-runtime', 'total-throughput', 'num-full-replicas',
        'num-light-replicas', 'num-shards'
    ]

    all_metrics = all_local_metrics + all_global_metrics

    labels = []
    metric_filter = []

    if args.metrics == 'all':
        metrics = all_local_metrics + all_global_metrics
    else:
        metrics = args.metrics.split(',')

    keys = copy.deepcopy(metrics)
    local_metric_count = 0

    for metric in all_metrics:
        if metric not in metric_names:
            raise RuntimeError(f"No such metric: {metric}")

        if metric in keys:
            if metric not in all_global_metrics:
                local_metric_count += 1
            keys.remove(metric)
            metric_filter.append(True)
            labels.append(metric_names[metric])
        else:
            if metric in metrics:
                print(f"WARN: Metric '{metric}' specified more than once")
            metric_filter.append(False)

    for key in keys:
        print(f"WARN: No such metric '{key}'")

    num_global_metrics = len(all_global_metrics)
    num_local_metrics = len(all_local_metrics)
    num_metrics = len(labels)

    if num_metrics == 0:
        raise RuntimeError("need at least one metric")

    # if args.one_plot and num_metrics != 2:
    #     raise RuntimeError("one-plot needs exactly two metrics")

    times = []
    data = [[] for _ in range(num_metrics)]

    if os.path.isdir(args.path):
        path = args.path + '/cluster-metrics.csv'
        print(f'Path is a directory. Trying "{path}" instead.')
    else:
        path = args.path

    with open(path, 'r', encoding='utf-8') as infile:
        for (line_no, line) in enumerate(infile.readlines()):
            if line_no == 0:
                parse_start_time(line)
                continue

            line = line.replace('\n', '')
            times.append((line_no-1) * args.report_frequency * 0.001)
            entries = [float(v) for v in line.split(',')]

            if len(entries) == 0 or (len(entries)-num_global_metrics) % num_local_metrics != 0:
                stderr.write(f"Line #{line_no} is invalid: {line}\n")
                sys.exit(1)

            num_nodes = int((len(entries)-num_global_metrics) / num_local_metrics)

            data_points = [[] for _ in range(local_metric_count)]

            for node_idx in range(num_nodes):
                metric_idx = 0
                for total_metric_idx in range(num_local_metrics):
                    if metric_filter[total_metric_idx]:
                        pos = node_idx * num_local_metrics + total_metric_idx
                        data_points[metric_idx].append(entries[pos])
                        metric_idx += 1

            for metric_idx, data_point in enumerate(data_points):
                data[metric_idx].append(data_point)

            metric_idx = len(data_points)
            for global_idx in range(num_global_metrics):
                total_metric_idx = num_local_metrics + global_idx
                if metric_filter[total_metric_idx]:
                    pos = num_nodes * num_local_metrics + global_idx
                    data[metric_idx].append(entries[pos])
                    metric_idx += 1

    if len(times) == 0:
        print("ERROR: No data found")
        return

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

    if args.start_at:
        # remove data until we are at the start point
        while len(times) > 0 and times[0] < args.start_at:
            times.pop(0)
            for metric in data:
                metric.pop(0)

    if args.end_at:
        while len(times) > 0 and times[-1] > args.end_at:
            times.pop()
            for metric in data:
                metric.pop()

    for idx in range(len(times)):
        times[idx]  -= args.start_at

    num_replicas_metrics = [idx for (idx, metric_name) in enumerate(metrics) if metric_name in ['num-full-replicas', 'num-light-replicas']]
    total_replicas = [sum([data[metric_idx][i] for metric_idx in num_replicas_metrics]) for i in range(len(data[0]))]

    axes[0].plot(times, [data_point / 1000 for data_point in data[0]], linewidth=args.linewidth)
    axes[1].plot(times, data[2], linewidth=args.linewidth, color='green', linestyle='-.', label="Light Replicas")
    axes[1].plot(times, total_replicas, linewidth=args.linewidth, color='red', linestyle='--', label="Total Replicas")

    axes[0].set(ylim=(0, 1.75))
    axes[0].set_ylabel("Throughput (ktps)")
    axes[1].set(ylim=(0, None), yticks=[0,2,4,6,8])
    axes[1].set_ylabel("Num. Replicas")
    axes[1].set(xlim=(min(times), max(times)))
    axes[0].set_xlabel("Time (s)")
    axes[1].legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, 0.9), ncol=2)

    # for (metric_idx, metric_name) in enumerate(metrics):
    #     # axis = axes[metric_idx]
    #     # if metric_name in :
    #     #     axis = axes[1]
    #     # else:
    #     #     axis = axes[0]

    #     if metric_name in all_global_metrics:
    #         # this is a global metric
    #         if metric_idx > 0 and args.one_plot:
    #             axis.plot(times, data[metric_idx], linewidth=args.linewidth, color='red', linestyle='--')
    #         else:
    #             axis.plot(times, data[metric_idx], linewidth=args.linewidth)
    #     else:
    #         # this is a per node metric
    #         assert len(times) == len(data[metric_idx])
    #         per_node = [[] for _ in range(num_nodes)]
    #         for data_point in data[metric_idx]:
    #             idx = 0
    #             for val in data_point:
    #                 per_node[idx].append(val)
    #                 idx += 1

    #             while idx < num_nodes:
    #                 per_node[idx].append(0.0)
    #                 idx += 1

    #         for (node_idx, node_data) in enumerate(per_node):
    #             axis.plot(times, node_data, label=node_labels[node_idx],\
    #                     linewidth=args.linewidth)

    #         axis.legend()

    #     if metric_name in ["job-runtime", "num-objects"]:
    #         # show runtime in log scale (first instance spawn takes long)
    #         axis.set_yscale("log")

    #     if metric_idx+1 == len(metrics) or args.one_plot:
    #         # only label x axis once
    #         axis.set_xlabel("Time (s)")
    #     elif not args.one_plot:
    #         xax = axis.get_xaxis()
    #         xax.set_visible(False)

    #     if args.one_plot and metric_idx == 1:
    #         axis.get_yaxis().set_ticks([0,1,2,3,4,5])


    plt.tight_layout()

    print(f'Writing output to {args.outfile}')
    plt.savefig(args.outfile)

if __name__ == "__main__":
    _main()
