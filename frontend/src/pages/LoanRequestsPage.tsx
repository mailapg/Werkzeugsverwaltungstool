import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import jsQR from 'jsqr'
import { loanRequestsApi, lookupsApi, toolsApi, toolItemsApi } from '../api/services'
import type { LoanRequest, LoanRequestStatus, Tool } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Trash2, ClipboardList, CheckCircle, XCircle, X, AlertTriangle, Search, ScanLine } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'
import { loanRequestStatusLabel as statusLabel, t } from '../lib/labels'

const statusColor: Record<string, string> = {
  REQUESTED: 'bg-amber-100 text-amber-700',
  APPROVED: 'bg-emerald-100 text-emerald-700',
  REJECTED: 'bg-red-100 text-red-700',
  CANCELLED: 'bg-slate-100 text-slate-500',
}

interface RequestItem { tool_id: string; quantity: number }

export default function LoanRequestsPage() {
  const { user, isAdmin, isManager } = useAuth()
  const [searchParams] = useSearchParams()
  const [requests, setRequests] = useState<LoanRequest[]>([])
  const [statuses, setStatuses] = useState<LoanRequestStatus[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [filterStatus, setFilterStatus] = useState(searchParams.get('filter') ?? 'all')
  const [search, setSearch] = useState('')
  const [qrToolId, setQrToolId] = useState<number | null>(null)
  const [scanning, setScanning] = useState(false)
  const scanInputRef = useRef<HTMLInputElement>(null)

  // Create dialog
  const [createOpen, setCreateOpen] = useState(false)
  const [daysNeeded, setDaysNeeded] = useState('')
  const [comment, setComment] = useState('')
  const [items, setItems] = useState<RequestItem[]>([{ tool_id: '', quantity: 1 }])
  const [saving, setSaving] = useState(false)

  // Detail dialog
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailRequest, setDetailRequest] = useState<LoanRequest | null>(null)

  const openDetail = (req: LoanRequest) => {
    setDetailRequest(req)
    setDetailOpen(true)
  }

  // Decide dialog
  const [decideOpen, setDecideOpen] = useState(false)
  const [decideRequest, setDecideRequest] = useState<LoanRequest | null>(null)
  const [decideStatusId, setDecideStatusId] = useState('')
  const [decideComment, setDecideComment] = useState('')
  const [deciding, setDeciding] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([loanRequestsApi.list(), lookupsApi.loanRequestStatuses(), toolsApi.list()])
      .then(([r, s, t]) => { setRequests(r); setStatuses(s); setTools(t) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

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
        if (parts[0] === 'tool_item' && parts[1]) {
          try {
            const item = await toolItemsApi.get(Number(parts[1]))
            setSearch('')
            setQrToolId(item.tool_id)
            toast.success(`QR erkannt: ${parts[2] ?? parts[1]}`)
          } catch {
            setQrToolId(null)
            toast.error('Exemplar nicht gefunden')
          }
        } else {
          setQrToolId(null)
          setSearch(code.data)
          toast.success('QR erkannt')
        }
      } else {
        toast.error('Kein QR-Code erkannt')
      }
    } catch { toast.error('Fehler beim Lesen des QR-Codes') }
    finally { setScanning(false); e.target.value = '' }
  }

  const openDecide = (req: LoanRequest) => {
    setDecideRequest(req)
    setDecideStatusId('')
    setDecideComment('')
    setDecideOpen(true)
  }

  const openCreate = () => {
    setDaysNeeded('')
    setComment('')
    setItems([{ tool_id: '', quantity: 1 }])
    setCreateOpen(true)
  }

  const addItem = () => setItems(i => [...i, { tool_id: '', quantity: 1 }])
  const removeItem = (idx: number) => setItems(i => i.filter((_, n) => n !== idx))
  const updateItem = (idx: number, field: keyof RequestItem, value: string | number) =>
    setItems(i => i.map((item, n) => n === idx ? { ...item, [field]: value } : item))

  const handleCreate = async () => {
    if (!daysNeeded || Number(daysNeeded) < 1 || items.some(i => !i.tool_id)) {
      toast.error('Bitte alle Felder ausfüllen')
      return
    }
    setSaving(true)
    try {
      const newRequest = await loanRequestsApi.create({
        requester_user_id: user!.id,
        days_needed: Number(daysNeeded),
        comment: comment || null,
        items: items.map(i => ({ tool_id: Number(i.tool_id), quantity: i.quantity })),
      })

      // DEPARTMENT_MANAGER genehmigt die eigene Anfrage sofort → Ausleihe wird direkt erstellt
      if (isManager && !isAdmin) {
        const approvedStatus = statuses.find(s => s.name === 'APPROVED')
        if (approvedStatus) {
          await loanRequestsApi.decide(newRequest.id, {
            approver_user_id: user.id,
            status_id: approvedStatus.id,
            decision_comment: null,
          })
          toast.success('Ausleihe erfolgreich erstellt')
        }
      } else {
        toast.success('Anfrage gestellt')
      }

      setCreateOpen(false)
      load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler beim Erstellen')
    } finally { setSaving(false) }
  }

  const handleDecide = async () => {
    if (!decideRequest || !decideStatusId) { toast.error('Status wählen'); return }
    setDeciding(true)
    try {
      await loanRequestsApi.decide(decideRequest.id, {
        approver_user_id: user!.id,
        status_id: Number(decideStatusId),
        decision_comment: decideComment || null,
      })
      toast.success('Entscheidung gespeichert')
      setDecideOpen(false)
      setFilterStatus('all')
      load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler')
    }
    finally { setDeciding(false) }
  }

  const handleDelete = async (req: LoanRequest) => {
    if (!confirm('Anfrage löschen?')) return
    try { await loanRequestsApi.delete(req.id); toast.success('Gelöscht'); load() }
    catch { toast.error('Fehler') }
  }

  const now = new Date()
  const isOverdue = (req: LoanRequest) =>
    !!req.due_at && (req.status.name === 'APPROVED' || req.status.name === 'REQUESTED') && new Date(req.due_at) < now

  const filtered = requests
    .filter(r => filterStatus === 'all' || r.status.name === filterStatus)
    .filter(r => {
      if (qrToolId !== null) {
        // QR-Scan: exakter Abgleich per tool_id → zeigt auch Anfragen mit mehreren Werkzeugen
        return r.items.some(i => i.tool_id === qrToolId)
      }
      if (!search.trim()) return true
      return (
        r.items.some(i => i.tool.tool_name.toLowerCase().includes(search.toLowerCase())) ||
        `${r.requester.firstname} ${r.requester.lastname}`.toLowerCase().includes(search.toLowerCase())
      )
    })

  const decideableStatuses = statuses.filter(s => s.name === 'APPROVED' || s.name === 'REJECTED')

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <ClipboardList size={24} />Ausleiheanfragen
          </h1>
          <p className="text-slate-500 mt-1">{requests.length} Anfragen insgesamt</p>
        </div>
        <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus size={16} className="mr-2" />Neue Anfrage
        </Button>
      </div>

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Werkzeug oder Antragsteller…"
            value={search}
            onChange={e => { setSearch(e.target.value); setQrToolId(null) }}
            className="pl-9 pr-9"
          />
          {search && (
            <button onClick={() => { setSearch(''); setQrToolId(null) }} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
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
            {statuses.map(s => <SelectItem key={s.id} value={s.name}>{t(statusLabel, s.name)}</SelectItem>)}
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
                {['Antragsteller', 'Werkzeuge', 'Status', 'Fällig am', 'Beantragt am', ''].map(h => (
                  <th key={h} className="px-5 py-3.5 text-left font-semibold text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-5 py-10 text-center text-slate-400">Keine Anfragen gefunden</td></tr>
              ) : filtered.map(req => (
                <tr key={req.id} className={cn('cursor-pointer', isOverdue(req) ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-slate-50')} onClick={() => openDetail(req)}>
                  <td className="px-5 py-3 font-medium text-slate-800">
                    <div className="flex items-center gap-2">
                      {isOverdue(req) && <AlertTriangle size={13} className="text-red-500 shrink-0" />}
                      {req.requester.firstname} {req.requester.lastname}
                    </div>
                  </td>
                  <td className="px-5 py-3 text-slate-600 text-xs">
                    {req.items.map(i => `${i.tool.tool_name} ×${i.quantity}`).join(', ')}
                  </td>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2">
                      <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', statusColor[req.status.name] ?? 'bg-slate-100 text-slate-600')}>
                        {statusLabel[req.status.name] ?? req.status.name}
                      </span>
                      {isOverdue(req) && <span className="text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">Überfällig</span>}
                    </div>
                  </td>
                  <td className={cn('px-5 py-3 font-medium', isOverdue(req) ? 'text-red-600' : 'text-slate-500')}>
                    {req.due_at
                      ? new Date(req.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
                      : req.days_needed ? <span className="text-slate-400 italic text-xs">{req.days_needed} Tage (nach Genehmigung)</span> : '–'}
                  </td>
                  <td className="px-5 py-3 text-slate-500">{new Date(req.requested_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                  <td className="px-5 py-3" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-1 justify-end">
                      {isManager && req.status.name === 'REQUESTED' && (
                        <Button size="sm" variant="ghost" className="text-emerald-600 hover:bg-emerald-50" onClick={() => openDecide(req)}>
                          <CheckCircle size={14} className="mr-1" />Entscheiden
                        </Button>
                      )}
                      {isAdmin && (
                        <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(req)}>
                          <Trash2 size={14} />
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ClipboardList size={18} />
              Anfrage #{detailRequest?.id}
            </DialogTitle>
          </DialogHeader>
          {detailRequest && (
            <div className="space-y-4 py-1">
              <div className="flex items-center justify-between">
                <span className={cn('text-xs font-semibold px-3 py-1 rounded-full', statusColor[detailRequest.status.name] ?? 'bg-slate-100 text-slate-600')}>
                  {statusLabel[detailRequest.status.name] ?? detailRequest.status.name}
                </span>
                <span className="text-xs text-slate-400">#{detailRequest.id}</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="space-y-0.5">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Antragsteller</p>
                  <p className="font-medium text-slate-800">{detailRequest.requester.firstname} {detailRequest.requester.lastname}</p>
                  <p className="text-slate-500 text-xs">{detailRequest.requester.email}</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Beantragt am</p>
                  <p className="text-slate-700">{new Date(detailRequest.requested_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Fällig am</p>
                  <p className="text-slate-700">
                    {detailRequest.due_at
                      ? new Date(detailRequest.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })
                      : detailRequest.days_needed
                        ? <span className="italic text-slate-400">{detailRequest.days_needed} Tage – wird bei Genehmigung berechnet</span>
                        : '–'}
                  </p>
                </div>
                {detailRequest.decision_at && (
                  <div className="space-y-0.5">
                    <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Entschieden am</p>
                    <p className="text-slate-700">{new Date(detailRequest.decision_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</p>
                  </div>
                )}
              </div>

              {detailRequest.comment && (
                <div className="bg-slate-50 rounded-lg p-3 text-sm">
                  <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Kommentar</p>
                  <p className="text-slate-700">{detailRequest.comment}</p>
                </div>
              )}

              <div>
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-2">Werkzeuge</p>
                <div className="space-y-1.5">
                  {detailRequest.items.map(item => (
                    <div key={item.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2 text-sm">
                      <span className="text-slate-700 font-medium">{item.tool.tool_name}</span>
                      <span className="text-slate-500 text-xs bg-white border border-slate-200 rounded px-2 py-0.5">×{item.quantity}</span>
                    </div>
                  ))}
                </div>
              </div>

              {(detailRequest.approver || detailRequest.decision_comment) && (
                <div className="border-t border-slate-100 pt-3 space-y-2 text-sm">
                  {detailRequest.approver && (
                    <div className="space-y-0.5">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Entschieden von</p>
                      <p className="text-slate-700">{detailRequest.approver.firstname} {detailRequest.approver.lastname}</p>
                    </div>
                  )}
                  {detailRequest.decision_comment && (
                    <div className="bg-slate-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">Entscheidungskommentar</p>
                      <p className="text-slate-700">{detailRequest.decision_comment}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailOpen(false)}>Schließen</Button>
            {isManager && detailRequest?.status.name === 'REQUESTED' && (
              <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setDetailOpen(false); openDecide(detailRequest!) }}>
                <CheckCircle size={14} className="mr-2" />Entscheiden
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{isManager && !isAdmin ? 'Neue Ausleihe' : 'Neue Ausleiheanfrage'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Wie viele Tage benötigst du?</Label>
              <Input
                type="number"
                min={1}
                placeholder="z.B. 7"
                value={daysNeeded}
                onChange={e => setDaysNeeded(e.target.value)}
              />
              <p className="text-xs text-slate-400">Das Fälligkeitsdatum wird nach der Genehmigung berechnet.</p>
            </div>
            <div className="space-y-1.5">
              <Label>Kommentar (optional)</Label>
              <Input value={comment} onChange={e => setComment(e.target.value)} placeholder="Grund der Anfrage…" />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Werkzeuge</Label>
                <Button type="button" size="sm" variant="outline" onClick={addItem}><Plus size={13} className="mr-1" />Hinzufügen</Button>
              </div>
              {items.map((item, idx) => (
                <div key={idx} className="flex gap-2 items-center">
                  <Select value={item.tool_id} onValueChange={v => updateItem(idx, 'tool_id', v)}>
                    <SelectTrigger className="flex-1"><SelectValue placeholder="Werkzeug wählen…" /></SelectTrigger>
                    <SelectContent>{tools.map(t => <SelectItem key={t.id} value={String(t.id)}>{t.tool_name}</SelectItem>)}</SelectContent>
                  </Select>
                  <Input
                    type="number" min={1} value={item.quantity}
                    onChange={e => updateItem(idx, 'quantity', Number(e.target.value))}
                    className="w-20"
                  />
                  {items.length > 1 && (
                    <Button type="button" size="sm" variant="ghost" className="text-red-500" onClick={() => removeItem(idx)}>
                      <X size={13} />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Abbrechen</Button>
            <Button onClick={handleCreate} disabled={saving} className="bg-blue-600 hover:bg-blue-700">
              {saving ? 'Erstellen…' : isManager && !isAdmin ? 'Ausleihe erstellen' : 'Anfrage senden'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Decide Dialog */}
      <Dialog open={decideOpen} onOpenChange={setDecideOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Anfrage entscheiden</DialogTitle></DialogHeader>
          {decideRequest && (
            <div className="space-y-4 py-2">
              <div className="bg-slate-50 rounded-lg p-3 text-sm space-y-1">
                <p><span className="text-slate-500">Antragsteller:</span> <span className="font-medium">{decideRequest.requester.firstname} {decideRequest.requester.lastname}</span></p>
                <p><span className="text-slate-500">Werkzeuge:</span> {decideRequest.items.map(i => `${i.tool.tool_name} ×${i.quantity}`).join(', ')}</p>
                <p><span className="text-slate-500">Benötigte Tage:</span> {decideRequest.days_needed ?? '–'}</p>
                {decideRequest.comment && <p><span className="text-slate-500">Kommentar:</span> {decideRequest.comment}</p>}
              </div>
              <div className="flex gap-3">
                <Button
                  className={cn('flex-1', decideStatusId === String(decideableStatuses.find(s => s.name === 'APPROVED')?.id) ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-slate-100 text-slate-700 hover:bg-emerald-50')}
                  onClick={() => setDecideStatusId(String(decideableStatuses.find(s => s.name === 'APPROVED')?.id ?? ''))}
                >
                  <CheckCircle size={15} className="mr-2" />Genehmigen
                </Button>
                <Button
                  className={cn('flex-1', decideStatusId === String(decideableStatuses.find(s => s.name === 'REJECTED')?.id) ? 'bg-red-600 hover:bg-red-700 text-white' : 'bg-slate-100 text-slate-700 hover:bg-red-50')}
                  onClick={() => setDecideStatusId(String(decideableStatuses.find(s => s.name === 'REJECTED')?.id ?? ''))}
                >
                  <XCircle size={15} className="mr-2" />Ablehnen
                </Button>
              </div>
              <div className="space-y-1.5">
                <Label>Kommentar (optional)</Label>
                <Input value={decideComment} onChange={e => setDecideComment(e.target.value)} placeholder="Begründung…" />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDecideOpen(false)}>Abbrechen</Button>
            <Button onClick={handleDecide} disabled={deciding || !decideStatusId} className="bg-blue-600 hover:bg-blue-700">
              {deciding ? 'Speichern…' : 'Bestätigen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
