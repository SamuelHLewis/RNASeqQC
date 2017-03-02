# RNASeqQC
## Purpose
A pipeline to quality filter, trim adapters, despike (if necessary) and QC paired-end RNA-Seq data

## Dependencies

Written in python3

[fastqc](http://www.bioinformatics.babraham.ac.uk/projects/fastqc/)

[bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

## Usage instructions

Basic usage is:
```bash
RNASeqQC.py -l left.fq.gz -r right.fq.gz
```
RNASeqQC takes two mandatory arguments:

	-l (input mate1 file)

	-r (input mate2 file)

RNASeqQC takes two optional arguments:

	-c (number of cores to use, default=1)

	-s (path to bowtie2 database for genome of spike-in sample)

