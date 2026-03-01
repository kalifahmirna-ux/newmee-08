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

## What's Been Implemented (2026-03-01)

### Backend
- ✅ Full backend from GitHub repo installed
- ✅ PayDisini service created (`/app/backend/services/paydisini.py`)
- ✅ Midtrans completely removed from user_payments.py, transactions.py, wallet.py
- ✅ Manual payment upload proof with admin approval
- ✅ JWT_SECRET_KEY env var added (was JWT_SECRET mismatch)
- ✅ 15 test questions seeded (5 free, 10 paid)
- ✅ Admin account seeded: admin@newme.com / admin123
- ✅ Settings seeded: paymentAmount=100000, bankName=BCA

### Frontend
- ✅ Full frontend from GitHub repo installed
- ✅ API exports added to App.js (BACKEND_URL, API)
- ✅ PayDisini settings section in admin Settings.jsx
- ✅ Midtrans removed from Shop.jsx
- ✅ Route `/verifikasi-sertifikat` added as alias to `/certificate-verify`
- ✅ Yayasan dashboard with custom price editor
- ✅ Admin dashboard with payments approval

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

## API Credentials
- PayDisini API ID: 3463
- PayDisini API Key: 2f5f4ce34bcecba908f1038e65cb4624
- Admin: admin@newme.com / admin123
- JWT_SECRET_KEY: newme-secret-key-2026

## Prioritized Backlog
### P0 (Critical - Done)
- ✅ Install from GitHub
- ✅ Remove Midtrans
- ✅ Add PayDisini
- ✅ Manual upload payment
- ✅ Admin approval

### P1 (High Priority - Done)
- ✅ Yayasan custom pricing
- ✅ Referral system
- ✅ Free test 1x validation
- ✅ Premium test access after payment
- ✅ Admin analytics

### P2 (Future)
- Certificate PDF template matching exactly to uploaded designs
- Email notification when payment approved
- QR code integration with PayDisini for bank transfers
- Automated test for certificate image generation
- WhatsApp notification bot

## Next Tasks
1. Configure bank account details in admin settings
2. Upload real NEWME logo for certificates
3. Test full user journey end-to-end with real payment
4. Set up PayDisini callback URL after deployment
