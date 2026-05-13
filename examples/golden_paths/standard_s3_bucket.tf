module "standard_s3" {
  source      = "./golden_paths/s3" # In a real scenario, this would be a git path
  bucket_name = "approved-standard-bucket"
  tags = {
    Project    = "Internal"
    CostCenter = "IT-101"
  }
}
