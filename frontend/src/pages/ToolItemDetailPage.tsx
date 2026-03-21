import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { toolItemsApi } from '../api/services'
import type { ToolItem, ToolItemHistoryEntry } from '../types'
import { Button } from '../components/ui/button'
import { Skeleton } from '../components/ui/skeleton'
import { ArrowLeft, Package, Clock, QrCode, CheckCircle, XCircle, AlertTriangle, TrendingUp, CalendarDays, RotateCcw } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { cn } from '../lib/utils'
import { toolStatusLabel, toolConditionLabel, t } from '../lib/labels'

const statusColor: Record<string, string> = {
  AVAILABLE: 'bg-emerald-100 text-emerald-700',
  LOANED:    'bg-blue-100 text-blue-700',
  DEFECT:    'bg-red-100 text-red-700',
  MAINTENANCE: 'bg-amber-100 text-amber-700',
  RETIRED:   'bg-slate-100 text-slate-500',
}

const conditionColor: Record<string, string> = {
  OK:    'bg-emerald-100 text-emerald-700',
  WORN:  'bg-amber-100 text-amber-700',
  DEFECT: 'bg-red-100 text-red-700',
}
const statusIcon: Record<string, React.ReactNode> = {
  AVAILABLE: <CheckCircle size={13} />, LOANED: <Clock size={13} />,
  DEFECT: <XCircle size={13} />, MAINTENANCE: <AlertTriangle size={13} />, RETIRED: <XCircle size={13} />,
}

