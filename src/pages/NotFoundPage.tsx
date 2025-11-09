import { Link } from 'react-router-dom'
import { Button } from '../components/ui/Button'
import { Home } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-muted-foreground mb-4">404</h1>
        <p className="text-2xl mb-8">페이지를 찾을 수 없습니다</p>
        <Link to="/">
          <Button size="lg">
            <Home className="mr-2" />
            홈으로 돌아가기
          </Button>
        </Link>
      </div>
    </div>
  )
}

