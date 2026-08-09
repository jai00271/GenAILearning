# Runbook: Auth service CrashLoopBackOff

**doc_id:** runbook-auth-crashloop  
**service:** auth  
**updated_at:** 2026-08-01

## Symptoms

- Pod restarts with `CrashLoopBackOff` on `auth-api`.
- Readiness probe failing; login 401/503 spikes.

## Triage

1. `kubectl describe pod -n identity -l app=auth-api` — check Last State reason.
2. Confirm recent config/secret rollout in the last 2 hours.
3. If `OOMKilled`, raise memory limit 25% and verify leak before permanent bump.
4. If `CreateContainerConfigError`, restore secret `auth-oidc` from last known good.

## Next safe steps

- Page identity on-call only after confirming blast radius > single pod.
- Do **not** delete PVCs.
- Rollback Deployment `auth-api` to previous ReplicaSet if error rate > 5% for 10 minutes.

## Related

- Ticket patterns: password-reset storms often co-occur with IdP outages.
- Alerts: `auth-api 5xx` on the HTML alert page fixture.
