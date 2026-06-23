import { useState, useEffect, useRef } from 'react'
import { T } from '../i18n'
import type {
  ScoutPhase,
  ScoutTechRoute,
  ScoutRouteDetail,
  ScoutRound1Response,
  ScoutRound2Response,
  ScoutOutputResponse,
} from '../types'

export default function ScoutStep({
  lang,
  voc,
  onOutput,
  onSkip,
  onRound1Data,
}: {
  lang: import('../i18n').Lang
  voc: string
  onOutput: (output: ScoutOutputResponse) => void
  onSkip: () => void
  onRound1Data?: (data: { market_share: any; domain_class: string; confidence: string }) => void
}) {
  const [phase, setPhase] = useState<ScoutPhase>('scout_round1')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Round 1 状态
  const [routes, setRoutes] = useState<ScoutTechRoute[]>([])
  const [domainClass, setDomainClass] = useState('')
  const [confidence, setConfidence] = useState('★★☆')
  const [analysis, setAnalysis] = useState('')
  const [contradictions, setContradictions] = useState<string[]>([])
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Round 2 状态
  const [routeDetails, setRouteDetails] = useState<ScoutRouteDetail[]>([])

  // 防止 StrictMode 双挂载触发两次 fetch（同 ReportStep 修过的 bug）
  const startedRef = useRef(false)

  // Round 1: 获取技术路线
  async function fetchRound1() {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch('/api/voc-scout/round1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voc }),
      })
      if (!resp.ok) throw new Error(`Round 1 failed: ${resp.status}`)
      const data: ScoutRound1Response & { market_share?: any } = await resp.json()
      setRoutes(data.routes)
      // 默认全选所有技术路线
      setSelectedIds(new Set(data.routes.map((r) => r.id)))
      setDomainClass(data.domain_class)
      setConfidence(data.confidence)
      setAnalysis(data.analysis)
      setContradictions(data.contradictions)
      if (onRound1Data) {
        onRound1Data({
          market_share: (data as any).market_share || null,
          domain_class: data.domain_class,
          confidence: data.confidence,
        })
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Round 1 error')
    }
    setLoading(false)
  }

  // 切换路线选择（多选）
  function toggleRoute(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  // Round 2: 钻取
  async function fetchRound2() {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch('/api/voc-scout/round2', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voc,
          selected_route_ids: [...selectedIds],
        }),
      })
      if (!resp.ok) throw new Error(`Round 2 failed: ${resp.status}`)
      const data: ScoutRound2Response = await resp.json()
      setRouteDetails(data.routes)
      setPhase('scout_round2')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Round 2 error')
    }
    setLoading(false)
  }

  // 最终输出：生成三件套
  async function fetchOutput() {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch('/api/voc-scout/output', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voc,
          selected_route_ids: [...selectedIds],
          round_history: [{ phase: 'round1', selected: [...selectedIds] }],
        }),
      })
      if (!resp.ok) throw new Error(`Output failed: ${resp.status}`)
      const data: ScoutOutputResponse = await resp.json()
      setPhase('scout_output')
      onOutput(data)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Output error')
    }
    setLoading(false)
  }

  // 挂载时自动获取 Round 1（用 ref 守卫防 StrictMode 双调用）
  useEffect(() => {
    if (startedRef.current) return
    startedRef.current = true
    fetchRound1()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="scout-container">
      <div className="scout-header-bar">
        <h2 className="scout-title">{T.scoutTitle[lang]}</h2>
        <p className="scout-sub">{T.scoutSub[lang]}</p>
      </div>

      {/* Round 1: 技术路线卡片 */}
      {phase === 'scout_round1' && (
        <div className="scout-round1">
          <div className="scout-header">
            {domainClass && (
              <span className="scout-domain">
                {T.scoutDomainLabel[lang]}: {domainClass}
              </span>
            )}
            <span className="scout-confidence">
              {T.scoutConfidenceLabel[lang]}: {confidence}
            </span>
          </div>
          {analysis && <p className="scout-analysis">{analysis}</p>}

          {contradictions.length > 0 && (
            <div className="scout-contradictions">
              <strong>{T.scoutContradictionLabel[lang]}:</strong>
              {contradictions.map((c, i) => (
                <p key={i} className="scout-contradiction-item">⚡ {c}</p>
              ))}
            </div>
          )}

          <p className="scout-hint">{T.scoutRound1Hint[lang]}</p>

          {loading && routes.length === 0 && (
            <div className="scout-loading">
              <span className="spinner" /> AI 正在扫描全球专利，识别技术路线...
            </div>
          )}

          <div className="scout-route-cards">
            {routes.map((route) => (
              <label
                key={route.id}
                className={`scout-route-card ${selectedIds.has(route.id) ? 'selected' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.has(route.id)}
                  onChange={() => toggleRoute(route.id)}
                />
                <div className="route-card-content">
                  <div className="route-card-name">{route.name}</div>
                  <div className="route-card-desc">{route.description}</div>
                  <div className="route-card-meta">
                    {route.companies.length > 0 && (
                      <span className="route-card-companies">
                        {route.companies.join(', ')}
                      </span>
                    )}
                    {route.patent_status_hint === 'expired' && (
                      <span className="route-card-frees">✅ Patent expired</span>
                    )}
                    {route.patent_status_hint === 'active' && (
                      <span className="route-card-warn">⚠️ Active patent</span>
                    )}
                    {route.confidence && (
                      <span className="route-card-conf">{route.confidence}</span>
                    )}
                  </div>
                </div>
              </label>
            ))}
          </div>

          {error && <div className="scout-error">{error}</div>}

          <div className="scout-actions">
            <button className="ghost-btn" onClick={onSkip} type="button">
              {T.scoutBtnSkip[lang]}
            </button>
            <button
              className="primary-btn"
              onClick={fetchRound2}
              disabled={loading || selectedIds.size === 0}
              type="button"
            >
              {loading ? 'Searching...' : T.scoutBtnNext[lang]}
            </button>
          </div>
        </div>
      )}

      {/* Round 2: 公司钻取 */}
      {phase === 'scout_round2' && (
        <div className="scout-round2">
          <p className="scout-hint">{T.scoutRound2Hint[lang]}</p>

          {routeDetails.map((rd) => (
            <div key={rd.route_id} className="scout-route-detail">
              <h3 className="route-detail-title">{rd.route_name}</h3>
              {rd.companies.map((c, ci) => (
                <div key={ci} className={`scout-company-card level-${c.level.toLowerCase()}`}>
                  <div className="company-card-header">
                    <span className="company-level">{c.level}</span>
                    <span className="company-name">{c.name}</span>
                    <span className="company-patent-status">
                      {c.patent_status === 'expired' && '✅ Expired'}
                      {c.patent_status === 'active' && '⚠️ Active'}
                      {c.patent_status === 'pending' && '⏳ Pending'}
                    </span>
                  </div>
                  <div className="company-card-tech">{c.tech_summary}</div>
                  {c.patent_number && (
                    <div className="company-card-patent">Patent: {c.patent_number}</div>
                  )}
                  {Object.keys(c.key_ctq).length > 0 && (
                    <div className="company-card-ctq">
                      {Object.entries(c.key_ctq).map(([k, v]) => (
                        <span key={k} className="ctq-chip">{k}: {v}</span>
                      ))}
                    </div>
                  )}
                  {c.notes.length > 0 && (
                    <div className="company-card-notes">
                      {c.notes.map((n, ni) => <p key={ni}>{n}</p>)}
                    </div>
                  )}
                  <div className="company-card-sources">
                    {c.source_labels.map((s, si) => (
                      <span key={si} className="source-label">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ))}

          {error && <div className="scout-error">{error}</div>}

          <div className="scout-actions">
            <button className="ghost-btn" onClick={() => setPhase('scout_round1')} type="button">
              {T.scoutBtnBack[lang]}
            </button>
            <button
              className="primary-btn"
              onClick={fetchOutput}
              disabled={loading}
              type="button"
            >
              {loading ? 'Generating...' : T.scoutBtnOutput[lang]}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
