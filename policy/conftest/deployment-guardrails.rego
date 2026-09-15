package main

# Production-readiness guardrails for Kubernetes Deployments.
# Run with: conftest test k8s/base --policy policy/conftest

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.resources.requests
	msg := sprintf("%s/%s: container '%s' is missing resource requests", [input.kind, input.metadata.name, container.name])
}

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.resources.limits
	msg := sprintf("%s/%s: container '%s' is missing resource limits", [input.kind, input.metadata.name, container.name])
}

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.securityContext.runAsNonRoot == true
	msg := sprintf("%s/%s: container '%s' does not set runAsNonRoot: true", [input.kind, input.metadata.name, container.name])
}

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.readinessProbe
	msg := sprintf("%s/%s: container '%s' is missing a readinessProbe", [input.kind, input.metadata.name, container.name])
}

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	not container.livenessProbe
	msg := sprintf("%s/%s: container '%s' is missing a livenessProbe", [input.kind, input.metadata.name, container.name])
}

deny[msg] {
	input.kind == "Deployment"
	container := input.spec.template.spec.containers[_]
	endswith(container.image, ":latest")
	msg := sprintf("%s/%s: container '%s' must not use the ':latest' tag", [input.kind, input.metadata.name, container.name])
}
