#!/usr/bin/env python3
# @package    sylph2krona
# @version    0.1.0
# @license    MIT
# @author     Jonas Ohlsson <jonas.ohlsson at slu.se>
# @depends    pandas>=2.3,<3
"""
Convert Sylph profiles to Krona-compatible format using GTDB taxonomy.
"""

import re
import sys
import os
import hashlib
import argparse
import pandas as pd
import urllib.request
from pathlib import Path


def read_gtdb_tax(paths):
    # read one or more gtdb taxonomy tsvs (two cols: id \t taxonomy)
    # keys look like RS_GCF_..., GB_GCA_...; we store both the raw key and a version stripped of RS_/GB_
    frames = []
    for p in paths:
        if p is None:
            continue
        # Handle gzipped files
        if p.endswith(".gz"):
            # pandas can read directly from gzipped files
            df = pd.read_csv(
                p,
                sep="\t",
                header=None,
                names=["gtdb_id", "gtdb_taxonomy"],
                compression="gzip",
            )
        else:
            df = pd.read_csv(
                p, sep="\t", header=None, names=["gtdb_id", "gtdb_taxonomy"]
            )
        frames.append(df)
    if not frames:
        return {}
    gtdb = pd.concat(frames, ignore_index=True).drop_duplicates("gtdb_id")
    # make a dict with multiple access patterns
    taxmap = {}
    for gid, tax in zip(gtdb["gtdb_id"], gtdb["gtdb_taxonomy"]):
        taxmap[gid] = tax
        # strip RS_/GB_ prefix
        bare = re.sub(r"^(RS_|GB_)", "", gid)
        taxmap[bare] = tax
        # also keep a key without version, just in case (e.g., GCA_012345678)
        novers = re.sub(r"\.\d+$", "", bare)
        taxmap[novers] = tax
    return taxmap


def extract_accession(genome_file):
    # pull gca/gcf accession with version from a path like .../GCA_012345678.1_genomic.fna.gz
    m = re.search(r"(GCA|GCF)_\d+\.\d+", genome_file)
    return m.group(0) if m else None


def gtdb_to_krona_path(tax):
    # convert 'd__Bacteria;p__Firmicutes;...' to a krona path like 'root;Bacteria;Firmicutes;...'
    if pd.isna(tax) or tax == "":
        return None
    parts = tax.split(";")
    parts = [re.sub(r"^(d|p|c|o|f|g|s|t)__", "", p) for p in parts]
    return "root;" + ";".join(parts)


def fallback_from_contig(contig_name):
    # very light heuristic fallback if accession not found in gtdb
    # strip leading accession and any prefix up to colon, cut at first comma
    s = re.sub(r"^[^:]+:\s*", "", contig_name)
    s = s.split(",", 1)[0].strip()
    if not s:
        return "root;unclassified"
    toks = re.split(r"\s+", s)
    toks = [
        t
        for t in toks
        if t.lower() not in {"bin", "isolate", "strain", "mag", "tpa_asm"}
    ]
    toks = [re.sub(r"[^A-Za-z0-9_-]", "_", t) for t in toks if t]
    if not toks:
        toks = ["unclassified"]
    return "root;" + ";".join(toks)


def safe_fname(x):
    # make filesystem-friendly filename
    return re.sub(r"[^A-Za-z0-9._-]", "_", x)


def get_gtdb_version():
    """Download VERSION.txt to get the current GTDB version"""
    # Try both mirrors
    urls = [
        "https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/VERSION.txt",
        "https://data.gtdb.ecogenomic.org/releases/latest/VERSION.txt",
    ]

    for url in urls:
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode("utf-8")
                # Extract just the first line
                version = content.split("\n")[0].strip()
                return version
        except Exception as e:
            print(f"Warning: Failed to fetch GTDB version from {url}: {str(e)}")

    return "unknown"


def download_taxonomy_file(file_name):
    """Download GTDB taxonomy file if it doesn't exist locally"""
    if os.path.exists(file_name):
        return file_name

    # try to use local .gz version even if not requested
    if not file_name.endswith(".gz") and os.path.exists(f"{file_name}.gz"):
        return f"{file_name}.gz"

    # download gzipped taxonomy
    download_name = f"{file_name}.gz" if not file_name.endswith(".gz") else file_name

    # get md5 checksums for verification
    checksums = get_md5_checksums()
    base_filename = os.path.basename(download_name)
    expected_md5 = checksums.get(base_filename)

    # Try both mirrors
    urls = [
        f"https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/{os.path.basename(download_name)}",
        f"https://data.gtdb.ecogenomic.org/releases/latest/{os.path.basename(download_name)}",
    ]

    print(f"Downloading {os.path.basename(download_name)}... ", end="")
    for url in urls:
        try:
            urllib.request.urlretrieve(url, download_name)
            print(f"Saved to {download_name}")

            # verify md5 checksum if available
            if expected_md5:
                with open(download_name, "rb") as f:
                    file_md5 = hashlib.md5(f.read()).hexdigest()

                if not file_md5 == expected_md5:
                    print(
                        f"ERROR: MD5 checksum mismatch! Expected {expected_md5}, got {file_md5}"
                    )
                    sys.exit(1)
            else:
                print("No MD5 checksum available for verification")

            return download_name
        except Exception as e:
            print(f"Failed to download from {url}: {str(e)}")

    sys.exit(f"ERROR: Could not download taxonomy file {file_name}. Exiting.")
    return None


