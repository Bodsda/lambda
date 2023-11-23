# S3 state bucket:

variable "force_destroy" {
  description = "A boolean that indicates all objects (including any locked objects) should be deleted from the bucket so that the bucket can be destroyed without error. These objects are not recoverable. Defaults to 'false'."
  type        = bool
}

variable "versioning" {
  description = "(bool) - A state of versioning."
  type        = bool
}

variable "global_tags" {
  description = "A set of tags to apply to all 'taggable' resources."
  type        = map(string)
}
