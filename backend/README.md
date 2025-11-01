## Auth Endpoints

### POST /api/register
Body:
{"username":"string","email":"string","password":"string"}
Responses:
- 200: {"message":"User created successfully"}
- 400: {"detail":"Username already taken"} | {"detail":"Email already registered"}

### POST /api/login
Body:
{"username":"string","password":"string"}
Responses:
- 200: {"token":"<JWT_TOKEN>","user":{"id":1,"username":"alice","email":"alice@example.com"}}
- 401: {"detail":"Invalid credentials"}
