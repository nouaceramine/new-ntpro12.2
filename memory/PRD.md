# NT Commerce 12.0 - PRD

## Original Problem Statement
SaaS multi-tenant commerce platform with AI robots, RBAC permissions, integrations, and PWA support.

## Architecture
```
/app/backend/
├── main.py                # 942 lines (down from 1,163)
├── server.py              # Supervisor entry point
├── models/
│   ├── schemas.py         # Core Pydantic models
│   └── extra_schemas.py   # Extracted from main.py (228 lines)
├── utils/
│   ├── pagination.py      # Shared pagination helper
│   └── password_validator.py  # Password strength rules
├── services/
│   └── cache_service.py   # Redis cache manager
├── robots/                # 11 AI robots
├── routes/                # 64 modular route files
│   └── __init__.py        # Clean (no stale imports)
└── reset_db.py            # Fresh DB initialization

/app/frontend/src/
├── lib/apiClient.js       # Centralized API client
├── components/
│   ├── ErrorBoundary.js   # Global error handling
│   └── Layout.js          # 7-section sidebar (was 17)
└── pages/                 # 80 page components
```

## Completed Work
### P0 - Security ✅
- CORS, Rate limiting (slowapi), JWT secret, Password logging, Admin permissions

### P1 - Performance ✅
- N+1 fix, Pagination (9+ endpoints), Password validation, Redis cache

### P2 - Features ✅
- Repairs, Wallets, Backup (with restore), AI Robots (profit_robot fixed)

### Code Quality Refactor ✅
- Deleted duplicate `auth.py`, Fixed `_id` leaks in AI routes
- Extracted 220 lines models from main.py → `models/extra_schemas.py`
- Cleaned `routes/__init__.py`, Deleted 60 old test files
- Created `apiClient.js`, Added `ErrorBoundary` to App.js
- Fixed `ProductFamilyResponse` optional fields
- Reorganized sidebar from 17 → 7 sections
- Fixed JWT SECRET_KEY across 4 route files
- Fixed `TenantResponse` extra field handling

## Credentials
- **Super Admin**: admin@ntcommerce.com / Admin@2024
- **Tenant**: ncr@ntcommerce.com / Test@123

## Test Results
| Iter | Pass Rate | Notes |
|------|-----------|-------|
| 75 | 17/17 | P0 Security |
| 76 | 28/28 | P1 Performance |
| 77 | 24/24 | P2 Features |
| 78 | 18/18 + FE | Code Quality Refactor |

## Remaining (P3)
- [ ] Multi-tenancy agent hierarchy
- [ ] Docker deployment
- [ ] Data import/export
- [ ] Split large frontend files (Settings 2757 lines, POS 2314 lines)
- [ ] Migrate pages to use centralized apiClient.js

*Updated: 2026-04-12*
