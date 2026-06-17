# ZiyOne Personal Homepage Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 把 `akz142857/ZiyOne` 建成用户个人主页，而不是单一作品仓库；绘本等作品放入独立作品目录。

**Architecture:** 推荐使用 Vue 3 + Bun + Vite 构建个人主页，内容数据化管理。根路径 `/` 是个人主页；作品、学习、研究、关注内容分别由路由或内容集合承载；绘本页面迁移到 `/works/english-picture-book/`。

**Tech Stack:** Bun, Vue 3, Vite, TypeScript, Vue Router, Markdown/JSON 内容数据, GitHub Pages.

---

## 1. 信息架构

### 顶级导航

```text
/              首页 Home
/about         个人信息 About
/works         个人作品 Works
/learning      学习 Learning
/research      AI 研究方向 AI Research
/watchlist     AI 关注 AI Watchlist
/contact       联系 Contact
```

### 作品目录

```text
/works/english-picture-book/   Tomi's English Time Book 英语启蒙绘本
/works/claycosmos/             claycosmos.ai 相关作品
/works/polymarket-agent/       Polymarket / Agent 产品实验
/works/tools/                  小工具、自动化、网页实验
```

### 内容分层

```text
src/content/profile.ts        # 个人身份、简介、链接
src/content/works.ts          # 作品列表
src/content/learning.ts       # 学习计划、英语、编程、AI
src/content/research.ts       # AI 研究方向
src/content/watchlist.ts      # AI 关注的人、公司、项目、论文、工具
src/content/timeline.ts       # 个人时间线 / 更新记录
```

---

## 2. 推荐仓库结构

```text
ZiyOne/
├── README.md
├── index.html                         # Vite 入口，不再放绘本内容
├── package.json
├── bun.lockb
├── vite.config.ts
├── tsconfig.json
├── public/
│   ├── favicon.svg
│   └── works/
│       └── english-picture-book/       # 静态作品归档；也可保留现在的 HTML
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router.ts
│   ├── styles/
│   │   ├── tokens.css
│   │   └── global.css
│   ├── content/
│   │   ├── profile.ts
│   │   ├── works.ts
│   │   ├── learning.ts
│   │   ├── research.ts
│   │   └── watchlist.ts
│   ├── components/
│   │   ├── SiteHeader.vue
│   │   ├── SiteFooter.vue
│   │   ├── HeroIntro.vue
│   │   ├── WorkCard.vue
│   │   ├── ResearchCard.vue
│   │   └── TagPill.vue
│   └── pages/
│       ├── Home.vue
│       ├── About.vue
│       ├── Works.vue
│       ├── WorkDetail.vue
│       ├── Learning.vue
│       ├── Research.vue
│       ├── Watchlist.vue
│       └── Contact.vue
├── docs/
│   └── plans/
└── works/
    └── english-picture-book/           # 当前先保留的静态 HTML 源文件
```

---

## 3. 首页内容规划

### Hero

目标：一句话说清楚“你是谁 + 你在做什么”。

建议文案：

```text
ZiyOne
Builder of AI-native learning, creative tools, and agent products.

我关注 AI Agent、个人知识系统、英语学习、创作工具与可售卖的 AI 产品。
```

### 首页模块顺序

1. **个人定位**
   - AI 产品实践者
   - Agent / 自动化 / 知识系统探索者
   - claycosmos.ai 推进者

2. **精选作品 Featured Works**
   - Tomi's English Time Book
   - claycosmos.ai
   - Polymarket Agent / 市场信息产品
   - 其他小工具

3. **学习 Learning**
   - English learning
   - AI engineering
   - Product building
   - Design / storytelling

4. **AI Research Directions**
   - Autonomous agents
   - Agent economy / agent-to-agent commerce
   - AI-native education
   - Personal knowledge base
   - AI creative tooling

5. **AI Watchlist**
   - 关注项目：OpenAI, Anthropic, Nous Research, Hugging Face 等
   - 关注方向：multimodal agents, coding agents, inference infra, AI browsers
   - 关注来源：GitHub Trending, HN, YC, arXiv, emergentmind

6. **Now / 最近在做**
   - 推进 claycosmos.ai
   - 搭建个人主页
   - 制作英语启蒙绘本
   - 研究 Agent 商业化

---

## 4. 绘本放置规则

绘本不能放根目录。当前迁移路径：

```text
works/english-picture-book/index.html
```

未来 Vue 站点中通过作品卡片链接到：

```text
/works/english-picture-book/
```

如果使用 Vite 构建，建议把静态绘本拷贝到：

```text
public/works/english-picture-book/index.html
```

