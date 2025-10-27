library(torch)
library(Seurat)
library(reticulate)
library(here)

# Set up device
device <- if(cuda_is_available()) torch_device("cuda") else torch_device("cpu")
cat("Using device:", device$type, "\n")

# Define the neural network class
Net <- nn_module(
  "Net",
  initialize = function(input_size, hidden_size, num_classes) {
    self$fc1 <- nn_linear(input_size, hidden_size)
    self$relu <- nn_relu()
    self$fc2 <- nn_linear(hidden_size, num_classes)
  },
  forward = function(x) {
    x %>%
      self$fc1() %>%
      self$relu() %>%
      self$fc2()
  }
)

# # Load the model and other objects
models_dir <- "R/models"  # Update this path
human_gene_cols <- readRDS(here(models_dir, "human_gene_cols.rds"))
hle <- readRDS(here(models_dir, "hle.rds"))

# Load the model architecture
human_model_nn <- torch_load(here(models_dir, "human_model_architecture.pt"))

# Load the state dictionary
human_model_state <- torch_load(here(models_dir, "human_model_state_dict.pt"))

# Load the state dictionary into the model
human_model_nn$load_state_dict(human_model_state)

cat("Human model loaded successfully.\n")

# Classification function
classify_cells <- function(seurat_obj, batch_size = 128) {
  # Get the gene expression matrix
  exp_matrix <- GetAssayData(seurat_obj, slot = "data")

  # Find shared genes
  shared_genes <- intersect(human_gene_cols, rownames(exp_matrix))

  if (length(shared_genes) != length(human_gene_cols)) {
    cat("Warning:", length(human_gene_cols) - length(shared_genes),
        "genes from the training data are not in this dataset.\n")
  }

  # Prepare the input matrix
  mat_with_missing <- matrix(0, ncol = length(human_gene_cols), nrow = ncol(exp_matrix))
  colnames(mat_with_missing) <- human_gene_cols
  mat_with_missing[, shared_genes] <- t(as.matrix(exp_matrix[shared_genes, ]))

  # Convert to torch tensor
  tensor_data <- torch_tensor(mat_with_missing, dtype = torch_float32())

  # Create DataLoader
  dataset <- tensor_dataset(tensor_data)
  dataloader <- dataloader(dataset, batch_size = batch_size, shuffle = FALSE)

  # Make predictions
  all_preds <- list()
  all_probs <- list()

  human_model_nn$eval()

  with_no_grad({
    for (batch in dataloader) {
      batch <- batch[[1]]$to(device)
      outputs <- human_model_nn(batch)
      probs <- nnf_softmax(outputs, dim = 2)
      preds <- torch_max(outputs, dim = 2)$indices
      all_preds <- c(all_preds, preds$cpu()$numpy())
      all_probs <- c(all_probs, probs$cpu()$numpy())
    }
  })

  # Convert predictions to cell type names
  pred_names <- hle$inverse_transform(unlist(all_preds))

  # Return predictions and probabilities
  list(predictions = pred_names, probabilities = all_probs)
}

# Helper function for most frequent element
most_frequent <- function(x) {
  names(sort(table(x), decreasing = TRUE))[1]
}

# Cluster annotation function
cluster_annotations <- function(seurat_obj, clusters = "seurat_clusters", algorithm = "mode") {
  if (!(clusters %in% colnames(seurat_obj@meta.data))) {
    stop("Specified cluster column not found in Seurat object metadata.")
  }

  # Run cell classification if not already done
  if (!"nn_model_predictions" %in% colnames(seurat_obj@meta.data)) {
    results <- classify_cells(seurat_obj)
    seurat_obj$nn_model_predictions <- results$predictions
    seurat_obj$nn_model_probabilities <- results$probabilities
  }

  cluster_names <- unique(seurat_obj@meta.data[[clusters]])

  if (algorithm == "mode") {
    out <- sapply(cluster_names, function(name) {
      cells <- WhichCells(seurat_obj, expression = paste0(clusters, " == '", name, "'"))
      most_frequent(seurat_obj$nn_model_predictions[cells])
    })
  } else if (algorithm == "prob") {
    out <- sapply(cluster_names, function(name) {
      cells <- WhichCells(seurat_obj, expression = paste0(clusters, " == '", name, "'"))
      probs <- do.call(rbind, seurat_obj$nn_model_probabilities[cells])
      sum_probs <- colSums(probs)
      pred <- which.max(sum_probs)
      hle$inverse_transform(pred - 1)  # Subtract 1 because R is 1-indexed
    })
  } else {
    stop("algorithm must be either 'mode' or 'prob'")
  }

  names(out) <- cluster_names
  out
}

test_data = readRDS(here("R", "testdata", "Integrated_with_Subannotations.RDS"))

classify_cells(test_data)
