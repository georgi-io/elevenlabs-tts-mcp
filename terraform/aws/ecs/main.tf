# Create CloudWatch Log Group for the ECS Service
resource "aws_cloudwatch_log_group" "service" {
  name              = "/ecs/${var.service_name}"
  retention_in_days = var.log_retention_days
}

# Create Security Group for the ECS Service
resource "aws_security_group" "service" {
  name        = "${var.service_name}-ecs-service"
  description = "Security group for ${var.service_name} ECS service"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    description     = "Allow traffic from NLB to API port"
    cidr_blocks     = ["0.0.0.0/0"] # NLB is transparent, so traffic appears to come directly from clients
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name = "${var.service_name}-ecs-service"
  }
}

# Create Target Groups for the central ALB
resource "aws_lb_target_group" "api" {
  name        = "${var.service_name}-api"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    protocol            = "HTTP"
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# Create WebSocket target group
resource "aws_lb_target_group" "ws" {
  name        = "${var.service_name}-ws"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    protocol            = "HTTP"
    path                = "/health"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }
}

# Create path-based routing rules on the ALB for HTTPS
resource "aws_lb_listener_rule" "api_https" {
  listener_arn = var.central_alb_https_listener_arn
  priority     = 100 # Choose a unique priority

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  # Exclude /jessica-service/sse* and /jessica-service/ws* paths, handle all other /jessica-service/ paths
  condition {
    path_pattern {
      values = ["/jessica-service/*"]
    }
  }
}

resource "aws_lb_listener_rule" "ws_https" {
  listener_arn = var.central_alb_https_listener_arn
  priority     = 91 # Higher priority (lower number) than the API rule but lower than MCP

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ws.arn
  }

  condition {
    path_pattern {
      values = ["/jessica-service/ws*"]
    }
  }
}

# Create IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution" {
  name = "${var.service_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Attach the ECS Task Execution Role policy
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create IAM Role for the ECS Task
resource "aws_iam_role" "ecs_task" {
  name = "${var.service_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Create ECS Task Definition for Fargate
resource "aws_ecs_task_definition" "service" {
  family                   = var.service_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = var.service_name
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      environment = [
        for name, value in var.environment_variables : {
          name  = name
          value = value
        }
      ]
      secrets = [
        for name, valueFrom in var.secrets : {
          name      = name
          valueFrom = valueFrom
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.service.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = var.service_name
        }
      }
    }
  ])
}

# Get current AWS region
data "aws_region" "current" {}

# Create ECS Service
resource "aws_ecs_service" "service" {
  name            = var.service_name
  cluster         = var.ecs_cluster_arn
  task_definition = aws_ecs_task_definition.service.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.service.id]
    assign_public_ip = false
  }

  # Load balancer configuration for API
  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  # Load balancer configuration for WebSocket
  load_balancer {
    target_group_arn = aws_lb_target_group.ws.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }

  # Additional service configuration...

  # Don't allow desired count to block updates
  lifecycle {
    ignore_changes = [desired_count]
  }
}

# Create App Autoscaling Target (required for scheduled scaling)
resource "aws_appautoscaling_target" "service" {
  count              = var.enable_scheduled_scaling ? 1 : 0
  max_capacity       = 1
  min_capacity       = 0
  resource_id        = "service/${var.ecs_cluster_name}/${aws_ecs_service.service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Create scheduled scaling rule to scale up in the morning
resource "aws_appautoscaling_scheduled_action" "scale_up" {
  count              = var.enable_scheduled_scaling ? 1 : 0
  name               = "${var.service_name}-scale-up"
  service_namespace  = aws_appautoscaling_target.service[0].service_namespace
  resource_id        = aws_appautoscaling_target.service[0].resource_id
  scalable_dimension = aws_appautoscaling_target.service[0].scalable_dimension
  schedule           = var.scale_up_cron

  scalable_target_action {
    min_capacity = 1
    max_capacity = 1
  }
}

# Create scheduled scaling rule to scale down in the evening
resource "aws_appautoscaling_scheduled_action" "scale_down" {
  count              = var.enable_scheduled_scaling ? 1 : 0
  name               = "${var.service_name}-scale-down"
  service_namespace  = aws_appautoscaling_target.service[0].service_namespace
  resource_id        = aws_appautoscaling_target.service[0].resource_id
  scalable_dimension = aws_appautoscaling_target.service[0].scalable_dimension
  schedule           = var.scale_down_cron

  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
} 