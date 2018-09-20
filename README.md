# Somatic pipeline

## Installation
* Python 3 is required.

```
python -m venv somatic_venv
. ./somatic_venv/bin/activate
pip install -r requirements.txt
```

## Dependencies
* reference/genome.fa: this file needs to be bwa indexed.

Modules
* bwa
* java
* samtools

Tools directory
* picard

### Strelka ###
```
wget https://github.com/Illumina/strelka/releases/download/v2.9.2/strelka-2.9.2.centos6_x86_64.tar.bz2
bunzip2 < strelka-2.9.2.centos6_x86_64.tar.bz2 | tar xvf -
```

### fastqc ###
```
wget http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.7.zip
unzip fastqc_v0.11.7.zip
chmod +x tools/FastQC/fastqc
```

### GATK 4
```
wget https://github.com/broadinstitute/gatk/releases/download/4.0.0.0/gatk-4.0.0.0.zip
```

### GATK 3.8.1
```
wget 'https://software.broadinstitute.org/gatk/download/auth?package=GATK-archive&version=3.8-1-0-gf15c1c3ef'
tar xvfj GenomeAnalysisTK-3.8-1-0-gf15c1c3ef.tar.bz2 
```

### GATK 4 Bundle
```
wget "gsapubftp-anonymous@ftp.broadinstitute.org:/bundle/b37/1000G_omni2.5.b37.sites.vcf.*"
wget ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/beta/Mutect2/af-only-gnomad.raw.sites.b37.vcf.gz
```

### DKFZBiasFilter
git clone https://github.com/supernifty/DKFZBiasFilter.git
pip install -r requirements.txt

### Conpair
```
git clone https://github.com/supernifty/Conpair.git
```

### pindel
wget https://github.com/genome/pindel/archive/v0.2.5b8.tar.gz
tar xvfj v0.2.5b8.tar.gz
cd pindel-0.2.5b8
module load gcc/6.4.0
module load htslib-intel/1.8
./INSTALL /usr/local/htslib/1.8-intel/

### Trimmomatic
```
wget http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.38.zip
unzip Trimmomatic-0.38.zip
```

### verifyBamID
```
wget https://github.com/statgen/verifyBamID/releases/download/v1.1.3/verifyBamIDLibStatGen.1.1.3.tgz
cd tools/verifyBamID_1.1.3
make
```

### mutational signature
cd tools
wget https://github.com/supernifty/mutational_signature/archive/0.1.tar.gz
tar xvfz 0.1.tar.gz
pip install -r mutational_signature-0.1/requirements.txt
cd -

### platypus
* request from http://www.well.ox.ac.uk/platypus
```
cd tools
git clone https://github.com/andyrimmer/Platypus
cd -
```

### varscan
cd tools
wget https://downloads.sourceforge.net/project/varscan/VarScan.v2.3.9.jar
cd -

The following R packages need to be installed:
```
#!/usr/bin/env Rscript

# installation
install.packages('optparse', repos = "http://cran.us.r-project.org")
source("http://bioconductor.org/biocLite.R");
biocLite("DNAcopy");
```

## Configuration

* cfg/config.yaml: set sample details
* cfg/cluster.json: set cluster resources

## Usage

```
./run.sh
```

## Directories
* cfg: configuration files
* in: input files (fastq)
* log: command logs
* out: generated files
* reference: reference files
* tools: 3rd party tools

## TODO
* extract all high impact to tsv
* include commonality in extracted tsv
