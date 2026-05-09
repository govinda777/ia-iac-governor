variable "app_name" {
  description = "Nome da aplicação"
  type        = string
}

variable "environment" {
  description = "Ambiente (dev, prod)"
  type        = string
}

variable "compliance_level" {
  description = "Nível de compliance (pci, standard)"
  type        = string
  default     = "standard"
}
