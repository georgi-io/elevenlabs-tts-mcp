# Create API Gateway integration with the central ALB using VPC Link
resource "aws_apigatewayv2_integration" "api" {
  # Erstelle die Integration nur, wenn keine Jessica-Service-Integration-ID aus der Infrastruktur bereitgestellt wird
  count          = var.jessica_service_integration_id == "" ? 1 : 0
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

# Link the integration to the route when no jessica_service_integration_id is provided
# Statt die Route zu aktualisieren, nutzen wir ein leeres AWS CLI-Kommando mit null_resource und local-exec
# Dies führt das AWS CLI-Kommando aus, um die Route mit der Integration zu verbinden
resource "null_resource" "update_route_integration" {
  # Nur ausführen, wenn eine route_id angegeben wurde und keine jessica_service_integration_id
  count = var.route_id != "" && var.jessica_service_integration_id == "" ? 1 : 0
  
  triggers = {
    # Trigger, wenn sich die Integration ändert
    integration_id = aws_apigatewayv2_integration.api[0].id
    route_id = var.route_id
  }
  
  # Führt das AWS CLI-Kommando aus, um die Route mit der Integration zu verbinden
  provisioner "local-exec" {
    command = "aws --profile ${var.aws_profile} apigatewayv2 update-route --api-id ${var.api_gateway_id} --route-id ${var.route_id} --target integrations/${aws_apigatewayv2_integration.api[0].id}"
  }
  
  # Führt einen weiteren Befehl aus, um zu überprüfen, ob die Route aktualisiert wurde
  provisioner "local-exec" {
    command = "aws --profile ${var.aws_profile} apigatewayv2 get-route --api-id ${var.api_gateway_id} --route-id ${var.route_id}"
  }
}

# Wenn eine Integration-ID vom Hub bereitgestellt wird, aktualisieren wir diese
# Hinweis: Terraform unterstützt keine direkte Aktualisierung existierender Integrationen,
# daher verwenden wir das AWS CLI über null_resource
resource "null_resource" "update_hub_integration" {
  count = var.jessica_service_integration_id != "" ? 1 : 0
  
  triggers = {
    # Trigger, wenn sich die wichtigen Konfigurationsparameter ändern
    integration_id = var.jessica_service_integration_id
    uri = var.central_alb_https_listener_arn
    vpc_link_id = var.vpc_link_id
    tls_server_name = var.tls_server_name
  }
  
  # Führt das AWS CLI-Kommando aus, um die bestehende Integration zu aktualisieren
  provisioner "local-exec" {
    command = <<EOF
      aws --profile ${var.aws_profile} apigatewayv2 update-integration \
        --api-id ${var.api_gateway_id} \
        --integration-id ${var.jessica_service_integration_id} \
        --integration-type HTTP_PROXY \
        --integration-uri ${var.central_alb_https_listener_arn} \
        --integration-method ANY \
        --connection-type VPC_LINK \
        --connection-id ${var.vpc_link_id} \
        --payload-format-version 1.0 \
        --timeout-in-millis 30000 \
        --tls-config "ServerNameToVerify=${var.tls_server_name}"
    EOF
  }
}