variable vm_names {
  description = "Map of VM names with names of secrets as values"
  type = map(string)
}

variable key_pair_name {
  description = "Key pair to ssh log in"
  type = string
}
