import { useEffect, useState } from 'react'
import { departmentsApi, usersApi } from '../api/services'
import type { Department, User } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Building2, Users } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function DepartmentsPage() {
  const { isAdmin } = useAuth()
  const [departments, setDepartments] = useState<Department[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editDept, setEditDept] = useState<Department | null>(null)

  // Detail dialog
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailDept, setDetailDept] = useState<Department | null>(null)
  const openDetail = (d: Department) => { setDetailDept(d); setDetailOpen(true) }
  const [name, setName] = useState('')
  const [leadId, setLeadId] = useState<string>('none')
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([departmentsApi.list(), usersApi.list()])
      .then(([d, u]) => { setDepartments(d); setUsers(u) })
      .finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditDept(null); setName(''); setLeadId('none'); setOpen(true) }
  const openEdit = (d: Department) => {
    setEditDept(d); setName(d.name)
    setLeadId(d.lead_user_id ? String(d.lead_user_id) : 'none')
    setOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    const payload = { name, lead_user_id: leadId === 'none' ? null : Number(leadId) }
    try {
      if (editDept) {
        await departmentsApi.update(editDept.id, payload); toast.success('Abteilung aktualisiert')
      } else {
        await departmentsApi.create(payload); toast.success('Abteilung erstellt')
      }
      setOpen(false); load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler')
    } finally { setSaving(false) }
  }

  const handleDelete = async (d: Department) => {
    if (!confirm(`Abteilung "${d.name}" löschen?`)) return
    try { await departmentsApi.delete(d.id); toast.success('Abteilung gelöscht'); load() }
    catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Löschen fehlgeschlagen')
    }
  }

  const getLeadName = (d: Department) => {
    if (!d.lead_user_id) return null
    const u = users.find(u => u.id === d.lead_user_id)
    return u ? `${u.firstname} ${u.lastname}` : null
  }

  const deptUsers = (d: Department) => users.filter(u => u.department_id === d.id)

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Building2 size={24} />Abteilungen</h1>
          <p className="text-slate-500 mt-1">{departments.length} Abteilungen</p>
        </div>
        {isAdmin && (
          <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
            <Plus size={16} className="mr-2" />Neue Abteilung
          </Button>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-36" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {departments.map(d => {
            const lead = getLeadName(d)
            const members = deptUsers(d)
            return (
              <div key={d.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:shadow-md transition-shadow cursor-pointer" onClick={() => openDetail(d)}>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-slate-800">{d.name}</h3>
                    {lead ? (
                      <p className="text-sm text-slate-500 mt-0.5">Leiter: <span className="text-slate-700 font-medium">{lead}</span></p>
                    ) : (
                      <p className="text-sm text-slate-400 mt-0.5 italic">Kein Leiter</p>
                    )}
                  </div>
                  {isAdmin && (
                    <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                      <Button size="sm" variant="ghost" onClick={() => openEdit(d)}><Pencil size={14} /></Button>
                      <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(d)}><Trash2 size={14} /></Button>
                    </div>
                  )}
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">{members.length} Mitglieder</span>
                  <Badge variant="secondary">{members.length}</Badge>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Building2 size={18} />{detailDept?.name}
            </DialogTitle>
          </DialogHeader>
          {detailDept && (() => {
            const lead = users.find(u => u.id === detailDept.lead_user_id) ?? null
            const members = users.filter(u => u.department_id === detailDept.id && u.role.name !== 'ADMIN')
            return (
              <div className="space-y-4 py-1">
                {/* Abteilungsleiter */}
                <div className={`rounded-lg p-4 ${lead ? 'bg-blue-50 border border-blue-100' : 'bg-slate-50'}`}>
                  <p className="text-xs font-semibold text-blue-600 uppercase tracking-wide mb-2">
                    Abteilungsleiter
                  </p>
                  {lead ? (
                    <div>
                      <p className="font-semibold text-slate-800">{lead.firstname} {lead.lastname}</p>
                      <p className="text-sm text-slate-500">{lead.email}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-400 italic">Kein Leiter zugewiesen</p>
                  )}
                </div>

                {/* Mitglieder */}
                <div>
                  <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide flex items-center gap-1.5 mb-2">
                    <Users size={12} />{members.length} Mitglieder
                  </p>
                  {members.length === 0 ? (
                    <p className="text-sm text-slate-400 italic">Keine Mitglieder</p>
                  ) : (
                    <div className="space-y-2">
                      {members.map(u => (
                        <div key={u.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-3 py-2.5">
                          <div>
                            <p className="text-sm font-medium text-slate-800">
                              {u.firstname} {u.lastname}
                              {u.id === detailDept.lead_user_id && (
                                <span className="ml-2 text-xs text-blue-600 font-semibold">Leiter</span>
                              )}
                            </p>
                            <p className="text-xs text-slate-500">{u.email}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )
          })()}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailOpen(false)}>Schließen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editDept ? 'Abteilung bearbeiten' : 'Neue Abteilung'}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Name</Label>
              <Input value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div className="space-y-1.5">
              <Label>Abteilungsleiter</Label>
              <Select value={leadId} onValueChange={setLeadId}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">– Kein Leiter –</SelectItem>
                  {users.map(u => (
                    <SelectItem key={u.id} value={String(u.id)}>
                      {u.firstname} {u.lastname} ({u.role?.name ?? ''})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={saving || !name} className="bg-blue-600 hover:bg-blue-700">
              {saving ? 'Speichern…' : 'Speichern'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
