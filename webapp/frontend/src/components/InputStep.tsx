import { useState, useEffect, useRef } from 'react'
import { T } from '../i18n'
import type { Patent, SearchResponse, SearchStrategy, AnalyzeVocResponse, ClarifyQuestion, ClarifyVocResponse, EnrichVocResponse, ScoutOutputResponse, DeepSearchOutput } from '../types'
import ExploreStep from './ExploreStep'
import ScoutStep from './ScoutStep'

/** 材料科学领域 VOC 示例池（每次随机展示 12 个，中英文双语，应用导向无具体参数） */
const VOC_POOL: { en: string; zh: string }[] = [
  {
    en: "Battery cell termination tape that maintains adhesion after long-term exposure to electrolyte at high temperatures. The tape should not swell, leave residue, or contaminate the electrolyte. It must provide reliable electrical insulation and work stably under thermal cycling. Additionally, it should be easy to apply and remove during manufacturing.",
    zh: "一种电池终止胶带，在高温电解液中长期浸泡后仍保持粘接力。不溶胀、无残胶、不污染电解液。电气绝缘可靠，冷热循环下稳定工作。便于产线贴附和撕除定位。"
  },
  {
    en: "Silicon-carbon composite anode material for lithium-ion batteries that achieves high capacity while maintaining structural stability during charge-discharge cycles. The material should minimize volume expansion and be compatible with existing graphite production lines.",
    zh: "一种锂离子电池用硅碳复合负极材料，在充放电循环中保持结构稳定的高容量表现。需控制体积膨胀，与现有石墨负极产线兼容。"
  },
  {
    en: "Surface coating for titanium orthopedic implants that provides long-term stability in body fluid environment without degradation or metal ion release over 10 years. The coating must promote bone integration and maintain mechanical properties such as hardness and fatigue resistance.",
    zh: "一种钛合金骨科植入物表面涂层，在体液环境下10年以上不降解、不释放金属离子。需促进骨整合，保持硬度和耐疲劳等机械性能。"
  },
  {
    en: "Transparent conductive film for flexible OLED displays that achieves high optical transmittance and low sheet resistance while maintaining performance after repeated bending. The film should be compatible with roll-to-roll manufacturing processes.",
    zh: "一种柔性OLED显示屏用透明导电薄膜，具有高透光率和低方阻，弯折多次后仍保持性能。需与卷对卷生产工艺兼容。"
  },
  {
    en: "Electrochromic smart window glass that can switch between transparent and tinted states quickly and repeatedly. The device should have long cycle life and work reliably in large-area applications.",
    zh: "一种电致变色智能窗玻璃，能在透明和着色状态间快速反复切换。需具有长循环寿命，在大面积应用中可靠工作。"
  },
  {
    en: "Proton exchange membrane for hydrogen fuel cells that enables high proton conductivity under operating conditions while providing excellent chemical stability and mechanical strength suitable for hot-pressing membrane electrode assembly.",
    zh: "一种氢燃料电池质子交换膜，在工作条件下实现高质子电导率，同时具备优异的化学稳定性和适合热压MEA装配的机械强度。"
  },
  {
    en: "Perovskite solar cell light-absorbing layer that achieves high power conversion efficiency while maintaining stability under continuous illumination and humidity exposure. The material should be suitable for large-area solution-based coating processes.",
    zh: "一种钙钛矿太阳能电池吸光层，在连续光照和湿度环境下保持稳定的高转换效率。需适合溶液法大面积涂布工艺。"
  },
  {
    en: "Low-emissivity glass coating for architectural applications that provides good thermal insulation performance while maintaining high visible light transmission. The coating should withstand outdoor weathering for at least 10 years without significant performance degradation.",
    zh: "一种建筑用低辐射玻璃镀膜，在保持高可见光透射的同时提供良好的隔热性能。需耐户外老化10年以上，性能衰减小。"
  },
  {
    en: "Superhydrophobic self-cleaning exterior wall coating that maintains water repellency and self-cleaning properties over long-term outdoor exposure. The coating should be easy to apply and have a service life of at least 10 years.",
    zh: "一种超疏水自清洁建筑外墙涂层，在长期户外环境下保持疏水自清洁性能。需施工方便，使用寿命10年以上。"
  },
  {
    en: "Wear-resistant self-lubricating polymer composite for precision engineering components such as gears and bearings. The material should maintain stable performance across a wide temperature range and be suitable for injection molding.",
    zh: "一种耐磨自润滑聚合物复合材料，用于精密齿轮和轴承等工程部件。需在宽温度范围内保持稳定性能，适合注塑成型。"
  },
  {
    en: "Epoxy molding compound for semiconductor packaging that provides high glass transition temperature, low thermal expansion, and high reliability under temperature and humidity stress. The material should be suitable for high-reliability IC packaging with no voids or warpage after molding.",
    zh: "一种半导体封装用环氧塑封料，具有高玻璃化转变温度、低热膨胀系数，在温湿度应力下高可靠性。需适合高可靠性IC封装，成型后无气泡、无翘曲。"
  },
  {
    en: "Thermal interface material for electronic device heat dissipation that maintains stable thermal conductivity over long-term high-temperature operation. The material should not corrode chips or leak, and be suitable for screen printing or compression molding.",
    zh: "一种电子器件散热用导热界面材料，在长期高温工作下保持稳定导热率。需与芯片无腐蚀、无渗漏，适合丝网印刷或模压成型。"
  },
  {
    en: "Reverse osmosis composite membrane for seawater desalination that achieves high salt rejection and high water flux under standard test conditions. The membrane should have good chlorine resistance and stable performance across a wide pH range for cleaning.",
    zh: "一种海水淡化用反渗透复合膜，在标准测试条件下实现高脱盐率和高水通量。需具有良好的耐氯性，在宽pH范围内稳定清洗。"
  },
  {
    en: "Carbon paper gas diffusion layer for fuel cells that provides suitable porosity and gas permeability while maintaining good electrical conductivity and mechanical strength. The material should be suitable for roll pressing and surface hydrophobic treatment.",
    zh: "一种燃料电池用碳纸气体扩散层，具有合适的孔隙率和透气率，同时保持良好的导电性和机械强度。需适合辊压成型和表面疏水处理。"
  },
  {
    en: "Carbon fiber reinforced epoxy composite for structural applications that achieves high strength and modulus while maintaining good fatigue resistance and hot-wet environment stability. The material should be suitable for prepreg-autoclave molding with low void content.",
    zh: "一种结构用碳纤维增强环氧树脂复合材料，具有高强度和高模量，同时保持良好的耐疲劳性和湿热环境稳定性。需适合预浸料热压罐成型，孔隙率低。"
  },
  {
    en: "High-temperature resistant adhesive for aerospace applications that maintains mechanical properties over a wide temperature range from cryogenic to elevated temperatures. The adhesive should be suitable for honeycomb structure bonding and have a practical curing cycle.",
    zh: "一种航空航天用耐高温胶粘剂，在从低温到高温的宽温度范围内保持机械性能。需适合蜂窝结构粘接，具有实用的固化工艺。"
  },
  {
    en: "Electrically conductive silver paste for stretchable electronics that maintains stable electrical conductivity under repeated stretching. The paste should be compatible with common substrate materials and suitable for screen or inkjet printing.",
    zh: "一种可拉伸电子用导电银浆，在反复拉伸下保持稳定的导电性。需与常见基底材料兼容，适合丝网印刷或喷墨打印。"
  },
  {
    en: "Conductive silicone rubber for electromagnetic interference shielding in 5G base station applications. The material should provide excellent shielding effectiveness across a wide frequency range while maintaining flexibility and durability.",
    zh: "一种5G基站用电磁屏蔽导电硅橡胶，在宽频段范围内提供优异屏蔽效能，同时保持柔性和耐久性。"
  },
  {
    en: "Sulfide solid-state electrolyte for all-solid-state batteries that demonstrates high ionic conductivity at room temperature and good interfacial stability with lithium metal. The material should be suitable for dry electrode coating processes.",
    zh: "一种全固态电池用硫化物固体电解质，在室温下展现高离子电导率，与锂金属界面稳定。需适合干法电极涂布工艺。"
  },
  {
    en: "Artificial solid electrolyte interphase for lithium metal batteries that enables uniform lithium plating and suppresses dendrite growth. The interphase should be ultra-thin, mechanically robust, and stable over many cycles.",
    zh: "一种锂金属电池用人工固态电解质界面，实现均匀锂沉积并抑制枝晶生长。需超薄、机械强度高、多次循环稳定。"
  },
  {
    en: "Biodegradable packaging film that degrades completely in soil within a specified timeframe while maintaining necessary mechanical and barrier properties. The material should be suitable for blown film extrusion and cost-competitive for food packaging applications.",
    zh: "一种在土壤中特定时间内完全降解的生物降解包装薄膜，同时保持必要的机械性能和阻隔性能。需适合吹膜工艺，成本有竞争力用于食品包装。"
  },
  {
    en: "Wear-resistant anti-corrosion epoxy coating for offshore steel structures that withstands harsh marine environment including salt spray and cathodic protection conditions. The coating should be suitable for airless spray application.",
    zh: "一种海洋钢结构用耐磨防腐环氧涂层，能承受盐雾和阴极保护等恶劣海洋环境。需适合无气喷涂施工。"
  },
  {
    en: "Piezoelectric ceramic material for medical ultrasound transducers that achieves high piezoelectric constants and coupling coefficients while maintaining good temperature stability. The material should be suitable for sintering forming with consistent properties.",
    zh: "一种医用超声换能器压电陶瓷材料，具有高压电常数和耦合系数，同时保持良好的温度稳定性。需适合烧结成型，性能一致性好。"
  },
  {
    en: "Phase change thermal management material for electronic devices that provides effective heat dissipation through latent heat absorption. The material should not corrode chips, maintain stable performance over many thermal cycles, and be suitable for thin-film applications.",
    zh: "一种电子器件用相变热管理材料，通过潜热吸收提供有效散热。需不腐蚀芯片，在多次热循环下性能稳定，适合薄膜应用。"
  },
  {
    en: "Medical catheter polyurethane elastomer with good flexibility, blood compatibility, and gamma sterilization stability. The material should be suitable for extrusion molding and meet requirements for central venous catheter applications.",
    zh: "一种具有良好的柔韧性、血液相容性和γ射线灭菌稳定性的医用导管聚氨酯弹性体。需适合挤出成型，满足中心静脉导管应用要求。"
  },
  {
    en: "Radiation-resistant cable insulation material for nuclear power plant applications that maintains mechanical properties after high-dose gamma radiation exposure. The material should be suitable for extrusion molding with consistent wall thickness.",
    zh: "一种核电站用电缆辐射防护绝缘材料，在高剂量γ射线辐照后保持机械性能。需适合挤出成型，壁厚均匀一致。"
  },
  {
    en: "Self-healing polymer coating for automotive clearcoat applications that can repair surface scratches autonomously under ambient conditions. The coating should maintain transparency, weather resistance, and be suitable for spray application.",
    zh: "一种汽车清漆用自修复聚合物涂层，能在常温下自动修复表面划痕。需保持透明度、耐老化，适合喷涂施工。"
  },
  {
    en: "Piezoelectric single crystal material for medical ultrasound and underwater acoustic applications that achieves ultra-high piezoelectric performance. The material should be suitable for Bridgman crystal growth method and provide consistent properties.",
    zh: "一种用于医用超声和水声换能器的压电单晶材料，实现超高压电性能。需适合布里奇曼法生长，提供一致的性能。"
  },
  {
    en: "Sodium-ion battery hard carbon anode material that achieves reversible capacity from biomass precursors while maintaining good first-cycle efficiency and cycle stability. The material should be cost-effective and suitable for carbonization processes.",
    zh: "一种生物质前驱体钠离子电池硬碳负极材料，从生物质前驱体实现可逆容量，同时保持良好的首效和循环稳定性。需成本经济，适合碳化工艺。"
  },
  {
    en: "Absorbable hemostatic sponge for surgical applications that achieves rapid hemostasis in blood and gets absorbed by the body within a specified timeframe. The material should be sterile, non-pyrogenic, and suitable for freeze-drying manufacturing.",
    zh: "一种外科用可吸收止血海绵，在血液中快速止血并在特定时间内被体内吸收。需无菌、无致热原，适合冻干成型工艺。"
  },
]

