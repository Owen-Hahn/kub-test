terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.0"
    }
  }
}
provider "kubernetes" {
  config_path = "~/.kube/config"
}
resource "kubernetes_namespace" "kub-server" {
  metadata {
    name = "minikube"
  }
}
resource "kubernetes_deployment" "kub-server" {
  metadata {
    name      = "kub-server"
    namespace = kubernetes_namespace.kub-server.metadata.0.name
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "KubServerTest"
      }
    }
    template {
      metadata {
        labels = {
          app = "KubServerTest"
        }
      }
      spec {
        container {
          image = "docker.io/orhahn/kub-server"
          name  = "kub-sever-container"
          port {
            container_port = 8080
          }
          env {
            name = "DB_HOST"
            value = "kub-db"
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "kub-server" {
  metadata {
    name      = "kub-server"
    namespace = kubernetes_namespace.kub-server.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.kub-server.spec.0.template.0.metadata.0.labels.app
    }
    type = "NodePort"
    port {
      node_port   = 32123 
      port        = 80
      target_port = 8080
    }
  }
}

resource "kubernetes_deployment" "kub-db" {
  metadata {
    name      = "kub-db"
    namespace = kubernetes_namespace.kub-server.metadata.0.name
  }
  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "KubDBTest"
      }
    }
    template {
      metadata {
        labels = {
          app = "KubDBTest"
        }
      }
      spec {
        container {
          image = "docker.io/orhahn/kub-db"
          name  = "kub-db-container"
          port {
            container_port = 5432 
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "kub-db" {
  metadata {
    name      = "kub-db"
    namespace = kubernetes_namespace.kub-server.metadata.0.name
  }
  spec {
    selector = {
      app = kubernetes_deployment.kub-db.spec.0.template.0.metadata.0.labels.app
    }
    type = "NodePort"
    port {
      port        = 5432
      target_port = 5432
    }
  }
}