这样部署后访问路径稳定为：

```text
https://akz142857.github.io/ZiyOne/works/english-picture-book/
```

---

## 5. 视觉方向

### 推荐风格

```text
AI-native personal lab
不是传统简历，不是普通博客，而是一个个人实验室 / 作品操作台。
```

### 设计关键词

- clean but warm
- editorial + technical
- high contrast typography
- cards for works
- timeline for learning/research
- dark/light friendly
- bilingual capable: 中文为主，英文作为身份和项目标题补充

### 色彩建议

```text
Ink: #0f172a
Surface: #f8fafc
Card: #ffffff
Muted: #64748b
Accent: #2563eb 或 #7c3aed
AI Glow: very subtle cyan/violet gradients only for hero
```

---

## 6. 实施任务

### Task 1: 清理根目录内容

**Objective:** 根目录只保留个人主页入口，不直接承载绘本。

**Files:**
- Move: `index.html` → `works/english-picture-book/index.html`
- Create: `index.html` temporary homepage placeholder
- Modify: `README.md`

**Verification:**

```bash
git status --short
# Expected: index.html changed, works/english-picture-book/index.html exists
```

### Task 2: 初始化 Vue 3 + Bun + Vite

**Objective:** 建立现代前端项目结构。

**Commands:**

```bash
bun create vite . --template vue-ts
bun install
bun run build
```

**Important:** 如果目录非空，手动创建配置文件，不覆盖 `works/` 和 `docs/`。

### Task 3: 建立内容数据层

**Objective:** 把个人信息、作品、学习、AI 研究方向数据化。

**Files:**
- Create: `src/content/profile.ts`
- Create: `src/content/works.ts`
- Create: `src/content/learning.ts`
- Create: `src/content/research.ts`
- Create: `src/content/watchlist.ts`

### Task 4: 建立路由和页面

**Objective:** 创建 `/`, `/about`, `/works`, `/learning`, `/research`, `/watchlist`, `/contact` 页面。

**Files:**
- Create: `src/router.ts`
- Create: `src/pages/*.vue`
- Modify: `src/main.ts`

### Task 5: 首页设计实现

**Objective:** 实现首页：Hero、精选作品、学习、AI 研究、关注列表、Now。

**Files:**
- Create: `src/components/HeroIntro.vue`
- Create: `src/components/WorkCard.vue`
- Modify: `src/pages/Home.vue`

### Task 6: 作品系统

**Objective:** 作品列表页展示所有作品，并链接到绘本静态页面。

**Files:**
- Modify: `src/content/works.ts`
- Modify: `src/pages/Works.vue`
- Copy: `works/english-picture-book/` → `public/works/english-picture-book/`

### Task 7: GitHub Pages 部署

**Objective:** 使用 GitHub Actions 自动构建部署。

**Files:**
- Create: `.github/workflows/deploy.yml`

**Build command:**

```bash
bun install --frozen-lockfile
bun run build
```

**Deploy output:**

```text
dist/
```

### Task 8: 验证

**Objective:** 确认本地和远端路径都可用。

**Commands:**

```bash
bun run build
bun run preview
```

检查：

```text
/                              # 个人主页
/works                         # 作品列表
/works/english-picture-book/    # 绘本页面
```

---

## 7. 内容草案

### 个人信息

```ts
export const profile = {
  name: 'ZiyOne',
  title: 'AI-native builder / product explorer',
  intro: '我关注 AI Agent、个人知识系统、英语学习、创作工具与可售卖的 AI 产品。',
  email: 'tomi@claycosmos.ai',
  links: [
    { label: 'GitHub', href: 'https://github.com/akz142857' },
    { label: 'ClayCosmos', href: 'https://claycosmos.ai' }
  ]
}
```

### 作品

```ts
export const works = [
  {
    title: "Tomi's English Time Book",
    type: 'Learning / Picture Book',
    description: '从数字、时间、星期、月份开始的英语启蒙绘本。',
    href: '/works/english-picture-book/'
  },
  {
    title: 'ClayCosmos',
    type: 'AI Product',
    description: 'AI-native creative and product experiments.',
    href: 'https://claycosmos.ai'
  }
]
```

---

## 8. 决策建议

推荐路线：

```text
先提交结构修正 → 再用 Vue3 + Bun 重构 → 再开 GitHub Pages 自动部署
```

原因：

1. 立即解决“绘本不该在根目录”的问题。
2. Vue3 + Bun 适合后续长期扩展。
3. 内容数据化后，作品、学习、AI 关注列表都可以持续追加。
4. GitHub Pages 可以自动发布，不需要手动传 HTML。
