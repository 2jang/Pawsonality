import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getPawnaType } from "../services/api";
import { Button } from "../components/ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { Home, MessageCircle, Share2 } from "lucide-react";

export default function PawnaResultPage() {
  const { code } = useParams<{ code: string }>();

  const {
    data: result,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["pawna-type", code],
    queryFn: () => getPawnaType(code!),
    enabled: !!code,
  });

  const careTips = result?.care_tips ?? [];
  const bestMatches = result?.compatibility?.best_match ?? [];
  const goodMatches = result?.compatibility?.good_match ?? [];

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-muted-foreground">결과를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>결과를 찾을 수 없습니다</CardTitle>
            <CardDescription>유효하지 않은 코드입니다</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/">
              <Button>홈으로 돌아가기</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Result Header */}
        <div className="text-center mb-8">
          <div className="inline-block px-6 py-3 bg-primary text-primary-foreground rounded-full text-2xl font-bold mb-4">
            {result.pawna_code}
          </div>
          <h1 className="text-4xl font-bold mb-2">{result.type_name}</h1>
          <p className="text-xl text-muted-foreground">{result.description}</p>
        </div>

        {/* Personality Traits */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>🐾 성격 특성</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.personality_traits.map((trait, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>{trait}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Care Tips */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>💡 양육 팁</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {careTips.map((tip, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Compatibility */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>❤️ 궁합</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2 text-green-600">최고의 궁합</h3>
              <div className="flex flex-wrap gap-2">
                {bestMatches.map((match, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium"
                  >
                    {match}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-blue-600">좋은 궁합</h3>
              <div className="flex flex-wrap gap-2">
                {goodMatches.map((match, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium"
                  >
                    {match}
                  </span>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <Link to="/">
            <Button variant="outline" size="lg">
              <Home className="mr-2" />
              홈으로
            </Button>
          </Link>
          <Link to="/chat" state={{ pawnaType: result.pawna_code }}>
            <Button size="lg">
              <MessageCircle className="mr-2" />
              AI 챗봇과 대화하기
            </Button>
          </Link>
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              if (navigator.share) {
                navigator.share({
                  title: `Pawsonality 결과: ${result.type_name}`,
                  text: `나의 강아지는 ${result.type_name}! ${result.description}`,
                  url: window.location.href,
                });
              } else {
                navigator.clipboard.writeText(window.location.href);
                alert("링크가 복사되었습니다!");
              }
            }}
          >
            <Share2 className="mr-2" />
            공유하기
          </Button>
        </div>
      </div>
    </div>
  );
}
