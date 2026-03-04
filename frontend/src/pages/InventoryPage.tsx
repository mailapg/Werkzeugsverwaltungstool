import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import jsQR from 'jsqr'
import { toolItemsApi, toolsApi, lookupsApi } from '../api/services'
import type { ToolItem, Tool, ToolStatus, ToolCondition } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Search, Package, QrCode, Archive, ScanLine, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'
import { toolStatusLabel, toolConditionLabel, t } from '../lib/labels'

const statusColor: Record<string, string> = {
  AVAILABLE: 'bg-emerald-100 text-emerald-700',
  LOANED: 'bg-blue-100 text-blue-700',
  DEFECT: 'bg-red-100 text-red-700',
  MAINTENANCE: 'bg-amber-100 text-amber-700',
  RETIRED: 'bg-slate-100 text-slate-500',
}

const conditionColor: Record<string, string> = {
  OK: 'bg-emerald-100 text-emerald-700',
  WORN: 'bg-amber-100 text-amber-700',
  DEFECT: 'bg-red-100 text-red-700',
}

export default function InventoryPage() {
  const { isAdmin } = useAuth()
  const navigate = useNavigate()
  const [items, setItems] = useState<ToolItem[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [statuses, setStatuses] = useState<ToolStatus[]>([])
  const [conditions, setConditions] = useState<ToolCondition[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [open, setOpen] = useState(false)
  const [editItem, setEditItem] = useState<ToolItem | null>(null)
  const [form, setForm] = useState({ inventory_no: '', description: '', tool_id: '', status_id: '', condition_id: '' })
  const [saving, setSaving] = useState(false)

  // QR anzeigen
  const [qrOpen, setQrOpen] = useState(false)
  const [qrItem, setQrItem] = useState<ToolItem | null>(null)
  const [qrUrl, setQrUrl] = useState<string | null>(null)
  const [qrLoading, setQrLoading] = useState(false)

  // QR scannen
  const scanInputRef = useRef<HTMLInputElement>(null)
  const [scanning, setScanning] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([toolItemsApi.list(), toolsApi.list(), lookupsApi.statuses(), lookupsApi.conditions()])
      .then(([i, t, s, c]) => { setItems(i); setTools(t); setStatuses(s); setConditions(c) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditItem(null); setForm({ inventory_no: '', description: '', tool_id: '', status_id: '', condition_id: '' }); setOpen(true) }
  const openEdit = (item: ToolItem) => {
    setEditItem(item)
    setForm({ inventory_no: item.inventory_no, description: item.description ?? '', tool_id: String(item.tool_id), status_id: String(item.status_id), condition_id: String(item.condition_id) })
    setOpen(true)
  }

  const openQr = async (item: ToolItem) => {
    setQrItem(item)
    setQrUrl(null)
    setQrOpen(true)
    setQrLoading(true)
    try {
      const url = await toolItemsApi.qrCodeBlob(item.id)
      setQrUrl(url)
    } catch { toast.error('QR-Code konnte nicht geladen werden') }
    finally { setQrLoading(false) }
  }

  const handleScanFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setScanning(true)
    try {
      const img = new Image()
      img.src = URL.createObjectURL(file)
      await new Promise(resolve => { img.onload = resolve })
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      canvas.getContext('2d')!.drawImage(img, 0, 0)
      const imageData = canvas.getContext('2d')!.getImageData(0, 0, canvas.width, canvas.height)
      const code = jsQR(imageData.data, imageData.width, imageData.height)
      if (code) {
        // Format: "tool_item:{id}:{inventory_no}"
        const parts = code.data.split(':')
        if (parts[0] === 'tool_item' && parts[2]) {
          setSearch(parts[2])
          toast.success(`QR erkannt: ${parts[2]}`)
        } else {
          setSearch(code.data)
          toast.success('QR erkannt')
        }
      } else {
        toast.error('Kein QR-Code erkannt')
      }
    } catch { toast.error('Fehler beim Lesen des QR-Codes') }
    finally {
      setScanning(false)
      e.target.value = ''
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = { inventory_no: form.inventory_no, description: form.description, tool_id: Number(form.tool_id), status_id: Number(form.status_id), condition_id: Number(form.condition_id) }
      if (editItem) { await toolItemsApi.update(editItem.id, payload); toast.success('Exemplar aktualisiert') }
      else { await toolItemsApi.create(payload); toast.success('Exemplar erstellt') }
      setOpen(false); load()
    } catch { toast.error('Fehler beim Speichern') }
    finally { setSaving(false) }
  }

  const handleDelete = async (item: ToolItem) => {
    if (!confirm(`Exemplar "${item.inventory_no}" löschen?`)) return
    try { await toolItemsApi.delete(item.id); toast.success('Gelöscht'); load() }
    catch { toast.error('Löschen fehlgeschlagen') }
  }

  const handleRetire = async (item: ToolItem) => {
    if (!confirm(`Exemplar "${item.inventory_no}" aussondern?`)) return
    try { await toolItemsApi.retire(item.id); toast.success('Ausgesondert'); load() }
    catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler')
    }
  }

  const filtered = items.filter(i => {
    const matchSearch = i.inventory_no.toLowerCase().includes(search.toLowerCase()) || i.tool.tool_name.toLowerCase().includes(search.toLowerCase())
    const matchStatus = filterStatus === 'all' || i.status.name === filterStatus
    return matchSearch && matchStatus
  })

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Package size={24} />Inventar</h1>
          <p className="text-slate-500 mt-1">{items.length} Exemplare</p>
        </div>
        {isAdmin && (
          <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
            <Plus size={16} className="mr-2" />Neues Exemplar
          </Button>
        )}
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Inventar-Nr. oder Werkzeug…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 pr-9"
          />
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
              <X size={14} />
            </button>
          )}
        </div>

        {/* QR scannen */}
        <Button
          variant="outline"
          title="QR-Code scannen"
          disabled={scanning}
          onClick={() => scanInputRef.current?.click()}
          className="gap-2"
        >
          <ScanLine size={16} />
          {scanning ? 'Lesen…' : 'QR scannen'}
        </Button>
        <input
          ref={scanInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleScanFile}
        />

        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-44"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {statuses.map(s => <SelectItem key={s.id} value={s.name}>{t(toolStatusLabel, s.name)}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {['Inv.-Nr.', 'Werkzeug', 'Kategorie', 'Status', 'Zustand', ''].map(h => (
                  <th key={h} className="px-5 py-3.5 text-left font-semibold text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-5 py-10 text-center text-slate-400">Keine Exemplare gefunden</td></tr>
              ) : filtered.map(item => (
                <tr key={item.id} className="hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => navigate('/inventory/detail', { state: { id: item.id } })}>
                  <td className="px-5 py-3 font-mono text-xs text-slate-600 font-medium">{item.inventory_no}</td>
                  <td className="px-5 py-3 font-medium text-slate-800">{item.tool.tool_name}</td>
                  <td className="px-5 py-3 text-slate-500">{item.tool.category.name}</td>
                  <td className="px-5 py-3">
                    <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', statusColor[item.status.name] ?? 'bg-slate-100 text-slate-600')}>
                      {t(toolStatusLabel, item.status.name)}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', conditionColor[item.condition.name] ?? 'bg-slate-100 text-slate-600')}>
                      {t(toolConditionLabel, item.condition.name)}
                    </span>
                  </td>
                  <td className="px-5 py-3" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-1 justify-end">
                      <Button size="sm" variant="ghost" title="QR-Code anzeigen" onClick={() => openQr(item)}><QrCode size={14} /></Button>
                      {isAdmin && <>
                        <Button size="sm" variant="ghost" onClick={() => openEdit(item)}><Pencil size={14} /></Button>
                        {item.status.name !== 'RETIRED' && (
                          <Button size="sm" variant="ghost" className="text-amber-500 hover:bg-amber-50" title="Aussondern" onClick={() => handleRetire(item)}><Archive size={14} /></Button>
                        )}
                        <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(item)}><Trash2 size={14} /></Button>
                      </>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* QR-Code Dialog */}
      <Dialog open={qrOpen} onOpenChange={o => { setQrOpen(o); if (!o && qrUrl) URL.revokeObjectURL(qrUrl) }}>
        <DialogContent className="max-w-xs">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><QrCode size={18} />QR-Code</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center gap-3 py-2">
            {qrLoading ? (
              <Skeleton className="w-48 h-48" />
            ) : qrUrl ? (
              <img src={qrUrl} alt="QR-Code" className="w-48 h-48" />
            ) : null}
            {qrItem && (
              <div className="text-center text-sm text-slate-600 space-y-0.5">
                <p className="font-mono font-medium">{qrItem.inventory_no}</p>
                <p className="text-slate-500">{qrItem.tool.tool_name}</p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Exemplar Dialog */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editItem ? 'Exemplar bearbeiten' : 'Neues Exemplar'}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Inventar-Nr.</Label>
              <Input value={form.inventory_no} onChange={e => setForm(f => ({ ...f, inventory_no: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Werkzeug</Label>
              <Select value={form.tool_id} onValueChange={v => setForm(f => ({ ...f, tool_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                <SelectContent>{tools.map(t => <SelectItem key={t.id} value={String(t.id)}>{t.tool_name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>Status</Label>
                <Select value={form.status_id} onValueChange={v => setForm(f => ({ ...f, status_id: v }))}>
                  <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                  <SelectContent>{statuses.map(s => <SelectItem key={s.id} value={String(s.id)}>{s.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Zustand</Label>
                <Select value={form.condition_id} onValueChange={v => setForm(f => ({ ...f, condition_id: v }))}>
                  <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                  <SelectContent>{conditions.map(c => <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={saving} className="bg-blue-600 hover:bg-blue-700">{saving ? 'Speichern…' : 'Speichern'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
