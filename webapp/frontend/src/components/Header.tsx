import type { Step } from '../types'

const STEPS: { key: Step; label: string; num: number }[] = [
  { key: 'input', label: 'VOC 输入', num: 1 },
  { key: 'patents', label: '专利确认', num: 2 },
  { key: 'report', label: '报告生成', num: 3 },
]

export default function Header({ step }: { step: Step }) {
  const currentIndex = STEPS.findIndex((s) => s.key === step)

  return (
    <header className="header">
      <div className="header-inner">
        <div className="logo">
          <span className="logo-mark">⬡</span>
          <span className="logo-text">R&D INTELLIGENCE</span>
        </div>
        <nav className="steps">
          {STEPS.map((s, i) => (
            <div
              key={s.key}
              className={`step ${i === currentIndex ? 'active' : ''} ${
                i < currentIndex ? 'done' : ''
              }`}
            >
              <span className="step-num">{s.num}</span>
              <span className="step-label">{s.label}</span>
              {i < STEPS.length - 1 && <span className="step-line" />}
            </div>
          ))}
        </nav>
      </div>
    </header>
  )
}
