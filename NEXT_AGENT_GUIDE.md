# SIMG Dashboard - Next Agent Guide: Authentication & Session Management

## 🎯 Current Status

The SIMG Dashboard is **fully functional** with:
- ✅ Working backend API (FastAPI on port 8004)
- ✅ Working frontend UI (Vanilla JS with glassmorphism design)
- ✅ Real web scraping with proper async handling
- ✅ All 15 SIMG Report 1 criteria filters implemented
- ✅ Favorites system
- ✅ File-based JSON database storage

### What Needs to Be Done Next:
**Implement User Authentication & Session Management**

---

## 📋 Authentication Requirements

### 1. JWT-Based Authentication
- Implement JWT token generation and validation
- Create login/logout endpoints
- Add token refresh mechanism
- Secure API routes with authentication middleware

### 2. User Registration & Profile
- User registration endpoint
- Profile management (name, email, preferences)
- Password hashing with bcrypt
- Email verification (optional)

### 3. Protected Endpoints
- Add authentication to favorites CRUD operations
- Protect job application tracking
- Implement user-specific filtering preferences

### 4. Session Management
- Token storage in httpOnly cookies (preferred) or localStorage
- Automatic token refresh
- Session timeout handling
- Logout functionality

### 5. Frontend Integration
- Login/Register pages
- Protected routes
- Session persistence
- Error handling for authentication failures

---

## 🏗️ Recommended Implementation Plan

### Step 1: Install Dependencies
```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

### Step 2: Create User Model
File: `models/user.py`

```python
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserBase(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
```

### Step 3: Create Auth Utility
File: `utils/auth.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.user import Token, TokenData

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Step 4: Create Auth Routes
File: `api/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from api import db_session
from models.user import UserCreate, Token
from utils.auth import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(db_session)):
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db_session)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

@router.get("/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    return current_user
```

### Step 5: Add Authentication Middleware
File: `api/main.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from api import db_session
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### Step 6: Update Existing Endpoints
Add `Depends(get_current_active_user)` to:
- `/api/v1/favorites/` endpoints
- `/api/v1/favorites/{job_id}` endpoints
- Job application tracking

### Step 7: Frontend Integration
Add login modal to `frontend/index.html`:

```javascript
// Login function
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({
                username: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token in httpOnly cookie or localStorage
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            showToast('Login successful!', 'success');
            // Redirect to dashboard
            window.location.href = '/frontend/';
        } else {
            showToast('Login failed: ' + data.detail, 'error');
        }
    } catch (error) {
        showToast('Error logging in', 'error');
    }
}
```

---

## 🧪 Testing Checklist

- [ ] User can register with valid credentials
- [ ] User can login and receive JWT token
- [ ] Protected endpoints reject unauthenticated requests (401)
- [ ] JWT token is validated on each request
- [ ] User can logout and token is invalidated
- [ ] Favorites are user-specific after authentication
- [ ] Session persists across page refreshes
- [ ] Token refresh works when access token expires
- [ ] Rate limiting prevents brute force attacks

---

## 📊 Current Application State

### Server
- **Port**: 8004
- **Framework**: FastAPI
- **Status**: Running
- **Logs**: `/c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log`

### Database
- **Type**: File-based JSON
- **Location**: `data/` directory
- **Files**: `jobs.json`, `favorites.json`, `scraper_configs.json`

### Frontend
- **Type**: Vanilla JavaScript
- **Framework**: None (pure JS)
- **UI**: Tailwind CSS + Glassmorphism
- **State**: localStorage

### Scrapers
- **SEEK**: Implemented with async HTTP
- **LinkedIn**: Implemented with async HTTP
- **Indeed**: Implemented with async HTTP
- **Medical Boards**: Implemented with multiple board support

---

## 🔧 Quick Start

```bash
# Start the server
cd /c/Users/cjarn/VIBE/simg_dashboard
./start.sh

# Access the app
# Frontend: http://localhost:8004/frontend/
# API Docs: http://localhost:8004/docs
# Health Check: http://localhost:8004/api/v1/health
```

---

## 📚 Key Files to Modify

1. `api/auth.py` - Create new file for authentication routes
2. `api/main.py` - Add authentication middleware
3. `models/user.py` - Add User model
4. `utils/auth.py` - Create new file for JWT utilities
5. `frontend/index.html` - Add login modal and session management
6. `requirements.txt` - Add python-jose, passlib, bcrypt

---

## ⚠️ Security Considerations

1. **Never commit SECRET_KEY** - Use environment variables
2. **Use HTTPS in production** - JWT tokens should be transmitted securely
3. **Implement rate limiting** - Prevent brute force attacks
4. **Use httpOnly cookies** - Better than localStorage for tokens
5. **Validate all inputs** - Prevent injection attacks
6. **Sanitize outputs** - Prevent XSS attacks

---

## 🎯 Success Criteria

After implementing authentication:
- User can create account
- User can login/logout
- Favorites are protected and user-specific
- All API routes are secured
- Session persists across refreshes
- No security vulnerabilities

Good luck! 🚀
