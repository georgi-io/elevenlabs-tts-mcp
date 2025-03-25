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

# Link the integration to the route
# Statt die Route zu aktualisieren, nutzen wir ein leeres AWS CLI-Kommando mit null_resource und local-exec
# Dies führt das AWS CLI-Kommando aus, um die Route mit der Integration zu verbinden
resource "null_resource" "update_route_integration" {
  # Nur ausführen, wenn eine route_id angegeben wurde
  count = var.route_id != "" ? 1 : 0
  
  triggers = {
    # Trigger, wenn sich die Integration ändert
    integration_id = aws_apigatewayv2_integration.api.id
    route_id = var.route_id
  }
  
  # Führt das AWS CLI-Kommando aus, um die Route mit der Integration zu verbinden
  provisioner "local-exec" {
    command = "aws --profile ${var.aws_profile} apigatewayv2 update-route --api-id ${var.api_gateway_id} --route-id ${var.route_id} --target integrations/${aws_apigatewayv2_integration.api.id}"
  }
  
  # Führt einen weiteren Befehl aus, um zu überprüfen, ob die Route aktualisiert wurde
  provisioner "local-exec" {
    command = "aws --profile ${var.aws_profile} apigatewayv2 get-route --api-id ${var.api_gateway_id} --route-id ${var.route_id}"
  }
}