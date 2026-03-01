import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Trophy, Star, Target, Briefcase, Lightbulb, Download, Share2,
  ArrowLeft, CheckCircle, Brain, Heart, Zap, Users, Award,
  ChevronRight, Sparkles, TrendingUp
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const TestResult = () => {
  const { resultId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState(null);
  const [showCertificatePrompt, setShowCertificatePrompt] = useState(false);

  useEffect(() => {
    if (resultId) {
      loadResult();
    }
  }, [resultId]);

  const loadResult = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/test-results/${resultId}`);
      setResult(response.data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Gagal memuat hasil test',
        variant: 'destructive'
      });
      navigate('/user-test');
    } finally {
      setLoading(false);
    }
  };

  const downloadCertificate = async () => {
    try {
      const token = localStorage.getItem('user_token');
      const response = await axios.get(`${BACKEND_URL}/api/certificates/download-ai-certificate`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `sertifikat_newmeclass_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Berhasil',
        description: 'Sertifikat berhasil diunduh'
      });
    } catch (error) {
      if (error.response?.status === 403) {
        setShowCertificatePrompt(true);
      } else {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Gagal mengunduh sertifikat',
          variant: 'destructive'
        });
      }
    }
  };

  const shareResult = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Hasil Test Kepribadian NEWMECLASS',
        text: `Saya baru saja menyelesaikan test kepribadian dan mendapatkan hasil: ${result?.analysis?.personalityType}`,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast({
        title: 'Link Disalin',
        description: 'Link hasil test telah disalin ke clipboard'
      });
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      personality: <Heart className="w-5 h-5" />,
      talent: <Zap className="w-5 h-5" />,
      skills: <Target className="w-5 h-5" />,
      interest: <Lightbulb className="w-5 h-5" />,
      general: <Brain className="w-5 h-5" />
    };
    return icons[category] || icons.general;
  };

  const getCategoryColor = (category) => {
    const colors = {
      personality: 'from-pink-500 to-rose-500',
      talent: 'from-yellow-500 to-orange-500',
      skills: 'from-blue-500 to-indigo-500',
      interest: 'from-green-500 to-emerald-500',
      general: 'from-purple-500 to-violet-500'
    };
    return colors[category] || colors.general;
  };

  const getCategoryLabel = (category) => {
    const labels = {
      personality: 'Kepribadian',
      talent: 'Bakat',
      skills: 'Kemampuan',
      interest: 'Minat',
      general: 'Umum'
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-yellow-400">Memuat hasil test...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] flex items-center justify-center">
        <Card className="bg-[#2a2a2a] border-red-500/30 max-w-md">
          <CardContent className="p-6 text-center">
            <p className="text-white mb-4">Hasil test tidak ditemukan</p>
            <Link to="/user-test">
              <Button className="bg-yellow-400 text-black">Kembali ke Test</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const analysis = result.analysis || {};
  const categoryAnalysis = analysis.categoryAnalysis || {};

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] py-8" data-testid="test-result-page">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <Link to="/user-test">
            <Button variant="outline" className="border-yellow-400 text-yellow-400">
              <ArrowLeft className="w-4 h-4 mr-2" /> Kembali
            </Button>
          </Link>
          <div className="flex gap-2">
            <Button 
              onClick={shareResult}
              variant="outline" 
              className="border-yellow-400/50 text-yellow-400"
            >
              <Share2 className="w-4 h-4 mr-2" /> Share
            </Button>
            {result.testType === 'paid' && (
              <Button 
                onClick={downloadCertificate}
                className="bg-yellow-400 text-black"
              >
                <Download className="w-4 h-4 mr-2" /> Sertifikat
              </Button>
            )}
          </div>
        </div>

        {/* Main Result Card */}
        <Card className="bg-gradient-to-br from-yellow-400/20 to-yellow-600/10 border-yellow-400/30 mb-6 overflow-hidden">
          <div className="absolute top-0 right-0 w-40 h-40 bg-yellow-400/10 rounded-full blur-3xl"></div>
          <CardHeader className="text-center relative z-10">
            <div className="w-24 h-24 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg shadow-yellow-400/30">
              <Trophy className="w-12 h-12 text-[#1a1a1a]" />
            </div>
            <CardTitle className="text-white text-3xl mb-2">Test Selesai!</CardTitle>
            <CardDescription className="text-gray-300 text-lg">
              {result.testType === 'free' ? '5 Test Dasar Gratis' : 'Test Berbayar Premium'}
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center pb-8">
            <div className="inline-block bg-[#1a1a1a]/50 rounded-2xl px-8 py-4 mb-4">
              <p className="text-yellow-400 text-sm mb-1">Tipe Kepribadian Anda</p>
              <p className="text-white text-2xl font-bold">{analysis.personalityType || 'Analitis'}</p>
            </div>
            <div className="flex justify-center gap-8 text-center">
              <div>
                <p className="text-3xl font-bold text-white">{result.answeredCount || 0}</p>
                <p className="text-gray-400 text-sm">Pertanyaan Dijawab</p>
              </div>
              <div>
                <p className="text-3xl font-bold text-yellow-400">{result.totalScore || 0}</p>
                <p className="text-gray-400 text-sm">Total Skor</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Category Scores */}
        {Object.keys(categoryAnalysis).length > 0 && (
          <Card className="bg-[#2a2a2a] border-yellow-400/20 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-yellow-400" />
                Analisis per Kategori
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(categoryAnalysis).map(([category, data]) => (
                <div key={category} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-8 h-8 rounded-full bg-gradient-to-r ${getCategoryColor(category)} flex items-center justify-center text-white`}>
                        {getCategoryIcon(category)}
                      </div>
                      <span className="text-white font-medium">{getCategoryLabel(category)}</span>
                    </div>
                    <span className="text-yellow-400 font-semibold">{data.percentage}%</span>
                  </div>
                  <Progress value={data.percentage} className="h-2" />
                  <p className="text-gray-400 text-sm">Skor: {data.score} / {data.maxScore}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Strengths */}
        {analysis.strengths && analysis.strengths.length > 0 && (
          <Card className="bg-[#2a2a2a] border-green-500/20 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Star className="w-5 h-5 text-green-500" />
                Kekuatan Anda
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {analysis.strengths.map((strength, index) => (
                  <div 
                    key={index}
                    className="flex items-start gap-3 bg-green-500/10 rounded-lg p-3"
                  >
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <p className="text-gray-300 text-sm">{strength}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Areas to Improve */}
        {analysis.areasToImprove && analysis.areasToImprove.length > 0 && (
          <Card className="bg-[#2a2a2a] border-blue-500/20 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-blue-500" />
                Area Pengembangan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analysis.areasToImprove.map((area, index) => (
                  <div 
                    key={index}
                    className="flex items-center gap-3 bg-blue-500/10 rounded-lg p-3"
                  >
                    <ChevronRight className="w-5 h-5 text-blue-500 flex-shrink-0" />
                    <p className="text-gray-300 text-sm">{area}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Career Recommendations */}
        {analysis.careerRecommendations && analysis.careerRecommendations.length > 0 && (
          <Card className="bg-[#2a2a2a] border-purple-500/20 mb-6">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-purple-500" />
                Rekomendasi Karir
              </CardTitle>
              <CardDescription className="text-gray-400">
                Berdasarkan hasil analisis, berikut karir yang cocok untuk Anda
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {analysis.careerRecommendations.map((career, index) => (
                  <span 
                    key={index}
                    className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-full text-sm border border-purple-500/30"
                  >
                    {career}
                  </span>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Summary */}
        {analysis.summary && (
          <Card className="bg-gradient-to-r from-yellow-400/10 to-yellow-600/5 border-yellow-400/30 mb-6">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-yellow-400/20 rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-yellow-400" />
                </div>
                <div>
                  <h3 className="text-yellow-400 font-semibold mb-2">Ringkasan</h3>
                  <p className="text-gray-300 leading-relaxed">{analysis.summary}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Certificate Prompt for Free Test */}
        {result.testType === 'free' && (
          <Card className="bg-gradient-to-r from-yellow-400/20 to-orange-500/10 border-yellow-400/30 mb-6">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center flex-shrink-0">
                  <Award className="w-8 h-8 text-[#1a1a1a]" />
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-lg mb-1">
                    Ingin Sertifikat Digital?
                  </h3>
                  <p className="text-gray-400 text-sm mb-3">
                    Upgrade ke Test Berbayar untuk mendapatkan analisis mendalam dan sertifikat digital yang dapat dibagikan
                  </p>
                  <Link to="/user-test">
                    <Button className="bg-yellow-400 text-black hover:bg-yellow-500">
                      Ambil Test Berbayar <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          <Link to="/user-test" className="flex-1">
            <Button className="w-full bg-yellow-400 hover:bg-yellow-500 text-black">
              Test Lagi
            </Button>
          </Link>
          <Link to="/dashboard" className="flex-1">
            <Button variant="outline" className="w-full border-yellow-400 text-yellow-400">
              Dashboard
            </Button>
          </Link>
        </div>

        {/* Certificate Upgrade Modal */}
        {showCertificatePrompt && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <Card className="bg-[#2a2a2a] border-yellow-400/30 max-w-md w-full">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Award className="w-6 h-6 text-yellow-400" />
                  Sertifikat Premium
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-gray-300">
                  Sertifikat digital hanya tersedia untuk pengguna yang telah menyelesaikan Test Berbayar Premium.
                </p>
                <div className="flex gap-3">
                  <Link to="/user-test" className="flex-1">
                    <Button className="w-full bg-yellow-400 text-black">
                      Ambil Test Premium
                    </Button>
                  </Link>
                  <Button 
                    variant="outline" 
                    className="border-gray-500 text-gray-300"
                    onClick={() => setShowCertificatePrompt(false)}
                  >
                    Tutup
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default TestResult;
