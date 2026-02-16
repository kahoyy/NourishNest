# NourishNest - Smart Kitchen Assistant

NourishNest is a full-stack web application that helps users manage their kitchen inventory, generate personalized recipes based on available ingredients, track meals, and earn rewards for healthy cooking habits.

## 🌟 Features

### Core Features

- **Pantry Management**: Add, organize, and track pantry items with expiration dates
- **Recipe Generation**: Automatically generate recipes based on available ingredients and dietary preferences
- **Meal Tracking**: Log meals you've cooked with ratings and track nutrition
- **Rewards System**: Earn points and badges for consistent cooking and meal logging
- **Community Recipes**: Share and explore recipes from the community
- **Safe-Filter**: Allergen and dietary restriction checking to ensure recipe safety
- **Daily Rate Limiting**: Control recipe generation with subscription-based tier limits (Free: 5/day, Premium: 50/day, Pro: 100/day)

### User Profiles

- Health profile management (age, weight, height, activity level)
- Dietary restrictions and allergy tracking
- Subscription tier management
- Streaks and achievement tracking

## 📋 Project Structure

```
Project/
├── Backend/                      # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── recipes/                  # Recipe generation & management
│   ├── users/                    # User profiles & authentication
│   ├── inventory/                # Pantry item management
│   ├── community/                # Community recipes
│   ├── paypal_integration/       # Payment processing
│   └── API_DOCS.md              # Detailed API documentation
│
├── Frontend/                     # React + Vite SPA
│   ├── src/
│   │   ├── pages/               # Page components
│   │   ├── components/          # Reusable components
│   │   ├── api.js               # API integration with JWT auth
│   │   ├── App.jsx              # Main app router
│   │   └── index.css            # Tailwind styles
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
│
└── README.md                     # This file
```

## 🛠️ Technology Stack

### Backend

- **Framework**: Django 5.2.11 + Django REST Framework
- **Database**: PostgreSQL (via psycopg)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Recipe Generation**: OpenRouter API (LLM integration)
- **Payments**: PayPal SDK (paypalrestsdk 1.13.3)
- **HTTP Client**: httpx (for async API calls)

### Frontend

- **Framework**: React 19+ with React Router
- **Build Tool**: Vite 5.0+
- **Styling**: Tailwind CSS 4.1.18
- **HTTP Client**: axios with JWT interceptors
- **State**: React hooks (useState, useEffect)

### Infrastructure

- **Development**: Windows 10, Python 3.13, Node.js (npm)
- **Dev Server**: Django (port 8000) + Vite (port 5173)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (npm)
- PostgreSQL 12+ (or SQLite for development)

### Backend Setup

1. **Install dependencies**:

   ```bash
   cd Backend
   python -m pip install -r requirements.txt
   ```

2. **Configure environment** (create `.env` in Backend/):

   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/nourishnest
   OPENROUTER_API_KEY=your-openrouter-key
   PAYPAL_MODE=sandbox
   PAYPAL_CLIENT_ID=your-paypal-client-id
   PAYPAL_CLIENT_SECRET=your-paypal-secret
   ```

3. **Run migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Load fixtures** (optional demo data):

   ```bash
   python manage.py loaddata users/fixtures/subscription_plans.json
   python manage.py loaddata inventory/fixtures/dietary_tags.json
   ```

5. **Create demo user** (optional):

   ```bash
   python manage.py seed_nourishnest
   # Demo login: demo@nourishnest.local / Password123!
   ```

6. **Start backend server**:
   ```bash
   python manage.py runserver
   ```
   Backend runs on `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**:

   ```bash
   cd Frontend
   npm install
   ```

2. **Start development server**:

   ```bash
   npm run dev
   ```

   Frontend runs on `http://localhost:5173`

3. **Build for production**:
   ```bash
   npm run build
   ```

## 📱 How to Use

### 1. Register & Login

- Visit `http://localhost:5173`
- Create a new account or use demo credentials
- JWT tokens are stored in localStorage for session management

### 2. Add Pantry Items

- Navigate to **Inventory**
- Click **+ Add Item** to add ingredients
- Mark items as perishable and set expiry dates
- Non-perishable items can be added without dates

### 3. Generate Recipes

- Go to **Generate** page
- Select ingredients from your inventory
- Choose dietary filters (vegan, gluten-free, etc.)
- Click **Generate Recipe**
- Recipes are created by analyzing your ingredients and preferences

### 4. Log Meals

- View a recipe and click **✓ Log This Meal**
- Rate the meal (1-5 stars)
- Add notes about improvements
- Earn points and badges instantly

### 5. Track Progress

- Visit **Rewards** page to see:
  - Total points earned
  - Current cooking streak
  - Badges achieved
  - Recent meal history

### 6. Customize Recipes

