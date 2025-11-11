PLOTS = object-creation.pdf job-length.pdf micro-throughput.pdf micro-latency.pdf sharding.pdf object-partitioning.pdf app-latency.pdf timeout.pdf light-replication.pdf

all: $(PLOTS)

sharding.pdf: sharding/plot.py sharding/forum.csv sharding/filesystem.csv sharding/microblog.csv
	cd $(@:.pdf=) && python3 ./plot.py
	mv $(@:.pdf=/output.pdf) $@

app-latency.pdf: app-latency/plot.py sharding/forum.csv sharding/filesystem.csv sharding/microblog.csv
	cd $(@:.pdf=) && python3 ./plot.py
	mv $(@:.pdf=/output.pdf) $@

timeout.pdf: timeout/plot.sh timeout/plot_metrics.py timeout/cluster-metrics.csv timeout/extract_metrics.py
	cd $(@:.pdf=) && bash ./plot.sh
	mv $(@:.pdf=/output.pdf) $@

light-replication.pdf: light-replication/plot.sh light-replication/plot_metrics.py light-replication/cluster-metrics.csv light-replication/extract_metrics.py
	cd $(@:.pdf=) && bash ./plot.sh
	mv $(@:.pdf=/output.pdf) $@

%.pdf: %/plot.py %/results.csv
	cd $(@:.pdf=) && python3 ./plot.py
	mv $(@:.pdf=/output.pdf) $@

clean: 
	rm -f $(PLOTS)