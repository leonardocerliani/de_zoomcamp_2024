terraform {
  required_providers {
    google = {
      # credentials = "./path/to/keys"
      source = "hashicorp/google"
      version = "5.12.0"
    }
  }
}

provider "google" {
  project     = "de-zoomcamp-001-411007"
  region      = "europe-west4"
}


resource "google_storage_bucket" "taxi-bucket" {
  for_each = var.buckets

  name          = "${var.project}-${each.value}-terra-bucket"
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "Delete"
    }
  }
}
