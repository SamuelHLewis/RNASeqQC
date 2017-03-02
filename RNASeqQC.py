#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

# argument parsing
parser=argparse.ArgumentParser(description="Read arguments")
parser.add_argument("-l","--left",type=str,help="Input mate1 file")
parser.add_argument("-r","--right",type=str,help="Input mate2 file")
parser.add_argument("-s","--spikein",type=str,help="Path to bowtie2 database for genome of spike-in sample")
parser.add_argument("-c","--cores",type=int,help="Number of cores to use (default=1)")
args=parser.parse_args()
# default values
Cores = 1
SpikeIn=False
# parse input mate1 file
if args.left is not None:
	LeftFile=args.left
	print("Mate1 file = "+LeftFile)
else:
	print("ERROR: input mate1 file (-l) not specified")
	sys.exit(0)
# parse input mate2 file
if args.right is not None:
	RightFile=args.right
	print("Mate2 file = "+RightFile)
else:
	print("ERROR: input mate2 file (-r) not specified")
	sys.exit(0)
# parse spike-in path
if args.spikein is not None:
	SpikeIn=args.spikein
	print("Path to spike-in = "+SpikeIn)
else:
	print("No spike-in specified")
# parse Cores
if args.cores is not None:
	if args.cores>0:
		Cores=int(args.cores)
		print("Using "+str(Cores)+" cores")
	else:
		print("Using default of 1 core")


# function to quality-filter and adapter-trim reads
def Filter(left,right):
	# trim adapters, trim bases with Q<20, retain unpaired reads in a separate file
	print('Filtering out low quality reads')
	cmd = 'trim_galore --paired --retain_unpaired -q 20 ' + left + ' ' + right
	subprocess.call(cmd,shell=True)
	if left.endswith(".fq.gz") and right.endswith(".fq.gz"):
		return(left.replace('.fq.gz','_val_1.fq.gz'),right.replace('.fq.gz','_val_2.fq.gz'))
	elif left.endswith(".fastq.gz") and right.endswith(".fastq.gz"):
		return(left.replace('.fastq.gz','_val_1.fq.gz'),right.replace('.fastq.gz','_val_2.fq.gz'))
	else:
		print("ERROR: Filter doesn't know what to return - left and right file endings must be different!")
		sys.exit(0)

# function to remove reads mapping to genome of spike-in sample
def Despiker(left,right,cores):
	# map the reads to spike-in genome, writing the mapped reads and unmapped reads to separate files
	print('Despiking trimmed read files')
	cmd = 'bowtie2 --fast --un-conc-gz ./despiked -p ' + str(cores) + ' -x ' + SpikeIn + ' -1 ' + left + ' -2 ' + right + ' -S SpikeInReads.sam'
	subprocess.call(cmd,shell=True)
	# rename despiked read files
	os.rename("despiked.1",left.replace("_1.fq.gz","_despiked_1.fq.gz"))
	os.rename("despiked.2",right.replace("_2.fq.gz","_despiked_2.fq.gz"))
	return(left.replace('_1.fq.gz','_despiked_1.fq.gz'),right.replace('_2.fq.gz','_despiked_2.fq.gz'))

# function to generate fastQC report for file
def QC(infile,cores=1):
	# make dir for fastQC results if it doesn't already exist
	if os.path.isdir('./fastqc') is False:
		print('Making fastqc output dir')
		os.makedirs('./fastqc')
	else:
		print('fastqc output dir already exists')
	# run fastQC on file (NB running fastqc v0.11.05 installed in user bin)
	print('QCing ' + infile)
	cmd = 'fastqc -t ' + str(cores) + ' -o ./fastqc ' + infile
	subprocess.call(cmd,shell=True)
	print('QC complete')

# function to quality filter and adapter trim a read file, remove spike-in, and generate fastQC profile
def RNASeqQC(leftinput,rightinput):
	# filter and trim reads
	File1Trimmed, File2Trimmed = Filter(left=leftinput,right=rightinput)
	# despike reads (if spike-in specified)
	if SpikeIn is not False:
		File1Despiked, File2Despiked = Despiker(left=File1Trimmed,right=File2Trimmed,cores=Cores)
		# QC reads
		QC(File1Despiked,cores=Cores)
		QC(File2Despiked,cores=Cores)
	else:
		# QC reads
		QC(File1Trimmed,cores=Cores)
		QC(File2Trimmed,cores=Cores)

RNASeqQC(leftinput=LeftFile,rightinput=RightFile)

