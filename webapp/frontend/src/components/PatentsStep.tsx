import type { Patent, SearchStrategy } from '../types'

export default function PatentsStep({
  voc,
  patents,
  selected,
  strategies,
  onSelectedChange,
  onBack,
  onHome,
  onGenerate,
}: {
  voc: string
  patents: Patent[]
  selected: Patent[]
  strategies: SearchStrategy[]
  onSelectedChange: (p: Patent[]) => void
  onBack: () => void
  onHome: () => void
  onGenerate: () => void
}) {
  const selectedSet = new Set(selected.map((p) => p.patent_number))

  function toggle(p: Patent) {
    if (selectedSet.has(p.patent_number)) {
      onSelectedChange(selected.filter((s) => s.patent_number !== p.patent_number))
    } else {
      onSelectedChange([...selected, p])
    }
  }

  // 判断"前8篇"是否已全选（用于按钮状态提示）
  const top8Nums = new Set(patents.slice(0, 8).map((p) => p.patent_number))
  const isTop8Selected =
    selected.length === Math.min(8, patents.length) &&
    selected.every((p) => top8Nums.has(p.patent_number))

  function selectTop8() {
    onSelectedChange(patents.slice(0, 8))
  }

  function selectAll() {
    onSelectedChange([...patents])
  }

  function clearAll() {
    onSelectedChange([])
  }

  // 来源可信度标签：真实检索 vs AI生成(未核实)
  const REAL_SOURCES = new Set(['local_cache', 'uspto_patentsview', 'google_patents'])
  function sourceBadge(src: string): { label: string; cls: string } {
    if (src === 'llm_generated' || src === 'llm') {
      return { label: '⚠ AI生成·未核实', cls: 'badge-fabricated' }
    }
    if (REAL_SOURCES.has(src)) {
      return { label: '✓ 真实检索', cls: 'badge-real' }
    }
    return { label: src || '未知来源', cls: 'badge-unknown' }
  }

  return (
    <div className="step-container">
      <div className="step-hero">
        <h1 className="hero-title">确认入选专利</h1>
        <p className="hero-sub">
          共检索到 {patents.length} 篇专利，已默认选择前 8 篇。请勾选要纳入报告的专利。
        </p>
      </div>

      <div className="voc-recap">
        <span className="recap-label">VOC 摘要:</span>
        <span className="recap-text">{voc.slice(0, 120)}{voc.length > 120 ? '...' : ''}</span>
      </div>

      {strategies.length > 0 && (
        <div className="strategies-block">
          <div className="strategies-title">
            AI 从 VOC 拆解的 {strategies.length} 个搜索角度
          </div>
          <div className="strategies-list">
            {strategies.map((s, i) => (
              <div key={i} className="strategy-card">
                <div className="strategy-angle">{i + 1}. {s.angle}</div>
                <code className="strategy-query">{s.query}</code>
                {s.rationale && <div className="strategy-rationale">{s.rationale}</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="patent-actions">
        <button
          className={`ghost-btn ${isTop8Selected ? 'ghost-btn-active' : ''}`}
          onClick={selectTop8}
          disabled={isTop8Selected}
        >
          {isTop8Selected ? '✅ 已选前8篇' : '⭐ 选前8篇（推荐）'}
        </button>
        <button className="ghost-btn primary-ghost" onClick={selectAll}>☑ 全选（{patents.length} 篇）</button>
        <button className="ghost-btn" onClick={clearAll}>✕ 清空</button>
        <span className="patent-count">
          已选 <strong>{selected.length}</strong> / {patents.length} 篇
        </span>
      </div>

      <div className="patent-list">
        {patents.map((p, i) => {
          const checked = selectedSet.has(p.patent_number)
          return (
            <div
              key={p.patent_number + i}
              className={`patent-card ${checked ? 'checked' : ''}`}
              onClick={() => toggle(p)}
            >
              <div className="patent-check">
                <input type="checkbox" checked={checked} readOnly />
              </div>
              <div className="patent-body">
                <div className="patent-header">
                  <span className="patent-num">{p.patent_number}</span>
                  <span className="patent-country">{p.country}</span>
                  <span className={`patent-source ${sourceBadge(p.source).cls}`}>
                    {sourceBadge(p.source).label}
                  </span>
                  <span className="patent-date">{p.publication_date}</span>
                </div>
                <h3 className="patent-title">{p.title || '(无标题)'}</h3>
                <p className="patent-assignee">{p.assignee || '(未标注受让人)'}</p>
                <p className="patent-snippet">{p.snippet || '(无摘要)'}</p>
                {p.url && (
                  <a
                    href={p.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="patent-link"
                    onClick={(e) => e.stopPropagation()}
                  >
                    查看原文 ↗
                  </a>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="step-nav">
        <div className="step-nav-left">
          <button className="ghost-btn" onClick={onBack}>← 返回修改 VOC</button>
          <button className="ghost-btn home-btn" onClick={onHome}>🏠 返回主页</button>
        </div>
        <button
          className="primary-btn"
          onClick={onGenerate}
          disabled={selected.length === 0}
        >
          生成报告（{selected.length} 篇专利）→
        </button>
      </div>
    </div>
  )
}
