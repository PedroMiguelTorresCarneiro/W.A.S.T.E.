# AUTH SERVICE (FIREBASE)


# ENDPOINTS

| method | endpoint | Description |
|--------|----------|-------------|
| `POST` | */auth/register* | Creates a new account using email/password and adds role (admin | user) |
| `POST` | */auth/login* | logs into an account using email/password |
| `POST` | */auth/oauth* | generates a OAuth link to Google/Facebook and returns do PWA |
| `GET` | */auth/callback* | Receives the Firebase autenticated user and generates a JWT token |


### `POST` /auth/register

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "role": "admin"
}
````

### `POST` /auth/login 

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}

````

### `POST` /auth/oauth

- SEND:
```json
{
  "provider": "google"
}
````
- RETURNS
```json
{
  "oauth_url": "https://accounts.google.com/o/oauth2/auth?...redirect_uri=http://localhost:5002/auth/callback"
}
```

### `GET` /auth/callback

Receives the token from the redirect on the `POST` */auth/oauth*
and returns the role and the token(maye)