function StatCard({ icon, label, value, sub }: { icon: React.ReactNode; label: string; value: string; sub?: string }) {
  return (
    <div className="bg-slate-50 rounded-xl p-4 flex items-start gap-3">
      <div className="text-blue-500 mt-0.5">{icon}</div>
      <div>
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">{label}</p>
        <p className="text-2xl font-bold text-slate-800 leading-tight">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function ToolItemDetailPage() {
  const navigate = useNavigate()
  const { state } = useLocation()
  const id = (state as { id?: number })?.id
  const [item, setItem] = useState<ToolItem | null>(null)
  const [history, setHistory] = useState<ToolItemHistoryEntry[]>([])
  const [qrUrl, setQrUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([toolItemsApi.get(id), toolItemsApi.history(id)])
      .then(([i, h]) => {
        setItem(i); setHistory(h)
        return toolItemsApi.qrCodeBlob(id)
      })
      .then(url => setQrUrl(url))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  // Statistiken berechnen
  const stats = useMemo(() => {
    const returned = history.filter(e => e.returned_at)
    const avgDays = returned.length > 0
      ? Math.round(returned.reduce((sum, e) => sum + (new Date(e.returned_at!).getTime() - new Date(e.issued_at).getTime()) / 86400000, 0) / returned.length)
      : null
    const activeNow = history.some(e => !e.returned_at)
    return { total: history.length, avgDays, activeNow }
  }, [history])

  // Ausleihen letzte 6 Monate
  const monthChart = useMemo(() => {
    return Array.from({ length: 6 }, (_, i) => {
      const d = new Date()
      d.setMonth(d.getMonth() - (5 - i))
      const yr = d.getFullYear(), mo = d.getMonth()
      return {
        label: d.toLocaleDateString('de-DE', { month: 'short' }),
        count: history.filter(e => {
          const dt = new Date(e.issued_at)
          return dt.getFullYear() === yr && dt.getMonth() === mo
        }).length,
      }
    })
  }, [history])

  if (loading) return (
    <div className="p-8 space-y-4">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-3 gap-4">
        <Skeleton className="h-[520px]" />
        <div className="col-span-2 space-y-3">
          <Skeleton className="h-10 w-2/3" /><Skeleton className="h-6 w-1/3" /><Skeleton className="h-96" />
        </div>
      </div>
      <Skeleton className="h-64" />
    </div>
  )

  if (!item) return <div className="p-8 text-center text-slate-400">Exemplar nicht gefunden</div>

  return (
    <div className="p-8 space-y-4">
      <Button variant="ghost" className="text-slate-500 -ml-2" onClick={() => navigate('/inventory')}>
        <ArrowLeft size={16} className="mr-2" />Zurück zum Inventar
      </Button>

      <div className="grid grid-cols-3 gap-4 items-stretch">

        {/* Linke Spalte: Bild + QR in einer Karte */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex flex-col gap-4">
          <div className="rounded-lg overflow-hidden aspect-square flex items-center justify-center bg-slate-50">
            {item.tool.image_filename ? (
              <img src={`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/static/tool_images/${item.tool.image_filename}`} alt={item.tool.tool_name} className="w-full h-full object-cover" />
            ) : (
              <div className="flex flex-col items-center gap-2 text-slate-300">
                <Package size={52} />
                <span className="text-xs">Kein Bild vorhanden</span>
              </div>
            )}
          </div>

          <div className="flex-1 flex flex-col">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide flex items-center gap-1.5 mb-3">
              <QrCode size={12} />QR-Code
            </p>
            {qrUrl ? (
              <img src={qrUrl} alt="QR-Code" className="w-full rounded" />
            ) : (
              <div className="flex-1 bg-slate-50 rounded flex items-center justify-center text-slate-300">
                <QrCode size={32} />
              </div>
            )}
            <p className="font-mono text-xs text-slate-400 text-center mt-2">{item.inventory_no}</p>
          </div>
        </div>

        {/* Rechte Spalte: Infos + Stats + Diagramm */}
        <div className="col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6 flex flex-col">

          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-slate-800">{item.tool.tool_name}</h1>
            <p className="font-mono text-slate-400 mt-0.5">{item.inventory_no}</p>
            <div className="flex gap-2 mt-3">
              <span className={cn('text-xs font-semibold px-3 py-1 rounded-full flex items-center gap-1.5', statusColor[item.status.name] ?? 'bg-slate-100 text-slate-600')}>
                {statusIcon[item.status.name]}{t(toolStatusLabel, item.status.name)}
              </span>
              <span className={cn('text-xs font-semibold px-3 py-1 rounded-full', conditionColor[item.condition.name] ?? 'bg-slate-100 text-slate-600')}>
                {t(toolConditionLabel, item.condition.name)}
              </span>
            </div>
          </div>

          {/* Detailfelder */}
          <div className="border-t border-slate-100 pt-5 text-sm space-y-0">
            {[
              { label: 'Kategorie', value: item.tool.category.name },
              { label: 'Inventar-Nr.', value: <span className="font-mono">{item.inventory_no}</span> },
              ...(item.description ? [{ label: 'Beschreibung', value: item.description }] : []),
              ...(item.tool.description ? [{ label: 'Werkzeugbeschreibung', value: item.tool.description }] : []),
            ].map(({ label, value }) => (
              <div key={label} className="flex items-start py-3.5 border-b border-slate-100 last:border-0">
                <span className="w-52 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide pt-0.5 pl-1">{label}</span>
                <span className="text-slate-800 pl-6">{value}</span>
              </div>
            ))}
          </div>

          {/* Statistiken */}
          <div className="grid grid-cols-3 gap-3 border-t border-slate-100 pt-5">
            <StatCard
              icon={<RotateCcw size={18} />}
              label="Ausleihen gesamt"
              value={String(stats.total)}
              sub={stats.total === 0 ? 'Noch nie ausgeliehen' : `${history.filter(e => e.returned_at).length} zurückgegeben`}
            />
            <StatCard
              icon={<CalendarDays size={18} />}
              label="Ø Ausleihdauer"
              value={stats.avgDays !== null ? `${stats.avgDays}d` : '–'}
              sub="Tage pro Ausleihe"
            />
            <StatCard
              icon={<TrendingUp size={18} />}
              label="Aktueller Status"
              value={stats.activeNow ? 'Aktiv' : 'Frei'}
              sub={stats.activeNow ? 'Gerade ausgeliehen' : 'Verfügbar'}
            />
          </div>

          {/* Diagramm: Ausleihen letzte 6 Monate */}
          <div className="border-t border-slate-100 pt-5 flex-1 flex flex-col">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-4">Ausleihen – letzte 6 Monate</p>
            <ResponsiveContainer width="100%" height="100%" minHeight={120} className="flex-1">
              <BarChart data={monthChart} barSize={28} margin={{ top: 0, right: 0, left: -28, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#f8fafc' }}
                  contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
                  formatter={(v: number) => [`${v} Ausleihe${v !== 1 ? 'n' : ''}`, '']}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Ausleihverlauf */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="font-semibold text-slate-700 flex items-center gap-2 mb-4">
          <Clock size={16} />Ausleihverlauf
          <span className="text-xs font-normal text-slate-400 ml-1">({history.length} Einträge)</span>
        </h2>
        {history.length === 0 ? (
          <p className="text-sm text-slate-400 italic">Noch nie ausgeliehen</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100">
                {['Ausleiher', 'Ausgegeben am', 'Fällig am', 'Zurück am', 'Zustand', 'Kommentar'].map(h => (
                  <th key={h} className="pb-2 text-left text-xs font-semibold text-slate-400 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {history.map((entry, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="py-3 font-medium text-slate-800">{entry.borrower.firstname} {entry.borrower.lastname}</td>
                  <td className="py-3 text-slate-500">{new Date(entry.issued_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                  <td className="py-3 text-slate-500">{new Date(entry.due_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</td>
                  <td className="py-3">
                    {entry.returned_at
                      ? <span className="text-slate-500">{new Date(entry.returned_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' })}</span>
                      : <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">Aktiv</span>}
                  </td>
                  <td className="py-3 text-slate-500">{entry.return_condition ? t(toolConditionLabel, entry.return_condition.name) : '–'}</td>
                  <td className="py-3 text-slate-400 italic text-xs">{entry.return_comment ?? '–'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
