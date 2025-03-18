output "api_integration_id" {
  description = "ID of the API Gateway integration"
  value       = aws_apigatewayv2_integration.api.id
} 