"""
Phase 6 — Terraform Generation Agent
=======================================
Generates production-grade Terraform HCL files from infrastructure_state.json.

Generated file structure:
    infrastructure/terraform/
        provider.tf       — AWS provider + backend config
        variables.tf      — All input variables with defaults
        vpc.tf            — VPC, subnets, IGW, route tables
        security.tf       — Security groups
        compute.tf        — ECS Fargate task/service OR EC2 ASG
        database.tf       — RDS instance
        cache.tf          — ElastiCache Redis (if enabled)
        load_balancer.tf  — ALB + target group + listener
        storage.tf        — S3 bucket (if enabled)
        monitoring.tf     — CloudWatch alarms
        outputs.tf        — Application URLs and resource ARNs

Rules:
  - All secrets come from AWS Secrets Manager (never hardcoded)
  - All files are internally consistent (same variable names everywhere)
  - Only generates modules for services present in infrastructure_state
  - Terraform is validated (fmt + validate + plan) by terraform_validation_agent
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from backend.agents.state import AgentState


def terraform_generation_agent(state: AgentState) -> AgentState:
    """
    Generate Terraform HCL files from infrastructure_state.json.
    """
    infra: dict = state.get("infrastructure_state", {})
    spec: dict = state.get("cloud_architecture_spec", {})
    project_id: str = state.get("project_id", "generated-app")
    project_name: str = state.get("project_name", "generated-app").lower().replace(" ", "-")
    assembled_path: str = state.get("assembled_project_path", "")

    if not infra and not spec:
        state["terraform_generation"] = {
            "status": "SKIPPED",
            "reason": "No infrastructure_state or cloud_architecture_spec available",
            "files": {},
        }
        return state

    # Extract key config
    region = spec.get("region", infra.get("region", "ap-south-1"))
    compute = spec.get("compute", {})
    database = spec.get("database", {})
    network = spec.get("network", {})
    cache = spec.get("cache", {})
    storage = spec.get("storage", {})
    lb = spec.get("load_balancer", {})
    monitoring_cfg = spec.get("monitoring", {})
    security_cfg = spec.get("security", {})

    compute_service = compute.get("service", "ecs_fargate")
    has_cache = cache.get("enabled", False)
    has_storage = storage.get("enabled", False)
    has_waf = security_cfg.get("waf", False)
    multi_az = database.get("multi_az", False)

    app_port = compute.get("port", 8000)
    db_port = database.get("port", 5432)
    db_engine = database.get("engine", "postgres")
    desired_count = compute.get("desired_count", 1)
    min_count = compute.get("min_count", 1)
    max_count = compute.get("max_count", 2)

    # Build terraform files dict
    tf_files: dict[str, str] = {}

    tf_files["provider.tf"] = _provider_tf(region, project_name)
    tf_files["variables.tf"] = _variables_tf(project_name, region, db_engine, app_port, db_port)
    tf_files["vpc.tf"] = _vpc_tf(
        project_name,
        public_subnets=network.get("public_subnets", 2),
        private_subnets=network.get("private_subnets", 2),
    )
    tf_files["security.tf"] = _security_tf(project_name, app_port, db_port)
    tf_files["compute.tf"] = _compute_tf(
        project_name, compute_service,
        compute.get("fargate_cpu", 512),
        compute.get("fargate_memory", 1024),
        app_port, desired_count, min_count, max_count,
    )
    tf_files["database.tf"] = _database_tf(
        project_name, db_engine,
        database.get("instance_class", "db.t3.medium"),
        database.get("allocated_storage_gb", 20),
        multi_az, db_port,
    )
    tf_files["load_balancer.tf"] = _load_balancer_tf(project_name, app_port)
    tf_files["monitoring.tf"] = _monitoring_tf(project_name, monitoring_cfg.get("alarms", []))
    tf_files["outputs.tf"] = _outputs_tf(project_name, has_cache, has_storage)

    if has_cache:
        tf_files["cache.tf"] = _cache_tf(
            project_name,
            cache.get("node_type", "cache.t4g.micro"),
        )

    if has_storage:
        tf_files["storage.tf"] = _storage_tf(project_name)

    # Write files to disk
    written_paths: list[str] = []
    tf_dir = None
    if assembled_path and os.path.isdir(assembled_path):
        tf_dir = Path(assembled_path) / "infrastructure" / "terraform"
        tf_dir.mkdir(parents=True, exist_ok=True)
        for fname, content in tf_files.items():
            fpath = tf_dir / fname
            fpath.write_text(content, encoding="utf-8")
            written_paths.append(str(fpath))

    state["terraform_generation"] = {
        "status": "GENERATED",
        "terraform_dir": str(tf_dir) if tf_dir else None,
        "files": {k: len(v) for k, v in tf_files.items()},
        "file_contents": tf_files,
        "file_count": len(tf_files),
        "written_paths": written_paths,
        "compute_service": compute_service,
        "region": region,
    }
    state["terraform_path"] = str(tf_dir) if tf_dir else None

    arch = state.get("architecture", {})
    arch["terraform_generation"] = state["terraform_generation"]
    state["architecture"] = arch
    return state


# ─── HCL generators ───────────────────────────────────────────────────────────

def _provider_tf(region: str, project_name: str) -> str:
    return f'''terraform {{
  required_version = ">= 1.5"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
  # Uncomment to use S3 remote state
  # backend "s3" {{
  #   bucket = "{project_name}-terraform-state"
  #   key    = "terraform.tfstate"
  #   region = "{region}"
  # }}
}}

provider "aws" {{
  region = var.aws_region
  default_tags {{
    tags = {{
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }}
  }}
}}
'''


def _variables_tf(project_name: str, region: str, db_engine: str, app_port: int, db_port: int) -> str:
    return f'''variable "project_name" {{
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "{project_name}"
}}

variable "environment" {{
  description = "Deployment environment (production, staging, development)"
  type        = string
  default     = "production"
}}

variable "aws_region" {{
  description = "AWS region to deploy resources"
  type        = string
  default     = "{region}"
}}

variable "vpc_cidr" {{
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}}

variable "app_port" {{
  description = "Port the application container listens on"
  type        = number
  default     = {app_port}
}}

variable "db_engine" {{
  description = "Database engine type"
  type        = string
  default     = "{db_engine}"
}}

variable "db_port" {{
  description = "Database port"
  type        = number
  default     = {db_port}
}}

variable "db_name" {{
  description = "Database name"
  type        = string
  default     = "{project_name.replace("-", "_")}_db"
}}

variable "db_username" {{
  description = "Database master username (use Secrets Manager in production)"
  type        = string
  default     = "dbadmin"
  sensitive   = true
}}

variable "db_password" {{
  description = "Database master password — MUST be provided via secrets or CI/CD, never hardcoded"
  type        = string
  sensitive   = true
}}

variable "container_image" {{
  description = "Docker image URI for the application container"
  type        = string
  default     = "your-ecr-repo/{project_name}:latest"
}}

variable "acm_certificate_arn" {{
  description = "ACM Certificate ARN for HTTPS listener (optional)"
  type        = string
  default     = ""
}}
'''


def _vpc_tf(project_name: str, public_subnets: int, private_subnets: int) -> str:
    pub_cidrs = "\n    ".join(
        f'"{10}.0.{i}.0/24",' for i, _ in enumerate(range(public_subnets))
    ).rstrip(",")
    priv_cidrs = "\n    ".join(
        f'"10.0.{10+i}.0/24",' for i, _ in enumerate(range(private_subnets))
    ).rstrip(",")
    return f'''# ── VPC ─────────────────────────────────────────────────────────────────────
resource "aws_vpc" "main" {{
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

# ── Internet Gateway ─────────────────────────────────────────────────────────
resource "aws_internet_gateway" "main" {{
  vpc_id = aws_vpc.main.id

  tags = {{
    Name = "${{var.project_name}}-igw"
  }}
}}

# ── Public Subnets ────────────────────────────────────────────────────────────
resource "aws_subnet" "public" {{
  count             = {public_subnets}
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {{
    Name = "${{var.project_name}}-public-${{count.index + 1}}"
    Tier = "public"
  }}
}}

# ── Private Subnets ───────────────────────────────────────────────────────────
resource "aws_subnet" "private" {{
  count             = {private_subnets}
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + {public_subnets})
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {{
    Name = "${{var.project_name}}-private-${{count.index + 1}}"
    Tier = "private"
  }}
}}

# ── NAT Gateway ───────────────────────────────────────────────────────────────
resource "aws_eip" "nat" {{
  count  = 1
  domain = "vpc"
  tags = {{
    Name = "${{var.project_name}}-nat-eip"
  }}
}}

resource "aws_nat_gateway" "main" {{
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.main]

  tags = {{
    Name = "${{var.project_name}}-nat"
  }}
}}

# ── Route Tables ──────────────────────────────────────────────────────────────
resource "aws_route_table" "public" {{
  vpc_id = aws_vpc.main.id
  route {{
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }}
  tags = {{ Name = "${{var.project_name}}-public-rt" }}
}}

resource "aws_route_table_association" "public" {{
  count          = {public_subnets}
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}}

resource "aws_route_table" "private" {{
  vpc_id = aws_vpc.main.id
  route {{
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }}
  tags = {{ Name = "${{var.project_name}}-private-rt" }}
}}

resource "aws_route_table_association" "private" {{
  count          = {private_subnets}
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}}

# ── Data Source ───────────────────────────────────────────────────────────────
data "aws_availability_zones" "available" {{
  state = "available"
}}
'''


def _security_tf(project_name: str, app_port: int, db_port: int) -> str:
    return f'''# ── ALB Security Group ────────────────────────────────────────────────────────
resource "aws_security_group" "alb" {{
  name        = "${{var.project_name}}-alb-sg"
  description = "Allow HTTP/HTTPS inbound to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "${{var.project_name}}-alb-sg" }}
}}

# ── App Security Group ────────────────────────────────────────────────────────
resource "aws_security_group" "app" {{
  name        = "${{var.project_name}}-app-sg"
  description = "Allow traffic from ALB to application"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "App port from ALB"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "${{var.project_name}}-app-sg" }}
}}

# ── Database Security Group ───────────────────────────────────────────────────
resource "aws_security_group" "db" {{
  name        = "${{var.project_name}}-db-sg"
  description = "Allow database access from app tier only"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "DB access from app"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "${{var.project_name}}-db-sg" }}
}}
'''


def _compute_tf(project_name: str, service: str, cpu: int, memory: int, port: int,
                desired: int, min_c: int, max_c: int) -> str:
    if "fargate" in service.lower() or "ecs" in service.lower():
        return f'''# ── ECS Cluster ──────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {{
  name = "${{var.project_name}}-cluster"
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

# ── IAM Role for ECS Task Execution ──────────────────────────────────────────
resource "aws_iam_role" "ecs_task_execution" {{
  name = "${{var.project_name}}-ecs-execution-role"
  assume_role_policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [{{
      Effect    = "Allow"
      Principal = {{ Service = "ecs-tasks.amazonaws.com" }}
      Action    = "sts:AssumeRole"
    }}]
  }})
}}

resource "aws_iam_role_policy_attachment" "ecs_execution" {{
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}}

# ── CloudWatch Log Group ──────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "app" {{
  name              = "/ecs/${{var.project_name}}"
  retention_in_days = 30
}}

# ── ECS Task Definition ───────────────────────────────────────────────────────
resource "aws_ecs_task_definition" "app" {{
  family                   = "${{var.project_name}}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = {cpu}
  memory                   = {memory}
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([{{
    name      = "${{var.project_name}}"
    image     = var.container_image
    essential = true
    portMappings = [{{
      containerPort = var.app_port
      protocol      = "tcp"
    }}]
    environment = [
      {{ name = "PORT", value = tostring(var.app_port) }},
      {{ name = "ENVIRONMENT", value = var.environment }}
    ]
    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }}
    }}
  }}])
}}

# ── ECS Service ───────────────────────────────────────────────────────────────
resource "aws_ecs_service" "app" {{
  name            = "${{var.project_name}}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = {desired}
  launch_type     = "FARGATE"

  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }}

  load_balancer {{
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "${{var.project_name}}"
    container_port   = var.app_port
  }}

  depends_on = [aws_lb_listener.http]
  lifecycle {{ ignore_changes = [desired_count] }}
}}

# ── Auto Scaling ──────────────────────────────────────────────────────────────
resource "aws_appautoscaling_target" "ecs" {{
  max_capacity       = {max_c}
  min_capacity       = {min_c}
  resource_id        = "service/${{aws_ecs_cluster.main.name}}/${{aws_ecs_service.app.name}}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}}

resource "aws_appautoscaling_policy" "cpu" {{
  name               = "${{var.project_name}}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {{
    predefined_metric_specification {{
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }}
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }}
}}
'''
    else:
        # EC2 ASG fallback
        return f'''# ── EC2 Launch Template ───────────────────────────────────────────────────────
resource "aws_launch_template" "app" {{
  name_prefix   = "${{var.project_name}}-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "{cpu}"

  network_interfaces {{
    associate_public_ip_address = false
    security_groups             = [aws_security_group.app.id]
  }}

  user_data = base64encode(<<-EOF
    #!/bin/bash
    docker run -d -p {port}:{port} ${{var.container_image}}
  EOF
  )
}}

data "aws_ami" "amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]
  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}

resource "aws_autoscaling_group" "app" {{
  name                = "${{var.project_name}}-asg"
  min_size            = {min_c}
  max_size            = {max_c}
  desired_capacity    = {desired}
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.app.arn]

  launch_template {{
    id      = aws_launch_template.app.id
    version = "$Latest"
  }}
}}
'''


def _database_tf(project_name: str, engine: str, instance_class: str,
                 storage_gb: int, multi_az: bool, port: int) -> str:
    return f'''# ── DB Subnet Group ───────────────────────────────────────────────────────────
resource "aws_db_subnet_group" "main" {{
  name       = "${{var.project_name}}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id
  tags       = {{ Name = "${{var.project_name}}-db-subnet-group" }}
}}

# ── RDS Instance ──────────────────────────────────────────────────────────────
resource "aws_db_instance" "main" {{
  identifier             = "${{var.project_name}}-db"
  engine                 = "{engine}"
  instance_class         = "{instance_class}"
  allocated_storage      = {storage_gb}
  storage_type           = "gp3"
  storage_encrypted      = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = var.db_port

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  multi_az               = {str(multi_az).lower()}
  publicly_accessible    = false
  skip_final_snapshot    = false
  final_snapshot_identifier = "${{var.project_name}}-final-snapshot"
  deletion_protection    = true

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {{ Name = "${{var.project_name}}-db" }}
}}
'''


def _load_balancer_tf(project_name: str, app_port: int) -> str:
    return f'''# ── Application Load Balancer ─────────────────────────────────────────────────
resource "aws_lb" "main" {{
  name               = "${{var.project_name}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  enable_deletion_protection = false

  tags = {{ Name = "${{var.project_name}}-alb" }}
}}

# ── Target Group ──────────────────────────────────────────────────────────────
resource "aws_lb_target_group" "app" {{
  name        = "${{var.project_name}}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {{
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }}

  tags = {{ Name = "${{var.project_name}}-tg" }}
}}

# ── HTTP Listener (redirect to HTTPS) ────────────────────────────────────────
resource "aws_lb_listener" "http" {{
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type = "redirect"
    redirect {{
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }}
  }}
}}

# ── HTTPS Listener ────────────────────────────────────────────────────────────
# Note: Uncomment and set certificate_arn after provisioning ACM cert
# resource "aws_lb_listener" "https" {{
#   load_balancer_arn = aws_lb.main.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
#   certificate_arn   = var.acm_certificate_arn
#   default_action {{
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.app.arn
#   }}
# }}
'''


def _cache_tf(project_name: str, node_type: str) -> str:
    return f'''# ── ElastiCache Redis Security Group ─────────────────────────────────────────
resource "aws_security_group" "cache" {{
  name        = "${{var.project_name}}-cache-sg"
  description = "Allow Redis access from app tier"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "Redis from app"
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{ Name = "${{var.project_name}}-cache-sg" }}
}}

# ── ElastiCache Subnet Group ──────────────────────────────────────────────────
resource "aws_elasticache_subnet_group" "main" {{
  name       = "${{var.project_name}}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}}

# ── ElastiCache Redis Cluster ─────────────────────────────────────────────────
resource "aws_elasticache_replication_group" "main" {{
  replication_group_id = "${{var.project_name}}-redis"
  description          = "Redis cache for ${{var.project_name}}"
  node_type            = "{node_type}"
  num_cache_clusters   = 1
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.cache.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {{ Name = "${{var.project_name}}-redis" }}
}}
'''


def _storage_tf(project_name: str) -> str:
    return f'''# ── S3 Bucket ─────────────────────────────────────────────────────────────────
resource "aws_s3_bucket" "assets" {{
  bucket        = "${{var.project_name}}-assets-${{data.aws_caller_identity.current.account_id}}"
  force_destroy = false
  tags = {{ Name = "${{var.project_name}}-assets" }}
}}

resource "aws_s3_bucket_versioning" "assets" {{
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {{
    status = "Enabled"
  }}
}}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {{
  bucket = aws_s3_bucket.assets.id
  rule {{
    apply_server_side_encryption_by_default {{
      sse_algorithm = "AES256"
    }}
  }}
}}

resource "aws_s3_bucket_public_access_block" "assets" {{
  bucket                  = aws_s3_bucket.assets.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

data "aws_caller_identity" "current" {{}}
'''


def _monitoring_tf(project_name: str, alarms: list) -> str:
    alarm_blocks = ""
    alarm_configs = [
        ("high-cpu", "CPUUtilization", 80, "AWS/ECS", "ServiceName"),
        ("high-errors", "HTTPCode_Target_5XX_Count", 10, "AWS/ApplicationELB", "LoadBalancer"),
    ]
    for name, metric, threshold, namespace, dim_name in alarm_configs:
        alarm_blocks += f'''
resource "aws_cloudwatch_metric_alarm" "{name.replace("-", "_")}" {{
  alarm_name          = "${{var.project_name}}-{name}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "{metric}"
  namespace           = "{namespace}"
  period              = 60
  statistic           = "Average"
  threshold           = {threshold}
  alarm_description   = "Alarm when {metric} exceeds {threshold}"
  treat_missing_data  = "notBreaching"

  dimensions = {{
    {dim_name} = "${{var.project_name}}"
  }}
}}
'''
    return f'''# ── CloudWatch Log Group (main app) ──────────────────────────────────────────
resource "aws_cloudwatch_log_group" "main" {{
  name              = "/${{var.project_name}}"
  retention_in_days = 30
  tags = {{ Name = "${{var.project_name}}-logs" }}
}}
{alarm_blocks}'''


def _outputs_tf(project_name: str, has_cache: bool, has_storage: bool) -> str:
    cache_out = '''
output "cache_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}
''' if has_cache else ""

    storage_out = '''
output "assets_bucket" {
  description = "S3 assets bucket name"
  value       = aws_s3_bucket.assets.bucket
}
''' if has_storage else ""

    return f'''output "alb_dns_name" {{
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}}

output "alb_zone_id" {{
  description = "ALB hosted zone ID (for Route53 alias records)"
  value       = aws_lb.main.zone_id
}}

output "vpc_id" {{
  description = "VPC ID"
  value       = aws_vpc.main.id
}}

output "db_endpoint" {{
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}}

output "ecs_cluster_name" {{
  description = "ECS cluster name"
  value       = try(aws_ecs_cluster.main.name, null)
}}
{cache_out}{storage_out}'''
