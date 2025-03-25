output "api_integration_id" {
  description = "ID of the API Gateway integration"
  value       = aws_apigatewayv2_integration.api.id
}

output "api_route_id" {
  description = "ID of the API Gateway route"
  value       = aws_apigatewayv2_route.service_route.id
}

output "api_route_key" {
  description = "Route key of the API Gateway route"
  value       = aws_apigatewayv2_route.service_route.route_key
} 