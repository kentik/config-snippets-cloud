output "subscription" {
  value       = google_pubsub_subscription.kentik_topic_subscription.name
  description = "Subscribtion name for kentik config"
}
