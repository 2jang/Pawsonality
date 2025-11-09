import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { getMBTIMatch } from '../services/api'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card'
import { Heart, Search } from 'lucide-react'

const MBTI_TYPES = [
  'INTJ', 'INTP', 'ENTJ', 'ENTP',
  'INFJ', 'INFP', 'ENFJ', 'ENFP',
  'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
  'ISTP', 'ISFP', 'ESTP', 'ESFP',
]

export default function MBTIMatchPage() {
  const [selectedMBTI, setSelectedMBTI] = useState('')

  const matchMutation = useMutation({
    mutationFn: getMBTIMatch,
  })

  const handleSearch = () => {
    if (!selectedMBTI) return
    matchMutation.mutate({ mbti: selectedMBTI })
  }

  return (
    <div className="min-h-screen py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <Heart className="w-16 h-16 text-primary mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">MBTI 매칭</h1>
          <p className="text-xl text-muted-foreground">
            나의 MBTI와 잘 맞는 강아지 유형을 찾아보세요!
          </p>
        </div>

        {/* MBTI Selection */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>나의 MBTI를 선택하세요</CardTitle>
            <CardDescription>16가지 유형 중 하나를 선택해주세요</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-3 mb-4">
              {MBTI_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedMBTI(type)}
                  className={`p-4 rounded-lg border-2 font-bold transition-all hover:shadow-md ${
                    selectedMBTI === type
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
            <Button
              onClick={handleSearch}
              disabled={!selectedMBTI || matchMutation.isPending}
              size="lg"
              className="w-full"
            >
              {matchMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2"></div>
                  매칭 중...
                </>
              ) : (
                <>
                  <Search className="mr-2" />
                  매칭 결과 보기
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results */}
        {matchMutation.data && (
          <>
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>
                  {matchMutation.data.mbti} - {matchMutation.data.mbti_type_name}
                </CardTitle>
                <CardDescription>
                  {matchMutation.data.mbti_description}
                </CardDescription>
              </CardHeader>
            </Card>

            <div className="space-y-4">
              <h2 className="text-2xl font-bold">추천 강아지 유형</h2>
              {matchMutation.data.recommended_dogs.map((dog, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-xl font-bold">{dog.type_name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {dog.dbti_code}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-primary">
                          {dog.match_score}%
                        </div>
                        <div className="text-xs text-muted-foreground">
                          매칭률
                        </div>
                      </div>
                    </div>
                    <p className="text-muted-foreground">
                      {dog.compatibility_reason}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>

            {matchMutation.data.care_tips.length > 0 && (
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>💡 양육 팁</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {matchMutation.data.care_tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  )
}

