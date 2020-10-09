// Create sink to gather logs from subnetwork. One sink per subnet
resource "google_logging_project_sink" "kentik_sink" {
  for_each    = toset(var.subnets_names_list)
  name        = "${var.sink_prefix}_${each.key}"

  destination = "pubsub.googleapis.com/projects/kentik-291211/topics/${var.topic_prefix}_topic"

  filter = "resource.type = gce_subnetwork AND resource.labels.subnetwork_name = ${each.key}"

  unique_writer_identity = true
}
// Provides publisher role to each sink
resource "google_project_iam_binding" "log_writer" {
  for_each    = toset(var.subnets_names_list)
  role        = "roles/pubsub.publisher"
  members = [
    google_logging_project_sink.kentik_sink[each.key].writer_identity,
  ]
}
