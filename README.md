# TqZzMiaoのBlog — 项目文档

当前开发版本：**v0.2**（v0.1 完整备份在 `versions/v0.1/`）。

这套博客的架构：**加载态（欢迎页 + 初始化栅栏）** → **业务态（`main.html` 主干）** 叠加在**背景层**之上。
核心是 `init_complete` 初始化栅栏：等所有初始化任务全部完成，才淡出加载态、显示业务主干。

---

## 目录结构

```
BLOG/
├─ app.py                    # Flask 开发服务器（静态路由 + 限速 + 延迟 + 禁缓存）
├─ versions/v0.1/            # 旧版本完整备份（冻结）
├─ public/                   # 静态页面根（v0.2 活跃版）
│  ├─ index.html             # 主页面（加载态 + 初始化流程）
│  ├─ content/               # 业务数据根：每层一个 config.txt 描述该层菜单项
│  │  ├─ config.txt          # 根目录项（f/d/m 前缀）
│  │  └─ 各子文件夹/…        # 各自一个 config.txt
│  ├─ css/
│  │  ├─ global.css          # 全局样式 + 固定暗色主题变量
│  │  ├─ index.css           # 首页专属（背景分层 + 磨砂 + 标题 + 加载指示器）
│  │  └─ main.css            # 业务主干 main.html 的样式（菜单/内容/跑马灯）
│  ├─ html/
│  │  └─ main.html           # 业务主干页面（fetch 注入显示）
│  ├─ images/                # 背景图（PC / 移动端两套）
│  └─ javascripts/
│     ├─ index.js            # 首页揭幕：背景图/字体加载完 → .loaded
│     ├─ init.js             # init_complete 栅栏（register/complete + 保底 + 监控）
│     ├─ init_main.js        # 注入业务主干：fetch main.html → 容器
│     └─ main.js             # main.html 页面逻辑（菜单渲染/内容/跑马灯/面包屑）
└─ README.md                 # 本文档
```

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
- 侧边抽屉 `#drawer`：完整树菜单（移动端汉堡 / 左上角标题打开）。

独立资源引用：`<link ../css/main.css>`、`<script src ../javascripts/main.js>`。

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
- **菜单**：`renderTree` 递归渲染（文件夹分组 + 文件项）；`buildNav` 渲染右上角根目录项（文件+文件夹）。
- **交互**：JS 自动绑定文件夹 head 展开/收起（箭头内联控制）；跑马灯；面包屑；高亮；菜单标题栏按钮（关闭）。

## 关键点
- **展开/收起**：JS 直接绑定每个文件夹 head（闭包持有自己 group），`maxHeight` 展开/收起，箭头 `rotate` 内联同步。收起时 `collapseGroup` 递归折叠所有子文件夹 + 转回箭头。
- **追踪定位**：`applyCurrentState` 用 `.locating` 类临时禁用过渡 → 布局到最终态 → `getBoundingClientRect` 精确计算 → 让当前选中项在 `#menu-tree` 垂直居中（重开菜单时定位）。
- **跑马灯**：超长菜单项 `.running` 时 0.5s 延迟滚动（双副本 16 硬空格间隔，父文件夹收起时复位）。
- **面包屑**：左上角路径（同行，超 80 字符隐藏中间层）。
- **右上角 nav 高亮**：`highlightNav` 按当前路径首段高亮对应项（顶层文件→自身；深层→其顶层文件夹）。
- **菜单标题栏**：仅"菜单"标题 + 右侧 `✕` 关闭按钮（简约图标）。
- **config.txt 扫描**：同层文件夹并行（`Promise.all`），一个请求/层，无探测 404。

---

# 七、css/main.css（业务主干样式）

- 顶栏/面包屑/菜单树（简约文本，层级靠缩进引导线；子项名字比父文件夹靠后）。
- 文件夹分组展开/收起（CSS transition；`.locating` 定位时禁用）。
- 菜单项/文件夹标题超长不换行、可横滚（隐藏滑块）；超长跑马灯（双副本 16 空格间隔，`.running` 时滚动）。
- 菜单标题栏：仅图标（`✕ 关闭`）、简约。
- 内容区：文档流、背景透明、`overflow:hidden`（禁业务区滚动）；`.content-loading` 居中加载动画（`.loading-spinner` 转圈）。

---

# 八、app.py（Flask 开发服务器）

静态路由 + 极端网络模拟。

| 项 | 值 | 环境变量可调 |
|----|----|-------------|
| 静态根目录 | `public/` | — |
| 限速 | 50 KB/s | `RATE_KBPS` |
| 延迟 | 500ms | `DELAY_MS` |
| 监听 | 0.0.0.0（局域网）| `HOST` |
| 缓存 | 禁用（no-store）| — |

- **ThrottleMiddleware**：限速响应字节流。 **DelayMiddleware**：每请求先 sleep。
- **no_cache（after_request）**：no-store + 去 ETag/Last-Modified。
- **路由**：`/`→index.html；`/<path>` 按文件映射；目录补 index.html；未命中 404。

---

## 版本记录
- **v0.1**：初版（背景分层 + 主题 + 加载指示器 + 限速/延迟），备份于 `versions/v0.1/`。
- **v0.2**：`init_complete` 栅栏 + 业务主干 main.html（fetch 注入）+ 菜单由 config.txt 驱动（f/d/m）。

---

## 主题：固定暗色（无切换）
- 全局固定暗色（黑底白字/灰字），**不再允许切换主题**（无 theme.js、无空格/三连击/菜单切换）。
- 仅启动时：系统白 → `boot-bg` 初始白渐黑；系统黑 → 直接黑。

---

## 常见坑（编辑时注意）
1. **@media 切背景在 PC 拖窗口会误触发** → 已改为 JS 固定背景图（index.js）。
2. **fetch 只注入 `<body>`** → `<head>` 的 css/js 需 `init_main.js` 补到外层。
3. **`innerHTML` 注入 `<script>` 不执行** → main.js 用 `<script src>` 动态加载。
4. **展开/收起用 JS 内联控制**（maxHeight + 箭头 rotate），不用 CSS class 派生（避免嵌套误匹配）。
5. **config.txt 前缀 f/d/m** 决定文件/文件夹/主页面，扫描时不再探测（免 404）。
6. **内容懒加载**：只探 config.txt，用户选中才 fetch 内容 + 显示居中加载动画。深层文件不再预渲染（初始化快）。
7. **追踪定位需禁用过渡**：`.locating` 类临时禁用 `#menu-tree` 的 transition，否则 `max-height` 中间态导致 rect 不准、定位随机偏移/飞出屏幕。
8. **不拦截浏览器 F5**：浏览器刷新无法被 JS 真正取消（已还原为默认刷新）。
