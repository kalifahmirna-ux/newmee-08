import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Building2, Users, Gift, LogOut, Settings,
  TrendingUp, Copy, Edit, Save, CheckCircle,
  DollarSign, Eye, Search, Wallet, ArrowDownToLine,
  FileText, CreditCard
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (n) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n || 0);

const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
  { id: 'users',     label: 'Pengguna',  icon: Users },
  { id: 'results',   label: 'Hasil Test', icon: FileText },
  { id: 'wallet',    label: 'Wallet',     icon: Wallet },
  { id: 'settings',  label: 'Pengaturan', icon: Settings },
];

export default function YayasanDashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [yayasan, setYayasan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');

  // Data state
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [testResults, setTestResults] = useState([]);
  const [wallet, setWallet] = useState({ balance: 0, transactions: [] });

  // Price editing
  const [editingPrice, setEditingPrice] = useState(false);
  const [newPrice, setNewPrice] = useState(100000);
  const [savingPrice, setSavingPrice] = useState(false);

  // Users filter
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // Withdrawal form
  const [withdrawForm, setWithdrawForm] = useState({ amount: '', bankName: '', bankAccount: '', accountName: '' });
  const [withdrawing, setWithdrawing] = useState(false);

  const token = () => localStorage.getItem('yayasan_token');
  const headers = () => ({ Authorization: `Bearer ${token()}` });

  useEffect(() => { checkAuth(); }, []);

  const checkAuth = async () => {
    try {
      if (!token()) { navigate('/yayasan/login'); return; }
      const res = await axios.get(`${API_URL}/api/yayasan/me`, { headers: headers() });
      setYayasan(res.data);
      setNewPrice(res.data.referralPrice || 100000);
      await loadAll();
    } catch {
      localStorage.removeItem('yayasan_token');
      navigate('/yayasan/login');
    } finally { setLoading(false); }
  };

  const loadAll = async () => {
    try {
      const [statsRes, usersRes, resultsRes, walletRes] = await Promise.allSettled([
        axios.get(`${API_URL}/api/yayasan/dashboard/stats`, { headers: headers() }),
        axios.get(`${API_URL}/api/yayasan/users`, { headers: headers() }),
        axios.get(`${API_URL}/api/yayasan/test-results`, { headers: headers() }),
        axios.get(`${API_URL}/api/yayasan/wallet`, { headers: headers() }),
      ]);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (usersRes.status === 'fulfilled') setUsers(usersRes.value.data);
      if (resultsRes.status === 'fulfilled') setTestResults(resultsRes.value.data);
      if (walletRes.status === 'fulfilled') setWallet(walletRes.value.data);
    } catch (e) { console.error(e); }
  };

  const handleLogout = () => {
    localStorage.removeItem('yayasan_token');
    navigate('/yayasan/login');
  };

  const handleCopyReferral = () => {
    const link = `${window.location.origin}/register?ref=${yayasan?.referralCode}`;
    navigator.clipboard.writeText(link);
    toast({ title: 'Tersalin!', description: 'Link referral berhasil disalin' });
  };

  const handleUpdatePrice = async () => {
    if (!newPrice || newPrice < 10000) {
      toast({ title: 'Error', description: 'Harga minimal Rp 10.000', variant: 'destructive' }); return;
    }
    setSavingPrice(true);
    try {
      await axios.put(`${API_URL}/api/yayasan/referral-price`, { referralPrice: Number(newPrice) }, { headers: headers() });
      setYayasan(prev => ({ ...prev, referralPrice: Number(newPrice) }));
      setEditingPrice(false);
      toast({ title: 'Berhasil', description: 'Harga referral diupdate' });
    } catch (e) {
      toast({ title: 'Error', description: e.response?.data?.detail || 'Gagal update harga', variant: 'destructive' });
    } finally { setSavingPrice(false); }
  };

  const handleWithdraw = async () => {
    const { amount, bankName, bankAccount, accountName } = withdrawForm;
    if (!amount || !bankName || !bankAccount || !accountName) {
      toast({ title: 'Error', description: 'Lengkapi semua data penarikan', variant: 'destructive' }); return;
    }
    setWithdrawing(true);
    try {
      await axios.post(`${API_URL}/api/yayasan/wallet/withdraw`,
        { amount: Number(amount), bankName, bankAccount, accountName },
        { headers: headers() }
      );
      toast({ title: 'Berhasil!', description: 'Permintaan penarikan diajukan, admin akan memproses' });
      setWithdrawForm({ amount: '', bankName: '', bankAccount: '', accountName: '' });
      await loadAll();
    } catch (e) {
      toast({ title: 'Error', description: e.response?.data?.detail || 'Gagal ajukan penarikan', variant: 'destructive' });
    } finally { setWithdrawing(false); }
  };

  const filteredUsers = users.filter(u => {
    const s = !searchTerm || u.fullName?.toLowerCase().includes(searchTerm.toLowerCase()) || u.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const f = filterStatus === 'all' ||
      (filterStatus === 'paid' && u.paymentStatus === 'approved') ||
      (filterStatus === 'pending' && u.paymentStatus === 'pending') ||
      (filterStatus === 'completed' && u.paidTestStatus === 'completed');
    return s && f;
  });

  if (loading) return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1a1a] to-[#2a2a2a] flex items-center justify-center">
      <div className="w-12 h-12 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const referralLink = `${window.location.origin}/register?ref=${yayasan?.referralCode}`;

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
              <p className="text-gray-400 text-sm">Dashboard Yayasan</p>
              {yayasan?.isVerified && (
                <span className="inline-flex items-center px-2 py-0.5 text-xs bg-green-400/20 text-green-400 rounded mt-1">
                  <CheckCircle className="w-3 h-3 mr-1" /> Terverifikasi
                </span>
              )}
            </div>
          </div>
          <Button onClick={handleLogout} variant="outline" className="border-red-400/50 text-red-400 hover:bg-red-400/10">
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {TABS.map(tab => (
            <Button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              data-testid={`tab-${tab.id}`}
              className={activeTab === tab.id
                ? 'bg-yellow-400 text-black hover:bg-yellow-500 whitespace-nowrap'
                : 'border border-yellow-400/30 text-gray-400 bg-transparent hover:bg-yellow-400/10 whitespace-nowrap'}
            >
              <tab.icon className="w-4 h-4 mr-2" /> {tab.label}
            </Button>
          ))}
        </div>

        {/* ═══ DASHBOARD TAB ═══ */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Total Pengguna', val: stats?.totalUsers || 0, icon: Users, color: 'text-yellow-400' },
                { label: 'Sudah Bayar', val: stats?.paidUsers || 0, icon: CreditCard, color: 'text-green-400' },
                { label: 'Test Selesai', val: stats?.completedTests || 0, icon: CheckCircle, color: 'text-purple-400' },
                { label: 'Saldo Wallet', val: fmt(wallet.balance), icon: Wallet, color: 'text-blue-400', isText: true },
              ].map((s, i) => (
                <Card key={i} className="bg-[#2a2a2a] border-yellow-400/20">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <p className="text-gray-400 text-xs">{s.label}</p>
                      <p className={`text-2xl font-bold ${s.color} ${s.isText ? 'text-base mt-1' : ''}`}>{s.val}</p>
                    </div>
                    <s.icon className={`w-8 h-8 ${s.color} opacity-30`} />
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Referral Link */}
            <Card className="bg-[#2a2a2a] border-yellow-400/30">
              <CardHeader><CardTitle className="text-white text-sm">Link Referral Yayasan</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="flex gap-2">
                  <Input value={referralLink} readOnly className="bg-[#1a1a1a] text-gray-300 text-xs flex-1" />
                  <Button onClick={handleCopyReferral} className="bg-yellow-400 text-black hover:bg-yellow-500 shrink-0">
                    <Copy className="w-4 h-4 mr-1" /> Salin
                  </Button>
                </div>
                <div className="flex gap-2 text-xs">
                  <span className="text-gray-400">Kode:</span>
                  <code className="text-yellow-400 font-bold">{yayasan?.referralCode}</code>
                  <span className="text-gray-400 ml-3">Harga Referral:</span>
                  <span className="text-green-400 font-bold">{fmt(yayasan?.referralPrice || 100000)}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ═══ PENGGUNA TAB ═══ */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            <div className="flex gap-3 flex-wrap">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input value={searchTerm} onChange={e => setSearchTerm(e.target.value)}
                  placeholder="Cari nama / email..." className="pl-9 bg-[#2a2a2a] text-white border-yellow-400/30" />
              </div>
              <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                className="bg-[#2a2a2a] text-white border border-yellow-400/30 rounded px-3 text-sm">
                <option value="all">Semua</option>
                <option value="paid">Sudah Bayar</option>
                <option value="pending">Pending</option>
                <option value="completed">Test Selesai</option>
              </select>
            </div>

            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-yellow-400/20 text-gray-400">
                        <th className="text-left py-3 px-4">Nama</th>
                        <th className="text-left py-3 px-4">Email</th>
                        <th className="text-left py-3 px-4">Status Bayar</th>
                        <th className="text-left py-3 px-4">Status Test</th>
                        <th className="text-left py-3 px-4">Bergabung</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.length === 0 ? (
                        <tr><td colSpan={5} className="text-center text-gray-400 py-8">Belum ada pengguna</td></tr>
                      ) : filteredUsers.map((u, i) => (
                        <tr key={i} className="border-b border-yellow-400/10 hover:bg-[#333]">
                          <td className="py-3 px-4 text-white font-medium">{u.fullName}</td>
                          <td className="py-3 px-4 text-gray-400 text-xs">{u.email}</td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              u.paymentStatus === 'approved' ? 'bg-green-400/20 text-green-400' :
                              u.paymentStatus === 'pending' ? 'bg-yellow-400/20 text-yellow-400' :
                              'bg-red-400/20 text-red-400'}`}>
                              {u.paymentStatus === 'approved' ? 'Lunas' : u.paymentStatus === 'pending' ? 'Pending' : 'Belum Bayar'}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              u.paidTestStatus === 'completed' ? 'bg-purple-400/20 text-purple-400' : 'bg-gray-400/20 text-gray-400'}`}>
                              {u.paidTestStatus === 'completed' ? 'Selesai' : 'Belum'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-400 text-xs">
                            {u.createdAt ? new Date(u.createdAt).toLocaleDateString('id-ID') : '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ═══ HASIL TEST TAB ═══ */}
        {activeTab === 'results' && (
          <div className="space-y-4">
            <p className="text-gray-400 text-sm">Hasil test premium dari pengguna yang menggunakan link referral Anda.</p>
            {testResults.length === 0 ? (
              <Card className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="py-12 text-center text-gray-400">
                  Belum ada hasil test dari pengguna referral Anda.
                </CardContent>
              </Card>
            ) : testResults.map((r, i) => {
              const a = r.analysis || {};
              const ins = a.insights || {};
              return (
                <Card key={i} className="bg-[#2a2a2a] border-yellow-400/20">
                  <CardContent className="p-5">
                    <div className="flex flex-col md:flex-row justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-full border-2 border-yellow-400 flex items-center justify-center bg-[#1a1a1a] shrink-0">
                          <span className="text-yellow-400 font-black text-sm">{ins.code || 'aK'}</span>
                        </div>
                        <div>
                          <p className="text-white font-bold">{r.userName}</p>
                          <p className="text-gray-400 text-xs">{r.userEmail}</p>
                          <div className="flex gap-3 mt-2 text-xs">
                            <span className="text-gray-400">Elemen: <strong className="text-yellow-400">{a.dominantElement?.toUpperCase()}</strong></span>
                            <span className="text-gray-400">Tipe: <strong className="text-blue-400">{a.personalityType}</strong></span>
                            <span className="text-gray-400">Jatidiri: <strong className="text-purple-400">{ins.kekuatanJatidiri?.tipe || '-'}</strong></span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Link to={`/test-result/${r._id}`} target="_blank">
                          <Button size="sm" className="bg-yellow-400 text-black hover:bg-yellow-500">
                            <Eye className="w-4 h-4 mr-1" /> Lihat
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* ═══ WALLET TAB ═══ */}
        {activeTab === 'wallet' && (
          <div className="space-y-6">
            {/* Balance Card */}
            <Card className="bg-gradient-to-br from-yellow-400/20 to-yellow-600/10 border-yellow-400/40">
              <CardContent className="p-6">
                <p className="text-gray-400 text-sm">Saldo Wallet</p>
                <p className="text-4xl font-black text-yellow-400 mt-1">{fmt(wallet.balance)}</p>
                <p className="text-gray-500 text-xs mt-2">Komisi dari setiap pengguna referral yang membayar</p>
              </CardContent>
            </Card>

            {/* Withdrawal Form */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader><CardTitle className="text-white">Ajukan Penarikan</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-400 text-sm">Jumlah Penarikan (min. Rp 50.000)</Label>
                    <Input type="number" value={withdrawForm.amount} onChange={e => setWithdrawForm(p => ({...p, amount: e.target.value}))}
                      placeholder="50000" className="bg-[#1a1a1a] text-white border-yellow-400/30 mt-1" />
                  </div>
                  <div>
                    <Label className="text-gray-400 text-sm">Nama Bank</Label>
                    <Input value={withdrawForm.bankName} onChange={e => setWithdrawForm(p => ({...p, bankName: e.target.value}))}
                      placeholder="BCA / BNI / Mandiri..." className="bg-[#1a1a1a] text-white border-yellow-400/30 mt-1" />
                  </div>
                  <div>
                    <Label className="text-gray-400 text-sm">Nomor Rekening</Label>
                    <Input value={withdrawForm.bankAccount} onChange={e => setWithdrawForm(p => ({...p, bankAccount: e.target.value}))}
                      placeholder="1234567890" className="bg-[#1a1a1a] text-white border-yellow-400/30 mt-1" />
                  </div>
                  <div>
                    <Label className="text-gray-400 text-sm">Nama Pemilik Rekening</Label>
                    <Input value={withdrawForm.accountName} onChange={e => setWithdrawForm(p => ({...p, accountName: e.target.value}))}
                      placeholder="Nama sesuai rekening" className="bg-[#1a1a1a] text-white border-yellow-400/30 mt-1" />
                  </div>
                </div>
                <Button onClick={handleWithdraw} disabled={withdrawing} className="bg-yellow-400 text-black hover:bg-yellow-500">
                  <ArrowDownToLine className="w-4 h-4 mr-2" />
                  {withdrawing ? 'Memproses...' : 'Ajukan Penarikan'}
                </Button>
              </CardContent>
            </Card>

            {/* Transaction History */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader><CardTitle className="text-white text-sm">Riwayat Transaksi</CardTitle></CardHeader>
              <CardContent className="p-0">
                {wallet.transactions.length === 0 ? (
                  <p className="text-gray-400 text-center py-6 text-sm">Belum ada transaksi</p>
                ) : (
                  <div className="divide-y divide-yellow-400/10">
                    {wallet.transactions.map((t, i) => (
                      <div key={i} className="flex justify-between items-center px-4 py-3">
                        <div>
                          <p className="text-white text-sm">{t.type === 'withdrawal' ? 'Penarikan' : t.type === 'commission' ? 'Komisi Referral' : t.type}</p>
                          <p className="text-gray-400 text-xs">{t.createdAt ? new Date(t.createdAt).toLocaleDateString('id-ID') : '-'}</p>
                        </div>
                        <div className="text-right">
                          <p className={`font-bold ${t.type === 'withdrawal' ? 'text-red-400' : 'text-green-400'}`}>
                            {t.type === 'withdrawal' ? '-' : '+'}{fmt(t.amount)}
                          </p>
                          <p className={`text-xs ${t.status === 'pending' ? 'text-yellow-400' : 'text-green-400'}`}>
                            {t.status === 'pending' ? 'Menunggu' : 'Selesai'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* ═══ PENGATURAN TAB ═══ */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            {/* Edit Harga */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader>
                <CardTitle className="text-white">Harga Test Premium Referral</CardTitle>
                <p className="text-gray-400 text-sm">Atur harga khusus untuk pengguna yang mendaftar via link referral Yayasan Anda.</p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <Label className="text-gray-400 text-sm">Harga (Rp)</Label>
                    {editingPrice ? (
                      <Input type="number" value={newPrice} onChange={e => setNewPrice(Number(e.target.value))}
                        min={10000} className="bg-[#1a1a1a] text-white border-yellow-400/50 mt-1" />
                    ) : (
                      <p className="text-3xl font-bold text-yellow-400 mt-1">{fmt(yayasan?.referralPrice || 100000)}</p>
                    )}
                  </div>
                  {editingPrice ? (
                    <div className="flex gap-2 mt-5">
                      <Button onClick={handleUpdatePrice} disabled={savingPrice} className="bg-yellow-400 text-black hover:bg-yellow-500">
                        <Save className="w-4 h-4 mr-1" /> {savingPrice ? 'Menyimpan...' : 'Simpan'}
                      </Button>
                      <Button onClick={() => setEditingPrice(false)} variant="outline" className="border-gray-500 text-gray-400">Batal</Button>
                    </div>
                  ) : (
                    <Button onClick={() => setEditingPrice(true)} variant="outline" className="border-yellow-400/50 text-yellow-400 mt-5">
                      <Edit className="w-4 h-4 mr-1" /> Edit Harga
                    </Button>
                  )}
                </div>
                <div className="bg-yellow-400/10 rounded-lg p-3">
                  <p className="text-yellow-400 text-xs">
                    Harga default platform: <strong>Rp 100.000</strong>. Anda bisa menetapkan harga berbeda untuk pengguna referral Yayasan Anda.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Info Yayasan */}
            <Card className="bg-[#2a2a2a] border-yellow-400/20">
              <CardHeader><CardTitle className="text-white">Informasi Yayasan</CardTitle></CardHeader>
              <CardContent className="space-y-3 text-sm">
                {[
                  { label: 'Nama', val: yayasan?.name },
                  { label: 'Email', val: yayasan?.email },
                  { label: 'Kode Referral', val: yayasan?.referralCode },
                  { label: 'Status', val: yayasan?.isVerified ? 'Terverifikasi' : 'Menunggu Verifikasi' },
                ].map((r, i) => (
                  <div key={i} className="flex justify-between border-b border-yellow-400/10 pb-2">
                    <span className="text-gray-400">{r.label}</span>
                    <span className="text-white font-medium">{r.val || '-'}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

      </div>
    </div>
  );
}
