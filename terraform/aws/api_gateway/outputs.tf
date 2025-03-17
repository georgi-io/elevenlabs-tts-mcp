output "api_integration_id" {
  description = "ID of the API Gateway integration"
  value       = aws_apigatewayv2_integration.api.id
}

output "api_route_id" {
  description = "ID of the API Gateway route for the API"
  value       = aws_apigatewayv2_route.api.id
}

output "mcp_route_id" {
  description = "ID of the API Gateway route for the MCP server"
  value       = aws_apigatewayv2_route.mcp.id
}

output "api_route_key" {
  description = "Route key of the API Gateway route for the API"
  value       = aws_apigatewayv2_route.api.route_key
}

output "mcp_route_key" {
  description = "Route key of the API Gateway route for the MCP server"
  value       = aws_apigatewayv2_route.mcp.route_key
} 