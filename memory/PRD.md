# NEWME CLASS - Platform Tes Bakat & Potensi

## Problem Statement
Install repository https://github.com/dwipuspaanggita-sketch/newme07 ke environment lokal dengan fitur-fitur berikut:
- Payment manual upload & admin approval
- Free test (1x only)
- Premium test (after payment approval)
- Show premium results in user dashboard and admin dashboard
- Admin dashboard real-time analytics
- All image uploads (no URL input)
- Test flow & validation
- Referral system
- Custom pricing yayasan (only via yayasan referral link)
- Yayasan dashboard view
- Delete all Midtrans integration
- Replace with PayDisini production (API ID: 3463, API Key: 2f5f4ce34bcecba908f1038e65cb4624)
- Language: Bahasa Indonesia

## Architecture

### Backend (FastAPI + MongoDB)
- `/app/backend/server.py` - Main FastAPI app
- `/app/backend/routes/` - All API routes
- `/app/backend/services/paydisini.py` - PayDisini integration service
- `/app/backend/certificate_generator.py` - Certificate PDF generator
- `/app/backend/personality_data.py` - 5-element personality data

### Frontend (React + TailwindCSS)
- `/app/frontend/src/App.js` - Route configuration
- `/app/frontend/src/pages/` - All pages
- `/app/frontend/src/pages/admin/` - Admin dashboard pages
- `/app/frontend/src/pages/yayasan/` - Yayasan dashboard pages
- `/app/frontend/src/services/api.js` - API service layer

## User Personas
1. **User** - Takes free test (1x) or premium test after payment
2. **Admin** - Manages payments, users, questions, certificates, analytics
3. **Yayasan** - Organization with custom referral link and pricing

## Core Requirements (Static)
- Free test: 1x per user (isFree=true questions)
- Premium test: Requires payment approval
- Price default: Rp 100.000 (editable in admin)
- Yayasan custom price: Rp 100.000 (editable in yayasan dashboard)
- No Midtrans - Manual upload proof + admin approval
- PayDisini production API ID: 3463

## What's Been Implemented

### Backend
- Full backend from GitHub repo installed
- PayDisini service created (`/app/backend/services/paydisini.py`)
- Midtrans completely removed from user_payments.py, transactions.py, wallet.py
- Manual payment upload proof with admin approval
- JWT_SECRET_KEY env var properly configured
- 15 test questions seeded (5 free, 10 paid)
- Admin account seeded: admin@newme.com / admin123
- Settings seeded: paymentAmount=100000, bankName=BCA
- **Yayasan commission credit** - 10% commission on referral payments

### Frontend
- Full frontend from GitHub repo installed
- API exports added to App.js (BACKEND_URL, API)
- PayDisini settings section in admin Settings.jsx
- Midtrans removed from Shop.jsx
- Route `/verifikasi-sertifikat` added as alias to `/certificate-verify`
- Yayasan dashboard with custom price editor
- Admin dashboard with payments approval
- **Share buttons** (WA/FB/IG) added to TestResult.jsx
- **Teaser blur** for free test results to encourage upgrade

### Payment Flow
1. User registers → takes free test (1x)
2. User uploads payment proof image → Admin approves
3. After approval → user accesses premium test
4. Premium test result → certificate generated

### Yayasan Flow
1. Yayasan registers at /yayasan/register
2. Gets referral link: `/register?ref=CODE`
3. Users who register with code get yayasan's custom price
4. Yayasan dashboard shows: referral stats, users, custom price editor
5. **NEW**: Yayasan wallet with commission tracking (10% of referral payments)
6. **NEW**: Yayasan can request withdrawals (min Rp 50.000)
7. **NEW**: Admin can approve/reject withdrawals at /admin/withdrawals

## API Credentials
- PayDisini API ID: 3463
- PayDisini API Key: 2f5f4ce34bcecba908f1038e65cb4624
- Admin: admin@newme.com / admin123
- JWT_SECRET_KEY: newme-secret-key-2026

## Prioritized Backlog

### P0 (Critical - Done)
- Install from GitHub
- Remove Midtrans
- Add PayDisini
- Manual upload payment
- Admin approval
- Yayasan registration & login
- Yayasan dashboard (Dashboard, Pengguna, Hasil Test, Wallet, Pengaturan)
- Yayasan commission credit system
- Yayasan withdrawal request
- Admin withdrawal approval
- Share to WA/FB/IG for test results
- Free test teaser with blur effect

### P1 (High Priority - Done)
- Yayasan custom pricing
- Referral system
- Free test 1x validation
- Premium test access after payment
- Admin analytics
- Admin yayasan management

### P2 (Future)
- Certificate PDF template matching exactly to uploaded designs
- Email notification when payment approved
- Automated test for certificate image generation
- WhatsApp notification bot
- Content management for all website text/images

## Key Features Summary

### Yayasan (Foundation) Features
| Feature | Status | Location |
|---------|--------|----------|
| Registration | Done | /yayasan/register |
| Login | Done | /yayasan/login |
| Dashboard Stats | Done | /yayasan/dashboard |
| View Referral Users | Done | Tab Pengguna |
| View Test Results | Done | Tab Hasil Test |
| Wallet Balance | Done | Tab Wallet |
| Withdrawal Request | Done | Tab Wallet |
| Custom Price Editor | Done | Tab Pengaturan |
| Commission Credit | Done | 10% auto-credited |

### Admin Features for Yayasan
| Feature | Status | Location |
|---------|--------|----------|
| List All Yayasan | Done | /admin/yayasan |
| Verify Yayasan | Done | /admin/yayasan |
| Toggle Active Status | Done | /admin/yayasan |
| View Withdrawals | Done | /admin/withdrawals |
| Approve/Reject Withdrawal | Done | /admin/withdrawals |

### TestResult Enhancements
| Feature | Status | Description |
|---------|--------|-------------|
| Share to WhatsApp | Done | Opens WA with pre-filled text |
| Share to Facebook | Done | Opens FB share dialog |
| Share to Instagram | Done | Copies text to clipboard for IG |
| Free Test Teaser | Done | Blur effect on Karakter, Kekuatan Jatidiri, Kompilasi Adaptasi |
| Upgrade CTA | Done | Prominent upgrade button for free test results |

## Test Results (2026-03-02)
- Backend: 100% (20/20 tests)
- Frontend: 100% - All features working
- Test file: /app/test_reports/iteration_2.json

## Next Tasks
1. Configure bank account details in admin settings
2. Upload real NEWME logo for certificates
3. Test full user journey end-to-end with real payment
4. Set up PayDisini callback URL after deployment
