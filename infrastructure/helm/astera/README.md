# Astera Runtime Helm chart

The chart expects `ASTERA_AUTH_SECRET` to be supplied by an existing Kubernetes
Secret. It does not create or template secret values.

```bash
helm upgrade --install astera-runtime ./infrastructure/helm/astera \
  --namespace astera --create-namespace \
  --set image.tag="$ASTERA_IMAGE_TAG"
```
