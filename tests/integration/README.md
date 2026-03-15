Integration test skeleton

This folder contains a docker-compose file that starts Redpanda (Kafka API compatible)
and Redis for local end-to-end testing.

Usage (example):

1. Start services:
   docker-compose -f docker-compose.yml up -d

2. Produce test messages to the `transactions` topic (e.g. using kafka-console-producer
   pointed at localhost:9092), then run a small driver that imports src.data.kafka_consumer
   and points it at the configs in configs/*.yaml

This is a skeleton to make it easier to iterate — the test runner and harness can be
implemented in a follow-up change.
