import { useEffect, useState } from 'react'
import { usersApi, rolesApi, departmentsApi } from '../api/services'
import type { User, Role, Department } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Search, Users, Mail, Building2, ShieldCheck, CalendarDays, ToggleLeft, ToggleRight } from 'lucide-react'
import { cn } from '../lib/utils'
import { roleLabel, t } from '../lib/labels'

const roleBadge = (role: string) => {
  const map: Record<string, string> = {
    ADMIN: 'bg-red-100 text-red-700 border-red-200',
    DEPARTMENT_MANAGER: 'bg-amber-100 text-amber-700 border-amber-200',
    EMPLOYEE: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  }
  return map[role] ?? 'bg-slate-100 text-slate-700'
}

const emptyForm = { firstname: '', lastname: '', email: '', password: '', role_id: '', department_id: '', is_active: true }

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [open, setOpen] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [detailUser, setDetailUser] = useState<User | null>(null)

  const load = () => {
    setLoading(true)
    Promise.all([usersApi.list(), rolesApi.list(), departmentsApi.list()])
      .then(([u, r, d]) => { setUsers(u); setRoles(r); setDepartments(d) })
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const openCreate = () => { setEditUser(null); setForm(emptyForm); setOpen(true) }
  const openEdit = (u: User) => {
    setEditUser(u)
    setForm({ firstname: u.firstname, lastname: u.lastname, email: u.email, password: '', role_id: String(u.role_id), department_id: String(u.department_id), is_active: u.is_active })
    setOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload: Record<string, unknown> = {
        firstname: form.firstname, lastname: form.lastname, email: form.email,
        role_id: Number(form.role_id), department_id: Number(form.department_id),
        is_active: form.is_active,
      }
      if (form.password) payload.password = form.password
      if (editUser) {
        await usersApi.update(editUser.id, payload)
        toast.success('Nutzer aktualisiert')
      } else {
        await usersApi.create({ ...payload, password: form.password })
        toast.success('Nutzer erstellt')
      }
      setOpen(false); load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: unknown } } }
      const detail = err.response?.data?.detail
      let msg = 'Fehler beim Speichern'
      if (typeof detail === 'string') msg = detail
      else if (Array.isArray(detail) && detail.length > 0)
        msg = ((detail[0] as { msg?: string }).msg ?? 'Fehler').replace(/^Value error,\s*/, '')
      toast.error(msg)
    } finally { setSaving(false) }
  }

  const handleDelete = async (u: User) => {
    if (!confirm(`Nutzer "${u.firstname} ${u.lastname}" löschen?`)) return
    try {
      await usersApi.delete(u.id); toast.success('Nutzer gelöscht'); load()
    } catch { toast.error('Löschen fehlgeschlagen') }
  }

  const filtered = users.filter(u =>
    `${u.firstname} ${u.lastname} ${u.email}`.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Users size={24} />Nutzer</h1>
          <p className="text-slate-500 mt-1">{users.length} Nutzer insgesamt</p>
        </div>
        <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus size={16} className="mr-2" />Neuer Nutzer
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <Input placeholder="Suchen…" value={search} onChange={e => setSearch(e.target.value)} className="pl-9" />
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {loading ? (
          <div className="p-6 space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                {['Name', 'E-Mail', 'Rolle', 'Abteilung', 'Status', ''].map(h => (
                  <th key={h} className="px-5 py-3.5 text-left font-semibold text-slate-600">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(u => (
                <tr key={u.id} className="hover:bg-slate-50 transition-colors cursor-pointer" onClick={() => setDetailUser(u)}>
                  <td className="px-5 py-3.5 font-medium text-slate-800">{u.firstname} {u.lastname}</td>
                  <td className="px-5 py-3.5 text-slate-500">{u.email}</td>
                  <td className="px-5 py-3.5">
                    <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full border', roleBadge(u.role.name))}>
                      {t(roleLabel, u.role.name)}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">{u.department.name}</td>
                  <td className="px-5 py-3.5">
                    <Badge variant={u.is_active ? 'default' : 'secondary'} className={u.is_active ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : ''}>
                      {u.is_active ? 'Aktiv' : 'Inaktiv'}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5" onClick={e => e.stopPropagation()}>
                    <div className="flex gap-2 justify-end">
                      <Button size="sm" variant="ghost" onClick={() => openEdit(u)}><Pencil size={14} /></Button>
                      <Button size="sm" variant="ghost" className="text-red-500 hover:text-red-700 hover:bg-red-50" onClick={() => handleDelete(u)}><Trash2 size={14} /></Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* User detail dialog */}
      <Dialog open={!!detailUser} onOpenChange={v => !v && setDetailUser(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <div className={cn('w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold', roleBadge(detailUser?.role.name ?? ''))}>
                {detailUser?.firstname[0]}{detailUser?.lastname[0]}
              </div>
              {detailUser?.firstname} {detailUser?.lastname}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-0 text-sm">
            {[
              { icon: <Mail size={14} />, label: 'E-Mail', value: detailUser?.email },
              { icon: <ShieldCheck size={14} />, label: 'Rolle', value: (
                <span className={cn('text-xs font-medium px-2.5 py-1 rounded-full border', roleBadge(detailUser?.role.name ?? ''))}>
                  {t(roleLabel, detailUser?.role.name ?? '')}
                </span>
              )},
              { icon: <Building2 size={14} />, label: 'Abteilung', value: detailUser?.department.name },
              { icon: <CalendarDays size={14} />, label: 'Erstellt am', value: detailUser?.created_at ? new Date(detailUser.created_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '–' },
              { icon: <CalendarDays size={14} />, label: 'Zuletzt geändert', value: detailUser?.updated_at ? new Date(detailUser.updated_at).toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '–' },
            ].map(({ icon, label, value }) => (
              <div key={label} className="flex items-center py-3 border-b border-slate-100 last:border-0 gap-3">
                <span className="text-slate-400">{icon}</span>
                <span className="w-36 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">{label}</span>
                <span className="text-slate-800">{value}</span>
              </div>
            ))}

            <div className="flex items-center py-3 gap-3">
              <span className="text-slate-400"><Users size={14} /></span>
              <span className="w-36 shrink-0 text-xs font-semibold text-slate-400 uppercase tracking-wide">Status</span>
              <Badge className={detailUser?.is_active ? 'bg-emerald-100 text-emerald-700 border-emerald-200' : ''} variant={detailUser?.is_active ? 'default' : 'secondary'}>
                {detailUser?.is_active ? 'Aktiv' : 'Inaktiv'}
              </Badge>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailUser(null)}>Schließen</Button>
            <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => { setDetailUser(null); openEdit(detailUser!) }}>
              <Pencil size={14} className="mr-2" />Bearbeiten
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>{editUser ? 'Nutzer bearbeiten' : 'Neuer Nutzer'}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="space-y-1.5">
              <Label>Vorname</Label>
              <Input value={form.firstname} onChange={e => setForm(f => ({ ...f, firstname: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Nachname</Label>
              <Input value={form.lastname} onChange={e => setForm(f => ({ ...f, lastname: e.target.value }))} />
            </div>
            <div className="space-y-1.5 col-span-2">
              <Label>E-Mail</Label>
              <Input type="text" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} />
            </div>
            <div className="space-y-1.5 col-span-2">
              <Label>{editUser ? 'Neues Passwort (optional)' : 'Passwort'}</Label>
              <Input type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} />
            </div>
            <div className="space-y-1.5">
              <Label>Rolle</Label>
              <Select value={form.role_id} onValueChange={v => setForm(f => ({ ...f, role_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                <SelectContent>{roles.map(r => <SelectItem key={r.id} value={String(r.id)}>{t(roleLabel, r.name)}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Abteilung</Label>
              <Select value={form.department_id} onValueChange={v => setForm(f => ({ ...f, department_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Wählen…" /></SelectTrigger>
                <SelectContent>{departments.map(d => <SelectItem key={d.id} value={String(d.id)}>{d.name}</SelectItem>)}</SelectContent>
              </Select>
            </div>
            <div className="col-span-2 flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-700">Konto aktiv</p>
                <p className="text-xs text-slate-400">Inaktive Nutzer können sich nicht einloggen</p>
              </div>
              <button
                type="button"
                onClick={() => setForm(f => ({ ...f, is_active: !f.is_active }))}
                className="text-slate-400 hover:text-blue-600 transition-colors"
              >
                {form.is_active
                  ? <ToggleRight size={36} className="text-blue-600" />
                  : <ToggleLeft size={36} />}
              </button>
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
