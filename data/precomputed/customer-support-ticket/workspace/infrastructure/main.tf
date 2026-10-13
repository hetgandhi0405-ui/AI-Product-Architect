# Terraform HCL Infrastructure Definition for Customer Support Ticket System
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_ecs_cluster" "app_cluster" {
  name = "customer-support-ticket-system-cluster"
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "customer-support-ticket-system-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "api-service"
      image     = "public.ecr.aws/ai-architect/customer-support-ticket-system:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
    }
  ])
}
