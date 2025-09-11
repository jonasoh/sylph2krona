# sylph2krona

Convert [sylph](https://github.com/bluenote-1577/sylph) profiles to [Krona](https://github.com/marbl/Krona)-compatible format using [GTDB](https://gtdb.ecogenomic.org/) taxonomy.

## Requirements

- Python 3.6+
- pandas
- [GTDB taxonomy files](https://data.gtdb.ecogenomic.org/releases/latest/) (the latest are downloaded automatically if not present)
- [KronaTools](https://github.com/marbl/Krona/wiki/KronaTools) for visualization
- A sylph profile generated with a [GTDB sylph database](http://faust.compbio.cs.cmu.edu/sylph-stuff/) (e.g., gtdb-r226-c200-dbv1.syldb)

## Usage

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

sylph2krona generates individual Krona-compatible text files for each sample in the input profile,
and prints a suggested `ktImportText` command to generate a combined Krona HTML visualization.
After running the tool, use the suggested KronaTools command to generate the interactive HTML visualization.
