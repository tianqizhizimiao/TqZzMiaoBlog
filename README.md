# TqZzMiaoのBlog — 项目文档

当前版本：**v0.5**（固定暗色主题，无主题切换）。

博客架构：**加载态（欢迎页 + 初始化栅栏）** → **业务态（`main.html` 主干）** 叠加在**背景层**之上。
核心是 `init_complete` 初始化栅栏：等所有初始化任务全部完成，才淡出加载态、显示业务主干。

---

## 目录结构

```
BLOG/
├─ app.py                    # Flask 开发服务器（静态路由 + 限速 + 延迟 + 禁缓存）
├─ public/                   # 静态页面根
│  ├─ index.html             # 主页面（加载态 + 初始化流程）
│  ├─ content/               # 业务数据根：每层一个 config.txt 描述该层菜单项
│  │  ├─ config.txt          # 根目录项（f/d/m 前缀）
│  │  └─ 各子文件夹/…        # 各自一个 config.txt
│  ├─ css/
│  │  ├─ global.css          # 全局样式 + 固定暗色主题变量（所有颜色集中定义）
│  │  ├─ index.css           # 首页专属（背景分层 + 磨砂 + 标题 + 加载指示器）
│  │  └─ main.css            # 业务主干 main.html 的样式（菜单/内容/跑马灯/代码块）
│  ├─ html/
│  │  └─ main.html           # 业务主干页面（fetch 注入显示）
│  ├─ images/                # 背景图（PC / 移动端两套）
│  ├─ fonts/                 # 自托管字体（Space Grotesk）
│  └─ javascripts/
│     ├─ index.js            # 首页揭幕：背景图/字体加载完 → .loaded
│     ├─ init.js             # init_complete 栅栏（register/complete + 保底 + 监控）
│     ├─ init_main.js        # 注入业务主干：fetch main.html → 容器
│     ├─ main.js             # main.html 页面逻辑（菜单渲染/内容/复制/跑马灯/面包屑）
│     └─ lib/                # 第三方库（markdown-it + highlight.js 语法高亮）
└─ README.md                 # 本文档
```

> 说明：`content/` 目录当前为空。它由每层一个 `config.txt` 驱动，需按下方规则填充后页面才有菜单与内容。

---

# 一、index.html（主页面 / 加载态）

首页是整套流程的入口：背景层渲染 → 初始化流程 → 显示业务主干。

## 内联 JS
- **`.boot-bg` 主题渐入**：系统**黑** → 直接黑（不闪）；系统**白** → 初始白，0.5s 后渐变到黑。加载完淡出（`.done`）。
- **15s 超时**：用户停留 >15s，把加载指示器文案换成"TqZzMiaoの土豆可能熟了"。

## 外部引入 JS（按加载顺序）
| 顺序 | 文件 | 作用 |
|------|------|------|
| 1 | `javascripts/index.js` | 背景揭幕：等背景图 + 字体加载完 → 加 `.loaded` |
| 2 | `javascripts/init.js` | 初始化栅栏：init_complete 工具 + 保底 + 监控 |
| 3 | `javascripts/init_main.js` | 注入 main.html 到容器 + 补 css/js 引用 |

---

# 二、javascripts/index.js（首页揭幕）

等背景图和字体加载完成 → 揭幕（`html.loaded`）。

- 按初始屏幕比例选背景图（竖屏 Mobile / 横屏 PC），内联固定到 body（不随 resize 切）。
- `new Image()` 预加载背景图，onload 触发揭幕 + 调 `init.startInit(3000)`（3 秒保底从图片加载完成起算）。
- `document.fonts.ready` 等字体；两者 done → `root.classList.add('loaded')`。

---

# 三、javascripts/init.js（初始化栅栏）

管理 `init_complete` 清单，等所有任务完成后淡出加载态、显示业务主干。

## 对外接口
| 方法 | 说明 |
|------|------|
| `init.register(key)` | 把 `init_complete[key] = false`（任务登记为未完成） |
| `init.complete(key)` | 把 `init_complete[key] = true`（任务完成） |
| `init.isAllDone()` | 清单非空且所有值为 true |
| `init.startInit(ms)` | 从调用时刻起 ms 后完成 `'init'` 保底任务 |

- 注册 `'init'` 占位保底任务；完成由 `index.js` 图片加载后 `startInit(3000)` 触发。
- 监控循环（200ms）检查 `isAllDone()` → 淡出 `.page/.loader`，显示 `#main-container`。

