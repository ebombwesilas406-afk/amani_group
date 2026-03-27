# Unit Trust - URL Testing Checklist

Run migrations and start the server, then systematically test each URL.

---

## Prerequisites

```bash
# Apply migrations (required after model changes)
python manage.py migrate

# Create test data
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth import get_user_model
from members.models import PreapprovedMember

User = get_user_model()

# Create a superuser
User.objects.create_superuser(
    phone_number='+254700000000',
    full_name='John Chairman',
    password='testpass123'
)

# Create an Active member
active = User.objects.create_user(
    phone_number='+254700000001',
    full_name='Alice Active',
    password='testpass123'
)
active.role = 'Member'
active.status = 'Active'
active.save()

# Create a Visitor
visitor = User.objects.create_user(
    phone_number='+254700000002',
    full_name='Bob Visitor',
    password='testpass123'
)
visitor.role = 'Member'
visitor.status = 'Visitor'
visitor.save()

# Add to preapproved list for next test
PreapprovedMember.objects.create(
    phone_number='+254700000003',
    full_name='Carol PreApproved'
)

exit()
```

Then start server:
```bash
python manage.py runserver
```

---

## Test Cases

### 1. PUBLIC PAGES (no auth required)

| Test | URL | Expected | Status |
|------|-----|----------|--------|
| Home page | http://127.0.0.1:8000/ | Home template renders | ⬜ |
| About | http://127.0.0.1:8000/about/ | About template renders | ⬜ |
| Contact | http://127.0.0.1:8000/contact/ | Contact template renders | ⬜ |
| Membership info | http://127.0.0.1:8000/membership/ | Membership template renders | ⬜ |
| Rules | http://127.0.0.1:8000/rules/ | Rules template renders | ⬜ |
| Updates | http://127.0.0.1:8000/updates/ | Updates template renders | ⬜ |

### 2. AUTHENTICATION FLOW

| Test | URL | Expected | Status |
|------|-----|----------|--------|
| Register page | http://127.0.0.1:8000/accounts/register/ | Registration form | ⬜ |
| Register new user | POST to above + phone +254700000004, name Test, pwd | Redirect to post-register | ⬜ |
| Post-register page | http://127.0.0.1:8000/accounts/post-register/ | Info page renders | ⬜ |
| Login page | http://127.0.0.1:8000/accounts/login/ | Login form | ⬜ |
| Login as Active member | POST login: +254700000001 / testpass123 | Redirect to /dashboard/ | ⬜ |
| Logout | Click logout in nav | POST to /accounts/logout/, redirect to /accounts/login/ | ⬜ |

### 3. MEMBER DASHBOARD (Active members only, logged in)

| Test | URL | User | Expected | Status |
|------|-----|------|----------|--------|
| Dashboard | http://127.0.0.1:8000/dashboard/ | Active | Dashboard template + profile completion | ⬜ |
| Profile view | http://127.0.0.1:8000/profile/view/ | Active | Profile summary + completion % | ⬜ |
| Edit profile (Active) | http://127.0.0.1:8000/profile/ | Active | Official form renders | ⬜ |
| Edit profile (Visitor) | http://127.0.0.1:8000/profile/ | Visitor | Redirect to /accounts/post-register/ | ⬜ |
| Submit official form | POST to /profile/ | Active | Saves data, redirect to /dashboard/, success message | ⬜ |
| Add beneficiary (JS) | Click "Add beneficiary" button | Active | New beneficiary row appears | ⬜ |
| Remove beneficiary (JS) | Click "Remove" in beneficiary row | Active | Row marked for deletion or removed | ⬜ |

### 4. LEADER DASHBOARD (role-restricted: Chairman/Secretary/Treasurer)

Login as superuser (+254700000000 / testpass123) first.

| Test | URL | Expected | Status |
|------|-----|----------|--------|
| Leader home | http://127.0.0.1:8000/leader/ | Stats (total, active, visitors) | ⬜ |
| Members list | http://127.0.0.1:8000/leader/members/ | Table of all members | ⬜ |
| Add member page | http://127.0.0.1:8000/leader/members/add/ | Form to create user | ⬜ |
| Add member (form) | POST to above | Creates user, redirect to members list | ⬜ |
| Edit member page | http://127.0.0.1:8000/leader/members/1/edit/ | Form pre-filled with user data | ⬜ |
| Edit member (form) | POST to above | Updates user, redirect to members list | ⬜ |

### 5. ACCESS CONTROL TESTS

| Test | URL | User | Expected | Status |
|------|-----|------|----------|--------|
| Dashboard as anonymous | http://127.0.0.1:8000/dashboard/ | None | Redirect to /accounts/login/ | ⬜ |
| Profile as anonymous | http://127.0.0.1:8000/profile/ | None | Redirect to /accounts/login/ | ⬜ |
| Leader as Member | http://127.0.0.1:8000/leader/ | Active (Member role) | 403 Forbidden or redirect | ⬜ |
| Members list as Member | http://127.0.0.1:8000/leader/members/ | Active (Member role) | 403 Forbidden or redirect | ⬜ |

### 6. NAVIGATION LINKS

Log in as Active member and check:

| Link | Expected URL |in nav in nav | Status |
|------|---|---|---|
| Home (logo) | / | ✓ | ⬜ |
| About | /about/ | ✓ | ⬜ |
| Contact | /contact/ | ✓ | ⬜ |
| Rules | /rules/ | ✓ | ⬜ |
| Updates | /updates/ | ✓ | ⬜ |
| User menu dropdown | Not a link, button | ✓ | ⬜ |
| Profile (in dropdown) | /profile/view/ | ✓ | ⬜ |
| Dashboard (in dropdown) | /dashboard/ | ✓ | ⬜ |
| Manage Members (in dropdown - leaders only) | /leader/members/ | ✓ for Chairman | ⬜ |
| Logout (in dropdown) | POST to /accounts/logout/ | ✓ | ⬜ |

---

## Final Checklist

- [ ] All public pages load without 404
- [ ] Registration → Post-register flow works
- [ ] Login → Dashboard redirect works
- [ ] Logout (POST) works
- [ ] Active member can access profile edit
- [ ] Visitor is blocked from profile edit with helpful message
- [ ] Leader can access leader dashboard
- [ ] Non-leader cannot access leader dashboard
- [ ] Dynamic add/remove beneficiaries works silently (no page reload)
- [ ] Official form submission saves to database
- [ ] Profile completion % updates correctly
- [ ] All nav links point to correct URLs
- [ ] No 404 errors in normal flow
- [ ] No 405 (POST/GET mismatch) errors

---

## If Tests Fail

Provide:
1. URL that failed
2. Expected vs actual result
3. HTTP status code (404, 403, 405, 500, etc.)
4. Error message or traceback (if any)
5. User type (anonymous/Active/Visitor/Leader)
