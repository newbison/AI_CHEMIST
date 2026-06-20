import { useState } from 'react'
import type { Patent, SearchResponse, SearchStrategy, AnalyzeVocResponse } from '../types'

/** 材料科学领域 VOC 示例池（每次随机展示 10 个） */
const VOC_POOL: string[] = [
  '锂电池电芯终止胶带，要求在电解液（碳酸酯类，含 LiPF6）长期浸泡（85°C/72h 及以上）下保持粘接力不脱落、不溶胀、无残胶、不污染电解液；同时电气绝缘可靠，在高温和冷热循环下稳定工作；且便于产线手工/自动贴附、易撕定位、不起翘。',
  '医用钛合金植入物表面涂层，要求在体液环境下（37°C，pH 7.4）长期稳定（10 年以上）不降解、不释放金属离子；涂层需具备良好的生物相容性，促进骨整合；硬度 ≥ 5GPa，耐磨耐疲劳；表面粗糙度 Ra ≤ 0.5μm，适合精密加工。',
  '柔性 OLED 显示屏用透明导电薄膜，要求透光率 ≥ 88%（550nm），方阻 ≤ 50Ω/□；在 1000 次弯折（R=3mm）后电阻变化率 < 10%；耐高温 150°C/1000h 稳定；与 PET 基材附着力强，无分层；适合卷对卷量产工艺。',
  '氢燃料电池质子交换膜，要求在 80°C、100% RH 下质子电导率 ≥ 0.1 S/cm；气体渗透率 < 10⁻⁸ cm³/cm²·s·cmHg；厚度 10-20μm 且均匀；耐化学降解（Fenton 试剂测试 ≥ 100h）；机械强度 ≥ 30MPa，适合 MEA 热压装配。',
  '建筑用低辐射（Low-E）玻璃镀膜，要求辐射率 ≤ 0.08；可见光透射比 ≥ 60%；红外反射率 ≥ 85%；在户外曝晒 10 年后性能衰减 < 5%；耐酸碱清洗；适合大面积磁控溅射镀膜工艺，膜层均匀无色差。',
  '碳纤维增强环氧树脂复合材料（CFRP），要求拉伸强度 ≥ 1500MPa，模量 ≥ 120GPa；层间剪切强度 ≥ 80MPa；在湿热环境（70°C/85%RH/1000h）后强度保留率 ≥ 85%；Tg ≥ 180°C；适合预浸料热压罐成型，孔隙率 < 1%。',
  '半导体封装用环氧塑封料（EMC），要求 Tg ≥ 160°C；热膨胀系数 CTE ≤ 15ppm/°C；吸水率 < 0.3%（PCT 121°C/100%RH/96h）；阻燃 UL94 V-0；螺旋流动长度 80-120cm；成型后无气泡、无翘曲，适合高可靠性 IC 封装。',
  '钙钛矿太阳能电池吸光层，要求光电转换效率 ≥ 22%；在连续光照 1000h（AM1.5G, 1 sun）后效率保持率 ≥ 90%；带隙 1.5-1.6eV 可调；晶粒尺寸 ≥ 1μm，无针孔；耐湿度（RH 50% 环境稳定）；适合溶液法大面积涂布。',
  '高温合金涡轮叶片热障涂层（TBC），要求陶瓷层热导率 ≤ 1.5 W/m·K；抗热震性 ≥ 1000 次循环（1100°C↔室温）；与粘结层结合强度 ≥ 40MPa；表面粗糙度 Ra ≤ 6μm；耐高温氧化（1100°C/1000h）；适合 EB-PVD 或等离子喷涂工艺。',
  '锂离子电池硅碳复合负极材料，要求比容量 ≥ 800 mAh/g；首次库仑效率 ≥ 85%；循环 500 次（0.5C）容量保持率 ≥ 80%；体积膨胀率 < 30%；粒度 D50 = 8-12μm；适合水系匀浆涂布工艺，与现有石墨产线兼容。',
  '海水淡化用反渗透复合膜（RO），要求脱盐率 ≥ 99.5%；水通量 ≥ 40 L/m²·h（测试条件 1.5MPa, 2000ppm NaCl, 25°C）；耐氯性 ≥ 1000 ppm·h；耐 pH 2-12 清洗；使用寿命 ≥ 5 年；适合卷式膜元件生产。',
  '电磁屏蔽用导电硅橡胶，要求体积电阻率 ≤ 0.05 Ω·cm；屏蔽效能 ≥ 80dB（10MHz-10GHz）；硬度 60-80 Shore A；拉伸强度 ≥ 5MPa；耐老化 150°C/1000h；适合模压成型，尺寸精度 ±0.05mm；适合 5G 基站密封屏蔽。',
  '生物可降解聚乳酸（PLA）薄膜，要求在土壤中 6 个月内降解率 ≥ 90%；拉伸强度 ≥ 50MPa；透光率 ≥ 90%；氧气透过率 < 500 cm³/m²·24h；热封温度 80-120°C；适合吹膜工艺，厚度 20-50μm，用于食品包装。',
  '固态电池硫化物电解质，要求室温离子电导率 ≥ 10⁻³ S/cm；电子电导率 < 10⁻⁹ S/cm；电化学窗口 ≥ 5V（vs Li）；与金属锂界面稳定；可冷压成型，致密度 ≥ 95%；适合干法电极涂布工艺，厚度 20-50μm。',
  '航空航天用耐高温胶粘剂，要求工作温度 -55°C 至 230°C；剪切强度 ≥ 25MPa（室温）；在 200°C/1000h 后强度保留率 ≥ 70%；耐航空液压油、燃油；适合蜂窝结构粘接；固化温度 ≤ 180°C，固化时间 ≤ 2h。',
  '自修复聚合物涂层，要求在室温下划痕（宽度 < 100μm）48h 内愈合率 ≥ 90%；附着力 ≥ 5B（ASTM D3359）；耐盐雾 ≥ 1000h；透光率 ≥ 90%（若透明）；适合喷涂或刷涂，表干 ≤ 2h，实干 ≤ 24h；用于汽车面漆。',
  '压电陶瓷换能器材料（PZT），要求压电常数 d33 ≥ 500 pC/N；机电耦合系数 kp ≥ 0.65；介电常数 εr = 1500-3000；居里温度 Tc ≥ 300°C；机械品质因数 Qm = 50-200；适合烧结成型，密度 ≥ 7.8 g/cm³，用于医用超声探头。',
  '导热相变材料（PCM），要求热导率 ≥ 5 W/m·K；相变温度 55-65°C；潜热 ≥ 150 J/g；循环 1000 次后潜热衰减 < 5%；与芯片无腐蚀、无渗漏；适合丝网印刷或模压成型，厚度 0.1-0.5mm，用于电子器件散热。',
  '耐磨自润滑聚甲醛（POM）复合材料，要求摩擦系数 ≤ 0.2；磨损率 < 1×10⁻⁶ mm³/N·m；在 -40°C 至 100°C 范围稳定；拉伸强度 ≥ 60MPa；尺寸稳定性好（吸水率 < 0.2%）；适合注塑成型，用于精密齿轮和轴承。',
  '电致变色智能窗玻璃，要求着色/褪色时间 < 30s（25mm×25mm 样品）；着色态透射比 ≤ 10%，褪色态 ≥ 60%；循环寿命 ≥ 10000 次；驱动电压 ≤ 3V；耐紫外老化（1000h）性能衰减 < 5%；适合大面积（≥ 1m²）制备。',
  '海水钢管环氧防腐涂层，要求耐盐雾 ≥ 3000h 无起泡；附着力 ≥ 8MPa；耐阴极剥离（48V, 25°C, 30d）剥离半径 < 8mm；干膜厚度 300-500μm；耐磨损（Taber 1kg/1000r）失重 < 50mg；适合无气喷涂，表干 ≤ 4h。',
  '燃料电池气体扩散层（GDL）碳纸，要求孔隙率 70-80%；透气率 ≥ 1000 mL·mm/cm²·h·mmAq；厚度 100-200μm 且均匀；体积电阻率 ≤ 15 mΩ·cm；弯曲强度 ≥ 10MPa；适合辊压成型，表面经 PTFE 疏水处理。',
  '可拉伸电子用液态金属导电墨水，要求室温电导率 ≥ 3×10⁶ S/m；在 100% 拉伸应变下电阻变化 < 50%；与 PDMS/ Ecoflex 基材附着力强；粘度 10-100 mPa·s；适合丝网印刷或喷墨打印；无毒、无泄漏风险。',
  '核电站用耐辐射电缆绝缘材料，要求在 γ 射线累计剂量 ≥ 1000 MGy 后拉伸强度保留率 ≥ 60%；工作温度 -40°C 至 90°C；氧指数 ≥ 30%；耐 LOCA 环境（175°C 蒸汽/345kPa/30d）；适合挤出成型，绝缘厚度 0.5-2mm。',
  '医用可吸收止血海绵（氧化再生纤维素），要求在血液中 2-5 分钟内完全止血；28 天内体内完全吸收；pH 3.0-4.5（酸性抑菌）；无菌、无致热原；拉伸强度 ≥ 0.5MPa（干燥态）；适合冻干成型，孔径 50-200μm。',
  '锂金属电池人工固态电解质界面（SEI），要求锂离子电导率 ≥ 10⁻⁴ S/cm；电子绝缘；机械模量 ≥ 1GPa（抑制锂枝晶）；在锂金属界面稳定 ≥ 500 次循环；厚度 < 100nm 且均匀；适合原位或非原位制备工艺。',
  '高温压电单晶 PMN-PT，要求压电常数 d33 ≥ 1500 pC/N；机电耦合系数 k33 ≥ 0.90；居里温度 Tc ≥ 150°C；介电损耗 tan δ ≤ 0.01；尺寸 ≥ 5mm×5mm×5mm 单晶；适合布里奇曼法生长，用于医用超声和水声换能器。',
  '超疏水自清洁建筑外墙涂层，要求水接触角 ≥ 150°，滚动角 ≤ 5°；耐紫外老化 2000h 后性能保持率 ≥ 80%；附着力 ≥ 2B；耐沾污性 ≤ 10%（反射率下降）；适合喷涂施工，表干 ≤ 2h，使用寿命 ≥ 10 年。',
  '钠离子电池硬碳负极材料，要求可逆容量 ≥ 300 mAh/g；首次库仑效率 ≥ 85%；循环 1000 次（0.5C）容量保持率 ≥ 80%；平均储钠电位 ≤ 0.2V vs Na⁺/Na；粒度 D50 = 5-15μm；适合生物质前驱体碳化工艺，成本 < 5 万元/吨。',
  '医用导管用聚氨酯弹性体，要求硬度 70-90 Shore A；拉伸强度 ≥ 40MPa；断裂伸长率 ≥ 400%；耐血液相容性（溶血率 < 5%）；耐 γ 射线灭菌（25kGy）后性能稳定；适合挤出成型，壁厚 0.2-1mm，用于中心静脉导管。',
]

