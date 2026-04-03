# Admin Registration Guide

## Two Methods to Register Admins

### Method 1: Frontend GUI (Recommended)

1. Navigate to the **Sign Up** page (`signup.html`)
2. Fill in the registration form:
   - **Full name**: Enter the admin's name
   - **Email address**: Enter admin email
   - **Password**: Create a strong password
   - **Confirm password**: Repeat the password
3. **Check the "Register as admin" checkbox** ✓
4. Click **"Create Account"**
5. You'll be logged in automatically and redirected to the home page
6. The admin can now:
   - Click **Admin** link in the header to access the admin dashboard
   - Create places from "Host" menu
   - Edit places from the admin panel

### Method 2: API Direct Call

Send a POST request to register an admin user:

```bash
curl -X POST http://localhost:5000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Admin",
    "email": "admin@example.com",
    "password": "secure_password123",
    "is_admin": true
  }'
```

Response (201 Created):
```json
{
  "id": "uuid-of-user",
  "first_name": "John",
  "last_name": "Admin",
  "email": "admin@example.com",
  "created_at": "2026-04-03T21:10:00.000000",
  "updated_at": "2026-04-03T21:10:00.000000"
}
```

## Admin Capabilities After Registration

Once registed as an admin, users gain access to:

✅ **Admin Dashboard** - View all users, places, and reviews
✅ **Create Places** - Use the Host/Create Place form
✅ **Edit Places** - Edit any place from the admin dashboard
✅ **Full CRUD Operations** - Complete control over places

## Regular User Registration

If the "Register as admin" checkbox is **NOT checked**, the user is registered as a regular user with limited permissions:
- Can view places
- Can write reviews
- Cannot create or edit places
- No access to admin dashboard
