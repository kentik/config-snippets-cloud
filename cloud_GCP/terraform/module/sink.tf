	// Create sink to gather logs from subnetwork. One sink per subnet
resource "google_logging_project_sink" "kentik_sink" {
  name        = "${var.sink_prefix}_sink"

    destination = "pubsub.googleapis.com/${google_pubsub_topic.kentik_topic.id}"

  filter  = "resource.type = gce_subnetwork AND ( resource.labels.subnetwork_name = ${join(" OR resource.labels.subnetwork_name = ", var.subnets_names_list)} )"

  unique_writer_identity = true
}
// Provides publisher role to each sink
resource "google_project_iam_binding" "log_writer" {
  role    = "roles/pubsub.publisher"
  project = var.project
  members = [
    google_logging_project_sink.kentik_sink.writer_identity,
  ]
}
