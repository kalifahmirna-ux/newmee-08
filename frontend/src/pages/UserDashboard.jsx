import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  User, CreditCard, Award, FileText, LogOut, Upload, Clock, CheckCircle, XCircle, 
  ShoppingBag, ChevronRight, Copy, Share2, Gift, AlertCircle, Play, Lock, Sparkles, Wallet,
  Droplets, Flame, Mountain, Wind, Leaf, Info, Trophy, Star, Target, Brain
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { useToast } from '../hooks/use-toast';
import { authAPI, userPaymentsAPI, settingsAPI, runningInfoAPI, referralAPI, aiAnalysisAPI } from '../services/api';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const UserDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState(null);
  const [uploadingProof, setUploadingProof] = useState(false);
  const [proofFile, setProofFile] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('bank');
  const [runningInfo, setRunningInfo] = useState([]);
  const [referralSettings, setReferralSettings] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [qrisData, setQrisData] = useState(null);
  const [loadingQris, setLoadingQris] = useState(false);
  const [checkingPayment, setCheckingPayment] = useState(false);
  const [premiumResult, setPremiumResult] = useState(null);
  const [showElementInfo, setShowElementInfo] = useState(false);

  // 5 Element Data
  const fiveElements = [
    {
      name: 'KAYU',
      label: 'SI KREATIF',
      icon: Leaf,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-500/20',
      textColor: 'text-green-400',
      description: 'Inovatif, visioner, artistik, kaya gagasan. Organ terkait: Hati & Empedu.',
      traits: ['Inovatif', 'Visioner', 'Artistik', 'Kaya Gagasan', 'Fleksibel'],
      careers: ['Desainer', 'Seniman', 'Entrepreneur', 'Content Creator', 'Arsitek']
    },
    {
      name: 'API',
      label: 'SI PERASA',
      icon: Flame,
      color: 'from-red-500 to-orange-500',
      bgColor: 'bg-red-500/20',
      textColor: 'text-red-400',
      description: 'Passionate, energik, ekspresif, penyampai. Organ terkait: Jantung & Usus Halus.',
      traits: ['Passionate', 'Energik', 'Ekspresif', 'Hangat', 'Antusias'],
      careers: ['Public Speaker', 'Sales', 'Marketing', 'Entertainer', 'Motivator']
    },
    {
      name: 'TANAH',
      label: 'SI STABIL',
      icon: Mountain,
      color: 'from-yellow-600 to-amber-600',
      bgColor: 'bg-yellow-500/20',
      textColor: 'text-yellow-400',
      description: 'Konsisten, praktis, dapat diandalkan, penggerak. Organ terkait: Limpa & Lambung.',
      traits: ['Konsisten', 'Praktis', 'Dapat Diandalkan', 'Sabar', 'Loyal'],
      careers: ['Manager', 'Akuntan', 'Administrator', 'HR', 'Project Manager']
    },
    {
      name: 'LOGAM',
      label: 'SI TEGAS',
      icon: Wind,
      color: 'from-gray-400 to-slate-500',
      bgColor: 'bg-gray-500/20',
      textColor: 'text-gray-300',
      description: 'Disiplin, tegas, terstruktur, perfeksionis, pencerna. Organ terkait: Paru & Usus Besar.',
      traits: ['Disiplin', 'Tegas', 'Terstruktur', 'Perfeksionis', 'Fokus'],
      careers: ['Lawyer', 'Auditor', 'Engineer', 'Quality Control', 'Analyst']
    },
    {
      name: 'AIR',
      label: 'SI ADAPTIF',
      icon: Droplets,
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-500/20',
      textColor: 'text-blue-400',
      description: 'Bijaksana, intuitif, reflektif, penenang. Organ terkait: Ginjal & Kandung Kemih.',
      traits: ['Bijaksana', 'Intuitif', 'Reflektif', 'Adaptif', 'Tenang'],
      careers: ['Konselor', 'Peneliti', 'Psikolog', 'Penulis', 'Mediator']
    }
  ];

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    await Promise.all([
      loadUserData(),
      loadSettings(),
      loadRunningInfo(),
      loadReferralSettings(),
      loadPremiumResult()
    ]);
    setLoading(false);
  };

  const loadPremiumResult = async () => {
    try {
      const response = await aiAnalysisAPI.getLatest();
      if (response.data.success && response.data.analysis) {
        setPremiumResult(response.data.analysis);
      }
    } catch (error) {
      console.log('No premium result found');
    }
  };

  const loadUserData = async () => {
    try {
      const token = localStorage.getItem('user_token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await authAPI.getProfile();
      setUser(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_data');
        navigate('/login');
      }
    }
  };

  const loadSettings = async () => {
    try {
      const response = await settingsAPI.get();
      setSettings(response.data);
    } catch (error) {
      console.error('Failed to load settings');
    }
  };

  const loadRunningInfo = async () => {
    try {
      const response = await runningInfoAPI.getActive();
      setRunningInfo(response.data);
    } catch (error) {
      console.error('Failed to load running info');
    }
  };

  const loadReferralSettings = async () => {
    try {
      const response = await referralAPI.getSettings();
      setReferralSettings(response.data);
    } catch (error) {
      console.error('Failed to load referral settings');
    }
  };

  const handleUploadProof = async () => {
    if (!proofFile) {
      toast({
        title: 'Error',
        description: 'Pilih file bukti pembayaran',
        variant: 'destructive'
      });
      return;
    }

    setUploadingProof(true);
    try {
      const formData = new FormData();
      formData.append('file', proofFile);
      formData.append('paymentType', 'test');
      formData.append('paymentMethod', paymentMethod === 'bank' ? 'Transfer Bank' : 'QRIS');
      formData.append('paymentAmount', settings?.paymentAmount || 50000);

      await userPaymentsAPI.uploadProof(formData);
      
      toast({
        title: 'Berhasil',
        description: 'Bukti pembayaran berhasil diupload. Menunggu verifikasi admin.'
      });
      
      setProofFile(null);
      loadUserData();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Gagal upload bukti pembayaran',
        variant: 'destructive'
      });
    } finally {
      setUploadingProof(false);
    }
  };

  const handleCopyReferral = () => {
    const referralLink = `${window.location.origin}/register?ref=${user?.myReferralCode}`;
    navigator.clipboard.writeText(referralLink);
    toast({
      title: 'Berhasil',
      description: 'Link referral berhasil disalin!'
    });
  };

  const handleShareReferral = async () => {
    const referralLink = `${window.location.origin}/register?ref=${user?.myReferralCode}`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Daftar di NEWME CLASS',
          text: `Daftar di NEWME CLASS dan temukan potensi terbaikmu! Gunakan kode referral saya: ${user?.myReferralCode}`,
          url: referralLink
        });
      } catch (error) {
        handleCopyReferral();
      }
    } else {
      handleCopyReferral();
    }
  };

  const handleCreateQRIS = async () => {
    // QRIS generation removed - use bank transfer or E-Wallet manual upload instead
    toast({
      title: 'Info',
      description: 'Pilih Transfer Bank atau E-Wallet, lakukan pembayaran, lalu upload bukti bayar.',
    });
  };

  const handleCheckPaymentStatus = async (orderId) => {
    if (checkingPayment) return;
    
    setCheckingPayment(true);
    try {
      const response = await userPaymentsAPI.checkPayment(orderId);
      
      if (response.data.status === 'settlement') {
        toast({
          title: 'Pembayaran Berhasil!',
          description: 'Pembayaran Anda telah dikonfirmasi'
        });
        setQrisData(null);
        await loadUserData();
      }
    } catch (error) {
      console.error('Error checking payment:', error);
    } finally {
      setCheckingPayment(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(price || 0);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'not_started': { label: 'Belum Mulai', color: 'bg-gray-400/20 text-gray-400', icon: AlertCircle },
      'in_progress': { label: 'Sedang Berlangsung', color: 'bg-purple-400/20 text-purple-400', icon: Play },
      'completed': { label: 'Selesai', color: 'bg-green-400/20 text-green-400', icon: CheckCircle },
      'unpaid': { label: 'Belum Bayar', color: 'bg-red-400/20 text-red-400', icon: XCircle },
      'pending': { label: 'Menunggu Verifikasi', color: 'bg-yellow-400/20 text-yellow-400', icon: Clock },
      'approved': { label: 'Disetujui', color: 'bg-green-400/20 text-green-400', icon: CheckCircle },
      'rejected': { label: 'Ditolak', color: 'bg-red-400/20 text-red-400', icon: XCircle }
    };
    return statusMap[status] || { label: status, color: 'bg-gray-400/20 text-gray-400', icon: AlertCircle };
  };

  const canStartFreeTest = user?.freeTestStatus !== 'completed';
  const canStartPaidTest = user?.paymentStatus === 'approved' && user?.paidTestStatus !== 'completed';
  const needsPayment = settings?.requirePayment && user?.paymentStatus !== 'approved';

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a]">
      {/* Running Information Marquee */}
      {runningInfo.length > 0 && (
        <div className="bg-yellow-400 text-black py-2 overflow-hidden">
          <div className="animate-marquee whitespace-nowrap">
            {runningInfo.map((info, idx) => (
              <span key={idx} className="mx-8 inline-flex items-center">
                <Sparkles className="w-4 h-4 mr-2" />
                {info.message}
                {info.linkUrl && (
                  <a href={info.linkUrl} className="ml-2 underline font-semibold">{info.linkText || 'Selengkapnya'}</a>
                )}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Selamat Datang, {user?.fullName}</h1>
            <p className="text-gray-400">Dashboard NEWME CLASS</p>
          </div>
          <div className="flex gap-3">
            <Link to="/shop">
              <Button variant="outline" className="border-yellow-400/50 text-yellow-400">
                <ShoppingBag className="w-4 h-4 mr-2" /> Shop
              </Button>
            </Link>
            <Button onClick={handleLogout} variant="outline" className="border-red-400/50 text-red-400">
              <LogOut className="w-4 h-4 mr-2" /> Logout
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: User },
            { id: 'results', label: 'Hasil Test', icon: Trophy },
            { id: 'elements', label: '5 Element', icon: Info },
            { id: 'test', label: 'Test', icon: FileText },
            { id: 'payment', label: 'Pembayaran', icon: CreditCard },
            { id: 'referral', label: 'Referral', icon: Gift }
          ].map(tab => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'default' : 'outline'}
              onClick={() => setActiveTab(tab.id)}
              className={activeTab === tab.id 
                ? 'bg-yellow-400 text-black hover:bg-yellow-500' 
                : 'border-yellow-400/30 text-gray-400'
              }
            >
              <tab.icon className="w-4 h-4 mr-2" /> {tab.label}
            </Button>
          ))}
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Test Gratis</p>
                      <span className={`inline-flex items-center mt-1 px-2 py-1 rounded text-xs ${getStatusBadge(user?.freeTestStatus).color}`}>
                        {React.createElement(getStatusBadge(user?.freeTestStatus).icon, { className: 'w-3 h-3 mr-1' })}
                        {getStatusBadge(user?.freeTestStatus).label}
                      </span>
                    </div>
                    <Sparkles className="w-8 h-8 text-green-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Test Premium</p>
                      <span className={`inline-flex items-center mt-1 px-2 py-1 rounded text-xs ${getStatusBadge(user?.paidTestStatus).color}`}>
                        {React.createElement(getStatusBadge(user?.paidTestStatus).icon, { className: 'w-3 h-3 mr-1' })}
                        {getStatusBadge(user?.paidTestStatus).label}
                      </span>
                    </div>
                    <Award className="w-8 h-8 text-yellow-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Pembayaran</p>
                      <span className={`inline-flex items-center mt-1 px-2 py-1 rounded text-xs ${getStatusBadge(user?.paymentStatus).color}`}>
                        {React.createElement(getStatusBadge(user?.paymentStatus).icon, { className: 'w-3 h-3 mr-1' })}
                        {getStatusBadge(user?.paymentStatus).label}
                      </span>
                    </div>
                    <CreditCard className="w-8 h-8 text-yellow-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Referral</p>
                      <p className="text-2xl font-bold text-yellow-400">{user?.referralCount || 0}</p>
                    </div>
                    <Gift className="w-8 h-8 text-yellow-400/30" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Profile Info */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <User className="w-5 h-5 mr-2" /> Profil Saya
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-sm">Nama Lengkap</p>
                    <p className="text-white">{user?.fullName}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Email</p>
                    <p className="text-white">{user?.email}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">WhatsApp</p>
                    <p className="text-white">{user?.whatsapp}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Tanggal Lahir</p>
                    <p className="text-white">{user?.birthDate}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Provinsi</p>
                    <p className="text-white">{user?.province || '-'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Kota/Kabupaten</p>
                    <p className="text-white">{user?.city || '-'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Kecamatan</p>
                    <p className="text-white">{user?.district || '-'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Kelurahan/Desa</p>
                    <p className="text-white">{user?.village || '-'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Results Tab - Premium Results */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            {user?.paidTestStatus === 'completed' && premiumResult ? (
              <>
                {/* Premium Result Header */}
                <Card className="bg-gradient-to-br from-yellow-400/20 to-yellow-600/10 border-yellow-400/30">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-16 h-16 bg-yellow-400 rounded-full flex items-center justify-center">
                        <Trophy className="w-8 h-8 text-[#1a1a1a]" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold text-white">Hasil Test Premium</h2>
                        <p className="text-yellow-400">{premiumResult.aiAnalysis?.personalityType || 'Kepribadian Anda'}</p>
                      </div>
                    </div>
                    <p className="text-gray-300">{premiumResult.aiAnalysis?.summary || 'Analisis lengkap kepribadian Anda berdasarkan test premium.'}</p>
                  </CardContent>
                </Card>

                {/* Element Scores */}
                {premiumResult.aiAnalysis?.elementScores && (
                  <Card className="bg-[#2a2a2a] border-yellow-400/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Star className="w-5 h-5 text-yellow-400" /> Skor 5 Element
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {Object.entries(premiumResult.aiAnalysis.elementScores).map(([element, data]) => {
                          const elementInfo = fiveElements.find(e => e.name === element);
                          const Icon = elementInfo?.icon || Star;
                          return (
                            <div key={element} className="space-y-2">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <div className={`w-8 h-8 rounded-full ${elementInfo?.bgColor || 'bg-gray-500/20'} flex items-center justify-center`}>
                                    <Icon className={`w-4 h-4 ${elementInfo?.textColor || 'text-gray-400'}`} />
                                  </div>
                                  <span className="text-white">{element} - {data.label || elementInfo?.label}</span>
                                </div>
                                <span className={`font-bold ${elementInfo?.textColor || 'text-yellow-400'}`}>{data.percentage}%</span>
                              </div>
                              <div className="h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
                                <div 
                                  className={`h-full bg-gradient-to-r ${elementInfo?.color || 'from-yellow-400 to-yellow-600'}`}
                                  style={{ width: `${data.percentage}%` }}
                                />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Strengths & Areas to Improve */}
                <div className="grid md:grid-cols-2 gap-6">
                  {premiumResult.aiAnalysis?.strengths && (
                    <Card className="bg-[#2a2a2a] border-green-400/20">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                          <CheckCircle className="w-5 h-5 text-green-400" /> Kekuatan Anda
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {premiumResult.aiAnalysis.strengths.map((strength, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-gray-300">
                              <CheckCircle className="w-4 h-4 text-green-400 mt-1 flex-shrink-0" />
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}

                  {premiumResult.aiAnalysis?.areasToImprove && (
                    <Card className="bg-[#2a2a2a] border-blue-400/20">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                          <Target className="w-5 h-5 text-blue-400" /> Area Pengembangan
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {premiumResult.aiAnalysis.areasToImprove.map((area, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-gray-300">
                              <ChevronRight className="w-4 h-4 text-blue-400 mt-1 flex-shrink-0" />
                              {area}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Career Recommendations */}
                {premiumResult.aiAnalysis?.careerRecommendations && (
                  <Card className="bg-[#2a2a2a] border-purple-400/20">
                    <CardHeader>
                      <CardTitle className="text-white flex items-center gap-2">
                        <Award className="w-5 h-5 text-purple-400" /> Rekomendasi Karir
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {premiumResult.aiAnalysis.careerRecommendations.map((career, idx) => (
                          <span key={idx} className="px-4 py-2 bg-purple-500/20 text-purple-300 rounded-full text-sm border border-purple-500/30">
                            {career}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Download Certificate */}
                <Card className="bg-gradient-to-r from-yellow-400/10 to-yellow-600/5 border-yellow-400/30">
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-yellow-400 rounded-full flex items-center justify-center">
                          <FileText className="w-7 h-7 text-[#1a1a1a]" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-white">Sertifikat Analisa Kepribadian</h3>
                          <p className="text-gray-400 text-sm">Download sertifikat hasil analisis Anda dalam format PDF</p>
                        </div>
                      </div>
                      <a 
                        href={`${BACKEND_URL}/api/certificates/generate-newme/${user?._id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex"
                      >
                        <Button className="bg-yellow-400 text-black hover:bg-yellow-500">
                          <FileText className="w-4 h-4 mr-2" /> Download Sertifikat
                        </Button>
                      </a>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-8 text-center">
                  <Trophy className="w-16 h-16 text-yellow-400/30 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">Belum Ada Hasil Premium</h3>
                  <p className="text-gray-400 mb-4">Selesaikan Test Premium untuk melihat hasil analisis lengkap Anda</p>
                  <Link to="/user-test">
                    <Button className="bg-yellow-400 text-black hover:bg-yellow-500">
                      <Play className="w-4 h-4 mr-2" /> Mulai Test Premium
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* 5 Elements Tab */}
        {activeTab === 'elements' && (
          <div className="space-y-6">
            <Card className="bg-gradient-to-br from-yellow-400/20 to-yellow-600/10 border-yellow-400/30">
              <CardContent className="p-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center">
                    <Info className="w-6 h-6 text-[#1a1a1a]" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Metodologi 5 Element</h2>
                    <p className="text-gray-400">Sistem kepribadian berdasarkan filosofi 5 elemen</p>
                  </div>
                </div>
                <p className="text-gray-300">
                  NEWMECLASS menggunakan pendekatan 5 Element yang menggabungkan filosofi timur dengan psikologi modern. 
                  Setiap orang memiliki kombinasi unik dari 5 elemen yang membentuk kepribadian, bakat, dan potensi mereka.
                </p>
              </CardContent>
            </Card>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {fiveElements.map((element) => {
                const Icon = element.icon;
                return (
                  <Card key={element.name} className={`bg-[#2a2a2a] border-l-4 border-l-${element.textColor.replace('text-', '')}`} style={{borderLeftColor: element.textColor === 'text-green-400' ? '#4ade80' : element.textColor === 'text-red-400' ? '#f87171' : element.textColor === 'text-yellow-400' ? '#facc15' : element.textColor === 'text-gray-300' ? '#d1d5db' : '#60a5fa'}}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${element.color} flex items-center justify-center`}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <CardTitle className={`${element.textColor}`}>{element.name}</CardTitle>
                          <p className="text-gray-400 text-sm">{element.label}</p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-gray-300 text-sm">{element.description}</p>
                      
                      <div>
                        <p className="text-gray-400 text-xs mb-1">Ciri-ciri:</p>
                        <div className="flex flex-wrap gap-1">
                          {element.traits.map((trait, idx) => (
                            <span key={idx} className={`text-xs px-2 py-1 rounded ${element.bgColor} ${element.textColor}`}>
                              {trait}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-gray-400 text-xs mb-1">Karir Cocok:</p>
                        <p className="text-gray-300 text-xs">{element.careers.join(', ')}</p>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* 9 Result Categories */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white">9 Kategori Hasil Test</CardTitle>
                <CardDescription className="text-gray-400">
                  Kombinasi kepribadian (Introvert/Extrovert/Ambivert) dengan elemen dominan
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <h4 className="text-yellow-400 font-semibold">EXTROVERT</h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-gray-300"><span className="text-green-400">eK</span> - Extrovert-Kayu: Si Kreatif Ekspresif</p>
                      <p className="text-gray-300"><span className="text-red-400">eA</span> - Extrovert-Api: Si Perasa Hangat</p>
                      <p className="text-gray-300"><span className="text-yellow-400">eT</span> - Extrovert-Tanah: Si Stabil Terbuka</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-purple-400 font-semibold">INTROVERT</h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-gray-300"><span className="text-green-400">iK</span> - Introvert-Kayu: Si Kreatif Mendalam</p>
                      <p className="text-gray-300"><span className="text-red-400">iA</span> - Introvert-Api: Si Perasa Dalam</p>
                      <p className="text-gray-300"><span className="text-yellow-400">iT</span> - Introvert-Tanah: Si Stabil Tenang</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-blue-400 font-semibold">AMBIVERT</h4>
                    <div className="space-y-1 text-sm">
                      <p className="text-gray-300"><span className="text-gray-400">aL</span> - Ambivert-Logam: Si Tegas Seimbang</p>
                      <p className="text-gray-300"><span className="text-blue-400">aAi</span> - Ambivert-Air: Si Adaptif Seimbang</p>
                      <p className="text-gray-300"><span className="text-yellow-400">aT</span> - Ambivert-Tanah: Si Stabil Fleksibel</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Test Tab */}
        {activeTab === 'test' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Free Test */}
            <Card className="bg-[#2a2a2a] border-green-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Sparkles className="w-5 h-5 mr-2 text-green-400" /> Test Gratis
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Test dasar untuk mengenal potensi Anda
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${getStatusBadge(user?.freeTestStatus).color}`}>
                    {getStatusBadge(user?.freeTestStatus).label}
                  </span>
                </div>
                
                {user?.freeTestStatus === 'completed' ? (
                  <div className="bg-green-400/10 border border-green-400/30 rounded-lg p-4">
                    <div className="flex items-center text-green-400">
                      <CheckCircle className="w-5 h-5 mr-2" />
                      <span>Test Gratis sudah selesai!</span>
                    </div>
                  </div>
                ) : (
                  <Link to="/user-test?type=free">
                    <Button className="w-full bg-green-500 text-white hover:bg-green-600">
                      <Play className="w-4 h-4 mr-2" />
                      {user?.freeTestStatus === 'in_progress' ? 'Lanjutkan Test' : 'Mulai Test Gratis'}
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>

            {/* Paid Test */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Award className="w-5 h-5 mr-2 text-yellow-400" /> Test Premium
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Test lengkap dengan analisis mendalam
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${getStatusBadge(user?.paidTestStatus).color}`}>
                    {getStatusBadge(user?.paidTestStatus).label}
                  </span>
                </div>
                
                {user?.paidTestStatus === 'completed' ? (
                  <div className="bg-green-400/10 border border-green-400/30 rounded-lg p-4">
                    <div className="flex items-center text-green-400">
                      <CheckCircle className="w-5 h-5 mr-2" />
                      <span>Test Premium sudah selesai!</span>
                    </div>
                    {user?.certificateNumber && (
                      <p className="text-gray-400 text-sm mt-2">
                        No. Sertifikat: {user?.certificateNumber}
                      </p>
                    )}
                  </div>
                ) : needsPayment ? (
                  <div className="space-y-3">
                    <div className="bg-yellow-400/10 border border-yellow-400/30 rounded-lg p-4">
                      <div className="flex items-center text-yellow-400">
                        <Lock className="w-5 h-5 mr-2" />
                        <span>Perlu pembayaran untuk mengakses</span>
                      </div>
                    </div>
                    <Button 
                      onClick={() => setActiveTab('payment')}
                      className="w-full bg-yellow-400 text-black hover:bg-yellow-500"
                    >
                      <CreditCard className="w-4 h-4 mr-2" /> Lakukan Pembayaran
                    </Button>
                  </div>
                ) : (
                  <Link to="/user-test?type=paid">
                    <Button className="w-full bg-yellow-400 text-black hover:bg-yellow-500">
                      <Play className="w-4 h-4 mr-2" />
                      {user?.paidTestStatus === 'in_progress' ? 'Lanjutkan Test' : 'Mulai Test Premium'}
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Payment Tab */}
        {activeTab === 'payment' && (
          <div className="space-y-6">
            {user?.paymentStatus === 'approved' ? (
              <Card className="bg-[#2a2a2a] border-green-400/20">
                <CardContent className="p-6">
                  <div className="text-center">
                    <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Pembayaran Disetujui!</h3>
                    <p className="text-gray-400">Anda sudah dapat mengakses Test Premium.</p>
                    <Button 
                      onClick={() => setActiveTab('test')}
                      className="mt-4 bg-yellow-400 text-black hover:bg-yellow-500"
                    >
                      Mulai Test Premium
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ) : user?.paymentStatus === 'pending' ? (
              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-6">
                  <div className="text-center">
                    <Clock className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Menunggu Verifikasi</h3>
                    <p className="text-gray-400">Bukti pembayaran Anda sedang diverifikasi oleh admin. Mohon tunggu 1x24 jam.</p>
                  </div>
                </CardContent>
              </Card>
            ) : user?.paymentStatus === 'rejected' ? (
              <Card className="bg-[#2a2a2a] border-red-400/20">
                <CardContent className="p-6">
                  <div className="text-center mb-6">
                    <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Pembayaran Ditolak</h3>
                    <p className="text-gray-400">Silakan upload ulang bukti pembayaran yang valid.</p>
                  </div>
                </CardContent>
              </Card>
            ) : null}

            {(user?.paymentStatus === 'unpaid' || user?.paymentStatus === 'rejected') && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Payment Info */}
                <Card className="bg-[#2a2a2a] border-yellow-400/20">
                  <CardHeader>
                    <CardTitle className="text-white">Informasi Pembayaran</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="bg-[#1a1a1a] rounded-lg p-4 text-center">
                      <p className="text-gray-400 text-sm">Biaya Test Premium</p>
                      <p className="text-3xl font-bold text-yellow-400">{formatPrice(settings?.paymentAmount)}</p>
                    </div>

                    {/* Payment Method Selection */}
                    <div>
                      <p className="text-gray-400 text-sm mb-2">Pilih Metode Pembayaran:</p>
                      <div className="grid grid-cols-2 gap-3">
                        <button
                          onClick={() => setPaymentMethod('bank')}
                          className={`p-4 rounded-lg border-2 transition ${
                            paymentMethod === 'bank' 
                              ? 'border-yellow-400 bg-yellow-400/10' 
                              : 'border-gray-600 hover:border-gray-500'
                          }`}
                        >
                          <CreditCard className={`w-8 h-8 mx-auto mb-2 ${paymentMethod === 'bank' ? 'text-yellow-400' : 'text-gray-400'}`} />
                          <p className={`text-sm ${paymentMethod === 'bank' ? 'text-yellow-400' : 'text-gray-400'}`}>Transfer Bank</p>
                        </button>
                        <button
                          onClick={() => setPaymentMethod('ewallet')}
                          className={`p-4 rounded-lg border-2 transition ${
                            paymentMethod === 'ewallet' 
                              ? 'border-yellow-400 bg-yellow-400/10' 
                              : 'border-gray-600 hover:border-gray-500'
                          }`}
                        >
                          <div className={`w-8 h-8 mx-auto mb-2 flex items-center justify-center ${paymentMethod === 'ewallet' ? 'text-yellow-400' : 'text-gray-400'}`}>
                            <span className="text-xs font-bold">E-Wallet</span>
                          </div>
                          <p className={`text-sm ${paymentMethod === 'ewallet' ? 'text-yellow-400' : 'text-gray-400'}`}>E-Wallet / QRIS</p>
                        </button>
                      </div>
                    </div>

                    {/* Bank Transfer Info */}
                    {paymentMethod === 'bank' && (
                      <div className="bg-[#1a1a1a] rounded-lg p-4 space-y-3">
                        <p className="text-yellow-400 font-semibold">Transfer ke:</p>
                        <div>
                          <p className="text-gray-400 text-sm">Bank</p>
                          <p className="text-white font-semibold">{settings?.bankName || 'BCA'}</p>
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">No. Rekening</p>
                          <div className="flex items-center gap-2">
                            <p className="text-white font-mono text-lg">{settings?.bankAccountNumber || '1234567890'}</p>
                            <button 
                              onClick={() => {
                                navigator.clipboard.writeText(settings?.bankAccountNumber || '1234567890');
                                toast({ title: 'Disalin!', description: 'No. rekening berhasil disalin' });
                              }}
                              className="text-yellow-400 hover:text-yellow-300"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <div>
                          <p className="text-gray-400 text-sm">Atas Nama</p>
                          <p className="text-white">{settings?.bankAccountName || 'NEWME CLASS'}</p>
                        </div>
                        {settings?.paymentInstructions && (
                          <div className="mt-3 pt-3 border-t border-gray-700">
                            <p className="text-gray-400 text-sm whitespace-pre-line">{settings.paymentInstructions}</p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* E-Wallet / QRIS Info */}
                    {paymentMethod === 'ewallet' && (
                      <div className="bg-[#1a1a1a] rounded-lg p-4 space-y-3">
                        <p className="text-yellow-400 font-semibold">Pembayaran E-Wallet / QRIS</p>
                        <p className="text-gray-400 text-sm">
                          Lakukan pembayaran via E-Wallet (GoPay, OVO, DANA, ShopeePay) atau QRIS ke:
                        </p>
                        <div>
                          <p className="text-gray-400 text-sm">Nama Merchant</p>
                          <p className="text-white font-semibold">{settings?.bankAccountName || 'NEWME CLASS'}</p>
                        </div>
                        {settings?.paymentInstructions && (
                          <div className="mt-3 pt-3 border-t border-gray-700">
                            <p className="text-gray-400 text-sm whitespace-pre-line">{settings.paymentInstructions}</p>
                          </div>
                        )}
                        <div className="bg-yellow-400/10 border border-yellow-400/30 rounded-lg p-3">
                          <p className="text-yellow-400 text-xs">
                            Setelah transfer, upload screenshot/foto bukti pembayaran di bawah
                          </p>
                        </div>
                      </div>
                  </CardContent>
                </Card>

                {/* Upload Proof */}
                <Card className="bg-[#2a2a2a] border-yellow-400/20">
                  <CardHeader>
                    <CardTitle className="text-white">Upload Bukti Pembayaran</CardTitle>
                    <CardDescription className="text-gray-400">
                      Upload screenshot atau foto bukti transfer Anda
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-[#1a1a1a] hover:bg-[#252525] transition">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                          <Upload className="w-10 h-10 mb-3 text-gray-400" />
                          <p className="text-sm text-gray-400">
                            {proofFile ? proofFile.name : 'Klik untuk upload'}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">PNG, JPG, JPEG (Max. 5MB)</p>
                        </div>
                        <input
                          type="file"
                          className="hidden"
                          accept="image/png,image/jpeg,image/jpg"
                          onChange={(e) => setProofFile(e.target.files[0])}
                        />
                      </label>
                    </div>

                    {proofFile && (
                      <div className="relative">
                        <img 
                          src={URL.createObjectURL(proofFile)} 
                          alt="Preview" 
                          className="max-h-40 mx-auto rounded-lg"
                        />
                        <button 
                          onClick={() => setProofFile(null)}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    )}

                    <Button
                      onClick={handleUploadProof}
                      disabled={!proofFile || uploadingProof}
                      className="w-full bg-yellow-400 text-black hover:bg-yellow-500"
                    >
                      {uploadingProof ? (
                        <span className="flex items-center">
                          <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2"></div>
                          Mengupload...
                        </span>
                      ) : (
                        <span className="flex items-center">
                          <Upload className="w-4 h-4 mr-2" /> Upload Bukti Pembayaran
                        </span>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* Referral Tab */}
        {activeTab === 'referral' && (
          <div className="space-y-6">
            {/* Referral Link Card */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Gift className="w-5 h-5 mr-2 text-yellow-400" /> Link Referral Anda
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-[#1a1a1a] rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Kode Referral:</p>
                  <p className="text-2xl font-bold text-yellow-400 font-mono">{user?.myReferralCode}</p>
                </div>

                <div className="bg-[#1a1a1a] rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Link Referral:</p>
                  <div className="flex items-center gap-2">
                    <input 
                      type="text"
                      readOnly
                      value={`${window.location.origin}/register?ref=${user?.myReferralCode}`}
                      className="flex-1 bg-transparent text-white text-sm truncate"
                    />
                    <Button onClick={handleCopyReferral} size="sm" variant="outline" className="border-yellow-400/50 text-yellow-400">
                      <Copy className="w-4 h-4" />
                    </Button>
                    <Button onClick={handleShareReferral} size="sm" className="bg-yellow-400 text-black hover:bg-yellow-500">
                      <Share2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#1a1a1a] rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-yellow-400">{user?.referralCount || 0}</p>
                    <p className="text-gray-400 text-sm">Total Referral</p>
                  </div>
                  <div className="bg-[#1a1a1a] rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-green-400">{formatPrice(user?.referralBonus)}</p>
                    <p className="text-gray-400 text-sm">Total Bonus</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Referral Info */}
            {referralSettings && (
              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardHeader>
                  <CardTitle className="text-white">{referralSettings.title}</CardTitle>
                  <CardDescription className="text-gray-400">{referralSettings.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-[#1a1a1a] rounded-lg p-4">
                    <p className="text-yellow-400 font-semibold mb-2">Keuntungan:</p>
                    <ul className="space-y-2">
                      {referralSettings.benefits?.map((benefit, idx) => (
                        <li key={idx} className="flex items-center text-gray-300">
                          <CheckCircle className="w-4 h-4 mr-2 text-green-400" />
                          {benefit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="bg-[#1a1a1a] rounded-lg p-4">
                    <p className="text-yellow-400 font-semibold mb-2">Syarat & Ketentuan:</p>
                    <p className="text-gray-400 text-sm whitespace-pre-line">{referralSettings.termsAndConditions}</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes marquee {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
        .animate-marquee {
          animation: marquee 20s linear infinite;
        }
      `}</style>
    </div>
  );
};

export default UserDashboard;
