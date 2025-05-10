#Testing User API Endpoints with curl
##Register a new user
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
-H "Content-Type: application/json" \
-d '{"username": "testuser", "email": "test@example.com", "password": "secret"}'
```

##Login to get JWT token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "username=testuser&password=secret"
```

##Get current user info (replace JWT_TOKEN with the actual token)
```bash
curl -X GET "http://127.0.0.1:8000/auth/users/me" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Get list of users (replace JWT_TOKEN with the actual token)
```bash
curl -X GET "http://127.0.0.1:8000/auth/users" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Change password (replace JWT_TOKEN with the actual token)
```bash
curl -X POST "http://127.0.0.1:8000/auth/change-password" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"old_password": "secret", "new_password": "newsecret"}'
```

#Finance Endpoints
##Create Transaction
```bash
curl -X POST "http://127.0.0.1:8000/finance/transactions" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"account_id": 1, "amount": 50.0, "description": "Dinner", "type": "expense", "categories": [{"category_id": 2, "allocated_amount": 50.0}]}'
```

##Create Account
```bash
curl -X POST "http://127.0.0.1:8000/finance/accounts" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"name": "Checking", "balance": 1000.0}'
```

##Get Accounts
```bash
curl -X GET "http://127.0.0.1:8000/finance/accounts" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Create category
```bash
curl -X POST "http://127.0.0.1:8000/finance/categories" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"name": "Groceries", "description": "Food and supplies"}'
```

##Create budget
```bash
curl -X POST "http://127.0.0.1:8000/finance/budgets" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $JWT_TOKEN" \
-d '{"category_id": 3, "period": "2025-05", "limit_amount": 100.0, "start_date": "2025-04-01", "end_date": "2025-12-31"}'
```

##Get categories
```bash
curl -X GET "http://127.0.0.1:8000/finance/categories" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Expense Analysis
```bash
curl -X GET "http://127.0.0.1:8000/finance/analysis/expenses" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Dashboard Summary
```bash
curl -X GET "http://127.0.0.1:8000/finance/dashboard" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Spending Trends
```bash
curl -X GET "http://127.0.0.1:8000/finance/trends/spending" \
-H "Authorization: Bearer $JWT_TOKEN"
```

##Get notifications
```bash
curl -X GET "http://127.0.0.1:8000/finance/notifications" \
-H "Authorization: Bearer $JWT_TOKEN"
```