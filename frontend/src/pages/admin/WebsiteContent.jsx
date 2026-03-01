import React, { useState, useEffect } from 'react';
import { 
  Image, Plus, Trash2, Edit, Save, X, ChevronDown, ChevronUp, 
  RefreshCw, Layout, Users, ShoppingBag, MessageSquare, Activity
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const WebsiteContent = () => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('slides');
  const [loading, setLoading] = useState(false);
  
  // Data states
  const [heroSlides, setHeroSlides] = useState([]);
  const [products, setProducts] = useState([]);
  const [testimonials, setTestimonials] = useState([]);
  const [activities, setActivities] = useState([]);
  const [sectionImages, setSectionImages] = useState([]);
  
  // Edit states
  const [editingSlide, setEditingSlide] = useState(null);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editingTestimonial, setEditingTestimonial] = useState(null);
  const [editingActivity, setEditingActivity] = useState(null);

  useEffect(() => {
    loadAllContent();
  }, []);

  const loadAllContent = async () => {
    setLoading(true);
    try {
      const [slidesRes, productsRes, testimonialsRes, activitiesRes, imagesRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/website-content/hero-slides`),
        axios.get(`${BACKEND_URL}/api/website-content/products`),
        axios.get(`${BACKEND_URL}/api/website-content/testimonials`),
        axios.get(`${BACKEND_URL}/api/website-content/activities`),
        axios.get(`${BACKEND_URL}/api/website-content/section-images`)
      ]);
      setHeroSlides(slidesRes.data || []);
      setProducts(productsRes.data || []);
      setTestimonials(testimonialsRes.data || []);
      setActivities(activitiesRes.data || []);
      setSectionImages(imagesRes.data || []);
    } catch (error) {
      console.error('Failed to load content:', error);
    } finally {
      setLoading(false);
    }
  };

  const seedDefaults = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/api/website-content/seed-defaults`);
      toast({ title: 'Berhasil', description: response.data.message });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal seed data', variant: 'destructive' });
    }
  };

  // Hero Slides handlers
  const saveSlide = async (slide) => {
    try {
      if (slide._id) {
        await axios.put(`${BACKEND_URL}/api/website-content/hero-slides/${slide._id}`, slide);
      } else {
        await axios.post(`${BACKEND_URL}/api/website-content/hero-slides`, slide);
      }
      toast({ title: 'Berhasil', description: 'Slide berhasil disimpan' });
      setEditingSlide(null);
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menyimpan slide', variant: 'destructive' });
    }
  };

  const deleteSlide = async (id) => {
    if (!window.confirm('Hapus slide ini?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/website-content/hero-slides/${id}`);
      toast({ title: 'Berhasil', description: 'Slide berhasil dihapus' });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menghapus slide', variant: 'destructive' });
    }
  };

  // Products handlers
  const saveProduct = async (product) => {
    try {
      if (product._id) {
        await axios.put(`${BACKEND_URL}/api/website-content/products/${product._id}`, product);
      } else {
        await axios.post(`${BACKEND_URL}/api/website-content/products`, product);
      }
      toast({ title: 'Berhasil', description: 'Produk berhasil disimpan' });
      setEditingProduct(null);
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menyimpan produk', variant: 'destructive' });
    }
  };

  const deleteProduct = async (id) => {
    if (!window.confirm('Hapus produk ini?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/website-content/products/${id}`);
      toast({ title: 'Berhasil', description: 'Produk berhasil dihapus' });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menghapus produk', variant: 'destructive' });
    }
  };

  // Testimonials handlers
  const saveTestimonial = async (testimonial) => {
    try {
      if (testimonial._id) {
        await axios.put(`${BACKEND_URL}/api/website-content/testimonials/${testimonial._id}`, testimonial);
      } else {
        await axios.post(`${BACKEND_URL}/api/website-content/testimonials`, testimonial);
      }
      toast({ title: 'Berhasil', description: 'Testimonial berhasil disimpan' });
      setEditingTestimonial(null);
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menyimpan testimonial', variant: 'destructive' });
    }
  };

  const deleteTestimonial = async (id) => {
    if (!window.confirm('Hapus testimonial ini?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/website-content/testimonials/${id}`);
      toast({ title: 'Berhasil', description: 'Testimonial berhasil dihapus' });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menghapus testimonial', variant: 'destructive' });
    }
  };

  // Activities handlers
  const saveActivity = async (activity) => {
    try {
      if (activity._id) {
        await axios.put(`${BACKEND_URL}/api/website-content/activities/${activity._id}`, activity);
      } else {
        await axios.post(`${BACKEND_URL}/api/website-content/activities`, activity);
      }
      toast({ title: 'Berhasil', description: 'Kegiatan berhasil disimpan' });
      setEditingActivity(null);
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menyimpan kegiatan', variant: 'destructive' });
    }
  };

  const deleteActivity = async (id) => {
    if (!window.confirm('Hapus kegiatan ini?')) return;
    try {
      await axios.delete(`${BACKEND_URL}/api/website-content/activities/${id}`);
      toast({ title: 'Berhasil', description: 'Kegiatan berhasil dihapus' });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menghapus kegiatan', variant: 'destructive' });
    }
  };

  // Section Images handler
  const saveSectionImage = async (sectionName, imageUrl) => {
    try {
      await axios.post(`${BACKEND_URL}/api/website-content/section-images`, {
        sectionName,
        imageUrl,
        altText: sectionName
      });
      toast({ title: 'Berhasil', description: 'Gambar section berhasil disimpan' });
      loadAllContent();
    } catch (error) {
      toast({ title: 'Error', description: 'Gagal menyimpan gambar', variant: 'destructive' });
    }
  };

  const tabs = [
    { id: 'slides', name: 'Hero Slides', icon: Layout, count: heroSlides.length },
    { id: 'products', name: 'Produk', icon: ShoppingBag, count: products.length },
    { id: 'testimonials', name: 'Testimonial', icon: MessageSquare, count: testimonials.length },
    { id: 'activities', name: 'Kegiatan', icon: Activity, count: activities.length },
    { id: 'sections', name: 'Gambar Section', icon: Image, count: sectionImages.length }
  ];

  return (
    <div className="space-y-6" data-testid="website-content-page">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Konten Website</h1>
          <p className="text-gray-400">Kelola semua gambar dan konten di website</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadAllContent} variant="outline" className="border-yellow-400 text-yellow-400">
            <RefreshCw className="w-4 h-4 mr-2" /> Refresh
          </Button>
          <Button onClick={seedDefaults} className="bg-yellow-400 text-black hover:bg-yellow-500">
            Seed Default Data
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-yellow-400/20 pb-4">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <Button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              variant={activeTab === tab.id ? 'default' : 'outline'}
              className={activeTab === tab.id 
                ? 'bg-yellow-400 text-black' 
                : 'border-yellow-400/30 text-gray-300 hover:bg-yellow-400/10'}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.name}
              <span className="ml-2 bg-black/20 px-2 py-0.5 rounded text-xs">{tab.count}</span>
            </Button>
          );
        })}
      </div>

      {loading && <div className="text-center text-yellow-400 py-8">Loading...</div>}

      {/* Hero Slides Tab */}
      {activeTab === 'slides' && (
        <div className="space-y-4">
          <Button 
            onClick={() => setEditingSlide({ title: '', subtitle: '', description: '', badge: '', imageUrl: '', ctaText: '', ctaLink: '/', order: heroSlides.length, isActive: true })}
            className="bg-yellow-400 text-black hover:bg-yellow-500"
          >
            <Plus className="w-4 h-4 mr-2" /> Tambah Slide
          </Button>

          {editingSlide && (
            <Card className="bg-[#2a2a2a] border-yellow-400/30">
              <CardHeader>
                <CardTitle className="text-white">{editingSlide._id ? 'Edit Slide' : 'Tambah Slide Baru'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">Judul</Label>
                    <Input value={editingSlide.title} onChange={e => setEditingSlide({...editingSlide, title: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Subtitle</Label>
                    <Input value={editingSlide.subtitle} onChange={e => setEditingSlide({...editingSlide, subtitle: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                <div>
                  <Label className="text-white">Deskripsi</Label>
                  <Input value={editingSlide.description} onChange={e => setEditingSlide({...editingSlide, description: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">Badge</Label>
                    <Input value={editingSlide.badge} onChange={e => setEditingSlide({...editingSlide, badge: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">URL Gambar</Label>
                    <Input value={editingSlide.imageUrl} onChange={e => setEditingSlide({...editingSlide, imageUrl: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" placeholder="https://..." />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">Teks Tombol</Label>
                    <Input value={editingSlide.ctaText} onChange={e => setEditingSlide({...editingSlide, ctaText: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Link Tombol</Label>
                    <Input value={editingSlide.ctaLink} onChange={e => setEditingSlide({...editingSlide, ctaLink: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                {editingSlide.imageUrl && (
                  <div className="mt-2">
                    <Label className="text-white mb-2 block">Preview</Label>
                    <img src={editingSlide.imageUrl} alt="Preview" className="w-32 h-32 object-cover rounded-full border-2 border-yellow-400" />
                  </div>
                )}
                <div className="flex gap-2">
                  <Button onClick={() => saveSlide(editingSlide)} className="bg-green-600 hover:bg-green-700">
                    <Save className="w-4 h-4 mr-2" /> Simpan
                  </Button>
                  <Button onClick={() => setEditingSlide(null)} variant="outline" className="border-gray-500 text-gray-300">
                    <X className="w-4 h-4 mr-2" /> Batal
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4">
            {heroSlides.map((slide, index) => (
              <Card key={slide._id} className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4 flex items-center gap-4">
                  <img src={slide.imageUrl} alt={slide.title} className="w-20 h-20 object-cover rounded-lg" />
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">{slide.title}</h3>
                    <p className="text-gray-400 text-sm">{slide.subtitle}</p>
                    <p className="text-yellow-400 text-xs mt-1">Badge: {slide.badge}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => setEditingSlide(slide)} variant="outline" className="border-yellow-400 text-yellow-400">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button size="sm" onClick={() => deleteSlide(slide._id)} variant="outline" className="border-red-400 text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="space-y-4">
          <Button 
            onClick={() => setEditingProduct({ title: '', subtitle: '', imageUrl: '', link: '/', badge: '', order: products.length, isActive: true })}
            className="bg-yellow-400 text-black hover:bg-yellow-500"
          >
            <Plus className="w-4 h-4 mr-2" /> Tambah Produk
          </Button>

          {editingProduct && (
            <Card className="bg-[#2a2a2a] border-yellow-400/30">
              <CardHeader>
                <CardTitle className="text-white">{editingProduct._id ? 'Edit Produk' : 'Tambah Produk Baru'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">Nama Produk</Label>
                    <Input value={editingProduct.title} onChange={e => setEditingProduct({...editingProduct, title: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Subtitle</Label>
                    <Input value={editingProduct.subtitle} onChange={e => setEditingProduct({...editingProduct, subtitle: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">URL Gambar</Label>
                    <Input value={editingProduct.imageUrl} onChange={e => setEditingProduct({...editingProduct, imageUrl: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Link</Label>
                    <Input value={editingProduct.link} onChange={e => setEditingProduct({...editingProduct, link: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                <div>
                  <Label className="text-white">Badge</Label>
                  <Input value={editingProduct.badge} onChange={e => setEditingProduct({...editingProduct, badge: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => saveProduct(editingProduct)} className="bg-green-600 hover:bg-green-700">
                    <Save className="w-4 h-4 mr-2" /> Simpan
                  </Button>
                  <Button onClick={() => setEditingProduct(null)} variant="outline" className="border-gray-500 text-gray-300">
                    <X className="w-4 h-4 mr-2" /> Batal
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {products.map((product) => (
              <Card key={product._id} className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <img src={product.imageUrl} alt={product.title} className="w-full h-32 object-cover rounded-lg mb-3" />
                  <h3 className="text-white font-semibold text-sm">{product.title}</h3>
                  <p className="text-gray-400 text-xs">{product.subtitle}</p>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" onClick={() => setEditingProduct(product)} variant="outline" className="border-yellow-400 text-yellow-400 flex-1">
                      <Edit className="w-3 h-3" />
                    </Button>
                    <Button size="sm" onClick={() => deleteProduct(product._id)} variant="outline" className="border-red-400 text-red-400 flex-1">
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Testimonials Tab */}
      {activeTab === 'testimonials' && (
        <div className="space-y-4">
          <Button 
            onClick={() => setEditingTestimonial({ name: '', organization: '', role: '', imageUrl: '', text: '', rating: 5, order: testimonials.length, isActive: true })}
            className="bg-yellow-400 text-black hover:bg-yellow-500"
          >
            <Plus className="w-4 h-4 mr-2" /> Tambah Testimonial
          </Button>

          {editingTestimonial && (
            <Card className="bg-[#2a2a2a] border-yellow-400/30">
              <CardHeader>
                <CardTitle className="text-white">{editingTestimonial._id ? 'Edit Testimonial' : 'Tambah Testimonial Baru'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label className="text-white">Nama</Label>
                    <Input value={editingTestimonial.name} onChange={e => setEditingTestimonial({...editingTestimonial, name: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Organisasi</Label>
                    <Input value={editingTestimonial.organization} onChange={e => setEditingTestimonial({...editingTestimonial, organization: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Jabatan</Label>
                    <Input value={editingTestimonial.role} onChange={e => setEditingTestimonial({...editingTestimonial, role: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                <div>
                  <Label className="text-white">URL Foto</Label>
                  <Input value={editingTestimonial.imageUrl} onChange={e => setEditingTestimonial({...editingTestimonial, imageUrl: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                </div>
                <div>
                  <Label className="text-white">Testimonial</Label>
                  <textarea 
                    value={editingTestimonial.text} 
                    onChange={e => setEditingTestimonial({...editingTestimonial, text: e.target.value})} 
                    className="w-full bg-[#1a1a1a] border border-yellow-400/30 text-white rounded-md p-2 min-h-[100px]" 
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => saveTestimonial(editingTestimonial)} className="bg-green-600 hover:bg-green-700">
                    <Save className="w-4 h-4 mr-2" /> Simpan
                  </Button>
                  <Button onClick={() => setEditingTestimonial(null)} variant="outline" className="border-gray-500 text-gray-300">
                    <X className="w-4 h-4 mr-2" /> Batal
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4">
            {testimonials.map((t) => (
              <Card key={t._id} className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4 flex items-center gap-4">
                  <img src={t.imageUrl} alt={t.name} className="w-16 h-16 object-cover rounded-full" />
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">{t.name}</h3>
                    <p className="text-yellow-400 text-sm">{t.role} - {t.organization}</p>
                    <p className="text-gray-400 text-sm mt-1 line-clamp-2">{t.text}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => setEditingTestimonial(t)} variant="outline" className="border-yellow-400 text-yellow-400">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button size="sm" onClick={() => deleteTestimonial(t._id)} variant="outline" className="border-red-400 text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Activities Tab */}
      {activeTab === 'activities' && (
        <div className="space-y-4">
          <Button 
            onClick={() => setEditingActivity({ title: '', imageUrl: '', link: '/', order: activities.length, isActive: true })}
            className="bg-yellow-400 text-black hover:bg-yellow-500"
          >
            <Plus className="w-4 h-4 mr-2" /> Tambah Kegiatan
          </Button>

          {editingActivity && (
            <Card className="bg-[#2a2a2a] border-yellow-400/30">
              <CardHeader>
                <CardTitle className="text-white">{editingActivity._id ? 'Edit Kegiatan' : 'Tambah Kegiatan Baru'}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-white">Nama Kegiatan</Label>
                    <Input value={editingActivity.title} onChange={e => setEditingActivity({...editingActivity, title: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                  <div>
                    <Label className="text-white">Link</Label>
                    <Input value={editingActivity.link} onChange={e => setEditingActivity({...editingActivity, link: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                  </div>
                </div>
                <div>
                  <Label className="text-white">URL Gambar</Label>
                  <Input value={editingActivity.imageUrl} onChange={e => setEditingActivity({...editingActivity, imageUrl: e.target.value})} className="bg-[#1a1a1a] border-yellow-400/30 text-white" />
                </div>
                <div className="flex gap-2">
                  <Button onClick={() => saveActivity(editingActivity)} className="bg-green-600 hover:bg-green-700">
                    <Save className="w-4 h-4 mr-2" /> Simpan
                  </Button>
                  <Button onClick={() => setEditingActivity(null)} variant="outline" className="border-gray-500 text-gray-300">
                    <X className="w-4 h-4 mr-2" /> Batal
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {activities.map((activity) => (
              <Card key={activity._id} className="bg-[#2a2a2a] border-yellow-400/20">
                <CardContent className="p-4">
                  <img src={activity.imageUrl} alt={activity.title} className="w-full h-24 object-cover rounded-lg mb-3" />
                  <h3 className="text-white font-semibold text-sm text-center">{activity.title}</h3>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" onClick={() => setEditingActivity(activity)} variant="outline" className="border-yellow-400 text-yellow-400 flex-1">
                      <Edit className="w-3 h-3" />
                    </Button>
                    <Button size="sm" onClick={() => deleteActivity(activity._id)} variant="outline" className="border-red-400 text-red-400 flex-1">
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Section Images Tab */}
      {activeTab === 'sections' && (
        <div className="space-y-4">
          <Card className="bg-[#2a2a2a] border-yellow-400/30">
            <CardHeader>
              <CardTitle className="text-white">Gambar Section Website</CardTitle>
              <CardDescription className="text-gray-400">Kelola gambar untuk setiap section di halaman utama</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6">
                {[
                  { name: 'about-main', label: 'About Section - Gambar Utama' },
                  { name: 'services-corporate', label: 'Services - Korporasi/B2B' },
                  { name: 'services-individual', label: 'Services - Individual/B2C' },
                  { name: 'promo-main', label: 'Promo Section - Gambar Utama' }
                ].map((section) => {
                  const currentImage = sectionImages.find(img => img.sectionName === section.name);
                  return (
                    <div key={section.name} className="border border-yellow-400/20 rounded-lg p-4">
                      <Label className="text-white mb-2 block">{section.label}</Label>
                      <div className="flex gap-4 items-center">
                        {currentImage?.imageUrl && (
                          <img src={currentImage.imageUrl} alt={section.label} className="w-24 h-24 object-cover rounded-lg" />
                        )}
                        <div className="flex-1">
                          <Input
                            placeholder="URL Gambar"
                            defaultValue={currentImage?.imageUrl || ''}
                            id={`section-${section.name}`}
                            className="bg-[#1a1a1a] border-yellow-400/30 text-white mb-2"
                          />
                          <Button 
                            size="sm"
                            onClick={() => {
                              const input = document.getElementById(`section-${section.name}`);
                              saveSectionImage(section.name, input.value);
                            }}
                            className="bg-yellow-400 text-black hover:bg-yellow-500"
                          >
                            <Save className="w-4 h-4 mr-2" /> Simpan
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default WebsiteContent;
