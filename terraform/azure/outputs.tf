output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.this.name
}

output "aks_kube_config_command" {
  description = "Run this to fetch cluster credentials with the Azure CLI"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.this.name} --name ${azurerm_kubernetes_cluster.this.name}"
}

output "key_vault_name" {
  value = azurerm_key_vault.this.name
}
