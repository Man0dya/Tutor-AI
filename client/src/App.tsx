import { Routes, Route, Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import ContentPage from './pages/Content'
import QuestionsPage from './pages/Questions'
import ProgressPage from './pages/Progress'
import FeedbackPage from './pages/Feedback'
import ContentViewPage from './pages/ContentView'
import PricingPage from './pages/Pricing'
import { useAuth } from './context/AuthContext'
import { useEffect, useState } from 'react'

function PrivateRoute({ children }: { children: ReactElement }) {
  const { user } = useAuth()
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    // Allow one tick for AuthContext to hydrate from localStorage
    const t = setTimeout(() => setChecking(false), 0)
    return () => clearTimeout(t)
  }, [])

  if (checking) return <></>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
  <Route path="/pricing" element={<PricingPage />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/content"
        element={
          <PrivateRoute>
            <ContentPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/questions"
        element={
          <PrivateRoute>
            <QuestionsPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/progress"
        element={
          <PrivateRoute>
            <ProgressPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/content/view"
        element={
          <PrivateRoute>
            <ContentViewPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/feedback"
        element={
          <PrivateRoute>
            <FeedbackPage />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
