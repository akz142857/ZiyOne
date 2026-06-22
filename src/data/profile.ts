export interface SocialLink {
  label: string;
  href: string;
}

export interface Profile {
  name: string;
  tagline: string;
  intro: string;
  email: string;
  links: SocialLink[];
  now: string[];
}

export const profile: Profile = {
  name: 'ZiyOne',
  tagline: 'Builder of AI-native learning, creative tools, and agent products.',
  intro:
    '我关注 AI Agent、个人知识系统、英语学习、创作工具,以及可售卖的 AI 产品。这里是我的个人实验室与作品操作台。',
  email: 'tomi@claycosmos.ai',
  links: [
    { label: 'GitHub', href: 'https://github.com/akz142857' },
    { label: 'ClayCosmos', href: 'https://claycosmos.ai' },
    { label: 'Email', href: 'mailto:tomi@claycosmos.ai' },
  ],
  now: [
    '推进 claycosmos.ai',
    '搭建个人主页(就是这个站)',
    '制作 Tomi 英语启蒙绘本',
    '研究 Agent 商业化',
  ],
};
