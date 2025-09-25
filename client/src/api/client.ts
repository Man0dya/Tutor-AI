import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

export const api = axios.create({
  baseURL,
})

// Redirect to pricing if server signals payment required
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status
    if (status === 402) {
      // Optionally pass code/message to UI via querystring
      const code = error?.response?.data?.code
      const url = code ? `/pricing?code=${encodeURIComponent(code)}` : '/pricing'
      try {
        if (typeof window !== 'undefined') window.location.assign(url)
      } catch {}
    }
    return Promise.reject(error)
  }
)

export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

export type LoginResponse = {
  access_token: string
  token_type: string
}

export async function login(email: string, password: string) {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)
  const res = await api.post<LoginResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}

export async function signup(name: string, email: string, password: string) {
  const res = await api.post('/auth/signup', { name, email, password })
  return res.data
}

export type UserProfile = {
  id: string
  email: string
  name: string
}

export async function getCurrentUser() {
  const res = await api.get<UserProfile>('/auth/me')
  return res.data
}

// Content generation
export type ContentRequest = {
  topic: string
  difficulty?: string
  subject?: string
  contentType?: string
  learningObjectives?: string[]
}

export type ContentOut = {
  id: string
  topic: string
  content: string
  metadata: Record<string, unknown>
  // Optional denormalized fields used in UI
  subject?: string
  difficulty?: string
  contentType?: string
}

export async function generateContent(payload: ContentRequest) {
  const res = await api.post<ContentOut>('/content/generate', payload)
  return res.data
}

// Billing
export type SubscriptionSummary = {
  status?: string
  current_period_end?: number
  cancel_at_period_end?: boolean
  price?: { id?: string; unit_amount?: number; currency?: string; interval?: string }
  next_invoice_amount_due?: number
  next_invoice_currency?: string
  next_payment_attempt?: number
}

export async function getBillingStatus() {
  const res = await api.get('/billing/me')
  return res.data as { plan: string; usage: Record<string, unknown>; subscription?: SubscriptionSummary }
}

export async function createCheckoutSession(
  price: 'standard' | 'premium',
  successUrl?: string,
  cancelUrl?: string,
  priceId?: string
) {
  const payload: any = { price, successUrl, cancelUrl }
  if (priceId) payload.priceId = priceId
  const res = await api.post('/billing/checkout/session', payload)
  return res.data as { id: string; url?: string }
}

export async function createBillingPortal() {
  const res = await api.post('/billing/portal')
  return res.data as { url: string }
}

export async function cancelSubscription(atPeriodEnd: boolean = true) {
  const res = await api.post('/billing/subscription/cancel', { atPeriodEnd })
  return res.data as { status: string; cancel_at_period_end?: boolean; plan?: string }
}

export async function resumeSubscription() {
  const res = await api.post('/billing/subscription/resume')
  return res.data as { status: string; cancel_at_period_end?: boolean }
}

export async function getContentById(id: string) {
  const res = await api.get<ContentOut>(`/content/${encodeURIComponent(id)}`)
  return res.data
}

// Questions
export type QuestionsRequest = {
  contentId: string
  questionCount?: number
  questionTypes?: string[]
  difficultyDistribution?: Record<string, number>
  bloomLevels?: string[]
}

export type Question = {
  type: string
  question: string
  options?: string[]
  correct_answer?: string
  explanation?: string
  difficulty?: string
  bloom_level?: string
}

export type QuestionSetOut = {
  id: string
  contentId: string
  questions: Question[]
  metadata: Record<string, unknown>
}

export async function generateQuestions(payload: QuestionsRequest) {
  const res = await api.post<QuestionSetOut>('/questions/generate', payload)
  return res.data
}

// Answers & feedback
export type AnswerSubmitRequest = {
  questionSetId: string
  answers: Record<number | string, string>
}

export type FeedbackOut = {
  id: string
  questionSetId: string
  overallScore: number
  detailedFeedback: string
  studySuggestions?: string
  individualEvaluations?: Array<Record<string, any>>
}

export async function submitAnswers(payload: AnswerSubmitRequest) {
  const res = await api.post<FeedbackOut>('/answers/submit', payload)
  return res.data
}

// Progress
export type ProgressOut = {
  content_count?: number
  questions_answered?: number
  average_score?: number
  study_streak?: number
  score_history?: { date: string; score: number }[]
  subject_performance?: Record<string, number>
  recent_activity?: Array<Record<string, any>>
  recent_contents?: Array<{ id: string; topic: string; createdAt: string }>
  recent_question_sets?: Array<{ id: string; contentId: string; questionCount: number; createdAt: string }>
  recent_feedback?: Array<{ id: string; questionSetId: string; overallScore: number; createdAt: string }>
  threads?: Array<{
    content: { id: string; topic: string; createdAt: string }
    questionSets: Array<{
      id: string
      createdAt: string
      questionCount: number
      answers: Array<{ id: string; submittedAt: string }>
      feedback: Array<{ id: string; overallScore: number; createdAt: string }>
    }>
  }>
}

export async function getMyProgress() {
  const res = await api.get<ProgressOut>('/progress/me')
  return res.data
}

export interface ProfileUpdateRequest {
  name: string
  email: string
  current_password?: string
  new_password?: string
}

export async function updateProfile(data: ProfileUpdateRequest) {
  const res = await api.put<UserProfile>('/auth/profile', data)
  return res.data
}

// Helper: extract a human-friendly error message from Axios/FastAPI errors
export function getErrorMessage(err: any): string {
  const d = err?.response?.data
  if (!d) return err?.message || 'Unexpected error'
  if (typeof d === 'string') return d
  if (typeof d?.detail === 'string') return d.detail
  // FastAPI can send detail as object
  if (d?.detail && typeof d.detail === 'object') {
    try { return JSON.stringify(d.detail) } catch { /* noop */ }
  }
  try { return JSON.stringify(d) } catch { return 'Request failed' }
}
