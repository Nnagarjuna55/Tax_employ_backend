# Admin Login Credentials

## Default Admin Credentials

The admin credentials are stored in the `.env` file:

```
ADMIN_EMAIL=admin@.com
ADMIN_PASSWORD=Admin@123
ADMIN_NAME= Administrator
```

## Login Information

- **Email**: `admin@.com`
- **Password**: `Admin@123`
- **Name**:  Administrator

## Automatic Admin Creation

The admin user is automatically created/updated when the server starts if:
1. The `.env` file contains `ADMIN_EMAIL` and `ADMIN_PASSWORD`
2. MongoDB is running and accessible

## Manual Admin Creation

If you need to create the admin user manually, you can:

### Option 1: Use the init script
```bash
cd backend
python init_admin.py
```

### Option 2: Use the create_admin script
```bash
cd backend
python create_admin.py --email admin@.com --password Admin@123 --name " Administrator"
```

## Changing Admin Credentials

1. Update the credentials in `backend/.env`:
   ```
   ADMIN_EMAIL=your_new_email@.com
   ADMIN_PASSWORD=YourNewPassword123
   ADMIN_NAME=Your Name
   ```

2. Restart the server - the admin user will be automatically updated

## Security Notes

⚠️ **Important Security Reminders:**

- Change the default password in production
- Keep the `.env` file secure and never commit it to version control
- Use strong passwords (minimum 8 characters, mix of letters, numbers, and symbols)
- The `.env` file is already in `.gitignore` to prevent accidental commits

## Troubleshooting

If you can't login:

1. Check that MongoDB is running
2. Verify the `.env` file has the correct credentials
3. Check server logs for any errors during admin initialization
4. Run `python init_admin.py` manually to create/update the admin user
