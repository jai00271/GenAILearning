# Auth service health

The authentication service exposes `/healthz` and `/readyz`.

If pods are in CrashLoopBackOff:
- check recent configmap changes
- verify Redis session store connectivity
- roll back the last deployment if error rate > 5%

Pager duty severity: SEV-2 when login success rate drops below 95% for 10 minutes.
