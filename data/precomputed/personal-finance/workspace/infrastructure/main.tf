# Terraform HCL Infrastructure Definition for Personal Finance Tracker
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
  name = "personal-finance-tracker-cluster"
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "personal-finance-tracker-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "api-service"
      image     = "public.ecr.aws/ai-architect/personal-finance-tracker:latest"
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
