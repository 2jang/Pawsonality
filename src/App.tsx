import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DBTITestPage from './pages/DBTITestPage'
import DBTIResultPage from './pages/DBTIResultPage'
import ChatbotPage from './pages/ChatbotPage'
import MBTIMatchPage from './pages/MBTIMatchPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/test" element={<DBTITestPage />} />
        <Route path="/result/:code" element={<DBTIResultPage />} />
        <Route path="/chat" element={<ChatbotPage />} />
        <Route path="/mbti" element={<MBTIMatchPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  )
}

export default App

