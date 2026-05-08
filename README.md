# NHKListening - 日语听写练习网站

一个帮助学习日语听力的网站，提供两种练习模式。

## 🎯 两种练习模式

### 🐢 慢速练习模式
- 数据来源：nhkeasier.com
- 音频特点：慢速朗读（ゆっくり），适合初学者
- 内容特点：配有完整的日文原文和振り仮名
- 访问方式：`index_slow.html` 或主页选择"慢速练习"
- 功能：三级难度、进阶系统、颜色反馈

### ⚡ 快速听力模式
- 数据来源：NHK Radio News（每日更新1条）
- 音频特点：正常播报速度（真实语速）
- 内容特点：需要手动输入日文文字
- 访问方式：`index_fast.html` 或主页选择"快速听力"
- **特色功能**：支持导入本地音频自由练习

## 📁 文件结构

```
nhk-listening/
├── index.html              # 主页（模式选择）
├── index_slow.html         # 慢速练习模式
├── index_fast.html        # 快速听力模式
├── practice.html           # 慢速练习的练习页面
├── practice_fast.html      # 快速听力的练习页面（含本地音频导入）
├── articles.json           # nhkeasier.com 数据（完整文字+振り仮名）
├── articles_nhk_radio.json # NHK Radio News 数据（仅音频）
├── scraper.py              # nhkeasier.com 数据抓取脚本
├── scraper_nhk_radio.py    # NHK Radio News 数据抓取脚本
└── .github/workflows/      # GitHub Actions 自动更新
```

## 🚀 快速开始

### 慢速练习（已有数据）
1. 直接打开 `index_slow.html`
2. 选择文章开始练习

### 快速听力（每日1条）
1. 打开 `index_fast.html`
2. 点击"开始练习"进入今天的NHK广播
3. 点击"📝 文字"按钮粘贴日文文字
4. 开始听写练习

### 本地音频练习
1. 打开 `index_fast.html`
2. 点击"💾 导入本地音频"或下方的"选择音频文件"
3. 上传你的音频（MP3、WAV等）
4. 输入日文文字开始练习

## 📝 快速听力模式 - 导入原文流程

由于NHK Radio News只有音频没有文字，需要配合语音转文字工具使用：

### 推荐工具：Soundwise.ai
- **网址**：https://soundwise.ai/zh-CN/mp3-to-text
- **特点**：基于Whisper的免费浏览器端转录，保护隐私
- **使用方法**：
  1. 从NHK Radio News下载音频（右键另存）
  2. 打开 soundwise.ai，上传音频文件
  3. 等待转写完成（几秒钟到几分钟）
  4. 复制转写结果
  5. 打开本网站的快速听力页面，点击"📝 文字"按钮粘贴

### 导入步骤
1. 打开 `index_fast.html`
2. 点击"开始练习"
3. 点击右上角的"📝 文字"按钮
4. 在弹出的文本框中粘贴日文文字
5. 点击"确认并开始练习"

## 📝 本地音频模式特点

- **不受进阶规则限制**：可以自由切换初级/中级/高级
- **文字单独保存**：每次导入的音频和文字会保存在本地
- **支持拖拽上传**：也可以把音频文件拖到上传区域

## 📝 数据抓取

### nhkeasier.com（慢速练习）
```bash
python scraper.py
```
- 自动获取最新文章和音频
- 生成完整的文字内容和振り仮名
- 通过GitHub Actions每天自动更新

### NHK Radio News（快速听力）
```bash
python scraper_nhk_radio.py
```
- 只获取最新1条广播音频
- 只提供音频URL，不含文字内容
- 需要在网页上手动输入文字

## 🎮 进阶系统

两种模式都支持三级难度进阶：

- **初级**：按整句（「。」）分割，每句独立练习
- **中级**：按整句（「。」）分割，每句独立练习
- **高级**：按段落分割，整段一起练习

解锁条件：当前难度连续5次达到95%以上正确率

**注意**：本地音频模式不受进阶规则限制，可以自由切换难度

## 📱 移动端适配

网站已针对移动端优化，支持PWA安装。

## 🔧 技术栈

- HTML5 + CSS3 + JavaScript
- LocalStorage 存储进度和本地音频文字
- GitHub Pages 托管

## 📄 License

MIT License
