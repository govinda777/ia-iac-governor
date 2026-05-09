module "standard_s3" {
  source      = "../../golden_paths" # In a real scenario, this would be a git path
  bucket_name = "approved-standard-bucket"
  tags = {
    Project    = "Internal"
    CostCenter = "IT-101"
  }
}
