export interface WatchGroup {
  label: string;
  items: string[];
}

export const watchlist: WatchGroup[] = [
  {
    label: '关注项目',
    items: ['OpenAI', 'Anthropic', 'Nous Research', 'Hugging Face'],
  },
  {
    label: '关注方向',
    items: ['Multimodal agents', 'Coding agents', 'Inference infra', 'AI browsers'],
  },
  {
    label: '关注来源',
    items: ['GitHub Trending', 'Hacker News', 'YC', 'arXiv', 'emergentmind'],
  },
];
