# ZiyOne

ZiyOne 个人主页 —— AI-native builder 的个人实验室与作品操作台。

用 **Astro + Bun** 构建,部署在 GitHub Pages:
<https://akz142857.github.io/ZiyOne/>

## 开发

```bash
bun install        # 安装依赖
bun run dev        # 本地开发 http://localhost:4321/ZiyOne
bun run build      # 构建到 dist/
bun run preview    # 预览构建产物
bun run check      # 类型检查
```

## 结构

```text
src/
├── pages/        # 路由页面 (index.astro, works.astro)
├── layouts/      # BaseLayout
├── components/   # SiteHeader / SiteFooter / WorkCard
├── data/         # 内容数据 (profile, works, research, learning, watchlist)
├── lib/          # withBase() 等工具
└── styles/       # tokens.css + global.css
public/
└── works/english-picture-book/   # Tomi 英语启蒙绘本(静态作品,原样部署)
```

## 加内容

编辑 `src/data/*.ts` 即可增删作品、研究方向、关注项;新作品页放 `src/pages/`,静态作品放 `public/works/`。

## X 归档脚本

`scripts/` 下另有独立的 X/Twitter 公开推文归档与周报脚本,见 [`data/x/README.md`](data/x/README.md)。

## 规划

见 [`docs/plans/`](docs/plans/)。
