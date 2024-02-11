variable "project" {
  description = "Project ID"
  default = "de-zoomcamp-001-411007"
}

variable "region" {
  description = "Region"
  default = "europe-west4"
}

variable "location" {
  description = "Project Location"
  default = "EU"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default = "STANDARD"
}

variable "buckets" {
  description = "A map of bucket names to create"
  type        = map(string)
  default     = {
    "yellow-taxi" = "yellow-taxi",
    "green-taxi"  = "green-taxi",
    "fhv-vehicles" = "fhv-taxi"
  }
}

