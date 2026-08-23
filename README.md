# TqZzMiao の Blog

一个纯静态的个人博客，Markdown 渲染 + 代码高亮，移动端 / 桌面端自适应。配套一个用于性能调试的 Flask 限速服务器。

> 仓库地址：`git@github.com:tianqizhizimiao/TqZzMiaoBlog.git`

## 特性

- **纯静态站点**：整个博客就是 `public/` 文件夹，无需构建、无需后端，任何静态托管都能跑。
- **Markdown 渲染**：基于 `markdown-it`，文章直接写 `.md`，自动渲染成页面。
- **代码高亮**：基于 `highlight.js`，代码块自动高亮，右上角带"复制"按钮。
- **自动菜单**：菜单由 `content/` 里每层的 `config.txt` 驱动，`main.js` 自动扫描生成树形菜单（可展开/收起）。
- **响应式布局**：桌面端顶栏导航 + 右上角导航；移动端（竖屏）汉堡菜单 + 左侧滑出的侧边抽屉。
- **面包屑 + 跑马灯**：顶栏显示当前路径面包屑；过长的菜单项自动触发无缝跑马灯滚动。
- **多层背景与揭幕动画**：磨砂层、主题罩、背景图三层叠加，资源加载完成后平滑揭幕。
- **限速调试服务器**：`app.py` 可把响应限速 / 延迟，模拟真实网络加载环境。

## 目录结构

```
BLOG/
├── app.py                 # 本地调试用 Flask 服务器（限速/延迟，模拟真实网络）
├── README.md
└── public/                # 静态站点根目录（上线整体托管）
    ├── index.html         # 首页（加载页，负责揭幕动画）
    ├── css/
    │   ├── global.css     # 全局变量（主题色、字体、CSS 变量）与基础样式
    │   ├── index.css      # 首页专属样式（多层背景、加载动画、标题淡入）
    │   └── main.css       # 业务主干 main.html 的样式（菜单、内容区、抽屉）
    ├── fonts/
    │   └── SpaceGrotesk.ttf
    ├── html/
    │   └── main.html      # 业务主干（顶栏、内容区、移动端抽屉的骨架）
    ├── images/
    │   ├── background-PC.jpg    # 桌面端背景图
    │   └── background-Mobile.jpg# 移动端背景图
    ├── javascripts/
    │   ├── index.js       # 首页逻辑：选定背景图、等图片/字体加载完揭幕
    │   ├── init.js        # 初始化屏障：所有任务完成后淡出加载页
    │   ├── init_main.js   # 拉取并注入 main.html 到首页
    │   ├── main.js        # 业务逻辑：扫描 config.txt、生成菜单、渲染/切换内容
    │   └── lib/           # 第三方库
    │       ├── markdown-it.min.js  # Markdown 渲染
    │       ├── highlight.min.js    # 代码高亮
    │       └── highlight-theme.css # 代码高亮主题
    └── content/           # ✏️ 你的博客内容在这里（见下文"如何写内容"）
```

## 如何运行（本地调试）

### 方式一：直接用 Flask 服务器（推荐，可模拟限速）

需要 Python 3 + Flask：

```bash
pip install flask
python app.py
```

打开浏览器访问 <http://127.0.0.1:5000>。

默认参数：

- 监听 `0.0.0.0:5000`（局域网可访问）
- 每个请求延迟 `500ms`（`DELAY_MS`）
- 限速 `50 KB/s`（`RATE_KBPS`）
- 禁用浏览器缓存（每次刷新完整走一遍加载）

可用环境变量覆盖：

| 变量         | 作用               | 默认值      |
| ------------ | ------------------ | ----------- |
| `RATE_KBPS`  | 限速速率（KB/s）   | `50`        |
| `DELAY_MS`   | 每个请求延迟（ms） | `500`       |
| `HOST`       | 监听地址           | `0.0.0.0`   |

示例：

```bash
RATE_KBPS=200 DELAY_MS=100 HOST=127.0.0.1 python app.py
```

### 方式二：直接静态打开

直接双击 `public/index.html` 用浏览器打开即可（某些浏览器可能限制 `fetch` 读取本地 `main.html`，若空白请用方式一或起个静态服务器）。

## 如何写内容（博客文章）

博客的所有内容都在 `public/content/` 目录下。**每层目录用一个 `config.txt` 描述该层的菜单项**，`main.js` 启动时会递归扫描这些配置文件并生成菜单。

### `config.txt` 语法

每行一个条目，格式为 `类型 名称`：

| 类型 | 含义                                     |
| ---- | ---------------------------------------- |
| `m`  | 主页面 — 进入该层时默认显示的内容        |
| `f`  | 文件 — 普通可点击的文章 / 页面           |
| `d`  | 文件夹 — 子目录分组，可继续展开一层      |

> 一行如果只写名称、不带前缀，默认当作 `f`（文件）。

### 示例

`public/content/` 下这样组织：

```
content/
├── config.txt          # 根目录菜单
├── 首页.md              # 主页面（m 指向它）
├── 关于我.md
└── 技术笔记/            # 文件夹分组（d）
    ├── config.txt      # 该子层的菜单
    └── Python入门.md
```

`content/config.txt`：

```
m 首页.md
f 关于我.md
d 技术笔记
```

`content/技术笔记/config.txt`：

```
f Python入门.md
```

> ⚠️ **主页面（`m`）必须在根目录**。子文件夹里的 `m` 用于在该文件夹打开时显示对应内容。未设置主页面时页面会提示"未设置初始页面"。

### 内容格式

- **Markdown（`.md` / `.txt`）**：用 `markdown-it` 渲染，代码块自动高亮并带复制按钮。
- **HTML（`.html`）**：`.html` 文件通过透明 `iframe` 内嵌显示，适合自定义排版的页面。

## 如何部署上线

博客是纯静态站点，**上线不需要 Flask**，把 `public/` 整个文件夹托管到任意静态服务即可。

### 方案一：GitHub Pages（免费）

1. 把 `public/` 内的内容推送到仓库根目录。
2. 在仓库 Settings → Pages 选择部署源（如 `main` 分支的 `/` 目录）。
3. 通过 `https://<用户名>.github.io/<仓库名>/` 访问。

### 方案二：Netlify / Cloudflare Pages / Vercel（免费）

直接将 `public/` 文件夹拖拽上传即可，自动配置 HTTPS + CDN。

### 方案三：自己的服务器（Nginx）

把 `public/` 内容放到服务器，用 Nginx 指向它：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/blog;   # 把 public/ 内容放这里
    index index.html;
}
```

> **提示**：项目中所有资源路径都是**相对路径**（`./css/...`、`./html/...`、`../css/...`），只要保持 `public/` 内部目录结构不变，放到任何托管位置都能正常跑。

## 技术栈

- **前端**：原生 HTML / CSS / JavaScript（无框架）
- **Markdown**：`markdown-it`
- **代码高亮**：`highlight.js`
- **调试服务器**：Python Flask（仅本地/演示用）
- **字体**：Space Grotesk

## 目录说明

| 路径                        | 说明                                       |
| --------------------------- | ------------------------------------------ |
| `public/content/`           | ✏️ 博客文章内容（Markdown / HTML / config.txt） |
| `public/css/global.css`     | 主题变量（`--bg`、`--accent`、`--text` 等），想改配色来这里 |
| `public/fonts/`             | 字体文件                                    |
| `public/images/`            | 背景图等资源                                |
| `public/javascripts/main.js`| 核心逻辑：扫描 `config.txt`、渲染菜单与内容 |
