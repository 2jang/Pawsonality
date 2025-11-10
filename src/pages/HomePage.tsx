import { Link } from "react-router-dom";
import { Button } from "../components/ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { Dog, MessageCircle, Heart } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <header className="container mx-auto px-4 py-16 text-center">
        <div className="flex justify-center mb-6">
          <Dog size={64} className="text-primary" />
        </div>
        <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
          Pawsonality
        </h1>
        <p className="text-xl text-muted-foreground mb-2">
          Dog Personality Test
        </p>
        <p className="text-lg text-muted-foreground mb-8">
          우리 강아지의 성격을 알아보고, AI 챗봇과 대화해보세요! 🐾
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/test">
            <Button size="lg" className="text-lg px-8">
              테스트 시작하기
            </Button>
          </Link>
          <Link to="/chat">
            <Button size="lg" variant="outline" className="text-lg px-8">
              AI 챗봇
            </Button>
          </Link>
        </div>
      </header>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Dog className="w-12 h-12 text-primary mb-4" />
              <CardTitle>Personality Test</CardTitle>
              <CardDescription>
                12가지 질문으로 우리 강아지의 성격을 파악해보세요
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/test">
                <Button variant="outline" className="w-full">
                  테스트 시작
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <MessageCircle className="w-12 h-12 text-primary mb-4" />
              <CardTitle>AI 챗봇</CardTitle>
              <CardDescription>
                Dog Personality 전문 AI와 대화하며 양육 팁을 얻으세요
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/chat">
                <Button variant="outline" className="w-full">
                  챗봇 시작
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <Heart className="w-12 h-12 text-primary mb-4" />
              <CardTitle>MBTI 매칭</CardTitle>
              <CardDescription>
                나의 MBTI와 잘 맞는 강아지 유형을 찾아보세요
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/mbti">
                <Button variant="outline" className="w-full">
                  매칭 시작
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© 2025 Pawsonality - Dog Personality Test</p>
          <p className="text-sm mt-2">
            FastAPI + Vite + React + TypeScript + OpenRouter
          </p>
        </div>
      </footer>
    </div>
  );
}
