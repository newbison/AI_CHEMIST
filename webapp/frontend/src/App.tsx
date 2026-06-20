import { useState } from 'react'
import type { Step, SearchStrategy } from './types'
import InputStep from './components/InputStep'
import PatentsStep from './components/PatentsStep'
import ReportStep from './components/ReportStep'
import Header from './components/Header'
import './styles.css'

export default function App() {
  const [step, setStep] = useState<Step>('input')
  const [voc, setVoc] = useState('')
  const [patents, setPatents] = useState<import('./types').Patent[]>([])
  const [selectedPatents, setSelectedPatents] = useState<import('./types').Patent[]>([])
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])

  return (
    <div className="app">
      <Header step={step} />
      <main className="main">
        {step === 'input' && (
          <InputStep
            voc={voc}
            setVoc={setVoc}
            onSearched={(all, selected, strats) => {
              setPatents(all)
              setSelectedPatents(selected)
              setStrategies(strats)
              setStep('patents')
            }}
          />
        )}
        {step === 'patents' && (
          <PatentsStep
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
            onGenerate={() => setStep('report')}
          />
        )}
        {step === 'report' && (
          <ReportStep
            voc={voc}
            patents={selectedPatents}
            onBack={() => setStep('patents')}
            onHome={() => {
              setStep('input')
              setVoc('')
              setPatents([])
              setSelectedPatents([])
              setStrategies([])
            }}
          />
        )}
      </main>
    </div>
  )
}
