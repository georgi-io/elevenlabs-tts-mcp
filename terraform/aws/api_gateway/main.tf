# Create API Gateway integration with the central ALB using VPC Link
resource "aws_apigatewayv2_integration" "api" {
  api_id           = var.api_gateway_id
  integration_type = "HTTP_PROXY"
  integration_uri  = var.central_alb_https_listener_arn
  
  integration_method = "ANY"
  connection_type    = "VPC_LINK"
  connection_id      = var.vpc_link_id
  
  payload_format_version = "1.0"
  timeout_milliseconds   = 30000
  
  # TLS-Konfiguration für VPC-Link Integration zum ALB
  tls_config {
    server_name_to_verify = var.tls_server_name
  }
}

# Statt mit CLI-Befehl erstellen wir die Route direkt über Terraform
resource "aws_apigatewayv2_route" "service_route" {
  api_id    = var.api_gateway_id
  route_key = "ANY /${var.service_name}/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# Die Route wird zentral verwaltet und wird von der zentralen Infrastruktur bereitgestellt 