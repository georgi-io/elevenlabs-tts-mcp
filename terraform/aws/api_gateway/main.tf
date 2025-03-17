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
}

# Create API Gateway route for the API endpoint
resource "aws_apigatewayv2_route" "api" {
  api_id    = var.api_gateway_id
  route_key = var.api_gateway_route_key
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# Create API Gateway route for the MCP server endpoint
# Note: Since we're using path-based routing on the ALB, we can use the same integration
resource "aws_apigatewayv2_route" "mcp" {
  api_id    = var.api_gateway_id
  route_key = var.mcp_gateway_route_key
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
} 