- Click **🔀 Fork & Customize** on any recipe
- Create your own version with modifications
- Your forked recipe is saved independently

## 🔐 Authentication Flow

1. **Register**: POST `/api/v1/auth/register/` → returns `access_token`, `refresh_token`, `user`
2. **Login**: POST `/api/v1/token/` → returns tokens
3. **API Calls**: Include `Authorization: Bearer <access_token>` header
4. **Auto-Refresh**: When token expires, API automatically fetches new one using `refresh_token`
5. **Logout**: Clear localStorage (tokens & user data)

## 📊 API Endpoints

### Authentication

- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/token/` - Login
- `POST /api/v1/token/refresh/` - Refresh access token

### Recipes

- `POST /api/v1/recipes/generate/` - Generate recipe from ingredients
- `GET /api/v1/recipes/` - List user's recipes
- `GET /api/v1/recipes/{id}/` - Recipe details
- `POST /api/v1/recipes/{id}/fork/` - Create custom version
- `POST /api/v1/recipes/{id}/log-meal/` - Log meal & earn rewards
- `GET /api/v1/recipes/history/` - Meal history

### Users

- `GET/PATCH /api/v1/users/profile/` - User base profile
- `GET /api/v1/users/rewards/` - Rewards & badges

### Inventory

- `GET/POST /api/v1/inventory/` - List/create items
- `PATCH/DELETE /api/v1/inventory/{id}/` - Update/delete items

### Community

- `GET /api/v1/community/recipes/` - Public recipes
- `GET /api/v1/community/recipes/{id}/` - Public recipe details

See [Backend/API_DOCS.md](Backend/API_DOCS.md) for detailed endpoint documentation.

## ⚙️ Configuration

### Rate Limiting

Daily recipe generation limits by subscription tier:

- **Free**: 5 recipes/day
- **Premium**: 50 recipes/day
- **Pro**: 100 recipes/day

Limits are tracked per calendar day and reset at midnight.

### Safe-Filtering

The backend automatically excludes recipes with ingredients that conflict with user's:

- Allergies
- Dietary restrictions

This is applied at two levels:

1. Query-level (database filtering)
2. Serializer-level (response validation)

### Rewards & Badges

Earn badges for:

- **Waste Warrior**: 7+ day cooking streak
- **Budget Boss**: 100+ points or $50+ savings
- **Green Chef**: Using only pantry items, 3+ streak
- **Protein Pro**: High-protein recipes or protein tag usage

Points are awarded for:

- Base: 10 points per logged meal
- Rating bonus: Meals rated 4+ stars get +5 points
- Streak bonus: Consistent cooking multipliers

## 🐛 Troubleshooting

### Frontend can't connect to backend

- Ensure backend is running on `http://localhost:8000`
- Check Vite proxy settings in `Frontend/vite.config.js`
- Clear browser cache and localStorage

### Rate limit exceeded error

- Check your subscription tier on Profile page
- Daily limits reset at midnight UTC
- Upgrade plan for more generations

### JWT token errors

- Check browser DevTools → Application → localStorage
- Clear tokens and re-login
- Check token expiry in browser console: `JSON.parse(atob(token.split('.')[1]))`

### API_DOCS not generating

- Ensure `drf-spectacular` dependency is installed
- Run: `python manage.py spectacular --file schema.yml`

## 🚀 Deployment

### Backend (Django)

1. Set `DEBUG=False` in settings
2. Update `ALLOWED_HOSTS` with your domain
3. Configure PostgreSQL database
4. Set environment variables (SECRET_KEY, API keys, etc.)
5. Run: `python manage.py collectstatic`
6. Use Gunicorn/WSGI server (e.g., `gunicorn config.wsgi`)

### Frontend (React)

1. Update API base URL in `Frontend/src/api.js`
2. Run: `npm run build`
3. Deploy `dist/` folder to static hosting (Vercel, Netlify, S3, etc.)
4. Configure CORS on backend for frontend domain

## 📚 Documentation

- **API Documentation**: [Backend/API_DOCS.md](Backend/API_DOCS.md)
- **Django Models**: Check `Backend/users/models.py`, `Backend/recipes/models.py`, etc.
- **React Components**: See component files in `Frontend/src/pages/` and `Frontend/src/components/`

## 🧪 Demo Data

Run the seed command to populate demo data:

```bash
python Backend/manage.py seed_nourishnest
```

This creates:

- Demo user: `demo@nourishnest.local` / `Password123!`
- 3 subscription plans (Free, Premium, Pro)
- Sample inventory items
- Demo recipes

## 📄 License

This project is proprietary and confidential.

## 🤝 Support

For issues or feature requests, please reach out to the development team.

---

**Note**: This application is designed for local development and testing. For production deployment, ensure proper security measures, environment configuration, and database backups.