/** 从池中随机抽取 n 个不重复的 VOC（根据当前语言） */
function pickRandomVocs(pool: { en: string; zh: string }[], n: number, lang: 'en' | 'zh'): string[] {
  const arr = [...pool]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr.slice(0, Math.min(n, arr.length)).map(v => v[lang])
}

/** 截取 VOC 前 40 字作为卡片标题 */
function vocTitle(voc: string): string {
  const t = voc.length > 40 ? voc.slice(0, 40) + '...' : voc
  return t
}

export default function InputStep({
  lang,
  voc,
  setVoc,
  onSearched,
  onDeepSearchReport,
}: {
  lang: import('../i18n').Lang
  voc: string
  setVoc: (v: string) => void
  onSearched: (all: Patent[], selected: Patent[], strategies: SearchStrategy[]) => void
  onDeepSearchReport?: (all: Patent[], selected: Patent[], strategies: SearchStrategy[], deepSearchData: Record<string, unknown>) => void
}) {
  // 阶段：'input' → 'scout' → 'deepsearch' → 'clarify' → 'enriched' → 'explore' → 'keywords'
  const [phase, setPhase] = useState<'input' | 'scout' | 'deepsearch' | 'clarify' | 'enriched' | 'explore' | 'keywords'>('input')
  const [analyzing, setAnalyzing] = useState(false)
  const [searching, setSearching] = useState(false)
  const [clarifying, setClarifying] = useState(false)
  const [enriching, setEnriching] = useState(false)
  const [error, setError] = useState('')
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])
  const [patentNum, setPatentNum] = useState<number>(20)
  const [sampleVocs, setSampleVocs] = useState<string[]>(() => pickRandomVocs(VOC_POOL, 12, lang))
  // 澄清环节状态
  const [clarifyQuestions, setClarifyQuestions] = useState<ClarifyQuestion[]>([])
  const [clarifyAnalysis, setClarifyAnalysis] = useState('')
  const [clarifyAnswers, setClarifyAnswers] = useState<Record<string, string>>({})
  const [enrichedVoc, setEnrichedVoc] = useState('')
  const [enrichChanges, setEnrichChanges] = useState<string[]>([])
  // Deep Search 状态
  const [scoutOutput, setScoutOutput] = useState<ScoutOutputResponse | null>(null)
  const [marketShare, setMarketShare] = useState<any>(null)
  const [dsResult, setDsResult] = useState<any>(null)
  const [dsLoading, setDsLoading] = useState(false)
  const [mrResult, setMrResult] = useState<any>(null)
  const [mrLoading, setMrLoading] = useState(false)
  const [mrProgress, setMrProgress] = useState<{ completed: number; total: number } | null>(null)
  const dsStartedRef = useRef(false)

  // 触发 VOC 澄清：调 /api/clarify-voc 生成选择题
  async function handleClarify() {
    if (!voc.trim()) {
      setError('请输入 VOC')
      return
    }
    setClarifying(true)
    setError('')
    try {
      const resp = await fetch('/api/clarify-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voc, num_questions: 4 }),
      })
      if (!resp.ok) throw new Error(`澄清失败: ${resp.status}`)
      const data: ClarifyVocResponse = await resp.json()
      if (data.questions.length === 0) {
        // 澄清失败，直接进入关键词生成
        setClarifying(false)
        handleAnalyze()
        return
      }
      setClarifyQuestions(data.questions)
      setClarifyAnalysis(data.analysis || '')
      setClarifyAnswers({})
      setPhase('clarify')
    } catch (e) {
      setError(e instanceof Error ? e.message : '澄清出错，已跳过')
      // 失败时直接进入关键词生成
      handleAnalyze()
    }
    setClarifying(false)
  }

  // 选择某题的某个选项
  function selectAnswer(qid: string, option: string) {
    setClarifyAnswers((prev) => ({ ...prev, [qid]: option }))
  }

  // 选择"以上都不是"并输入自定义答案
  function setCustomAnswer(qid: string, text: string) {
    setClarifyAnswers((prev) => ({ ...prev, [qid]: `custom:${text}` }))
  }

  // 提交澄清答案，生成增强 VOC
  async function handleEnrich() {
    setEnriching(true)
    setError('')
    try {
      const resp = await fetch('/api/enrich-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_voc: voc,
          questions: clarifyQuestions,
          answers: clarifyAnswers,
        }),
      })
      if (!resp.ok) throw new Error(`增强失败: ${resp.status}`)
      const data: EnrichVocResponse = await resp.json()
      setEnrichedVoc(data.enriched_voc || voc)
      setEnrichChanges(data.changes || [])
      setPhase('enriched')
    } catch (e) {
      setError(e instanceof Error ? e.message : '增强出错')
      // 失败时用原 VOC 直接进入关键词生成
      handleAnalyze()
    }
    setEnriching(false)
  }

  // 确认增强 VOC，进入关键词生成
  function confirmEnriched() {
    setVoc(enrichedVoc)
    setPhase('keywords')
    // 自动触发关键词生成
    setTimeout(() => handleAnalyze(), 0)
  }

  // 从 enriched 返回 clarify 重新答
  function backToClarify() {
    setPhase('clarify')
  }

  // 生成关键词
  async function handleAnalyze() {
    if (!voc.trim()) {
      setError('请输入 VOC')
      return
    }
    setAnalyzing(true)
    setError('')
    try {
      const resp = await fetch('/api/analyze-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voc, num_angles: 4 }),
      })
      if (!resp.ok) throw new Error(`分析失败: ${resp.status}`)
      const data: AnalyzeVocResponse = await resp.json()
      if (data.strategies.length === 0) {
        // 回退：用 fallback_keywords 作为单条策略
        if (data.fallback_keywords) {
          setStrategies([{
            angle: '关键词提取（LLM 分析失败，已回退）',
            query: data.fallback_keywords,
            rationale: '可手动修改后检索',
          }])
        } else {
          setError(data.warning || 'VOC 分析失败，请重试或手动输入关键词')
          setAnalyzing(false)
          return
        }
      } else {
        setStrategies(data.strategies)
      }
      setPhase('keywords')
    } catch (e) {
      setError(e instanceof Error ? e.message : '分析出错')
    }
    setAnalyzing(false)
  }

  // 修改某条策略的 query
  function updateStrategyQuery(idx: number, query: string) {
    setStrategies((prev) => prev.map((s, i) => (i === idx ? { ...s, query } : s)))
  }

  // 删除某条策略
  function removeStrategy(idx: number) {
    setStrategies((prev) => prev.filter((_, i) => i !== idx))
  }

  // 添加自定义策略
  function addStrategy() {
    setStrategies((prev) => [...prev, { angle: '自定义角度', query: '', rationale: '手动添加' }])
  }

  // 重新生成关键词（清空 VOC 重新开始）
  function reAnalyze() {
    setVoc('')
    setStrategies([])
    setPhase('input')
  }

  // 确认关键词并开始检索
  async function handleSearch() {
    const valid = strategies.filter((s) => s.query.trim())
    if (valid.length === 0) {
      setError('请至少保留一条有效的搜索关键词')
      return
    }
    setSearching(true)
    setError('')
    try {
      const resp = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voc,
          strategies: valid,
          num: patentNum,
        }),
      })
      if (!resp.ok) throw new Error(`检索失败: ${resp.status}`)
      const data: SearchResponse = await resp.json()
      if (data.patents.length === 0) {
        setError(data.warning || '未找到专利，请尝试调整关键词')
        setSearching(false)
        return
      }
      const selected = data.patents.slice(0, 8)
      onSearched(data.patents, selected, data.strategies || [])
    } catch (e) {
      setError(e instanceof Error ? e.message : '检索出错')
    }
    setSearching(false)
  }

  // Deep Search：进入 deepsearch 阶段时自动调用
  useEffect(() => {
    if (phase !== 'deepsearch' || !scoutOutput || dsStartedRef.current) return
    dsStartedRef.current = true
    async function runDeepSearch() {
      setDsLoading(true)
      setError('')
      try {
        const resp = await fetch('/api/deep-search/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            voc,
            domain_class: '',
            p0_companies: scoutOutput!.companies.priority.filter(c => c.level === 'P0').map(c => c.name),
            p1_companies: scoutOutput!.companies.priority.filter(c => c.level === 'P1').map(c => c.name),
            core_keywords: scoutOutput!.keywords.core || [],
            supp_keywords: scoutOutput!.keywords.supplement || [],
            exclude_keywords: scoutOutput!.keywords.exclude || [],
            core_ipc: scoutOutput!.ipc.core || [],
            supp_ipc: scoutOutput!.ipc.supplement || [],
            fto_notes: scoutOutput!.fto.notes || [],
            round_history: scoutOutput!.round_history || [],
          }),
        })
        if (!resp.ok) throw new Error(`Deep Search failed: ${resp.status}`)
        const data = await resp.json()
        setDsResult(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Deep Search error')
      }
      setDsLoading(false)
    }
    runDeepSearch()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, scoutOutput])

  // Map-Reduce：对 Deep Search 返回的 capped 专利号运行 CTQ 提取（SSE 流式进度）
  async function runMapReduce() {
    if (!dsResult?.patent_numbers?.length) return
    setMrLoading(true)
    setMrProgress(null)
    setError('')
    try {
      const resp = await fetch('/api/deep-search/map-reduce', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patent_numbers: dsResult.patent_numbers,
          max_patents: dsResult.patent_numbers.length,
        }),
      })
      if (!resp.ok) throw new Error(`Map-Reduce failed: ${resp.status}`)

      const reader = resp.body?.getReader()
      if (!reader) throw new Error('No response body reader')
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const msg = JSON.parse(line.slice(6))
              if (msg.type === 'progress' && msg.stage === 'ctq') {
                setMrProgress({ completed: msg.completed, total: msg.total })
              } else if (msg.type === 'reduce_start') {
                setMrProgress(null) // clear counter, show "aggregating..."
              } else if (msg.type === 'done') {
                setMrResult(msg.result)
              } else if (msg.type === 'error') {
                setError(msg.message || 'Map-Reduce error')
              }
            } catch { /* skip parse errors on heartbeat lines */ }
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Map-Reduce error')
    }
    setMrLoading(false)
    setMrProgress(null)
  }

