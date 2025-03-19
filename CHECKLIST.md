# Migration zu fastapi-mcp und SSE-Integration Checkliste

## Ausgangssituation und Problemanalyse

- [ ] **Verständnis der aktuellen Architektur**
  - [ ] API Gateway → VPC Link → ALB → ECS/Fargate Services
  - [ ] Aktuelle Routing-Konfiguration für Jessica-Service prüfen
  - [ ] Bestehende WebSocket-Implementierung analysieren

- [ ] **SSE-Problemanalyse**
  - [ ] Dokumentieren, warum API Gateway für SSE problematisch ist (REST API Gateway unterstützt kein natives Streaming oder Chunked Transfer)
  - [ ] Aktuellen Traffic-Flow für Streaming-Verbindungen identifizieren
  - [ ] Potenzielle Timeouts und Verbindungsprobleme erfassen

## Änderungen im zentralen Infrastruktur-Repository

- [ ] **DNS-Konfiguration**
  - [ ] Neuen DNS-Eintrag `mcp.run.georgi.io` in Route53 erstellen
  - [ ] CNAME oder A-Record auf den existierenden ALB einrichten
  - [ ] DNS-Propagation nach Änderung überprüfen

- [ ] **ACM-Zertifikat**
  - [ ] Bestehendes ACM-Zertifikat für `*.georgi.io` überprüfen 
  - [ ] Sicherstellen, dass es `mcp.run.georgi.io` abdeckt oder erweitern
  - [ ] Zertifikat mit dem ALB verknüpfen

- [ ] **Security Groups für ALB**
  - [ ] ALB Security Group anpassen für öffentlichen Zugriff
  - [ ] Spezifische Einschränkung auf Port 443 (HTTPS)
  - [ ] Optional: IP-basierte Einschränkungen hinzufügen
  ```hcl
  resource "aws_security_group_rule" "alb_ingress_sse" {
    security_group_id = "${var.alb_security_group_id}"
    type              = "ingress"
    from_port         = 443
    to_port           = 443
    protocol          = "tcp"
    cidr_blocks       = ["0.0.0.0/0"]
    description       = "Allow HTTPS access from internet for SSE endpoints"
  }
  ```

- [ ] **ALB Listener**
  - [ ] HTTPS-Listener für Host `mcp.run.georgi.io` konfigurieren
  - [ ] Zertifikat dem Listener zuweisen
  - [ ] Default-Action für diesen Host definieren

## Änderungen im Jessica-Repository (lokale Änderungen)

- [ ] **Anpassung der Target Groups**
  - [ ] Bestehende Target Groups überprüfen (`aws_lb_target_group.api` und `aws_lb_target_group.ws`)
  - [ ] Neue Target Group für SSE-Endpunkte erstellen
  ```hcl
  resource "aws_lb_target_group" "sse" {
    name        = "${var.service_name}-sse"
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
  ```

- [ ] **ALB Listener Rules**
  - [ ] Neue Listener Rule für SSE-Endpunkte erstellen
  ```hcl
  resource "aws_lb_listener_rule" "sse_https" {
    listener_arn = var.central_alb_https_listener_arn
    priority     = 90  # Höhere Priorität als die existierenden Regeln
    
    action {
      type             = "forward"
      target_group_arn = aws_lb_target_group.sse.arn
    }
    
    condition {
      path_pattern {
        values = ["/jessica-service/mcp/sse*"]
      }
    }
    
    condition {
      host_header {
        values = ["mcp.run.georgi.io"]
      }
    }
  }
  ```

- [ ] **ECS Service Anpassung**
  - [ ] Load Balancer Konfiguration für die neue Target Group ergänzen
  ```hcl
  load_balancer {
    target_group_arn = aws_lb_target_group.sse.arn
    container_name   = var.service_name
    container_port   = var.container_port
  }
  ```

- [ ] **Code-Migration zu fastapi-mcp**
  - [ ] Codebase von FastMC zu fastapi-mcp migrieren
  - [ ] BASE_PATH aus .env-Umgebungsvariable einlesen
  - [ ] API-Endpoints unter `${BASE_PATH}/api` implementieren
  - [ ] SSE-Endpunkte unter `${BASE_PATH}/mcp/sse` implementieren

