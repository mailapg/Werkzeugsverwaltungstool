import { useEffect, useState } from 'react'
import { toolsApi, lookupsApi } from '../api/services'
import type { Tool, ToolCategory } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Search, Wrench, Package } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export default function ToolsPage() {
  const { isAdmin } = useAuth()
  const [tools, setTools] = useState<Tool[]>([])
  const [categories, setCategories] = useState<ToolCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterCat, setFilterCat] = useState<string>('all')
  const [open, setOpen] = useState(false)
  const [editTool, setEditTool] = useState<Tool | null>(null)
  const [form, setForm] = useState({ tool_name: '', description: '', category_id: '' })
  const [saving, setSaving] = useState(false)
  const [detailTool, setDetailTool] = useState<Tool | null>(null)

  const load = () => {
    setLoading(true)
    Promise.all([toolsApi.list(), lookupsApi.categories()])
      .then(([t, c]) => { setTools(t); setCategories(c) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditTool(null); setForm({ tool_name: '', description: '', category_id: '' }); setOpen(true) }
  const openEdit = (t: Tool) => {
    setEditTool(t)
    setForm({ tool_name: t.tool_name, description: t.description ?? '', category_id: String(t.category_id) })
    setOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const fd = new FormData()
      fd.append('tool_name', form.tool_name)
      fd.append('description', form.description)
      fd.append('category_id', form.category_id)
      if (editTool) {
        await toolsApi.update(editTool.id, fd); toast.success('Werkzeug aktualisiert')
      } else {
        await toolsApi.create(fd); toast.success('Werkzeug erstellt')
      }
      setOpen(false); load()
    } catch { toast.error('Fehler beim Speichern') }
    finally { setSaving(false) }
  }

  const handleDelete = async (t: Tool) => {
    if (!confirm(`Werkzeug "${t.tool_name}" löschen?`)) return
    try { await toolsApi.delete(t.id); toast.success('Werkzeug gelöscht'); load() }
    catch { toast.error('Löschen fehlgeschlagen') }
  }

  const filtered = tools.filter(t => {
    const matchesSearch = t.tool_name.toLowerCase().includes(search.toLowerCase())
    const matchesCat = filterCat === 'all' || t.category_id === Number(filterCat)
    return matchesSearch && matchesCat
  })

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Wrench size={24} />Werkzeuge</h1>
          <p className="text-slate-500 mt-1">{tools.length} Werkzeugtypen</p>
        </div>
        {isAdmin && (
          <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
            <Plus size={16} className="mr-2" />Neues Werkzeug
          </Button>
        )}
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input placeholder="Suchen…" value={search} onChange={e => setSearch(e.target.value)} className="pl-9" />
        </div>
        <Select value={filterCat} onValueChange={setFilterCat}>
          <SelectTrigger className="w-48"><SelectValue placeholder="Kategorie" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Kategorien</SelectItem>
            {categories.map(c => <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-40" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map(t => (
            <div
              key={t.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition-shadow group cursor-pointer"
              onClick={() => setDetailTool(t)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center overflow-hidden">
                  {t.image_filename
                    ? <img src={`${API_URL}/static/tool_images/${t.image_filename}`} alt={t.tool_name} className="w-full h-full object-cover" />
                    : <Wrench size={18} className="text-blue-600" />}
                </div>
                {isAdmin && (
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                    <Button size="sm" variant="ghost" onClick={() => openEdit(t)}><Pencil size={13} /></Button>
                    <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(t)}><Trash2 size={13} /></Button>
                  </div>
                )}
              </div>
              <h3 className="font-semibold text-slate-800 text-sm leading-tight">{t.tool_name}</h3>
              {t.description && <p className="text-xs text-slate-500 mt-1 line-clamp-2">{t.description}</p>}
              <div className="mt-3">
                <Badge variant="secondary" className="text-xs">{t.category.name}</Badge>
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="col-span-full text-center py-12 text-slate-400">Keine Werkzeuge gefunden</div>
          )}
        </div>
      )}

      {/* Tool detail dialog */}
      <Dialog open={!!detailTool} onOpenChange={v => !v && setDetailTool(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>{detailTool?.tool_name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-lg overflow-hidden aspect-square flex items-center justify-center bg-slate-50">
              {detailTool?.image_filename ? (
                <img
                  src={`${API_URL}/static/tool_images/${detailTool.image_filename}`}
                  alt={detailTool.tool_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center gap-2 text-slate-300">
                  <Package size={52} />
                  <span className="text-xs">Kein Bild vorhanden</span>
                </div>
              )}
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Kategorie</span>
                <Badge variant="secondary" className="text-xs">{detailTool?.category.name}</Badge>
              </div>
              {detailTool?.description && (
                <div className="pt-1 border-t border-slate-100">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Beschreibung</p>
                  <p className="text-slate-700 text-sm">{detailTool.description}</p>
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editTool ? 'Werkzeug bearbeiten' : 'Neues Werkzeug'}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Name</Label>
              <Input value={form.tool_name} onChange={e => setForm(f => ({ ...f, tool_name: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Beschreibung</Label>
              <Input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Kategorie</Label>
              <Select value={form.category_id} onValueChange={v => setForm(f => ({ ...f, category_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                <SelectContent>{categories.map(c => <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={saving} className="bg-blue-600 hover:bg-blue-700">
              {saving ? 'Speichern…' : 'Speichern'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
