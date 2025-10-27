# Human Neural Network Model for Single-Cell RNA-seq Data Analysis

This R script provides functionality to classify cell types in single-cell RNA-seq data using a pre-trained neural network model. It is designed to work with Seurat objects and focuses on human cell type classification.

## Features

- Load and use a pre-trained PyTorch neural network model in R
- Classify cell types in Seurat objects
- Perform cluster-level annotations based on cell type predictions
- Compatible with both CPU and GPU (CUDA) environments

## Requirements

- R (>= 4.0.0)
- torch
- Seurat
- reticulate

## Installing LiverAnnotation
The LiverAnnotation package is available on GitHub. You can install it directly using the devtools package:
If you haven't already, install devtools:
```
install.packages("devtools")
```
Install LiverAnnotation from GitHub:
```
devtools::install_github("mThkTrn/LiverAnnotation")
```
### Updating LiverAnnotation
To update to the latest version of LiverAnnotation, simply run the installation command again:
```
devtools::install_github("mThkTrn/LiverAnnotation")
```
This will fetch and install the most recent version of the package from the GitHub repository.
## Setup

1. Clone this repository or download the R script.
2. Ensure you have the following files in your `models` directory:
   - `human.pt`: The PyTorch model file
   - `human_gene_cols.rds`: RDS file containing the gene names used in the model
   - `hle.rds`: RDS file containing the label encoder object

3. Update the `models_dir` variable in the script to point to your models directory:

```R
models_dir <- "path/to/your/models/directory"
```

## Usage

1. Source the R script in your R environment:

```R
source("path/to/human_nn_model_script.R")
```

2. Load your Seurat object:

```R
seurat_obj <- ReadH5AD("path/to/your/data.h5ad")  # If you have an h5ad file
# Or load your Seurat object directly
```

3. Classify cells:

```R
results <- classify_cells(seurat_obj)
seurat_obj$nn_model_predictions <- results$predictions
seurat_obj$nn_model_probabilities <- results$probabilities
```

4. Perform cluster-level annotation:

```R
cluster_annotations <- cluster_annotations(seurat_obj, algorithm = "prob")
```

## Functions

### `classify_cells(seurat_obj, batch_size = 128)`

Classifies cells in a Seurat object using the pre-trained neural network model.

- `seurat_obj`: A Seurat object containing single-cell RNA-seq data
- `batch_size`: Batch size for processing (default: 128)

Returns a list with two elements:
- `predictions`: Cell type predictions for each cell
- `probabilities`: Probability scores for each cell type

### `cluster_annotations(seurat_obj, clusters = "seurat_clusters", algorithm = "mode")`

Annotates clusters based on cell type predictions.

- `seurat_obj`: A Seurat object with cell type predictions (run `classify_cells` first)
- `clusters`: Name of the clustering metadata column (default: "seurat_clusters")
- `algorithm`: Method for cluster annotation, either "mode" or "prob" (default: "mode")

Returns a named vector of cluster annotations.

## Notes

- Ensure that your Seurat object's gene names match those used in training the model.
- The script will automatically use GPU if available, otherwise it will use CPU.
- Adjust the `Net` class definition if your saved model has a different architecture.

## Troubleshooting

If you encounter any issues:
1. Check that all required packages are installed and up-to-date.
2. Verify that the model files are in the correct location and format.
3. Ensure your Seurat object is properly formatted and contains gene expression data.

For any other issues, please open an issue in the repository.