- [ ] **FastAPI App-Konfiguration**
  - [ ] Dynamische BASE_PATH-Konfiguration in FastAPI-Anwendung einrichten
  ```python
  # .env-Datei:
  # BASE_PATH=/jessica-service
  
  import os
  from dotenv import load_dotenv
  
  load_dotenv()
  
  base_path = os.getenv("BASE_PATH", "")
  
  app = FastAPI(
      title="Jessica MCP API",
      description="Jessica MCP API with SSE support",
      root_path=base_path  # Aus .env-Umgebungsvariable
  )
  
  # API-Endpoints unter /api
  api_router = APIRouter(prefix="/api")
  
  # MCP-Endpoints unter /mcp
  mcp_router = APIRouter(prefix="/mcp")
  
  # SSE-Endpoint unter /mcp/sse
  @mcp_router.get("/sse/stream")
  async def stream_events():
      async def event_generator():
          # SSE-Implementation
          yield "data: Event message\n\n"
          
      return StreamingResponse(
          event_generator(),
          media_type="text/event-stream",
          headers={
              "Cache-Control": "no-cache",
              "Connection": "keep-alive",
          }
      )
  
  # Router registrieren
  app.include_router(api_router)
  app.include_router(mcp_router)
  ```

- [ ] **SSE-Implementierung**
  - [ ] Server-Sent Events Endpunkte unter `/mcp/sse` implementieren
  - [ ] Korrekte Content-Type Header und Formatierung
  ```python
  # Bereits im mcp_router enthalten
  @mcp_router.get("/sse/stream")
  async def stream_events():
      async def event_generator():
          # SSE-Implementation
          yield "data: Event message\n\n"
          
      return StreamingResponse(
          event_generator(),
          media_type="text/event-stream",
          headers={
              "Cache-Control": "no-cache",
              "Connection": "keep-alive",
          }
      )
  ```

## Testing und Validierung

- [ ] **Lokales Testing der FastAPI-App**
  - [ ] Verschiedene BASE_PATH-Werte in .env testen
  - [ ] SSE-Endpunkte mit curl/Postman testen
  ```bash
  # Mit BASE_PATH=/jessica-service in .env
  curl -N http://localhost:8000/jessica-service/mcp/sse/stream
  
  # Mit BASE_PATH=/test in .env
  curl -N http://localhost:8000/test/mcp/sse/stream
  ```

- [ ] **Infrastruktur-Testing**
  - [ ] API Gateway-Zugriff für reguläre Endpunkte testen
  - [ ] Direkter ALB-Zugriff für SSE-Endpunkte testen
  ```bash
  # Regulärer API Gateway Zugriff (API-Endpoints)
  curl https://api.georgi.io/jessica-service/api/v1/endpoint
  
  # Direkter Zugriff auf SSE über neuen DNS-Namen
  curl -N https://mcp.run.georgi.io/jessica-service/mcp/sse/stream
  ```

- [ ] **End-to-End Validierung**
  - [ ] Frontend-Integration mit SSE-Endpunkten
  - [ ] Verbindungsstabilität und Timeout-Verhalten überprüfen
  - [ ] Last- und Performance-Tests

## Dokumentation und Monitoring

- [ ] **Infrastruktur-Dokumentation aktualisieren**
  - [ ] README-INFRASTRUCTURE.md ergänzen
  - [ ] Architekturdiagramme aktualisieren
  - [ ] Terraform-Module dokumentieren

- [ ] **Monitoring und Alerting**
  - [ ] CloudWatch-Alarme für neue Endpunkte einrichten
  - [ ] SSE-Verbindungsabbrüche überwachen
  - [ ] Dashboard für SSE-Performance erstellen

## Rollback-Plan

- [ ] **Rollback-Strategie dokumentieren**
  - [ ] Bedingungen für Rollback definieren
  - [ ] Schritte zum Zurücksetzen der Infrastruktur
  - [ ] Client-seitige Fallback-Mechanismen

## Ressourcen und Referenzen

- [AWS API Gateway Limitations](https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html)
- [FastAPI SSE Implementation](https://github.com/sysid/sse-starlette)
- [AWS ALB Path-Based Routing](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html#path-conditions)
- [FastAPI root_path Configuration](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
- [AWS ALB Host-Based Routing](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html#host-conditions)
- [Server-Sent Events MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) 