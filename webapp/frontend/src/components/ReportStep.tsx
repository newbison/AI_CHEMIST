import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { T } from '../i18n'
import type { Lang } from '../i18n'
import type { Patent } from '../types'

export default function ReportStep({
  lang,
  voc,
  patents,
  docAnalysis,
  deepSearchData,
  onBack,
  onHome,
}: {
  lang: Lang
  voc: string
  patents: Patent[]
  docAnalysis?: string | null
  deepSearchData?: Record<string, unknown> | null
  onBack: () => void
  onHome: () => void
}) {
  const [report, setReport] = useState('')
  const [reportTitle, setReportTitle] = useState<string | null>(null)  // 动态标题
  const [status, setStatus] = useState<'idle' | 'generating' | 'done' | 'error'>('idle')
  const [error, setError] = useState('')
  const [meta, setMeta] = useState<{ patent_count: number } | null>(null)
  const [progressStage, setProgressStage] = useState<string>('')
  const [pptxLoading, setPptxLoading] = useState(false)
  const reportRef = useRef<HTMLDivElement>(null)
  // AbortController 用于 StrictMode cleanup 时取消 in-flight 请求；
  // catch 块里 AbortError 静默返回，第二次挂载会重新发起请求。
  const abortRef = useRef<AbortController | null>(null)

  async function generate() {
    const controller = new AbortController()
    abortRef.current = controller
    setStatus('generating')
    setError('')
    setReport('')

    // 用局部标志代替陈旧的 status 闭包，避免出错时仍被标成 done
    let errored = false

    try {
      const resp = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voc, patents, fetch_details: true, doc_analysis: docAnalysis, language: lang, deep_search_data: deepSearchData }),
        signal: controller.signal,
      })
      if (!resp.ok) throw new Error(`生成失败: ${resp.status}`)
      if (!resp.body) throw new Error('无响应流')

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          // 流结束：冲刷 TextDecoder 内部缓冲，处理最后残留数据
          buffer += decoder.decode()
          if (buffer.trim()) {
            for (const line of buffer.split('\n')) {
              if (!line.startsWith('data: ')) continue
              try {
                const evt = JSON.parse(line.slice(6).trim())
                if (evt.type === 'chunk') {
                  setReport((prev) => prev + evt.content)
                } else if (evt.type === 'done' || evt.type === 'meta') {
                  // meta/done 正常处理
                  if (evt.type === 'done') setStatus('done')
                } else if (evt.type === 'error') {
                  errored = true
                  setError(evt.message)
                  setStatus('error')
                }
              } catch { /* 末尾残留不完整行，跳过 */ }
            }
          }
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const jsonStr = line.slice(6).trim()
          if (!jsonStr) continue
          try {
            const evt = JSON.parse(jsonStr)
            if (evt.type === 'meta') {
              setMeta({ patent_count: evt.patent_count })
            } else if (evt.type === 'progress') {
              // 显示当前处理阶段，让用户知道后端在做什么
              const stageText: Record<string, string> = {
                detail_skipped: '专利详情源不可达，使用已有摘要',
                detail: `抓取专利详情 (${evt.index}/${evt.total})`,
                llm_calling: `调用 DeepSeek 生成报告 (prompt ~${Math.round((evt.prompt_size || 0) / 1024)}KB)`,
              }
              setProgressStage(stageText[evt.stage] || evt.stage || '')
            } else if (evt.type === 'chunk') {
              setReport((prev) => {
                const next = prev + evt.content
                // 从 Markdown 内容中提取第一行作为标题（# 开头）
                if (!reportTitle && next.startsWith('# ')) {
                  const firstLine = next.split('\n')[0].replace(/^#\s*/, '').trim()
                  if (firstLine && !firstLine.includes('根据 VOC') && firstLine.length > 3) {
                    setReportTitle(firstLine)
                  }
                }
                return next
              })
              setProgressStage('') // 开始收到内容，清除进度提示
            } else if (evt.type === 'done') {
              setStatus('done')
            } else if (evt.type === 'error') {
              errored = true
              setError(evt.message)
              setStatus('error')
            }
          } catch (parseErr) {
            console.warn('[SSE] JSON 解析失败:', parseErr, 'line:', line.slice(0, 80))
          }
        }
      }
      if (!errored && !controller.signal.aborted) setStatus('done')
    } catch (e) {
      // 组件卸载/StrictMode 重挂载触发的 abort 不算错误，静默返回
      if (controller.signal.aborted) return
      if (e instanceof DOMException && e.name === 'AbortError') return
      setError(e instanceof Error ? e.message : '生成出错')
      setStatus('error')
    }
  }

  // 自动开始生成。
  // StrictMode 在 dev 模式下会双挂载：cleanup abort 第一个请求，
  // catch 块检测到 AbortError 后静默返回，第二个 mount 重新发起请求。
  useEffect(() => {
    generate()
    return () => {
      if (abortRef.current) {
        abortRef.current.abort()
        abortRef.current = null
      }
    }
  }, [])

  // 自动滚动
  useEffect(() => {
    if (reportRef.current) {
      reportRef.current.scrollTop = reportRef.current.scrollHeight
    }
  }, [report])

  /** 从报告标题/VOC 生成安全的项目文件名 */
  function getProjectFilename(ext: string): string {
    const date = new Date().toISOString().slice(0, 10)
    // 1. 用动态提取的报告标题
    if (reportTitle) {
      const safe = reportTitle
        .replace(/^#+\s*/, '')           // 去掉 markdown 标题标记
        .replace(/[\\/:*?"<>|]/g, '')    // 去掉 Windows 非法文件名字符
        .replace(/\s+/g, '_')            // 空格 → 下划线
        .replace(/_+/g, '_')             // 多下划线合并
        .replace(/^_|_$/g, '')           // 去首尾下划线
        .slice(0, 60)                    // 限长
      if (safe) return `${safe}_${date}.${ext}`
    }
    // 2. 回退：从 report markdown 第一行提取（去掉 # 和 null 字节）
    const firstLine = (report || '').replace(/^#+\s*/, '').split('\n')[0].trim()
    if (firstLine && firstLine.length > 3) {
      const safe = firstLine
        .replace(/[\\/:*?"<>|]/g, '')
        .replace(/\s+/g, '_')
        .replace(/_+/g, '_')
        .slice(0, 60)
      if (safe) return `${safe}_${date}.${ext}`
    }
    // 3. 回退：从 VOC 截取
    const vocShort = (voc || '').replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, '_').slice(0, 40)
    if (vocShort) return `${vocShort}_${date}.${ext}`
    // 4. 最终回退
    return `rd-report_${date}.${ext}`
  }

  function downloadReport() {
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = getProjectFilename('md')
    a.click()
    URL.revokeObjectURL(url)
  }

  async function downloadDocx() {
    if (!report) return
    try {
      const resp = await fetch('/api/export-docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report, filename: getProjectFilename('docx') }),
      })
      if (!resp.ok) throw new Error(`导出失败: ${resp.status}`)
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = getProjectFilename('docx')
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : '导出出错')
    }
  }

  async function downloadPptx() {
    if (!report) return
    setPptxLoading(true)
    setError('')
    try {
      const resp = await fetch('/api/export-pptx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report, filename: getProjectFilename('pptx') }),
      })
      if (!resp.ok) throw new Error(`导出失败: ${resp.status}`)
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = getProjectFilename('pptx')
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : '导出出错')
    }
    setPptxLoading(false)
  }

  return (
    <div className="step-container report-step">
      <div className="report-header">
        <div>
          <h1 className="hero-title">{reportTitle || (lang === 'zh' ? 'R&D 智能报告生成中...' : 'Generating R&D Intelligence Report...')}</h1>
          <p className="hero-sub">
            {meta ? `基于 ${meta.patent_count} 篇专利生成` : `基于 ${patents.length} 篇专利生成`}
            {status === 'generating' && (progressStage ? ` · ${progressStage}` : ' · 生成中...')}
            {status === 'done' && ' · 生成完成'}
            {status === 'error' && ' · 生成失败'}
          </p>
        </div>
        <div className="report-actions">
          {status === 'done' && (
            <>
              <button className="ghost-btn" onClick={downloadPptx} disabled={pptxLoading}>
                {pptxLoading ? (
                  <><span className="spinner" /> AI 设计中...</>
                ) : (
                  '下载 PPT (AI设计)'
                )}
              </button>
              <button className="ghost-btn" onClick={downloadDocx}>
                下载 Word
              </button>
              <button className="ghost-btn" onClick={downloadReport}>
                下载 .md
              </button>
            </>
          )}
          <button className="ghost-btn" onClick={onBack}>← 返回选专利</button>
          <button className="ghost-btn home-btn" onClick={onHome}>🏠 返回主页</button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="report-body" ref={reportRef}>
        {report ? (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
          </div>
        ) : status === 'generating' ? (
          <div className="loading-state">
            <span className="spinner large" />
            <p>{progressStage || '正在调用 DeepSeek 生成报告，请稍候...'}</p>
            <p className="loading-hint">
              {progressStage === '' || progressStage.startsWith('调用')
                ? '大 prompt 处理可能需要 1-3 分钟，报告将逐段流式输出'
                : '处理中...'}
            </p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