---

# 四、javascripts/init_main.js（业务主干注入）

fetch `main.html` → 注入外层隐藏容器。

- `init.register('main')`。
- 创建 `<div id="main-container">`（fixed 全屏、透明）。
- fetch `html/main.html` → DOMParser 解析 → 补 `<head>` 的 css/js `<link>`/`<script src>` 到外层（路径 `../`→`./`）→ 注入 `<body>` 内容 → `init.complete('main')`。
- 失败兜底也 `complete('main')`。

---

# 五、html/main.html（业务主干）

顶部菜单栏 + 内容区 + 移动端侧边抽屉。背景透明，透出下层背景图/磨砂。

- 顶栏 `.topbar`：左上角标题 + 面包屑（可点击开完整菜单）；右上角 `.nav`（根目录项）。
- 内容区 `#content-area`：预渲染的 `.content-view`（默认隐藏，点菜单切换显示）。
  - 内含 `#content-loading` 加载动画 + `#content-frame` 透明 iframe（`.html` 内容内嵌用）。
- 侧边抽屉 `#drawer`：完整树菜单（移动端汉堡 / 左上角标题打开）。
- 独立资源引用：`<link ../css/main.css>`、`<script src ../javascripts/main.js>`、以及 `lib/` 下的 markdown-it / highlight.js / highlight-theme.css。

---

# 六、javascripts/main.js（业务主干逻辑）

## 数据来源：config.txt（f/d/m 前缀）
每层一个 `config.txt`，一行一项：`前缀 名称`
```
f 测试文章.md     → 文件（点击加载内容）
d 子文件夹        → 文件夹（展开的分组，递归读它的 config.txt）
m 首页.md         → 主页面文件（既是菜单项，也是该层默认加载页）
```
仅 `main.js` 读取 config.txt（初始化递归预加载，同层并行），别处无依赖。

## 职责划分
- **扫描**：`preloadAll` 递归预加载所有 config.txt → `menuCache`（含文件/文件夹/主页面）。**只做索引探测，不预渲染内容**。
- **内容**：**懒加载**——`showContent(path)` 用户选中时才 fetch 该文件。内容区默认只显示居中的**加载动画**（`.content-loading`/`.loading-spinner`），加载完成隐藏动画、显示内容。
- **Markdown 渲染**：`.md/.txt` 用 **markdown-it** 渲染；`.html` 进透明 iframe；若 markdown-it 不可用退回纯文本。
- **代码高亮**：渲染后用 **highlight.js** 对 `<pre><code>` 高亮（配合 `highlight-theme.css`）。
- **代码复制按钮**：每个代码块右上角「复制」按钮，`navigator.clipboard` 优先、`execCommand` 兜底，点击后文字变「已复制」。
- **菜单**：`renderTree` 递归渲染（文件夹分组 + 文件项）；`buildNav` 渲染右上角根目录项。
- **交互**：JS 自动绑定文件夹 head 展开/收起（箭头内联控制）；跑马灯；面包屑；高亮；菜单标题栏按钮（关闭）。

## 关键点
- **展开/收起**：JS 直接绑定每个文件夹 head（闭包持有自己 group），`maxHeight` 展开/收起，箭头 `rotate` 内联同步。收起时 `collapseGroup` 递归折叠所有子文件夹 + 转回箭头。
- **追踪定位**：`applyCurrentState` 用 `.locating` 类临时禁用过渡 → 布局到最终态 → `getBoundingClientRect` 精确计算 → 让当前选中项在 `#menu-tree` 垂直居中。
- **跑马灯**：超长菜单项 `.running` 时 0.5s 延迟滚动（双副本 16 硬空格间隔，父文件夹收起时复位）。
- **面包屑**：左上角路径（同行，超 80 字符隐藏中间层）。
- **右上角 nav 高亮**：`highlightNav` 按当前路径首段高亮对应项。
- **未设置初始页面**：根目录 `config.txt` 无 `m` 主页面时，显示居中提示。

---

# 七、css/main.css（业务主干样式）

- 顶栏/面包屑/菜单树（简约文本，层级靠缩进引导线）。
- 文件夹分组展开/收起（CSS transition；`.locating` 定位时禁用）。
- 超长菜单项/文件夹标题不换行、可横滚（隐藏滑块）；超长跑马灯。
- 菜单标题栏：仅图标（`✕ 关闭`）、简约。
- **内容区**：文档流、背景透明、`overflow-y: auto` 允许滚动；`.content-loading` 居中加载动画。
- **滚动条**：轨道透明、滑块深灰圆角方块（`--scrollbar-thumb`）。
- **代码块**：不透明深灰背景（`--code-block-bg`）+ 白色粗边框（`--code-block-border`）；代码可选中复制；右上角复制按钮（`.copy-btn`）。

