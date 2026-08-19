import { useCallback, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import api from '@/lib/api'
import {
  Upload, FileText, Image, Trash2, RefreshCw,
  CheckCircle, Clock, Loader, XCircle, ChevronDown, ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  uploaded:       { label: 'Uploaded',       color: 'badge-sand',    icon: Clock },
  processing:     { label: 'Processing',     color: 'badge-amber',   icon: Loader },
  text_extracted: { label: 'Text Extracted', color: 'badge-editorial',icon: FileText },
  ai_analyzing:   { label: 'AI Analyzing',   color: 'badge-amber',   icon: Loader },
  completed:      { label: 'Verified',       color: 'badge-emerald', icon: CheckCircle },
  failed:         { label: 'Failed',         color: 'badge-red',     icon: XCircle },
}

function CertCard({ cert, onDelete, onReprocess }: any) {
  const [expanded, setExpanded] = useState(false)
  const cfg = STATUS_CONFIG[cert.status] || STATUS_CONFIG.uploaded
  const StatusIcon = cfg.icon
  const allSkills = Object.values(cert.extracted_skills || {}).flat() as string[]

  return (
    <div className="card p-5">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="w-10 h-10 bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded-md flex items-center justify-center flex-shrink-0">
          {cert.file_name?.endsWith('.pdf')
            ? <FileText className="w-5 h-5 text-[#FF5722] dark:text-[#FF7043]" />
            : <Image className="w-5 h-5 text-[#FF5722] dark:text-[#FF7043]" />
          }
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start gap-2 justify-between flex-wrap">
            <div className="min-w-0">
              <p className="font-heading text-lg font-bold text-app truncate">
                {cert.certificate_title || cert.file_name}
              </p>
              {cert.issuing_organization && (
                <p className="text-xs font-bold text-[#FF5722] dark:text-[#FF7043]">{cert.issuing_organization}</p>
              )}
              <p className="text-[10px] text-secondary font-medium mt-0.5">
                Uploaded: {cert.upload_date ? new Date(cert.upload_date).toLocaleDateString() : ''}
              </p>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <span className={`badge ${cfg.color} flex items-center gap-1`}>
                <StatusIcon className={`w-3 h-3 ${cert.status === 'processing' || cert.status === 'ai_analyzing' ? 'animate-spin' : ''}`} />
                {cfg.label}
              </span>
            </div>
          </div>

          {/* Skills preview */}
          {allSkills.length > 0 && (
            <div className="mt-3">
              <div className="flex flex-wrap gap-1.5">
                {allSkills.slice(0, expanded ? 100 : 6).map((s: string) => (
                  <span key={s} className="px-2.5 py-0.5 text-[11px] font-bold bg-[#FF5722]/10 text-[#FF5722] border border-[#FF5722]/30 dark:bg-[#FF5722]/15 dark:text-[#FF7043] dark:border-[#FF5722]/40 rounded">
                    {s}
                  </span>
                ))}
                {!expanded && allSkills.length > 6 && (
                  <button
                    onClick={() => setExpanded(true)}
                    className="px-2 py-0.5 text-[11px] font-medium bg-subtle text-secondary flex items-center gap-1 border border-app rounded"
                  >
                    +{allSkills.length - 6} more <ChevronDown className="w-3 h-3" />
                  </button>
                )}
                {expanded && (
                  <button
                    onClick={() => setExpanded(false)}
                    className="px-2 py-0.5 text-[11px] font-medium bg-subtle text-secondary flex items-center gap-1 border border-app rounded"
                  >
                    Show less <ChevronUp className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          )}

          {cert.processing_error && (
            <p className="text-xs text-red-600 font-medium mt-2">Processing Exception: {cert.processing_error}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-1 flex-shrink-0">
          {cert.status === 'failed' && (
            <button
              onClick={() => onReprocess(cert.id)}
              className="p-1.5 text-[#FF5722] dark:text-[#FF7043] hover:bg-subtle rounded"
              title="Retry verification"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={() => onDelete(cert.id)}
            className="p-1.5 text-secondary hover:text-red-600 hover:bg-subtle rounded transition-colors"
            title="Delete certificate"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default function CertificatesPage() {
  const queryClient = useQueryClient()
  const [uploading, setUploading] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['certificates'],
    queryFn: () => api.get('/api/certificates').then((r) => r.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return api.post('/api/certificates/upload', formData)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['certificates'] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      // Invalidate score — certificates_score component contributes to readiness
      queryClient.invalidateQueries({ queryKey: ['jobScore'], exact: false })
      toast.success('Certificate uploaded! Skills extracted and Career Readiness Score recalculated.')
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || err.message || 'Upload failed'),
    onSettled: () => setUploading(false),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/api/certificates/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['certificates'] })
      // Removing a cert affects certificates_score — recalculate
      queryClient.invalidateQueries({ queryKey: ['jobScore'], exact: false })
      toast.success('Certificate deleted. Career Readiness Score recalculated.')
    },
  })

  const reprocessMutation = useMutation({
    mutationFn: (id: string) => api.post(`/api/certificates/${id}/reprocess`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['certificates'] })
      toast.success('Reprocessing triggered')
    },
  })

  const onDrop = useCallback(
    (files: File[]) => {
      if (files.length === 0) return
      setUploading(true)
      files.forEach((f) => uploadMutation.mutate(f))
    },
    [uploadMutation]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    maxSize: 10 * 1024 * 1024,
    disabled: uploading,
  })

  const certs = data?.certificates || []

  return (
    <div className="space-y-6 max-w-3xl animate-fade-in text-app">
      <div className="card p-6 shadow-xs">
        <span className="text-[10px] font-bold text-[#FF5722] dark:text-[#FF7043] uppercase tracking-wider block mb-1">OCR Skill Verification Log</span>
        <h2 className="font-heading text-3xl font-extrabold text-app">Verified Credentials & Certificates</h2>
        <p className="text-secondary text-xs mt-0.5">Upload academic & industry certificates for automated OCR skill extraction</p>
      </div>

      {/* Upload zone */}
      <div
        {...getRootProps()}
        id="cert-upload-zone"
        className={`border-2 border-dashed p-8 rounded-xl text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-[#FF5722] bg-[#FF5722]/10 dark:bg-[#FF5722]/15'
            : 'border-app hover:border-[#FF5722]/60 bg-surface'
        }`}
      >
        <input {...getInputProps()} id="cert-file-input" />
        <div className="flex flex-col items-center gap-3">
          {uploading ? (
            <Loader className="w-8 h-8 text-[#FF5722] dark:text-[#FF7043] animate-spin" />
          ) : (
            <Upload className={`w-8 h-8 ${isDragActive ? 'text-[#FF5722]' : 'text-secondary'}`} />
          )}
          <div>
            <p className="text-sm font-bold text-app">
              {uploading ? 'Uploading Certificate Document...' : isDragActive ? 'Drop certificate files to verify' : 'Drag & drop official credential documents'}
            </p>
            <p className="text-xs text-secondary mt-1">PDF, PNG, JPG, JPEG • Max 10MB per document</p>
          </div>
          {!uploading && !isDragActive && (
            <button className="btn btn-primary text-xs">Select Certificate Files</button>
          )}
        </div>
      </div>

      {/* Certificate list */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(2)].map((_, i) => <div key={i} className="card h-24 skeleton" />)}
        </div>
      ) : certs.length === 0 ? (
        <div className="card p-10 text-center">
          <FileText className="w-10 h-10 text-secondary mx-auto mb-3" />
          <h3 className="font-heading text-xl font-bold text-app">No Credentials Uploaded</h3>
          <p className="text-xs text-secondary mt-1">Upload accredited certificates to automatically extract verified skills into your dossier</p>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-xs font-bold uppercase tracking-wider text-secondary">{certs.length} Verified Credential Entry{certs.length !== 1 ? 's' : ''}</p>
          {certs.map((cert: any) => (
            <CertCard
              key={cert.id}
              cert={cert}
              onDelete={(id: string) => deleteMutation.mutate(id)}
              onReprocess={(id: string) => reprocessMutation.mutate(id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}
