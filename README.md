# sylph2krona

Convert [sylph](https://github.com/bluenote-1577/sylph) profiles to [Krona](https://github.com/marbl/Krona)-compatible format using [GTDB](https://gtdb.ecogenomic.org/) taxonomy.

## Requirements

- Python 3.9+
- pandas
- [GTDB taxonomy files](https://data.gtdb.ecogenomic.org/releases/latest/) (the latest are downloaded automatically if not present)
- [KronaTools](https://github.com/marbl/Krona/wiki/KronaTools) for visualization
- A sylph profile generated with a [GTDB sylph database](http://faust.compbio.cs.cmu.edu/sylph-stuff/) (e.g., gtdb-r226-c200-dbv1.syldb)

## Installation

The easiest way to use sylph2krona is via [uv](https://docs.astral.sh/uv/), e.g. for quick one-offs:
```bash
$ alias sylph2krona='uvx git+https://github.com/jonasoh/sylph2krona'
$ sylph2krona -h
<…>
usage: sylph2krona [-h] [--version] --input INPUT [--bac BAC] [--ar AR] [--abundance {tax,seq}] [--outdir OUTDIR]

sylph2krona v0.1.0: join sylph profile to GTDB taxonomy and emit krona-ready text files

options:
  -h, --help            show this help message and exit
  --version, -v         show version information and exit
  --input INPUT, -i INPUT
                        sylph profile tsv (use '-' for stdin)
  --bac BAC             GTDB bac taxonomy tsv file (can be gzipped)
  --ar AR               GTDB ar taxonomy tsv file (can be gzipped)
  --abundance {tax,seq}
                        which abundance column to use: tax (Taxonomic) or seq (Sequence) abundance
  --outdir OUTDIR, -o OUTDIR
                        output directory for *_krona.txt
```

Or to install it permanently in your Python environment:
```bash
uv pip install git+https://github.com/jonasoh/sylph2krona
```

## Usage

sylph2krona generates individual Krona-compatible text files for each sample in the input profile, and prints a suggested `ktImportText` command to generate a combined Krona HTML visualization.
After running the tool, use the suggested KronaTools command to generate the interactive HTML visualization.

```bash
# Basic usage
sylph2krona --input profile.tsv

# Custom output directory
sylph2krona --input profile.tsv --outdir my_results

# Using stdin to clean sample names
sed 's/.fastq.gz//g' profile.tsv | sylph2krona --input -

# Specifying GTDB taxonomy files
sylph2krona --input profile.tsv --bac path/to/bac120_taxonomy.tsv.gz --ar path/to/ar53_taxonomy.tsv.gz

# Using sequence abundance instead of taxonomic abundance
sylph2krona --input profile.tsv --abundance seq
```

<img width="1546" height="1442" alt="image" src="https://github.com/user-attachments/assets/8d0c5adc-cce5-47ca-833b-354d0b14b0f9" />
