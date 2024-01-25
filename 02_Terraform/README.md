# Terraform

[terraform.io](https://www.terraform.io/) allows to define the infrastructure of your project using code.

In other words, it allows you to avoid the gui-click nightmare you have to through if you want to setup an infrastructure on GCS, AWS, Azure or similar.

Instead, you (1) install Terraform locally, (2) download the code to interact with the cloud provider you want to work with , (3) provide Terraform your keys (like a .json) to interact with the cloud provider.

At this point, you write terraform tf files with specifications of the desired infrastructure, and they will instruct your cloud provider to create that infrastructure.

This also means that Terraform uses a **declarative style**: you tell it _what_ you want, and it will take care of _how_ to get it done.

Check out other advantages of tf in [this video](https://www.youtube.com/watch?v=nvNqfgojocs)

We can download the binary for terraform [here](https://developer.hashicorp.com/terraform/install) and then move it into a path dir, e.g. `/usr/local/bin`


## Terraform Primer - Concepts and Overview
[video](https://www.youtube.com/watch?v=s2bOYDCKl_M)

Key Terraform commands:

- Init : get the code to access the specific provider once you have indicated where the keys (a .json file) are on your machine

- Plan : shows the resources that will be created

- Apply : create the infrastructure defined in the tf files on the cloud provider platform

- Destroy : remove everything which is defined in the tf files


## Terraform basics - Simple one file Terraform Deployment
[video](https://www.youtube.com/watch?v=Y2ux7gq3Z0o)

### Create a Service Account
Once we are in our Google Cloud project, we first need to create a *service account**. This is like a regular account, except that it's not meant to log into. Instead it's used by software to run tasks.

`console >> IAM and admin >> service accounts >> Create a service account`

1. Fill in the service account name, e.g. `terraform-runner`
2. Grant this service account access to the project
  - Cloud Storage >> Storage Admin
  - BigQuery admin

In case we want to add/remove other roles, we can go to IAM (left menu), choose and edit the service account. In this case we will add Compute Engine >> admin

### Generate the keys for that service account
Service Accounts >> [choose the service account] >> Manage Keys >> Create New Keys

We are prompted to download the json file and we save these in a directory .gc.

**Never expose these keys**. Michael in the video opens a VM and continues to work from there, which is probably one of the safest solutions. Especially, don't put them on Dropbox or Google Drive!

For the moment, we will just make sure that this directory is in the .gitignore, and we will destroy the keys after the end of the video - from the Service Accounts >> Manage Keys. We can then re-create another set of keys and place them in the same location with the same name.


### Connect terraform to the GCS
Start VS Code and create a new `main.tf` file. It can be very useful to have the HashiCorp Terraform extension installed, in order to get autocompletion.

To get started with the main.tf file, we can google "terraform google provider". On the top right of the first link we will click on "Use Provider" which will give us a starting boilerplate

```bash
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
   project     = "my-project-id"
  region      = "europe-west4"
}
```

The location of the keys can be hardcoded into the tf file, which is not a great idea. We can then use an environmental variable

```bash
export GOOGLE_CREDENTIALS="./path/to/keys"
```

We can then unset this variable with `unset GOOGLE_CREDENTIALS`

Now that we provided the keys, we can get a tf provider.
```bash
terraform init
```

Which should return an output similar to this:
<details><summary>toggle show output</summary>

```
Initializing the backend...

Initializing provider plugins...
- Finding hashicorp/google versions matching "5.12.0"...
- Installing hashicorp/google v5.12.0...
- Installed hashicorp/google v5.12.0 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```
</details>

### Let's make a bucket... and destroy it!
To get the boilerplate we can google something like "terraform google cloud storage bucket".

Note that the name must be unique across all the google cloud. One way to ensure this is to use the project name as part of the bucket name (see below)

```bash
resource "google_storage_bucket" "demo-bucket" {
  name          = "de-zoomcamp-001-411007-terra-bucket"
  location      = "EU"
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}
```

we will remove the first lifecycle_rule and try to run it with `terraform plan` which shows us what will happen if we deploy.

```bash
terraform plan
```

<details><summary>output</summary>

```
Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # google_storage_bucket.demo-bucket will be created
  + resource "google_storage_bucket" "demo-bucket" {
      + effective_labels            = (known after apply)
      + force_destroy               = true
      + id                          = (known after apply)
      + location                    = "EU"
      + name                        = "auto-expiring-bucket"
      + project                     = (known after apply)
      + public_access_prevention    = (known after apply)
      + rpo                         = (known after apply)
      + self_link                   = (known after apply)
      + storage_class               = "STANDARD"
      + terraform_labels            = (known after apply)
      + uniform_bucket_level_access = (known after apply)
      + url                         = (known after apply)

      + lifecycle_rule {
          + action {
              + type = "AbortIncompleteMultipartUpload"
            }
          + condition {
              + age                   = 1
              + matches_prefix        = []
              + matches_storage_class = []
              + matches_suffix        = []
              + with_state            = (known after apply)
            }
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

<br>

Let's go ahead and apply these modifications.

```bash
terraform apply
```

```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

google_storage_bucket.demo-bucket: Creating...
google_storage_bucket.demo-bucket: Creation complete after 2s [id=de-zoomcamp-001-411007-terra-bucket]
```

A new `terraform.tfstate` file will be created.

If we go back to the google cloud console in `Cloud Storage >> Buckets` we will see the new bucket appearing.

Finally, once we have done what we need with this bucket, we can simply destroy it

```bash
terraform destroy
```

## Deployment with a variable file
[video](https://www.youtube.com/watch?v=PBi0hHjLftk)

Let's create a bigquery dataset. Again you can find the boilerplate with something like "terraform google bigquery dataset"

After terraform plan and apply, we can go to the BigQuery section of our console and see that also the dataset has been created.

After destroying these resources, we can see how to create something similar using **variables**. Variables can be stored either in a `variables.tf` file or in the `main.tf`.


Here's how the two files look like in order to use variables in the `main.tf`

<details>
<summary>main.tf</summary>

```bash
# main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.12.0"
    }
  }
}

provider "google" {
  credentials = "./.gc/chiavi.json"
  project     = var.project
  region      = var.region
}


resource "google_storage_bucket" "demo-bucket" {
  name          = "${var.project}-terra-bucket"
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_name
  location = var.location
}
```
</details>

<br>

<details>
<summary>variables.tf</summary>

```bash
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

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default = "demo_dataset"
}
```
</details>


### Use var + files for credentials
We previously authenticated by setting the path to the .json keys in the `$GOOGLE_CREDENTIALS` variable. Alternatively, we can specify the path as a variable and refer to the .json file pointed to by the variable in the main.tf file.

```bash
# main.tf
provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

# variables.tf
variable "credentials" {
  description = "Location of json keys"
  default = "/path/to/credentials.json"
}
```





## Alternative setting on AWS
Sid Palas has a [2:30 hrs course](https://www.youtube.com/watch?v=7xngnjfIlK4&t=360s) on Terraform where he goes through a simple web app infrastructure built on AWS.The companion github repo is [here](https://github.com/sidpalas/devops-directive-terraform-course)

EOF
