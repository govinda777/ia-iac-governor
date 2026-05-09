resource "aws_s3_bucket" "no_tags" {
  bucket = "forgot-to-tag-me"
  # Violation: missing mandatory tags CostCenter and Project
}
