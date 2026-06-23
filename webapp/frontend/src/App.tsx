import { useState } from 'react'
import type { Step, SearchStrategy } from './types'
import type { Lang } from './i18n'
import InputStep from './components/InputStep'
import PatentsStep from './components/PatentsStep'
import DocumentStep from './components/DocumentStep'
import ReportStep from './components/ReportStep'
import Header from './components/Header'
import './styles.css'

export default function App() {
  const [step, setStep] = useState<Step>('input')
  const [lang, setLang] = useState<Lang>('en')
  const [voc, setVoc] = useState('')
  const [patents, setPatents] = useState<import('./types').Patent[]>([])
  const [selectedPatents, setSelectedPatents] = useState<import('./types').Patent[]>([])
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])
  const [docAnalysis, setDocAnalysis] = useState<string | null>(null)
  const [deepSearchData, setDeepSearchData] = useState<Record<string, unknown> | null>(null)

  return (
    <div className="app">
      <Header
        step={step}
        lang={lang}
        setLang={setLang}
        onBack={step !== 'input' ? () => {
          if (step === 'patents') setStep('input')
          else if (step === 'report') setStep('patents')
          else if (step === 'document') setStep('input')
        } : undefined}
        onHome={step !== 'input' ? () => {
          setStep('input')
          setVoc('')
          setPatents([])
          setSelectedPatents([])
          setStrategies([])
          setDocAnalysis(null)
        } : undefined}
      />
      <main className="main">
        {step === 'input' && (
          <InputStep
            lang={lang}
            voc={voc}
            setVoc={setVoc}
            onSearched={(all, selected, strats) => {
              setPatents(all)
              setSelectedPatents(selected)
              setStrategies(strats)
              setDeepSearchData(null)
              setStep('patents')
            }}
            onDeepSearchReport={(all, selected, strats, dsData) => {
              setPatents(all)
              setSelectedPatents(selected)
              setStrategies(strats)
              setDeepSearchData(dsData)
              setStep('patents')
            }}
          />
        )}
        {step === 'patents' && (
          <PatentsStep
            lang={lang}
            voc={voc}
            patents={patents}
            selected={selectedPatents}
            strategies={strategies}
            onSelectedChange={setSelectedPatents}
            onBack={() => setStep('input')}
            onHome={() => {
              setStep('input')
              setVoc('')
              setPatents([])
              setSelectedPatents([])
              setStrategies([])
            }}
            onGenerate={() => setStep('document')}
          />
        )}
        {step === 'report' && (
          <ReportStep
            lang={lang}
            voc={voc}
            patents={selectedPatents}
            docAnalysis={docAnalysis}
            deepSearchData={deepSearchData}
            onBack={() => setStep('document')}
            onHome={() => {
              setStep('input')
              setVoc('')
              setPatents([])
              setSelectedPatents([])
              setStrategies([])
              setDocAnalysis(null)
              setDeepSearchData(null)
            }}
          />
        )}
        {step === 'document' && (
          <DocumentStep
            lang={lang}
            onContinue={(analysis) => {
              setDocAnalysis(analysis)
              setStep('report')
            }}
            onSkip={() => {
              setDocAnalysis(null)
              setStep('report')
            }}
            onBack={() => setStep('patents')}
            onHome={() => {
              setStep('input')
              setVoc('')
              setPatents([])
              setSelectedPatents([])
              setStrategies([])
              setDocAnalysis(null)
            }}
          />
        )}
      </main>
    </div>
  )
}
