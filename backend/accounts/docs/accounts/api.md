# Accounts API

## Design Philosophy

- Action-based endpoints (not pure CRUD)
- Thin views
- Strong validation
- Services handle logic

---

## Example Endpoints

### Account Lifecycle

POST /accounts/{id}/activate/
POST /accounts/{id}/suspend/
POST /accounts/{id}/reactivate/

---

### Roles

POST /accounts/{id}/roles/assign/
POST /accounts/{id}/roles/revoke/

---

### Onboarding

POST /accounts/{id}/onboarding/client/complete/
POST /accounts/{id}/onboarding/writer/complete/
POST /accounts/{id}/onboarding/staff/complete/

---

### Self

GET /accounts/me/profile/
GET /accounts/me/summary/
GET /accounts/me/roles/
