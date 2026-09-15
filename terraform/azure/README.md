# Terraform — Azure AKS (demo)

Defines a minimal AKS cluster plus the supporting Azure resources this
project references in its docs (monitoring via Log Analytics, secrets via
Key Vault). Sized small (`Standard_B2s`, 2 nodes) to be cheap to run and free
to `plan`.

## Free tier / cost notes

- New Azure accounts get a free trial credit; AKS itself has **no
  cluster-management fee** — you only pay for the underlying VMs, disks, and
  the Log Analytics workspace.
- `terraform plan` (shown below) requires only an Azure login and costs
  nothing — no resources are created.
- If you do `terraform apply`, remember to `terraform destroy` when you're
  done to avoid ongoing charges.

## Usage

```bash
az login
az account set --subscription "<your-subscription-id>"

terraform init
terraform plan      # free — review what would be created
# terraform apply   # optional, costs money while resources exist
# terraform destroy # tear down when finished
```

No `terraform.tfvars` is required — every variable in `variables.tf` has a
sensible default. Override any of them with `-var` if you want a different
region, node size, or node count.

## What this proves

This maps directly to the "Infrastructure as Code" and "Azure expertise
(AKS, monitoring, networking, security)" parts of the SRE role this project
was built to practice for: an AKS cluster with monitoring wired in via
`oms_agent`/Log Analytics, and a Key Vault for secrets management, all
defined declaratively and reproducible from a clean `terraform apply`.
