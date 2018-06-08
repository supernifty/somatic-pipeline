#!/bin/bash

# run on the cluster
MAXJOBS=64
PREFIX="ls"

echo "cleaning up..."
mkdir -p log
rm log/*
mkdir -p tmp
rm -r tmp/*

# dry
echo "dry run..."
snakemake --verbose -n -j $MAXJOBS --cluster-config cfg/cluster.json --rerun-incomplete --jobname "${PREFIX}-{rulename}-{jobid}" --cluster "sbatch -A {cluster.account} -p {cluster.partition} --ntasks={cluster.n}  -t {cluster.time} --mem={cluster.memory} --output=log/slurm-%j.out --error=log/slurm-%j.out"
echo "return to start pipeline, ctrl-c to quit"
read -n 1 -p "Continue?"

# real
echo "starting live run at $(date)..."
snakemake -p -j $MAXJOBS --cluster-config cfg/cluster.json --rerun-incomplete --jobname "${PREFIX}-{rulename}-{jobid}" --cluster "sbatch -A {cluster.account} -p {cluster.partition} --ntasks={cluster.n}  -t {cluster.time} --mem={cluster.memory} --output=log/slurm-%j.out --error=log/slurm-%j.out"
echo "finished at $(date)"