def get_md5_checksums():
    """Download MD5SUM.txt and parse it into a dictionary of filename: md5hash"""
    urls = [
        "https://data.ace.uq.edu.au/public/gtdb/data/releases/latest/MD5SUM.txt",
        "https://data.gtdb.ecogenomic.org/releases/latest/MD5SUM.txt",
    ]

    checksums = {}
    for url in urls:
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode("utf-8")
                # Parse each line - format is "md5hash  ./filename"
                for line in content.splitlines():
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            md5_hash = parts[0].strip()
                            filename = os.path.basename(parts[1].strip())
                            # Remove version suffix like _r123 to match generic filenames
                            generic_name = re.sub(r"_r\d+", "", filename)
                            checksums[generic_name] = md5_hash
                            # Also keep the original name for direct matching
                            checksums[filename] = md5_hash
                return checksums
        except Exception as e:
            print(f"Warning: Failed to fetch MD5 checksums from {url}: {str(e)}")

    return checksums


def main():
    ap = argparse.ArgumentParser(
        description="join sylph profile to gtdb taxonomy and emit krona-ready text files per sample"
    )
    ap.add_argument(
        "--input", "-i", required=True, help="sylph profile tsv (use '-' for stdin)"
    )
    ap.add_argument(
        "--bac",
        default="bac120_taxonomy.tsv",
        help="GTDB bac taxonomy tsv file (can be gzipped)",
    )
    ap.add_argument(
        "--ar",
        default="ar53_taxonomy.tsv",
        help="GTDB ar taxonomy tsv file (can be gzipped)",
    )
    ap.add_argument(
        "--abundance",
        choices=["tax", "seq"],
        default="tax",
        help="which abundance column to use: tax (Taxonomic) or seq (Sequence) abundance",
    )
    ap.add_argument(
        "--outdir", "-o", default="krona_out", help="output directory for *_krona.txt"
    )
    args = ap.parse_args()

    # Get GTDB version before downloading files
    gtdb_version = get_gtdb_version()

    # download taxonomy files if they don't exist
    bac_file = download_taxonomy_file(args.bac)
    ar_file = download_taxonomy_file(args.ar)

    def check_file_exists(file_path):
        return os.path.exists(file_path) or os.path.exists(f"{file_path}.gz")

    if not (check_file_exists(args.bac) and check_file_exists(args.ar)):
        print(
            f"\nWARNING: GTDB taxonomy files are downloaded for version {gtdb_version}. "
            f"Make sure that this version matches your sylph database!\n"
        )

    # load gtdb taxonomy maps
    taxmap = read_gtdb_tax([bac_file, ar_file])

    # read sylph profile - handle stdin if input is "-"
    if args.input == "-":
        sylph = pd.read_csv(sys.stdin, sep="\t")
    else:
        sylph = pd.read_csv(args.input, sep="\t")

    # Map short abundance options to full column names
    abundance_map = {
        "tax": "Taxonomic_abundance",
        "seq": "Sequence_abundance",
    }
    abundance_col = abundance_map[args.abundance]

    # basic column checks
    required_cols = {"Sample_file", "Genome_file", "Contig_name", abundance_col}
    missing = required_cols - set(sylph.columns)
    if missing:
        sys.exit(
            f"missing required columns in sylph file: {', '.join(sorted(missing))}"
        )

    # extract accession and map to taxonomy
    sylph["accession"] = sylph["Genome_file"].apply(extract_accession)
    sylph["gtdb_taxonomy"] = sylph["accession"].map(taxmap)

    # build krona path with gtdb, falling back to contig-based heuristic
    sylph["krona_path"] = sylph.apply(
        lambda r: str(
            gtdb_to_krona_path(r["gtdb_taxonomy"])
            if pd.notna(r["gtdb_taxonomy"]) and r["gtdb_taxonomy"] != ""
            else fallback_from_contig(r["Contig_name"])
        ),
        axis=1,
    )

    # choose abundance
    sylph["abundance"] = sylph[abundance_col].astype(float)

    # aggregate identical paths per sample
    grouped = sylph.groupby(["Sample_file", "krona_path"], as_index=False)[
        "abundance"
    ].sum()

    # write one krona file per cleaned sample name
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    written = []
    for sample, g in grouped.groupby("Sample_file"):
        out_path = outdir / f"{safe_fname(sample)}_krona.txt"
        g_out = g[["abundance", "krona_path"]].copy()
        # krona expects: number \t level1 \t level2 ... but also accepts 'number \t semicolon path'
        # we will split the semicolon path into columns to be maximally compliant
        # path like 'root;a;b;c' -> columns: number, root, a, b, c
        split_cols = g_out["krona_path"].str.split(";", expand=True)
        to_write = pd.concat([g_out[["abundance"]], split_cols], axis=1)
        to_write.to_csv(out_path, sep="\t", header=False, index=False)
        # g_out.to_csv(out_path, sep="\t", header=False, index=False)
        written.append((out_path, sample))

    # print a handy ktImportText command suggestion to stdout
    args_joined = " ".join(f"{p},{n}" for p, n in written)
    print("# run this to build a multi-dataset krona chart")
    print(f"ktImportText {args_joined} -o {outdir / 'sylph2krona.html'}")


if __name__ == "__main__":
    main()
