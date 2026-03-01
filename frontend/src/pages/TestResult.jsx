import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ── helper ──────────────────────────────────────────────────
const pct = (val, max) => max > 0 ? Math.round((val / max) * 100) : 0;

const ELEM_COLORS = {
  kayu: '#4CAF50', api: '#FF5722', tanah: '#FFC107',
  logam: '#9E9E9E', air: '#2196F3',
};
const ELEM_EN = {
  kayu: 'Wood', api: 'Fire', tanah: 'Earth', logam: 'Metal', air: 'Water',
};

// ── PersonalityCode badge ────────────────────────────────────
function CodeBadge({ code }) {
  const prefix = code?.[0] || 'e';
  const suffix = code?.[1] || 'K';
  return (
    <div className="flex items-center justify-center">
      <div
        className="w-28 h-28 rounded-full border-4 border-yellow-400 flex items-center justify-center bg-white shadow-xl"
        style={{ fontFamily: 'serif' }}
      >
        <span className="text-4xl font-black text-gray-800 tracking-tight">
          <span className="text-yellow-500">{prefix}</span>
          <span className="text-gray-900">{suffix}</span>
        </span>
      </div>
    </div>
  );
}

// ── Element Score Bar ────────────────────────────────────────
function ElementBar({ name, score, maxScore }) {
  const p = pct(score, maxScore);
  const color = ELEM_COLORS[name] || '#888';
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="w-14 text-right text-gray-700 font-semibold capitalize">{name}</span>
      <div className="flex-1 bg-gray-200 rounded-full h-2.5">
        <div className="h-2.5 rounded-full" style={{ width: `${p}%`, backgroundColor: color }} />
      </div>
      <span className="w-8 text-gray-600 font-bold">{p}%</span>
    </div>
  );
}

