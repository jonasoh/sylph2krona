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
alias sylph2krona='uvx git+https://github.com/jonasoh/sylph2krona'
sylph2krona -h
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

# Using stdin to clean sample names
sed 's/.fastq.gz//g' profile.tsv | sylph2krona --input -

# Specifying GTDB taxonomy files
sylph2krona --input profile.tsv --bac path/to/bac120_taxonomy.tsv.gz --ar path/to/ar53_taxonomy.tsv.gz

# Using sequence abundance instead of taxonomic abundance
sylph2krona --input profile.tsv --abundance seq

# Custom output directory
sylph2krona --input profile.tsv --outdir my_results
```

<img width="1546" height="1442" alt="image" src="https://github.com/user-attachments/assets/8d0c5adc-cce5-47ca-833b-354d0b14b0f9" />
