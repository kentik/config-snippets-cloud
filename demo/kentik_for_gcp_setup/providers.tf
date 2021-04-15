terraform {
  required_version = ">= 0.12.0"
  required_providers {
    google = {
      version = ">= 3.41.0"
    }
    kentik-cloudexport = {
      version = "0.1.0"
      source = "kentik/kentik-cloudexport"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

provider "kentik-cloudexport" {
  # email, token and apiurl are read from KTAPI_AUTH_EMAIL, KTAPI_AUTH_TOKEN, KTAPI_URL env variables
}
