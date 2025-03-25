output "api_integration_id" {
  description = "ID of the API Gateway integration (ALB VPC Link)"
  value       = length(aws_apigatewayv2_integration.api) > 0 ? aws_apigatewayv2_integration.api[0].id : var.jessica_service_integration_id
}

# Da die Route nicht mehr über Terraform verwaltet wird, sind diese Outputs nicht mehr verfügbar
# output "api_route_id" {
#   description = "ID of the API Gateway route"
#   value       = aws_apigatewayv2_route.service_route.id
# }

# output "api_route_key" {
#   description = "Route key of the API Gateway route"
#   value       = aws_apigatewayv2_route.service_route.route_key
# } 