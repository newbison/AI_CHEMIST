import { useState } from 'react'
import { T } from '../i18n'
import type { Lang } from '../i18n'
import type { VocIdea, ExploreVocResponse } from '../types'

export default function ExploreStep({
  lang,
  onSelect,
  onBack,
}: {
  lang: Lang
  onSelect: (voc: string) => void
  onBack: () => void
}) {
  const [product, setProduct] = useState('')
  const [context, setContext] = useState('')
  const [direction, setDirection] = useState('')
  const [generating, setGenerating] = useState(false)
  const [ideas, setIdeas] = useState<VocIdea[]>([])
  const [error, setError] = useState('')

  async function handleGenerate() {
    if (!product.trim()) {
      setError(T.exploreErrorEmpty[lang])
      return
    }
    setGenerating(true)
    setError('')
    setIdeas([])

    try {
      const resp = await fetch('/api/explore-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product: product.trim(),
          context: context.trim(),
          direction,
          num_ideas: 12,
          seed: Date.now(),  // force fresh ideas each call
        }),
      })
      if (!resp.ok) throw new Error(`Generation failed: ${resp.status}`)
      const data: ExploreVocResponse = await resp.json()

      if (data.ideas.length === 0) {
        setError(data.warning || 'No ideas generated. Please try a different product category.')
      } else {
        setIdeas(data.ideas)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation error')
    }
    setGenerating(false)
  }

  return (
    <div className="step-container">
      <div className="step-hero">
        <h1 className="hero-title">{T.exploreTitle[lang]}</h1>
        <p className="hero-sub">{T.exploreSub[lang]}</p>
      </div>

      {ideas.length === 0 ? (
        <div className="form-block">
          <label className="form-label">
            <span className="label-tag">{T.exploreProductLabel[lang]}</span>
            {T.exploreProductLabel[lang]}
          </label>
          <input
            className="voc-input"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder={T.exploreProductPlaceholder[lang]}
          />

          <label className="form-label" style={{ marginTop: '16px' }}>
            <span className="label-tag">{T.exploreContextLabel[lang]}</span>
            {T.exploreContextLabel[lang]}
          </label>
          <textarea
            className="voc-input"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder={T.exploreContextPlaceholder[lang]}
            rows={3}
          />

          <label className="form-label" style={{ marginTop: '16px' }}>
            <span className="label-tag">{T.exploreDirectionLabel[lang]}</span>
            {T.exploreDirectionLabel[lang]}
          </label>
          <div className="num-select-group">
            {(['', 'next-gen', 'cost-down', 'adjacent'] as const).map((d) => {
              const labels: Record<string, string> = {
                '': T.exploreDirAll[lang],
                'next-gen': T.exploreDirNextGen[lang],
                'cost-down': T.exploreDirCostDown[lang],
                'adjacent': T.exploreDirAdjacent[lang],
              }
              return (
                <button
                  key={d}
                  type="button"
                  className={`num-chip ${direction === d ? 'active' : ''}`}
                  onClick={() => setDirection(d)}
                >
                  {labels[d]}
                </button>
              )
            })}
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button
            className="primary-btn"
            onClick={handleGenerate}
            disabled={generating || !product.trim()}
            style={{ marginTop: '20px' }}
          >
            {generating ? (
              <>
                <span className="spinner" /> {T.exploreGenerating[lang]}
              </>
            ) : (
              T.exploreGenerate[lang]
            )}
          </button>

          <button
            className="ghost-btn"
            onClick={onBack}
            style={{ marginTop: '12px' }}
          >
            {T.exploreBack[lang]}
          </button>
        </div>
      ) : (
        <div className="explore-results">
          <div className="explore-results-header">
            <h2>{T.exploreResultsTitle[lang]} "{product}"</h2>
            <p>{T.exploreResultsSub[lang]}</p>
          </div>

          <div className="voc-idea-list">
            {ideas.map((idea, i) => (
              <div
                key={i}
                className="voc-idea-card"
                onClick={() => onSelect(idea.voc)}
              >
                <div className="voc-idea-number">{i + 1}</div>
                <div className="voc-idea-body">
                  <div className="voc-idea-text">{idea.voc}</div>
                  <div className="voc-idea-why">💡 {idea.why}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="explore-results-actions">
            <button
              className="primary-btn"
              onClick={handleGenerate}
              disabled={generating}
            >
              {generating ? (
                <><span className="spinner" /> {T.exploreGenerating[lang]}</>
              ) : (
                T.exploreRegenerate[lang]
              )}
            </button>
            <button
              className="ghost-btn"
              onClick={() => {
                setIdeas([])
                setError('')
              }}
            >
              {T.exploreTryDifferent[lang]}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
