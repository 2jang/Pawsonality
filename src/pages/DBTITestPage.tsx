import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getDBTIQuestions, submitDBTI } from "../services/api";
import { Button } from "../components/ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";
import { ArrowLeft, ArrowRight, Send } from "lucide-react";

export default function DBTITestPage() {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<number, string>>({});

  // 질문 목록 불러오기
  const {
    data: questions,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["dbti-questions"],
    queryFn: getDBTIQuestions,
  });

  // 테스트 제출
  const submitMutation = useMutation({
    mutationFn: submitDBTI,
    onSuccess: (data) => {
      navigate(`/result/${data.dbti_code}`);
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-muted-foreground">질문을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>오류가 발생했습니다</CardTitle>
            <CardDescription>질문을 불러올 수 없습니다</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => navigate("/")}>홈으로 돌아가기</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return null;
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const isLastQuestion = currentQuestion === questions.length - 1;
  const canProceed = answers[question.id] !== undefined;

  const handleAnswer = (answer: "A" | "B") => {
    setAnswers((prev) => ({
      ...prev,
      [question.id]: answer,
    }));
  };

  const handleNext = () => {
    if (isLastQuestion) {
      // 마지막 질문이면 제출
      // answers 객체를 배열로 변환
      const answersArray = Object.entries(answers).map(
        ([questionId, selected]) => ({
          question_id: parseInt(questionId),
          selected: selected,
        })
      );
      submitMutation.mutate({ answers: answersArray });
    } else {
      // 다음 질문으로
      setCurrentQuestion((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion((prev) => prev - 1);
    }
  };

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-3xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold mb-2">DBTI 테스트</h1>
          <p className="text-muted-foreground">
            질문 {currentQuestion + 1} / {questions.length}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">{question.title}</CardTitle>
            <CardDescription>
              A와 B 중 우리 강아지에 더 가까운 것을 선택해주세요
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Option A */}
            <button
              onClick={() => handleAnswer('A')}
              className={`w-full p-6 text-left rounded-lg border-2 transition-all hover:shadow-md ${
                answers[question.id] === 'A'
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold ${
                    answers[question.id] === 'A'
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border'
                  }`}
                >
                  A
                </div>
                <span className="text-lg">{question.option_a}</span>
              </div>
            </button>

            {/* Option B */}
            <button
              onClick={() => handleAnswer('B')}
              className={`w-full p-6 text-left rounded-lg border-2 transition-all hover:shadow-md ${
                answers[question.id] === 'B'
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center font-bold ${
                    answers[question.id] === 'B'
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border'
                  }`}
                >
                  B
                </div>
                <span className="text-lg">{question.option_b}</span>
              </div>
            </button>
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            <ArrowLeft className="mr-2" />
            이전
          </Button>

          <Button
            onClick={handleNext}
            disabled={!canProceed || submitMutation.isPending}
          >
            {submitMutation.isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2"></div>
                제출 중...
              </>
            ) : isLastQuestion ? (
              <>
                결과 보기
                <Send className="ml-2" />
              </>
            ) : (
              <>
                다음
                <ArrowRight className="ml-2" />
              </>
            )}
          </Button>
        </div>

        {/* Answer Summary */}
        <div className="mt-8 p-4 bg-secondary rounded-lg">
          <p className="text-sm text-muted-foreground text-center">
            답변 완료: {Object.keys(answers).length} / {questions.length}
          </p>
        </div>
      </div>
    </div>
  );
}
