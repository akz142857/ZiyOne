export interface ResearchDirection {
  title: string;
  summary: string;
}

export const research: ResearchDirection[] = [
  { title: 'Autonomous agents', summary: '长时任务、工具使用、自主规划与执行。' },
  { title: 'Agent economy', summary: 'Agent-to-agent 商业化与可售卖的 AI 产品。' },
  { title: 'AI-native education', summary: '个性化辅导、英语学习、儿童启蒙。' },
  { title: 'Personal knowledge base', summary: '个人记忆系统与长期上下文。' },
  { title: 'AI creative tooling', summary: '写作、绘本、内容生成的创作工具。' },
];
