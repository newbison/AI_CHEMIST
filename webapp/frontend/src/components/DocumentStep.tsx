import { useState, useRef, useCallback } from 'react'
import type { UploadDocResponse } from '../types'

const API_BASE = 'http://localhost:8001'

interface Props {
  onContinue: (docAnalysis: string) => void
  onSkip: () => void
  onBack: () => void
  onHome: () => void
}

export default function DocumentStep({ onContinue, onSkip, onBack, onHome }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [analysis, setAnalysis] = useState<UploadDocResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback((f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase()
    if (!ext || !['pdf', 'docx'].includes(ext)) {
      setError('仅支持 PDF 和 Word (.docx) 文件')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('文件超过 10MB 限制')
      return
    }
    setFile(f)
    setError(null)
    setAnalysis(null)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }, [handleFile])

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError(null)
    setAnalysis(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_name', file.name)

    try {
      const res = await fetch(`${API_BASE}/api/upload-doc`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || data.error || '上传失败')
      }
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="step-container">
      <div className="step-hero">
        <h1 className="hero-title">上传参考文档（可选）</h1>
        <p className="hero-sub">
          上传 PDF 或 Word 文档作为背景参考资料，系统将自动分析并融入报告。
        </p>
      </div>

      <div className="doc-upload-area">
        {/* 文件选择区 */}
        <div
          className={`doc-drop-zone ${isDragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragOver(true) }}
          onDragLeave={() => setIsDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={{ display: 'none' }}
            onChange={(e) => {
              const f = e.target.files?.[0]
              if (f) handleFile(f)
            }}
          />

          {file ? (
            <div className="doc-file-info">
              <span className="doc-file-icon">📄</span>
              <div className="doc-file-details">
                <span className="doc-file-name">{file.name}</span>
                <span className="doc-file-size">{formatSize(file.size)}</span>
              </div>
              <button
                className="doc-remove-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  setFile(null)
                  setAnalysis(null)
                  setError(null)
                }}
              >
                ✕
              </button>
            </div>
          ) : (
            <div className="doc-drop-hint">
              <span className="doc-drop-icon">📎</span>
              <span className="doc-drop-text">
                拖拽文件到此处，或<span className="doc-drop-link">点击选择</span>
              </span>
              <span className="doc-drop-formats">支持 PDF、Word (.docx)，最大 10MB</span>
            </div>
          )}
        </div>

        {/* 上传按钮 */}
        {file && !analysis && (
          <button
            className="primary-btn doc-upload-btn"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? '⏳ 正在分析...' : '🚀 上传并分析'}
          </button>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="doc-error">
            <span>⚠️ {error}</span>
          </div>
        )}

        {/* 分析结果预览 */}
        {analysis && (
          <div className="doc-analysis-result">
            <div className="doc-analysis-header">
              <span className="doc-analysis-title">✅ 分析完成</span>
              <span className="doc-analysis-name">📄 {analysis.doc_name}</span>
            </div>
            <div className="doc-analysis-content">
              <div className="doc-text-preview">
                <details className="doc-preview-details">
                  <summary>原文预览（前500字）</summary>
                  <pre className="doc-preview-text">{analysis.text_preview}</pre>
                </details>
              </div>
              <div className="doc-analysis-text">
                <div dangerouslySetInnerHTML={{ __html: analysis.analysis.replace(/\n/g, '<br/>') }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 底部操作按钮 */}
      <div className="step-nav">
        <div className="step-nav-left">
          <button className="ghost-btn" onClick={onBack}>← 返回专利列表</button>
          <button className="ghost-btn home-btn" onClick={onHome}>🏠 返回主页</button>
        </div>
        <div className="step-nav-right">
          <button className="ghost-btn" onClick={onSkip}>
            跳过此步 →
          </button>
          {analysis && (
            <button
              className="primary-btn"
              onClick={() => onContinue(analysis.analysis)}
            >
              确认并继续 →
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
