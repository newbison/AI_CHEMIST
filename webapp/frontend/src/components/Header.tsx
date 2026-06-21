import type { Step } from '../types'
import type { Lang } from '../i18n'
import { T } from '../i18n'

const STEP_KEYS: { key: Step; labelKey: keyof typeof T; num: number }[] = [
  { key: 'input',    labelKey: 'stepInput',    num: 1 },
  { key: 'patents',  labelKey: 'stepPatents',  num: 2 },
  { key: 'report',   labelKey: 'stepReport',   num: 3 },
]

export default function Header({
  step,
  lang,
  setLang,
  onBack,
  onHome,
}: {
  step: Step
  lang: Lang
  setLang: (l: Lang) => void
  onBack?: () => void
  onHome?: () => void
}) {
  const currentIndex = STEP_KEYS.findIndex((s) => s.key === step)

  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-left">
          {(onBack || onHome) && (
            <div className="header-nav">
              {onBack && (
                <button className="header-nav-btn" onClick={onBack} title={T.headerBack[lang]}>
                  {T.headerBack[lang]}
                </button>
              )}
              {onHome && (
                <button className="header-nav-btn" onClick={onHome} title={T.headerHome[lang]}>
                  🏠
                </button>
              )}
            </div>
          )}
          <div className="logo">
            <span className="logo-mark">⚒️</span>
            <span className="logo-text">FORGE AI</span>
          </div>
        </div>
        <nav className="steps">
          {STEP_KEYS.map((s, i) => (
            <div
              key={s.key}
              className={`step ${i === currentIndex ? 'active' : ''} ${
                i < currentIndex ? 'done' : ''
              }`}
            >
              <span className="step-num">{s.num}</span>
              <span className="step-label">{T[s.labelKey][lang]}</span>
              {i < STEP_KEYS.length - 1 && <span className="step-line" />}
            </div>
          ))}
        </nav>
        <div className="header-lang">
          <button
            className={`header-lang-btn ${lang === 'en' ? 'active' : ''}`}
            onClick={() => setLang('en')}
          >EN</button>
          <button
            className={`header-lang-btn ${lang === 'zh' ? 'active' : ''}`}
            onClick={() => setLang('zh')}
          >中文</button>
        </div>
      </div>
    </header>
  )
}
