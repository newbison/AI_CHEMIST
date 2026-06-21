import { useState } from 'react'
import type { VocIdea, ExploreVocResponse } from '../types'

export default function ExploreStep({
  onSelect,
  onBack,
}: {
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
      setError('Please enter a product category')
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
        <h1 className="hero-title">Explore VOC Ideas</h1>
        <p className="hero-sub">
          Describe your product and industry context. AI will generate 12 research
          questions — pick one to analyze.
        </p>
      </div>

      {ideas.length === 0 ? (
        <div className="form-block">
          <label className="form-label">
            <span className="label-tag">Product</span>
            Product Category
          </label>
          <input
            className="voc-input"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="e.g., UV-curable hard coats, Ti alloys for implants, PSA tapes for batteries..."
          />

          <label className="form-label" style={{ marginTop: '16px' }}>
            <span className="label-tag">Context</span>
            Industry Context (optional)
          </label>
          <textarea
            className="voc-input"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="e.g., Our formulation yellows after 2 years. Competitor X launched a 5-year weatherable version."
            rows={3}
          />

          <label className="form-label" style={{ marginTop: '16px' }}>
            <span className="label-tag">Direction</span>
            Innovation Direction (optional)
          </label>
          <div className="num-select-group">
            {(['', 'next-gen', 'cost-down', 'adjacent'] as const).map((d) => {
              const labels: Record<string, string> = {
                '': 'All directions',
                'next-gen': 'Next-gen performance',
                'cost-down': 'Cost-down',
                'adjacent': 'Adjacent markets',
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
                <span className="spinner" /> AI is generating research ideas...
              </>
            ) : (
              'Generate 12 VOC Ideas →'
            )}
          </button>

          <button
            className="ghost-btn"
            onClick={onBack}
            style={{ marginTop: '12px' }}
          >
            ← Back
          </button>
        </div>
      ) : (
        <div className="explore-results">
          <div className="explore-results-header">
            <h2>12 Research Ideas for "{product}"</h2>
            <p>Click one to use it as your VOC and start analysis.</p>
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
                <><span className="spinner" /> Generating...</>
              ) : (
                '🔄 Regenerate 12 Ideas'
              )}
            </button>
            <button
              className="ghost-btn"
              onClick={() => {
                setIdeas([])
                setError('')
              }}
            >
              ← Try a different product
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
