// Creates pubsub topic for flow logs
resource "google_pubsub_topic" "kentik_topic" {
  name        = "${var.topic_prefix}_topic"
  labels = {
    app = "kentik"
  }
}

// Creates pull subscription for Kentik log aggregation
resource "google_pubsub_subscription" "kentik_topic_subscription" {
  name        = "${var.topic_prefix}_topic_subscription"
  topic       = google_pubsub_topic.kentik_topic.name

  labels = {
    app = "kentik"
  }

}

// Allows Kentik to view logs
resource "google_pubsub_subscription_iam_binding" "pubsub_viewer" {
  subscription = google_pubsub_subscription.kentik_topic_subscription.name
  role         = "roles/pubsub.viewer"
  members = [
    "serviceAccount:kentik-vpc-flow@kentik-vpc-flow.iam.gserviceaccount.com",
  ]
}

// Allows Kentik to subscribe logs
resource "google_pubsub_subscription_iam_binding" "pubsub_subscriber" {
  subscription = google_pubsub_subscription.kentik_topic_subscription.name
  role         = "roles/pubsub.subscriber"
  members = [
    "serviceAccount:kentik-vpc-flow@kentik-vpc-flow.iam.gserviceaccount.com",
  ]
  depends_on = [google_pubsub_subscription_iam_binding.pubsub_viewer]
}
