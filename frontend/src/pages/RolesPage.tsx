import { useEffect, useState } from 'react'
import { rolesApi } from '../api/services'
import type { Role } from '../types'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Skeleton } from '../components/ui/skeleton'
import { toast } from 'sonner'
import { Plus, Pencil, Trash2, Shield } from 'lucide-react'
import { roleLabel, t } from '../lib/labels'

export default function RolesPage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [open, setOpen] = useState(false)
  const [editRole, setEditRole] = useState<Role | null>(null)
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)

  const load = () => {
    setLoading(true)
    rolesApi.list().then(setRoles).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const openCreate = () => { setEditRole(null); setName(''); setOpen(true) }
  const openEdit = (r: Role) => { setEditRole(r); setName(r.name); setOpen(true) }

  const handleSave = async () => {
    if (!name.trim()) { toast.error('Name eingeben'); return }
    setSaving(true)
    try {
      if (editRole) {
        await rolesApi.update(editRole.id, { name }); toast.success('Rolle aktualisiert')
      } else {
        await rolesApi.create({ name }); toast.success('Rolle erstellt')
      }
      setOpen(false); load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Fehler')
    } finally { setSaving(false) }
  }

  const handleDelete = async (r: Role) => {
    if (!confirm(`Rolle "${r.name}" löschen?`)) return
    try { await rolesApi.delete(r.id); toast.success('Rolle gelöscht'); load() }
    catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      toast.error(err.response?.data?.detail ?? 'Löschen fehlgeschlagen')
    }
  }

  const roleColor: Record<string, string> = {
    ADMIN: 'bg-red-50 border-red-200',
    DEPARTMENT_MANAGER: 'bg-amber-50 border-amber-200',
    EMPLOYEE: 'bg-emerald-50 border-emerald-200',
  }
  const iconColor: Record<string, string> = {
    ADMIN: 'text-red-500',
    DEPARTMENT_MANAGER: 'text-amber-500',
    EMPLOYEE: 'text-emerald-500',
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2"><Shield size={24} />Rollen</h1>
          <p className="text-slate-500 mt-1">{roles.length} Rollen</p>
        </div>
        <Button onClick={openCreate} className="bg-blue-600 hover:bg-blue-700">
          <Plus size={16} className="mr-2" />Neue Rolle
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-28" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.map(r => (
            <div key={r.id} className={`bg-white rounded-xl border shadow-sm p-5 hover:shadow-md transition-shadow ${roleColor[r.name] ?? 'border-slate-200'}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
                    <Shield size={18} className={iconColor[r.name] ?? 'text-slate-500'} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{t(roleLabel, r.name)}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">ID: {r.id}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" onClick={() => openEdit(r)}><Pencil size={14} /></Button>
                  <Button size="sm" variant="ghost" className="text-red-500 hover:bg-red-50" onClick={() => handleDelete(r)}><Trash2 size={14} /></Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editRole ? 'Rolle bearbeiten' : 'Neue Rolle'}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label>Name</Label>
              <Input value={name} onChange={e => setName(e.target.value)} placeholder="z.B. ADMIN" />
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