/** MR 统计信息 */
interface MrStats {
  fetch_success_rate?: string
  ctq_extracted?: number
  total_requested?: number
}

/** MR 结果类型 */
interface MrResult {
  stats?: MrStats
  ctq_comparison_table?: Record<string, unknown>[]
  ctq_records?: Record<string, unknown>[]
}

  // 根据 DS 收敛状态 + MR 统计自动生成已知局限
  function buildKnownLimitations(ds: DeepSearchOutput, mr: MrResult): string[] {
    const limits: string[] = []
    if (!ds.converged) {
      limits.push('搜索未完全收敛，可能存在未覆盖的技术路线或公司')
    }
    if (mr?.stats) {
      const rate = mr.stats.fetch_success_rate || ''
      if (rate.includes('⚠️')) {
        limits.push('部分专利全文抓取失败，CTQ 数据可能不完整')
      }
      limits.push(`CTQ 提取覆盖率: ${mr.stats.ctq_extracted || 0}/${mr.stats.total_requested || 0} 篇专利`)
    }
    limits.push('中文实用新型、日文/韩文专利未系统检索')
    limits.push('本报告适合行业格局初判与技术方向选择，不适合 FTO 最终法律判断')
    limits.push('专利法律状态为基于公开日的估算，正式 FTO 请以各国专利局登记簿为准')
    return limits
  }

  // 将 Deep Search 结果 + Scout 输出打包，送往报告生成
  function handleDeepSearchReport() {
    if (!dsResult?.patents || !onDeepSearchReport) return

    // 转换 DS 专利为 Patent[] 格式
    const patents = dsResult.patents || []
    const allPatents: Patent[] = patents.map((p: Patent) => ({
      patent_number: p.patent_number || '',
      title: p.title || '',
      assignee: p.assignee || '',
      snippet: p.snippet || '',
      publication_date: p.publication_date || '',
      source: p.source || 'deep_search',
      url: p.url || '',
      country: p.country || '',
    }))

    // 组装 Deep Search 全景数据（直接喂给 prompt_builder）
    const dsData: Record<string, unknown> = {
      // 市场份额
      market_share: marketShare,
      // 公司优先级
      companies: scoutOutput?.companies || {},
      // CTQ 表
      ctq_table: mrResult?.ctq_comparison_table || [],
      ctq_records: mrResult?.ctq_records || [],
      // 技术路线（从 scoutOutput 或 dsResult）
      tech_routes: dsResult.routes || [],
      // FTO
      fto: dsResult.fto || {},
      // 搜索路径 + 收敛
      search_path: dsResult.search_path || '',
      converged: dsResult.converged || false,
      total_companies_found: dsResult.total_companies_found || 0,
      total_found: dsResult.total_found || 0,
      cap_note: dsResult.cap_note || '',
      // 建议
      recommendation: dsResult.recommendation || {},
      // 领域 + 信心
      domain_class: dsResult.domain_class || '',
      confidence: dsResult.confidence || '★★☆',
      // 已知局限（由 DS 收敛状态决定）
      known_limitations: buildKnownLimitations(dsResult, mrResult),
    }

    onDeepSearchReport(allPatents, allPatents.slice(0, 8), [], dsData)
  }

  return (
    <div className="step-container">
      {phase === 'input' && (
        <div className="home-hero">
          <h1 className="home-hero-title">{T.homeTitle[lang]}</h1>
          <p className="home-hero-tagline">{T.homeTagline[lang]}</p>
          <p className="home-hero-desc">{T.homeDesc[lang]}</p>
          <div className="home-hero-caps">
            <span>{T.homeCap1[lang]}</span>
            <span>{T.homeCap2[lang]}</span>
            <span>{T.homeCap3[lang]}</span>
            <span>{T.homeCap4[lang]}</span>
            <span>{T.homeCap5[lang]}</span>
          </div>
        </div>
      )}

      {phase !== 'input' && (
        <div className="step-hero">
          <h1 className="hero-title">输入客户需求</h1>
          <p className="hero-sub">
            输入 VOC（Voice of Customer），AI 会先分析 VOC 拆解出多个技术角度并生成英文检索关键词，
            供您确认或修改后再联网检索专利，最终生成完整 R&D 智能报告。
          </p>
        </div>
      )}

      {/* 双入口：用户选路径 */}
      {phase === 'input' && (
        <div className="entry-cards">
          <div className="entry-card entry-card-primary" onClick={() => setPhase('input')}>
            <div className="entry-card-icon">📝</div>
            <h3 className="entry-card-title">{T.entryCard1Title[lang]}</h3>
            <p className="entry-card-desc">{T.entryCard1Desc[lang]}</p>
          </div>
          <div className="entry-card" onClick={() => setPhase('explore')}>
            <div className="entry-card-icon">💡</div>
            <h3 className="entry-card-title">{T.entryCard2Title[lang]}</h3>
            <p className="entry-card-desc">{T.entryCard2Desc[lang]}</p>
          </div>
        </div>
      )}

      {/* VOC 示例池：随机 12 个材料科学场景 */}
      {phase === 'input' && (
        <div className="form-block">
          <label className="form-label">
            <span className="label-tag">示例</span>
            材料科学 VOC 示例（随机 12 个，点击试用）
          </label>
          <div className="voc-samples">
            {sampleVocs.map((v, i) => (
              <button
                key={i}
                className="voc-sample-card"
                onClick={() => setVoc(v)}
                type="button"
                title={v}
              >
                {vocTitle(v)}
              </button>
            ))}
          </div>
          <button
            className="link-btn"
            onClick={() => setSampleVocs(pickRandomVocs(VOC_POOL, 12, lang))}
            type="button"
          >
            ↻ 换一批示例
          </button>
        </div>
      )}

      <div className="form-block">
        <label className="form-label">
          <span className="label-tag">VOC</span>
          客户需求描述
        </label>
        <textarea
          className="voc-input"
          value={voc}
          onChange={(e) => setVoc(e.target.value)}
          placeholder="描述客户对材料/产品的性能、工艺、应用场景需求..."
          rows={6}
        />
      </div>

      {phase === 'input' && (
        <div className="input-phase-buttons" style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            className="primary-btn"
            onClick={() => setPhase('scout')}
            disabled={clarifying || analyzing || !voc.trim()}
            type="button"
          >
            AI Scout: 浏览技术全景 →
          </button>
          <button
            className="ghost-btn"
            onClick={handleClarify}
            disabled={clarifying || analyzing || !voc.trim()}
            type="button"
          >
            {clarifying ? (
              <>
                <span className="spinner" /> AI 分析 VOC 生成澄清问题...
              </>
            ) : analyzing ? (
              <>
                <span className="spinner" /> AI 分析 VOC 生成检索关键词...
              </>
            ) : (
              'AI 澄清 VOC →'
            )}
          </button>
        </div>
      )}

      {/* VOC Scout 阶段：AI 探索技术全景 */}
      {phase === 'scout' && (
        <ScoutStep
          lang={lang}
          voc={voc}
          onOutput={(output: ScoutOutputResponse) => {
            setScoutOutput(output)
            setPhase('deepsearch')
          }}
          onRound1Data={(data) => {
            if (data.market_share) setMarketShare(data.market_share)
          }}
          onSkip={() => {
            // 跳过 Scout，直接进入关键词生成
            setPhase('keywords')
            setTimeout(() => handleAnalyze(), 0)
          }}
        />
      )}

      {/* VOC 澄清阶段：回答选择题 */}
      {phase === 'clarify' && (
        <div className="clarify-panel">
          <div className="clarify-header">
            <h2 className="clarify-title">AI 发现以下信息需要明确</h2>
            {clarifyAnalysis && (
              <p className="clarify-analysis">{clarifyAnalysis}</p>
            )}
            <div className="clarify-original-voc">
              <span className="clarify-label">原始 VOC：</span>
              {voc}
            </div>
          </div>

          <div className="clarify-questions">
            {clarifyQuestions.map((q, qi) => (
              <div key={q.id} className="clarify-question-card">
                <div className="clarify-question-title">
                  {qi + 1}. {q.question}
                </div>
                <div className="clarify-options">
                  {q.options.map((opt) => (
                    <label key={opt} className="clarify-option">
                      <input
                        type="radio"
                        name={q.id}
                        checked={clarifyAnswers[q.id] === opt}
                        onChange={() => selectAnswer(q.id, opt)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                  {q.allow_custom && (
                    <label className="clarify-option">
                      <input
                        type="radio"
                        name={q.id}
                        checked={clarifyAnswers[q.id]?.startsWith('custom:') || false}
                        onChange={() => setCustomAnswer(q.id, '')}
                      />
                      <span>以上都不是</span>
                    </label>
                  )}
                  {q.allow_custom && clarifyAnswers[q.id]?.startsWith('custom:') && (
                    <input
                      type="text"
                      className="clarify-custom-input"
                      placeholder="请输入您的答案..."
                      value={clarifyAnswers[q.id].replace(/^custom:/, '')}
                      onChange={(e) => setCustomAnswer(q.id, e.target.value)}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {error && <div className="error-banner">{error}</div>}

          <div className="clarify-actions">
            <button
              className="ghost-btn"
              onClick={() => { setPhase('input') }}
              type="button"
            >
              ← 返回修改 VOC
            </button>
            <button
              className="ghost-btn"
              onClick={() => { handleAnalyze() }}
              type="button"
            >
              跳过澄清，直接生成关键词
            </button>
            <button
              className="primary-btn"
              onClick={handleEnrich}
              disabled={enriching}
            >
              {enriching ? (
                <>
                  <span className="spinner" /> 生成增强 VOC...
                </>
              ) : (
                '提交答案，生成增强 VOC →'
              )}
            </button>
          </div>
        </div>
      )}

      {/* 增强 VOC 确认阶段 */}
      {phase === 'enriched' && (
        <div className="enriched-panel">
          <div className="enriched-header">
            <h2 className="enriched-title">增强版 VOC</h2>
            <p className="enriched-hint">
              以下是根据您的回答补充完善的 VOC，可编辑后确认。
            </p>
          </div>

          {enrichChanges.length > 0 && (
            <div className="enrich-changes">
              <div className="enrich-changes-title">本次补充/修正：</div>
              <ul>
                {enrichChanges.map((c, i) => (
                  <li key={i}>✓ {c}</li>
                ))}
              </ul>
            </div>
          )}

          <textarea
            className="voc-input enriched-voc-input"
            value={enrichedVoc}
            onChange={(e) => setEnrichedVoc(e.target.value)}
            rows={10}
          />

          <div className="enriched-actions">
            <button className="ghost-btn" onClick={backToClarify} type="button">
              ← 返回修改答案
            </button>
            <button
              className="primary-btn"
              onClick={confirmEnriched}
              disabled={analyzing}
            >
              {analyzing ? (
                <>
                  <span className="spinner" /> AI 生成检索关键词...
                </>
              ) : (
                '确认，生成检索关键词 →'
              )}
            </button>
          </div>
        </div>
      )}

      {/* VOC 探索阶段 */}
      {phase === 'explore' && (
        <ExploreStep
          lang={lang}
          onSelect={(selectedVoc: string) => {
            setVoc(selectedVoc)
            setPhase('input')
          }}
          onBack={() => setPhase('input')}
        />
      )}

      {/* Deep Search 阶段：三轮迭代专利挖掘 */}
      {phase === 'deepsearch' && (
        <div className="deepsearch-panel">
          <div className="deepsearch-header">
            <h2 className="deepsearch-title">{T.deepSearchTitle[lang]}</h2>
            <p className="deepsearch-sub">{T.deepSearchSub[lang]}</p>
          </div>

          {/* 加载中 */}
          {dsLoading && (
            <div className="deepsearch-loading">
              <span className="spinner" /> {T.deepSearchSearching[lang]}
            </div>
          )}

          {/* Deep Search 结果 */}
          {dsResult && !dsLoading && (
            <div className="deepsearch-results">
              <div className="ds-result-card">
                <span className="ds-label">{T.deepSearchSearchPath[lang]}:</span>
                <span className="ds-value">{dsResult.search_path}</span>
              </div>

              <div className="ds-stats-row">
                <div className="ds-stat">
                  <span className="ds-stat-num">{dsResult.total_companies_found}</span>
                  <span className="ds-stat-label">{T.deepSearchCompaniesFound[lang]}</span>
                </div>
                <div className="ds-stat">
                  <span className="ds-stat-num">{dsResult.total_found}</span>
                  <span className="ds-stat-label">{T.deepSearchPatentsFound[lang]}</span>
                </div>
                <div className="ds-stat ds-stat-cap">
                  <span className="ds-stat-num">{dsResult.capped_to}</span>
                  <span className="ds-stat-label">{T.deepSearchCappedTo[lang]}</span>
                </div>
              </div>

              <div className="ds-convergence">
                {dsResult.converged ? (
                  <span className="ds-converged-yes">{T.deepSearchConverged[lang]}</span>
                ) : (
                  <span className="ds-converged-no">{T.deepSearchNotConverged[lang]}</span>
                )}
              </div>

              {dsResult.cap_note && (
                <p className="ds-cap-note">📊 {dsResult.cap_note}</p>
              )}

              {/* Map-Reduce 按钮（无手动数量选择！） */}
              <div className="ds-mr-section">
                {!mrLoading && !mrResult && (
                  <button
                    className="primary-btn"
                    onClick={runMapReduce}
                    disabled={!dsResult.patent_numbers?.length}
                    type="button"
                  >
                    {T.deepSearchBtnMR[lang]}
                  </button>
                )}

                {mrLoading && (
                  <div className="deepsearch-loading">
                    <span className="spinner" />
                    {mrProgress
                      ? (lang === 'zh'
                          ? `正在处理第 ${mrProgress.completed}/${mrProgress.total} 篇专利...`
                          : `Processing patent ${mrProgress.completed} of ${mrProgress.total}...`)
                      : T.deepSearchMRProgress[lang]}
                  </div>
                )}

                {mrResult && !mrLoading && (
                  <div className="mr-results">
                    <h3 className="mr-done-title">✅ {T.deepSearchMRDone[lang]}</h3>

                    {mrResult.stats && (
                      <div className="mr-stats">
                        <span>请求: {mrResult.stats.total_requested} 篇</span>
                        <span>抓取成功: {mrResult.stats.fetch_ok} 篇</span>
                        <span>提取 CTQ: {mrResult.stats.ctq_extracted} 篇</span>
                        <span className="mr-rate">{mrResult.stats.fetch_success_rate}</span>
                      </div>
                    )}

                    {mrResult.ctq_comparison_table?.length > 0 && (
                      <div className="mr-ctq-table-wrap">
                        <table className="mr-ctq-table">
                          <thead>
                            <tr>
                              <th>Company</th>
                              <th>CTQ Parameter</th>
                              <th>Value</th>
                            </tr>
                          </thead>
                          <tbody>
                            {mrResult.ctq_comparison_table.slice(0, 20).map((row: Record<string, unknown>, ri: number) => (
                              <tr key={ri}>
                                <td>{String(row.assignee || row.name || '-')}</td>
                                <td>{String(row.parameter || row.ctq_name || '-')}</td>
                                <td>{String(row.value || '-')}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}

                    {mrResult.error && (
                      <div className="error-banner">{mrResult.error}</div>
                    )}
                  </div>
                )}
              </div>

              {/* 生成报告按钮（用 Deep Search 数据） */}
              {onDeepSearchReport && (
                <div className="ds-report-section">
                  <button
                    className="primary-btn"
                    onClick={handleDeepSearchReport}
                    type="button"
                  >
                    📊 基于全景分析生成 R&D 报告 →
                  </button>
                  <p className="ds-report-hint">
                    报告将包含市场份额排名、CTQ 对比表、技术路线全景、FTO 风险评估和已知局限。
                  </p>
                </div>
              )}

              {/* 也可跳到旧的专利检索流程 */}
              <div className="ds-alt-actions">
                <button
                  className="ghost-btn"
                  onClick={() => {
                    setPhase('keywords')
                    setTimeout(() => handleAnalyze(), 0)
                  }}
                  type="button"
                >
                  {T.deepSearchBtnSkip[lang]}
                </button>
                <button
                  className="ghost-btn"
                  onClick={() => {
                    dsStartedRef.current = false
                    setDsResult(null)
                    setMrResult(null)
                    setPhase('scout')
                  }}
                  type="button"
                >
                  {T.deepSearchBtnBack[lang]}
                </button>
              </div>
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}
        </div>
      )}

      {/* 关键词确认/修改阶段 */}
      {phase === 'keywords' && (
        <div className="keywords-confirm">
          <div className="keywords-confirm-header">
            <h2 className="keywords-confirm-title">
              AI 生成的 {strategies.length} 条检索策略
            </h2>
            <p className="keywords-confirm-hint">
              可直接修改下方英文关键词、删除不需要的角度、或添加自定义策略，确认后开始检索。
            </p>
          </div>

          <div className="strategy-edit-list">
            {strategies.map((s, i) => (
              <div key={i} className="strategy-edit-card">
                <div className="strategy-edit-head">
                  <span className="strategy-edit-angle">{i + 1}. {s.angle}</span>
                  <button
                    className="strategy-remove-btn"
                    onClick={() => removeStrategy(i)}
                    type="button"
                    title="删除此策略"
                  >
                    ✕
                  </button>
                </div>
                <input
                  className="strategy-edit-input"
                  value={s.query}
                  onChange={(e) => updateStrategyQuery(i, e.target.value)}
                  placeholder="英文检索关键词，如 acrylic adhesive electrolyte battery"
                />
                {s.rationale && <div className="strategy-edit-rationale">{s.rationale}</div>}
              </div>
            ))}
          </div>

          <button className="ghost-btn" onClick={addStrategy} type="button">
            + 添加自定义策略
          </button>

          <div className="patent-num-selector">
            <label className="form-label">
              <span className="label-tag">数量</span>
              检索专利数量
            </label>
            <div className="num-select-group">
              {([20, 30, 40, 50] as const).map((n) => (
                <button
                  key={n}
                  type="button"
                  className={`num-chip ${patentNum === n ? 'active' : ''}`}
                  onClick={() => setPatentNum(n)}
                >
                  {n} 篇
                </button>
              ))}
            </div>
            <div className="num-hint">
              更多专利 = 更广的覆盖范围，但检索时间略长；默认 20 篇已足够大多数场景
            </div>
          </div>

          {error && <div className="error-banner">{error}</div>}

          <div className="keywords-confirm-actions">
            <button className="ghost-btn" onClick={reAnalyze} type="button">
              ← 重新生成
            </button>
            <button
              className="primary-btn"
              onClick={handleSearch}
              disabled={searching}
            >
              {searching ? (
                <>
                  <span className="spinner" /> 检索专利中...
                </>
              ) : (
                '确认并检索专利 →'
              )}
            </button>
          </div>
        </div>
      )}

      {phase === 'input' && error && <div className="error-banner">{error}</div>}
    </div>
  )
}
