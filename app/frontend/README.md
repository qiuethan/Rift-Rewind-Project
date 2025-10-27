# Rift Rewind Frontend

React + TypeScript frontend for League of Legends analytics with Supabase authentication.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm run dev
```

Visit http://localhost:5173

## 📁 Project Structure

```
src/
├── api/              # HTTP layer (axios client)
├── actions/          # Business logic layer
├── components/       # Reusable UI components
├── pages/            # Route pages
├── config/           # Constants and configuration
├── lib/              # Third-party integrations (Supabase)
├── App.tsx           # Route definitions
├── main.tsx          # Entry point
└── index.css         # Global styles
```

## 🏗️ Architecture

### Layer Flow
```
Components → Pages → Actions → API → Backend
```

### Key Principles
1. **Pages** call **Actions** (never API directly)
2. **Actions** call **API** (handle errors, return `{success, data/error}`)
3. **API** calls **Backend** (auto-injects auth headers)
4. **Components** are reusable UI building blocks

## 🔐 Authentication with Supabase

### Register
```typescript
const result = await authActions.register({
  email: 'user@example.com',
  password: 'password123'
});

if (result.success) {
  // User registered, token stored in localStorage
  navigate('/dashboard');
} else {
  // Show error: result.error
}
```

### Login
```typescript
const result = await authActions.login({
  email: 'user@example.com',
  password: 'password123'
});

if (result.success) {
  // User logged in, token stored
  navigate('/dashboard');
}
```

### Protected Routes
```typescript
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = authActions.isAuthenticated();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}
```

## 📦 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎨 Components

### Button
```typescript
<Button variant="primary" fullWidth loading={loading}>
  Click Me
</Button>
```

### Input
```typescript
<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={error}
  fullWidth
/>
```

### Card
```typescript
<Card title="My Card">
  <p>Content here</p>
</Card>
```

## 🔌 API Integration

All API calls automatically include authentication headers:

```typescript
// In actions/players.ts
const result = await playersActions.getSummoner();

if (result.success) {
  setSummoner(result.data);
} else {
  setError(result.error);
}
```

## 🎯 Pages

- **LoginPage** - User login with Supabase
- **RegisterPage** - User registration with optional summoner linking
- **DashboardPage** - Main dashboard with user info

## 🔧 Environment Variables

Required:
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Your Supabase anon/public key

Optional:
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## 📝 Adding New Features

### 1. Create API Function
```typescript
// src/api/feature.ts
export const featureApi = {
  getData: async (): Promise<DataType> => {
    return apiClient.get<DataType>('/api/feature');
  },
};
```

### 2. Create Action
```typescript
// src/actions/feature.ts
export const featureActions = {
  getData: async () => {
    try {
      const data = await featureApi.getData();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed',
      };
    }
  },
};
```

### 3. Use in Page
```typescript
const result = await featureActions.getData();
if (result.success) {
  setData(result.data);
} else {
  setError(result.error);
}
```

## 🛠️ Tech Stack

- **React 18** - UI library
- **TypeScript 5** - Type safety
- **Vite 5** - Build tool
- **React Router 6** - Routing
- **Supabase** - Authentication & database
- **Axios** - HTTP client
- **CSS Modules** - Component styling

## 🔒 Security

- JWT tokens stored in localStorage
- Auto-injected auth headers on all API calls
- Protected routes with authentication check
- Supabase handles password hashing and security

## 📚 Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [Vite Documentation](https://vitejs.dev/)

## ✅ Ready to Go!

Your frontend is fully set up with:
- ✅ Supabase authentication
- ✅ Clean architecture (Pages → Actions → API)
- ✅ Protected routes
- ✅ Reusable components
- ✅ TypeScript type safety
- ✅ Auto-injected auth headers

Just run `npm install` and `npm run dev` to start! 🚀
