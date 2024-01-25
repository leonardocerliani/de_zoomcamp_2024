# Terraform

[terraform.io](https://www.terraform.io/) allows to define the infrastructure of your project using code.

In other words, it allows you to avoid the gui-click nightmare you have to through if you want to setup an infrastructure on GCS, AWS, Azure or similar.

Instead, you (1) install Terraform locally, (2) download the code to interact with the cloud provider you want to work with , (3) provide Terraform your keys (like a .json) to interact with the cloud provider.

At this point, you write terraform tf files with specifications of the desired infrastructure, and they will instruct your cloud provider to create that infrastructure.

This also means that Terraform uses a **declarative style**: you tell it _what_ you want, and it will take care of _how_ to get it done.

Check out other advantages of tf in [this video](https://www.youtube.com/watch?v=nvNqfgojocs)


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

**Never expose these keys**. Michael in the video opens a VM and continues to work from there, which is probably one of the safest solutions.

For the moment, we will just make sure that this directory is in the .gitignore, and we will destroy the keys after the end of the video - from the Service Accounts >> Manage Keys. We can then re-create another set of keys and place them in the same location with the same name.


### Connect terraform to the GCS
Create a new `main.tf` file and open it in VS code. It can be very useful to have the HashiCorp Terraform extension installed, in order to get autocompletion.

To get started with the main.tf file, we can google "terraform google provider". On the top right of the first link we will click on "Use Provider" which will give us a starting boilerplate

continue from 11:13

Given the dangers of locally storing the json file with the keys, I came up with the following idea:
- build a Dockerfile of linux alpine with terraform
- map a local tf_files directory with the same in the container /tf_files
- note that this should be done when running the container, it cannot be specified in the dockerfile
- note also that this is instead possible with docker compose, so maybe that's the way to go
- run the container, create a new pair of keys and store them inside the container, e.g. in .gc. NB: this directory is NOT mapped to a local directory, and therefore will be destroyed when the container is shut down
- do what you need with terraform, and then close the container
- at this point, you can also remove the keys from the console.cloud.google.com.





















## Alternative setting on AWS
Sid Palas has a [2:30 hrs course](https://www.youtube.com/watch?v=7xngnjfIlK4&t=360s) on Terraform where he goes through a simple web app infrastructure built on AWS.The companion github repo is [here](https://github.com/sidpalas/devops-directive-terraform-course)

EOF
