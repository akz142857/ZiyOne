export interface Work {
  title: string;
  type: string;
  description: string;
  href: string;
  /** External link opens in a new tab; internal links stay in-app. */
  external?: boolean;
  featured?: boolean;
}

export const works: Work[] = [
  {
    title: "Tomi's English Time Book",
    type: 'Learning / Picture Book',
    description: '从数字、时间、星期、月份开始的中英双语英语启蒙绘本。',
    href: 'works/english-picture-book/index.html',
    featured: true,
  },
  {
    title: 'ClayCosmos',
    type: 'AI Product',
    description: 'AI-native creative and product experiments.',
    href: 'https://claycosmos.ai',
    external: true,
    featured: true,
  },
];
