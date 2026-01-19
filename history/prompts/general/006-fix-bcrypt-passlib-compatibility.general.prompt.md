---
id: 006
title: Fix bcrypt/passlib Compatibility Issue
stage: green
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: phase1-backend
branch: master
user: asadullahshafique
command: fix
labels: ["backend", "dependencies", "bcrypt", "passlib", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/backend/requirements.txt (pinned bcrypt==4.2.0)
  - src/backend/tests/unit/test_models.py (removed skipif markers)
tests:
  - tests/unit/test_models.py::TestAuthFunctions (6 tests)
---

# Prompt

Fix bcrypt/passlib compatibility issue

# Response

## Summary

Fixed the bcrypt/passlib version compatibility issue that was causing password hashing tests to be skipped.

### Root Cause

`passlib` 1.7.4 relies on `bcrypt.__about__.__version__` to detect the bcrypt version. However, bcrypt 5.0+ removed the `__about__` module entirely, causing import/runtime errors when passlib tries to check bcrypt's version.

### Changes Made

1. **`src/backend/requirements.txt`**
   - Added explicit `bcrypt==4.2.0` pin with comment explaining the compatibility requirement
   - bcrypt 4.x series maintains the `__about__` module that passlib expects

2. **`src/backend/tests/unit/test_models.py`**
   - Removed `@pytest.mark.skipif` decorators from `test_password_hashing`
   - Removed `@pytest.mark.skipif` decorators from `test_password_different_hashes`

### Verification

All authentication tests now pass:

```
tests/unit/test_models.py::TestAuthFunctions::test_password_hashing PASSED
tests/unit/test_models.py::TestAuthFunctions::test_password_different_hashes PASSED
tests/unit/test_models.py::TestAuthFunctions::test_create_access_token PASSED
tests/unit/test_models.py::TestAuthFunctions::test_verify_access_token PASSED
tests/unit/test_models.py::TestAuthFunctions::test_token_expiry PASSED
tests/unit/test_models.py::TestAuthFunctions::test_invalid_token_returns_none PASSED

======================== 6 passed, 25 warnings ========================
```

### Outcome

- Password hashing and verification now works correctly
- Test coverage increased (2 previously skipped tests now run)
- Backend authentication fully functional
