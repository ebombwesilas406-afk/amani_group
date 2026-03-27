# Django Unit Trust - URL Routing Map

## Project Root (unit_trust/urls.py)
```
admin/               → Django admin
accounts/            → accounts app
(root paths)         → members app + core app
```

---

## Accounts App URLs (accounts/urls.py)
| URL | Name | View | Purpose |
|-----|------|------|---------|
| `accounts/register/` | `accounts:register` | register() | User registration |
| `accounts/post-register/` | `accounts:post_register` | post_register() | Post-reg info page |
| `accounts/login/` | `accounts:login` | LoginView | User login |
| `accounts/logout/` | `accounts:logout` | LogoutView (POST) | User logout |

---

## Members App URLs (members/urls.py)
| URL | Name | View | Auth | Role |
|-----|------|------|------|------|
| `dashboard/` | `members:dashboard` | dashboard() | Login required | Any |
| `profile/view/` | `members:profile_view` | profile_view() | Login required | Any |
| `profile/` | `members:profile_edit` | profile_edit() | Login required + Active | Any Active |
| `members/` | `members:members_list` | members_list() | Login + Role | Chairman/Secretary/Treasurer |
| `payments/verify/<id>/` | `members:verify_payment` | verify_payment() | Login + Role | Chairman/Secretary/Treasurer |
| `leader/` | `members:leader_home` | leader_home() | Login + Role | Chairman/Secretary/Treasurer |
| `leader/members/` | `members:leader_members` | members_list() | Login + Role | Chairman/Secretary/Treasurer |
| `leader/members/add/` | `members:leader_add_member` | add_member() | Login + Role | Chairman/Secretary/Treasurer |
| `leader/members/<id>/edit/` | `members:leader_edit_member` | edit_member() | Login + Role | Chairman/Secretary/Treasurer |

---

## Core App URLs (core/urls.py)
| URL | Name | View | Auth |
|-----|------|------|------|
| `` (root) | `home` | home view | None |
| `about/` | `about` | about view | None |
| `contact/` | `contact` | contact view | None |
| `membership/` | `membership` | membership view | None |
| `operations/` (or support) | varies | support view | None |
| `rules/` | `rules` | rules view | None |
| `updates/` | `updates` | updates view | None |

---

## Important Notes

### Actual URL Paths (relative to 127.0.0.1:8000/)

**Public Pages:**
- `http://127.0.0.1:8000/` → Home
- `http://127.0.0.1:8000/about/` → About
- `http://127.0.0.1:8000/contact/` → Contact
- `http://127.0.0.1:8000/membership/` → Membership info
- `http://127.0.0.1:8000/rules/` → Rules
- `http://127.0.0.1:8000/updates/` → Updates

**Authentication:**
- `http://127.0.0.1:8000/accounts/register/` → Register
- `http://127.0.0.1:8000/accounts/login/` → Login
- `http://127.0.0.1:8000/accounts/logout/` → Logout (POST)
- `http://127.0.0.1:8000/accounts/post-register/` → Post-registration info

**Member Dashboard:**
- `http://127.0.0.1:8000/dashboard/` → Dashboard (login required)
- `http://127.0.0.1:8000/profile/view/` → View profile (login required)
- `http://127.0.0.1:8000/profile/` → Edit/complete official form (Active members only)

**Leader Dashboard:**
- `http://127.0.0.1:8000/leader/` → Leader home (role-restricted)
- `http://127.0.0.1:8000/leader/members/` → Members list (role-restricted)
- `http://127.0.0.1:8000/leader/members/add/` → Add member (role-restricted)
- `http://127.0.0.1:8000/leader/members/<id>/edit/` → Edit member (role-restricted)

---

## Auth Flow

1. Anonymous → `/accounts/register/` (or login)
2. Register → `/accounts/post-register/` (+ redirects login)
3. Login → `LOGIN_REDIRECT_URL` = `/dashboard/`
4. Dashboard → Choose action (profile, form, etc.)
5. Active member → `/profile/` to complete form
6. Visitor → Shows "payment required" banner, links to `/accounts/post-register/`
7. Leader → Access `/leader/` and manage members

---

## Issue in unit_trust/urls.py

Line: `path('admin/dashboard/', admin.site.urls),`

**PROBLEM:** This maps `admin/dashboard/` to Django admin (not our leader dashboard).
**FIX:** Should be removed or changed to redirect to `members:leader_home`.