// ── Main Component ───────────────────────────────────────────
export default function TestResult() {
  const { resultId, id: idParam } = useParams();
  const id = resultId || idParam;
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const printRef = useRef();

  useEffect(() => {
    (async () => {
      try {
        const token = localStorage.getItem('user_token');
        const res = await axios.get(`${API}/test-results/${id}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        });
        setResult(res.data);
      } catch (e) {
        setError('Hasil test tidak ditemukan.');
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <p className="text-yellow-600 animate-pulse text-lg font-semibold">Memuat hasil test...</p>
    </div>
  );

  if (error || !result) return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center gap-4">
      <p className="text-red-500">{error || 'Terjadi kesalahan'}</p>
      <Link to="/dashboard" className="text-yellow-600 underline">Kembali ke Dashboard</Link>
    </div>
  );

  const analysis = result.analysis || {};
  const insights = analysis.insights || {};
  const elem = (analysis.dominantElement || 'kayu').toLowerCase();
  const elemColor = ELEM_COLORS[elem] || '#FFC107';
  const elemScores = analysis.elementScores || {};
  const maxElem = Math.max(...Object.values(elemScores), 1);
  const ka = insights.kompilasiAdaptasi || {};
  const karakter = insights.karakter || [];
  const kj = insights.kekuatanJatidiri || {};
  const keprib = insights.elementDescription || [];
  const code = insights.code || '';
  const ciriKhas = insights.ciriKhas || [];

  return (
    <div className="min-h-screen bg-gray-100 py-6 px-4">
      {/* Action bar */}
      <div className="max-w-4xl mx-auto mb-4 flex gap-3 justify-between items-center print:hidden">
        <Link to="/dashboard" className="text-yellow-600 underline text-sm">← Dashboard</Link>
        <div className="flex gap-2">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 bg-yellow-500 text-white rounded-lg text-sm font-semibold hover:bg-yellow-600 transition"
          >
            Cetak / Simpan PDF
          </button>
          <Link
            to={`/certificate/${id}`}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 transition"
          >
            Download Sertifikat
          </Link>
        </div>
      </div>

      {/* ═══════ SERTIFIKAT ═══════ */}
      <div
        ref={printRef}
        className="max-w-4xl mx-auto bg-white shadow-2xl"
        style={{ fontFamily: 'Arial, sans-serif', border: '2px solid #d4af37' }}
        data-testid="certificate-container"
      >
        {/* ── TOP DECORATION ── */}
        <div className="flex">
          {/* Left gold dots */}
          <div className="w-16 bg-gray-900 relative overflow-hidden" style={{ minHeight: 90 }}>
            <div className="absolute inset-0 opacity-40"
              style={{ backgroundImage: 'radial-gradient(circle, #d4af37 1px, transparent 1px)', backgroundSize: '8px 8px' }} />
          </div>
          {/* Header content */}
          <div className="flex-1 flex items-start justify-between p-4 border-b-2" style={{ borderColor: '#d4af37' }}>
            {/* Logo placeholder */}
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full border-4 flex items-center justify-center overflow-hidden"
                style={{ borderColor: elemColor }}>
                <div className="grid grid-cols-2 gap-0.5 w-8 h-8">
                  <div className="rounded-tl-full bg-red-500" />
                  <div className="rounded-tr-full bg-yellow-500" />
                  <div className="rounded-bl-full bg-blue-500" />
                  <div className="rounded-br-full bg-green-500" />
                </div>
              </div>
              <div>
                <p className="font-black text-xl text-gray-900 leading-none">NEW ME</p>
                <p className="text-xs text-gray-500 italic">Jatidiri di sini</p>
              </div>
            </div>

            {/* Title */}
            <div className="text-right">
              <h1 className="text-xl font-black text-gray-900 leading-tight">SERTIFIKAT</h1>
              <p className="text-xs font-bold text-gray-700">ANALISA KEPRIBADIAN & JATIDIRI</p>
              <p className="text-xs text-gray-500 mt-1">
                ID: <span className="font-mono font-bold">{id?.slice(-8).toUpperCase()}</span>
              </p>
              <p className="text-xs italic text-gray-500 mt-0.5">Optimalkan versi terbaik_mu</p>
            </div>
          </div>
        </div>

        {/* ── BODY: 2 columns ── */}
        <div className="flex">
          {/* ═══ LEFT COLUMN ═══ */}
          <div className="flex-1 p-5 border-r" style={{ borderColor: '#e5e7eb' }}>

            {/* Kepribadian */}
            <section className="mb-4">
              <h3 className="font-black text-sm text-gray-900 border-b pb-1 mb-2" style={{ borderColor: '#d4af37' }}>
                Kepribadian :
              </h3>
              <p className="text-xs text-gray-700 leading-relaxed">
                {Array.isArray(keprib) ? keprib.join(' - ') : keprib}
              </p>
            </section>

            {/* Karakter */}
            <section className="mb-4">
              <h3 className="font-black text-sm text-gray-900 border-b pb-1 mb-2" style={{ borderColor: '#d4af37' }}>
                +/- Karakter :
              </h3>
              <p className="text-xs text-gray-700 leading-relaxed">
                {karakter.join(' - ')}
              </p>
            </section>

            {/* Kekuatan Jatidiri */}
            <section className="mb-4">
              <h3 className="font-black text-sm text-gray-900 border-b pb-1 mb-1" style={{ borderColor: '#d4af37' }}>
                Kekuatan Jatidiri :{' '}
                <span className="text-yellow-600">{kj.tipe || 'Si UNIK'}</span>
              </h3>
              <div className="text-xs text-gray-700 space-y-0.5">
                {kj.kehidupan && <p>Kehidupan : <strong>{kj.kehidupan}</strong> - Kesehatan : <strong>{kj.kesehatan}</strong></p>}
                {kj.kontribusi && <p>Kontribusi : <strong>{kj.kontribusi}</strong> - Kekhasan : <strong>{kj.kekhasan}</strong> - Kharisma : <strong>{kj.kharisma}</strong></p>}
              </div>
            </section>

            {/* Kompilasi Adaptasi */}
            {Object.keys(ka).length > 0 && (
              <section className="mb-4">
                <h3 className="font-black text-sm text-gray-900 border-b pb-1 mb-2" style={{ borderColor: '#d4af37' }}>
                  Kompilasi Adaptasi :
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed" style={{ wordBreak: 'break-word' }}>
                  {Object.entries(ka).map(([k, v]) =>
                    `${k.replace(/([A-Z])/g, ' $1').trim()} : ${v}`
                  ).join(' - ')}
                </p>
              </section>
            )}

            {/* Element Scores */}
            <section>
              <h3 className="font-black text-sm text-gray-900 border-b pb-1 mb-2" style={{ borderColor: '#d4af37' }}>
                Skor 5 Elemen :
              </h3>
              <div className="space-y-1.5">
                {Object.entries(elemScores)
                  .sort(([, a], [, b]) => b - a)
                  .map(([name, score]) => (
                    <ElementBar key={name} name={name} score={score} maxScore={maxElem} />
                  ))}
              </div>
            </section>
          </div>

          {/* ═══ RIGHT COLUMN ═══ */}
          <div className="w-60 p-5 flex flex-col gap-4">

            {/* Code Badge */}
            <div className="text-center">
              <CodeBadge code={code} />
            </div>

            {/* Kepribadian type */}
            <section>
              <h3 className="font-black text-xs text-gray-900 mb-1">Kepribadian :</h3>
              <p className="text-base font-black" style={{ color: elemColor }}>
                {insights.personalityLabel || analysis.personalityType || 'AMBIVERT'}
              </p>
            </section>

            {/* Simbol Jatidiri */}
            <section>
              <h3 className="font-black text-xs text-gray-900 mb-1">Simbol Jatidiri :</h3>
              <div className="text-xs space-y-1">
                {Object.entries(elemScores)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 3)
                  .map(([name, score], i) => (
                    <p key={name}>
                      <span className="text-gray-500">Dominan {['I', 'II', 'III'][i]} :</span>{' '}
                      <strong style={{ color: ELEM_COLORS[name] }}>{name.toUpperCase()}</strong>{' '}
                      <span className="text-gray-600">{pct(score, maxElem)}%</span>
                    </p>
                  ))}
              </div>
            </section>

            {/* Ciri Khas */}
            {ciriKhas.length > 0 && (
              <section>
                <h3 className="font-black text-xs text-gray-900 mb-1">Ciri Khas :</h3>
                <p className="text-xs text-gray-700">{ciriKhas.join(' - ')}</p>
              </section>
            )}

            {/* Dibutuhkan Profesi */}
            {insights.dibutuhkanPadaProfesi && (
              <section>
                <h3 className="font-black text-xs text-gray-900 mb-1">Dibutuhkan pada profesi :</h3>
                <p className="text-xs text-gray-700 italic">{insights.dibutuhkanPadaProfesi}</p>
              </section>
            )}

            {/* Test type badge */}
            <div className="mt-auto">
              <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                result.testType === 'paid'
                  ? 'bg-yellow-100 text-yellow-700 border border-yellow-400'
                  : 'bg-green-100 text-green-700 border border-green-400'
              }`}>
                {result.testType === 'paid' ? 'Test Premium' : 'Test Gratis'}
              </span>
            </div>
          </div>
        </div>

        {/* ── FOOTER ── */}
        <div className="flex items-end justify-between px-5 py-4 border-t-2" style={{ borderColor: '#d4af37' }}>
          <div>
            <div className="w-24 border-b-2 border-gray-800 mb-1" />
            <p className="text-xs font-bold text-gray-800">ABIE DIBYO</p>
            <p className="text-xs text-gray-500">Chairman & B. Development</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-400">
              {new Date(result.completedAt || result.createdAt).toLocaleDateString('id-ID', {
                day: 'numeric', month: 'long', year: 'numeric'
              })}
            </p>
          </div>
          {/* Right gold decoration */}
          <div className="w-20 h-14 relative overflow-hidden rounded-lg"
            style={{ background: 'linear-gradient(135deg, #1a1a1a 60%, #d4af37)' }}>
            <p className="absolute bottom-1 right-2 text-yellow-400 text-xs font-bold">NEW ME</p>
          </div>
        </div>
      </div>

      {/* ── Pesan untuk Free Test ── */}
      {result.testType === 'free' && (
        <div className="max-w-4xl mx-auto mt-4 bg-yellow-50 border border-yellow-400 rounded-xl p-4 print:hidden">
          <p className="text-yellow-800 font-semibold text-sm text-center">
            Ini adalah hasil Test Gratis. Untuk analisis lengkap, kompilasi adaptasi penuh, dan sertifikat resmi — upgrade ke <strong>Test Premium</strong>!
          </p>
          <div className="text-center mt-2">
            <Link to="/test" className="inline-block px-6 py-2 bg-yellow-500 text-white rounded-lg font-bold hover:bg-yellow-600 transition text-sm">
              Mulai Test Premium
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
