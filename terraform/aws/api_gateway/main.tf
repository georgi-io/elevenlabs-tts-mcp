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

# Statt zu versuchen, die Route zu erstellen/aktualisieren, erstellen wir einen null_resource,
# der einen AWS CLI-Befehl ausführt, um die Route zu aktualisieren
resource "null_resource" "update_route" {
  triggers = {
    integration_id = aws_apigatewayv2_integration.api.id
  }

  provisioner "local-exec" {
    command = "aws apigatewayv2 update-route --api-id ${var.api_gateway_id} --route-id ${var.route_id} --target integrations/${aws_apigatewayv2_integration.api.id} --profile ${var.aws_profile}"
  }
}

# Die Route wird zentral verwaltet und wird von der zentralen Infrastruktur bereitgestellt 