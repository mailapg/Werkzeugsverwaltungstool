import { useEffect, useRef, useState } from 'react'
import jsQR from 'jsqr'
import { issuesApi, toolItemsApi, lookupsApi } from '../api/services'
import type { ToolItemIssue, ToolItem, ToolItemIssueStatus } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, AlertTriangle, Search, ScanLine, X, Wrench, CalendarDays, User } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'
import { issueStatusLabel, t } from '../lib/labels'

const statusColor: Record<string, string> = {
  OPEN: 'bg-red-100 text-red-700',
  IN_PROGRESS: 'bg-amber-100 text-amber-700',
  RESOLVED: 'bg-emerald-100 text-emerald-700',
  CLOSED: 'bg-slate-100 text-slate-500',
}

export default function IssuesPage() {
  const { user, isAdmin, isManager } = useAuth()
  const [issues, setIssues] = useState<ToolItemIssue[]>([])
  const [toolItems, setToolItems] = useState<ToolItem[]>([])
  const [issueStatuses, setIssueStatuses] = useState<ToolItemIssueStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editIssue, setEditIssue] = useState<ToolItemIssue | null>(null)
  const [form, setForm] = useState({ title: '', description: '', tool_item_id: '', status_id: '' })
  const [saving, setSaving] = useState(false)
  const [detailIssue, setDetailIssue] = useState<ToolItemIssue | null>(null)
  const [detailOpen, setDetailOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [scanning, setScanning] = useState(false)
  const scanInputRef = useRef<HTMLInputElement>(null)

  const load = () => {
    setLoading(true)
    Promise.allSettled([issuesApi.list(), toolItemsApi.list(), lookupsApi.issueStatuses()])
      .then(([i, t, s]) => {
        if (i.status === 'fulfilled') setIssues(i.value)
        if (t.status === 'fulfilled') setToolItems(t.value)
        if (s.status === 'fulfilled') setIssueStatuses(s.value)
      })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditIssue(null); setForm({ title: '', description: '', tool_item_id: '', status_id: '' }); setOpen(true) }
  const openEdit = (issue: ToolItemIssue) => {
    setEditIssue(issue)
    setForm({ title: issue.title, description: issue.description ?? '', tool_item_id: String(issue.tool_item_id), status_id: String(issue.status_id) })
    setOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (editIssue) {
        await issuesApi.update(editIssue.id, { status_id: Number(form.status_id), title: form.title, description: form.description })
        toast.success('Meldung aktualisiert')
      } else {
        await issuesApi.create({ title: form.title, description: form.description, tool_item_id: Number(form.tool_item_id), reported_by_user_id: user!.id, status_id: Number(form.status_id) })
        toast.success('Meldung erstellt')
      }
      setOpen(false); load()
    } catch { toast.error('Fehler') }
    finally { setSaving(false) }
  }

  const handleDelete = async (issue: ToolItemIssue) => {
    if (!confirm('Meldung löschen?')) return
    try { await issuesApi.delete(issue.id); toast.success('Gelöscht'); load() }
    catch { toast.error('Fehler') }
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
    finally { setScanning(false); e.target.value = '' }
  }

  const filtered = issues
    .filter(issue => filterStatus === 'all' || issue.status.name === filterStatus)
    .filter(issue => !search.trim() ||
      issue.tool_item.inventory_no.toLowerCase().includes(search.toLowerCase()) ||
      issue.tool_item.tool.tool_name.toLowerCase().includes(search.toLowerCase()) ||
      issue.title.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => new Date(b.reported_at).getTime() - new Date(a.reported_at).getTime()
    )

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><AlertTriangle size={24} />Meldungen</h1>
          <p className="text-slate-500 mt-1">{issues.length} Meldungen insgesamt</p>
        </div>
        <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus size={16} className="mr-2" />Neue Meldung
        </Button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Inventar-Nr., Werkzeug oder Titel…"
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
        <input ref={scanInputRef} type="file" accept="image/*" capture="environment" className="hidden" onChange={handleScanFile} />
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-48"><SelectValue placeholder="Status" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Alle Status</SelectItem>
            {issueStatuses.map(s => <SelectItem key={s.id} value={s.name}>{t(issueStatusLabel, s.name)}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {['Titel', 'Exemplar', 'Gemeldet von', 'Status', 'Datum', ''].map(h => (
                  <th key={h} className="px-5 py-3.5 text-left font-semibold text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-5 py-10 text-center text-slate-400">Keine Meldungen gefunden</td></tr>
              ) : filtered.map(issue => (
                <tr key={issue.id} className="hover:bg-slate-50 cursor-pointer" onClick={() => { setDetailIssue(issue); setDetailOpen(true) }}>
                  <td className="px-5 py-3 font-medium text-slate-800">{issue.title}</td>
                  <td className="px-5 py-3 text-slate-500 font-mono text-xs">{issue.tool_item.inventory_no}</td>
                  <td className="px-5 py-3 text-slate-600">{issue.reported_by.firstname} {issue.reported_by.lastname}</td>
                  <td className="px-5 py-3">
                    <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', statusColor[issue.status.name] ?? 'bg-slate-100 text-slate-600')}>
                      {t(issueStatusLabel, issue.status.name)}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-500">{new Date(issue.reported_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                  <td className="px-5 py-3" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-1 justify-end">
                      {isManager && <Button size="sm" variant="ghost" onClick={() => openEdit(issue)}><Pencil size={14} /></Button>}
                      {isAdmin && <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(issue)}><Trash2 size={14} /></Button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {detailIssue && (
        <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <AlertTriangle size={18} />
                {detailIssue.title}
              </DialogTitle>
            </DialogHeader>
            <div className="text-sm divide-y divide-slate-100">
              <div className="flex items-center py-3 gap-3">
                <Wrench size={14} className="text-slate-400 shrink-0" />
                <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Werkzeug</span>
                <span className="text-slate-800">{detailIssue.tool_item.tool.tool_name}</span>
              </div>
              <div className="flex items-center py-3 gap-3">
                <Wrench size={14} className="text-slate-400 shrink-0" />
                <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Inventar-Nr.</span>
                <span className="font-mono text-xs text-slate-800">{detailIssue.tool_item.inventory_no}</span>
              </div>
              <div className="flex items-center py-3 gap-3">
                <User size={14} className="text-slate-400 shrink-0" />
                <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Gemeldet von</span>
                <span className="text-slate-800">{detailIssue.reported_by.firstname} {detailIssue.reported_by.lastname}</span>
              </div>
              <div className="flex items-center py-3 gap-3">
                <CalendarDays size={14} className="text-slate-400 shrink-0" />
                <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Gemeldet am</span>
                <span className="text-slate-800">{new Date(detailIssue.reported_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
              </div>
              <div className="flex items-center py-3 gap-3">
                <AlertTriangle size={14} className="text-slate-400 shrink-0" />
                <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Status</span>
                <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', statusColor[detailIssue.status.name] ?? 'bg-slate-100 text-slate-600')}>
                  {t(issueStatusLabel, detailIssue.status.name)}
                </span>
              </div>
              {detailIssue.resolved_at && (
                <div className="flex items-center py-3 gap-3">
                  <CalendarDays size={14} className="text-slate-400 shrink-0" />
                  <span className="w-32 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Gelöst am</span>
                  <span className="text-slate-800">{new Date(detailIssue.resolved_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
                </div>
              )}
            </div>
            {detailIssue.description && (
              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1.5">Beschreibung</p>
                <p className="text-slate-700 bg-slate-50 rounded-lg px-3 py-2 text-sm">{detailIssue.description}</p>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setDetailOpen(false)}>Schließen</Button>
              {isManager && (
                <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setDetailOpen(false); openEdit(detailIssue) }}>
                  <Pencil size={14} className="mr-2" />Bearbeiten
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editIssue ? 'Meldung bearbeiten' : 'Neue Meldung'}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Titel</Label>
              <Input value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Beschreibung</Label>
              <Input value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
            </div>
            {!editIssue && (
              <div className="space-y-1.5">
                <Label>Exemplar</Label>
                <Select value={form.tool_item_id} onValueChange={v => setForm(f => ({ ...f, tool_item_id: v }))}>
                  <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                  <SelectContent>{toolItems.map(t => <SelectItem key={t.id} value={String(t.id)}>{t.inventory_no} – {t.tool.tool_name}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            )}
            <div className="space-y-1.5">
              <Label>Status</Label>
              <Select value={form.status_id} onValueChange={v => setForm(f => ({ ...f, status_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                <SelectContent>{issueStatuses.map(s => <SelectItem key={s.id} value={String(s.id)}>{t(issueStatusLabel, s.name)}</SelectItem>)}</SelectContent>
              </Select>
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
