import { useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import jsQR from 'jsqr'
import { loansApi, lookupsApi } from '../api/services'
import type { Loan, ToolCondition } from '../types'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Label } from '../components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Input } from '../components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Trash2, ArrowLeftRight, RotateCcw, AlertTriangle, Search, ScanLine, X } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../lib/utils'
import { toolConditionLabel, t } from '../lib/labels'

type FilterMode = 'all' | 'active' | 'overdue' | 'returned'

function getLoanStatus(loan: Loan): { label: string; color: string } {
  if (loan.returned_at) return { label: 'Zurückgegeben', color: 'bg-slate-100 text-slate-500' }
  if (loan.is_overdue) return { label: 'Überfällig', color: 'bg-red-100 text-red-700' }
  return { label: 'Aktiv', color: 'bg-blue-100 text-blue-700' }
}

interface ReturnItemForm {
  loan_item_id: number
  tool_name: string
  inventory_no: string
  return_condition_id: string
  return_comment: string
}

export default function LoansPage() {
  const { user, isAdmin } = useAuth()
  const [searchParams] = useSearchParams()
  const [loans, setLoans] = useState<Loan[]>([])
  const [conditions, setConditions] = useState<ToolCondition[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterMode>((searchParams.get('filter') as FilterMode) ?? 'all')
  const [search, setSearch] = useState('')
  const [scanning, setScanning] = useState(false)
  const scanInputRef = useRef<HTMLInputElement>(null)

  // Detail dialog
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoan, setDetailLoan] = useState<Loan | null>(null)

  // Return dialog
  const [returnOpen, setReturnOpen] = useState(false)
  const [returnLoan, setReturnLoan] = useState<Loan | null>(null)
  const [returnItems, setReturnItems] = useState<ReturnItemForm[]>([])
  const [returning, setReturning] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([loansApi.list(), lookupsApi.conditions()])
      .then(([l, c]) => { setLoans(l); setConditions(c) })
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

  const openDetail = (loan: Loan) => { setDetailLoan(loan); setDetailOpen(true) }

  const openReturn = (loan: Loan) => {
    setReturnLoan(loan)
    setReturnItems(loan.items.map(item => ({
      loan_item_id: item.id,
      tool_name: item.tool_item.tool.tool_name,
      inventory_no: item.tool_item.inventory_no,
      return_condition_id: '',
      return_comment: '',
    })))
    setReturnOpen(true)
  }

  const updateReturnItem = (idx: number, field: keyof ReturnItemForm, value: string) =>
    setReturnItems(items => items.map((item, n) => n === idx ? { ...item, [field]: value } : item))

  const handleReturn = async () => {
    if (!returnLoan) return
    if (returnItems.some(i => !i.return_condition_id)) {
      toast.error('Bitte für alle Exemplare einen Zustand auswählen')
      return
    }
    setReturning(true)
    try {
      await loansApi.return(returnLoan.id, {
        returned_by_user_id: user!.id,
        items: returnItems.map(i => ({
          loan_item_id: i.loan_item_id,
          return_condition_id: Number(i.return_condition_id),
          return_comment: i.return_comment || null,
        })),
      })
      toast.success('Ausleihe zurückgegeben')
      setReturnOpen(false)
      load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler')
    }
    finally { setReturning(false) }
  }

  const handleDelete = async (loan: Loan) => {
    if (!confirm('Ausleihe löschen?')) return
    try { await loansApi.delete(loan.id); toast.success('Gelöscht'); load() }
    catch { toast.error('Fehler') }
  }

  const filtered = loans
    .filter(l => {
      if (filter === 'active') return !l.returned_at && !l.is_overdue
      if (filter === 'overdue') return !l.returned_at && l.is_overdue
      if (filter === 'returned') return !!l.returned_at
      return true
    })
    .filter(l => !search.trim() ||
      l.items.some(i =>
        i.tool_item.inventory_no.toLowerCase().includes(search.toLowerCase()) ||
        i.tool_item.tool.tool_name.toLowerCase().includes(search.toLowerCase())
      ) ||
      `${l.borrower.firstname} ${l.borrower.lastname}`.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => {
      const aActive = !a.returned_at ? 0 : 1
      const bActive = !b.returned_at ? 0 : 1
      if (aActive !== bActive) return aActive - bActive
      return new Date(a.due_at).getTime() - new Date(b.due_at).getTime()
    })

  const overdueCount = loans.filter(l => !l.returned_at && l.is_overdue).length
  const detailStatus = detailLoan ? getLoanStatus(detailLoan) : null

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <ArrowLeftRight size={24} />Ausleihen
          </h1>
          <p className="text-slate-500 mt-1">{loans.length} Ausleihen insgesamt</p>
        </div>
      </div>

      {overdueCount > 0 && (
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 rounded-xl px-5 py-3 text-sm text-red-700">
          <AlertTriangle size={18} />
          <span><strong>{overdueCount}</strong> überfällige Ausleihe{overdueCount > 1 ? 'n' : ''}</span>
        </div>
      )}

      <div className="flex gap-3 flex-wrap">
        <div className="relative flex-1 min-w-48 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Inventar-Nr., Werkzeug oder Ausleiher…"
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
      </div>

      <div className="flex gap-2">
        {([['all', 'Alle'], ['active', 'Aktiv'], ['overdue', 'Überfällig'], ['returned', 'Zurückgegeben']] as const).map(([val, label]) => (
          <button
            key={val}
            onClick={() => setFilter(val)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filter === val ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            )}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {['Ausleiher', 'Exemplare', 'Ausgegeben am', 'Fällig am', 'Zurück am', 'Status', ''].map(h => (
                  <th key={h} className="px-5 py-3.5 text-left font-semibold text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.length === 0 ? (
                <tr><td colSpan={6} className="px-5 py-10 text-center text-slate-400">Keine Ausleihen gefunden</td></tr>
              ) : filtered.map(loan => {
                const status = getLoanStatus(loan)
                return (
                  <tr key={loan.id} className={cn('cursor-pointer', loan.is_overdue ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-slate-50')} onClick={() => openDetail(loan)}>
                    <td className="px-5 py-3 font-medium text-slate-800">{loan.borrower.firstname} {loan.borrower.lastname}</td>
                    <td className="px-5 py-3 text-slate-500 text-xs">
                      {loan.items.map(i => i.tool_item.inventory_no).join(', ')}
                    </td>
                    <td className="px-5 py-3 text-slate-500">{new Date(loan.issued_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                    <td className={cn('px-5 py-3 font-medium', loan.is_overdue ? 'text-red-600' : 'text-slate-500')}>{new Date(loan.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                    <td className="px-5 py-3 text-slate-500">{loan.returned_at ? new Date(loan.returned_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '–'}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-1.5">
                        {!loan.returned_at && (
                          <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-blue-100 text-blue-700">
                            Aktiv
                          </span>
                        )}
                        {loan.returned_at && (
                          <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-slate-100 text-slate-500">
                            Zurückgegeben
                          </span>
                        )}
                        {loan.is_overdue && (
                          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-red-100 text-red-700 flex items-center gap-1">
                            <AlertTriangle size={11} />Überfällig
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-5 py-3" onClick={e => e.stopPropagation()}>
                      <div className="flex gap-1 justify-end">
                        {!loan.returned_at && (
                          <Button size="sm" variant="ghost" className="text-blue-600 hover:bg-blue-50" onClick={() => openReturn(loan)}>
                            <RotateCcw size={14} className="mr-1" />Zurückgeben
                          </Button>
                        )}
                        {isAdmin && (
                          <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(loan)}>
                            <Trash2 size={14} />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ArrowLeftRight size={18} />Ausleihe #{detailLoan?.id}
            </DialogTitle>
          </DialogHeader>
          {detailLoan && detailStatus && (
            <div className="space-y-4 py-1">
              <div className="flex items-center gap-2">
                <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full', detailStatus.color)}>{detailStatus.label}</span>
                {detailLoan.is_overdue && <span className="text-xs text-red-600 font-medium">Überfällig seit {new Date(detailLoan.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>}
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-slate-50 rounded-lg p-3 space-y-1">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Ausleiher</p>
                  <p className="font-medium text-slate-800">{detailLoan.borrower.firstname} {detailLoan.borrower.lastname}</p>
                  <p className="text-slate-500 text-xs">{detailLoan.borrower.email}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3 space-y-1">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Ausgegeben von</p>
                  <p className="font-medium text-slate-800">{detailLoan.issuer.firstname} {detailLoan.issuer.lastname}</p>
                  <p className="text-slate-500 text-xs">{detailLoan.issuer.email}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 text-sm">
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Ausgegeben am</p>
                  <p className="text-slate-700">{new Date(detailLoan.issued_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Fällig am</p>
                  <p className={cn('font-medium', detailLoan.is_overdue ? 'text-red-600' : 'text-slate-700')}>
                    {new Date(detailLoan.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                  </p>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">Zurück am</p>
                  <p className="text-slate-700">{detailLoan.returned_at ? new Date(detailLoan.returned_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '–'}</p>
                </div>
              </div>

              {detailLoan.return_processor && (
                <div className="text-sm bg-slate-50 rounded-lg p-3">
                  <span className="text-slate-500">Rückgabe verarbeitet von: </span>
                  <span className="font-medium text-slate-700">{detailLoan.return_processor.firstname} {detailLoan.return_processor.lastname}</span>
                </div>
              )}

              {detailLoan.comment && (
                <div className="text-sm bg-slate-50 rounded-lg p-3">
                  <span className="text-slate-500">Kommentar: </span>
                  <span className="text-slate-700">{detailLoan.comment}</span>
                </div>
              )}

              <div>
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">Ausgeliehene Exemplare</p>
                <div className="space-y-2">
                  {detailLoan.items.map(item => (
                    <div key={item.id} className="border border-slate-200 rounded-lg p-3 flex items-center justify-between text-sm">
                      <div>
                        <p className="font-medium text-slate-800">{item.tool_item.tool.tool_name}</p>
                        <p className="font-mono text-xs text-slate-500">{item.tool_item.inventory_no}</p>
                      </div>
                      {item.return_condition && (
                        <Badge variant="secondary">{t(toolConditionLabel, item.return_condition.name)}</Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            {detailLoan && !detailLoan.returned_at && (
              <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setDetailOpen(false); openReturn(detailLoan) }}>
                <RotateCcw size={14} className="mr-2" />Zurückgeben
              </Button>
            )}
            <Button variant="outline" onClick={() => setDetailOpen(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Return Dialog */}
      <Dialog open={returnOpen} onOpenChange={setReturnOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle>Ausleihe zurückgeben</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            {returnLoan && (
              <div className="bg-slate-50 rounded-lg p-3 text-sm space-y-1">
                <p><span className="text-slate-500">Ausleiher:</span> <span className="font-medium">{returnLoan.borrower.firstname} {returnLoan.borrower.lastname}</span></p>
                <p><span className="text-slate-500">Fällig am:</span> {new Date(returnLoan.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</p>
              </div>
            )}
            <p className="text-sm font-medium text-slate-700">Zustand der Exemplare</p>
            <div className="space-y-3">
              {returnItems.map((item, idx) => (
                <div key={idx} className="border border-slate-200 rounded-lg p-3 space-y-2">
                  <p className="text-sm font-medium text-slate-800">{item.tool_name} <span className="font-mono text-xs text-slate-500">({item.inventory_no})</span></p>
                  <div className="space-y-1">
                    <Label className="text-xs">Zustand *</Label>
                    <Select value={item.return_condition_id} onValueChange={v => updateReturnItem(idx, 'return_condition_id', v)}>
                      <SelectTrigger><SelectValue placeholder="Zustand wählen…" /></SelectTrigger>
                      <SelectContent>{conditions.map(c => <SelectItem key={c.id} value={String(c.id)}>{t(toolConditionLabel, c.name)}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Kommentar (optional)</Label>
                    <Input
                      value={item.return_comment}
                      onChange={e => updateReturnItem(idx, 'return_comment', e.target.value)}
                      placeholder="z.B. leichte Gebrauchsspuren…"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setReturnOpen(false)}>Abbrechen</Button>
            <Button onClick={handleReturn} disabled={returning} className="bg-blue-600 hover:bg-blue-700">
              {returning ? 'Verarbeiten…' : 'Zurückgeben bestätigen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
