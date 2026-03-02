import React, { useState, useEffect } from 'react';
import { Building2, CheckCircle, XCircle, Eye, ToggleLeft, ToggleRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const fmt = (n) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(n || 0);

export default function AdminYayasan() {
  const { toast } = useToast();
  const [yayasanList, setYayasanList] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = () => localStorage.getItem('admin_token');
  const headers = () => ({ Authorization: `Bearer ${token()}` });

  useEffect(() => { loadYayasan(); }, []);

  const loadYayasan = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/yayasan/admin/list`, { headers: headers() });
      setYayasanList(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const toggleActive = async (id, current) => {
    try {
      await axios.put(`${API_URL}/api/yayasan/admin/${id}/toggle-active`, {}, { headers: headers() });
      setYayasanList(prev => prev.map(y => y._id === id ? { ...y, isActive: !current } : y));
      toast({ title: 'Berhasil', description: `Yayasan ${!current ? 'diaktifkan' : 'dinonaktifkan'}` });
    } catch (e) {
      toast({ title: 'Error', description: 'Gagal mengubah status', variant: 'destructive' });
    }
  };

  const verify = async (id) => {
    try {
      await axios.put(`${API_URL}/api/yayasan/admin/${id}/verify`, {}, { headers: headers() });
      setYayasanList(prev => prev.map(y => y._id === id ? { ...y, isVerified: true } : y));
      toast({ title: 'Berhasil', description: 'Yayasan diverifikasi' });
    } catch (e) {
      toast({ title: 'Error', description: 'Gagal verifikasi', variant: 'destructive' });
    }
  };

  if (loading) return <div className="flex justify-center py-20"><div className="w-10 h-10 border-4 border-yellow-400 border-t-transparent rounded-full animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Building2 className="w-7 h-7 text-yellow-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Manajemen Yayasan</h1>
          <p className="text-gray-400 text-sm">Kelola yayasan yang terdaftar di platform</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Yayasan', val: yayasanList.length },
          { label: 'Terverifikasi', val: yayasanList.filter(y => y.isVerified).length },
          { label: 'Aktif', val: yayasanList.filter(y => y.isActive).length },
        ].map((s, i) => (
          <Card key={i} className="bg-[#2a2a2a] border-yellow-400/20">
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-yellow-400">{s.val}</p>
              <p className="text-gray-400 text-sm">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-[#2a2a2a] border-yellow-400/20">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-yellow-400/20 text-gray-400">
                  <th className="text-left py-3 px-4">Yayasan</th>
                  <th className="text-left py-3 px-4">Kode Referral</th>
                  <th className="text-left py-3 px-4">Harga Referral</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Bergabung</th>
                  <th className="text-left py-3 px-4">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {yayasanList.length === 0 ? (
                  <tr><td colSpan={6} className="text-center text-gray-400 py-8">Belum ada yayasan terdaftar</td></tr>
                ) : yayasanList.map((y) => (
                  <tr key={y._id} className="border-b border-yellow-400/10 hover:bg-[#333]">
                    <td className="py-3 px-4">
                      <p className="text-white font-medium">{y.name}</p>
                      <p className="text-gray-400 text-xs">{y.email}</p>
                    </td>
                    <td className="py-3 px-4">
                      <code className="text-yellow-400 text-xs bg-yellow-400/10 px-2 py-1 rounded">{y.referralCode}</code>
                    </td>
                    <td className="py-3 px-4 text-green-400 font-medium">
                      {fmt(y.referralPrice || 100000)}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        <span className={`px-2 py-0.5 rounded text-xs ${y.isActive ? 'bg-green-400/20 text-green-400' : 'bg-red-400/20 text-red-400'}`}>
                          {y.isActive ? 'Aktif' : 'Nonaktif'}
                        </span>
                        {y.isVerified && (
                          <span className="px-2 py-0.5 rounded text-xs bg-blue-400/20 text-blue-400">Verified</span>
                        )}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-gray-400 text-xs">
                      {y.createdAt ? new Date(y.createdAt).toLocaleDateString('id-ID') : '-'}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-1">
                        {!y.isVerified && (
                          <Button size="sm" onClick={() => verify(y._id)}
                            className="bg-green-600 hover:bg-green-700 text-white text-xs px-2 py-1 h-auto">
                            <CheckCircle className="w-3 h-3 mr-1" /> Verifikasi
                          </Button>
                        )}
                        <Button size="sm" onClick={() => toggleActive(y._id, y.isActive)}
                          variant="outline"
                          className={`text-xs px-2 py-1 h-auto ${y.isActive ? 'border-red-400/50 text-red-400' : 'border-green-400/50 text-green-400'}`}>
                          {y.isActive ? <ToggleRight className="w-3 h-3 mr-1" /> : <ToggleLeft className="w-3 h-3 mr-1" />}
                          {y.isActive ? 'Nonaktifkan' : 'Aktifkan'}
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