/** 从池中随机抽取 n 个不重复的 VOC */
function pickRandomVocs(pool: string[], n: number): string[] {
  const arr = [...pool]
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr.slice(0, Math.min(n, arr.length))
}

/** 截取 VOC 前 40 字作为卡片标题 */
function vocTitle(voc: string): string {
  const t = voc.length > 40 ? voc.slice(0, 40) + '...' : voc
  return t
}

export default function InputStep({
  voc,
  setVoc,
  onSearched,
}: {
  voc: string
  setVoc: (v: string) => void
  onSearched: (all: Patent[], selected: Patent[], strategies: SearchStrategy[]) => void
}) {
  // 阶段：'input' 输入VOC → 'keywords' AI生成关键词供确认 → 检索
  const [phase, setPhase] = useState<'input' | 'keywords'>('input')
  const [analyzing, setAnalyzing] = useState(false)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])
  const [patentNum, setPatentNum] = useState<number>(20)
  const [sampleVocs, setSampleVocs] = useState<string[]>(() => pickRandomVocs(VOC_POOL, 10))

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

  // 重新生成关键词
  function reAnalyze() {
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

  return (
    <div className="step-container">
      <div className="step-hero">
        <h1 className="hero-title">输入客户需求</h1>
        <p className="hero-sub">
          输入 VOC（Voice of Customer），AI 会先分析 VOC 拆解出多个技术角度并生成英文检索关键词，
          供您确认或修改后再联网检索专利，最终生成完整 R&D 智能报告。
        </p>
      </div>

      {/* VOC 示例池：随机 10 个材料科学场景 */}
      {phase === 'input' && (
        <div className="form-block">
          <label className="form-label">
            <span className="label-tag">示例</span>
            材料科学 VOC 示例（随机 10 个，点击试用）
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
            onClick={() => setSampleVocs(pickRandomVocs(VOC_POOL, 10))}
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
        <button
          className="primary-btn"
          onClick={handleAnalyze}
          disabled={analyzing}
        >
          {analyzing ? (
            <>
              <span className="spinner" /> AI 分析 VOC 生成检索关键词...
            </>
          ) : (
            'AI 生成检索关键词 →'
          )}
        </button>
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