---

# 八、css/global.css（全局变量）

- **固定暗色主题变量**：`--bg`、`--text`、`--muted`、`--border`、`--accent`、`--surface`、`--ctrl-gray`、`--code-bg`、`--code-text`、`--frost`、`--shadow`、`--hero-shadow` 等。
- **组件色（集中管理，其它文件不再写死颜色）**：`--scrollbar-thumb`、`--code-block-bg`、`--code-block-border`、`--btn-text`、`--btn-text-hover`、`--btn-border`、`--topbar-border`、`--headbar-border`、`--divider`、`--item-active-bg`、`--overlay`、`--drawer-shadow-1`、`--drawer-shadow-2`。
- 字体变量：`--font-sans`、`--font-mono`、`--font-display`（Space Grotesk）。
- `main.css` 中一律用 `var(--xx)` 引用，不写死颜色。

---

# 九、css/index.css（首页专属）

- 分层背景：body 直接放背景图（最稳）→ 层2 `.bg-blur` 磨砂 → 层3 `.bg-tint` 主题罩。
- `html.loaded` 后主题罩渐变成半透明（`--frost`），露出背景。
- 标题 `.hero-title` 初始隐藏，加载完成后淡入。
- 加载指示器 `.loader`（横屏右下角，Windows 11 风格旋转圆点；竖屏居中）。
- `@media (max-aspect-ratio: 1/1)` 竖屏调整（标题居中、显示汉堡、隐藏面包屑）。

---

# 十、app.py（Flask 开发服务器）

静态路由 + 极端网络模拟。

| 项 | 值 | 环境变量可调 |
|----|----|-------------|
| 静态根目录 | `public/` | — |
| 限速 | 50 KB/s | `RATE_KBPS` |
| 延迟 | 500ms | `DELAY_MS` |
| 监听 | 0.0.0.0（局域网）| `HOST` |
| 缓存 | 禁用（no-store）| — |

- **ThrottleMiddleware**：限速响应字节流。**DelayMiddleware**：每请求先 sleep。
- **no_cache（after_request）**：no-store + 去 ETag/Last-Modified。
- **路由**：`/`→index.html；`/<path>` 按文件映射；目录补 index.html；未命中 404。

---

## 第三方库（public/javascripts/lib/）
- `markdown-it.min.js`：Markdown → HTML 渲染。
- `highlight.min.js`：代码语法高亮。
- `highlight-theme.css`：高亮配色主题（One Dark 风格）。

## 主题：固定暗色（无切换）
- 全局固定暗色（黑底白字/灰字），**不再允许切换主题**（无 theme.js、无空格/三连击/菜单切换）。
- 仅启动时：系统白 → `boot-bg` 初始白渐黑；系统黑 → 直接黑。

## 常见坑（编辑时注意）
1. **@media 切背景在 PC 拖窗口会误触发** → 已改为 JS 固定背景图（index.js）。
2. **fetch 只注入 `<body>`** → `<head>` 的 css/js 需 `init_main.js` 补到外层。
3. **`innerHTML` 注入 `<script>` 不执行** → main.js 用 `<script src>` 动态加载。
4. **展开/收起用 JS 内联控制**（maxHeight + 箭头 rotate），不用 CSS class 派生（避免嵌套误匹配）。
5. **config.txt 前缀 f/d/m** 决定文件/文件夹/主页面，扫描时不再探测（免 404）。
6. **内容懒加载**：只探 config.txt，用户选中才 fetch 内容 + 显示居中加载动画。
7. **追踪定位需禁用过渡**：`.locating` 类临时禁用 `#menu-tree` 的 transition，否则 `max-height` 中间态导致 rect 不准。
8. **不拦截浏览器 F5**：浏览器刷新无法被 JS 真正取消。
9. **代码块双重背景**：highlight.js 给 `code` 加 `.hljs` 自带背景 → 用 `.content-view pre code.hljs { background: transparent; }` 覆盖，透出 `pre` 单一底色。
10. **隐藏的 `.content-view` 不占文档流**：用 `display:none`（而非 `opacity:0`），避免"空一大片"。
