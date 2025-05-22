# I will be comparing gene expression in 3 diffrent human cell lines
#the cell lines will be treated with Dexamethasone
#Dexamethasone provides relief for inflamed areas of the body.


# It is used to treat a number of different conditions, such as inflammation (swelling), severe allergies, adrenal problems, arthritis,  

#asthma, blood or bone marrow problems, kidney problems, skin conditions, and flare-ups of multiple sclerosis. 

#we will use a data set with 3 diffrent cell lines each with a treated and untreated sample 

#I will map the reads to a gene maper and see what specific genes are differentially expressed


import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Step 1: Load count data and metadata

# Load gene count data from a CSV file and convert the file into a pandas data frame. 
# This CSV contains gene expression counts: rows = genes, columns = samples.
counts_data = pd.read_csv(
    "C:\\Users\\dawso\\OneDrive\\Desktop\\counts_data (3).csv",index_col=0)
# Setting index col= 0 tells pd to use first colume of csv as row labels  
print(counts_data)

# assume first column is gene IDs
# Transpose if necessary: genes should be rows, samples should be columns
#In this case the transpose did not need to occure 
#But if I use this script for a diffrent project I might need to do this to the data

#if not counts_data.columns[0].startswith("SRR"):
 #   counts_data = counts_data.T
#print(counts_data)


# Load metadata (sample info)
# This typically contains information like treatment condition, timepoint, etc.
metadata = pd.read_csv("C:\\Users\\dawso\\OneDrive\\Desktop\\sample_info.csv", index_col=0)
print(metadata)

# Ensure numeric count data
# If any cells are not numbers, they'll be converted to NaN, and those rows will be dropped.
# .apply applies a function to each colume or row in the df 
# in this case the function to_numeric converts every cell of the df into a number 
#errors = coerce says if you can not convert the value into a number turn it into a NaN
#.dropna drops all Nans
#astype(int) converts all values into numbers (not strings or floats)
counts_data = counts_data.apply(pd.to_numeric, errors="coerce").dropna(axis=0)
counts_data = counts_data.astype(int) # Convert the counts to integers (now that we know they're numeric)





# Step 2: Pre-filtering genes with low counts 

# Remove genes with a total count less than 10 across all samples
# These genes are likely not informative for differential expression analysis
counts_data = counts_data[counts_data.sum(axis=1) >= 10]
print(counts_data)

# Ensure that sample names in counts_data match those in metadata.
# This is important so DESeq2 can match samples correctly.
counts_data = counts_data.loc[:, metadata.index]
counts_data





#Step 3: Create DESeqDataSet

dds = DeseqDataSet(
    counts=counts_data.T,  # PyDESeq2 expects samples as rows, genes as columns
    metadata=metadata,
    design_factors="dexamethasone" # This is the experimental condition to test
)





#Step 4: # Run the differential expression analysis using the DESeq2 algorithm
dds.deseq2()


#Define the contrast to compare: treated vs untreated in the "dexamethasone" condition.
contrast = ["dexamethasone", "treated", "untreated"]


#Get statisticly significant results
stat_res = DeseqStats(dds, alpha=0.05, contrast=contrast)


# Print a summary of the statistical results
stat_res.summary()


#Acess the statistical results 
res = stat_res.results_df
print(res)


# Map Ensembl gene IDs to human-readable gene symbols
#A enseble gene id is ie) ENSG00000139618
#id_map() connects to a database (like Ensembl or MyGene.info) that knows how to translate gene IDs to common gene names.
from sanbomics.tools import id_map
mapper = id_map(species = 'human')# Create a mapper for human genes


# Add a new column called "Symbol" that contains gene names instead of just IDs
#For each gene ID in the res DataFrame index ( Ensembl IDs), use the mapper to look up and assign the gene symbol, and store it in a new column called "Symbol".
res['Symbol'] = res.index.map(mapper.mapper) 
print(res)


## Filter out genes with very low expression (baseMean < 10)
res = res[res.baseMean >= 10]
res


# Further filter to show **significantly differentially expressed** genes:
# - padj < 0.05 = statistically significant
# - abs(log2FoldChange) > 0.5 = biologically meaningful effect size
sigs = res[(res.padj < 0.05) & (abs(res.log2FoldChange) > 0.5)]
print(sigs)


# Volcano Plot: visualize significance vs fold change
# Each dot is a gene: 
# - x-axis = log2FoldChange 
# - y-axis = -log10(p-value)
from sanbomics.plots import volcano
volcano(res, 
        symbol='Symbol', # Use gene symbols for labels
)
print(volcano)





