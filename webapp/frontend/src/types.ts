export interface Patent {
  patent_number: string
  title: string
  assignee: string
  snippet: string
  publication_date: string
  source: string
  url: string
  country: string
  detail_text?: string
}

export type Step = 'input' | 'patents' | 'report'

/** AI 从 VOC 拆解出的单个搜索角度 */
export interface SearchStrategy {
  angle: string      // 中文角度说明
  query: string      // 英文搜索关键词
  rationale: string  // 为什么从这角度搜
}

export interface SearchResponse {
  keywords: string
  strategies: SearchStrategy[]
  total: number
  patents: Patent[]
  warning?: string
}

/** /api/analyze-voc 的响应 */
export interface AnalyzeVocResponse {
  strategies: SearchStrategy[]
  fallback_keywords: string
  warning?: string
}
