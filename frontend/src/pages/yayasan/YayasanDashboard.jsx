import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Building2, Users, CreditCard, Gift, LogOut, Settings, 
  TrendingUp, Copy, Share2, Edit, Save, CheckCircle, Clock,
  ChevronRight, AlertCircle, DollarSign, Eye, Search
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const YayasanDashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [yayasan, setYayasan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [editingPrice, setEditingPrice] = useState(false);
  const [newPrice, setNewPrice] = useState(50000);
  const [savingPrice, setSavingPrice] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('yayasan_token');
      if (!token) {
        navigate('/yayasan/login');
        return;
      }

      const response = await axios.get(`${API_URL}/api/yayasan/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setYayasan(response.data);
      setNewPrice(response.data.referralPrice || 50000);
      await loadDashboardData(token);
    } catch (error) {
      localStorage.removeItem('yayasan_token');
      navigate('/yayasan/login');
    } finally {
      setLoading(false);
    }
  };

  const loadDashboardData = async (token) => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        axios.get(`${API_URL}/api/yayasan/dashboard/stats`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/yayasan/users`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setStats(statsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('yayasan_token');
    toast({
      title: 'Logout Berhasil',
      description: 'Anda telah keluar dari dashboard'
    });
    navigate('/yayasan/login');
  };

  const handleCopyReferral = () => {
    const referralLink = `${window.location.origin}/register?ref=${yayasan?.referralCode}`;
    navigator.clipboard.writeText(referralLink);
    toast({
      title: 'Berhasil',
      description: 'Link referral berhasil disalin!'
    });
  };

  const handleShareReferral = async () => {
    const referralLink = `${window.location.origin}/register?ref=${yayasan?.referralCode}`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Daftar Test NEWME CLASS - ${yayasan?.name}`,
          text: `Daftar di NEWME CLASS menggunakan kode referral dari ${yayasan?.name}`,
          url: referralLink
        });
      } catch (error) {
        handleCopyReferral();
      }
    } else {
      handleCopyReferral();
    }
  };

  const handleUpdatePrice = async () => {
    setSavingPrice(true);
    try {
      const token = localStorage.getItem('yayasan_token');
      await axios.put(
        `${API_URL}/api/yayasan/referral-price`,
        { referralPrice: newPrice },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setYayasan(prev => ({ ...prev, referralPrice: newPrice }));
      setEditingPrice(false);
      toast({
        title: 'Berhasil',
        description: 'Harga referral berhasil diupdate'
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Gagal mengupdate harga',
        variant: 'destructive'
      });
    } finally {
      setSavingPrice(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(price || 0);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'unpaid': { label: 'Belum Bayar', color: 'bg-red-400/20 text-red-400' },
      'pending': { label: 'Pending', color: 'bg-yellow-400/20 text-yellow-400' },
      'approved': { label: 'Lunas', color: 'bg-green-400/20 text-green-400' },
      'completed': { label: 'Selesai', color: 'bg-green-400/20 text-green-400' },
      'not_started': { label: 'Belum Mulai', color: 'bg-gray-400/20 text-gray-400' },
      'in_progress': { label: 'Berlangsung', color: 'bg-purple-400/20 text-purple-400' }
    };
    return statusMap[status] || { label: status, color: 'bg-gray-400/20 text-gray-400' };
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = !searchTerm || 
      user.fullName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' ||
      (filterStatus === 'paid' && user.paymentStatus === 'approved') ||
      (filterStatus === 'pending' && user.paymentStatus === 'pending') ||
      (filterStatus === 'completed' && user.paidTestStatus === 'completed');
    
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a]" data-testid="yayasan-dashboard">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center">
              <Building2 className="w-7 h-7 text-[#1a1a1a]" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{yayasan?.name}</h1>
              <p className="text-gray-400">Dashboard Yayasan</p>
              {yayasan?.isVerified && (
                <span className="inline-flex items-center px-2 py-0.5 text-xs bg-green-400/20 text-green-400 rounded">
                  <CheckCircle className="w-3 h-3 mr-1" /> Terverifikasi
                </span>
              )}
            </div>
          </div>
          <Button onClick={handleLogout} variant="outline" className="border-red-400/50 text-red-400">
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
            { id: 'users', label: 'Pengguna', icon: Users },
            { id: 'referral', label: 'Referral', icon: Gift },
            { id: 'settings', label: 'Pengaturan', icon: Settings }
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
                      <p className="text-gray-400 text-sm">Total Pengguna</p>
                      <p className="text-3xl font-bold text-white">{stats?.totalUsers || 0}</p>
                    </div>
                    <Users className="w-8 h-8 text-yellow-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Sudah Bayar</p>
                      <p className="text-3xl font-bold text-green-400">{stats?.paidUsers || 0}</p>
                    </div>
                    <CreditCard className="w-8 h-8 text-green-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Test Selesai</p>
                      <p className="text-3xl font-bold text-purple-400">{stats?.completedTests || 0}</p>
                    </div>
                    <CheckCircle className="w-8 h-8 text-purple-400/30" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Total Pendapatan</p>
                      <p className="text-2xl font-bold text-yellow-400">{formatPrice(stats?.totalEarnings)}</p>
                    </div>
                    <DollarSign className="w-8 h-8 text-yellow-400/30" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Referral Info */}
            <Card className="bg-gradient-to-r from-yellow-400/10 to-yellow-600/5 border-yellow-400/30">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div>
                    <p className="text-gray-400 text-sm">Kode Referral Anda</p>
                    <p className="text-2xl font-bold text-yellow-400 font-mono">{yayasan?.referralCode}</p>
                    <p className="text-gray-400 text-sm mt-1">Harga: {formatPrice(yayasan?.referralPrice)}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleCopyReferral} variant="outline" className="border-yellow-400/50 text-yellow-400">
                      <Copy className="w-4 h-4 mr-2" /> Salin
                    </Button>
                    <Button onClick={handleShareReferral} className="bg-yellow-400 text-black hover:bg-yellow-500">
                      <Share2 className="w-4 h-4 mr-2" /> Bagikan
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Users */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white">Pengguna Terbaru</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats?.recentUsers?.slice(0, 5).map((user, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-[#1a1a1a] rounded-lg">
                      <div>
                        <p className="text-white font-medium">{user.fullName}</p>
                        <p className="text-gray-400 text-sm">{user.email}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${getStatusBadge(user.paymentStatus).color}`}>
                        {getStatusBadge(user.paymentStatus).label}
                      </span>
                    </div>
                  ))}
                  {(!stats?.recentUsers || stats.recentUsers.length === 0) && (
                    <p className="text-gray-400 text-center py-4">Belum ada pengguna</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* Search & Filter */}
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Cari pengguna..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 bg-[#2a2a2a] border-yellow-400/30 text-white"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 bg-[#2a2a2a] border border-yellow-400/30 rounded-md text-white"
              >
                <option value="all">Semua Status</option>
                <option value="paid">Sudah Bayar</option>
                <option value="pending">Pending</option>
                <option value="completed">Test Selesai</option>
              </select>
            </div>

            {/* Users Table */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-yellow-400/20">
                        <th className="text-left py-3 px-4 text-gray-400">Nama</th>
                        <th className="text-left py-3 px-4 text-gray-400">Kontak</th>
                        <th className="text-left py-3 px-4 text-gray-400">Pembayaran</th>
                        <th className="text-left py-3 px-4 text-gray-400">Test</th>
                        <th className="text-left py-3 px-4 text-gray-400">Tanggal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((user, idx) => (
                        <tr key={idx} className="border-b border-gray-700 hover:bg-[#1a1a1a]">
                          <td className="py-3 px-4">
                            <p className="text-white font-medium">{user.fullName}</p>
                            <p className="text-gray-400 text-xs">{user.province}, {user.city}</p>
                          </td>
                          <td className="py-3 px-4">
                            <p className="text-gray-300 text-sm">{user.email}</p>
                            <p className="text-gray-400 text-xs">{user.whatsapp}</p>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded text-xs ${getStatusBadge(user.paymentStatus).color}`}>
                              {getStatusBadge(user.paymentStatus).label}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded text-xs ${getStatusBadge(user.paidTestStatus).color}`}>
                              {getStatusBadge(user.paidTestStatus).label}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-400 text-sm">
                            {new Date(user.createdAt).toLocaleDateString('id-ID')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {filteredUsers.length === 0 && (
                  <div className="text-center py-8">
                    <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">Tidak ada pengguna ditemukan</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Referral Tab */}
        {activeTab === 'referral' && (
          <div className="space-y-6">
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Gift className="w-5 h-5 text-yellow-400" /> Link Referral Anda
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-[#1a1a1a] rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Kode Referral:</p>
                  <p className="text-2xl font-bold text-yellow-400 font-mono">{yayasan?.referralCode}</p>
                </div>

                <div className="bg-[#1a1a1a] rounded-lg p-4">
                  <p className="text-gray-400 text-sm mb-2">Link Referral:</p>
                  <div className="flex items-center gap-2">
                    <input 
                      type="text"
                      readOnly
                      value={`${window.location.origin}/register?ref=${yayasan?.referralCode}`}
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
                    <p className="text-3xl font-bold text-yellow-400">{stats?.totalUsers || 0}</p>
                    <p className="text-gray-400 text-sm">Total Referral</p>
                  </div>
                  <div className="bg-[#1a1a1a] rounded-lg p-4 text-center">
                    <p className="text-3xl font-bold text-green-400">{formatPrice(stats?.totalEarnings)}</p>
                    <p className="text-gray-400 text-sm">Total Pendapatan</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* Edit Price */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-yellow-400" /> Harga Test Referral
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Atur harga test untuk pengguna yang mendaftar menggunakan link referral Anda
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-yellow-400/10 border border-yellow-400/30 rounded-lg p-4">
                  <p className="text-yellow-400 text-sm">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    Anda dapat mengatur harga test khusus untuk pengguna yang mendaftar melalui link referral Anda.
                  </p>
                </div>

                {editingPrice ? (
                  <div className="space-y-4">
                    <div>
                      <Label className="text-gray-400">Harga Test (Rp)</Label>
                      <Input
                        type="number"
                        value={newPrice}
                        onChange={(e) => setNewPrice(parseInt(e.target.value) || 0)}
                        className="bg-[#1a1a1a] border-yellow-400/20 text-white"
                        min="25000"
                        step="5000"
                      />
                      <p className="text-gray-400 text-xs mt-1">Minimum: Rp 25.000</p>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        onClick={handleUpdatePrice} 
                        disabled={savingPrice}
                        className="bg-yellow-400 text-black hover:bg-yellow-500"
                      >
                        {savingPrice ? (
                          <span className="flex items-center">
                            <div className="w-4 h-4 border-2 border-black border-t-transparent rounded-full animate-spin mr-2"></div>
                            Menyimpan...
                          </span>
                        ) : (
                          <><Save className="w-4 h-4 mr-2" /> Simpan</>
                        )}
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={() => {
                          setEditingPrice(false);
                          setNewPrice(yayasan?.referralPrice || 50000);
                        }}
                        className="border-gray-600 text-gray-400"
                      >
                        Batal
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-sm">Harga Saat Ini</p>
                      <p className="text-2xl font-bold text-yellow-400">{formatPrice(yayasan?.referralPrice)}</p>
                    </div>
                    <Button 
                      onClick={() => setEditingPrice(true)}
                      variant="outline"
                      className="border-yellow-400/50 text-yellow-400"
                    >
                      <Edit className="w-4 h-4 mr-2" /> Edit Harga
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Profile Info */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white">Informasi Yayasan</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-sm">Nama Yayasan</p>
                    <p className="text-white">{yayasan?.name}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Email</p>
                    <p className="text-white">{yayasan?.email}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Telepon</p>
                    <p className="text-white">{yayasan?.phone || '-'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Status</p>
                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${yayasan?.isVerified ? 'bg-green-400/20 text-green-400' : 'bg-yellow-400/20 text-yellow-400'}`}>
                      {yayasan?.isVerified ? 'Terverifikasi' : 'Pending Verifikasi'}
                    </span>
                  </div>
                  <div className="md:col-span-2">
                    <p className="text-gray-400 text-sm">Alamat</p>
                    <p className="text-white">{yayasan?.address || '-'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default YayasanDashboard;
