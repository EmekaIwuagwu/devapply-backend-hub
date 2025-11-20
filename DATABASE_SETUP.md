# DevApply Database Setup

## 🎯 Simple Instructions

### Step 1: Access Your Database
Go to **Render Dashboard** → **PostgreSQL** → **Shell** tab

### Step 2: Run the Schema
Copy the **ENTIRE contents** of `FULL_DATABASE_SCHEMA_FIXED.sql` and paste it into the shell.

Press Enter and wait for completion.

### Step 3: Verify Success
You should see:
```
✓ MIGRATION COMPLETE - YOUR DATABASE IS READY!
TOTAL TABLES: 15
```

## ✅ What This Does

- ✅ Creates all 15 tables for DevApply
- ✅ Fixes all column datatypes (JSONB, proper constraints)
- ✅ Adds indexes and triggers  
- ✅ Seeds initial data (LinkedIn, Indeed platforms)
- ✅ Handles both fresh installs AND existing databases

## 🚀 What's Fixed

✅ Skills column is JSONB (not JSON)  
✅ All JSON columns converted to JSONB  
✅ Reserved keyword "current_role" escaped  
✅ Platform credentials columns corrected  
✅ All optional fields are nullable  
✅ System fields have proper defaults  

## 🧪 Test Registration

After database is set up:

```bash
curl -X POST https://devapply-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Expected: ✅ 201 Created with user object and tokens

## 📋 That's It!

**One file. One step. Done.**

---

Need help? Check the comments at the top of `FULL_DATABASE_SCHEMA_FIXED.sql` for details.
